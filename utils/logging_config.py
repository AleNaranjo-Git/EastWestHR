import logging
import logging.config
import os
from typing import Dict, Any, Optional

def setup_logging(
    default_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "app.log",
    file_level: Optional[str] = None
) -> None:
    """
    Configures logging for the application.
    Logs to both console and a rotating file handler.
    """
    env = os.getenv("APP_ENV", "development")
    console_level = "WARNING" if env == "production" else "DEBUG"
    
    if file_level is None:
        file_level = default_level

    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": console_level,
            "stream": "ext://sys.stdout",
        }
    }
    root_handlers = ["console"]

    if env == "production":
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": file_level,
            "filename": os.path.join(log_dir, log_file),
            "maxBytes": 1024*1024*5,
            "backupCount": 5,
            "encoding": "utf8",
        }
        root_handlers.append("file")

    LOGGING_CONFIG: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "simple": {
                "format": "[%(levelname)s] %(message)s"
            },
        },
        "handlers": handlers,
        "root": {
            "handlers": root_handlers,
            "level": default_level,
        },
        "loggers": {},
    }

    logging.config.dictConfig(LOGGING_CONFIG)