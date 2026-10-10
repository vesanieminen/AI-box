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

## 2026-10-10 — Import selected SSD customizations

Source: the read-only Samsung T7 Omarchy 4.0.4 installation. This box primarily
serves AI models. The selected restoration policy is normal Arch package
installation, configuration templates and recorded model provenance. No one-off
SSD copying/installation scripts are retained. Raw shell/package history was
inspected for clues; sanitized findings are in `ssd-history.md`.

- Screenshot: Super+Shift+S saves a fullscreen screenshot, replacing Google Maps.
- Terminals: Alacritty and Ghostty use CaskaydiaMono Nerd Font at size 11; Foot
  uses JetBrainsMono at size 11; Kitty uses size 11. Current keyboard fixes remain.
- Idle: the cloned vesanieminen.idle plugin publishes desktop activity, and the
  enabled guard suspends after 15 minutes without desktop or AI activity. The
  user explicitly chose to keep this behavior for the AI box. Screen saver and
  lock remain at 150 and 300 seconds.
- Lighting: OpenRGB's imported login entry turns off ASUS RTX 3090 lighting.
- LACT: installed the app and enabled `lactd.service`. Both GPUs retain their
  existing 350 W limits. The SSD power-limit scripts were explicitly declined.
- GPU Observatory: copied the application to `~/code/gpu-monitor`, outside this
  repository for its future separate repository. Its transient user service
  serves http://127.0.0.1:8765 and reads LACT telemetry. Boot startup is not added.
- Assets: all 13 model directories and four Ollama model tags were copied; the
  vLLM cache was copied to save startup work. Weights, caches and runtime binaries
  stay outside Git. `models/` records sources, revisions, file sizes, Ollama
  manifests and download commands. Default Qwen file sizes and every Ollama
  manifest's referenced blob sizes were verified.
- Runtime: the boot backend is intended to be the exact SSD vLLM image and
  Qwen3.8 INT8 model, described by `system/local-ai/compose.yaml` and
  `vllm-boot.service`. Ollama is installed using Arch's `ollama-cuda`, with the
  SSD model directory/environment retained. See `system/local-ai/README.md` for
  normal restoration and manual backend switching.
- Package additions are listed in `packages/official.txt`, including the extra
  SSD applications and dotfile/model CLI tools. Transitive dependencies are not
  duplicated. The SSD's alternate kernel is not an application addition.

Validation so far: Hyprland reload/configerrors clean; idle IPC reports enabled;
fontconfig resolves CaskaydiaMono; lighting command exits successfully; idle guard
and LACT daemon active/enabled; all 12 GPU Observatory tests pass with local
socket access; captured JSON/TOML and Python syntax valid; all 21 captured files
match live settings. Runtime download, startup and final package validation are
still in progress. Live backups are temporarily in /tmp/omarchy-ssd-import-backup.
