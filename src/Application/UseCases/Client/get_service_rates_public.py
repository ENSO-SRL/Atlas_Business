from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.client_exceptions import ServiceNotPublicError
from src.Application.UseCases.Business.get_service_rates import ServiceRateResult
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository


@dataclass
class GetServiceRatesPublicCommand:
    service_id: UUID


@dataclass
class ServiceRatesPublicResult:
    service_id: UUID
    billing_nature: str
    rates: list[ServiceRateResult]


class GetServiceRatesPublicUseCase:
    """
    Devuelve el esquema completo de tarifas de un servicio para el lado cliente.
    """

    def __init__(
        self,
        client_service_repo: IClientServiceRepository,
        rate_repo: IServiceRateRepository,
    ):
        self.client_service_repo = client_service_repo
        self.rate_repo = rate_repo

    async def execute(self, command: GetServiceRatesPublicCommand) -> ServiceRatesPublicResult:
        service = await self.client_service_repo.get_published_by_id_only(command.service_id)
        if not service:
            raise ServiceNotPublicError()

        rates = await self.rate_repo.list_by_service(command.service_id)

        rates_result = [
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

        return ServiceRatesPublicResult(
            service_id=service.id,
            billing_nature=service.billing_nature.value,
            rates=rates_result,
        )
