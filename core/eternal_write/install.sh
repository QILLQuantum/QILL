#!/bin/bash
# install.sh — Eternal Write Linux/macOS one-click
# Daniel H. Fingal — November 25 2025 — MIT License

set -e

ETERNAL_DIR="$HOME/.eternal_write"
BIN_DIR="$ETERNAL_DIR/bin"
VAULT_DIR="$ETERNAL_DIR/public_vault"

echo -e "\033[1;36mETERNAL WRITE — Installing immortal provenance engine...\033[0m"

mkdir -p "$BIN_DIR" "$VAULT_DIR"

curl -sSL https://raw.githubusercontent.com/danielhfingal/eternal/main/ew.py -o "$BIN_DIR/ew.py"
chmod +x "$BIN_DIR/ew.py"

# Add to PATH
SHELL_RC="$HOME/.bashrc"
[[ -f "$HOME/.zshrc" ]] && SHELL_RC="$HOME/.zshrc"

if ! grep -q "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
    echo '' >> "$SHELL_RC"
    echo "# Eternal Write" >> "$SHELL_RC"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
    export PATH="$PATH:$BIN_DIR"
fi

echo -e "\033[1;32mEternal Write installed.\033[0m"
echo -e "\033[1;33m→ Type: ew your idea here\033[0m"
echo -e "\033[1;35mYour public soul: https://github.com/danielhfingal/eternal-proofs/blob/main/ETERNAL_FEED.txt\033[0m"