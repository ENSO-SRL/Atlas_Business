import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError, ServiceNotPublishedError
from src.Domain.Entities.content_request import ContentRequest
from src.Domain.Enums.content_request_status import ContentRequestStatus
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService
from src.Application.Exceptions.business_exceptions import ServiceCategoryNotFoundError, VerticalMetadataValidationError
from src.Domain.Services.service_vertical_validator_registry import ServiceVerticalValidatorRegistry


@dataclass
class UpdateServiceCommand:
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    name: str | None = None
    category_id: UUID | None = None
    description: str | None = None
    establishment_policies: list[str] | None = None
    pre_booking_requirements: list[str] | None = None
    # Campos operativos (precio/capacidad): NO pasan por el filtro
    buffer_minutes: int | None = None
    grid_interval_minutes: int | None = None
    max_booking_window_days: int | None = None
    min_booking_window_hours: int | None = None
    max_daily_bookings_per_user: int | None = None
    requires_manual_approval: bool | None = None
    exposes_end_time: bool | None = None
    vertical_metadata: dict[str, Any] | None = None
    payment_cancellation_policy: dict[str, Any] | None = None
    modification_policy: dict[str, Any] | None = None
    arrival_confirmation_policy: dict[str, Any] | None = None


@dataclass
class UpdateServiceResult:
    content_request_id: UUID | None
    status: str
    message: str


