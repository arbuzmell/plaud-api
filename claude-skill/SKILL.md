---
name: plaud
description: Use when asked to upload to Plaud, transcribe audio, download recordings, list tags, check analysis status, manage speakers, or work with Plaud API for meeting transcription.
---

# Plaud API Integration

Skill for working with Plaud AI meeting recordings using the `plaud-api` Python package.

## Prerequisites

Install the package:
```bash
pip install plaud-api
```

Authenticate (one-time):
```bash
plaud auth setup    # Paste token from browser DevTools
```

## Default Behavior

**CRITICAL: Don't ask** — run the appropriate command immediately.

| User request | Action |
|---|---|
| "list recordings" | `plaud recordings list` |
| "transcribe file X" | `plaud transcription start <id> && plaud transcription status <id>` |
| "download recording" | `plaud recordings download <id>` |
| "list speakers" | `plaud speakers list` |
| "rename speaker" | `plaud speakers rename <file_id> "Old" "New"` |

## Core Commands

### List recordings
```bash
plaud recordings list
plaud recordings list -n 50
```

### Upload and analyze
```bash
plaud recordings upload audio.mp3 --name "Meeting Name" --analyze --language en
```

### Get transcription
```bash
plaud transcription get <file_id>
plaud transcription get <file_id> --json
```

### Get AI summary
```bash
plaud transcription summary <file_id>
```

### Start analysis manually
```bash
plaud transcription start <file_id> --language en
plaud transcription status <file_id>
```

### Download audio
```bash
plaud recordings download <file_id>
plaud recordings download <file_id> --url-only
```

### List tags
```bash
plaud tags list
plaud tags recordings <tag_id>
```

### Speaker management
```bash
plaud speakers list                                            # list known speakers
plaud speakers recording <file_id>                             # who spoke in a recording
plaud speakers rename <file_id> "Speaker 1" "John Smith"       # rename in a recording
```

## Python API (for advanced workflows)

```python
from plaud import PlaudClient

client = PlaudClient()

# List unanalyzed recordings
recordings = client.recordings.list(limit=50)
unanalyzed = [r for r in recordings if not r.has_transcription]

# Batch analyze
for rec in unanalyzed:
    client.transcriptions.start(rec.id, language="en")
    result = client.transcriptions.wait(rec.id, timeout=600)
    client.transcriptions.save_results(rec.id, result)
```

## Troubleshooting

- **"Plaud token not found"** — run `plaud auth setup` or set `PLAUD_TOKEN` env var
- **401 Unauthorized** — token expired, run `plaud auth setup` again
- **Analysis timeout** — increase timeout: `client.transcriptions.wait(id, timeout=900)`
