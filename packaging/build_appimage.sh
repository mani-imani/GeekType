#!/usr/bin/env bash
# Builds GeekType-x86_64.AppImage.
#
# The AppDir is assembled fresh in a temporary folder from the files in this
# repository, so there is no second copy of the code that can drift.
#
# Usage:  ./packaging/build_appimage.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
OUT="$ROOT/GeekType-x86_64.AppImage"
TOOL="$HERE/appimagetool.AppImage"
APPDIR="$(mktemp -d)/GeekType.AppDir"
trap 'rm -rf "$(dirname "$APPDIR")"' EXIT

mkdir -p "$APPDIR/usr/lib/geektype"
cp -r "$ROOT/geektype" "$APPDIR/usr/lib/geektype/"
find "$APPDIR" -name __pycache__ -type d -prune -exec rm -rf {} +
install -m 0755 "$HERE/AppRun" "$APPDIR/AppRun"
cp "$HERE/geektype.desktop" "$APPDIR/geektype.desktop"
cp "$ROOT/assets/icons/geektype-icon.svg" "$APPDIR/geektype.svg"
cp "$ROOT/assets/icons/geektype-icon-256.png" "$APPDIR/geektype.png" 2>/dev/null \
  || cp "$ROOT/assets/icons/geektype-icon-512.png" "$APPDIR/geektype.png"

chmod -R a+rX "$APPDIR"

if [ ! -f "$TOOL" ]; then
    echo "==> Downloading appimagetool..."
    wget -q "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$TOOL"
    chmod +x "$TOOL"
fi

echo "==> Building $OUT ..."
ARCH=x86_64 "$TOOL" --appimage-extract-and-run "$APPDIR" "$OUT"
echo "==> Done: $OUT"
