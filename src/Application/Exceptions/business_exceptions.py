class ApplicationError(Exception):
    """Base exception for all application layer errors."""
    pass


class BusinessCodeAlreadyExistsError(ApplicationError):
    def __init__(self, code: str):
        super().__init__(f"El código de negocio '{code}' ya está en uso.")


class BusinessNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("El negocio no fue encontrado.")


class ServiceNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("El servicio no fue encontrado o no pertenece al negocio.")


class ServiceNotPublishedError(ApplicationError):
    def __init__(self):
        super().__init__("Solo se pueden solicitar ediciones (shadow edit) sobre servicios publicados.")


class EmailAlreadyInUseError(ApplicationError):
    def __init__(self, email: str):
        super().__init__(f"El email '{email}' ya está registrado en este negocio.")


class UserNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("El usuario no fue encontrado o no pertenece al negocio.")


class BookableObjectNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("El objeto reservable no fue encontrado o no pertenece al servicio.")


class CustomFieldNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("El campo personalizado no fue encontrado o no pertenece al servicio.")


class BookingNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("La reserva no fue encontrada o no pertenece al negocio.")


class RatesCoverageIncompleteError(ApplicationError):
    def __init__(self, weekday: str, gap_start: str, gap_end: str):
        super().__init__(
            f"El horario del {weekday} entre {gap_start} y {gap_end} no está cubierto por ninguna tarifa."
        )


class EmailAlreadyVerifiedError(ApplicationError):
    def __init__(self):
        super().__init__("El email ya ha sido verificado.")


class EmailNotVerifiedError(ApplicationError):
    def __init__(self):
        super().__init__("Debes confirmar tu correo electrónico antes de iniciar sesión.")


class InvalidEmailTokenError(ApplicationError):
    def __init__(self):
        super().__init__("El token es inválido, ya fue usado o ha expirado.")


class InvalidRncError(ApplicationError):
    def __init__(self, rnc: str):
        super().__init__(f"El RNC '{rnc}' no es válido o no está registrado en la DGII.")


class BusinessCategoryNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("La categoría de negocio no fue encontrada o no está activa.")


class ServiceCategoryNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("La categoría de servicio no fue encontrada o no está activa.")


class CategoryNameAlreadyExistsError(ApplicationError):
    def __init__(self, name: str):
        super().__init__(f"Ya existe una categoría con el nombre '{name}'.")
