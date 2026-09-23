from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from src.Application.Exceptions.client_exceptions import InvalidDateError, InvalidPartySizeError, ServiceNotPublicError
from src.Domain.Entities.service import BillingNature
from src.Domain.Enums.calculation_basis import CalculationBasis
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository, OccupiedGroup
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository


@dataclass
class GetServiceAvailabilityCommand:
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
    Algoritmo central de cálculo de disponibilidad de slots.
    """

    def __init__(
        self,
        client_service_repo: IClientServiceRepository,
        business_repo: IBusinessRepository,
        bookable_object_repo: IBookableObjectRepository,
        client_booking_repo: IClientBookingRepository,
        rate_repo: IServiceRateRepository,
    ):
        self.client_service_repo = client_service_repo
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

        service = await self.client_service_repo.get_published_by_id_only(command.service_id)
        if not service:
            raise ServiceNotPublicError()

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
        print(f"qualified_objects: {qualified_objects}")
        qualified_ids = [obj.id for obj in qualified_objects]

        # 2. Determinar horario laboral del negocio para ese día
        business = await self.business_repo.get_by_id(service.business_id)
        weekday = command.date.strftime("%A").upper()
        print(f"weekday: {weekday}")
        print(f"business.schedules: {[s.weekday.value for s in business.schedules]}")
        schedule = next((s for s in business.schedules if s.weekday.value == weekday), None)
        
        if not schedule:
            print("No schedule found")
            return empty_result

        # Asumimos UTC para las consultas a BD por simplicidad si no hay timezone especificado
        day_start = datetime.combine(command.date, time.fromisoformat(schedule.opening_time)).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(command.date, time.fromisoformat(schedule.closing_time)).replace(tzinfo=timezone.utc)
        print(f"day_start: {day_start}")
        print(f"day_end: {day_end}")

        # 3. Generar parrilla de slots candidatos
        total_duration = service.occupation_duration_minutes + service.buffer_minutes
        candidate_slots = []
        t = day_start
        while t < day_end:
            # El slot debe terminar (incluyendo buffer) antes o exactamente al cierre
            # O alternativamente, el cliente debe poder terminar su ocupación antes del cierre
            # Usaremos ocupación para permitir que terminen de usar el servicio justo al cierre
            if t + timedelta(minutes=service.occupation_duration_minutes) <= day_end:
                candidate_slots.append(t)
            t += timedelta(minutes=service.grid_interval_minutes)

        if not candidate_slots:
            return empty_result
        print(f"candidate_slots: {candidate_slots}")
        # 4. Recuperar grupos de ocupación desde la BD (un solo query)
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
            print(f"service.billing_nature: {service.billing_nature}")
            equal:bool = service.billing_nature == BillingNature.BILLABLE
            print(f"equal: {equal}")
            if equal:
                print(f"Finding rate for slot {slot_start} with party size {command.party_size}")
                rate_info = self._find_rate(rates, slot_start, command.party_size)
            print(f"rate_info: {rate_info}")

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
        
        # Grupos que se solapan con [slot_start, slot_end)
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
                return 0  # Lleno en algún punto
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
                    total = base * party_size if rate.calculation_basis == CalculationBasis.PER_PERSON else base
                    return SlotRateInfo(
                        amount=f"{base:.2f}",
                        calculation_basis=rate.calculation_basis.value,
                        total_amount=f"{total:.2f}",
                    )
        return None
