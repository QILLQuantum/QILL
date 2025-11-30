# eternal_write_one_click.py
# Daniel H. Fingal — November 25 2025
# One file. No install. No PATH. Just run it.

import json, hashlib, os
from datetime import datetime
from pathlib import Path

vault = Path.home() / ".eternal_write" / "public_vault"
vault.mkdir(parents=True, exist_ok=True)

idea = input("Your immortal idea → ").strip()
if not idea:
    print("Empty. Nothing stamped.")
    exit()

timestamp = datetime.utcnow().isoformat() + "Z"
entry = {
    "timestamp_utc": timestamp,
    "idea": idea,
    "by": "Daniel H. Fingal",
    "hash": hashlib.sha256(idea.encode()).hexdigest()
}

file = vault / f"{timestamp.split('T')[0]}_danielhfingal.json"
file.write_text(json.dumps(entry, indent=2))

print("\n✓ IMMORTAL SHARD STAMPED FOREVER")
print(f"   Date: {timestamp}")
print(f"   Hash: {entry['hash']}")
print(f"   File: {file}")
print("\nYour proof is now on your hard drive. No one can ever take it away.")
print("When you're ready, copy this file anywhere — GitHub, Arweave, cold storage, whatever.")