# Omarchy changes

This machine starts from a default Omarchy installation. This repository records
only deliberate changes made from now on. Untouched default configuration and
the initial installed-package inventory are excluded.

`home/` is a chezmoi source tree; `.chezmoiroot` prevents repository documentation
and scripts from being deployed into HOME.
When we change a configuration file, we retain the whole edited file so it can
be restored onto a fresh Omarchy installation. Git history explains the change;
this is not a complete operating-system backup.

## Record a change

```bash
cd ~/Projects/dotfiles
git status --short
# Inspect and edit the live file, then validate the affected application.
# For a newly changed file, capture it AFTER editing:
./scripts/capture.py --add "$HOME/.config/example/config"
# For files already tracked:
./scripts/capture.py
./scripts/capture.py --check
git diff
# Stage the files involved (including tracked-files.json when updated):
git add home/dot_config/example/config tracked-files.json
git commit -m "Explain the configuration change"
```

`tracked-files.json` is the explicit capture allowlist. `--add` accepts regular
files under HOME and records contents and chezmoi permission attributes. Capture
never changes live settings. It refuses to overwrite pending source edits or
recreate deleted source files without reconciliation. Missing live files also
require an explicit decision rather than automatic removal.

Review files for secrets before adding them. Do not import whole directories
of default settings. Keep temporary backups outside Git. To stop tracking a
file, remove its manifest entry and source file, then review the deletion before
committing.

## Chezmoi setup and restore

Chezmoi is installed and configured on this machine to use this checkout.
All 27 managed files match live settings. Restoration into an empty temporary
directory was verified for all 27 files and their permissions with umask 022.
Generated Python bytecode is excluded by `home/.chezmoiignore`, including files already ignored by Git.

Capturing changes also works without chezmoi. On a fresh machine, install it using
`sudo pacman -S --needed chezmoi`, then configure deployment:

```bash
cd ~/Projects/dotfiles
./scripts/setup-chezmoi.sh
chezmoi diff
# After reviewing the proposed changes:
chezmoi apply
```

The setup script points chezmoi at this repository and previews its diff without
applying settings. It refuses to replace an existing chezmoi configuration.
On another machine, clone/copy this repository first and run the script from
that checkout. Install Omarchy and necessary apps before applying settings.
Review hardware-specific settings and Git identity when they become tracked.

Use chezmoi directly for templates, encryption, and symlinks once installed.
Keep those files outside the simple capture manifest; Git still tracks their
source files. Generated theme output remains outside Git.

## Other machine changes

Record deliberate package additions/removals according to `packages/README.md`.
Store system configuration templates and direct restoration instructions in `system/`. Document
final installations, retained settings and validation in `docs/machine-changes.md`.
Keep documentation focused on the working configuration and restore steps,
without troubleshooting chronology, temporary workarounds or superseded settings.
Disk, firmware, and GUI settings need an explicit record when they do not
correspond to config files.

`~/AGENTS.md` directs future machine configuration work into this repository.
Its text is saved in `docs/home-AGENTS.md`; on a new machine, merge that policy
into `~/AGENTS.md` and adjust the repository path if needed.
Each completed task should include a local commit describing the change and
its validation. Tracking is an explicit workflow, not a background watcher.
The `origin` remote is `https://github.com/vesanieminen/AI-box.git`.
Pushing or publishing requires a user request.
GitHub CLI installation and separate PAT provisioning are documented in
[GitHub access](docs/github.md). Credentials stay outside this repository.

## AI box restoration

The optional [ComfyUI image-generation container](system/comfyui/README.md)
runs Qwen-Image-2.1 on demand, with models and outputs outside this repository.

Start with a fresh Omarchy installation, install `packages/official.txt`, apply
the user configs, then follow [AI service restoration](system/local-ai/README.md).
[Model provenance and download commands](models/README.md) record the copied
weights; weights themselves require a separate backup or download. The selected
boot service is llama-swap, with a retained unit preloading calibrated Strata 0.2.4.2 Qwen3.8 Flash Next IQ3_S on both RTX 3090 GPUs.

One-off SSD copying and installation helpers are not retained. App additions
are package names, overrides are configuration files, and model downloads are
recorded sources and revisions. No restore command depends on the external SSD.

LAN access and persistent wake are recorded in [firewall settings](system/firewall/README.md)
and [network wake settings](system/network/README.md). Geekbench 7 and llama-swap are the explicit
AUR additions; other unrelated SSD apps are excluded.
