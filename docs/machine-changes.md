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
  vLLM cache was copied to save startup work. Weights and caches
  stay outside Git. `models/` records sources, revisions, file sizes, Ollama
  manifests and download commands. Default Qwen file sizes and every Ollama
  manifest's referenced blob sizes were verified.
- Runtime: the boot backend uses the exact SSD vLLM image and
  Qwen3.8 INT8 model, described by `system/local-ai/compose.yaml` and
  `vllm-boot.service`. Ollama is installed using Arch's `ollama-cuda`, with the
  SSD model directory/environment retained. See `system/local-ai/README.md` for
  normal restoration and manual backend switching.
- Package additions are listed in `packages/official.txt`, limited to the AI runtime,
  GPU/lighting/font tools already selected, stress-ng and ethtool. Unrelated SSD
  desktop/development apps were declined. Transitive dependencies are not
  duplicated. The SSD's alternate kernel is not an application addition.

Validation: Hyprland reload/configerrors clean; custom idle IPC responds correctly;
fontconfig resolves CaskaydiaMono; lighting command exits successfully; idle guard
and LACT daemon active/enabled; all 12 GPU Observatory tests pass with local
socket access; captured JSON/TOML and Python syntax valid; all 22 captured files
match live settings. The vLLM image was downloaded, the boot service started and API readiness
was verified. A short chat completion returned `OK`. Live backups are temporarily in /tmp/omarchy-ssd-import-backup.

- Network wake: recovered Ethernet magic-packet wake (64) and Wi-Fi magic-packet
  wake (8) from the SSD’s NetworkManager profiles. Applied both as persistent
  defaults and to existing profiles without copying credentials. Verified Wi-Fi
  magic-packet wake enabled and both wired interfaces reporting `Wake-on: g`.
  Restoration is in `system/network/README.md`. Actual suspend/remote-wake has
  not been exercised during model setup.
- Copied the requested original HTML catalog to `~/Documents/Local-AI/Models.html`
  and captured it. It is an SSD snapshot, not live status for this box.
- Narrowed the package manifest to seven selected additions. Removed only the
  19 unrelated packages just added by the broad batch; pacman’s log confirms
  every removed package was newly installed in that batch. No default or other
  pre-existing Omarchy package was removed.
- Verified Arch Ollama 0.33.3 discovers all four copied tags and the custom
  `qwen3.8:3090` model returns `OK` with MTP enabled. Unloaded its weights and
  stopped the temporary validation server before vLLM startup.

- vLLM: `vllm-boot.service` is active/enabled and serves `qwen3.8-27b-int8`
  on port 8000 using the pinned vLLM 0.29.0 image, TP=2, MTP3 and FP8 E4M3 KV.
  `/v1/models` advertises a 262144-token maximum; a short non-thinking chat
  completion returned `OK`. Full-window context, other model recipes and an
  actual reboot have not been tested. Both GPU limits remain 350 W.
- The copied standalone Ollama binary and temporary PATH shim were removed after
  the Arch package passed model discovery and Qwen response validation. The
  package-managed executable is `/usr/bin/ollama`; system Ollama stays disabled
  alongside the vLLM boot backend.

- Geekbench 7: installed AUR `geekbench` 7.1.0-1 after reviewing the standard
  PKGBUILD, verifying its vendor archive SHA-256 and building with makepkg.
  `geekbench --version` reports 7.1.0; no benchmark was run. Recorded in
  `packages/foreign.txt`, with source/restoration links in `packages/README.md`.

- LAN API access: confirmed vLLM listens on `0.0.0.0:8000` and that UFW had
  no incoming rule for that port. Added the `Local vLLM` application profile
  and persistent TCP 8000 allow rule from `192.168.0.0/24`, preserving all
  existing firewall rules. The host’s LAN-address `/v1/models` request works;
  a request from another LAN device is still needed for end-to-end verification.
  Restoration is in `system/firewall/README.md`.
- Automatic suspend remains configured. At final validation, the existing
  runtime Stay Awake indicator was on; this override prevents suspend until
  toggled off. The indicator is runtime state and is not tracked in Git.

## 2026-10-10: Chezmoi setup and restoration validation

- Installed the normal Arch `chezmoi` package, version 2.72.1-1, and recorded it
  as an intentional addition. Ran the existing generic setup helper to create
  `~/.config/chezmoi/chezmoi.toml`, pointing at `~/Projects/dotfiles`. On a fresh
  checkout, the same helper generates the appropriate local path.
- Excluded generated Python bytecode explicitly in `home/.chezmoiignore`:
  Git ignore rules alone do not prevent Chezmoi from deploying source files.
- Restored into an empty temporary home with isolated persistent state/cache.
  All 22 expected files were present, contents and permissions matched, and
  there were no additional files. Both temporary and live `chezmoi verify`
  passed; live `chezmoi diff` is empty. No settings were applied to the live home.

## 2026-10-10: Permanently disable the screensaver

- Set `idle.screensaver` to zero and taught the user-owned idle plugin to treat
  zero as disabled, using the existing 300-second lock deadline directly.
  AI-aware suspend and the existing Stay Awake override are unchanged.
- Enabled Omarchy's persistent `screensaver-off` preference. Although Omarchy
  stores this under `.local/state/omarchy/toggles`, this specific empty flag is
  a deliberate saved preference and is captured for restoration. Other runtime
  state remains excluded. Normal screensaver launching is blocked; Omarchy's
  explicit `force` launch remains available.
- Restarted the desktop shell to load the plugin and checked idle IPC status.
  The screensaver is disabled and the lock timeout remains 300 seconds.
- Updated capture to encode empty files with Chezmoi's `empty_` attribute;
  otherwise an empty source file represents an absent target. Verified all 23
  files, including the preference flag, restore with matching contents and
  permissions into a fresh temporary home. Live Chezmoi verification passed.
