from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository


@dataclass
class GetServiceRatesCommand:
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

    def __init__(self, rate_repo: IServiceRateRepository):
        self.rate_repo = rate_repo

    async def execute(self, command: GetServiceRatesCommand) -> list[ServiceRateResult]:
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
