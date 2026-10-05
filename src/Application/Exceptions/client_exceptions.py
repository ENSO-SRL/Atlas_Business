from uuid import UUID

from src.Application.Exceptions.business_exceptions import ApplicationError


class BusinessNotVerifiedError(ApplicationError):
    def __init__(self):
        super().__init__("El negocio no fue encontrado o no está verificado.")


class ServiceNotPublicError(ApplicationError):
    def __init__(self):
        super().__init__("El servicio no fue encontrado o no está publicado.")


class InvalidPartySizeError(ApplicationError):
    def __init__(self):
        super().__init__("party_size debe ser >= 1.")


class InvalidDateError(ApplicationError):
    def __init__(self):
        super().__init__("La fecha no puede ser en el pasado.")


class BookingWindowExceededError(ApplicationError):
    def __init__(self):
        super().__init__("Esos horarios aún no están disponibles para reserva.")


class MinimumBookingNoticeRequiredError(ApplicationError):
    def __init__(self):
        super().__init__("El horario solicitado ya no está disponible por restricción de tiempo anticipado.")


class DailyBookingLimitExceededError(ApplicationError):
    def __init__(self):
        super().__init__("Has alcanzado el límite máximo de reservas por día en este servicio.")


class SlotNoLongerAvailableError(ApplicationError):
    def __init__(self):
        super().__init__("El slot solicitado ya no tiene objetos disponibles. Por favor, consulta la disponibilidad nuevamente.")


class CustomFieldValidationError(ApplicationError):
    def __init__(self, errors: list[str]):
        # errors es una lista de mensajes devueltos por validate_response
        msg = "Error en los campos personalizados: " + "; ".join(errors)
        super().__init__(msg)
        self.errors = errors
