from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.Domain.Entities.booking import Booking


@dataclass
class OccupiedGroup:
    start_time: datetime
    end_time: datetime
    count: int


class IClientBookingRepository(ABC):
    """
    Puerto de repositorio de reservas para la Client API, optimizado
    para consultas de disponibilidad consolidadas.
    """

    @abstractmethod
    async def get_occupied_groups(
        self,
        object_ids: list[UUID],
        day_start: datetime,
        day_end: datetime,
    ) -> list[OccupiedGroup]:
        """
        Ejecuta el query agrupado del algoritmo de disponibilidad:

            SELECT start_time, end_time, COUNT(*) as count
            FROM booking
            WHERE bookable_object_id IN (:object_ids)
              AND start_time < :day_end
              AND end_time > :day_start
            GROUP BY start_time, end_time

        Devuelve los grupos colapsados — no filas individuales.
        """
        pass

    @abstractmethod
    async def get_occupied_object_ids(
        self,
        object_ids: list[UUID],
        slot_start: datetime,
        slot_end: datetime,
    ) -> set[UUID]:
        """
        Devuelve los IDs de los objetos específicos que están ocupados
        en la ventana [slot_start, slot_end).

            SELECT DISTINCT bookable_object_id FROM booking
            WHERE bookable_object_id IN (:ids)
              AND start_time < :slot_end AND end_time > :slot_start
        """
        pass

    @abstractmethod
    async def create(self, entity: Booking) -> Booking:
        """
        Inserta la reserva. 
        Nota para la implementación: Si se viola el exclusion constraint GiST,
        lanzar una excepción que la capa superior pueda mapear a SlotNoLongerAvailableError.
        """
        pass
