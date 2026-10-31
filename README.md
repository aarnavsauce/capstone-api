# Capstone REST API (Design-First & Secure Implementation)

A production-ready RESTful API built with FastAPI and Pydantic, implementing full CRUD workflows, input validation schemas, pagination, structured logging with Request IDs, **JWT Authentication**, **Role/Ownership Scoping (BOLA Defense)**, and **Rate Limiting**.

---

## Key Features & Architecture

- **Routers (`app/routers/`)**: Pure HTTP route handling and response code management.
- **Services (`app/services/`)**: Enforces core business rules independently of the HTTP layer.
- **Schemas (`app/schemas/`)**: Pydantic models for strict payload validation and serialization.
- **Authentication (`app/auth.py`)**: Cryptographically signed JWT tokens (`HS256`) carrying user identity claims.
- **Data Scoping & Security**: Enforces Broken Object Level Authorization (BOLA) defenses so authenticated customers can only access their own orders.
- **Rate Limiting**: Integrated `slowapi` rate limiting (5 order creations/minute per IP) to prevent resource exhaustion attacks.
- **Structured Logging (`app/logging_config.py`)**: Contextual logging with unique `X-Request-ID` headers traced across requests.

---

## Project Structure

```text
capstone-api/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI workflow script
├── app/
│   ├── __init__.py
│   ├── auth.py             # JWT token utilities & HTTPBearer security
│   ├── config.py           # Application settings & secret keys
│   ├── logging_config.py    # Request ID middleware & structured JSON logger
│   ├── main.py             # FastAPI application, exception handlers, rate limits
│   ├── schemas/            # Pydantic validation models
│   │   ├── common.py
│   │   ├── customer.py
│   │   └── order.py
│   ├── services/           # Business logic layer & scoped filtering
│   │   ├── customer_service.py
│   │   └── order_service.py
│   └── routers/            # Route handlers & endpoints
│       ├── auth_router.py
│       ├── customers.py
│       ├── orders.py
│       └── webhooks.py      # HMAC signature validation & duplicate detection
├── tests/
│   └── test_api.py         # 18 automated unit, security, & integration tests
├── locustfile.py           # Load test specification script
├── requirements.txt        # Production & testing dependency declarations
└── README.md               # Architecture documentation, threat model, & setup guide

```

### Webhook Ingestion Security Controls

| Threat | Impact | Mitigation Implemented |
| :--- | :--- | :--- |
| **Payload Spoofing / Unauthorized POSTs** | Fake business events injected into backend workflows. | Constant-time HMAC-SHA256 signature verification (`X-Hub-Signature-256`) using a shared secret. |
| **Replay Attacks / Duplicate Processing** | Financial transactions or order updates executed multiple times. | Idempotency layer tracking unique event delivery IDs (`X-GitHub-Delivery`). |
| **DoS via Long-Running Tasks** | Server timeouts causing sender delivery failures and retry loops. | Fast-ack pattern returning `200 OK` immediately after validation. |

## Installation

Clone repository
git clone [https://github.com/aarnavsauce/capstone-api.git](https://github.com/aarnavsauce/capstone-api.git)

cd capstone-api

Activate virtual environment
.\venv\Scripts\Activate.ps1

Install dependencies
python -m pip install -r requirements.txt

## Running the Application

python -m uvicorn app.main:app --reload --port 8000
