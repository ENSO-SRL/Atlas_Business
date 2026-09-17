from enum import Enum

class Platform(Enum):
    """
    Plataforma a la que pertenece el negocio, lo que define el vertical
    (Padel, Golf, Restaurante) y la plantilla de configuración de reserva por defecto.
    """
    PADEL = "PADEL"
    GOLF = "GOLF"
    RESTAURANT = "RESTAURANT"
