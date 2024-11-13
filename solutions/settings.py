LOGGING = {
    "version": 1,
    "handlers": {
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "library.json.log",
            "formatter": "json",
            "maxBytes": 10485760,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "elasticsearch": {
            "class": "solutions.logging.ElasticsearchHandler",
            "formatter": "json",
            "hosts": ["http://127.0.0.1:9200"],
        },
    },
    "formatters": {
        "json": {
            "()": "solutions.logging.JSONFormatter",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console"],
            "level": "WARNING",
        },
        "catalog": {  # Your app logger
            "handlers": ["json_file", "console", "elasticsearch"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
