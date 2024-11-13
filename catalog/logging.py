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
        self.log_buffer = []
        self.index = "logs"  # Elasticsearch index to store logs

    def emit(self, record):
        try:
            # Format the log record to JSON
            json_log = self.format(record)
            # Convert JSON string back to a dict for Elasticsearch
            log_entry = json.loads(json_log)
            self.log_buffer.append(log_entry)

            # Send logs in bulk if buffer size exceeds threshold
            if len(self.log_buffer) >= 100:
                self.flush()
        except Exception:
            self.handleError(record)

    def flush(self):
        if self.log_buffer:
            # Bulk send logs to Elasticsearch
            actions = [
                {"_index": self.index, "_source": log_entry}
                for log_entry in self.log_buffer
            ]
            bulk(self.es, actions)
            self.log_buffer = []
