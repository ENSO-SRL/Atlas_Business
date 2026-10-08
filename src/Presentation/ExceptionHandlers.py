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
    BusinessCategoryNotFoundError,
    ServiceCategoryNotFoundError,
    InvalidRncError,
    VerticalMetadataValidationError,
    InvalidBookingStateTransitionError,
    InvalidScheduleError,
    BookableObjectNotFoundError,
    CustomFieldNotFoundError,
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
    RatesRequiredForBillableServiceError,
    EmailAlreadyVerifiedError,
    EmailNotVerifiedError,
    InvalidEmailTokenError,
    CategoryNameAlreadyExistsError,
)

from src.Application.Exceptions.client_exceptions import (
    BusinessNotVerifiedError,
    ServiceNotPublicError,
    InvalidPartySizeError,
    SlotNoLongerAvailableError,
    CustomFieldValidationError,
    BookingWindowExceededError,
    MinimumBookingNoticeRequiredError,
    DailyBookingLimitExceededError,
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

    @app.exception_handler(InvalidBookingStateTransitionError)
    async def booking_state_transition_handler(request: Request, exc: InvalidBookingStateTransitionError):
        return JSONResponse(status_code=400, content={"error": "INVALID_BOOKING_STATE_TRANSITION", "detail": str(exc)})

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

    @app.exception_handler(BookingWindowExceededError)
    async def booking_window_exceeded_handler(request: Request, exc: BookingWindowExceededError):
        return JSONResponse(status_code=400, content={"error": "BOOKING_WINDOW_EXCEEDED", "detail": str(exc)})

    @app.exception_handler(MinimumBookingNoticeRequiredError)
    async def minimum_booking_notice_handler(request: Request, exc: MinimumBookingNoticeRequiredError):
        return JSONResponse(status_code=400, content={"error": "MINIMUM_BOOKING_NOTICE_REQUIRED", "detail": str(exc)})

    @app.exception_handler(DailyBookingLimitExceededError)
    async def daily_booking_limit_exceeded_handler(request: Request, exc: DailyBookingLimitExceededError):
        return JSONResponse(status_code=400, content={"error": "DAILY_BOOKING_LIMIT_EXCEEDED", "detail": str(exc)})

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

    @app.exception_handler(VerticalMetadataValidationError)
    async def vertical_metadata_validation_handler(request: Request, exc: VerticalMetadataValidationError):
        return JSONResponse(status_code=400, content={"error": "VERTICAL_METADATA_INVALID", "detail": str(exc)})

    @app.exception_handler(InvalidScheduleError)
    async def invalid_schedule_handler(request: Request, exc: InvalidScheduleError):
        return JSONResponse(status_code=400, content={"error": "INVALID_SCHEDULE", "detail": str(exc)})

    @app.exception_handler(BookableObjectNotFoundError)
    async def bookable_object_not_found_handler(request: Request, exc: BookableObjectNotFoundError):
        return JSONResponse(status_code=404, content={"error": "BOOKABLE_OBJECT_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(CustomFieldNotFoundError)
    async def custom_field_not_found_handler(request: Request, exc: CustomFieldNotFoundError):
        return JSONResponse(status_code=404, content={"error": "CUSTOM_FIELD_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(CustomerAlreadyExistsError)
    async def customer_already_exists_handler(request: Request, exc: CustomerAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": "CUSTOMER_ALREADY_EXISTS", "detail": str(exc)})

    @app.exception_handler(CustomerNotFoundError)
    async def customer_not_found_handler(request: Request, exc: CustomerNotFoundError):
        return JSONResponse(status_code=404, content={"error": "CUSTOMER_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(RatesRequiredForBillableServiceError)
    async def rates_required_handler(request: Request, exc: RatesRequiredForBillableServiceError):
        return JSONResponse(status_code=422, content={"error": "RATES_REQUIRED_FOR_BILLABLE_SERVICE", "detail": str(exc)})

    @app.exception_handler(EmailAlreadyVerifiedError)
    async def email_already_verified_handler(request: Request, exc: EmailAlreadyVerifiedError):
        return JSONResponse(status_code=409, content={"error": "EMAIL_ALREADY_VERIFIED", "detail": str(exc)})

    @app.exception_handler(EmailNotVerifiedError)
    async def email_not_verified_handler(request: Request, exc: EmailNotVerifiedError):
        return JSONResponse(status_code=403, content={"error": "EMAIL_NOT_VERIFIED", "detail": str(exc)})

    @app.exception_handler(InvalidEmailTokenError)
    async def invalid_email_token_handler(request: Request, exc: InvalidEmailTokenError):
        return JSONResponse(status_code=400, content={"error": "INVALID_EMAIL_TOKEN", "detail": str(exc)})

    @app.exception_handler(CategoryNameAlreadyExistsError)
    async def category_name_already_exists_handler(request: Request, exc: CategoryNameAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": "CATEGORY_NAME_ALREADY_EXISTS", "detail": str(exc)})

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

    @app.exception_handler(BusinessCategoryNotFoundError)
    async def business_category_not_found_handler(request: Request, exc: BusinessCategoryNotFoundError):
        return JSONResponse(status_code=404, content={"error": "BUSINESS_CATEGORY_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(ServiceCategoryNotFoundError)
    async def service_category_not_found_handler(request: Request, exc: ServiceCategoryNotFoundError):
        return JSONResponse(status_code=404, content={"error": "SERVICE_CATEGORY_NOT_FOUND", "detail": str(exc)})

    @app.exception_handler(InvalidRncError)
    async def invalid_rnc_handler(request: Request, exc: InvalidRncError):
        return JSONResponse(status_code=422, content={"error": "INVALID_RNC", "detail": str(exc)})
