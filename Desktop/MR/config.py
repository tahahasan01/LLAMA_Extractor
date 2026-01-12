import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # TMDb API Configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_key_here')
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
    
    # Database Configuration
    # Set USE_SQL_SERVER to True to use SQL Server instead of SQLite
    USE_SQL_SERVER = os.getenv('USE_SQL_SERVER', 'False').lower() == 'true'
    
    # SQLite Configuration
    DATABASE_PATH = 'movie_chatbot.db'
    
    # SQL Server Configuration
    SQL_SERVER_HOST = os.getenv('SQL_SERVER_HOST', 'localhost')
    SQL_SERVER_DATABASE = os.getenv('SQL_SERVER_DATABASE', 'MovieChatbot')
    SQL_SERVER_USERNAME = os.getenv('SQL_SERVER_USERNAME', '')
    SQL_SERVER_PASSWORD = os.getenv('SQL_SERVER_PASSWORD', '')
    SQL_SERVER_DRIVER = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # SQL Server connection string - built after class attributes are defined
    SQL_SERVER_CONNECTION_STRING = None
    
    # Recommendation Settings
    DEFAULT_RECOMMENDATIONS = 10
    CONTENT_BASED_WEIGHT = 0.4
    COLLABORATIVE_WEIGHT = 0.6
    
    # Cache Settings
    CACHE_EXPIRY_HOURS = 24
    
    # API Rate Limits
    TMDB_MAX_REQUESTS_PER_SECOND = 4
    TMDB_REQUEST_TIMEOUT = 10
    
    # Flask Configuration
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # ML Model Settings
    MIN_RATINGS_FOR_COLLABORATIVE = 5
    SIMILARITY_THRESHOLD = 0.3
    MAX_CACHE_SIZE = 1000


# Build SQL Server connection string after Config class is defined
def _build_sql_server_connection_string():
    """Build SQL Server connection string"""
    if Config.SQL_SERVER_USERNAME and Config.SQL_SERVER_PASSWORD:
        # SQL Server Authentication
        return (
            f"DRIVER={{{Config.SQL_SERVER_DRIVER}}};"
            f"SERVER={Config.SQL_SERVER_HOST};"
            f"DATABASE={Config.SQL_SERVER_DATABASE};"
            f"UID={Config.SQL_SERVER_USERNAME};"
            f"PWD={Config.SQL_SERVER_PASSWORD}"
        )
    else:
        # Windows Authentication
        return (
            f"DRIVER={{{Config.SQL_SERVER_DRIVER}}};"
            f"SERVER={Config.SQL_SERVER_HOST};"
            f"DATABASE={Config.SQL_SERVER_DATABASE};"
            f"Trusted_Connection=yes;"
        )

Config.SQL_SERVER_CONNECTION_STRING = _build_sql_server_connection_string()
