# JSONPlaceholder API Proxy

A FastAPI-based proxy service for the [JSONPlaceholder](https://jsonplaceholder.typicode.com/) REST API. This project provides a clean, type-safe interface with comprehensive validation and error handling for users and posts resources.

## Features

- ✨ **Full CRUD operations** for users and posts
- 🔍 **Query filtering** - filter posts by user ID
- ✅ **Request validation** with Pydantic models
- 🛡️ **Error handling** - 404 detection and custom error messages
- 📝 **Type-safe** - full type annotations throughout
- 🧪 **Well-tested** - comprehensive unit test coverage
- 📚 **Auto-generated OpenAPI docs** - interactive API documentation

## Technology Stack

- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation using Python type annotations
- **httpx** - Async HTTP client for upstream requests
- **pytest** - Testing framework with async support

## Installation

### Prerequisites

- Python 3.12+
- Poetry (recommended) or pip

### Using Poetry

```bash
# Clone the repository
git clone <repository-url>
cd jsonplaceholder-api-proxy

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd jsonplaceholder-api-proxy

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Running the Application

### Development Server

```bash
# Using Poetry
poetry run fastapi dev jsonplaceholder_api_proxy/api.py

# Or directly with uvicorn
uvicorn jsonplaceholder_api_proxy.api:app --reload
```

The API will be available at `http://localhost:8000`

### Production Server

```bash
uvicorn jsonplaceholder_api_proxy.api:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON schema**: http://localhost:8000/openapi.json

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| POST | `/users` | Create a new user |
| GET | `/users/{userId}` | Get user by ID |
| PUT | `/users/{userId}` | Update user by ID |
| DELETE | `/users/{userId}` | Delete user by ID |
| GET | `/users/{userId}/posts` | Get all posts by a user |

### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts` | List all posts |
| GET | `/posts?userId={id}` | List posts filtered by user ID |
| POST | `/posts` | Create a new post |
| GET | `/posts/{postId}` | Get post by ID |
| PATCH | `/posts/{postId}` | Update post by ID |
| DELETE | `/posts/{postId}` | Delete post by ID |

### Example Requests

**Create a user:**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "address": {
      "street": "Main St",
      "suite": "Apt 1",
      "city": "Springfield",
      "zipcode": "12345",
      "geo": {"lat": 40.7128, "lng": -74.0060}
    },
    "company": {
      "name": "Acme Corp",
      "catchPhrase": "Making things",
      "bs": "smart solutions"
    }
  }'
```

**Get all posts by user:**
```bash
curl http://localhost:8000/posts?userId=1
```

**Update a post:**
```bash
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "body": "Updated content"}'
```

## Testing

### Run All Tests

```bash
# Using Poetry
poetry run pytest

# Or directly
pytest
```

### Run with Coverage

```bash
pytest --cov=jsonplaceholder_api_proxy --cov-report=html
```

View coverage report at `htmlcov/index.html`

### Run Specific Test Files

```bash
# Test utilities
pytest tests/test_utils.py -v

# Test user endpoints
pytest tests/users/test_api_router.py -v

# Test post endpoints
pytest tests/posts/test_api_router.py -v
```

## Project Structure

```
jsonplaceholder-api-proxy/
├── jsonplaceholder_api_proxy/
│   ├── __init__.py
│   ├── api.py              # FastAPI app and router configuration
│   ├── endpoint_tags.py    # OpenAPI tags
│   ├── http_client.py      # HTTP client dependency
│   ├── models.py           # Shared models (HTTPError)
│   ├── utils.py            # Utility functions
│   ├── posts/
│   │   ├── __init__.py
│   │   ├── api_router.py   # Posts endpoint handlers
│   │   └── models.py       # Post Pydantic models
│   └── users/
│       ├── __init__.py
│       ├── api_router.py   # User endpoint handlers
│       └── models.py       # User Pydantic models
├── tests/
│   ├── test_utils.py
│   ├── test_http_client.py
│   ├── posts/
│   │   └── test_api_router.py
│   └── users/
│       └── test_api_router.py
├── pyproject.toml
└── README.md
```

## Development

### Code Quality

The project uses:
- Type hints throughout
- Pydantic for validation
- Async/await for non-blocking I/O
- Dependency injection for testing

### Adding New Endpoints

1. Define Pydantic models in the appropriate `models.py`
2. Add route handlers in `api_router.py`
3. Write tests in the `tests/` directory
4. Run tests to ensure coverage

## License

This project is provided as-is for educational and demonstration purposes.

## Author

Marios Hadjiantonis <mhadjiantonis@gmail.com>
