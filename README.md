# makefun-bounty-autopilot 🤖

Detect, monitor, and auto-submit **make.fun** coding bounties from a server —
without leaking your credentials.

> **What this is:** the "kitchen" scripts that power an autonomous bounty
> hunter. It detects new bounties, monitors your submissions for wins, and
> documents the exact CLI flow to build + submit an entry.
>
> **What this is NOT:** a magic "one command = win" bot. make.fun bounties
> are judged on merit; these scripts remove the manual grind (detection,
> polling, submission ceremony), not the need to actually build a good entry.

---

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│  detect_new_bounties.py   → poll board, print NEW bounties   │
│           ↓ (agent decides: join / skip)                     │
│  build the entry (code / image) via an agent coding session  │
│           ↓                                                  │
│  submit_one.sh            → init → bundle → check → submit    │
│           ↓                                                  │
│  prize_monitor.py         → poll submissions, alert on win    │
└─────────────────────────────────────────────────────────────┘
```

Run the first and last on a cron (e.g. every 3h / 6h). The middle step is
the part that needs a human-or-agent to actually author the entry.

---

## Setup

### 1. Get the makefun CLI

Download a bounty kit from make.fun — it ships `cli/makefun.mjs` plus a
`RULES.txt` and `competition.yaml`. Put `makefun.mjs` on your `PATH`.

### 2. Create credentials (never commit these)

```bash
makefun connect          # links your make.fun account
# creates ~/.makefun/credentials  and  ~/.makefun/sans-keypair.json
```

### 3. Seed the state files

```bash
mkdir -p ~/.makefun
echo '{"seen": {}}' > ~/.makefun/bounty_state.json
echo '{}' > ~/.makefun/submissions.json
```

Add your submission IDs to `submissions.json` as `{"label": "01a1ec8f-..."}`
so `prize_monitor.py` knows what to watch.

### 4. Run

```bash
# detect new bounties (empty output = none)
python3 detect_new_bounties.py

# monitor your submissions (empty output = no win yet)
python3 prize_monitor.py
```

---

## The full submit flow (reference)

`submit_one.sh` documents the CLI ceremony. The **critical** part is the
agent coding session: make.fun grades a *transcript* of how you built the
entry (`thinking_reproduces`, `thinking_revised`, `thinking_turns` gates).
You must author the code inside a recorded session, not paste a finished
file. See the script comments + the makefun `RULES.txt` for exact rules.

```bash
./submit_one.sh <competition-slug> <source-dir> <title>
```

---

## Security (read this before pushing anything)

make.fun's `makefun init` writes **two** things that MUST NOT leave your
machine:

1. `~/.makefun/credentials` — your account bearer token
2. `~/.makefun/sans-keypair.json` — your payout wallet private key
3. `.makefun/freshness.json` — contains your payout **wallet address** +
   a drand anchor signature
4. `LICENSE` — `makefun init` writes your wallet address into the
   copyright line. **Edit it** before committing (e.g. `Copyright (c) 2026 <your-handle>`).

`.gitignore` here already excludes all of the above. **Always re-audit
before `git push`** — search your repo for wallet addresses and 87-88 char
base58 seeds:

```bash
git ls-files | xargs grep -lE '<YOUR_WALLET_ADDR>|[1-9A-HJ-NP-Za-km-z]{87}' 2>/dev/null
```

---

## Files

| File | Purpose |
|---|---|
| `detect_new_bounties.py` | Print NEW open bounties (silent if none) |
| `prize_monitor.py` | Poll submissions, print alert only on a win |
| `submit_one.sh` | Reference CLI flow (init → bundle → check → submit) |
| `.env.example` | Config placeholders |
| `.gitignore` | Excludes all credentials & internals |

---

## Honest expectations

- Bounties with thousands of entries (e.g. token-radar = 15,500 entries
  for 10 spots) are a lottery — this tooling removes the grind, not the odds.
- Bounties with **hundreds** of entries and low entry fees give you the best
  edge per dollar.
- The entry must be genuinely good. Auto-submit ≠ auto-win.
