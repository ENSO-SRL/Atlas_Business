from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Repositories.i_token_blacklist_repository import ITokenBlacklistRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Infrastructure.Persistence.Repositories.agent_metadata_repository import AgentMetadataRepository
from src.Infrastructure.Persistence.Repositories.bookable_object_repository import BookableObjectRepository
from src.Infrastructure.Persistence.Repositories.booking_repository import BookingRepository
from src.Infrastructure.Persistence.Repositories.business_repository import BusinessRepository
from src.Infrastructure.Persistence.Repositories.business_user_repository import BusinessUserRepository
from src.Infrastructure.Persistence.Repositories.client_booking_repository import ClientBookingRepository
from src.Infrastructure.Persistence.Repositories.client_service_repository import ClientServiceRepository
from src.Infrastructure.Persistence.Repositories.content_request_repository import ContentRequestRepository
from src.Infrastructure.Persistence.Repositories.custom_field_repository import CustomFieldRepository
from src.Infrastructure.Persistence.Repositories.service_rate_repository import ServiceRateRepository
from src.Infrastructure.Persistence.Repositories.service_repository import ServiceRepository
from src.Infrastructure.Persistence.Repositories.token_blacklist_repository import TokenBlacklistRepository
from src.Infrastructure.Persistence.Repositories.user_repository import UserRepository
from src.Presentation.Dependencies.db import get_session


def get_agent_metadata_repo(session: AsyncSession = Depends(get_session)) -> IAgentMetadataRepository:
    return AgentMetadataRepository(session)


def get_bookable_object_repo(session: AsyncSession = Depends(get_session)) -> IBookableObjectRepository:
    return BookableObjectRepository(session)


def get_booking_repo(session: AsyncSession = Depends(get_session)) -> IBookingRepository:
    return BookingRepository(session)


def get_business_repo(session: AsyncSession = Depends(get_session)) -> IBusinessRepository:
    return BusinessRepository(session)


def get_business_user_repo(session: AsyncSession = Depends(get_session)) -> IBusinessUserRepository:
    return BusinessUserRepository(session)


def get_client_booking_repo(session: AsyncSession = Depends(get_session)) -> IClientBookingRepository:
    return ClientBookingRepository(session)


def get_client_service_repo(session: AsyncSession = Depends(get_session)) -> IClientServiceRepository:
    return ClientServiceRepository(session)


def get_content_request_repo(session: AsyncSession = Depends(get_session)) -> IContentRequestRepository:
    return ContentRequestRepository(session)


def get_custom_field_repo(session: AsyncSession = Depends(get_session)) -> ICustomFieldRepository:
    return CustomFieldRepository(session)


def get_service_rate_repo(session: AsyncSession = Depends(get_session)) -> IServiceRateRepository:
    return ServiceRateRepository(session)


def get_service_repo(session: AsyncSession = Depends(get_session)) -> IServiceRepository:
    return ServiceRepository(session)


def get_token_blacklist_repo(session: AsyncSession = Depends(get_session)) -> ITokenBlacklistRepository:
    return TokenBlacklistRepository(session)


def get_user_repo(session: AsyncSession = Depends(get_session)) -> IUserRepository:
    return UserRepository(session)
