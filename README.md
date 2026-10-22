# Capstone REST API (Design-First Implementation)

A production-ready RESTful API implementing full CRUD, input schemas, pagination, and structured logging based on OpenAPI 3.1 specifications.

## Architecture

- **Routers (`app/routers/`)**: Pure HTTP handling, routing, and HTTP code management.
- **Services (`app/services/`)**: Enforces business logic and rules independently of HTTP.
- **Schemas (`app/schemas/`)**: Pydantic models for request/response serialization & validation.
- **Logging (`app/logging_config.py`)**: Request ID middleware for tracing across logs.

---

## Local Development Setup

### 1. Requirements & Installation
- Python 3.10+

```bash
# Clone repository
git clone [https://github.com/your-username/capstone-api.git](https://github.com/your-username/capstone-api.git)
cd capstone-api

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt