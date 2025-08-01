"""Production environment configuration"""
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production configuration with security hardening"""
    
    DEBUG = False
    TESTING = False
    
    # Production-specific MongoDB settings
    MONGODB_DB = BaseConfig.MONGODB_DB or 'ignatius'
    
    # Enhanced security for production
    SECRET_KEY = BaseConfig.SECRET_KEY
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Enhanced validation for production"""
        super().validate_required_settings()
        
        # Additional production-specific validations
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be changed from default in production")
        
        if not cls.MONGODB_USERNAME or not cls.MONGODB_PASSWORD:
            raise ValueError("MongoDB authentication is required in production")