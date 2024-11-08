import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime
from backend.app.core.config import settings

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON formatted logs
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    """
    Set up logging configuration for the application
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # JSON File Handler (Timed Rotating)
    json_file_handler = TimedRotatingFileHandler(
        filename=log_dir / "app.json",
        when="midnight",
        interval=1,
        backupCount=30
    )
    json_file_handler.setLevel(logging.INFO)
    json_formatter = JSONFormatter()
    json_file_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_file_handler)

    # Set up loggers for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Create a separate logger for sensitive information
    sensitive_logger = logging.getLogger("sensitive")
    sensitive_handler = RotatingFileHandler(
        filename=log_dir / "sensitive.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3
    )
    sensitive_handler.setLevel(logging.INFO)
    sensitive_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sensitive_handler.setFormatter(sensitive_formatter)
    sensitive_logger.addHandler(sensitive_handler)
    sensitive_logger.propagate = False  # Don't propagate to root logger

    # Performance logger
    perf_logger = logging.getLogger("performance")
    perf_handler = TimedRotatingFileHandler(
        filename=log_dir / "performance.log",
        when="H",
        interval=1,
        backupCount=24
    )
    perf_handler.setLevel(logging.INFO)
    perf_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    perf_handler.setFormatter(perf_formatter)
    perf_logger.addHandler(perf_handler)
    perf_logger.propagate = False  # Don't propagate to root logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    """
    return logging.getLogger(name)

class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom LoggerAdapter to add context information to log messages
    """
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        if "user_id" in self.extra:
            extra["user_id"] = self.extra["user_id"]
        if "request_id" in self.extra:
            extra["request_id"] = self.extra["request_id"]
        kwargs["extra"] = extra
        return msg, kwargs

def get_request_logger(request_id: str, user_id: str = None) -> LoggerAdapter:
    """
    Get a logger adapter with request context
    """
    logger = logging.getLogger("request")
    extra = {"request_id": request_id}
    if user_id:
        extra["user_id"] = user_id
    return LoggerAdapter(logger, extra)

def log_function_call(func):
    """
    Decorator to log function calls
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling function: {func.__name__}")
        result = func(*args, **kwargs)
        logger.debug(f"Function {func.__name__} completed")
        return result
    return wrapper
<<<<<<< Updated upstream
    
'''
# Configure Sentry for error tracking (if enabled in settings)
=======

'''
>>>>>>> Stashed changes
def configure_sentry():
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[sentry_logging],
            environment=settings.ENVIRONMENT,
            release=settings.PROJECT_VERSION
        )
        logging.info("Sentry initialized for error tracking")

# Initialize logging when this module is imported
setup_logging()
configure_sentry()
'''

# Example usage
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    sensitive_logger = get_logger("sensitive")
    sensitive_logger.info("This is sensitive information")

    perf_logger = get_logger("performance")
    perf_logger.info("Performance metric: response_time=100ms")

    @log_function_call
    def example_function():
        logger.info("Inside example function")

    example_function()

    request_logger = get_request_logger("123456", "user123")
    request_logger.info("Processing request")

