"""PlaudClient — main entry point for the Plaud API."""

from __future__ import annotations

from plaud.api.recordings import RecordingsAPI
from plaud.api.speakers import SpeakersAPI
from plaud.api.tags import TagsAPI
from plaud.api.transcriptions import TranscriptionsAPI
from plaud.auth import resolve_token
from plaud.session import PlaudSession


class PlaudClient:
    """High-level client for the Plaud API.

    Usage::

        from plaud import PlaudClient

        client = PlaudClient()  # auto-detect token from env / config file
        # or
        client = PlaudClient(token="eyJ...")
        # Regional endpoint (e.g. Southeast Asia):
        client = PlaudClient(base_url="https://api-apse1.plaud.ai")

        recordings = client.recordings.list()
        transcript = client.transcriptions.get("file_id")
        speakers = client.speakers.list()
        tags = client.tags.list()
    """

    def __init__(self, token: str | None = None, *, base_url: str | None = None) -> None:
        """Initialize the client.

        Args:
            token: Plaud JWT token. If not provided, resolves from
                   ``PLAUD_TOKEN`` env var or ``~/.config/plaud/token``.
            base_url: Override the API base URL for regional endpoints,
                e.g. ``"https://api-apse1.plaud.ai"`` for Southeast Asia.
                If not provided, defaults to ``https://api.plaud.ai``.
        """
        self._token = resolve_token(token)
        if base_url is None:
            self._session = PlaudSession(self._token)
        else:
            self._session = PlaudSession(self._token, base_url=base_url)

        self.recordings = RecordingsAPI(self._session)
        self.transcriptions = TranscriptionsAPI(self._session)
        self.speakers = SpeakersAPI(self._session)
        self.tags = TagsAPI(self._session)
