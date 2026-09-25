from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Application.Exceptions.client_exceptions import InvalidDateError, InvalidPartySizeError
from src.Domain.Entities.service import BillingNature
from src.Domain.Enums.calculation_basis import CalculationBasis
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository, OccupiedGroup
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetServiceAvailabilityCommand:
    business_id: UUID
    service_id: UUID
    date: date
    party_size: int


@dataclass
class SlotRateInfo:
    amount: str
    calculation_basis: str
    total_amount: str


@dataclass
class SlotResult:
    start_time: str
    end_time: str | None
    available_objects_count: int
    rate: SlotRateInfo | None


@dataclass
class ServiceAvailabilityResult:
    service_id: UUID
    date: str
    party_size: int
    occupation_duration_minutes: int
    buffer_minutes: int
    slots: list[SlotResult]


class GetServiceAvailabilityUseCase:
    """
    Calcula los slots horarios disponibles para un servicio, considerando:
    - Horarios del negocio para el día solicitado.
    - Ocupación actual (reservas) en los objetos reservables.
    - Capacidad de los objetos reservables vs party_size.
    - Tarifas (rates) si el servicio es facturable.
    NOTA: Esta es la versión B2B, no exige que el servicio esté PUBLICADO ni VERIFICADO.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        business_repo: IBusinessRepository,
        bookable_object_repo: IBookableObjectRepository,
        client_booking_repo: IClientBookingRepository,
        rate_repo: IServiceRateRepository,
    ):
        self.service_repo = service_repo
        self.business_repo = business_repo
        self.bookable_object_repo = bookable_object_repo
        self.client_booking_repo = client_booking_repo
        self.rate_repo = rate_repo

    async def execute(self, command: GetServiceAvailabilityCommand) -> ServiceAvailabilityResult:
        if command.party_size < 1:
            raise InvalidPartySizeError()
            
        today = datetime.now(timezone.utc).date()
        if command.date < today:
            raise InvalidDateError()

        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        # 1. Identificar objetos calificados por capacidad
        all_objects = await self.bookable_object_repo.list_by_service(service.id)
        qualified_objects = [
            obj for obj in all_objects
            if obj.is_active and obj.min_capacity <= command.party_size <= obj.max_capacity
        ]
        capacity_total = len(qualified_objects)
        
        empty_result = ServiceAvailabilityResult(
            service_id=service.id,
            date=command.date.isoformat(),
            party_size=command.party_size,
            occupation_duration_minutes=service.occupation_duration_minutes,
            buffer_minutes=service.buffer_minutes,
            slots=[]
        )

        if capacity_total == 0:
            return empty_result
            
        qualified_ids = [obj.id for obj in qualified_objects]

        # 2. Determinar horario laboral del negocio para ese día
        business = await self.business_repo.get_by_id(service.business_id)
        weekday = command.date.strftime("%A").upper()
        
        schedule = next((s for s in business.schedules if s.weekday.value == weekday), None)
        
        if not schedule:
            return empty_result

        day_start = datetime.combine(command.date, time.fromisoformat(schedule.opening_time)).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(command.date, time.fromisoformat(schedule.closing_time)).replace(tzinfo=timezone.utc)

        # 3. Generar parrilla de slots candidatos
        total_duration = service.occupation_duration_minutes + service.buffer_minutes
        candidate_slots = []
        t = day_start
        while t < day_end:
            if t + timedelta(minutes=service.occupation_duration_minutes) <= day_end:
                candidate_slots.append(t)
            t += timedelta(minutes=service.grid_interval_minutes)

        if not candidate_slots:
            return empty_result
            
        # 4. Recuperar grupos de ocupación desde la BD
        occupied_groups = await self.client_booking_repo.get_occupied_groups(
            object_ids=qualified_ids,
            day_start=day_start,
            day_end=day_end,
        )

        rates = await self.rate_repo.list_by_service(service.id)
        result_slots = []

        # 5. Sweep de ocupación combinada por slot candidato
        for slot_start in candidate_slots:
            available = self._slot_available_count(
                slot_start,
                total_duration,
                occupied_groups,
                capacity_total,
                service.grid_interval_minutes
            )

            if available <= 0:
                continue

            slot_end = slot_start + timedelta(minutes=service.occupation_duration_minutes)
            rate_info = None
            
            equal = service.billing_nature.value == BillingNature.BILLABLE.value
            
            if equal:
                rate_info = self._find_rate(rates, slot_start, command.party_size)

            result_slots.append(
                SlotResult(
                    start_time=slot_start.strftime("%H:%M"),
                    end_time=slot_end.strftime("%H:%M") if service.exposes_end_time else None,
                    available_objects_count=available,
                    rate=rate_info,
                )
            )

        return ServiceAvailabilityResult(
            service_id=service.id,
            date=command.date.isoformat(),
            party_size=command.party_size,
            occupation_duration_minutes=service.occupation_duration_minutes,
            buffer_minutes=service.buffer_minutes,
            slots=result_slots,
        )

    def _slot_available_count(
        self,
        slot_start: datetime,
        total_duration_min: int,
        groups: list[OccupiedGroup],
        capacity_total: int,
        step_min: int
    ) -> int:
        slot_end = slot_start + timedelta(minutes=total_duration_min)
        
        relevant = [g for g in groups if g.start_time < slot_end and g.end_time > slot_start]
        if not relevant:
            return capacity_total
            
        min_available = capacity_total
        point = slot_start
        while point < slot_end:
            ocupation = sum(
                g.count for g in relevant
                if g.start_time <= point < g.end_time
            )
            available = capacity_total - ocupation
            if available <= 0:
                return 0
            min_available = min(min_available, available)
            point += timedelta(minutes=step_min)
            
        return min_available

    def _find_rate(self, rates: list, slot_start: datetime, party_size: int) -> SlotRateInfo | None:
        weekday_name = slot_start.strftime("%A").upper()
        slot_time = slot_start.time()

        for rate in rates:
            if weekday_name in rate.weekdays:
                if rate.start_time <= slot_time < rate.end_time:
                    base = rate.amount
                    total = base * party_size if rate.calculation_basis.value == CalculationBasis.PER_PERSON.value else base
                    return SlotRateInfo(
                        amount=f"{base:.2f}",
                        calculation_basis=rate.calculation_basis.value,
                        total_amount=f"{total:.2f}",
                    )
        return None
