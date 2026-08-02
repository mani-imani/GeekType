#!/usr/bin/env bash
# GeekType - automated setup for Linux (GNOME / Wayland)
#
# This script does everything we set up by hand:
#   1. installs wl-clipboard, ydotool, libnotify (for notifications)
#   2. creates a systemd service for ydotoold with a socket the
#      current user can actually access
#   3. registers a GNOME custom keyboard shortcut (F9) that runs
#      linux_hook.py
#
# Safe to re-run - existing pieces are skipped or overwritten cleanly.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_PATH="$SCRIPT_DIR/linux_hook.py"
LOG_PATH="/tmp/geektype.log"
SOCKET_PATH="/tmp/.ydotool_socket"
UID_GID="$(id -u):$(id -g)"

echo "== GeekType setup =="

echo "-> Installing dependencies (wl-clipboard, ydotool, libnotify-bin)..."
sudo apt-get update -qq
sudo apt-get install -y wl-clipboard ydotool libnotify-bin

echo "-> Setting up the ydotoold systemd service..."
sudo tee /etc/systemd/system/ydotool.service > /dev/null <<EOF
[Unit]
Description=ydotool daemon

[Service]
ExecStart=/usr/bin/ydotoold --socket-path=${SOCKET_PATH} --socket-own=${UID_GID} --socket-perm=0600
Restart=always

[Install]
WantedBy=default.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ydotool.service

echo "-> Registering the F9 GNOME shortcut..."
KEY_BASE="org.gnome.settings-daemon.plugins.media-keys"
CUSTOM_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/geektype/"

existing=$(gsettings get "$KEY_BASE" custom-keybindings)
if [[ "$existing" != *"geektype"* ]]; then
    if [[ "$existing" == "@as []" ]]; then
        new_list="['$CUSTOM_PATH']"
    else
        new_list="${existing%]*}, '$CUSTOM_PATH']"
    fi
    gsettings set "$KEY_BASE" custom-keybindings "$new_list"
fi

gsettings set "$KEY_BASE.custom-keybinding:$CUSTOM_PATH" name "GeekType"
gsettings set "$KEY_BASE.custom-keybinding:$CUSTOM_PATH" command \
    "bash -c \"python3 $HOOK_PATH >> $LOG_PATH 2>&1\""
gsettings set "$KEY_BASE.custom-keybinding:$CUSTOM_PATH" binding "F9"

echo
echo "== Done =="
echo "Select some wrongly-typed text anywhere and press F9."
echo "Log file: $LOG_PATH"
