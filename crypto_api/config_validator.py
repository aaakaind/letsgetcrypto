"""
Configuration validation and management utilities for LetsGetCrypto.

Provides utilities for validating environment variables and configuration settings.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration validation fails"""
    pass


class ConfigValidator:
    """Validator for application configuration"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_env_var(self, name: str, required: bool = True, 
                        default: Optional[str] = None) -> Optional[str]:
        """
        Validate environment variable exists
        
        Args:
            name: Environment variable name
            required: Whether the variable is required
            default: Default value if not set
        
        Returns:
            Environment variable value or default
        
        Raises:
            ConfigurationError: If required variable is missing
        """
        value = os.environ.get(name, default)
        
        if required and not value:
            error_msg = f"Required environment variable {name} is not set"
            self.errors.append(error_msg)
            raise ConfigurationError(error_msg)
        
        if not value and not required:
            self.warnings.append(f"Optional environment variable {name} is not set, using default: {default}")
        
        return value
    
    def validate_url(self, url: str, name: str = "URL") -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            name: Name for error messages
        
        Returns:
            True if valid
        """
        if not url:
            self.errors.append(f"{name} is empty")
            return False
        
        if not (url.startswith('http://') or url.startswith('https://')):
            self.errors.append(f"{name} must start with http:// or https://")
            return False
        
        return True
    
    def validate_integer(self, value: Any, name: str = "value", 
                        min_val: Optional[int] = None, 
                        max_val: Optional[int] = None) -> bool:
        """
        Validate integer value
        
        Args:
            value: Value to validate
            name: Name for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            True if valid
        """
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            self.errors.append(f"{name} must be a valid integer, got: {value}")
            return False
        
        if min_val is not None and int_value < min_val:
            self.errors.append(f"{name} must be at least {min_val}, got: {int_value}")
            return False
        
        if max_val is not None and int_value > max_val:
            self.errors.append(f"{name} must be at most {max_val}, got: {int_value}")
            return False
        
        return True
    
    def validate_boolean(self, value: Any, name: str = "value") -> bool:
        """
        Validate boolean value
        
        Args:
            value: Value to validate (string 'true'/'false' or bool)
            name: Name for error messages
        
        Returns:
            True if valid
        """
        if isinstance(value, bool):
            return True
        
        if isinstance(value, str):
            if value.lower() in ('true', 'false', '1', '0', 'yes', 'no'):
                return True
        
        self.errors.append(f"{name} must be a valid boolean, got: {value}")
        return False
    
    def validate_file_exists(self, path: Union[str, Path], name: str = "file") -> bool:
        """
        Validate file exists
        
        Args:
            path: File path
            name: Name for error messages
        
        Returns:
            True if file exists
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            self.warnings.append(f"{name} does not exist: {path}")
            return False
        
        if not path_obj.is_file():
            self.errors.append(f"{name} is not a file: {path}")
            return False
        
        return True
    
    def validate_directory_exists(self, path: Union[str, Path], 
                                  name: str = "directory",
                                  create: bool = False) -> bool:
        """
        Validate directory exists
        
        Args:
            path: Directory path
            name: Name for error messages
            create: Whether to create directory if it doesn't exist
        
        Returns:
            True if directory exists or was created
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            if create:
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created {name}: {path}")
                    return True
                except OSError as e:
                    self.errors.append(f"Failed to create {name} {path}: {e}")
                    return False
            else:
                self.warnings.append(f"{name} does not exist: {path}")
                return False
        
        if not path_obj.is_dir():
            self.errors.append(f"{name} is not a directory: {path}")
            return False
        
        return True
    
    def get_errors(self) -> List[str]:
        """Get all validation errors"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get all validation warnings"""
        return self.warnings
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors"""
        return len(self.errors) > 0
    
    def report(self) -> str:
        """Generate validation report"""
        report = []
        
        if self.errors:
            report.append("Configuration Errors:")
            for error in self.errors:
                report.append(f"  ✗ {error}")
        
        if self.warnings:
            report.append("\nConfiguration Warnings:")
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")
        
        if not self.errors and not self.warnings:
            report.append("✓ Configuration is valid")
        
        return "\n".join(report)


def validate_crypto_api_settings(settings: Dict[str, Any]) -> ConfigValidator:
    """
    Validate crypto API settings
    
    Args:
        settings: Settings dictionary to validate
    
    Returns:
        ConfigValidator with validation results
    """
    validator = ConfigValidator()
    
    # Validate API URLs
    if 'COINGECKO_API_URL' in settings:
        validator.validate_url(settings['COINGECKO_API_URL'], 'COINGECKO_API_URL')
    else:
        validator.errors.append('COINGECKO_API_URL is required')
    
    if 'BINANCE_API_URL' in settings:
        validator.validate_url(settings['BINANCE_API_URL'], 'BINANCE_API_URL')
    
    # Validate timeouts and limits
    if 'REQUEST_TIMEOUT' in settings:
        validator.validate_integer(
            settings['REQUEST_TIMEOUT'], 
            'REQUEST_TIMEOUT',
            min_val=1,
            max_val=120
        )
    
    if 'CACHE_TIMEOUT' in settings:
        validator.validate_integer(
            settings['CACHE_TIMEOUT'],
            'CACHE_TIMEOUT',
            min_val=0,
            max_val=3600
        )
    
    if 'MAX_RETRIES' in settings:
        validator.validate_integer(
            settings['MAX_RETRIES'],
            'MAX_RETRIES',
            min_val=0,
            max_val=10
        )
    
    return validator


def validate_django_settings() -> ConfigValidator:
    """
    Validate Django settings
    
    Returns:
        ConfigValidator with validation results
    """
    validator = ConfigValidator()
    
    # Check critical Django settings
    secret_key = os.environ.get('DJANGO_SECRET_KEY')
    if not secret_key or secret_key.startswith('django-insecure'):
        if os.environ.get('DJANGO_DEBUG', 'False').lower() != 'true':
            validator.errors.append(
                'DJANGO_SECRET_KEY must be set to a secure value in production'
            )
    
    # Check database configuration
    database_url = os.environ.get('DATABASE_URL')
    debug = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
    
    if not database_url and not debug:
        validator.warnings.append(
            'DATABASE_URL not set, using SQLite (not recommended for production)'
        )
    
    # Validate allowed hosts
    allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '*')
    if allowed_hosts == '*' and not debug:
        validator.errors.append(
            'DJANGO_ALLOWED_HOSTS should not be * in production'
        )
    
    return validator


def load_and_validate_config() -> Dict[str, Any]:
    """
    Load and validate all configuration
    
    Returns:
        Dictionary with validation results
    
    Raises:
        ConfigurationError: If critical configuration is invalid
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validate Django settings
    django_validator = validate_django_settings()
    results['errors'].extend(django_validator.get_errors())
    results['warnings'].extend(django_validator.get_warnings())
    
    # Validate crypto API settings (would need to import from settings)
    # This is a placeholder for when called from Django context
    
    if results['errors']:
        results['valid'] = False
        logger.error("Configuration validation failed:")
        for error in results['errors']:
            logger.error(f"  ✗ {error}")
    
    if results['warnings']:
        logger.warning("Configuration warnings:")
        for warning in results['warnings']:
            logger.warning(f"  ⚠ {warning}")
    
    return results
