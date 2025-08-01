"""Configuration validation utilities"""
import os
import logging
from typing import List, Optional, Dict, Any


logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration settings and environment variables"""
    
    @staticmethod
    def validate_openai_config(config: object) -> List[str]:
        """
        Validate OpenAI configuration settings
        
        Args:
            config: Configuration object to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check API key
        if not getattr(config, 'OPENAI_API_KEY', None):
            errors.append("OPENAI_API_KEY is required")
        elif not isinstance(config.OPENAI_API_KEY, str) or len(config.OPENAI_API_KEY.strip()) == 0:
            errors.append("OPENAI_API_KEY must be a non-empty string")
        
        # Check model
        if not getattr(config, 'OPENAI_MODEL', None):
            errors.append("OPENAI_MODEL is required")
        
        # Check temperature range
        temperature = getattr(config, 'OPENAI_TEMPERATURE', None)
        if temperature is not None:
            try:
                temp_float = float(temperature)
                if not 0.0 <= temp_float <= 2.0:
                    errors.append("OPENAI_TEMPERATURE must be between 0.0 and 2.0")
            except (ValueError, TypeError):
                errors.append("OPENAI_TEMPERATURE must be a valid number")
        
        # Check max tokens
        max_tokens = getattr(config, 'OPENAI_MAX_TOKENS', None)
        if max_tokens is not None:
            try:
                tokens_int = int(max_tokens)
                if tokens_int <= 0:
                    errors.append("OPENAI_MAX_TOKENS must be a positive integer")
            except (ValueError, TypeError):
                errors.append("OPENAI_MAX_TOKENS must be a valid integer")
        
        return errors
    
    @staticmethod
    def validate_mongodb_config(config: object) -> List[str]:
        """
        Validate MongoDB configuration settings
        
        Args:
            config: Configuration object to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check database name
        if not getattr(config, 'MONGODB_DB', None):
            errors.append("MONGODB_DB is required")
        
        # Check host
        if not getattr(config, 'MONGODB_HOST', None):
            errors.append("MONGODB_HOST is required")
        
        # Check port
        port = getattr(config, 'MONGODB_PORT', None)
        if port is not None:
            try:
                port_int = int(port)
                if not 1 <= port_int <= 65535:
                    errors.append("MONGODB_PORT must be between 1 and 65535")
            except (ValueError, TypeError):
                errors.append("MONGODB_PORT must be a valid integer")
        
        # Check authentication consistency
        username = getattr(config, 'MONGODB_USERNAME', None)
        password = getattr(config, 'MONGODB_PASSWORD', None)
        
        if bool(username) != bool(password):
            errors.append("Both MONGODB_USERNAME and MONGODB_PASSWORD must be provided together")
        
        return errors
    
    @staticmethod
    def validate_flask_config(config: object) -> List[str]:
        """
        Validate Flask configuration settings
        
        Args:
            config: Configuration object to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check secret key
        secret_key = getattr(config, 'SECRET_KEY', None)
        if not secret_key:
            errors.append("SECRET_KEY is required")
        elif len(secret_key) < 16:
            errors.append("SECRET_KEY should be at least 16 characters long")
        
        # Check log level
        log_level = getattr(config, 'LOG_LEVEL', None)
        if log_level:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if log_level.upper() not in valid_levels:
                errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        
        return errors
    
    @classmethod
    def validate_config(cls, config: object, environment: str = None) -> Dict[str, Any]:
        """
        Comprehensive configuration validation
        
        Args:
            config: Configuration object to validate
            environment: Environment name for context
            
        Returns:
            Dictionary with validation results
        """
        all_errors = []
        warnings = []
        
        # Run all validation checks
        all_errors.extend(cls.validate_openai_config(config))
        all_errors.extend(cls.validate_mongodb_config(config))
        all_errors.extend(cls.validate_flask_config(config))
        
        # Environment-specific validation
        if environment == 'production':
            # Additional production checks
            if getattr(config, 'DEBUG', False):
                warnings.append("DEBUG mode should be disabled in production")
            
            secret_key = getattr(config, 'SECRET_KEY', '')
            if 'dev' in secret_key.lower() or 'test' in secret_key.lower():
                all_errors.append("SECRET_KEY appears to be a development/test key in production")
        
        # Log results
        if all_errors:
            logger.error(f"Configuration validation failed: {all_errors}")
        if warnings:
            logger.warning(f"Configuration validation warnings: {warnings}")
        
        return {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': warnings,
            'environment': environment
        }