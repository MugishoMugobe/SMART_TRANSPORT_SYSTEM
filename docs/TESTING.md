# Testing Report — Smart Public Transport Management System

## 1. Strategy

Three layers, matching the three places bugs actually show up in this app:

1. **Service layer** (`bookings/services.py`) — the seat-allocation and
   overbooking rules are tested directly, independent of HTTP, since both
   the HTML views and the REST API call into the same functions.
2. **View layer** (one `tests.py` per app) — CRUD through the real Django
   test client (`self.client.post(...)`), plus role-based access control:
   every module has a test proving a `PASSENGER`-role account is bounced
   from the actions it shouldn't reach, and a `STAFF`-role account can
   complete the full CRUD cycle.
3. **API layer** (`api/tests.py`) — the automated version of the manual
   `curl` walkthrough used while building the API (role gating, the
   custom error envelope, seat-conflict validation, per-passenger
   queryset scoping, the cancel action).

## 2. Running the suite

```bash
python3 manage.py test
```

## 3. Result (last run)

```
Creating test database for alias 'default'...
............................................................
----------------------------------------------------------------------
Ran 60 tests in 35.8s

OK
Destroying test database for alias 'default'...
```

**60/60 passing.** Breakdown:

| App | Tests | Covers |
|---|---|---|
| `accounts` | 8 | registration, login success/failure, role-based post-login redirect, logout |
| `passengers` | 9 | CRUD as staff, search, full module locked to STAFF/ADMIN (PII) |
| `drivers` | 6 | CRUD as staff (incl. photo upload), module locked to STAFF/ADMIN |
| `vehicles` | 7 | CRUD as staff, `vehicle_type` filter, read open to any role / write staff-only |
| `routes` | 6 | CRUD as staff, `status` filter, read open to any role / write staff-only |
| `trips` | 6 | CRUD as staff, `available_seats` auto-set from vehicle capacity, `status` filter, RBAC |
| `bookings` | 12 | reference generation, duplicate-seat rejection, overbooking rejection, seat-capacity bounds, cancel restores the seat (and is idempotent), passenger-scoped list, ownership checks on cancel/delete |
| `api` | 10 | anonymous → error envelope, role gating per endpoint, PII endpoints staff-only, booking creation/validation/scoping/cancel through the REST layer |

## 4. What this deliberately does not cover

Being upfront about the edges, rather than implying 100% coverage:

- **No coverage-percentage tool was run** (e.g. `coverage.py`) — the
  numbers above are test *counts*, not statement coverage.
- **No browser/UI automation** (Selenium/Playwright) — the seat-map
  JavaScript on the booking form and the login page's client-side
  password toggle are exercised manually, not by an automated test.
- **File upload edge cases** (wrong MIME type, oversized image) aren't
  tested — only the happy path (a valid small image) is.
- **Concurrency**: the overbooking/duplicate-seat checks are correct for
  sequential requests (each `TestCase` runs single-threaded against
  SQLite); a true race — two requests hitting `create_booking()` for the
  last seat at the same instant — isn't exercised here. `services.py`
  wraps the seat check + save in `transaction.atomic`, which is the right
  mitigation, but the test suite doesn't prove it under load.

## 5. Manual end-to-end verification (REST API)

Before the automated `api/tests.py` suite existed, the API was
walked through by hand against a running dev server with three seeded
accounts (`ADMIN`, `STAFF`, `PASSENGER`) to sanity-check the whole stack
end to end, not just Django's test client:

- Anonymous request → `403` with the custom error envelope (not DRF's
  raw default shape).
- Passenger role: can read `/api/v1/vehicles/`, blocked from writing to
  it, blocked entirely from `/api/v1/passengers/` and `/api/v1/drivers/`
  (PII).
- Staff role: full read/write on fleet data, full read on PII data.
- Booking created via API returns a real `BK#####` reference; booking
  the same seat twice returns a `validation_error` envelope naming the
  conflict.
- `/api/v1/bookings/` returns only the caller's own bookings for a
  passenger, and every booking for staff.
- `/api/v1/me/` reports the correct role for the logged-in account.

All of the above are now also codified as automated tests in
`api/tests.py`, so this was a one-time confirmation the design worked in
a real running server, not a substitute for the suite.
