# Machine changes

## 2026-10-10 — Establish tracking for future changes

- Created `~/Projects/dotfiles` with an empty chezmoi source tree, an explicit
  capture allowlist, and instructions for recording future changes.
- Added `~/AGENTS.md` so future machine configuration tasks include recording,
  validation, and a local commit.
- The starting point is the default Omarchy installation. No default configs or
  installed-package inventories are retained in this repository.
- Chezmoi is not installed. The session could not resolve its download server;
  capturing changes works now, while chezmoi setup/deployment remains pending.
- No remote, push, application reload, or privileged system change was performed.
- Validation: the capture helper passed checks for capture/update, drift,
  source-edit conflicts, deleted files, excluded credential paths, executable
  permissions, and symlink rejection. The final allowlist contains zero files;
  the chezmoi setup script passed Bash syntax validation.

For future manual changes, record the date, reason, exact actions, affected
files/services, validation, and restoration instructions here when Git diffs
and repeatable scripts do not fully describe the change.
