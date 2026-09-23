from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.Domain.Entities.business import Business
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_client_business_repository import IClientBusinessRepository
from src.Infrastructure.Persistence.Models.business_model import BusinessModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository
from src.Infrastructure.Persistence.Repositories.business_repository import BusinessRepository


class ClientBusinessRepository(BaseRepository, IClientBusinessRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_published(self, category_id: UUID | None, page: int, page_size: int) -> tuple[list[Business], int]:
        base_stmt = select(BusinessModel).where(
            BusinessModel.verification_status == VerificationStatus.VERIFIED.value
        )

        if category_id:
            base_stmt = base_stmt.where(BusinessModel.category_id == category_id)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one_or_none() or 0

        stmt = (
            base_stmt
            .order_by(BusinessModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        
        # Reusing the _to_entity mapper from BusinessRepository
        return [BusinessRepository._to_entity(m) for m in result.scalars().all()], total
