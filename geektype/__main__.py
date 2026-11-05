"""Command line: ``geektype`` (fix the selection), ``--install``, ``--doctor``."""

from __future__ import annotations

import argparse
import sys

from . import __version__, core, cycle, log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geektype",
        description="Fix text typed in the wrong keyboard layout (Persian/English). By GeekMani.",
    )
    parser.add_argument("--version", action="version", version="GeekType " + __version__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fix", action="store_true", help="fix the selected text (default)")
    group.add_argument("--install", action="store_true", help="install the service and the F9 shortcut")
    group.add_argument("--uninstall", action="store_true", help="remove the service and the shortcut")
    group.add_argument("--doctor", action="store_true", help="check that everything is set up")
    group.add_argument("--convert", metavar="TEXT", help="print TEXT converted, without touching the desktop")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.convert is not None:
        print(core.fix_layout(args.convert))
        return 0
    if args.install:
        from . import install
        return install.install()
    if args.uninstall:
        from . import install
        return install.uninstall()
    if args.doctor:
        from . import doctor
        return doctor.run()
    log.setup()
    outcome = cycle.run()
    return 0 if outcome in (cycle.OK, cycle.NO_SELECTION, cycle.NOTHING, cycle.BUSY) else 1


if __name__ == "__main__":
    sys.exit(main())
