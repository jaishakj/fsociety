# Fsociety

Phase 1 (foundation) + Phase 2 (product catalog) — storefront API and UI.

Stack: FastAPI + SQLAlchemy + PostgreSQL (modular monolith) on the backend,
Vite + React + TypeScript + react-router-dom + TanStack Query on the frontend,
GSAP + Motion for animation, Tailwind v4 for styling.

## What's included

- **Backend** (`apps/api`): auth (JWT + Argon2), categories, products, product
  images, admin-only CRUD, JSON/CSV bulk import with per-row error reporting,
  image upload, Alembic migration for the full schema, a seed script, and a
  smoke test. Verified: imports cleanly, all routes registered, tests pass,
  Alembic recognizes the migration.
- **Frontend** (`apps/web`): the design system (void/panel/paper/steel/signal
  palette, Clash Display / General Sans / JetBrains Mono type roles), a custom
  cursor, the Depth Stack hero (the signature component — reused on the
  storefront home and on product detail), animated product cards, a filter
  rail, and three real pages wired to the live API: Home, Shop, Product.

## Run it

### 1. Database

```bash
docker compose -f infra/docker-compose.yml up -d
```

### 2. Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env        # edit JWT_SECRET_KEY before deploying anywhere real

alembic upgrade head
python scripts/seed.py      # optional: adds sample categories + 2 sample products
uvicorn app.main:app --reload
```

API docs at `http://localhost:8000/docs`. Health check at `/health`.

To use the admin endpoints (product CRUD, import, image upload), register a
user via `POST /api/v1/auth/register`, then promote them to admin manually —
the register endpoint always creates a `user`-role account on purpose, so a
stray signup can't grant itself admin. Simplest path for now:

```sql
UPDATE user_roles SET role = 'admin' WHERE user_id = '<your-user-id>';
```

Then log in via `POST /api/v1/auth/login` and pass the returned token as
`Authorization: Bearer <token>` on `/api/v1/admin/*` routes.

### 3. Frontend

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev
```

Dev server proxies `/api` and `/uploads` to `http://localhost:8000`, so the
storefront works against your local backend with no extra config.

## What's deliberately not here

Per the blueprint's own phasing: the knowledge/learning engine (concepts,
paths, reflections, XP/badges), the AI service, real payments, a dedicated
admin dashboard UI, and cart persistence are all out of scope for this slice.
Cart in the current UI is a local, in-memory "Add to bag" stub, nothing is
persisted server-side yet.

## Known gaps to close before this is production-ready

- Admin promotion is a manual SQL step right now (see above) — fine for one
  operator, not fine for a real team.
- No refresh-token rotation; access tokens are long-lived (7 days) for
  developer convenience. Tighten this before shipping.
- Image upload writes to local disk (`apps/api/uploads`), matching the
  blueprint's MVP scope. Swap for S3-compatible object storage before
  deploying somewhere with an ephemeral filesystem (Railway included).
