"""
Runs every 5 minutes. Cheap and fast: only reads state.json (or computes a
first-time seed) and tells the workflow whether it's time to fire yet.
Does NOT install the Claude CLI or write any files -- that only happens in
fire_and_advance.py, once, only on the run that actually fires.
"""
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

STATE_FILE = "state.json"
LOCAL_TZ = ZoneInfo("America/New_York")

# First-ever seed: 1:30 AM local + a couple minutes, matching your current
# window reset. Only used if state.json doesn't exist yet.
SEED_HOUR = 1
SEED_MINUTE = 32


def get_next_trigger_utc():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
        return datetime.fromisoformat(state["next_trigger_utc"])

    # No state file yet -> seed to the next occurrence of 1:32 AM local time
    now_local = datetime.now(LOCAL_TZ)
    candidate = now_local.replace(
        hour=SEED_HOUR, minute=SEED_MINUTE, second=0, microsecond=0
    )
    if candidate <= now_local:
        candidate += timedelta(days=1)
    return candidate.astimezone(ZoneInfo("UTC"))


def main():
    next_trigger = get_next_trigger_utc()
    now = datetime.now(ZoneInfo("UTC"))
    due = now >= next_trigger

    print(f"Now (UTC):          {now.isoformat()}")
    print(f"Next trigger (UTC): {next_trigger.isoformat()}")
    print(f"Due: {due}")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"due={'true' if due else 'false'}\n")


if __name__ == "__main__":
    main()
