# SQL Project: Dockerized PostgreSQL

A professional, ready-to-run PostgreSQL project using Docker Compose. Includes
a sample e-commerce schema, seed data, and analytical queries — a solid
starting point you can adapt to your own domain.

## Stack

- **PostgreSQL 16** (Alpine)
- **pgAdmin 4** for a web-based DB UI
- **Docker Compose** to orchestrate both

## Project Structure

```
sql-docker-project/
├── docker-compose.yml       # Postgres + pgAdmin services
├── .env.example             # Copy to .env and customize
├── init-scripts/
│   ├── 01_schema.sql        # Table definitions, constraints, indexes
│   └── 02_seed.sql          # Sample data
├── queries/
│   └── sample_queries.sql   # Example analytical queries
└── .gitignore
```

## Getting Started

1. **Copy the environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if you want different credentials/ports.

2. **Start the containers**
   ```bash
   docker compose up -d
   ```
   On first run, Postgres automatically executes everything in
   `init-scripts/` in alphabetical order (schema, then seed data).

3. **Connect to the database**

   Via `psql`:
   ```bash
   docker exec -it sql_project_db psql -U app_user -d app_db
   ```

   Via pgAdmin: open [http://localhost:5050](http://localhost:5050),
   log in with the credentials from `.env`, and add a new server:
   - Host: `postgres` (the Docker service name)
   - Port: `5432`
   - Username/Password: from `.env`

4. **Run the sample queries**
   ```bash
   docker exec -it sql_project_db psql -U app_user -d app_db -f /docker-entrypoint-initdb.d/../queries/sample_queries.sql
   ```
   Or just open `queries/sample_queries.sql` in pgAdmin / your SQL client
   and run it there.

## Schema Overview

The sample domain is a small e-commerce system (`shop` schema):

- `customers` — customer records
- `categories` — product categories
- `products` — product catalog with price and stock
- `orders` — customer orders with status
- `order_items` — line items per order

## Resetting the Database

Since data lives in a Docker volume, `init-scripts/` only runs on the
**first** startup. To reset from scratch:

```bash
docker compose down -v   # removes volumes too
docker compose up -d
```

## Adapting This Template

- Replace the schema/seed SQL in `init-scripts/` with your own domain.
- Add migration tooling (e.g. Flyway, Alembic, sqlx-cli) as the project grows.
- Add a `tests/` folder with `pgTAP` or application-level tests against
  a throwaway test database/container.

## Security Notes

- `.env` is gitignored — never commit real credentials.
- Default credentials in `.env.example` are for local development only.
- For production, use a managed secrets store and don't expose Postgres
  or pgAdmin ports publicly.
