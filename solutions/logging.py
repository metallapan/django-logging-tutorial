import json
import datetime
from typing import Any, Dict
import logging
from elasticsearch import Elasticsearch
import inspect


class ExtraLogger:
    """Log proxy that puts the extras parameter on the member 'extra'"""

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


def get_user_from_stack():
    # Get the request object
    for frame in inspect.stack():
        if frame[3] == "get_response":
            request = frame[0].f_locals.get("request")
            return request.user


class SimpleJSONFormatter(logging.Formatter):
    """Used with the ExtraLogger to log the nested extras"""

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
            "extra": record.extra,
        }

        # Add location info if available
        if record.pathname and record.lineno:
            log_data.update(
                {
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                }
            )

        # Add exception info if present
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        # Custom JSON encoder to handle datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if isinstance(obj, (datetime.date, datetime.datetime)):
                    return obj.isoformat()
                return super().default(obj)

        return json.dumps(log_data, cls=DateTimeEncoder)


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

        # Add location info if available
        if record.pathname and record.lineno:
            log_data.update(
                {
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                }
            )

        # Add exception info if present
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        # Add any extra attributes (filtered to avoid standard LogRecord attributes)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key
            not in logging.LogRecord(None, None, None, None, None, None, None,).__dict__
        }
        if extras:
            log_data["extra"] = extras

        # Custom JSON encoder to handle datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if isinstance(obj, (datetime.date, datetime.datetime)):
                    return obj.isoformat()
                return super().default(obj)

        return json.dumps(log_data, cls=DateTimeEncoder)


class ElasticsearchHandler(logging.Handler):
    def __init__(self, hosts):
        super().__init__()
        self.es = Elasticsearch(hosts)
        self.log_buffer = []
        self.index = "logs"  # Elasticsearch index to store logs

    def emit(self, record):
        try:
            # Format the log record to JSON and back to a dict that Elasticsearch can handle
            data = self.formatter.format(record)

            log_entry = json.loads(data)
            user = get_user_from_stack()
            log_entry["user"] = user.username if user else "-"
            # No lag but a lot of writes
            self.es.index(index=self.index, document=log_entry)

            ### Better for production: ###
            # self.log_buffer.append(log_entry)
            # Send logs in bulk if buffer size exceeds threshold
            # if len(self.log_buffer) >= 100:
            #   self.flush()
        except Exception:
            self.handleError(record)

    # def flush(self):
    #     if self.log_buffer:
    #         # Bulk send logs to Elasticsearch
    #         actions = [
    #             {
    #                 "_index": self.index,
    #                 "_source": log_entry
    #             }
    #             for log_entry in self.log_buffer
    #         ]
    #         bulk(self.es, actions)
    #         self.log_buffer = []
