# Changelog

## v2.0.0 · Nov 2026
- New look in the GeekMani product family: brand icon and wordmark, and a bilingual product page in `docs/` (light and dark).
- Rewritten as a Python package (`geektype/`) with one command: `geektype`, `--install`, `--uninstall`, `--doctor`, `--convert`.
- Key table checked against Ubuntu's Persian layout (`xkb ir`); half-spaces, symbols and digits convert; an accidental Caps Lock is undone.
- Safer F9 cycle: a lock against double presses, a marker that detects an empty selection (v1 could paste stale text), and the previous clipboard restored after every fix.
- `--doctor` checks packages, service, socket, key sending, clipboard and shortcut one by one.
- The ydotoold socket moved to `/run/geektype/`; `--install` removes the v1 service.
- Release workflow runs the tests and a smoke test before attaching the AppImage.

## v1.0.0
- First release: F9 converts the selected text between Persian and English on Ubuntu GNOME (Wayland). AppImage built by GitHub Actions.
