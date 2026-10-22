import logging
import uuid
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to hold the Request ID across async tasks
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

class StructuredLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_ctx_var.get()
        return f'[{self.formatTime(record)}] [{record.levelname}] [req_id={req_id}] {record.getMessage()}'

def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogFormatter())
    logger.addHandler(handler)
    return logger

logger = setup_logging()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx_var.set(req_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        
        request_id_ctx_var.reset(token)
        return response