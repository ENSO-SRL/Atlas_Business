from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Admin.business_category_use_cases import (
    CreateBusinessCategoryCommand, CreateBusinessCategoryUseCase,
    ListBusinessCategoriesQuery, ListBusinessCategoriesUseCase,
    UpdateBusinessCategoryCommand, UpdateBusinessCategoryUseCase,
    DeleteBusinessCategoryCommand, DeleteBusinessCategoryUseCase,
)
from src.Application.UseCases.Admin.service_category_use_cases import (
    CreateServiceCategoryCommand, CreateServiceCategoryUseCase,
    ListServiceCategoriesQuery, ListServiceCategoriesUseCase,
    UpdateServiceCategoryCommand, UpdateServiceCategoryUseCase,
    DeleteServiceCategoryCommand, DeleteServiceCategoryUseCase,
)
from src.Domain.Ports.Repositories.i_business_category_repository import IBusinessCategoryRepository
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Presentation.Dependencies.auth import UserContext, require_superadmin
from src.Presentation.Dependencies.repositories import get_business_category_repo, get_service_category_repo
from pydantic import BaseModel


# ─── Schemas locales ───

class CategoryBodyRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateCategoryRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


# ─── Router ───

router = APIRouter()


# ─── Business Categories ───

@router.post("/business-categories", status_code=201)
async def create_business_category(
    body: CategoryBodyRequest,
    _: UserContext = Depends(require_superadmin),
    repo: IBusinessCategoryRepository = Depends(get_business_category_repo),
):
    use_case = CreateBusinessCategoryUseCase(repo)
    result = await use_case.execute(CreateBusinessCategoryCommand(name=body.name, description=body.description))
    return result


@router.get("/business-categories")
async def list_business_categories(
    only_active: bool = True,
    _: UserContext = Depends(require_superadmin),
    repo: IBusinessCategoryRepository = Depends(get_business_category_repo),
):
    use_case = ListBusinessCategoriesUseCase(repo)
    result = await use_case.execute(ListBusinessCategoriesQuery(only_active=only_active))
    return {"items": result}


@router.patch("/business-categories/{category_id}")
async def update_business_category(
    category_id: UUID,
    body: UpdateCategoryRequest,
    _: UserContext = Depends(require_superadmin),
    repo: IBusinessCategoryRepository = Depends(get_business_category_repo),
):
    use_case = UpdateBusinessCategoryUseCase(repo)
    result = await use_case.execute(UpdateBusinessCategoryCommand(
        category_id=category_id,
        name=body.name,
        description=body.description,
        is_active=body.is_active,
    ))
    return result


@router.delete("/business-categories/{category_id}", status_code=204)
async def delete_business_category(
    category_id: UUID,
    _: UserContext = Depends(require_superadmin),
    repo: IBusinessCategoryRepository = Depends(get_business_category_repo),
):
    use_case = DeleteBusinessCategoryUseCase(repo)
    await use_case.execute(DeleteBusinessCategoryCommand(category_id=category_id))
    return None


# ─── Service Categories ───

@router.post("/service-categories", status_code=201)
async def create_service_category(
    body: CategoryBodyRequest,
    _: UserContext = Depends(require_superadmin),
    repo: IServiceCategoryRepository = Depends(get_service_category_repo),
):
    use_case = CreateServiceCategoryUseCase(repo)
    result = await use_case.execute(CreateServiceCategoryCommand(name=body.name, description=body.description))
    return result


@router.get("/service-categories")
async def list_service_categories(
    only_active: bool = True,
    _: UserContext = Depends(require_superadmin),
    repo: IServiceCategoryRepository = Depends(get_service_category_repo),
):
    use_case = ListServiceCategoriesUseCase(repo)
    result = await use_case.execute(ListServiceCategoriesQuery(only_active=only_active))
    return {"items": result}


@router.patch("/service-categories/{category_id}")
async def update_service_category(
    category_id: UUID,
    body: UpdateCategoryRequest,
    _: UserContext = Depends(require_superadmin),
    repo: IServiceCategoryRepository = Depends(get_service_category_repo),
):
    use_case = UpdateServiceCategoryUseCase(repo)
    result = await use_case.execute(UpdateServiceCategoryCommand(
        category_id=category_id,
        name=body.name,
        description=body.description,
        is_active=body.is_active,
    ))
    return result


@router.delete("/service-categories/{category_id}", status_code=204)
async def delete_service_category(
    category_id: UUID,
    _: UserContext = Depends(require_superadmin),
    repo: IServiceCategoryRepository = Depends(get_service_category_repo),
):
    use_case = DeleteServiceCategoryUseCase(repo)
    await use_case.execute(DeleteServiceCategoryCommand(category_id=category_id))
    return None
