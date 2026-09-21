from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.Application.Exceptions.business_exceptions import (
    BusinessNotFoundError,
    ServiceNotFoundError,
    EmailAlreadyInUseError,
    BusinessCodeAlreadyExistsError,
    RatesCoverageIncompleteError,
    ServiceNotPublishedError,
    UserNotFoundError,
    BookingNotFoundError,
)

from src.Application.Exceptions.client_exceptions import (
    BusinessNotVerifiedError,
    ServiceNotPublicError,
    InvalidPartySizeError,
    SlotNoLongerAvailableError,
    CustomFieldValidationError,
)

# Excepciones de Infraestructura
from src.Infrastructure.Persistence.Repositories.exceptions import SlotAlreadyBookedInfraError


def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(BusinessNotFoundError)
    async def business_not_found_handler(request: Request, exc: BusinessNotFoundError):
        return JSONResponse(status_code=404, content={"error": "BUSINESS_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(ServiceNotFoundError)
    async def service_not_found_handler(request: Request, exc: ServiceNotFoundError):
        return JSONResponse(status_code=404, content={"error": "SERVICE_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(EmailAlreadyInUseError)
    async def email_in_use_handler(request: Request, exc: EmailAlreadyInUseError):
        return JSONResponse(status_code=409, content={"error": "EMAIL_ALREADY_IN_USE", "detail": str(exc)})

    @app.exception_handler(BusinessCodeAlreadyExistsError)
    async def business_code_exists_handler(request: Request, exc: BusinessCodeAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": "BUSINESS_CODE_EXISTS", "detail": str(exc)})

    @app.exception_handler(RatesCoverageIncompleteError)
    async def rates_coverage_handler(request: Request, exc: RatesCoverageIncompleteError):
        return JSONResponse(status_code=422, content={"error": "RATES_COVERAGE_INCOMPLETE", "detail": str(exc)})

    @app.exception_handler(CustomFieldValidationError)
    async def custom_field_validation_handler(request: Request, exc: CustomFieldValidationError):
        return JSONResponse(status_code=422, content={"error": "CUSTOM_FIELD_INVALID", "errors": exc.errors})

    @app.exception_handler(BusinessNotVerifiedError)
    async def business_not_verified_handler(request: Request, exc: BusinessNotVerifiedError):
        return JSONResponse(status_code=404, content={"error": "BUSINESS_NOT_VERIFIED", "detail": str(exc)})

    @app.exception_handler(ServiceNotPublicError)
    async def service_not_public_handler(request: Request, exc: ServiceNotPublicError):
        return JSONResponse(status_code=404, content={"error": "SERVICE_NOT_PUBLIC", "detail": str(exc)})

    @app.exception_handler(InvalidPartySizeError)
    async def invalid_party_size_handler(request: Request, exc: InvalidPartySizeError):
        return JSONResponse(status_code=400, content={"error": "INVALID_PARTY_SIZE", "detail": str(exc)})

    @app.exception_handler(SlotNoLongerAvailableError)
    async def slot_no_longer_available_handler(request: Request, exc: SlotNoLongerAvailableError):
        return JSONResponse(status_code=409, content={"error": "SLOT_NO_LONGER_AVAILABLE", "detail": str(exc)})

    @app.exception_handler(ServiceNotPublishedError)
    async def service_not_published_handler(request: Request, exc: ServiceNotPublishedError):
        return JSONResponse(status_code=409, content={"error": "SERVICE_NOT_PUBLISHED", "detail": str(exc)})

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(status_code=404, content={"error": "USER_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(BookingNotFoundError)
    async def booking_not_found_handler(request: Request, exc: BookingNotFoundError):
        return JSONResponse(status_code=404, content={"error": "BOOKING_NOT_FOUND", "detail": str(exc)})

    # Infra Exceptions
    
    @app.exception_handler(SlotAlreadyBookedInfraError)
    async def slot_already_booked_infra_handler(request: Request, exc: SlotAlreadyBookedInfraError):
        return JSONResponse(
            status_code=409, 
            content={
                "error": "SLOT_NO_LONGER_AVAILABLE", 
                "detail": "El slot ya fue reservado por otro usuario (Exclusion Constraint)."
            }
        )
