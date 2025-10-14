---
applyTo:
  - "crypto_api/**/*.py"
  - "letsgetcrypto_django/**/*.py"
  - "manage.py"
---

# Django API Development Instructions

## Django REST API Guidelines

### Views and Endpoints
- Use Django REST framework class-based views when possible
- Return appropriate HTTP status codes (200, 201, 400, 404, 500)
- Always return JSON responses with consistent structure:
  ```python
  {"status": "success", "data": {...}} # on success
  {"status": "error", "message": "..."} # on error
  ```
- Implement proper pagination for list endpoints
- Use Django's `@api_view` decorator for function-based views

### Models
- Use descriptive model names (e.g., `CryptoPrediction`, `TradingSignal`)
- Add `__str__()` method for better debugging
- Include `created_at` and `updated_at` timestamps
- Use Django's built-in fields (`CharField`, `IntegerField`, etc.)
- Add indexes for frequently queried fields

### URL Routing
- Follow RESTful conventions:
  - GET `/api/crypto/` - List resources
  - GET `/api/crypto/{id}/` - Retrieve single resource
  - POST `/api/crypto/` - Create resource
  - PUT/PATCH `/api/crypto/{id}/` - Update resource
  - DELETE `/api/crypto/{id}/` - Delete resource
- Use descriptive URL names with `name` parameter

### Database Operations
- Use Django ORM instead of raw SQL when possible
- Use `select_related()` and `prefetch_related()` to optimize queries
- Always handle `DoesNotExist` exceptions
- Use transactions for atomic operations: `transaction.atomic()`

### Security
- Enable CSRF protection for all POST/PUT/DELETE endpoints
- Use Django's built-in authentication/authorization
- Validate all user inputs
- Never expose sensitive data in responses
- Use environment variables for secrets (via `python-dotenv`)

### Settings
- Separate development and production settings
- Use environment variables for configuration
- Keep `SECRET_KEY` secure and never commit it
- Enable `DEBUG=False` in production
- Configure CORS properly for frontend access
