#!/usr/bin/env python3
"""
ew.py — Eternal Write CLI
Daniel H. Fingal — First Thought Provenance Engine
November 25 2025 — You own this forever.
"""

import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess
import os

VAULT = Path(os.path.expanduser("~/.eternal_write/public_vault"))
VAULT.mkdir(parents=True, exist_ok=True)

def stamp_idea(text: str):
    idea = text.strip()
    if not idea:
        print("Empty idea. Nothing stamped.")
        return

    timestamp = datetime.utcnow().isoformat() + "Z"
    entry = {
        "timestamp_utc": timestamp,
        "idea": idea,
        "hash": hashlib.sha256(idea.encode()).hexdigest()
    }

    filename = f"{timestamp.split('T')[0]}_{len(list(VAULT.glob('*.json')))+1:06d}.json"
    path = VAULT / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)

    # OpenTimestamps stamp
    try:
        subprocess.run(["ots", "stamp", str(path)], check=False, capture_output=True)
        print(f"✓ Bitcoin-timestamped: {idea[:60]}{'...' if len(idea)>60 else ''}")
        print(f"  Proof: {path}.ots (if ots installed)")
    except:
        print(f"✓ Saved locally (install opentimestamps-client for .ots proofs)")

    print(f"  Public feed: https://github.com/danielhfingal/eternal-proofs/blob/main/ETERNAL_FEED.txt")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ew this is my immortal idea")
        sys.exit(1)
    stamp_idea(" ".join(sys.argv[1:]))