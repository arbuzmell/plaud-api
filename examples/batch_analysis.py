"""Find unanalyzed recordings and process them in batch."""

from plaud import PlaudClient

client = PlaudClient()

# Find recordings without transcription
recordings = client.recordings.list(limit=50)
unanalyzed = [r for r in recordings if not r.has_transcription]

print(f"Found {len(unanalyzed)} unanalyzed recordings")

for rec in unanalyzed:
    print(f"\nProcessing: {rec.filename} ({rec.duration_display})")
    try:
        client.transcriptions.start(rec.id, language="en")
        result = client.transcriptions.wait(rec.id, language="en", timeout=600)
        client.transcriptions.save_results(rec.id, result)
        print(f"  Done!")
    except Exception as e:
        print(f"  Error: {e}")
