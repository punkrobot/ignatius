"""Configuration factory for loading environment-specific settings"""
import os
import logging
from typing import Type
from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig
from .validation import ConfigValidator

logger = logging.getLogger(__name__)


class ConfigFactory:
    """Factory for creating configuration objects based on environment"""
    
    CONFIG_MAP = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    @classmethod
    def get_config(cls, env: str = None) -> Type[BaseConfig]:
        """
        Get configuration class for the specified environment.
        
        Args:
            env: Environment name. If None, uses FLASK_ENV or defaults to 'development'
            
        Returns:
            Configuration class for the environment
            
        Raises:
            ValueError: If environment is not supported
        """
        if env is None:
            env = os.getenv('FLASK_ENV', 'development')
        
        config_class = cls.CONFIG_MAP.get(env.lower())
        if not config_class:
            raise ValueError(f"Unsupported environment: {env}. "
                           f"Supported environments: {list(cls.CONFIG_MAP.keys())}")
        
        return config_class
    
    @classmethod
    def create_config(cls, env: str = None, validate: bool = True) -> BaseConfig:
        """
        Create and validate configuration instance for the specified environment.
        
        Args:
            env: Environment name. If None, uses FLASK_ENV or defaults to 'development'
            validate: Whether to run comprehensive validation
            
        Returns:
            Configuration instance
            
        Raises:
            ValueError: If environment is not supported or configuration is invalid
        """
        if env is None:
            env = os.getenv('FLASK_ENV', 'development')
        
        config_class = cls.get_config(env)
        config = config_class()
        
        # Basic validation from config class
        config.validate_required_settings()
        
        # Comprehensive validation if requested
        if validate:
            validation_result = ConfigValidator.validate_config(config, env)
            if not validation_result['valid']:
                error_msg = f"Configuration validation failed: {'; '.join(validation_result['errors'])}"
                raise ValueError(error_msg)
            
            # Log warnings if any
            if validation_result['warnings']:
                for warning in validation_result['warnings']:
                    logger.warning(f"Configuration warning: {warning}")
        
        logger.info(f"Successfully loaded {env} configuration")
        return config