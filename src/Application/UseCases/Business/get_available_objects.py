from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Application.Exceptions.client_exceptions import InvalidPartySizeError
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetAvailableObjectsCommand:
    business_id: UUID
    service_id: UUID
    date: date
    start_time: str
    party_size: int


@dataclass
class AvailableObjectInfo:
    id: UUID
    name: str | None
    min_capacity: int
    max_capacity: int


@dataclass
class AvailableObjectsResult:
    service_id: UUID
    slot_start: str
    party_size: int
    available_objects: list[AvailableObjectInfo]


class GetAvailableObjectsUseCase:
    """
    Lista los objetos específicos disponibles para un slot y party_size.
    NOTA: B2B versión, no exige que el servicio esté publicado ni verificado.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        bookable_object_repo: IBookableObjectRepository,
        client_booking_repo: IClientBookingRepository,
    ):
        self.service_repo = service_repo
        self.bookable_object_repo = bookable_object_repo
        self.client_booking_repo = client_booking_repo

    async def execute(self, command: GetAvailableObjectsCommand) -> AvailableObjectsResult:
        if command.party_size < 1:
            raise InvalidPartySizeError()

        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        # Filtrar calificados por capacidad
        all_objects = await self.bookable_object_repo.list_by_service(service.id)
        qualified_objects = [
            obj for obj in all_objects
            if obj.is_active and obj.min_capacity <= command.party_size <= obj.max_capacity
        ]
        
        slot_start = datetime.combine(command.date, time.fromisoformat(command.start_time)).replace(tzinfo=timezone.utc)
        
        result = AvailableObjectsResult(
            service_id=service.id,
            slot_start=slot_start.isoformat(),
            party_size=command.party_size,
            available_objects=[]
        )

        if not qualified_objects:
            return result

        qualified_ids = [obj.id for obj in qualified_objects]
        slot_end = slot_start + timedelta(minutes=service.occupation_duration_minutes + service.buffer_minutes)

        # Consultar IDs de objetos ocupados
        occupied_ids = await self.client_booking_repo.get_occupied_object_ids(
            object_ids=qualified_ids,
            slot_start=slot_start,
            slot_end=slot_end,
        )

        # Filtrar los que no están ocupados
        available_objects = [obj for obj in qualified_objects if obj.id not in occupied_ids]

        # Ordenar por CLOSEST_MAX_CAPACITY: ascendente por max_capacity
        available_objects.sort(key=lambda x: x.max_capacity)

        result.available_objects = [
            AvailableObjectInfo(
                id=obj.id,
                name=obj.name,
                min_capacity=obj.min_capacity,
                max_capacity=obj.max_capacity,
            )
            for obj in available_objects
        ]

        return result
