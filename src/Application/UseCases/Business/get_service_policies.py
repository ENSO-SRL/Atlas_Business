from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetServicePoliciesCommand:
    service_id: UUID
    business_id: UUID


@dataclass
class ServicePoliciesResult:
    payment_cancellation_policy: dict[str, Any] | None
    modification_policy: dict[str, Any] | None
    arrival_confirmation_policy: dict[str, Any] | None


class GetServicePoliciesUseCase:
    """
    Obtiene específicamente las políticas operativas de un servicio,
    validando que pertenezca al negocio del usuario.
    """

    def __init__(self, service_repo: IServiceRepository):
        self.service_repo = service_repo

    async def execute(self, command: GetServicePoliciesCommand) -> ServicePoliciesResult:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

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

        return ServicePoliciesResult(
            payment_cancellation_policy=pol_payment,
            modification_policy=pol_mod,
            arrival_confirmation_policy=pol_arr,
        )
