# Claude Code Skill: Plaud

A Claude Code skill for working with Plaud AI recordings.

## Setup

1. Install the `plaud-api` package:
   ```bash
   pip install plaud-api
   ```

2. Authenticate:
   ```bash
   plaud auth setup
   ```

3. Copy `SKILL.md` to your project's Claude Code skills directory:
   ```bash
   mkdir -p .claude/skills/plaud
   cp SKILL.md .claude/skills/plaud/SKILL.md
   ```

   Claude Code auto-discovers skills from `.claude/skills/*/SKILL.md` — no additional configuration needed.

## Usage

Once installed, just ask Claude:

- "list my Plaud recordings"
- "transcribe the latest recording"
- "show speakers for recording abc123"
- "upload meeting.mp3 to Plaud"
