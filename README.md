# Simple Stock Flow · Seeder & Demo CLI Tool

> **SDD Technical Assessment · SENA ADSO Class 3413974**  
> Python command-line utility for seeding demo test data via the public REST API (Task T-24).

---

## 1. What is this repository and what role does it play in Simple Stock Flow?

This repository contains the **demo seeder and utility CLI** (`ssf_tool`) for *Simple Stock Flow*.
Its role is to automate loading realistic demonstration data (categories, products, real image uploads, and sales transactions) so evaluators and developers can immediately observe the running system with rich data.

**Design invariants (Task T-24):**
- **Zero Database Access:** Contains no dependencies on `sqlalchemy` or `pymysql`. Executes no direct DDL or SQL queries.
- **Exclusively Uses Public API:** All data is created through public REST endpoints (`/api/auth/login`, `/api/products`, `/api/products/{id}/image`, `/api/sales`).
- **Idempotency:** When executed multiple times consecutively, detects existing products by name and generates neither duplicates nor errors.

---

## 2. How to run it locally?

### With Docker (Recommended if Python is not installed locally)
```bash
# 1. Build the seeder image
docker build -t ssf-tool .

# 2. Run the seeding process against the running stack
docker run --rm --network host -e API_BASE_URL="http://localhost:8000" ssf-tool seed
```

### Without Docker (Python 3.10+ and virtual environment)
```bash
# 1. Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the seed command
python -m ssf_tool seed --url http://localhost:8000 --username admin --password "Admin12345!"
```

---

## 3. Required Environment Variables

The `seed` command reads the following configuration variables (with defaults if omitted):

| Variable | Description | Default Value |
|---|---|---|
| `API_BASE_URL` | Backend service base URL | `http://localhost:8000` |
| `ADMIN_USERNAME` | Administrator username for authentication | `admin` |
| `ADMIN_PASSWORD` | Administrator password | `Admin12345!` |

---

## 4. How are tests executed?

```bash
# Run unit tests with network mocks
python -m unittest discover tests/
```

---

## 5. Relevant Technical Decisions Taken During Implementation

1. **Strict Infrastructure Isolation (ADR-001):**
   - The seeder lives outside `test-simple-stock-flow-infra` so the infrastructure remains 100% self-contained and does not mandate host-level Python installations.
2. **Idempotent Seeding Based on Catalog Inspection:**
   - Before dispatching `POST /api/products`, the client inspects existing catalog records via `GET /api/products`. If a product already exists by name, it reuses its ID for sales association, avoiding unique constraint violations or duplicate entries.
3. **Real Multipart Handling for Images:**
   - Generates and uploads genuine binary image assets (JPEG and PNG) via `multipart/form-data`, strictly respecting the 5 MB limit and allowed MIME types.
