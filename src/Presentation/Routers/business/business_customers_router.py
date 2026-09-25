from fastapi import APIRouter, Depends, Query
from uuid import UUID

from src.Application.UseCases.Business.list_business_customers import (
    ListBusinessCustomersCommand,
    ListBusinessCustomersUseCase,
)
from src.Application.UseCases.Business.list_customer_bookings import (
    ListCustomerBookingsCommand,
    ListCustomerBookingsUseCase,
)
from src.Application.UseCases.Business.create_business_customer import (
    CreateBusinessCustomerCommand,
    CreateBusinessCustomerUseCase,
)
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository
from src.Presentation.Dependencies.auth import UserContext, require_admin
from src.Presentation.Dependencies.repositories import get_booking_repo, get_business_customer_repo
from src.Presentation.Schemas.business_schemas import (
    PaginatedBusinessCustomerResponse,
    PaginatedCustomerBookingResponse,
    CreateCustomerRequest,
)

router = APIRouter(prefix="/customers", tags=["Business Customers"])


@router.get("/", response_model=PaginatedBusinessCustomerResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(require_admin),
    customer_repo: IBusinessCustomerRepository = Depends(get_business_customer_repo),
):
    use_case = ListBusinessCustomersUseCase(customer_repo)
    command = ListBusinessCustomersCommand(
        business_id=user.business_id,
        page=page,
        page_size=page_size,
    )
    items, total = await use_case.execute(command)
    return {"items": items, "total": total}


@router.post("/", status_code=201)
async def create_customer(
    body: CreateCustomerRequest,
    user: UserContext = Depends(require_admin),
    customer_repo: IBusinessCustomerRepository = Depends(get_business_customer_repo),
):
    use_case = CreateBusinessCustomerUseCase(customer_repo)
    command = CreateBusinessCustomerCommand(
        business_id=user.business_id,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        email=body.email,
        gender=body.gender,
    )
    result = await use_case.execute(command)
    return result


@router.get("/{customer_id}/bookings", response_model=PaginatedCustomerBookingResponse)
async def list_customer_bookings(
    customer_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(require_admin),
    booking_repo: IBookingRepository = Depends(get_booking_repo),
):
    use_case = ListCustomerBookingsUseCase(booking_repo)
    command = ListCustomerBookingsCommand(
        business_id=user.business_id,
        customer_id=customer_id,
        page=page,
        page_size=page_size,
    )
    items, total = await use_case.execute(command)
    return {"items": items, "total": total}
