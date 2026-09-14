# common/logging/config.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler"
        }
    },
    "loggers": {
        "audit": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
}
