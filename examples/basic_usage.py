"""Basic usage of the Plaud API client."""

from plaud import PlaudClient

# Initialize — token auto-detected from PLAUD_TOKEN env or ~/.config/plaud/token
client = PlaudClient()

# List recent recordings
recordings = client.recordings.list(limit=5)
for r in recordings:
    print(f"{r.filename}  ({r.duration_display})  [{r.id}]")

# Get transcription for the most recent recording
if recordings:
    rec = recordings[0]
    transcript = client.transcriptions.get(rec.id)
    for seg in transcript.segments:
        speaker = f"[{seg.speaker}] " if seg.speaker else ""
        print(f"{speaker}{seg.text}")
