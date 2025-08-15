"""Base configuration settings"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """Base configuration class with common settings"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # MongoDB settings
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', '27017'))
    MONGODB_DB = os.getenv('MONGODB_DB', 'ignatius')
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
    MONGODB_AUTH_SOURCE = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # API settings
    API_VERSION = 'v1'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Prompts settings
    PROMPTS_FILE_PATH = os.getenv('PROMPTS_FILE_PATH', 
                                  str(Path(__file__).parent / 'prompts.yaml'))
    
    @classmethod
    def get_mongodb_settings(cls) -> Dict[str, Any]:
        """Get MongoDB configuration dictionary"""
        settings = {
            "db": cls.MONGODB_DB,
            "host": cls.MONGODB_HOST,
            "port": cls.MONGODB_PORT,
            "alias": "default",
        }
        
        # Add authentication if provided
        if cls.MONGODB_USERNAME and cls.MONGODB_PASSWORD:
            settings.update({
                "username": cls.MONGODB_USERNAME,
                "password": cls.MONGODB_PASSWORD,
                "authentication_source": cls.MONGODB_AUTH_SOURCE
            })
        
        return settings
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Validate that required settings are present"""
        required_settings = ['OPENAI_API_KEY']
        missing_settings = []
        
        for setting in required_settings:
            if not getattr(cls, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            raise ValueError(f"Missing required configuration settings: {', '.join(missing_settings)}")