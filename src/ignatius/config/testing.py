"""Testing environment configuration"""
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Testing configuration for unit and integration tests"""
    
    DEBUG = True
    TESTING = True
    
    # Test-specific MongoDB settings
    MONGODB_DB = 'ignatius_test'
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    
    # Testing-specific settings
    SECRET_KEY = 'test-secret-key'
    
    # Minimal logging for tests
    LOG_LEVEL = 'ERROR'
    
    # Mock OpenAI settings for testing
    OPENAI_API_KEY = 'test-api-key'  # Will be mocked in tests
    OPENAI_MODEL = 'gpt-3.5-turbo'
    OPENAI_TEMPERATURE = 0.0  # Deterministic for testing
    OPENAI_MAX_TOKENS = 100
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Skip validation for testing environment"""
        pass