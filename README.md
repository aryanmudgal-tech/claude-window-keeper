# Claude Window Keeper

Sends a trivial "hi" via headless Claude Code roughly every 5 hours + a
2-3 minute buffer, chained off the *actual* previous fire time (not a fixed
daily clock), to control when your Claude.ai 5-hour usage window opens.

## 0. Do this FIRST, before touching GitHub at all

Confirm headless mode actually uses your subscription's session window,
not pay-as-you-go billing:

```bash
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN="paste-the-token-here"
claude -p "hi"
```

Then check claude.ai -> Settings -> Usage. If "current session" didn't
reset/update, stop here and let me know -- the rest of this won't do what
you want.

## 1. Create the repo

Make a **new GitHub repo, set to Public** (this needs unlimited free Actions
minutes -- a private repo polling every 5 minutes will blow through the
2,000 free minutes/month in about a week and start costing real money).
Nothing sensitive lives in this repo; your token stays in GitHub Secrets.

Push these files (this folder) to the repo's default branch.

## 2. Add your OAuth token as a secret

You already generated it in step 0. In the repo:
Settings -> Secrets and variables -> Actions -> New repository secret
- Name: `CLAUDE_CODE_OAUTH_TOKEN`
- Value: the `sk-ant-oat01-...` token from `claude setup-token`

(This token is valid for 1 year -- note the date, you'll need to regenerate
and update the secret before it expires.)

## 3. Enable Actions

Go to the repo's "Actions" tab and enable workflows if prompted. You should
see "Claude Window Keeper" listed, polling every 5 minutes.

## 4. Test it manually

In the Actions tab, select "Claude Window Keeper" -> "Run workflow" to fire
it by hand once, and watch the logs to confirm it runs cleanly end to end
(installs the CLI, calls claude, commits state.json).

## How it works

- `scripts/check_due.py` runs every 5 min (cheap, no CLI install) and just
  checks `state.json` for whether `next_trigger_utc` has passed.
- If due, `scripts/fire_and_advance.py` runs: installs the Claude CLI, sends
  `claude -p "hi"`, then sets the new `next_trigger_utc` to
  (this actual fire time) + 5h + random(2-3 min), and commits it.
- First run ever (no `state.json` yet) seeds to the next occurrence of
  1:32 AM America/New_York (your current ~1:30 AM reset + buffer).

## Known limitations (being upfront about these)

- **GitHub's scheduled cron is best-effort**, not exact-to-the-minute --
  expect occasional multi-minute slippage, especially during high load on
  GitHub's infrastructure. The 2-3 min buffer you asked for is tighter than
  GitHub's own guarantees.
- **60-day inactivity auto-disable**: GitHub automatically disables
  scheduled workflows on repos with no commits for 60 days. Since a
  successful fire commits `state.json`, this should never happen as long as
  it's running -- but if you ever pause it for 2+ months, you'll need to
  manually re-enable the workflow in the Actions tab.
- If `claude -p "hi"` fails for any reason (token expired, CLI issue,
  GitHub outage), the schedule does NOT advance -- it'll just keep retrying
  every 5 min until it succeeds, so a transient failure won't derail the
  whole chain.
- This uses your subscription's usage quota (confirmed by your step-0 test),
  so each trivial "hi" does consume a small amount of that quota -- worth
  keeping in mind if you're ever close to your weekly cap too.
