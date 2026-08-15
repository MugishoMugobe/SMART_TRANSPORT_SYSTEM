# Deployment Report — Render

## 1. What's already prepared

Production readiness lives entirely in environment variables — nothing
about local development changes. With no env vars set, the app behaves
exactly as it did before (DEBUG on, SQLite, insecure dev key). Set the
variables below and it becomes production-safe: real secret key, DEBUG
off, Postgres, HTTPS-only cookies, HSTS.

| File | Purpose |
|---|---|
| `STS/settings.py` | Reads `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` from the environment; adds WhiteNoise for static files; hardens cookies/HSTS when `DEBUG=False` |
| `requirements.txt` | Adds `gunicorn`, `whitenoise`, `dj-database-url`, `psycopg[binary]` on top of the app's existing dependencies |
| `build.sh` | Render's build step: install deps → `collectstatic` → `migrate` |
| `Procfile` | `web: gunicorn STS.wsgi:application`; `release: migrate` |
| `render.yaml` | A Render **Blueprint** — describes the web service *and* a managed Postgres database together, so both are created in one step |
| `.env.example` | Documents every environment variable the app reads in production |

## 2. Deploying (Render Blueprint — one pass through the dashboard)

You'll need a free Render account linked to the GitHub repo
(`MugishoMugobe/SMART_TRANSPORT_SYSTEM`) — this part has to happen in
your browser, it's not something that can be scripted from here.

1. Push this branch to GitHub (`git push`).
2. Go to <https://dashboard.render.com> → **New** → **Blueprint**.
3. Select the `SMART_TRANSPORT_SYSTEM` repo. Render reads `render.yaml`
   automatically and shows two resources to create:
   - `smart-transport-system` (the web service)
   - `smart-transport-db` (a free Postgres database)
4. Click **Apply**. Render will:
   - provision the Postgres database and inject `DATABASE_URL` into the
     web service automatically (that wiring is what `fromDatabase:` in
     `render.yaml` does),
   - generate `DJANGO_SECRET_KEY` for you (`generateValue: true`),
   - run `build.sh` (installs deps, collects static files, runs
     migrations),
   - start the app with `gunicorn STS.wsgi:application`.
5. Once the first deploy finishes, open a **Shell** on the web service
   (Render dashboard → your service → Shell) and create the first admin
   account:
   ```bash
   python manage.py createsuperuser
   ```
   This is the same superuser flow you'd use locally — it exists so
   there's an `ADMIN`-role account before anyone can register through
   the app itself.
6. Visit the URL Render assigns (`https://smart-transport-system.onrender.com`,
   or whatever name you gave the service) — that's the "Live application
   URL" deliverable.

## 3. Known limitation: uploaded media on the free tier

Render's **free** web service plan has an *ephemeral* filesystem —
anything written to disk after a deploy (driver photos, vehicle images,
booking QR codes, all currently stored under `MEDIA_ROOT`) is wiped on
the next deploy or restart. This is a Render free-tier constraint, not a
bug in the app.

For this exam submission that's an acceptable, documented limitation —
the CRUD flows, uploads, and QR generation all work correctly in the
running app between deploys. For a real production deployment, the fix
is to point `DEFAULT_FILE_STORAGE` at an object store (Render persistent
disk on a paid plan, or S3/Cloudinary) instead of local disk — noted here
as the natural next step rather than implemented, since it requires a
paid resource or a third-party account this project doesn't otherwise
need.

## 4. Rollback

Render keeps every previous deploy. If a deploy breaks the app: dashboard
→ the web service → **Events** tab → find the last good deploy →
**Rollback to this deploy**.
