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
├── app/
│   ├── __init__.py
│   ├── auth.py             # JWT token creation and security dependencies
│   ├── config.py           # Environment variables & security settings
│   ├── logging_config.py    # Structured JSON logger with Request IDs
│   ├── main.py             # FastAPI entrypoint, middleware, & rate limits
│   ├── schemas/            # Pydantic request/response schemas
│   │   ├── common.py
│   │   ├── customer.py
│   │   └── order.py
│   ├── services/           # Business logic layer
│   │   ├── customer_service.py
│   │   └── order_service.py
│   └── routers/            # Scoped route handlers
│       ├── auth_router.py
│       ├── customers.py
│       └── orders.py
├── requirements.txt
└── README.md


## Installation

Clone repository
git clone [https://github.com/YOUR-USERNAME/capstone-api.git](https://github.com/YOUR-USERNAME/capstone-api.git)
cd capstone-api

Activate virtual environment
.\venv\Scripts\Activate.ps1

Install dependencies
python -m pip install -r requirements.txt

## Running the Application

python -m uvicorn app.main:app --reload --port 8000