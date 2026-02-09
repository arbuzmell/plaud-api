"""CLI entry point for the ``plaud`` command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from plaud import PlaudClient, __version__
from plaud.auth import clear_token, resolve_token, save_token

# ═══════════════════════════════════════════════════════════════════════════════
# Recordings
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_recordings_list(args: argparse.Namespace) -> None:
    client = PlaudClient()
    recordings = client.recordings.list(limit=args.limit)
    if not recordings:
        print("No recordings found.")
        return

    print(f"{'Filename':<40} {'Duration':>8}  {'Date':<12}  ID")
    print("-" * 90)
    for r in recordings:
        date_str = r.created_at.strftime("%Y-%m-%d")
        print(f"{r.filename:<40} {r.duration_display:>8}  {date_str:<12}  {r.id}")
    print(f"\nTotal: {len(recordings)} recordings")


def cmd_recordings_get(args: argparse.Namespace) -> None:
    client = PlaudClient()
    r = client.recordings.get(args.file_id)
    print(f"ID:        {r.id}")
    print(f"Filename:  {r.filename}")
    print(f"Duration:  {r.duration_display}")
    print(f"Size:      {r.filesize:,} bytes")
    print(f"Created:   {r.created_at.isoformat()}")
    print(f"Has transcript: {r.has_transcription}")
    print(f"Has summary:    {r.has_summary}")


def cmd_recordings_upload(args: argparse.Namespace) -> None:
    client = PlaudClient()
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Uploading {file_path.name}...")
    recording = client.recordings.upload(file_path, name=args.name)
    print("Upload complete!")
    print(f"  ID:       {recording.id}")
    print(f"  Filename: {recording.filename}")

    if args.analyze:
        print(f"\nStarting analysis (language: {args.language})...")
        client.transcriptions.start(recording.id, language=args.language)
        result = client.transcriptions.wait(recording.id, language=args.language)
        client.transcriptions.save_results(recording.id, result)
        print("Analysis complete!")


def cmd_recordings_download(args: argparse.Namespace) -> None:
    client = PlaudClient()
    url = client.recordings.get_audio_url(args.file_id)
    if args.url_only:
        print(url)
    else:
        import requests

        print(f"Downloading audio for {args.file_id}...")
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()

        out = Path(args.output) if args.output else Path(f"{args.file_id}.mp3")
        with open(out, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved to {out}")


# ═══════════════════════════════════════════════════════════════════════════════
# Transcriptions
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_transcription_start(args: argparse.Namespace) -> None:
    client = PlaudClient()
    print(f"Starting analysis for {args.file_id} (language: {args.language})...")
    client.transcriptions.start(args.file_id, language=args.language)
    print("Analysis started.")


def cmd_transcription_status(args: argparse.Namespace) -> None:
    client = PlaudClient()
    status = client.transcriptions.get_status(args.file_id, language=args.language)
    state = "Complete" if status.complete else "Processing"
    print(f"Status:  {state}")
    print(f"Message: {status.message}")


def cmd_transcription_get(args: argparse.Namespace) -> None:
    client = PlaudClient()
    transcript = client.transcriptions.get(args.file_id)
    if not transcript.segments:
        print("No transcription available.")
        return

    if args.json:
        data = [
            {
                "speaker": s.speaker,
                "text": s.text,
                "start_time_ms": s.start_time_ms,
                "end_time_ms": s.end_time_ms,
            }
            for s in transcript.segments
        ]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for seg in transcript.segments:
            if seg.speaker:
                print(f"[{seg.speaker}] {seg.text}")
            else:
                print(seg.text)


def cmd_transcription_summary(args: argparse.Namespace) -> None:
    client = PlaudClient()
    summary = client.transcriptions.get_summary(args.file_id)
    if summary.content:
        print(summary.content)
    else:
        print("No summary available.")


# ═══════════════════════════════════════════════════════════════════════════════
# Speakers
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_speakers_list(args: argparse.Namespace) -> None:
    client = PlaudClient()
    speakers = client.speakers.list()
    if not speakers:
        print("No speakers found.")
        return
    for s in speakers:
        print(f"  {s.name:<30}  (ID: {s.id})")
    print(f"\nTotal: {len(speakers)} speakers")


def cmd_speakers_rename(args: argparse.Namespace) -> None:
    client = PlaudClient()
    client.speakers.rename(args.file_id, args.old_name, args.new_name)
    print(f"Renamed '{args.old_name}' -> '{args.new_name}' in recording {args.file_id}")


def cmd_speakers_recording(args: argparse.Namespace) -> None:
    client = PlaudClient()
    speakers = client.speakers.get_for_recording(args.file_id)
    if not speakers:
        print("No speakers found in this recording.")
        return
    for s in speakers:
        print(f"  {s['name']:<25}  ({s['segments_count']} segments)")
    print(f"\nTotal: {len(speakers)} speakers")


# ═══════════════════════════════════════════════════════════════════════════════
# Tags
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_tags_list(args: argparse.Namespace) -> None:
    client = PlaudClient()
    tags = client.tags.list()
    if not tags:
        print("No tags found.")
        return
    for t in tags:
        print(f"  {t.name:<30}  ({t.recording_count} recordings)  ID: {t.id}")
    print(f"\nTotal: {len(tags)} tags")


def cmd_tags_recordings(args: argparse.Namespace) -> None:
    client = PlaudClient()
    file_ids = client.tags.get_recordings(args.tag_id)
    if not file_ids:
        print("No recordings in this tag.")
        return
    for fid in file_ids:
        print(fid)
    print(f"\nTotal: {len(file_ids)} recordings")


# ═══════════════════════════════════════════════════════════════════════════════
# Auth
# ═══════════════════════════════════════════════════════════════════════════════


def cmd_auth_token(args: argparse.Namespace) -> None:
    try:
        token = resolve_token()
        print(token)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def cmd_auth_setup(args: argparse.Namespace) -> None:
    print("Paste your Plaud token below.")
    print(
        "(Get it from browser DevTools -> Network"
        " -> any api.plaud.ai request -> Authorization header)"
    )
    print()
    token = input("Token: ").strip()
    if not token:
        print("No token provided.", file=sys.stderr)
        sys.exit(1)
    if token.lower().startswith("bearer "):
        token = token[7:]
    path = save_token(token)
    print(f"Token saved to {path}")


def cmd_auth_logout(args: argparse.Namespace) -> None:
    clear_token()
    print("Token removed.")


# ═══════════════════════════════════════════════════════════════════════════════
# Parser
# ═══════════════════════════════════════════════════════════════════════════════


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plaud",
        description="Unofficial CLI for the Plaud AI API",
    )
    parser.add_argument("-V", "--version", action="version", version=f"plaud-api {__version__}")

    sub = parser.add_subparsers(dest="command", help="Command group")

    # --- recordings ---
    rec = sub.add_parser("recordings", aliases=["rec"], help="Manage recordings")
    rec_sub = rec.add_subparsers(dest="subcommand")

    rec_list = rec_sub.add_parser("list", help="List recordings")
    rec_list.add_argument("-n", "--limit", type=int, default=20)
    rec_list.set_defaults(func=cmd_recordings_list)

    rec_get = rec_sub.add_parser("get", help="Get recording details")
    rec_get.add_argument("file_id")
    rec_get.set_defaults(func=cmd_recordings_get)

    rec_upload = rec_sub.add_parser("upload", help="Upload audio file")
    rec_upload.add_argument("file", help="Path to audio file")
    rec_upload.add_argument("--name", "-N", help="Recording name")
    rec_upload.add_argument("--analyze", "-a", action="store_true", default=False,
                            help="Run analysis after upload")
    rec_upload.add_argument("--language", "-l", default="en")
    rec_upload.set_defaults(func=cmd_recordings_upload)

    rec_dl = rec_sub.add_parser("download", help="Download audio")
    rec_dl.add_argument("file_id")
    rec_dl.add_argument("--output", "-o")
    rec_dl.add_argument("--url-only", action="store_true", help="Print URL only")
    rec_dl.set_defaults(func=cmd_recordings_download)

    # --- transcription ---
    tr = sub.add_parser("transcription", aliases=["tr"], help="Transcription & summary")
    tr_sub = tr.add_subparsers(dest="subcommand")

    tr_start = tr_sub.add_parser("start", help="Start analysis")
    tr_start.add_argument("file_id")
    tr_start.add_argument("--language", "-l", default="en")
    tr_start.set_defaults(func=cmd_transcription_start)

    tr_status = tr_sub.add_parser("status", help="Check analysis status")
    tr_status.add_argument("file_id")
    tr_status.add_argument("--language", "-l", default="en")
    tr_status.set_defaults(func=cmd_transcription_status)

    tr_get = tr_sub.add_parser("get", help="Get transcription")
    tr_get.add_argument("file_id")
    tr_get.add_argument("--json", action="store_true")
    tr_get.set_defaults(func=cmd_transcription_get)

    tr_summ = tr_sub.add_parser("summary", help="Get AI summary")
    tr_summ.add_argument("file_id")
    tr_summ.set_defaults(func=cmd_transcription_summary)

    # --- speakers ---
    sp = sub.add_parser("speakers", aliases=["sp"], help="Manage speakers")
    sp_sub = sp.add_subparsers(dest="subcommand")

    sp_list = sp_sub.add_parser("list", help="List all speakers")
    sp_list.set_defaults(func=cmd_speakers_list)

    sp_rename = sp_sub.add_parser("rename", help="Rename a speaker in a recording")
    sp_rename.add_argument("file_id", help="Recording ID")
    sp_rename.add_argument("old_name", help="Current speaker name in the transcript")
    sp_rename.add_argument("new_name", help="New speaker name")
    sp_rename.set_defaults(func=cmd_speakers_rename)

    sp_rec = sp_sub.add_parser("recording", help="Speakers in a recording")
    sp_rec.add_argument("file_id")
    sp_rec.set_defaults(func=cmd_speakers_recording)

    # --- tags ---
    tg = sub.add_parser("tags", help="Manage tags")
    tg_sub = tg.add_subparsers(dest="subcommand")

    tg_list = tg_sub.add_parser("list", help="List all tags")
    tg_list.set_defaults(func=cmd_tags_list)

    tg_recs = tg_sub.add_parser("recordings", help="Recording IDs in a tag")
    tg_recs.add_argument("tag_id")
    tg_recs.set_defaults(func=cmd_tags_recordings)

    # --- auth ---
    au = sub.add_parser("auth", help="Authentication")
    au_sub = au.add_subparsers(dest="subcommand")

    au_token = au_sub.add_parser("token", help="Show current token")
    au_token.set_defaults(func=cmd_auth_token)

    au_setup = au_sub.add_parser("setup", help="Paste token manually")
    au_setup.set_defaults(func=cmd_auth_setup)

    au_logout = au_sub.add_parser("logout", help="Remove saved token")
    au_logout.set_defaults(func=cmd_auth_logout)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if not hasattr(args, "func"):
        # Subcommand group without a subcommand
        # Find and print help for the subcommand group
        parser.parse_args([args.command, "--help"])
        sys.exit(0)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
