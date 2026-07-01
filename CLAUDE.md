# CLAUDE.md — smart-car-advisor Project Conventions

This file is the single source of truth for how this project is built. Read this file
(and `PROGRESS.md`) at the start of every session, before writing any code.

## 1. Project Overview

`smart-car-advisor` is a monorepo containing:
- **`apps/api`** — backend, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**
- **`apps/web`** — frontend, built with **Next.js**

The project is built **feature by feature**, starting with a simple car recommendation
system. No feature beyond what's currently agreed should be scaffolded ahead of time
(e.g. no auth/signup until a feature actually needs it).

## 2. Repository Structure

```
smart-car-advisor/
├── CLAUDE.md
├── PROGRESS.md
├── README.md
├── .gitignore
└── apps/
    ├── api/                        # FastAPI backend
    │   ├── pyproject.toml          # uv-managed deps + ruff config
    │   ├── alembic.ini
    │   ├── alembic/versions/
    │   ├── .env.example
    │   ├── src/app/
    │   │   ├── main.py             # FastAPI() instance, mounts routers + exception handlers
    │   │   ├── core/
    │   │   │   ├── config.py       # pydantic-settings Settings
    │   │   │   ├── database.py     # engine, SessionLocal, get_db dependency, Base
    │   │   │   ├── exceptions.py   # centralized AppException hierarchy + handlers
    │   │   │   └── response.py     # centralized APIResponse envelope + helpers
    │   │   ├── routes/             # APIRouter definitions ONLY — path/method/DI wiring
    │   │   │   └── car_recommendation_routes.py
    │   │   ├── controllers/        # request/response shaping ONLY
    │   │   │   └── car_recommendation_controller.py
    │   │   ├── services/           # ALL business logic
    │   │   │   └── car_recommendation_service.py
    │   │   ├── repositories/       # ALL DB access — only layer touching SQLAlchemy Session
    │   │   │   └── car_recommendation_repository.py
    │   │   ├── models/             # SQLAlchemy ORM models only
    │   │   │   └── car.py
    │   │   └── schemas/            # Pydantic request/response schemas only
    │   │       └── car_recommendation_schemas.py
    │   └── tests/
    │       ├── conftest.py         # test-DB fixture, TestClient fixture, get_db override
    │       ├── routes/
    │       ├── services/
    │       └── repositories/
    └── web/                        # Next.js frontend
        ├── app/                    # App Router, one route segment per feature
        ├── components/
        ├── lib/                    # api client, utils
        └── types/
```

Each backend layer folder (`routes/`, `controllers/`, `services/`, `repositories/`,
`models/`, `schemas/`) holds one file per feature. `core/` is the only cross-cutting
folder — config, DB session setup, and centralized error/response handling live there
because they are genuinely shared by every feature.

## 3. Backend Architecture & Layering

| Layer | Folder | Responsibility |
|---|---|---|
| Routes | `routes/` | Define API endpoints (path, method, DI wiring) only. No business logic. |
| Controllers | `controllers/` | Handle request/response shaping: call the service, wrap the result via `success_response`. No business logic. |
| Services | `services/` | All business logic. Framework-agnostic — never touches a DB session or an HTTP request/response object. |
| Repositories | `repositories/` | All database access. The only layer allowed to use a SQLAlchemy `Session`. |
| Models | `models/` | SQLAlchemy ORM models only. Never imports Pydantic. |
| Schemas | `schemas/` | Pydantic request/response validation only. Never imports SQLAlchemy. |
| Core | `core/` | Config, DB session, centralized exceptions, centralized response envelope. |

### Dependency injection chain

```
get_db (Session) → Repository (Depends) → Service (Depends) → Controller (Depends) → Route handler (Depends)
```

Each layer is a plain class using constructor injection. Each layer has one
`get_<thing>` provider function that FastAPI wires in via `Depends`, so no layer ever
imports or instantiates the layer below it directly — this is what makes every layer
independently testable and swappable.

### Illustrative code sketch (per layer)

