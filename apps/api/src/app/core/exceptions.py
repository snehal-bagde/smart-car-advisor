class AppException(Exception):
    """Base class for all application exceptions."""

    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, **details):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = 404
    error_code = "not_found"


class ValidationError(AppException):
    status_code = 422
    error_code = "validation_error"


class ConflictError(AppException):
    status_code = 409
    error_code = "conflict"


class NoMatchingCarsError(NotFoundError):
    error_code = "no_matching_cars"
    message = "No cars match the given criteria, even after relaxing optional filters."
