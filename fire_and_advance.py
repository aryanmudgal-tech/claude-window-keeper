"""
Only runs on the poll that's actually due. Sends a trivial headless message
via the Claude Code CLI (using your subscription, via CLAUDE_CODE_OAUTH_TOKEN),
then computes the next trigger as: this actual fire time + 5 hours + a random
2-3 minute buffer. True chaining -- each trigger is anchored to the previous
ACTUAL fire time, not a fixed daily clock.
"""
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

STATE_FILE = "state.json"

BUFFER_MIN_MINUTES = 2
BUFFER_MAX_MINUTES = 3

# Trivial ping -- no reasoning needed, so use the cheapest/fastest model.
# Use a full pinned model name (e.g. "claude-haiku-4-5") instead of the
# "haiku" alias if you want this to never silently change models on you.
MODEL = "haiku"


def main():
    now = datetime.now(ZoneInfo("UTC"))
    print(f"Firing at {now.isoformat()}")

    result = subprocess.run(
        ["claude", "-p", "hi", "--model", MODEL, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    print("STDOUT:", result.stdout[:1000])
    if result.returncode != 0:
        print("STDERR:", result.stderr[:1000])
        print("Claude call failed -- NOT advancing the schedule, so the next "
              "5-minute poll will simply retry.")
        sys.exit(1)

    buffer_minutes = random.uniform(BUFFER_MIN_MINUTES, BUFFER_MAX_MINUTES)
    next_trigger = now + timedelta(hours=5, minutes=buffer_minutes)

    state = {
        "next_trigger_utc": next_trigger.isoformat(),
        "last_fired_utc": now.isoformat(),
        "last_buffer_minutes": round(buffer_minutes, 2),
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Success. Next trigger: {next_trigger.isoformat()} "
          f"(buffer was {buffer_minutes:.2f} min)")


if __name__ == "__main__":
    main()
