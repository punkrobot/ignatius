"""Unit tests for ConfigValidator"""
import pytest
from unittest.mock import Mock

from ignatius.config.validation import ConfigValidator


class TestConfigValidator:
    """Test cases for ConfigValidator"""
    
    def test_validate_openai_config_success(self):
        """Test successful OpenAI config validation"""
        config = Mock()
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.OPENAI_TEMPERATURE = 0.7
        config.OPENAI_MAX_TOKENS = 500
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert errors == []
    
    def test_validate_openai_config_missing_api_key(self):
        """Test OpenAI config validation with missing API key"""
        config = Mock()
        config.OPENAI_API_KEY = None
        config.OPENAI_MODEL = "gpt-4o-mini"
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert "OPENAI_API_KEY is required" in errors
    
    def test_validate_openai_config_empty_api_key(self):
        """Test OpenAI config validation with empty API key"""
        config = Mock()
        config.OPENAI_API_KEY = "  "
        config.OPENAI_MODEL = "gpt-4o-mini"
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert "OPENAI_API_KEY must be a non-empty string" in errors
    
    def test_validate_openai_config_missing_model(self):
        """Test OpenAI config validation with missing model"""
        config = Mock()
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = None
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert "OPENAI_MODEL is required" in errors
    
    def test_validate_openai_config_invalid_temperature(self):
        """Test OpenAI config validation with invalid temperature"""
        config = Mock()
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.OPENAI_TEMPERATURE = 3.0  # Too high
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert "OPENAI_TEMPERATURE must be between 0.0 and 2.0" in errors
    
    def test_validate_openai_config_invalid_temperature_type(self):
        """Test OpenAI config validation with invalid temperature type"""
        config = Mock()
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.OPENAI_TEMPERATURE = "invalid"
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert "OPENAI_TEMPERATURE must be a valid number" in errors
    
    def test_validate_openai_config_invalid_max_tokens(self):
        """Test OpenAI config validation with invalid max tokens"""
        config = Mock()
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.OPENAI_MAX_TOKENS = -1
        
        errors = ConfigValidator.validate_openai_config(config)
        
        assert "OPENAI_MAX_TOKENS must be a positive integer" in errors
    
    def test_validate_mongodb_config_success(self):
        """Test successful MongoDB config validation"""
        config = Mock()
        config.MONGODB_DB = "test_db"
        config.MONGODB_HOST = "localhost"
        config.MONGODB_PORT = 27017
        config.MONGODB_USERNAME = "user"
        config.MONGODB_PASSWORD = "pass"
        
        errors = ConfigValidator.validate_mongodb_config(config)
        
        assert errors == []
    
    def test_validate_mongodb_config_missing_db(self):
        """Test MongoDB config validation with missing database"""
        config = Mock()
        config.MONGODB_DB = None
        config.MONGODB_HOST = "localhost"
        
        errors = ConfigValidator.validate_mongodb_config(config)
        
        assert "MONGODB_DB is required" in errors
    
    def test_validate_mongodb_config_invalid_port(self):
        """Test MongoDB config validation with invalid port"""
        config = Mock()
        config.MONGODB_DB = "test_db"
        config.MONGODB_HOST = "localhost"
        config.MONGODB_PORT = 70000  # Too high
        
        errors = ConfigValidator.validate_mongodb_config(config)
        
        assert "MONGODB_PORT must be between 1 and 65535" in errors
    
    def test_validate_mongodb_config_auth_inconsistency(self):
        """Test MongoDB config validation with inconsistent auth"""
        config = Mock()
        config.MONGODB_DB = "test_db"
        config.MONGODB_HOST = "localhost"
        config.MONGODB_PORT = 27017
        config.MONGODB_USERNAME = "user"
        config.MONGODB_PASSWORD = None  # Missing password
        
        errors = ConfigValidator.validate_mongodb_config(config)
        
        assert "Both MONGODB_USERNAME and MONGODB_PASSWORD must be provided together" in errors
    
    def test_validate_flask_config_success(self):
        """Test successful Flask config validation"""
        config = Mock()
        config.SECRET_KEY = "very-secure-secret-key"
        config.LOG_LEVEL = "INFO"
        
        errors = ConfigValidator.validate_flask_config(config)
        
        assert errors == []
    
    def test_validate_flask_config_missing_secret_key(self):
        """Test Flask config validation with missing secret key"""
        config = Mock()
        config.SECRET_KEY = None
        
        errors = ConfigValidator.validate_flask_config(config)
        
        assert "SECRET_KEY is required" in errors
    
    def test_validate_flask_config_invalid_log_level(self):
        """Test Flask config validation with invalid log level"""
        config = Mock()
        config.SECRET_KEY = "secure-secret-key"
        config.LOG_LEVEL = "INVALID"
        
        errors = ConfigValidator.validate_flask_config(config)
        
        assert "LOG_LEVEL must be one of:" in errors[0]
    
    def test_validate_config_comprehensive_success(self):
        """Test comprehensive config validation success"""
        config = Mock()
        # OpenAI config
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.OPENAI_TEMPERATURE = 0.7
        config.OPENAI_MAX_TOKENS = 500
        # MongoDB config
        config.MONGODB_DB = "test_db"
        config.MONGODB_HOST = "localhost"
        config.MONGODB_PORT = 27017
        config.MONGODB_USERNAME = None
        config.MONGODB_PASSWORD = None
        # Flask config
        config.SECRET_KEY = "secure-secret-key"
        config.LOG_LEVEL = "INFO"
        
        result = ConfigValidator.validate_config(config, 'development')
        
        assert result['valid'] is True
        assert result['errors'] == []
        assert result['environment'] == 'development'
    
    def test_validate_config_with_errors(self):
        """Test comprehensive config validation with errors"""
        config = Mock()
        config.OPENAI_API_KEY = None  # Missing
        config.SECRET_KEY = None  # Missing
        config.MONGODB_DB = None  # Missing
        
        result = ConfigValidator.validate_config(config)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert "OPENAI_API_KEY is required" in result['errors']
    
    def test_validate_config_production_warnings(self):
        """Test config validation with production-specific warnings"""
        config = Mock()
        # Valid basic config
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.OPENAI_TEMPERATURE = 0.7
        config.OPENAI_MAX_TOKENS = 500
        config.MONGODB_DB = "test_db"
        config.MONGODB_HOST = "localhost"
        config.MONGODB_PORT = 27017
        config.MONGODB_USERNAME = None
        config.MONGODB_PASSWORD = None
        config.SECRET_KEY = "secure-secret-key"
        config.LOG_LEVEL = "INFO"
        # Production warning trigger
        config.DEBUG = True
        
        result = ConfigValidator.validate_config(config, 'production')
        
        assert result['valid'] is True
        assert len(result['warnings']) > 0
        assert "DEBUG mode should be disabled in production" in result['warnings']
    
    def test_validate_config_production_dev_secret_key(self):
        """Test config validation with dev secret key in production"""
        config = Mock()
        config.OPENAI_API_KEY = "sk-test-key"
        config.OPENAI_MODEL = "gpt-4o-mini"
        config.MONGODB_DB = "test_db"
        config.MONGODB_HOST = "localhost"
        config.SECRET_KEY = "dev-secret-key"  # Contains 'dev'
        config.DEBUG = False
        
        result = ConfigValidator.validate_config(config, 'production')
        
        assert result['valid'] is False
        assert any("SECRET_KEY appears to be a development/test key" in error for error in result['errors'])