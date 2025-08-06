# Real Estate API

This project provides a RESTful API for managing real estate properties and transactions, including ownership percentages, with robust validation and filtering.

---

## Features

- Manage Users, Properties, and Transactions
- Ownership percentages with validation (max 100% total, max 80% per user)
- Price validation and minimum investment rules
- Filtering and ordering support on transactions
- Token-based authentication (JWT)
- Swagger UI API documentation with token authentication
- Dockerized environment for easy setup and deployment

---

## Technology Stack

- Python 3.12+
- Django + Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- drf-yasg for Swagger documentation
- Poetry for dependency management

---

## Getting Started

### Prerequisites

- Docker & Docker Compose installed (recommended)
- Or Python 3.12+ and Poetry installed for local development

---

### Environment Setup

Copy `.env.example` to `.env` and customize as needed (or create `.env`):

    cp .env.example .env

The `.env` file should contain:

    DJANGO_SECRET_KEY=your-secret-key
    DJANGO_DEBUG=True
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web

    POSTGRES_DB=realestate_db
    POSTGRES_USER=realestate_user
    POSTGRES_PASSWORD=realestate_pass
    POSTGRES_HOST=db
    POSTGRES_PORT=5432

    DJANGO_ADMIN_USERNAME=admin
    DJANGO_ADMIN_EMAIL=admin@example.com
    DJANGO_ADMIN_PASSWORD=AdminPass123!

---

### Running with Docker

1. Build and start containers:

        docker compose up --build

2. The API will be available at:  
   http://localhost:8000/

3. Run migrations automatically on startup.

---

## API Documentation (Swagger UI)

The Swagger UI is available at:

    http://localhost:8000/swagger/

### Authentication in Swagger

- Use the token endpoint alongside your login credentials to retrieve your JWT token.
- Click the **Authorize** button at the top right.  
- Paste your JWT token **without** the `Bearer ` prefix. The UI will add it automatically.  
- After authorizing, all API requests from Swagger will include the token in the `Authorization` header.

---

## Running Tests

### Using Docker

    docker-compose run --rm web poetry run pytest

Tests cover all endpoints, filtering, and edge cases for Transactions, Properties, and Users.

---

## Notes

- The API enforces business rules like ownership percentage limits and price validations strictly in serializers and viewsets.  
- Admin UI is optional and disabled by default.  
- Authentication is token-based; only authenticated users can create transactions, properties.  
- Users can only modify their own transactions, properties, user profile unless they are admins.
- Implementation time was initially couple of hours but i refined my solution on the following days with tests and more robust validations that took a while to finnish
---

## Contact

For questions, contact Theodore Flokos: `qqflokosqq@gmail.com`

