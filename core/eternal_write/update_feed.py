```python
#!/usr/bin/env python3
import os
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).parent
FEED = REPO_DIR / "ETERNAL_FEED.txt"
VAULT = Path.home() / ".eternal_write" / "public_vault"

def update():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    entries = sorted(VAULT.glob("*.json"))[-5:]  # last 5 for preview

    lines = [
        "ETERNAL WRITE — PUBLIC FIRST-THOUGHT LEDGER",
        "Daniel H. Fingal (@danielhfingal)",
        f"Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
    ]

    with open(FEED, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")
        for entry in entries:
            with open(entry) as ef:
                data = __import__("json").load(ef)
            f.write(f"\n=== {data['timestamp_utc']} ===\n")
            f.write(f"{data['idea']}\n")

    print("ETERNAL_FEED.txt updated")

if __name__ == "__main__":
    update()