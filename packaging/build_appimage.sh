#!/usr/bin/env bash
# Builds GeekType-x86_64.AppImage from packaging/GeekType.AppDir
#
# Usage:
#   ./packaging/build_appimage.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
APPDIR="$SCRIPT_DIR/GeekType.AppDir"
OUT="$REPO_ROOT/GeekType-x86_64.AppImage"
TOOL="$SCRIPT_DIR/appimagetool.AppImage"

# keep core.py in sync with the top-level copy used by setup.sh/linux_hook.py
cp "$REPO_ROOT/core.py" "$APPDIR/usr/bin/core.py"

if [ ! -f "$TOOL" ]; then
    echo "==> Downloading appimagetool..."
    wget -q "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$TOOL"
    chmod +x "$TOOL"
fi

echo "==> Building $OUT ..."
ARCH=x86_64 "$TOOL" --appimage-extract-and-run "$APPDIR" "$OUT"

echo "==> Done: $OUT"
