"""Unit tests for ConfigFactory"""
import pytest
from unittest.mock import patch, Mock
import os

from ignatius.config.factory import ConfigFactory
from ignatius.config.base import BaseConfig
from ignatius.config.development import DevelopmentConfig
from ignatius.config.production import ProductionConfig
from ignatius.config.testing import TestingConfig


class TestConfigFactory:
    """Test cases for ConfigFactory"""
    
    def test_get_config_development(self):
        """Test getting development configuration"""
        config_class = ConfigFactory.get_config('development')
        assert config_class == DevelopmentConfig
    
    def test_get_config_production(self):
        """Test getting production configuration"""
        config_class = ConfigFactory.get_config('production')
        assert config_class == ProductionConfig
    
    def test_get_config_testing(self):
        """Test getting testing configuration"""
        config_class = ConfigFactory.get_config('testing')
        assert config_class == TestingConfig
    
    def test_get_config_invalid_environment(self):
        """Test getting config for invalid environment"""
        with pytest.raises(ValueError, match="Unsupported environment: invalid"):
            ConfigFactory.get_config('invalid')
    
    def test_get_config_case_insensitive(self):
        """Test that environment names are case insensitive"""
        assert ConfigFactory.get_config('DEVELOPMENT') == DevelopmentConfig
        assert ConfigFactory.get_config('Production') == ProductionConfig
        assert ConfigFactory.get_config('TESTING') == TestingConfig
    
    @patch.dict(os.environ, {'FLASK_ENV': 'production'})
    def test_get_config_from_environment(self):
        """Test getting config from FLASK_ENV environment variable"""
        config_class = ConfigFactory.get_config()
        assert config_class == ProductionConfig
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_default_environment(self):
        """Test getting default config when no environment set"""
        config_class = ConfigFactory.get_config()
        assert config_class == DevelopmentConfig
    
    @patch.object(DevelopmentConfig, 'validate_required_settings')
    def test_create_config_success(self, mock_validate):
        """Test successful config creation"""
        mock_validate.return_value = None
        
        config = ConfigFactory.create_config('development', validate=False)
        
        assert isinstance(config, DevelopmentConfig)
        mock_validate.assert_called_once()
    
    @patch.object(DevelopmentConfig, 'validate_required_settings')
    def test_create_config_validation_failure(self, mock_validate):
        """Test config creation with validation failure"""
        mock_validate.side_effect = ValueError("Missing required setting")
        
        with pytest.raises(ValueError, match="Missing required setting"):
            ConfigFactory.create_config('development', validate=False)
    
    @patch('ignatius.config.factory.ConfigValidator')
    @patch.object(DevelopmentConfig, 'validate_required_settings')
    def test_create_config_with_validation(self, mock_validate, mock_validator):
        """Test config creation with comprehensive validation"""
        mock_validate.return_value = None
        mock_validator.validate_config.return_value = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        config = ConfigFactory.create_config('development', validate=True)
        
        assert isinstance(config, DevelopmentConfig)
        mock_validator.validate_config.assert_called_once_with(config, 'development')
    
    @patch('ignatius.config.factory.ConfigValidator')
    @patch.object(DevelopmentConfig, 'validate_required_settings')
    def test_create_config_validation_errors(self, mock_validate, mock_validator):
        """Test config creation with validation errors"""
        mock_validate.return_value = None
        mock_validator.validate_config.return_value = {
            'valid': False,
            'errors': ['OPENAI_API_KEY is required'],
            'warnings': []
        }
        
        with pytest.raises(ValueError, match="Configuration validation failed"):
            ConfigFactory.create_config('development', validate=True)
    
    @patch('ignatius.config.factory.ConfigValidator')
    @patch('ignatius.config.factory.logger')
    @patch.object(DevelopmentConfig, 'validate_required_settings')
    def test_create_config_with_warnings(self, mock_validate, mock_logger, mock_validator):
        """Test config creation with validation warnings"""
        mock_validate.return_value = None
        mock_validator.validate_config.return_value = {
            'valid': True,
            'errors': [],
            'warnings': ['DEBUG mode enabled in production']
        }
        
        config = ConfigFactory.create_config('development', validate=True)
        
        assert isinstance(config, DevelopmentConfig)
        mock_logger.warning.assert_called_once()
    
    @patch.dict(os.environ, {'FLASK_ENV': 'testing'})
    @patch.object(TestingConfig, 'validate_required_settings')
    def test_create_config_auto_environment_detection(self, mock_validate):
        """Test automatic environment detection from FLASK_ENV"""
        mock_validate.return_value = None
        
        config = ConfigFactory.create_config(validate=False)
        
        assert isinstance(config, TestingConfig)
    
    def test_config_map_completeness(self):
        """Test that CONFIG_MAP contains all expected environments"""
        expected_envs = {'development', 'production', 'testing'}
        actual_envs = set(ConfigFactory.CONFIG_MAP.keys())
        
        assert actual_envs == expected_envs
    
    def test_config_map_values(self):
        """Test that CONFIG_MAP values are correct config classes"""
        assert ConfigFactory.CONFIG_MAP['development'] == DevelopmentConfig
        assert ConfigFactory.CONFIG_MAP['production'] == ProductionConfig
        assert ConfigFactory.CONFIG_MAP['testing'] == TestingConfig