**`models/car.py`** — SQLAlchemy ORM model, no Pydantic:
```python
from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    fuel_type = Column(String, nullable=False)
```

**`schemas/car_recommendation_schemas.py`** — Pydantic validation, no SQLAlchemy:
```python
from pydantic import BaseModel

class CarRecommendationRequest(BaseModel):
    budget: float
    fuel_type: str

class CarRecommendationResponse(BaseModel):
    make: str
    model: str
    price: float
```

**`repositories/car_recommendation_repository.py`** — only place SQLAlchemy queries live:
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.car import Car

class CarRecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_max_price_and_fuel_type(self, max_price: float, fuel_type: str) -> list[Car]:
        return (
            self.db.query(Car)
            .filter(Car.price <= max_price, Car.fuel_type == fuel_type)
            .all()
        )

def get_car_recommendation_repository(db: Session = Depends(get_db)) -> CarRecommendationRepository:
    return CarRecommendationRepository(db)
```

**`services/car_recommendation_service.py`** — all business logic:
```python
from fastapi import Depends
from app.repositories.car_recommendation_repository import (
    CarRecommendationRepository, get_car_recommendation_repository,
)
from app.core.exceptions import NoCarsFoundError

class CarRecommendationService:
    def __init__(self, repository: CarRecommendationRepository):
        self.repository = repository

    def recommend(self, budget: float, fuel_type: str):
        candidates = self.repository.get_by_max_price_and_fuel_type(budget, fuel_type)
        if not candidates:
            raise NoCarsFoundError(budget=budget, fuel_type=fuel_type)
        return max(candidates, key=lambda c: c.price)  # best car within budget

def get_car_recommendation_service(
    repository: CarRecommendationRepository = Depends(get_car_recommendation_repository),
) -> CarRecommendationService:
    return CarRecommendationService(repository)
```

**`controllers/car_recommendation_controller.py`** — request/response shaping only:
```python
from fastapi import Depends
from app.services.car_recommendation_service import (
    CarRecommendationService, get_car_recommendation_service,
)
from app.schemas.car_recommendation_schemas import (
    CarRecommendationRequest, CarRecommendationResponse,
)
from app.core.response import APIResponse, success_response

class CarRecommendationController:
    def __init__(self, service: CarRecommendationService):
        self.service = service

    def recommend(self, request: CarRecommendationRequest) -> APIResponse[CarRecommendationResponse]:
        car = self.service.recommend(budget=request.budget, fuel_type=request.fuel_type)
        response = CarRecommendationResponse(make=car.make, model=car.model, price=car.price)
        return success_response(response, message="Car recommendation fetched successfully")

def get_car_recommendation_controller(
    service: CarRecommendationService = Depends(get_car_recommendation_service),
) -> CarRecommendationController:
    return CarRecommendationController(service)
```

**`routes/car_recommendation_routes.py`** — endpoint declaration only:
```python
from fastapi import APIRouter, Depends
from app.controllers.car_recommendation_controller import (
    CarRecommendationController, get_car_recommendation_controller,
)
from app.schemas.car_recommendation_schemas import (
    CarRecommendationRequest, CarRecommendationResponse,
)
from app.core.response import APIResponse

router = APIRouter(prefix="/car-recommendations", tags=["car-recommendations"])

@router.post("", response_model=APIResponse[CarRecommendationResponse])
def recommend_car(
    request: CarRecommendationRequest,
    controller: CarRecommendationController = Depends(get_car_recommendation_controller),
) -> APIResponse[CarRecommendationResponse]:
    return controller.recommend(request)
```

Pydantic validates the request body automatically from the `request: CarRecommendationRequest`
type annotation before the handler body ever runs — this is how payload validation is
enforced on every endpoint.

## 4. Centralized Response & Error Handling

Every API response — success or error — uses the **same envelope shape**, so the
frontend only ever needs to branch on a single `success` boolean.

**Success envelope — `core/response.py`:**
```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[dict] = None

def success_response(data: T, message: str | None = None) -> APIResponse[T]:
    return APIResponse(success=True, message=message, data=data)
