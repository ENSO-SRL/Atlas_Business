from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.Application.Exceptions.client_exceptions import BusinessNotVerifiedError
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository


@dataclass
class ListPublicServicesCommand:
    business_id: UUID


@dataclass
class PublicCustomFieldResult:
    id: UUID
    label: str
    required: bool
    data_type: str
    options: list[str] | None


@dataclass
class PublicServiceResult:
    id: UUID
    name: str
    occupation_duration_minutes: int
    exposes_end_time: bool
    billing_nature: str
    max_booking_window_days: int
    min_booking_window_hours: int
    max_daily_bookings_per_user: int
    allows_manual_object_selection: bool
    agent_metadata: dict
    vertical_metadata: dict[str, Any]
    custom_fields: list[PublicCustomFieldResult]
    payment_cancellation_policy: dict[str, Any] | None
    modification_policy: dict[str, Any] | None
    arrival_confirmation_policy: dict[str, Any] | None


class ListPublicServicesUseCase:
    """
    Lista todos los servicios publicados de un negocio verificado.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        client_service_repo: IClientServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        custom_field_repo: ICustomFieldRepository,
    ):
        self.business_repo = business_repo
        self.client_service_repo = client_service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.custom_field_repo = custom_field_repo

    async def execute(self, command: ListPublicServicesCommand) -> list[PublicServiceResult]:
        business = await self.business_repo.get_by_id(command.business_id)
        if not business or business.verification_status != VerificationStatus.VERIFIED:
            raise BusinessNotVerifiedError()

        services = await self.client_service_repo.list_published_by_business(command.business_id)
        result_list = []

        for s in services:
            metadata = await self.agent_metadata_repo.get_by_id(s.agent_metadata_id)
            metadata_dict = {
                "description": metadata.description if metadata else "",
                "establishment_policies": metadata.establishment_policies if metadata else [],
                "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
            }

            custom_fields = await self.custom_field_repo.list_by_service(s.id)
            public_fields = [
                PublicCustomFieldResult(
                    id=cf.id,
                    label=cf.label,
                    required=cf.required,
                    data_type=cf.data_type.value,
                    options=cf.options,
                )
                for cf in sorted(custom_fields, key=lambda x: x.order)
                if cf.visible_to_client
            ]

            pol_payment = None
            if s.payment_cancellation_policy:
                pol_payment = {
                    "payment_splits": [
                        {
                            "stage": sp.stage.value,
                            "percentage": sp.percentage,
                            "allowed_methods": [m.value for m in sp.allowed_methods],
                        }
                        for sp in s.payment_cancellation_policy.payment_splits
                    ],
                    "cancellation_description": s.payment_cancellation_policy.cancellation_description,
                    "min_cancellation_margin_hours": s.payment_cancellation_policy.min_cancellation_margin_hours,
                    "cancellation_fee": float(s.payment_cancellation_policy.cancellation_fee) if s.payment_cancellation_policy.cancellation_fee is not None else None,
                }

            pol_mod = None
            if s.modification_policy:
                pol_mod = {
                    "allows_same_day_reschedule": s.modification_policy.allows_same_day_reschedule,
                    "allows_date_change": s.modification_policy.allows_date_change,
                    "date_change_margin_days": s.modification_policy.date_change_margin_days,
                }

            pol_arr = None
            if s.arrival_confirmation_policy:
                pol_arr = {
                    "wait_time_minutes": s.arrival_confirmation_policy.wait_time_minutes,
                    "release_automatically": s.arrival_confirmation_policy.release_automatically,
                }

            result_list.append(
                PublicServiceResult(
                    id=s.id,
                    name=s.name,
                    occupation_duration_minutes=s.occupation_duration_minutes,
                    exposes_end_time=s.exposes_end_time,
                    billing_nature=s.billing_nature.value,
                    max_booking_window_days=s.max_booking_window_days,
                    min_booking_window_hours=s.min_booking_window_hours,
                    max_daily_bookings_per_user=s.max_daily_bookings_per_user,
                    allows_manual_object_selection=s.allows_manual_object_selection,
                    agent_metadata=metadata_dict,
                    vertical_metadata=s.vertical_metadata,
                    custom_fields=public_fields,
                    payment_cancellation_policy=pol_payment,
                    modification_policy=pol_mod,
                    arrival_confirmation_policy=pol_arr,
                )
            )

        return result_list
