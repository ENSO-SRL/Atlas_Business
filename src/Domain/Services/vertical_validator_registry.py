from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator
from src.Domain.Services.VerticalValidators.generic_validator import GenericVerticalValidator
from src.Domain.Services.VerticalValidators.Business.padel_validator import PadelVerticalValidator
from src.Domain.Services.VerticalValidators.Business.restaurant_validator import RestaurantBusinessValidator

class VerticalValidatorRegistry:
    """
    Registro que mapea nombres de categorías de negocio (verticales) 
    a sus respectivos validadores de metadatos.
    """
    
    def __init__(self):
        self._validators: dict[str, IVerticalValidator] = {
            "padel": PadelVerticalValidator(),
            "restaurante": RestaurantBusinessValidator(),
            # Puedes añadir más aquí en el futuro:
            # "canchas": CanchasVerticalValidator(),
            # "medico": MedicoVerticalValidator(),
        }
        self._default_validator = GenericVerticalValidator()

    def get_validator(self, category_name: str) -> IVerticalValidator:
        """
        Retorna el validador específico para la categoría.
        Si no hay uno registrado o el nombre es inválido/nulo, 
        retorna el validador genérico (fallback).
        """
        if not category_name:
            return self._default_validator
            
        key = category_name.lower().strip()
        return self._validators.get(key, self._default_validator)
