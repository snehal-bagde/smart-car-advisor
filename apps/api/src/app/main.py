from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.response import APIResponse
from app.routes.car_recommendation_routes import router as car_recommendation_router

app = FastAPI(title="Smart Car Advisor API")

# Dev-only: allows the Next.js frontend (localhost:3000) to call this API from the
# browser. Revisit with an env-driven allow-list before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    response = APIResponse(
        success=False,
        message=exc.message,
        error={"code": exc.error_code, "details": exc.details},
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    response = APIResponse(
        success=False,
        message="Request payload failed validation.",
        error={"code": "validation_error", "details": {"errors": exc.errors()}},
    )
    return JSONResponse(status_code=422, content=response.model_dump())


app.include_router(car_recommendation_router, prefix="/api/v1")
