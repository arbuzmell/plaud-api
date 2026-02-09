"""Custom exceptions for the Plaud API client."""

from __future__ import annotations


class PlaudError(Exception):
    """Base exception for all Plaud API errors."""


class AuthenticationError(PlaudError):
    """Authentication failed — token missing, invalid, or expired."""


class NotFoundError(PlaudError):
    """Requested resource not found (404)."""


class APIError(PlaudError):
    """Generic API error with status code and response body."""

    def __init__(self, message: str, status_code: int | None = None, response_body: str = ""):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class AnalysisTimeoutError(PlaudError):
    """Analysis did not complete within the specified timeout."""


class UploadError(PlaudError):
    """Error during file upload flow."""
