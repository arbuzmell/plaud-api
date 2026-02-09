"""Speaker management examples.

Speaker names live in each recording's transcription segments.
Use speakers.rename() to change a speaker's name in a specific recording.
"""

from plaud import PlaudClient

client = PlaudClient()

# List all known speakers (global list, read-only)
speakers = client.speakers.list()
for s in speakers:
    print(f"{s.name}  (ID: {s.id})")

# See who spoke in a specific recording
file_id = "YOUR_FILE_ID"
recording_speakers = client.speakers.get_for_recording(file_id)
for s in recording_speakers:
    print(f"{s['name']}: {s['segments_count']} segments")

# Rename a speaker in this recording's transcript
client.speakers.rename(file_id, "Speaker 1", "Alice Johnson")
