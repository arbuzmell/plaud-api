"""Upload an audio file and run analysis."""

from pathlib import Path

from plaud import PlaudClient

client = PlaudClient()

# Upload
recording = client.recordings.upload(
    Path("meeting.mp3"),
    name="Weekly Standup",
)
print(f"Uploaded: {recording.id}")

# Start analysis
client.transcriptions.start(recording.id, language="en")

# Wait for completion (blocks until done)
result = client.transcriptions.wait(recording.id, language="en", timeout=600)

# Save results back to Plaud
client.transcriptions.save_results(recording.id, result)
print("Analysis complete!")

# Retrieve the transcript
transcript = client.transcriptions.get(recording.id)
for seg in transcript.segments:
    print(f"[{seg.speaker}] {seg.text}")
