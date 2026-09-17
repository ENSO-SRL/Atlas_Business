# Importar todos los modelos aquí garantiza que SQLAlchemy los registre en el metadata
# de Base antes de que Alembic genere migraciones o se cree el schema.
from .agent_metadata_model import AgentMetadataModel
from .bookable_object_model import BookableObjectModel
from .booking_model import BookingModel
from .business_model import BusinessModel
from .business_user_model import BusinessUserModel
from .content_request_model import ContentRequestModel
from .custom_field_model import CustomFieldModel
from .service_model import ServiceModel
from .service_rate_model import ServiceRateModel

__all__ = [
    "AgentMetadataModel",
    "BookableObjectModel",
    "BookingModel",
    "BusinessModel",
    "BusinessUserModel",
    "ContentRequestModel",
    "CustomFieldModel",
    "ServiceModel",
    "ServiceRateModel",
]
