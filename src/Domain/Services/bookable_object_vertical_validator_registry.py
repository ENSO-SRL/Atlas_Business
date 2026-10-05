from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator
from src.Domain.Services.VerticalValidators.generic_validator import GenericVerticalValidator
from src.Domain.Services.VerticalValidators.restaurant_table_validator import RestaurantTableValidator

class BookableObjectVerticalValidatorRegistry:
    """
    Registro que mapea nombres de categorías de SERVICIO a sus 
    respectivos validadores de metadatos de OBJETOS RESERVABLES.
    """
    
    def __init__(self):
        self._validators: dict[str, IVerticalValidator] = {
            "restaurante": RestaurantTableValidator(),
        }
        self._default_validator = GenericVerticalValidator()

    def get_validator(self, category_name: str) -> IVerticalValidator:
        if not category_name:
            return self._default_validator
            
        key = category_name.lower().strip()
        return self._validators.get(key, self._default_validator)
