# Deployment Report — Namecheap (cPanel shared hosting)

## 1. What's already prepared

Production readiness lives in environment variables — nothing about
local development changes. With no env vars set, the app behaves
exactly as before (DEBUG on, SQLite, insecure dev key). Set the
variables in §3 and it becomes production-safe: real secret key, DEBUG
off, MySQL, HTTPS-only cookies.

| File | Purpose |
|---|---|
| `passenger_wsgi.py` | The entry point cPanel's Python App (Phusion Passenger) looks for — re-exports Django's WSGI `application` |
| `STS/__init__.py` | Shims PyMySQL in as `MySQLdb`, so Django's MySQL backend works without a C compiler (shared hosting usually doesn't have one) |
| `STS/settings.py` | Reads `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` from the environment; WhiteNoise serves static files from inside the WSGI process (no separate web-server config needed); media (uploaded photos/QR codes) is now served unconditionally, not just when `DEBUG=True` — see §5 |
| `requirements-base.txt` / `requirements-cpanel.txt` | Lean, compiler-free dependency set for shared hosting (no gunicorn — Passenger runs the app itself; PyMySQL instead of the C-extension `mysqlclient`) |
| `.env.example` | Every environment variable the app reads in production |

## 2. Before you start — confirm your plan has these

cPanel varies by host and plan tier. Check these on your Namecheap
account before following the steps below:

- **Setup Python App** in cPanel (this is the Phusion Passenger tool —
  not every shared tier includes it; if you don't see it, contact
  Namecheap support or upgrade to a plan that does).
- **A Python version new enough for Django 6** in that tool's dropdown.
  If only an older Python is offered, ask Namecheap support to enable a
  newer one, or downgrade Django as a fallback.
- **Terminal / SSH access**, to run `migrate`/`collectstatic`/
  `createsuperuser`. On Namecheap this is typically Stellar Plus/
  Business tier and above, not the base Stellar plan.
- **MySQL® Databases** in cPanel (standard on all tiers).

## 3. Deploying

### a) Get the code onto the server

Either:

- **cPanel → Git™ Version Control** (if available) → clone
  `https://github.com/MugishoMugobe/SMART_TRANSPORT_SYSTEM.git`
  directly on the server, or
- **File Manager / FTP**: download a zip of the repo from GitHub,
  upload it, extract it into a folder under your home directory (e.g.
  `~/smart-transport`) — not necessarily inside `public_html`;
  Passenger handles routing to it.

### b) Create the database

cPanel → **MySQL® Databases**:
1. Create a database (cPanel will prefix it, e.g. `cpaneluser_sts`).
2. Create a database user + password.
3. Add that user to the database with **All Privileges**.
4. Note the three values — you'll need `cpaneluser_sts`,
   `cpaneluser_dbuser`, and the password for §3d.

### c) Create the Python App

cPanel → **Setup Python App** → **Create Application**:

- **Python version**: the newest offered (see §2).
- **Application root**: the folder from §3a (e.g. `smart-transport`).
- **Application URL**: your domain or subdomain.
- **Application startup file**: `passenger_wsgi.py`
- **Application Entry point**: `application`

Creating it gives you an "Enter to the virtual environment" command
(something like `source /home/USER/virtualenv/smart-transport/3.12/bin/activate`).
In **Terminal**, run that, `cd` into the application root, then:

```bash
pip install -r requirements-cpanel.txt
```

### d) Set environment variables

Try the **Setup Python App** page's built-in **Environment variables**
section first, and add:

```
DJANGO_SECRET_KEY=<generate a long random value>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=mysql://cpaneluser_dbuser:PASSWORD@localhost/cpaneluser_sts
```

(A quick way to generate a secret key: `python -c "import secrets; print(secrets.token_urlsafe(50))"`.)

**Verify it actually persisted.** On at least one real deployment,
values saved in that UI later showed as "no results found" — silently
reverting the whole app to its insecure defaults (`DEBUG=True`,
SQLite) with no visible error. After saving, reopen the page and
confirm the variables are still listed. If they aren't, don't fight
the UI — use the `.env` fallback instead:

```bash
cat > ~/APPROOT/.env << 'EOF'
DJANGO_SECRET_KEY=your-actual-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=mysql://cpaneluser_dbuser:PASSWORD@localhost/cpaneluser_sts
EOF
chmod 600 ~/APPROOT/.env
```

`passenger_wsgi.py` loads this file itself (see the code — it's a
~15-line dependency-free parser) before Django's settings are read, so
it works regardless of whether cPanel's own mechanism does. It's
`.gitignore`d, so it only ever exists on the server, never in the
repo. A real environment variable (from cPanel's UI, if that ever
starts working) still takes precedence — `.env` only fills in what
isn't already set.

### e) Migrate, collect static files, create the first admin

**Terminal sessions do not automatically see either channel above** —
not cPanel's env-var UI, and not the `.env` file (that's loaded by
`passenger_wsgi.py`, which only runs inside the Passenger-managed web
process, not when you run `python manage.py ...` by hand). Every time
you open a new Terminal session to run management commands, export
the same values into that shell first:

```bash
cat > ~/APPROOT/set_env.sh << 'EOF'
export DJANGO_SECRET_KEY="your-actual-secret-key"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
export DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
export DATABASE_URL="mysql://cpaneluser_dbuser:PASSWORD@localhost/cpaneluser_sts"
EOF
chmod 600 ~/APPROOT/set_env.sh

source ~/APPROOT/set_env.sh
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])"
# must print django.db.backends.mysql — if it prints sqlite3, the
# export above didn't take, or you're not in the same terminal session
```

Once that confirms MySQL, run the real sequence against it:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # first ADMIN account
```

Skipping the `source`/verify step is exactly how this goes wrong: the
commands "succeed" silently against a throwaway local SQLite file
instead of the real database, and you end up debugging why an account
that clearly exists still can't log in on the live site.

### f) Restart

**Setup Python App** → this application → **Restart** — required
after *any* change here: env vars, `.env`, or a code pull. Visit your
domain — that's the "Live application URL" deliverable.

### g) Redeploying after a change

- With Git Version Control: **Pull** the latest commit, then Restart.
- Without it: re-upload the changed files, then Restart.
- Either way, re-run `migrate`/`collectstatic` in Terminal if the
  change touched models or static files.

## 4. Media and static files

Unlike a lot of PaaS free tiers, cPanel shared hosting has a normal
**persistent** filesystem — uploaded driver photos, vehicle images, and
booking QR codes stay put across restarts and redeploys, no object
storage needed.

The one thing that had to change to make that true: Django's `static()`
helper (what the project used before) only ever serves media when
`DEBUG=True` — in production that would 404 every upload. `STS/urls.py`
now serves `/media/` unconditionally via `django.views.static.serve`.
That view isn't built for heavy traffic, but it's the right tradeoff at
this project's scale versus standing up a separate file host.

## 5. Rollback

There's no automatic release history like a PaaS provides. Keep the
previous working commit's files (File Manager has a "trash"/version
option on some plans, or keep a zip backup before each deploy) so you
can restore quickly, then Restart the Python App.

## 6. Also supported: Render

The same environment-driven `settings.py` also runs unmodified on
Render (Postgres instead of MySQL, gunicorn instead of Passenger) —
`render.yaml`, `Procfile` and `build.sh` are still in the repo if you
ever want that path instead. Use `requirements.txt` (not
`requirements-cpanel.txt`) there. Not used for this submission's live
URL, kept as evidence the config isn't tied to one host.
