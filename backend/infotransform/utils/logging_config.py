"""
Enhanced logging configuration for InfoTransform
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from infotransform.config import config


# Global flag to prevent multiple logging configurations
_LOGGING_CONFIGURED = False

class LoggingManager:
    """Manages logging configuration for the entire application"""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        
    def setup_logging(self, environment: Optional[str] = None):
        """Setup logging configuration based on environment"""
        global _LOGGING_CONFIGURED
        
        if _LOGGING_CONFIGURED:
            return
            
        environment = environment or config.get('app.environment', 'development')
        
        # Get logging configuration
        log_config = self._get_logging_config(environment)
        
        # Configure root logger
        self._configure_root_logger(log_config)
        
        # Configure component-specific loggers
        self._configure_component_loggers(log_config)
        
        # Configure third-party loggers
        self._configure_third_party_loggers(log_config)
        
        _LOGGING_CONFIGURED = True
        
        # Log the configuration
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured for environment: {environment}")
        
    def _get_logging_config(self, environment: str) -> Dict[str, Any]:
        """Get logging configuration based on environment"""
        base_config = {
            'level': config.get('logging.level', 'INFO'),
            'format': config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'console_enabled': config.get('logging.console.enabled', True),
            'file_enabled': config.get('logging.file.enabled', True),
            'file_max_size': config.get('logging.file.max_size', '10MB'),
            'file_backup_count': config.get('logging.file.backup_count', 5),
        }
        
        # Environment-specific overrides
        env_configs = {
            'development': {
                'level': 'INFO',
                'component_levels': {
                    'infotransform.utils.token_counter': 'INFO',
                    'infotransform.processors.vision': 'INFO',
                    'infotransform.processors.batch_processor': 'INFO',
                    'infotransform.processors.async_converter': 'INFO',
                },
                'third_party_levels': {
                    'httpx': 'WARNING',  # Reduce HTTP request logs
                    'watchfiles': 'WARNING',  # Reduce file watching logs
                    'uvicorn.access': 'WARNING',  # Reduce access logs
                }
            },
            'staging': {
                'level': 'INFO',
                'component_levels': {
                    'infotransform.utils.token_counter': 'ERROR',
                    'infotransform.processors.vision': 'WARNING',
                    'infotransform.processors.batch_processor': 'WARNING',
                },
                'third_party_levels': {
                    'httpx': 'ERROR',
                    'watchfiles': 'ERROR',
                    'uvicorn.access': 'ERROR',
                }
            },
            'production': {
                'level': 'WARNING',
                'component_levels': {
                    'infotransform.utils.token_counter': 'ERROR',
                    'infotransform.processors.vision': 'ERROR',
                    'infotransform.processors.batch_processor': 'WARNING',
                },
                'third_party_levels': {
                    'httpx': 'ERROR',
                    'watchfiles': 'ERROR',
                    'uvicorn.access': 'ERROR',
                }
            }
        }
        
        # Merge environment-specific config
        if environment in env_configs:
            base_config.update(env_configs[environment])
        
        return base_config
        
    def _configure_root_logger(self, log_config: Dict[str, Any]):
        """Configure the root logger"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_config['level'].upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(log_config['format'])
        
        # Console handler
        if log_config['console_enabled']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(getattr(logging, log_config['level'].upper()))
            root_logger.addHandler(console_handler)
        
        # File handler
        if log_config['file_enabled']:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / 'infotransform.log'
            
            # Parse file size
            max_bytes = self._parse_size(log_config['file_max_size'])
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=log_config['file_backup_count']
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, log_config['level'].upper()))
            root_logger.addHandler(file_handler)
    
    def _configure_component_loggers(self, log_config: Dict[str, Any]):
        """Configure component-specific loggers"""
        component_levels = log_config.get('component_levels', {})
        
        for logger_name, level in component_levels.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, level.upper()))
            self.loggers[logger_name] = logger
    
    def _configure_third_party_loggers(self, log_config: Dict[str, Any]):
        """Configure third-party library loggers"""
        third_party_levels = log_config.get('third_party_levels', {})
        
        for logger_name, level in third_party_levels.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, level.upper()))
            self.loggers[logger_name] = logger
    
    def _parse_size(self, size_str: str) -> int:
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
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the configured settings"""
        global _LOGGING_CONFIGURED
        
        if not _LOGGING_CONFIGURED:
            self.setup_logging()
        
        return logging.getLogger(name)
    
    def set_debug_mode(self, enabled: bool = True):
        """Enable or disable debug mode for all loggers"""
        level = logging.DEBUG if enabled else logging.INFO
        
        # Update root logger
        logging.getLogger().setLevel(level)
        
        # Update all configured loggers
        for logger in self.loggers.values():
            logger.setLevel(level)
    
    def enable_quiet_mode(self):
        """Enable quiet mode - only show warnings and errors"""
        # Update root logger
        logging.getLogger().setLevel(logging.WARNING)
        
        # Update component loggers to be even quieter
        quiet_levels = {
            'infotransform.utils.token_counter': logging.ERROR,
            'infotransform.processors.vision': logging.ERROR,
            'infotransform.processors.batch_processor': logging.WARNING,
            'httpx': logging.ERROR,
            'watchfiles': logging.ERROR,
            'uvicorn.access': logging.ERROR,
        }
        
        for logger_name, level in quiet_levels.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)


# Global logging manager instance
logging_manager = LoggingManager()

# Convenience functions
def setup_logging(environment: Optional[str] = None):
    """Setup logging for the application"""
    logging_manager.setup_logging(environment)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger"""
    return logging_manager.get_logger(name)

def enable_debug_mode():
    """Enable debug logging"""
    logging_manager.set_debug_mode(True)

def enable_quiet_mode():
    """Enable quiet mode"""
    logging_manager.enable_quiet_mode()
