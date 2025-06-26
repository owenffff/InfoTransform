"""
Simplified logging configuration for InfoTransform
"""

import logging
import logging.handlers
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from infotransform.config import config as app_config

# Global flag to prevent multiple logging configurations
_LOGGING_CONFIGURED = False

def _load_logging_config() -> Dict[str, Any]:
    """Load logging configuration from YAML file"""
    config_path = Path(__file__).parent.parent.parent.parent / 'config' / 'logging_config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Logging config not found at {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def _parse_size(size_str: str) -> int:
    """Parse size string like '10MB' to bytes"""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)

def setup_logging(environment: Optional[str] = None, force_reconfigure: bool = False):
    """Setup logging configuration based on environment"""
    global _LOGGING_CONFIGURED
    
    if _LOGGING_CONFIGURED and not force_reconfigure:
        return
    
    # Get environment from parameter or app config
    if environment is None:
        environment = app_config.get('app.environment', 'development')
    
    # Load logging configuration
    try:
        config = _load_logging_config()
    except Exception as e:
        # Fallback to basic logging if config fails
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).error(f"Failed to load logging config: {e}")
        _LOGGING_CONFIGURED = True
        return
    
    # Get environment-specific settings
    env_config = config['environments'].get(environment, config['environments']['development'])
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, env_config['level'].upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config['format'])
    
    # Console handler
    if env_config.get('console', True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, env_config['level'].upper()))
        root_logger.addHandler(console_handler)
    
    # File handler
    if env_config.get('file', True):
        log_dir = Path(__file__).parent.parent.parent.parent / config.get('log_directory', 'logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / config.get('log_file_name', 'infotransform.log')
        
        # Parse file size
        max_bytes = _parse_size(env_config.get('file_max_size', '10MB'))
        backup_count = env_config.get('file_backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, env_config['level'].upper()))
        root_logger.addHandler(file_handler)
    
    # Apply component-specific overrides
    component_overrides = config.get('component_overrides', {}).get(environment, {})
    for logger_name, level in component_overrides.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))
    
    _LOGGING_CONFIGURED = True
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for environment: {environment}")

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger"""
    if not _LOGGING_CONFIGURED:
        setup_logging()
    
    return logging.getLogger(name)

def enable_debug_mode():
    """Enable debug logging for all loggers"""
    if not _LOGGING_CONFIGURED:
        setup_logging()
    
    # Set root logger to DEBUG
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Set all handlers to DEBUG
    for handler in logging.getLogger().handlers:
        handler.setLevel(logging.DEBUG)

def enable_quiet_mode():
    """Enable quiet mode - only show warnings and errors"""
    if not _LOGGING_CONFIGURED:
        setup_logging()
    
    # Set root logger to WARNING
    logging.getLogger().setLevel(logging.WARNING)
    
    # Set all handlers to WARNING
    for handler in logging.getLogger().handlers:
        handler.setLevel(logging.WARNING)
    
    # Set specific loggers to ERROR for even quieter operation
    quiet_loggers = [
        'infotransform.utils.token_counter',
        'infotransform.processors',
        'httpx',
        'uvicorn.access',
        'watchfiles'
    ]
    
    for logger_name in quiet_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)
