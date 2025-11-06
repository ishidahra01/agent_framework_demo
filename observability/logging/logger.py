"""
Structured logging setup with PII masking
"""
import logging
import json
import re
import os
from datetime import datetime
from typing import Any, Dict


class PIIMasker:
    """Mask PII in log messages"""
    
    # Patterns for common PII
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'api_key': r'(api[_-]?key|apikey|access[_-]?token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]+)',
    }
    
    @classmethod
    def mask(cls, text: str) -> str:
        """Mask PII in text"""
        if not text:
            return text
        
        masked_text = text
        
        for pii_type, pattern in cls.PATTERNS.items():
            if pii_type == 'api_key':
                # Special handling for API keys
                masked_text = re.sub(
                    pattern,
                    lambda m: f"{m.group(1)}=***MASKED***",
                    masked_text,
                    flags=re.IGNORECASE
                )
            else:
                masked_text = re.sub(
                    pattern,
                    f"***{pii_type.upper()}_MASKED***",
                    masked_text
                )
        
        return masked_text


class JSONFormatter(logging.Formatter):
    """JSON log formatter with structured fields"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': PIIMasker.mask(record.getMessage()),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, 'job_id'):
            log_data['job_id'] = record.job_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add any custom fields from 'extra'
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info']:
                if isinstance(value, (str, int, float, bool, dict, list, type(None))):
                    log_data[key] = value
        
        return json.dumps(log_data)


def setup_logging(log_level: str = None):
    """
    Setup structured logging for the application
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    log_file = os.getenv("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    root_logger.info("Logging configured", extra={
        "log_level": log_level,
        "json_format": True,
        "pii_masking": True
    })


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)
