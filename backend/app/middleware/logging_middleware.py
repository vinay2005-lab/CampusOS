"""Logging middleware for request/response tracking."""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details.

        Args:
            request: HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response: HTTP response
        """
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", str(time.time()))

        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Request ID: {request_id}"
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                f"Request Error: {request.method} {request.url.path} | "
                f"Error: {str(e)} | Request ID: {request_id}"
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response details
        logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {process_time:.3f}s | "
            f"Request ID: {request_id}"
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        return response
