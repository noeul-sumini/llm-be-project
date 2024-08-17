import logging
from logging.config import dictConfig

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s | %(name)s | %(lineno)d",
        },
    },
    "handlers": {
        "console": {
            "level": "ERROR",
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "app.log",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
        "app_logger": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# 로깅 설정 적용
dictConfig(log_config)

# 로거 가져오기
logger = logging.getLogger("app_logger")
