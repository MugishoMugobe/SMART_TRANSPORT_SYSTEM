# Smart Public Transport Management System

A full-stack Django application for running a public transport operation:
fleet, drivers, routes, scheduled trips, and passenger bookings with
QR-coded tickets — plus a REST API and role-based access control over the
same data.

Built for MIT714 (Database Systems Management), IUEA — see
[`docs/ERD.md`](docs/ERD.md) for the data model,
[`docs/USE_CASES.md`](docs/USE_CASES.md) for the use case diagram,
[`docs/TESTING.md`](docs/TESTING.md) for the test report, and
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for how it's deployed.

**Live app:** https://sts.mac-rdc.com

## Features

- **Fleet operations** — passengers, drivers, vehicles, routes and trips,
  each with full create/read/update/delete, search, and filtering.
- **Bookings** — interactive seat-map booking, automatic overbooking and
  duplicate-seat prevention, auto-generated booking references, and a
  scannable QR ticket per booking.
- **Dashboard & reports** — live counts, revenue, upcoming trips, and a
  CSV export of all bookings.
- **Role-based accounts** — `ADMIN`, `STAFF`, `PASSENGER`, enforced on
  every view and every API endpoint, not just at login.
- **REST API** — the same data and rules available at `/api/v1/`, for any
  client beyond the server-rendered pages.

## Tech stack

- **Backend:** Django 6, Django REST Framework
- **Database:** SQLite locally; MySQL in production on Namecheap/cPanel, Postgres if deployed to Render instead — both selected at runtime via `DATABASE_URL` (see `docs/DEPLOYMENT.md`)
- **Frontend:** Django templates + Bootstrap 5
- **Auth:** Django sessions (used by both the HTML views and the API)
- **Hosting:** Namecheap cPanel shared hosting (Phusion Passenger) — `passenger_wsgi.py`, `requirements-cpanel.txt`

## Roles

| Role | Can do |
|---|---|
| `PASSENGER` | Browse vehicles/routes/trips, create bookings, view and cancel their own bookings |
| `STAFF` | Everything a passenger can, plus manage passengers, drivers, vehicles, routes, trips and bookings, and view reports |
| `ADMIN` | Everything STAFF can, plus the Django admin site |

Role is stored on `accounts.models.Profile.role` and is set automatically
to `PASSENGER` on self-registration; `STAFF`/`ADMIN` accounts are created
via `python manage.py createsuperuser` or the Django admin. See
[`accounts/decorators.py`](accounts/decorators.py) (HTML views) and
[`api/permissions.py`](api/permissions.py) (API) for the enforcement — both
are built on the same `is_staff_or_admin()` helper so the two never drift
apart.

## Getting started (local development)

```bash
# from the STS/ directory
pip install -r requirements-base.txt

python manage.py migrate
python manage.py createsuperuser   # first ADMIN account
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. No environment variables are required for
local development — see `.env.example` for what production adds.

For deployment, use `requirements-cpanel.txt` (Namecheap/MySQL, the
platform this project actually deploys to) or `requirements.txt`
(Render/Postgres, also supported) instead of `requirements-base.txt` —
see [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Running the tests

```bash
python manage.py test
```

60 tests across every app — service-layer business rules, view-level
CRUD and RBAC, and the REST API. Details and results in
[`docs/TESTING.md`](docs/TESTING.md).

## REST API

Base path: `/api/v1/`. Session-authenticated (log in through the normal
web UI, then browse the API in the same session — or use HTTP Basic
auth for scripted access).

| Endpoint | Notes |
|---|---|
| `GET /api/v1/me/` | Who am I, what role |
| `/api/v1/vehicles/`, `/api/v1/routes/`, `/api/v1/trips/` | Read: any authenticated role. Write: STAFF/ADMIN only |
| `/api/v1/passengers/`, `/api/v1/drivers/` | STAFF/ADMIN only (personal data) |
| `/api/v1/bookings/` | Create: any role. A `PASSENGER` sees/manages only their own bookings; STAFF/ADMIN see all. `POST /api/v1/bookings/{id}/cancel/` releases the seat |

All endpoints support `?search=` and `?ordering=`; vehicles/routes/trips/
bookings also support `?status=`/`?vehicle_type=`. Errors always come back
as `{"error": {"code", "message", "details"}}` — see
[`api/exceptions.py`](api/exceptions.py).

## Project structure

```
accounts/     auth, roles, login/register, role_required decorator
passengers/   passenger directory (STAFF/ADMIN only — PII)
drivers/      driver directory (STAFF/ADMIN only — PII)
vehicles/     fleet (read: any role, write: STAFF/ADMIN)
routes/       route catalogue (read: any role, write: STAFF/ADMIN)
trips/        scheduled trips (read: any role, write: STAFF/ADMIN)
bookings/     booking flow + services.py (shared business-rule layer)
dashboard/    landing page with live counts
reports/      revenue/booking reports + CSV export (STAFF/ADMIN only)
api/          DRF serializers/viewsets/permissions over the same models
docs/         ERD, testing report, deployment report
```

## Exam requirement → where it's satisfied

| Requirement | Where |
|---|---|
| ERD + schema (Section A) | [`docs/ERD.md`](docs/ERD.md) |
| Use case diagram | [`docs/USE_CASES.md`](docs/USE_CASES.md) |
| CRUD per module (Section B) | each app's `views.py`/`urls.py`/`templates/<app>/` |
| REST API (Section C) | `api/` app; shared rules in `bookings/services.py` |
| Responsive UI, search/filter/validation (Section D) | Bootstrap 5 templates; `?q=`/`?status=`/`?vehicle_type=` on list views; form errors styled in `templates/base.html` |
| Auth & RBAC (Section E) | `accounts/decorators.py` + `api/permissions.py`, applied per-view/per-endpoint |
| Testing | [`docs/TESTING.md`](docs/TESTING.md) |
| Deployment | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |
