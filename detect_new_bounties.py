#!/usr/bin/env python3
"""Detect NEW open make.fun bounties vs a seen-state file.

Prints a JSON list of open bounties whose slug is NOT in state["seen"].
Silent (empty stdout) when there are no new open bounties, so it can be
used as a cron monitor without spamming. State is NOT mutated here — the
orchestrator updates it after deciding (join vs skip).

Pagination: the board returns pages ordered oldest-first, so NEW bounties
land on the LAST page. This follows next_cursor through ALL pages.

Usage:
    python3 detect_new_bounties.py            # uses ~/.makefun/bounty_state.json
    MAKEFUN_STATE=/path/state.json python3 detect_new_bounties.py
"""
import json, os, sys, urllib.request, urllib.parse

STATE = os.environ.get("MAKEFUN_STATE", os.path.expanduser("~/.makefun/bounty_state.json"))
BOARD = os.environ.get("MAKEFUN_BOARD", "https://make.fun/api/competitions")


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f).get("seen", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def iter_comps():
    """Yield every competition across all pages."""
    url = BOARD
    seen_ids = set()
    for _ in range(50):  # hard cap pages to avoid infinite loop
        d = fetch(url)
        comps = d if isinstance(d, list) else d.get("competitions", d.get("items", []))
        for c in comps:
            cid = c.get("id") or c.get("slug")
            if cid in seen_ids:
                continue
            seen_ids.add(cid)
            yield c
        cursor = d.get("next_cursor") if isinstance(d, dict) else None
        if not cursor:
            break
        url = BOARD + "?" + urllib.parse.urlencode({"cursor": cursor})


def main():
    seen = load_state()
    new = []
    for c in iter_comps():
        slug = c.get("slug")
        status = (c.get("status") or c.get("state") or "").lower()
        if status != "open":
            continue
        if slug in seen:
            continue
        fee = c.get("entryFeeUsd") or c.get("entry_fee_usd") or c.get("entryFee") or 0
        subs = c.get("submissionCount") or c.get("submissions") or c.get("entryCount") or 0
        new.append({
            "slug": slug,
            "title": c.get("title"),
            "fee_usd": float(fee or 0),
            "submissions": subs,
            "deadline": c.get("deadline") or c.get("closesAt") or c.get("endsAt"),
            "status": status,
        })

    if new:
        print(json.dumps(new, indent=2))


if __name__ == "__main__":
    main()