```
Controllers are the only layer that calls `success_response(...)` — building the
envelope is a response-shaping concern, not business logic.

**Error envelope — centralized exception hierarchy in `core/exceptions.py`:**
```python
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
```

Feature-specific exceptions subclass these (added to `core/exceptions.py`; split into
an `exceptions/` package later only if it grows too large):
```python
class NoCarsFoundError(NotFoundError):
    error_code = "no_cars_found"
    message = "No cars match the given criteria."
```

A global handler in `main.py` catches every `AppException` (plus FastAPI's own
`RequestValidationError`) and returns the same `APIResponse` shape with `success=false`:

```json
{ "success": false, "message": "No cars match the given criteria.", "data": null, "error": { "code": "no_cars_found", "details": { "budget": 5000 } } }
```

Matching success case, for reference:
```json
{ "success": true, "message": "Car recommendation fetched successfully", "data": { "make": "Toyota", "model": "Camry", "price": 28000 }, "error": null }
```

**Rules:**
- Raise domain exceptions from services — never raise `HTTPException` directly from
  controllers or routes.
- Controllers never build ad-hoc response dicts — always go through `success_response`.

## 5. Validation

- Every endpoint that accepts a body declares a typed Pydantic request schema.
- Every endpoint declares a `response_model` (wrapped in `APIResponse[...]`).
- Naming: `<Feature>Request` / `<Feature>Response` for action-style endpoints, or
  `<Noun>Create` / `<Noun>Read` / `<Noun>Update` for CRUD-style endpoints.

## 6. Naming Conventions

- Python files/functions: `snake_case`. Classes: `PascalCase`. Constants: `UPPER_SNAKE_CASE`.
- Per-feature filenames follow `<feature_name>_<layer>.py`
  (e.g. `car_recommendation_service.py`) so files stay greppable across the flat layer folders.
- DI provider functions always use a `get_<thing>` prefix
  (`get_db`, `get_car_recommendation_repository`, `get_car_recommendation_service`, `get_car_recommendation_controller`).
- SQLAlchemy models: singular `PascalCase` class (`Car`), plural `__tablename__` (`"cars"`).
- Frontend: `PascalCase.tsx` components, `camelCase.ts` hooks/utils, one route segment per feature.

## 7. Testing

- Framework: `pytest` + FastAPI `TestClient`.
- `apps/api/tests/` mirrors the flat layer structure: `tests/routes/`, `tests/services/`, `tests/repositories/`.
- Naming: `test_<method>_<condition>_<expected_result>`
  (e.g. `test_recommend_no_matching_cars_raises_not_found`).
- Services are unit-tested with a mocked repository (no real DB).
- Repositories are tested against a real, throwaway test database.
- Routes are tested end-to-end via `TestClient`, with `get_db` overridden to the test database.

## 8. Tooling & Environment

- Backend dependency/venv management: `uv`.
- Lint + format: `ruff` (backend), ESLint + Prettier defaults (frontend).
- Config: `pydantic-settings` reading from `.env` (`.env.example` committed, `.env` gitignored).
- Migrations: `alembic`, one migration per schema change, autogenerate reviewed manually before commit.
- All routes mounted under `/api/v1` from day one.

## 9. Workflow Rules

- Build **one feature at a time**. Briefly explain the approach and get alignment
  before writing code for a feature.
- Never start the next feature without the user's explicit go-ahead.
- Read `PROGRESS.md` and this file at the start of every session, before writing code.
- Update `PROGRESS.md` at the end of each feature or session.
- After finishing a feature, self-review it against this file: no business logic
  leaked into routes/controllers, no raw SQL/ORM in services, files reasonably small,
  naming consistent, tests present. Surface suggestions only if genuinely warranted —
  not as filler.
- No premature scaffolding: don't build infrastructure (e.g. auth) before a feature
  actually needs it.

## 10. Progress Tracking

Project status is tracked in `PROGRESS.md` at the repo root. Read it first when
resuming work; update it after every feature or session.
