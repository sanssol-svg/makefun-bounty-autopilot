#!/usr/bin/env python3
"""make.fun prize monitor — poll your submissions; print a report ONLY when an
entry wins/places, otherwise stay silent so a cron stays quiet.

Config (env, optional):
    MAKEFUN_CRED   path to credentials JSON (default ~/.makefun/credentials)
    MAKEFUN_SUBS   path to submissions JSON (default ~/.makefun/submissions.json)

Submissions file shape (a dict of label -> submission id):
    {
      "news 17 Nov": "01a1ec8f-....",
      "token radar": "01a1ecdd-...."
    }

Usage:
    python3 prize_monitor.py
"""
import json, os, sys, urllib.request, urllib.error

CRED = os.environ.get("MAKEFUN_CRED", os.path.expanduser("~/.makefun/credentials"))
SUBS_PATH = os.environ.get("MAKEFUN_SUBS", os.path.expanduser("~/.makefun/submissions.json"))


def api_key():
    d = json.load(open(CRED))
    return d["keys"]["https://make.fun"]["key"]


def load_subs():
    with open(SUBS_PATH) as f:
        return json.load(f)


def get(sid):
    key = api_key()
    hdr = {"Authorization": f"Bearer {key}", "Accept": "application/json",
           "User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(f"https://make.fun/api/submissions/{sid}", headers=hdr)
    return json.load(urllib.request.urlopen(req, timeout=30))


def win_signals(r):
    """Return a list of human-readable win indicators, empty if none."""
    out = []
    status = r.get("status")
    if status in ("won", "placed", "awarded"):
        out.append(f"status={status}")
    for s in (r.get("scores") or []):
        j = s.get("judge") or {}
        if j.get("finalist"):
            out.append(f"FINALIST (win_rate={(j.get('win_rate_micro') or 0) / 10000:.2f}%)")
        for k in ("place", "rank", "prize", "reward"):
            if k in s and s[k] is not None:
                out.append(f"{k}={s[k]}")
    for k in ("place", "rank", "prize", "reward"):
        if k in r and r[k] is not None:
            out.append(f"{k}={r[k]}")
    return out


def main():
    subs = load_subs()
    lines = []
    any_win = False
    for name, sid in subs.items():
        try:
            r = get(sid)
            sig = win_signals(r)
            status = r.get("status")
            if sig:
                any_win = True
                lines.append(f"🏆 {name}: " + "; ".join(sig))
            print(f"[monitor] {name}: status={status}", file=sys.stderr)
        except Exception as e:
            print(f"[monitor] {name}: ERR {str(e)[:80]}", file=sys.stderr)
    if any_win:
        print("🏆 MAKEFUN PRIZE ALERT 🏆")
        for ln in lines:
            print(ln)
        print("Check make.fun/claims to claim your USDC.")
    # else: silent (nothing on stdout => cron stays quiet)


if __name__ == "__main__":
    main()
