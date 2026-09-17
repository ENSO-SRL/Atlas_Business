from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.client_exceptions import BusinessNotVerifiedError
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository


@dataclass
class ListPublicServicesCommand:
    business_id: UUID


@dataclass
class PublicCustomFieldResult:
    id: UUID
    label: str
    required: bool
    data_type: str
    options: list[str] | None


@dataclass
class PublicServiceResult:
    id: UUID
    name: str
    occupation_duration_minutes: int
    exposes_end_time: bool
    billing_nature: str
    allows_manual_object_selection: bool
    agent_metadata: dict
    custom_fields: list[PublicCustomFieldResult]


class ListPublicServicesUseCase:
    """
    Lista todos los servicios publicados de un negocio verificado.
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

    async def execute(self, command: ListPublicServicesCommand) -> list[PublicServiceResult]:
        business = await self.business_repo.get_by_id(command.business_id)
        if not business or business.verification_status != VerificationStatus.VERIFIED:
            raise BusinessNotVerifiedError()

        services = await self.client_service_repo.list_published_by_business(command.business_id)
        result_list = []

        for s in services:
            metadata = await self.agent_metadata_repo.get_by_id(s.agent_metadata_id)
            metadata_dict = {
                "description": metadata.description if metadata else "",
                "establishment_policies": metadata.establishment_policies if metadata else [],
                "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
            }

            custom_fields = await self.custom_field_repo.list_by_service(s.id)
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

            result_list.append(
                PublicServiceResult(
                    id=s.id,
                    name=s.name,
                    occupation_duration_minutes=s.occupation_duration_minutes,
                    exposes_end_time=s.exposes_end_time,
                    billing_nature=s.billing_nature.value,
                    allows_manual_object_selection=s.allows_manual_object_selection,
                    agent_metadata=metadata_dict,
                    custom_fields=public_fields,
                )
            )

        return result_list
