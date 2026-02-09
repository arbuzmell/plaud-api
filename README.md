# plaud-api

[![PyPI](https://img.shields.io/pypi/v/plaud-api)](https://pypi.org/project/plaud-api/)
[![Python](https://img.shields.io/pypi/pyversions/plaud-api)](https://pypi.org/project/plaud-api/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-38%20passed-brightgreen)]()

Unofficial Python client for the [Plaud AI](https://plaud.ai) API.

[Plaud](https://plaud.ai) is a wearable meeting recorder that captures audio and provides cloud-based transcription and AI summaries. There is no official public API — this library is reverse-engineered from browser traffic to `api.plaud.ai` and allows programmatic access to your recordings, transcriptions, speakers, and tags.

> **Disclaimer:** This is an unofficial, reverse-engineered client. It is not affiliated with, endorsed by, or connected to Plaud Inc. in any way. Use at your own risk. The API may change without notice.

## Features

- List, upload, and download recordings
- Start transcription/analysis and retrieve results
- Get AI-generated meeting summaries
- Manage speakers (list, rename, per-recording stats)
- Organize recordings with tags
- Typed Pydantic models for all API responses
- CLI tool for quick operations from the terminal

**Requires Python 3.10+**

## Installation

```bash
pip install plaud-api
```

From source (local development):

```bash
git clone https://github.com/arbuzmell/plaud-api.git
cd plaud-api
pip install -e ".[dev]"
```

## Authentication

Token is resolved in this order:
1. Explicit `token=` parameter
2. `PLAUD_TOKEN` environment variable
3. `.env` file in current directory (`PLAUD_TOKEN=...`)
4. `~/.config/plaud/token` file

### How to get the token

1. Open [web.plaud.ai](https://web.plaud.ai) and sign in
2. Open DevTools → Network tab → find any request to `api.plaud.ai`
3. Copy the `Authorization` header value (without the "bearer " prefix)
4. Run `plaud auth setup` and paste it

**Step-by-step guides with screenshots:**

| Browser | Guide |
|---------|-------|
| Google Chrome | [Token guide for Chrome](docs/token-chrome.md) |
| Safari | [Token guide for Safari](docs/token-safari.md) |
| Firefox | [Token guide for Firefox](docs/token-firefox.md) |

> Safari users: DevTools are disabled by default — see the [Safari guide](docs/token-safari.md) for how to enable them.

## Quick Start

```python
from plaud import PlaudClient

client = PlaudClient()  # auto-detects token from env / config file

# List recent recordings
recordings = client.recordings.list(limit=5)
for rec in recordings:
    print(f"{rec.filename}  {rec.duration_display}  id={rec.id}")

# Get transcription for the first recording
transcript = client.transcriptions.get(recordings[0].id)
for seg in transcript.segments:
    print(f"[{seg.speaker}] {seg.text}")

# Get AI summary
summary = client.transcriptions.get_summary(recordings[0].id)
print(summary.content)
```

## API Reference

### Recordings

| Method | Returns | Description |
|--------|---------|-------------|
| `client.recordings.list(limit=50)` | `list[Recording]` | List recent recordings, most recent first |
| `client.recordings.get(file_id)` | `Recording` | Get a single recording by ID |
| `client.recordings.get_audio_url(file_id)` | `str` | Get a temporary S3 presigned URL to download the audio |
| `client.recordings.upload(path, name=...)` | `Recording` | Upload an MP3/OPUS file to Plaud |
| `client.recordings.get_raw(file_id)` | `dict` | Raw API response (includes `trans_result`, `ai_content`, etc.) |

`Recording` fields: `id`, `filename`, `duration_ms`, `filesize`, `created_at`, `has_transcription`, `has_summary`, `tag_ids`, `duration_display`, `duration_seconds`.

### Transcriptions

Analysis is a 3-step flow: **start -> wait -> save_results**.

```python
# 1. Start analysis on the Plaud server
client.transcriptions.start(file_id, language="en")

# 2. Block until the analysis completes (polls every 10s)
result = client.transcriptions.wait(file_id, language="en", timeout=600)

# 3. Save the results back to Plaud cloud (required to persist them)
client.transcriptions.save_results(file_id, result)
```

After analysis is saved, you can retrieve the structured data:

| Method | Returns | Description |
|--------|---------|-------------|
| `client.transcriptions.get(file_id)` | `Transcription` | Segments with `speaker`, `text`, `start_time_ms`, `end_time_ms` |
| `client.transcriptions.get_summary(file_id)` | `Summary` | AI-generated summary as markdown |
| `client.transcriptions.get_status(file_id)` | `AnalysisStatus` | Check if analysis is `complete` |
| `client.transcriptions.update_transcript(file_id, segments)` | `dict` | Update transcript segments (e.g. fix speaker names) |

Supported languages: `en`, `ru`, `zh`, `ja`, `ko`, `de`, `fr`, `es`, and others.

### Speakers

Speaker names live in each recording's transcription. Use `rename()` to change them.

| Method | Returns | Description |
|--------|---------|-------------|
| `client.speakers.list()` | `list[Speaker]` | All known speakers (global list, read-only) |
| `client.speakers.get_for_recording(file_id)` | `list[dict]` | Speakers in a recording with `name` and `segments_count` |
| `client.speakers.rename(file_id, old, new)` | `dict` | Rename a speaker in a recording's transcript |

```python
# See who spoke in a recording
speakers = client.speakers.get_for_recording("file_id")
# [{"name": "Speaker 1", "segments_count": 42}, {"name": "Speaker 2", ...}]

# Rename "Speaker 1" to "Alice" in this recording
client.speakers.rename("file_id", "Speaker 1", "Alice")
```

### Tags

| Method | Returns | Description |
|--------|---------|-------------|
| `client.tags.list()` | `list[Tag]` | All tags (folders) |
| `client.tags.get_recordings(tag_id)` | `list[str]` | Recording IDs belonging to a tag |

## CLI Usage

```bash
# Recordings
plaud recordings list                              # list recent recordings
plaud recordings list -n 50                        # list more
plaud recordings get <file_id>                     # show recording details
plaud recordings upload meeting.mp3 --name "Standup" --analyze
plaud recordings download <file_id>                # download audio file
plaud recordings download <file_id> --url-only     # just print the URL

# Transcription
plaud transcription start <file_id> --language en  # start analysis
plaud transcription status <file_id>               # check progress
plaud transcription get <file_id>                  # print transcript
plaud transcription get <file_id> --json           # print as JSON
plaud transcription summary <file_id>              # print AI summary

# Speakers
plaud speakers list                                         # list known speakers
plaud speakers recording <file_id>                          # who spoke in a recording
plaud speakers rename <file_id> "Speaker 1" "Alice"         # rename in a recording

# Tags
plaud tags list                                    # list all tags
plaud tags recordings <tag_id>                     # recording IDs in a tag

# Auth
plaud auth setup                                   # paste token manually
plaud auth token                                   # print current token
plaud auth logout                                  # remove saved token
```

Short aliases: `rec`, `tr`, `sp` for `recordings`, `transcription`, `speakers`.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Plaud token not found` | Run `plaud auth setup` or set `PLAUD_TOKEN` env var |
| `Authentication failed (401)` | Token expired. Run `plaud auth setup` to get a new one |
| `AnalysisTimeoutError` | Increase timeout: `client.transcriptions.wait(id, timeout=900)`. Long recordings can take up to 10 min |
| `NotFoundError` | Check the file ID. Use `plaud recordings list` to find valid IDs |
| `APIError 500` | Plaud server issue. The client retries 5xx automatically (3 attempts) |

## Claude Code Skill

A ready-to-use Claude Code skill is included in `claude-skill/`. See [claude-skill/README.md](claude-skill/README.md) for setup instructions.

## Contributing

1. Clone the repo
2. `pip install -e ".[dev]"`
3. `pytest` to run tests
4. `ruff check src/` to lint

## Legal Disclaimer

This project is for educational and personal use. It interacts with an undocumented API that was reverse-engineered from browser traffic. The author is not responsible for any consequences of using this software. The API may break at any time. Do not use this for any purpose that violates Plaud's Terms of Service.
