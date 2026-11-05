#!/usr/bin/env bash
# GeekType setup from a source checkout. Same as: python3 bin/geektype --install
set -euo pipefail
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bin/geektype" --install "$@"
