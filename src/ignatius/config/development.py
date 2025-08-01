"""Development environment configuration"""
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development configuration with debug enabled"""
    
    DEBUG = True
    TESTING = False
    
    # Development-specific MongoDB settings
    MONGODB_DB = BaseConfig.MONGODB_DB or 'ignatius_dev'
    
    # Relaxed settings for development
    SECRET_KEY = 'dev-secret-key-not-for-production'
    
    # Enhanced logging for development
    LOG_LEVEL = 'DEBUG'
    