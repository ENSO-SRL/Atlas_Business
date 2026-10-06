from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.service import Service, DurationNature, BillingNature, AutoSelectionCriteria
from src.Domain.Entities.service_policies import (
    ArrivalAndConfirmationPolicy,
    ModificationPolicy,
    PaymentAndCancellationPolicy,
    PaymentMethod,
    PaymentSplit,
    PaymentStage,
)
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Infrastructure.Persistence.Models.service_model import ServiceModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository, IServiceRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: ServiceModel) -> Service:
        svc = Service(
            id=model.id,
            business_id=model.business_id,
            name=model.name,
            occupation_duration_minutes=model.occupation_duration_minutes,
            duration_nature=DurationNature(model.duration_nature),
            exposes_end_time=model.exposes_end_time,
            buffer_minutes=model.buffer_minutes,
            grid_interval_minutes=model.grid_interval_minutes,
            max_booking_window_days=model.max_booking_window_days,
            min_booking_window_hours=model.min_booking_window_hours,
            max_daily_bookings_per_user=model.max_daily_bookings_per_user,
            allows_manual_object_selection=model.allows_manual_object_selection,
            auto_selection_criteria=AutoSelectionCriteria(model.auto_selection_criteria),
            billing_nature=BillingNature(model.billing_nature),
            agent_metadata_id=model.agent_metadata_id,
            category_id=model.category_id,
            publication_status=PublicationStatus(model.publication_status),
            rejection_reason=model.rejection_reason,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            vertical_metadata=model.vertical_metadata or {},
        )

        if model.payment_splits is not None or model.cancellation_description is not None:
            splits = []
            for s in (model.payment_splits or []):
                splits.append(PaymentSplit(
                    stage=PaymentStage(s["stage"]),
                    percentage=s["percentage"],
                    allowed_methods=[PaymentMethod(m) for m in s.get("allowed_methods", [])]
                ))
            svc.payment_cancellation_policy = PaymentAndCancellationPolicy(
                payment_splits=splits,
                cancellation_description=model.cancellation_description,
                min_cancellation_margin_hours=model.min_cancellation_margin_hours,
                cancellation_fee=float(model.cancellation_fee) if model.cancellation_fee is not None else None,
            )

        if model.allows_same_day_reschedule is not None or model.allows_date_change is not None:
            svc.modification_policy = ModificationPolicy(
                allows_same_day_reschedule=model.allows_same_day_reschedule,
                allows_date_change=model.allows_date_change,
                date_change_margin_days=model.date_change_margin_days,
            )

        if model.wait_time_minutes is not None or model.release_automatically is not None:
            svc.arrival_confirmation_policy = ArrivalAndConfirmationPolicy(
                wait_time_minutes=model.wait_time_minutes,
                release_automatically=model.release_automatically,
            )

        return svc

    async def list_by_business(
        self, business_id: UUID, status: PublicationStatus | None = None
    ) -> list[Service]:
        stmt = select(ServiceModel).where(ServiceModel.business_id == business_id)
        if status is not None:
            stmt = stmt.where(ServiceModel.publication_status == status.value)
        stmt = stmt.order_by(ServiceModel.name)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, id: UUID, business_id: UUID) -> Service | None:
        stmt = select(ServiceModel).where(
            ServiceModel.id == id,
            ServiceModel.business_id == business_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: Service) -> Service:
        model = ServiceModel(
            id=entity.id,
            business_id=entity.business_id,
            name=entity.name,
            occupation_duration_minutes=entity.occupation_duration_minutes,
            duration_nature=entity.duration_nature.value,
            exposes_end_time=entity.exposes_end_time,
            buffer_minutes=entity.buffer_minutes,
            grid_interval_minutes=entity.grid_interval_minutes,
            max_booking_window_days=entity.max_booking_window_days,
            min_booking_window_hours=entity.min_booking_window_hours,
            max_daily_bookings_per_user=entity.max_daily_bookings_per_user,
            allows_manual_object_selection=entity.allows_manual_object_selection,
            auto_selection_criteria=entity.auto_selection_criteria.value,
            billing_nature=entity.billing_nature.value,
            agent_metadata_id=entity.agent_metadata_id,
            category_id=entity.category_id,
            publication_status=entity.publication_status.value,
            rejection_reason=entity.rejection_reason,
            vertical_metadata=entity.vertical_metadata,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )

        if entity.payment_cancellation_policy:
            pol = entity.payment_cancellation_policy
            model.payment_splits = [
                {
                    "stage": s.stage.value,
                    "percentage": s.percentage,
                    "allowed_methods": [m.value for m in s.allowed_methods],
                }
                for s in pol.payment_splits
            ] if pol.payment_splits else None
            model.cancellation_description = pol.cancellation_description
            model.min_cancellation_margin_hours = pol.min_cancellation_margin_hours
            model.cancellation_fee = pol.cancellation_fee

        if entity.modification_policy:
            pol = entity.modification_policy
            model.allows_same_day_reschedule = pol.allows_same_day_reschedule
            model.allows_date_change = pol.allows_date_change
            model.date_change_margin_days = pol.date_change_margin_days

        if entity.arrival_confirmation_policy:
            pol = entity.arrival_confirmation_policy
            model.wait_time_minutes = pol.wait_time_minutes
            model.release_automatically = pol.release_automatically

        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: Service) -> Service:
        stmt = (
            sa.update(ServiceModel)
            .where(ServiceModel.id == entity.id)
            .values(
                name=entity.name,
                buffer_minutes=entity.buffer_minutes,
                grid_interval_minutes=entity.grid_interval_minutes,
                max_booking_window_days=entity.max_booking_window_days,
                min_booking_window_hours=entity.min_booking_window_hours,
                max_daily_bookings_per_user=entity.max_daily_bookings_per_user,
                exposes_end_time=entity.exposes_end_time,
                publication_status=entity.publication_status.value,
                rejection_reason=entity.rejection_reason,
                vertical_metadata=entity.vertical_metadata,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )

        if entity.payment_cancellation_policy:
            pol = entity.payment_cancellation_policy
            stmt = stmt.values(
                payment_splits=[
                    {
                        "stage": s.stage.value,
                        "percentage": s.percentage,
                        "allowed_methods": [m.value for m in s.allowed_methods],
                    }
                    for s in pol.payment_splits
                ] if pol.payment_splits else None,
                cancellation_description=pol.cancellation_description,
                min_cancellation_margin_hours=pol.min_cancellation_margin_hours,
                cancellation_fee=pol.cancellation_fee,
            )
        else:
            stmt = stmt.values(
                payment_splits=None,
                cancellation_description=None,
                min_cancellation_margin_hours=None,
                cancellation_fee=None,
            )

        if entity.modification_policy:
            pol = entity.modification_policy
            stmt = stmt.values(
                allows_same_day_reschedule=pol.allows_same_day_reschedule,
                allows_date_change=pol.allows_date_change,
                date_change_margin_days=pol.date_change_margin_days,
            )
        else:
            stmt = stmt.values(
                allows_same_day_reschedule=None,
                allows_date_change=None,
                date_change_margin_days=None,
            )

        if entity.arrival_confirmation_policy:
            pol = entity.arrival_confirmation_policy
            stmt = stmt.values(
                wait_time_minutes=pol.wait_time_minutes,
                release_automatically=pol.release_automatically,
            )
        else:
            stmt = stmt.values(
                wait_time_minutes=None,
                release_automatically=None,
            )

        await self.session.execute(stmt)
        return entity
