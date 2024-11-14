"""Half-implemented JSON logging - find the TODO/s"""

import json
import datetime
from typing import Any
import logging


class ExtraLogger:
    """Log proxy that puts the extras parameter on the member 'extra',
    which may help with resolving extra data for the formatter."""

    def __init__(self, name):
        self._log = logging.getLogger(name)

    def info(self, *args, extra=None, **kwargs):
        self._log.info(*args, extra={"extra": extra}, **kwargs)

    def debug(self, *args, extra=None, **kwargs):
        self._log.debug(*args, extra={"extra": extra}, **kwargs)

    def warning(self, *args, extra=None, **kwargs):
        self._log.warning(*args, extra={"extra": extra}, **kwargs)

    def critical(self, *args, extra=None, **kwargs):
        self._log.critical(*args, extra={"extra": extra}, **kwargs)

    def error(self, *args, extra=None, **kwargs):
        self._log.error(*args, extra={"extra": extra}, **kwargs)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON, including any extra attributes,
    format date-times, and adds location info if it exists.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record as JSON.

        Includes standard LogRecord attributes and any extra attributes
        added through the extra parameter when logging.
        """
        # Get basic log record attributes
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # TODO EX1: We need to log extra attributes here somehow

        # Custom JSON encoder to handle datetime objects
        # Almost every implementation will need this, as the default
        # encoder cannot handle datetimes
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if isinstance(obj, (datetime.date, datetime.datetime)):
                    return obj.isoformat()
                return super().default(obj)

        return json.dumps(log_data, cls=DateTimeEncoder)


# TODO EX5: Elasticsearch Handler
from elasticsearch import Elasticsearch


class ElasticsearchHandler(logging.Handler):
    def __init__(self, hosts):
        super().__init__()
        self.es = Elasticsearch(hosts)
        self.index = "logs"  # Elasticsearch index to store logs

    def emit(self, record):
        try:
            # TODO EX5: Format the log record to JSON and back to a dict that Elasticsearch can handle
            # TODO EX5: Add user to the entry? Hostname, other context?

            self.es.index(index=self.index, document=log_entry)

        except Exception: