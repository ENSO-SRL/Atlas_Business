from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class RestaurantBusinessValidator(IVerticalValidator):
    """
    Validador específico para la vertical de Restaurantes a nivel de Negocio (Business).
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
            
        # restaurant_areas
        if "restaurant_areas" in metadata:
            if not isinstance(metadata["restaurant_areas"], list):
                return False, "El campo 'restaurant_areas' debe ser una lista."
            if not all(isinstance(x, str) for x in metadata["restaurant_areas"]):
                return False, "Los elementos de 'restaurant_areas' deben ser texto."

        # payment_options
        if "payment_options" in metadata:
            if not isinstance(metadata["payment_options"], list):
                return False, "El campo 'payment_options' debe ser una lista."
            if not all(isinstance(x, str) for x in metadata["payment_options"]):
                return False, "Los elementos de 'payment_options' deben ser texto."

        # price_range
        if "price_range" in metadata and not isinstance(metadata["price_range"], str):
            return False, "El campo 'price_range' debe ser texto."

        # dining_style
        if "dining_style" in metadata and not isinstance(metadata["dining_style"], str):
            return False, "El campo 'dining_style' debe ser texto."

        # gastronomic_style
        if "gastronomic_style" in metadata:
            val = metadata["gastronomic_style"]
            if not isinstance(val, (str, list)):
                return False, "El campo 'gastronomic_style' debe ser texto o una lista de textos."
            if isinstance(val, list) and not all(isinstance(x, str) for x in val):
                return False, "Los elementos de 'gastronomic_style' deben ser texto."

        # relevant_staff
        if "relevant_staff" in metadata:
            val = metadata["relevant_staff"]
            if not isinstance(val, (str, list)):
                return False, "El campo 'relevant_staff' debe ser texto o una lista de textos."
            if isinstance(val, list) and not all(isinstance(x, str) for x in val):
                return False, "Los elementos de 'relevant_staff' deben ser texto."

        # dress_code
        if "dress_code" in metadata and not isinstance(metadata["dress_code"], str):
            return False, "El campo 'dress_code' debe ser texto."

        # allows_pets
        if "allows_pets" in metadata and not isinstance(metadata["allows_pets"], bool):
            return False, "El campo 'allows_pets' debe ser booleano."

        # allows_children
        if "allows_children" in metadata and not isinstance(metadata["allows_children"], bool):
            return False, "El campo 'allows_children' debe ser booleano."

        # has_valet_parking
        if "has_valet_parking" in metadata and not isinstance(metadata["has_valet_parking"], bool):
            return False, "El campo 'has_valet_parking' debe ser booleano."

        # extra_services
        if "extra_services" in metadata:
            if not isinstance(metadata["extra_services"], list):
                return False, "El campo 'extra_services' debe ser una lista."
            for item in metadata["extra_services"]:
                if not isinstance(item, dict):
                    return False, "Cada elemento en 'extra_services' debe ser un objeto."
                if "name" in item and not isinstance(item["name"], str):
                    return False, "El 'name' de extra_services debe ser texto."
                if "items" in item:
                    if not isinstance(item["items"], list):
                        return False, "'items' dentro de extra_services debe ser una lista."
                    for subitem in item["items"]:
                        if not isinstance(subitem, dict):
                            return False, "Cada item en 'items' de extra_services debe ser un objeto."

        return True, None
