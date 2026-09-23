from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetServiceRatesCommand:
    business_id: UUID
    service_id: UUID


@dataclass
class ServiceRateResult:
    id: UUID
    weekdays: list[str]
    start_time: str
    end_time: str
    amount: str
    calculation_basis: str


class GetServiceRatesUseCase:
    """
    Obtiene las tarifas de un servicio.
    """

    def __init__(self, service_repo: IServiceRepository, rate_repo: IServiceRateRepository):
        self.service_repo = service_repo
        self.rate_repo = rate_repo

    async def execute(self, command: GetServiceRatesCommand) -> list[ServiceRateResult]:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()
            
        rates = await self.rate_repo.list_by_service(command.service_id)
        return [
            ServiceRateResult(
                id=r.id,
                weekdays=r.weekdays,
                start_time=r.start_time.strftime("%H:%M"),
                end_time=r.end_time.strftime("%H:%M"),
                amount=str(r.amount),
                calculation_basis=r.calculation_basis.value,
            )
            for r in rates
        ]
