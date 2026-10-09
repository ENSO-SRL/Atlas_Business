from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetServiceCommand:
    service_id: UUID
    business_id: UUID


@dataclass
class PendingEditRequest:
    id: UUID
    status: str
    created_at: str | None


@dataclass
class ServiceDetailResult:
    id: UUID
    name: str
    category_id: UUID
    category_name: str
    publication_status: str
    occupation_duration_minutes: int
    duration_nature: str
    exposes_end_time: bool
    buffer_minutes: int
    grid_interval_minutes: int
    max_booking_window_days: int
    min_booking_window_hours: int
    max_daily_bookings_per_user: int
    allows_manual_object_selection: bool
    auto_selection_criteria: str
    billing_nature: str
    rejection_reason: str | None
    agent_metadata: dict
    vertical_metadata: dict[str, Any]
    payment_cancellation_policy: dict[str, Any] | None
    modification_policy: dict[str, Any] | None
    arrival_confirmation_policy: dict[str, Any] | None
    pending_edit_request: PendingEditRequest | None


class GetServiceUseCase:
    """
    Obtiene el detalle completo de un servicio junto con su posible solicitud de edición activa.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        content_request_repo: IContentRequestRepository,
    ):
        self.service_repo = service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.content_request_repo = content_request_repo

    async def execute(self, command: GetServiceCommand) -> ServiceDetailResult:
        print("LLEGUE AL USE CASE")
        print(command)
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        metadata = await self.agent_metadata_repo.get_by_id(service.agent_metadata_id)
        metadata_dict = {
            "description": metadata.description if metadata else "",
            "establishment_policies": metadata.establishment_policies if metadata else [],
            "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
        }

        active_request = await self.content_request_repo.get_active_by_service(service.id)
        pending_request_dto = None
        if active_request:
            created_at_str = active_request.created_at.isoformat() if active_request.created_at else None
            pending_request_dto = PendingEditRequest(
                id=active_request.id,
                status=active_request.status.value,
                created_at=created_at_str,
            )

        pol_payment = None
        if service.payment_cancellation_policy:
            pol_payment = {
                "payment_splits": [
                    {
                        "stage": s.stage.value,
                        "percentage": s.percentage,
                        "allowed_methods": [m.value for m in s.allowed_methods],
                    }
                    for s in service.payment_cancellation_policy.payment_splits
                ],
                "cancellation_description": service.payment_cancellation_policy.cancellation_description,
                "min_cancellation_margin_hours": service.payment_cancellation_policy.min_cancellation_margin_hours,
                "cancellation_fee": float(service.payment_cancellation_policy.cancellation_fee) if service.payment_cancellation_policy.cancellation_fee is not None else None,
            }

        pol_mod = None
        if service.modification_policy:
            pol_mod = {
                "allows_same_day_reschedule": service.modification_policy.allows_same_day_reschedule,
                "allows_date_change": service.modification_policy.allows_date_change,
                "date_change_margin_days": service.modification_policy.date_change_margin_days,
            }

        pol_arr = None
        if service.arrival_confirmation_policy:
            pol_arr = {
                "wait_time_minutes": service.arrival_confirmation_policy.wait_time_minutes,
                "release_automatically": service.arrival_confirmation_policy.release_automatically,
            }

        return ServiceDetailResult(
            id=service.id,
            name=service.name,
            category_id=service.category_id,
            category_name=service.category_name or "Desconocida",
            publication_status=service.publication_status.value,
            occupation_duration_minutes=service.occupation_duration_minutes,
            duration_nature=service.duration_nature.value,
            exposes_end_time=service.exposes_end_time,
            buffer_minutes=service.buffer_minutes,
            grid_interval_minutes=service.grid_interval_minutes,
            max_booking_window_days=service.max_booking_window_days,
            min_booking_window_hours=service.min_booking_window_hours,
            max_daily_bookings_per_user=service.max_daily_bookings_per_user,
            allows_manual_object_selection=service.allows_manual_object_selection,
            auto_selection_criteria=service.auto_selection_criteria.value,
            billing_nature=service.billing_nature.value,
            rejection_reason=service.rejection_reason,
            agent_metadata=metadata_dict,
            vertical_metadata=service.vertical_metadata or {},
            payment_cancellation_policy=pol_payment,
            modification_policy=pol_mod,
            arrival_confirmation_policy=pol_arr,
            pending_edit_request=pending_request_dto,
        )
