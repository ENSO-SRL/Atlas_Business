from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from typing import Any
from src.Application.Exceptions.business_exceptions import BusinessNotFoundError, VerticalMetadataValidationError
from src.Application.UseCases.Business.get_my_business import BusinessProfileResult, GetMyBusinessCommand, GetMyBusinessUseCase
from src.Application.UseCases.Business.register_business import ScheduleInput
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Services.vertical_validator_registry import VerticalValidatorRegistry


@dataclass
class AgentMetadataInput:
    description: str | None = None
    establishment_policies: list[str] | None = None
    pre_booking_requirements: list[str] | None = None


@dataclass
class UpdateBusinessCommand:
    business_id: UUID
    actor_id: UUID  # Para updated_by
    name: str | None = None
    phone: str | None = None
    province: str | None = None
    municipality: str | None = None
    neighborhood: str | None = None
    street_address: str | None = None
    reference: str | None = None
    maps_url: str | None = None
    aliases: list[str] | None = None
    schedules: list[ScheduleInput] | None = None
    agent_metadata: AgentMetadataInput | None = None
    vertical_metadata: dict[str, Any] | None = None


class UpdateBusinessUseCase:
    """
    Actualiza el perfil del negocio y/o su metadata. Solo los campos presentes (no None) se modifican.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        agent_metadata_repo: IAgentMetadataRepository,
    ):
        self.business_repo = business_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.get_use_case = GetMyBusinessUseCase(business_repo, agent_metadata_repo)
        self.vertical_registry = VerticalValidatorRegistry()

    async def execute(self, command: UpdateBusinessCommand) -> BusinessProfileResult:
        business = await self.business_repo.get_by_id(command.business_id)
        if not business:
            raise BusinessNotFoundError()

        metadata = await self.agent_metadata_repo.get_by_id(business.agent_metadata_id)
        now_utc = datetime.now(timezone.utc)

        # 1. Update Business fields
        business_changed = False
        if command.name is not None:
            business.name = command.name
            business_changed = True
        if command.phone is not None:
            business.phone = command.phone
            business_changed = True
        if command.province is not None:
            business.province = command.province
            business_changed = True
        if command.municipality is not None:
            business.municipality = command.municipality
            business_changed = True
        if command.neighborhood is not None:
            business.neighborhood = command.neighborhood
            business_changed = True
        if command.street_address is not None:
            business.street_address = command.street_address
            business_changed = True
        if command.reference is not None:
            business.reference = command.reference
            business_changed = True
        if command.maps_url is not None:
            business.maps_url = command.maps_url
            business_changed = True
        if command.aliases is not None:
            business.aliases = command.aliases
            business_changed = True
        if command.schedules is not None:
            business.schedules = [
                {"weekday": s.weekday, "opening_time": s.opening_time, "closing_time": s.closing_time}
                for s in command.schedules
            ]
            business_changed = True
            
        if command.vertical_metadata is not None:
            # Validar con la categoría actual
            validator = self.vertical_registry.get_validator(business.category_name)
            is_valid, error_msg = validator.validate(command.vertical_metadata)
            if not is_valid:
                raise VerticalMetadataValidationError(error_msg or "Estructura inválida.")
            business.vertical_metadata = command.vertical_metadata
            business_changed = True

        if business_changed:
            business.updated_at = now_utc
            business.updated_by = command.actor_id
            await self.business_repo.update(business)

        # 2. Update AgentMetadata fields
        if metadata and command.agent_metadata:
            metadata_changed = False
            if command.agent_metadata.description is not None:
                metadata.description = command.agent_metadata.description
                metadata_changed = True
            if command.agent_metadata.establishment_policies is not None:
                metadata.establishment_policies = command.agent_metadata.establishment_policies
                metadata_changed = True
            if command.agent_metadata.pre_booking_requirements is not None:
                metadata.pre_booking_requirements = command.agent_metadata.pre_booking_requirements
                metadata_changed = True

            if metadata_changed:
                metadata.updated_at = now_utc
                metadata.updated_by = command.actor_id
                await self.agent_metadata_repo.update(metadata)

        # 3. Return updated profile
        return await self.get_use_case.execute(GetMyBusinessCommand(business_id=command.business_id))
