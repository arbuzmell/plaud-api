"""plaud — Unofficial Python client for the Plaud AI API."""

__version__ = "0.1.0"

from plaud.client import PlaudClient
from plaud.exceptions import (
    AnalysisTimeoutError,
    APIError,
    AuthenticationError,
    NotFoundError,
    PlaudError,
    UploadError,
)

__all__ = [
    "PlaudClient",
    "PlaudError",
    "AuthenticationError",
    "NotFoundError",
    "APIError",
    "AnalysisTimeoutError",
    "UploadError",
    "__version__",
]
