import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from datetime import time
from src.Domain.Entities.agent_metadata import AgentMetadata
from src.Domain.Entities.service import Service, ServiceSchedule
from src.Domain.Enums.weekday import Weekday
from src.Domain.Enums.auto_selection import AutoSelectionCriteria
from src.Domain.Enums.billing_nature import BillingNature
from src.Domain.Enums.duration_nature import DurationNature
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Entities.service_policies import (
    ArrivalAndConfirmationPolicy,
    ModificationPolicy,
    PaymentAndCancellationPolicy,
    PaymentMethod,
    PaymentSplit,
    PaymentStage,
)
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService
from src.Application.Exceptions.business_exceptions import ServiceCategoryNotFoundError, RatesRequiredForBillableServiceError, VerticalMetadataValidationError
from src.Application.UseCases.Business.replace_service_rates import ReplaceServiceRatesUseCase, ReplaceServiceRatesCommand, RateInput
from src.Domain.Services.service_vertical_validator_registry import ServiceVerticalValidatorRegistry


@dataclass
class CreateServiceCommand:
    business_id: UUID
    actor_id: UUID
    name: str
    category_id: UUID
    occupation_duration_minutes: int
    duration_nature: str
    exposes_end_time: bool
    buffer_minutes: int
    grid_interval_minutes: int
    allows_manual_object_selection: bool
    auto_selection_criteria: str
    billing_nature: str
    description: str
    establishment_policies: list[str]
    pre_booking_requirements: list[str]
    vertical_metadata: dict[str, Any]
    max_booking_window_days: int
    min_booking_window_hours: int
    max_daily_bookings_per_user: int
    payment_cancellation_policy: dict[str, Any] | None = None
    modification_policy: dict[str, Any] | None = None
    arrival_confirmation_policy: dict[str, Any] | None = None
    schedules: list[dict[str, Any]] | None = None
    rates: list[RateInput] | None = None


@dataclass
class CreateServiceResult:
    id: UUID
    name: str
    publication_status: str
    message: str


class CreateServiceUseCase:
    """
    Crea un nuevo servicio pasando por el filtro de contenido.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        content_filter: IContentFilterService,
        service_category_repo: IServiceCategoryRepository,
        business_repo: IBusinessRepository,
        rate_repo: IServiceRateRepository,
    ):
        self.service_repo = service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.content_filter = content_filter
        self.service_category_repo = service_category_repo
        self.business_repo = business_repo
        self.rate_repo = rate_repo
        self.vertical_registry = ServiceVerticalValidatorRegistry()

    async def execute(self, command: CreateServiceCommand) -> CreateServiceResult:
        # Validar tarifas si es facturable
        if command.billing_nature == BillingNature.BILLABLE.value:
            if not command.rates:
                raise RatesRequiredForBillableServiceError()

        # Validar categoría
        category = await self.service_category_repo.get_by_id(command.category_id)
        if not category or not category.is_active:
            raise ServiceCategoryNotFoundError()

        # Validar vertical_metadata
        validator = self.vertical_registry.get_validator(category.name)
        is_valid, error_msg = validator.validate(command.vertical_metadata)
        if not is_valid:
            raise VerticalMetadataValidationError(error_msg or "Estructura de metadatos inválida.")

        try:
            metadata_id = uuid.uuid7()
        except AttributeError:
            metadata_id = uuid.uuid4()

        metadata = AgentMetadata(
            id=metadata_id,
            description=command.description,
            establishment_policies=command.establishment_policies,
            pre_booking_requirements=command.pre_booking_requirements,
            created_by=command.actor_id,
        )
        await self.agent_metadata_repo.create(metadata)

        try:
            service_id = uuid.uuid7()
        except AttributeError:
            service_id = uuid.uuid4()

        # Solo enviamos campos de texto libre al filtro
        matches = await self.content_filter.check(
            {
                "name": command.name,
                "description": command.description,
            }
        )

        initial_status = PublicationStatus.UNDER_REVIEW if matches else PublicationStatus.PUBLISHED
        message = "En revisión por posible contenido restringido." if matches else "Servicio publicado exitosamente."

        service = Service(
            id=service_id,
            business_id=command.business_id,
            name=command.name,
            occupation_duration_minutes=command.occupation_duration_minutes,
            duration_nature=DurationNature(command.duration_nature),
            exposes_end_time=command.exposes_end_time,
            buffer_minutes=command.buffer_minutes,
            grid_interval_minutes=command.grid_interval_minutes,
            allows_manual_object_selection=command.allows_manual_object_selection,
            auto_selection_criteria=AutoSelectionCriteria(command.auto_selection_criteria),
            billing_nature=BillingNature(command.billing_nature),
            agent_metadata_id=metadata_id,
            category_id=command.category_id,
            publication_status=initial_status,
            created_by=command.actor_id,
            vertical_metadata=command.vertical_metadata,
            max_booking_window_days=command.max_booking_window_days,
            min_booking_window_hours=command.min_booking_window_hours,
            max_daily_bookings_per_user=command.max_daily_bookings_per_user,
        )

        if command.payment_cancellation_policy:
            pol_dict = command.payment_cancellation_policy
            splits = []
            for s in pol_dict.get("payment_splits", []):
                splits.append(PaymentSplit(
                    stage=PaymentStage(s["stage"]),
                    percentage=s["percentage"],
                    allowed_methods=[PaymentMethod(m) for m in s.get("allowed_methods", [])]
                ))
            service.payment_cancellation_policy = PaymentAndCancellationPolicy(
                payment_splits=splits,
                cancellation_description=pol_dict.get("cancellation_description"),
                min_cancellation_margin_hours=pol_dict.get("min_cancellation_margin_hours"),
                cancellation_fee=pol_dict.get("cancellation_fee"),
            )

        if command.modification_policy:
            mod_dict = command.modification_policy
            service.modification_policy = ModificationPolicy(
                allows_same_day_reschedule=mod_dict.get("allows_same_day_reschedule"),
                allows_date_change=mod_dict.get("allows_date_change"),
                date_change_margin_days=mod_dict.get("date_change_margin_days"),
            )

        if command.arrival_confirmation_policy:
            arr_dict = command.arrival_confirmation_policy
            service.arrival_confirmation_policy = ArrivalAndConfirmationPolicy(
                wait_time_minutes=arr_dict.get("wait_time_minutes"),
                release_automatically=arr_dict.get("release_automatically"),
            )

        if command.schedules:
            for s in command.schedules:
                service.schedules.append(
                    ServiceSchedule(
                        weekday=Weekday(s["weekday"]),
                        opening_time=time.fromisoformat(s["opening_time"]),
                        closing_time=time.fromisoformat(s["closing_time"]),
                    )
                )

        await self.service_repo.create(service)

        # Crear tarifas si corresponde
        if command.billing_nature == BillingNature.BILLABLE.value and command.rates:
            replace_rates_use_case = ReplaceServiceRatesUseCase(
                self.rate_repo, self.service_repo, self.business_repo
            )
            replace_cmd = ReplaceServiceRatesCommand(
                service_id=service_id,
                business_id=command.business_id,
                actor_id=command.actor_id,
                rates=command.rates,
            )
            await replace_rates_use_case.execute(replace_cmd)

        return CreateServiceResult(
            id=service.id,
            name=service.name,
            publication_status=service.publication_status.value,
            message=message,
        )
