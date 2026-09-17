import uuid
from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

from src.Application.Exceptions.business_exceptions import RatesCoverageIncompleteError, ServiceNotFoundError
from src.Application.UseCases.Business.get_service_rates import ServiceRateResult
from src.Domain.Entities.service_rate import ServiceRate
from src.Domain.Enums.calculation_basis import CalculationBasis
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class RateInput:
    weekdays: list[str]
    start_time: str
    end_time: str
    amount: str
    calculation_basis: str


@dataclass
class ReplaceServiceRatesCommand:
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    rates: list[RateInput]


class ReplaceServiceRatesUseCase:
    """
    Reemplaza todo el conjunto de tarifas de un servicio atómicamente, validando
    cobertura completa contra el horario del negocio.
    """

    def __init__(
        self,
        rate_repo: IServiceRateRepository,
        service_repo: IServiceRepository,
        business_repo: IBusinessRepository,
    ):
        self.rate_repo = rate_repo
        self.service_repo = service_repo
        self.business_repo = business_repo

    async def execute(self, command: ReplaceServiceRatesCommand) -> list[ServiceRateResult]:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        business = await self.business_repo.get_by_id(command.business_id)
        # Convertir horarios de negocio a un diccionario dict[weekday, (opening, closing)]
        # Asume que un día solo aparece una vez en los horarios del negocio
        business_schedule = {}
        for s in business.schedules:
            opening = datetime.strptime(s["opening_time"], "%H:%M").time()
            closing = datetime.strptime(s["closing_time"], "%H:%M").time()
            business_schedule[s["weekday"]] = (opening, closing)

        # Validar cobertura
        self._validate_coverage(command.rates, business_schedule)

        new_rates = []
        for ri in command.rates:
            try:
                rate_id = uuid.uuid7()
            except AttributeError:
                rate_id = uuid.uuid4()

            new_rates.append(
                ServiceRate(
                    id=rate_id,
                    service_id=command.service_id,
                    weekdays=ri.weekdays,
                    start_time=datetime.strptime(ri.start_time, "%H:%M").time(),
                    end_time=datetime.strptime(ri.end_time, "%H:%M").time(),
                    amount=Decimal(ri.amount),
                    calculation_basis=CalculationBasis(ri.calculation_basis),
                    created_by=command.actor_id,
                )
            )

        saved_rates = await self.rate_repo.replace_all(command.service_id, new_rates)

        return [
            ServiceRateResult(
                id=r.id,
                weekdays=r.weekdays,
                start_time=r.start_time.strftime("%H:%M"),
                end_time=r.end_time.strftime("%H:%M"),
                amount=str(r.amount),
                calculation_basis=r.calculation_basis.value,
            )
            for r in saved_rates
        ]

    def _validate_coverage(self, rates_input: list[RateInput], business_schedule: dict[str, tuple[time, time]]):
        """
        Valida que para cada día en el que el negocio abre, las tarifas cubran 
        exactamente desde opening_time hasta closing_time sin huecos.
        """
        # Agrupar tarifas por día
        rates_by_day: dict[str, list[tuple[time, time]]] = {wd: [] for wd in business_schedule.keys()}

        for ri in rates_input:
            start_t = datetime.strptime(ri.start_time, "%H:%M").time()
            end_t = datetime.strptime(ri.end_time, "%H:%M").time()
            
            for wd in ri.weekdays:
                if wd in rates_by_day:
                    rates_by_day[wd].append((start_t, end_t))

        # Validar día a día
        for weekday, (opening, closing) in business_schedule.items():
            day_rates = rates_by_day[weekday]
            
            if not day_rates:
                raise RatesCoverageIncompleteError(
                    weekday=weekday,
                    gap_start=opening.strftime("%H:%M"),
                    gap_end=closing.strftime("%H:%M"),
                )

            # Ordenar por hora de inicio
            day_rates.sort(key=lambda r: r[0])

            # 1. Empieza al abrir el negocio?
            if day_rates[0][0] > opening:
                raise RatesCoverageIncompleteError(
                    weekday=weekday,
                    gap_start=opening.strftime("%H:%M"),
                    gap_end=day_rates[0][0].strftime("%H:%M"),
                )

            # 2. Sin huecos?
            current_end = day_rates[0][1]
            for i in range(1, len(day_rates)):
                next_start = day_rates[i][0]
                
                if next_start > current_end:
                    raise RatesCoverageIncompleteError(
                        weekday=weekday,
                        gap_start=current_end.strftime("%H:%M"),
                        gap_end=next_start.strftime("%H:%M"),
                    )
                # Si hay solapamiento, next_start < current_end, 
                # por ahora lo permitimos pero tomamos el máximo
                current_end = max(current_end, day_rates[i][1])

            # 3. Termina al cerrar el negocio?
            if current_end < closing:
                raise RatesCoverageIncompleteError(
                    weekday=weekday,
                    gap_start=current_end.strftime("%H:%M"),
                    gap_end=closing.strftime("%H:%M"),
                )
