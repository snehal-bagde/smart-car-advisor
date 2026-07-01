from pydantic import BaseModel


class APIResponse[T](BaseModel):
    success: bool = True
    message: str | None = None
    data: T | None = None
    error: dict | None = None


def success_response[T](data: T, message: str | None = None) -> APIResponse[T]:
    return APIResponse(success=True, message=message, data=data)
