from dotenv import dotenv_values

# Load environment variables from .env file
config = dotenv_values(".env")

# Database configuration
DATABASE_URL = config.get("DATABASE_URL", "")

# API settings
API_PORT = int(config.get("API_PORT", "8000"))
API_HOST = config.get("API_HOST", "0.0.0.0")
API_KEY = config.get("API_KEY", "")