class UpdateServiceUseCase:
    """
    Edita un servicio. Implementa el patrón shadow edit.
    Si hay cambios de texto, pasan por el filtro de contenido.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        content_request_repo: IContentRequestRepository,
        content_filter: IContentFilterService,
        service_category_repo: IServiceCategoryRepository,
    ):
        self.service_repo = service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.content_request_repo = content_request_repo
        self.content_filter = content_filter
        self.service_category_repo = service_category_repo
        self.vertical_registry = ServiceVerticalValidatorRegistry()

    async def execute(self, command: UpdateServiceCommand) -> UpdateServiceResult:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        if service.publication_status != PublicationStatus.PUBLISHED:
            raise ServiceNotPublishedError()

        if command.category_id is not None and command.category_id != service.category_id:
            category = await self.service_category_repo.get_by_id(command.category_id)
            if not category or not category.is_active:
                raise ServiceCategoryNotFoundError()
            category_name = category.name
        else:
            category = await self.service_category_repo.get_by_id(service.category_id)
            category_name = category.name if category else ""

        if command.vertical_metadata is not None:
            validator = self.vertical_registry.get_validator(category_name)
            is_valid, error_msg = validator.validate(command.vertical_metadata)
            if not is_valid:
                raise VerticalMetadataValidationError(error_msg or "Estructura de metadatos inválida.")

        # Construir payload de cambios
        payload = {}
        if command.name is not None and command.name != service.name:
            payload["name"] = command.name
        if command.category_id is not None and command.category_id != service.category_id:
            payload["category_id"] = str(command.category_id)
        if command.buffer_minutes is not None and command.buffer_minutes != service.buffer_minutes:
            payload["buffer_minutes"] = command.buffer_minutes
        if command.grid_interval_minutes is not None and command.grid_interval_minutes != service.grid_interval_minutes:
            payload["grid_interval_minutes"] = command.grid_interval_minutes
        if command.max_booking_window_days is not None and command.max_booking_window_days != service.max_booking_window_days:
            payload["max_booking_window_days"] = command.max_booking_window_days
        if command.min_booking_window_hours is not None and command.min_booking_window_hours != service.min_booking_window_hours:
            payload["min_booking_window_hours"] = command.min_booking_window_hours
        if command.max_daily_bookings_per_user is not None and command.max_daily_bookings_per_user != service.max_daily_bookings_per_user:
            payload["max_daily_bookings_per_user"] = command.max_daily_bookings_per_user
        if command.exposes_end_time is not None and command.exposes_end_time != service.exposes_end_time:
            payload["exposes_end_time"] = command.exposes_end_time
        if command.requires_manual_approval is not None and command.requires_manual_approval != service.requires_manual_approval:
            payload["requires_manual_approval"] = command.requires_manual_approval
        if command.vertical_metadata is not None and command.vertical_metadata != service.vertical_metadata:
            payload["vertical_metadata"] = command.vertical_metadata
        if command.payment_cancellation_policy is not None:
            # En la vida real haríamos un dict_factory, pero por simplicidad de JSON serialize:
            payload["payment_cancellation_policy"] = command.payment_cancellation_policy
        if command.modification_policy is not None:
            payload["modification_policy"] = command.modification_policy
        if command.arrival_confirmation_policy is not None:
            payload["arrival_confirmation_policy"] = command.arrival_confirmation_policy

        metadata = await self.agent_metadata_repo.get_by_id(service.agent_metadata_id)
        
        if command.description is not None and (not metadata or command.description != metadata.description):
            payload["description"] = command.description
        if command.establishment_policies is not None and (not metadata or command.establishment_policies != metadata.establishment_policies):
            payload["establishment_policies"] = command.establishment_policies
        if command.pre_booking_requirements is not None and (not metadata or command.pre_booking_requirements != metadata.pre_booking_requirements):
            payload["pre_booking_requirements"] = command.pre_booking_requirements

        if not payload:
            return UpdateServiceResult(content_request_id=None, status="NO_CHANGES", message="No hay cambios para aplicar.")

        # Buscar solicitud activa previa
        active_request = await self.content_request_repo.get_active_by_service(service.id)
        if active_request:
            active_request.status = ContentRequestStatus.SUPERSEDED
            active_request.updated_at = datetime.now(timezone.utc)
            active_request.updated_by = command.actor_id
            await self.content_request_repo.update(active_request)

        # Correr filtro de contenido sobre campos de texto libre
        text_fields_to_check = {
            k: v for k, v in payload.items() 
            if k in ("name", "description")
        }
        
        matches = []
        if text_fields_to_check:
            matches = await self.content_filter.check(text_fields_to_check)

        try:
            request_id = uuid.uuid7()
        except AttributeError:
            request_id = uuid.uuid4()

        if not matches:
            # Aplicar cambios directamente
            if "name" in payload: service.name = payload["name"]
            if "category_id" in payload: service.category_id = UUID(payload["category_id"])
            if "buffer_minutes" in payload: service.buffer_minutes = payload["buffer_minutes"]
            if "grid_interval_minutes" in payload: service.grid_interval_minutes = payload["grid_interval_minutes"]
            if "exposes_end_time" in payload: service.exposes_end_time = payload["exposes_end_time"]
            if "requires_manual_approval" in payload: service.requires_manual_approval = payload["requires_manual_approval"]
            if "vertical_metadata" in payload: service.vertical_metadata = payload["vertical_metadata"]
            if "payment_cancellation_policy" in payload:
                from src.Domain.Entities.service_policies import PaymentAndCancellationPolicy, PaymentSplit, PaymentStage, PaymentMethod
                pol_dict = payload["payment_cancellation_policy"]
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
            if "modification_policy" in payload:
                from src.Domain.Entities.service_policies import ModificationPolicy
                mod_dict = payload["modification_policy"]
                service.modification_policy = ModificationPolicy(
                    allows_same_day_reschedule=mod_dict.get("allows_same_day_reschedule"),
                    allows_date_change=mod_dict.get("allows_date_change"),
                    date_change_margin_days=mod_dict.get("date_change_margin_days"),
                )
            if "arrival_confirmation_policy" in payload:
                from src.Domain.Entities.service_policies import ArrivalAndConfirmationPolicy
                arr_dict = payload["arrival_confirmation_policy"]
                service.arrival_confirmation_policy = ArrivalAndConfirmationPolicy(
                    wait_time_minutes=arr_dict.get("wait_time_minutes"),
                    release_automatically=arr_dict.get("release_automatically"),
                )
            
            if metadata:
                if "description" in payload: metadata.description = payload["description"]
                if "establishment_policies" in payload: metadata.establishment_policies = payload["establishment_policies"]
                if "pre_booking_requirements" in payload: metadata.pre_booking_requirements = payload["pre_booking_requirements"]

            now = datetime.now(timezone.utc)
            service.updated_at = now
            service.updated_by = command.actor_id
            await self.service_repo.update(service)
            
            if metadata:
                metadata.updated_at = now
                metadata.updated_by = command.actor_id
                await self.agent_metadata_repo.update(metadata)

            # Trazabilidad
            content_req = ContentRequest(
                id=request_id,
                service_id=service.id,
                status=ContentRequestStatus.APPROVED,
                payload=payload,
                filter_matches=[],
                created_by=command.actor_id
            )
            await self.content_request_repo.create(content_req)
            
            return UpdateServiceResult(
                content_request_id=request_id,
                status=ContentRequestStatus.APPROVED.value,
                message="Edición aplicada de inmediato."
            )
        else:
            # Crear ContentRequest para revisión (Shadow Edit)
            content_req = ContentRequest(
                id=request_id,
                service_id=service.id,
                status=ContentRequestStatus.UNDER_REVIEW,
                payload=payload,
                filter_matches=matches,
                created_by=command.actor_id
            )
            await self.content_request_repo.create(content_req)

            return UpdateServiceResult(
                content_request_id=request_id,
                status=ContentRequestStatus.UNDER_REVIEW.value,
                message="La edición está en revisión por posible contenido restringido."
            )
