# FastAPI Starter Template

A production-ready FastAPI starter template with modern development practices and essential features built-in. This template provides a solid foundation for building scalable web APIs with Python.

## Features

- **Modern FastAPI Setup**: Latest FastAPI with async/await support
- **Database Integration**: PostgreSQL with SQLAlchemy 2.0 and Alembic migrations
- **Authentication Ready**: JWT authentication structure (easily configurable)
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Error Handling**: Centralized exception handling and custom error responses
- **Request Validation**: Pydantic models for request/response validation
- **CORS Support**: Configurable CORS middleware
- **Environment Configuration**: Pydantic Settings for environment management
- **Database Migrations**: Alembic integration for schema management
- **Service Layer Architecture**: Clean separation of concerns
- **Testing Setup**: Pytest configuration with test database
- **Code Quality**: Pre-configured linting and formatting tools
- **Health Checks**: Built-in health check endpoints

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- pip or poetry for dependency management

### Installation

1. **Clone or download this template:**

```bash
git clone https://github.com/raihanhd12/fastapi-starter.git
cd fastapi-starter
```

2. **Create and activate a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up the database:**

```bash
# Create database migrations
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Or use the fresh migration script
python scripts/migrate_fresh.py
```

6. **Run the application:**

```bash
python main.py
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and adjust the values:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
DATABASE_URL_TEST=postgresql://user:password@localhost/test_dbname

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_PORT="8000"
API_HOST="127.0.0.1"
API_KEY="yout-api-key"
```

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py script
python main.py
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1

# Reset database (development only)
python scripts/migrate_fresh.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api/test_users.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

## API Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

## Customization

This starter template is designed to be easily customizable:

1. **Add new models**: Create new SQLAlchemy models in `src/app/models/`
2. **Add new APIs**: Create new route files in `src/routes/api`
3. **Add business logic**: Implement services in `src/app/services/`
4. **Add validation**: Create Pydantic schemas in `src/app/schemas/`
5. **Add middleware**: Custom middleware goes in `src/app/middleware.py`

## Best Practices Included

- **Async/Await**: Proper async handling throughout the application
- **Dependency Injection**: Clean dependency management with FastAPI's DI system
- **Error Handling**: Centralized exception handling with custom HTTP exceptions
- **Input Validation**: Comprehensive request validation using Pydantic
- **Database Sessions**: Proper database session management with context managers
- **Security**: JWT authentication, password hashing, and CORS configuration
- **Testing**: Comprehensive test setup with fixtures and test database
- **Documentation**: Auto-generated API documentation with proper descriptions
- **Logging**: Structured logging configuration
- **Configuration Management**: Environment-based configuration with validation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you have any questions or need help getting started:

- Check the [documentation](http://localhost:8000/docs) when running locally
- Review the example implementations in the codebase
- Open an issue for bugs or feature requests

---

**Happy coding!** 🚀
