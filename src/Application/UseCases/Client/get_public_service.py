from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.client_exceptions import BusinessNotVerifiedError, ServiceNotPublicError
from src.Application.UseCases.Client.list_public_services import PublicCustomFieldResult, PublicServiceResult
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository


@dataclass
class GetPublicServiceCommand:
    business_id: UUID
    service_id: UUID


class GetPublicServiceUseCase:
    """
    Detalle completo de un servicio publicado para el cliente.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        client_service_repo: IClientServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        custom_field_repo: ICustomFieldRepository,
    ):
        self.business_repo = business_repo
        self.client_service_repo = client_service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.custom_field_repo = custom_field_repo

    async def execute(self, command: GetPublicServiceCommand) -> PublicServiceResult:
        business = await self.business_repo.get_by_id(command.business_id)
        if not business or business.verification_status != VerificationStatus.VERIFIED:
            raise BusinessNotVerifiedError()

        service = await self.client_service_repo.get_published_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotPublicError()

        metadata = await self.agent_metadata_repo.get_by_id(service.agent_metadata_id)
        metadata_dict = {
            "description": metadata.description if metadata else "",
            "establishment_policies": metadata.establishment_policies if metadata else [],
            "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
        }

        custom_fields = await self.custom_field_repo.list_by_service(service.id)
        public_fields = [
            PublicCustomFieldResult(
                id=cf.id,
                label=cf.label,
                required=cf.required,
                data_type=cf.data_type.value,
                options=cf.options,
            )
            for cf in sorted(custom_fields, key=lambda x: x.order)
            if cf.visible_to_client
        ]

        return PublicServiceResult(
            id=service.id,
            name=service.name,
            occupation_duration_minutes=service.occupation_duration_minutes,
            exposes_end_time=service.exposes_end_time,
            billing_nature=service.billing_nature.value,
            allows_manual_object_selection=service.allows_manual_object_selection,
            agent_metadata=metadata_dict,
            custom_fields=public_fields,
        )
