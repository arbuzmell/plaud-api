"""Token management for Plaud API.

Token is resolved in priority order:
1. Explicit ``token`` parameter
2. ``PLAUD_TOKEN`` environment variable
3. ``.env`` file in current directory
4. ``~/.config/plaud/token`` file
"""

from __future__ import annotations

import os
from pathlib import Path

TOKEN_DIR = Path.home() / ".config" / "plaud"
TOKEN_FILE = TOKEN_DIR / "token"
ENV_FILE = Path(".env")


def _read_env_token() -> str | None:
    """Read PLAUD_TOKEN from .env file in current directory."""
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "PLAUD_TOKEN":
            value = value.strip().strip("\"'")
            if value:
                return value
    return None


def resolve_token(token: str | None = None) -> str:
    """Resolve token from explicit value, env var, .env file, or config file.

    Priority:
        1. Explicit ``token`` parameter
        2. ``PLAUD_TOKEN`` environment variable
        3. ``.env`` file in current directory
        4. ``~/.config/plaud/token`` file

    Raises:
        ValueError: if no token can be found
    """
    if token:
        return token

    env_token = os.environ.get("PLAUD_TOKEN")
    if env_token:
        return env_token

    dotenv_token = _read_env_token()
    if dotenv_token:
        return dotenv_token

    if TOKEN_FILE.exists():
        stored = TOKEN_FILE.read_text().strip()
        if stored:
            return stored

    raise ValueError(
        "Plaud token not found.\n"
        "Options:\n"
        "  1. Run:  plaud auth setup  (saves to .env)\n"
        "  2. Set:  export PLAUD_TOKEN='your-token'\n"
    )


def save_token(token: str) -> Path:
    """Save token to ``.env`` file in current directory."""
    lines: list[str] = []
    found = False
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            stripped = line.strip()
            if stripped and "=" in stripped and stripped.partition("=")[0].strip() == "PLAUD_TOKEN":
                lines.append(f"PLAUD_TOKEN={token}")
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f"PLAUD_TOKEN={token}")
    ENV_FILE.write_text("\n".join(lines) + "\n")
    return ENV_FILE.resolve()


def clear_token() -> None:
    """Remove saved token from .env and ~/.config/plaud/token."""
    if ENV_FILE.exists():
        remaining = [
            line for line in ENV_FILE.read_text().splitlines()
            if not (line.strip() and "=" in line.strip()
                    and line.strip().partition("=")[0].strip() == "PLAUD_TOKEN")
        ]
        if remaining:
            ENV_FILE.write_text("\n".join(remaining) + "\n")
        else:
            ENV_FILE.unlink()
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
