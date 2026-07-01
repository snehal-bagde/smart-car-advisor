# Project Progress

## Status Legend
- [ ] Not started   [~] In progress   [x] Done

## Features
- [x] Project setup — CLAUDE.md conventions written — 2026-07-01
- [x] Database layer — schema, SQLAlchemy models, migration, seed script — 2026-07-01
  - [x] `apps/api` bootstrapped with uv (pyproject.toml, src layout, ruff config)
  - [x] `core/config.py` + `core/database.py` (Settings, engine, SessionLocal, get_db)
  - [x] 7 SQLAlchemy models: Maker, CarModel, CarVariant, VariantSpecification, Feature, VariantFeature, Review
  - [x] Initial Alembic migration (`0001` / `e3b118921749_create_initial_schema`) — creates all tables + 3 Postgres enum types, verified clean upgrade/downgrade cycle
  - [x] Seed script (`app/seed/run_seed.py`) — 132 real Indian-market models across 25 makers, 335 variants, 42 features, 765 reviews
  - [x] Verified idempotency (rerun is a no-op) and healing (deleted maker + deleted reviews both restored identically) against a live local Postgres DB
- [x] BE/FE project scaffolding (structure only, no feature logic) — 2026-07-01
  - [x] Backend: `main.py` wired with `AppException` + `RequestValidationError` handlers returning the `APIResponse` envelope; `core/response.py`, `core/exceptions.py` created; empty `routes/`, `controllers/`, `services/`, `repositories/`, `schemas/` packages ready for the first feature; `tests/` skeleton with `conftest.py` (test-DB engine fixture, `db_session`, `client` with `get_db` override); pytest + httpx added as dev deps
  - [x] Frontend: Next.js 16 (App Router, TypeScript, Tailwind, ESLint) scaffolded at `apps/web`; added `components/`, `lib/api-client.ts` (generic fetch wrapper matching the backend's `APIResponse` envelope), `types/api.ts` (`ApiResponse<T>`); verified `tsc --noEmit`, `next lint`, and `npm run dev` all pass clean
  - Verification: booted the FastAPI app in-process and confirmed a thrown `NotFoundError` produces the exact documented error envelope; booted `next dev` and confirmed HTTP 200 on `/`
- [x] Car recommendation engine — backend API — 2026-07-02
  - [x] `POST /api/v1/car-recommendations` — request/response schemas, repository (hard filters + relaxation-ready queries, review aggregates, review snippets), 6-dimension weighted scoring (`car_recommendation_scoring.py`), rule-based explanations (`car_recommendation_explanations.py`), orchestrating service with a 4-step relaxation ladder, controller, route
  - [x] `NoMatchingCarsError` added; wired into `main.py` under `/api/v1`
  - [x] 43 unit/service tests (pure scoring functions, explanation templates, mocked-repository service tests) — all passing, `ruff check` clean
  - [x] Verified end-to-end against the live seeded DB across several scenarios (family-of-7 SUV/MUV fit, solo budget+mileage buyer, narrow-filter relaxation cascade, zero-match error envelope)
  - Found and fixed two real bugs during manual verification: (1) a comfort-dimension match reason that contradicted itself when the dimension scored well via seating fit but feature count was below average, (2) a seating shortfall that could be fully absent from `trade_offs` if the blended comfort score didn't dip below median — now always disclosed when seats < family_size, since that's safety-relevant information a soft-scoring system must never hide
  - Frontend UI for this feature is **not** built yet — scope for this pass was backend-only, per feature-by-feature workflow
- [x] Car recommendation frontend UI — 2026-07-02
  - [x] Landing page (`/`), guided 8-step conversational questionnaire (`/questionnaire` — one question per screen: budget/distance sliders, usage/fuel/transmission/body-type choice cards, family-size stepper, priorities multi-select), and results page (`/recommendations`) with full inline detail per card (score, confidence, match reasons, trade-offs, key features, star ratings + expandable review snippets) — car details and compare-cars screens deliberately dropped from scope per user direction
  - [x] Hand-rolled Tailwind component set in `components/ui/` (Button, Card-less composition, ProgressBar, ChoiceCard, Slider, Stepper, Badge, StarRating, Spinner) — no component framework (shadcn/ui was tried and explicitly removed per user preference); `clsx` + `tailwind-merge` added as the only two small utility deps, via a `cn()` helper
  - [x] Answers persist to `sessionStorage` between `/questionnaire` and `/recommendations` (no new backend endpoints needed); returning to the questionnaire after a "no matches" error prefills previous answers instead of resetting
  - [x] Backend: added dev-only CORS middleware to `main.py` (`http://localhost:3000`) — required for the browser to call the API at all
  - [x] Loading state (rotating status messages), and distinct error states: no-answers-yet, `no_matching_cars` (friendly "adjust your preferences" CTA, preserves answers), and generic/network errors (retry button) — all render the same `APIResponse` envelope the backend guarantees
  - [x] Verified with a real Playwright-driven browser (not just `curl`) against the live backend: full 8-step questionnaire → real recommendation results, at both desktop (1280px) and mobile (390px) viewports; zero console errors/warnings on the final pass
  - Found and fixed three real UI bugs during verification: (1) top-heavy vertical layout with a large dead zone on every questionnaire step — fixed by vertically centering; (2) the "no compromises" honest fallback trade-off rendered under the same amber warning icon as a real trade-off — now shown with a checkmark/emerald tone when it's the fallback string; (3) the 2-column choice-card grid truncated/overlapped labels on mobile (390px) — changed to `grid-cols-1 sm:grid-cols-2`
  - Not built: automated frontend tests (no test runner set up yet for `apps/web`) — verification for this pass was manual/scripted-browser only, noted as a gap not a silent skip

## Notes / Decisions Log
- 2026-07-01: Chose flat layer-based backend folders (routes/controllers/services/repositories/models/schemas) over feature-based folders, per user preference.
- 2026-07-01: uv + ruff for backend tooling, pydantic-settings for config, alembic for migrations.
- 2026-07-01: Frontend styling is Tailwind CSS (user's choice over plain CSS Modules).
- 2026-07-01: Reviews attach to `CarModel`, not `CarVariant`. `fuel_type`/`transmission_type`/`body_type` are Postgres enums, not lookup tables. `average_rating` is never stored — always computed live via `AVG(rating)`.
- 2026-07-01: `features.category` and seed data's `segment` tag are seed-time-only concepts, not persisted columns — kept the schema minimal per CLAUDE.md.
- 2026-07-01: Reviews have no natural key, so idempotent seeding only guarantees healing when a model's reviews are *entirely* deleted (count == 0 triggers reseed); partial deletion of some-but-not-all reviews is an accepted gap, documented in `run_seed.py`.
- 2026-07-01: Local dev DB is Postgres running on localhost, database `smart-car-advisor`, role `crest` (trust auth, no password) — see `apps/api/.env`.
- 2026-07-02: `family_size` is never a hard filter (a large family shouldn't see zero results over one missing seat) — it's a soft signal in the Comfort & Features dimension's raw value (seating shortfall/surplus, weighted heavily enough to matter) and in that dimension's weight. Seating shortfall is still always disclosed in `trade_offs` regardless of how it nets out in the blended score.
- 2026-07-02: Reliability dimension uses a plain average review rating (no Bayesian shrinkage for low review counts) — kept simple per user request; flagged as revisitable if thin-review models start ranking unrealistically high.
- 2026-07-02: `ruff`'s B008 rule (flags `Depends(...)` as a function-call default) is ignored project-wide in `apps/api/pyproject.toml` — it's FastAPI's canonical DI pattern, not the mutable-default hazard the rule targets, and every future feature's `get_<thing>` providers will hit it.
- 2026-07-02: Tried shadcn/ui for frontend components, then explicitly removed it per user request — the frontend uses hand-rolled Tailwind components only, plus `clsx`/`tailwind-merge` as small utility deps (not a component framework).
- 2026-07-02: Car details and compare-cars pages are deliberately out of scope for now (user's call) — recommendation results show full detail inline on each card instead of linking to a drill-down page. Revisit if/when those are prioritized; there's currently no "get car by id" backend endpoint to support them.
- 2026-07-02: `react-hooks/set-state-in-effect` (a new stricter lint rule shipped with Next 16 / React 19's eslint-config) is turned off project-wide in `apps/web/eslint.config.mjs` — it flags the standard "fetch data on mount" / "sync from sessionStorage on mount" effect pattern used on both client pages, which is a sanctioned React use case, not the derived-state anti-pattern the rule targets.

## How to resume
Read this file, then `CLAUDE.md`, then continue the first "[~]" or "[ ]" item.
