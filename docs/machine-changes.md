# Installed configuration

This is the reproducible configuration on top of a default Omarchy installation,
verified on 2026-10-10. Record final installations, retained settings, restoration
instructions and validation here.

## Programs

Install the additions in [official packages](../packages/official.txt) with
`sudo pacman -S --needed $(cat packages/official.txt)`. Pacman resolves dependencies.

| Package | Purpose |
| --- | --- |
| chezmoi | Restore managed user configuration from this repository |
| ethtool | Inspect and configure Ethernet wake support |
| lact | GPU control application and `lactd.service` telemetry daemon |
| nvidia-container-toolkit | Expose NVIDIA GPUs to the vLLM container through CDI |
| ollama-cuda | Package-managed Ollama with NVIDIA acceleration |
| openrgb | Turn off ASUS RTX 3090 lighting at desktop login |
| stress-ng | Manual system stress testing |
| ttf-cascadia-mono-nerd | Configured terminal font |

Install Geekbench 7 using `yay -S --needed geekbench`. Package sources and
restoration commands are in [packages](../packages/README.md); installed versions
are recorded in [versions.txt](../packages/versions.txt).

## User configuration

Chezmoi manages 23 files. Configure it with `scripts/setup-chezmoi.sh` from this
checkout, review `chezmoi diff`, then run `chezmoi apply` to restore settings.
The capture allowlist is `tracked-files.json`. Python bytecode is excluded;
empty preference files use Chezmoi's `empty_` attribute.

- Super+Shift+S saves a fullscreen screenshot.
- Ghostty and Alacritty use CaskaydiaMono Nerd Font at size 11; Foot uses
  JetBrainsMono at size 11; Kitty uses size 11.
- The screensaver is disabled: `idle.screensaver` is zero, the custom idle
  plugin supports zero as disabled, and the persistent `screensaver-off`
  preference blocks normal screensaver launching. The lock timeout is 300 seconds.
- The custom idle plugin publishes desktop activity to the AI-aware suspend guard.
  Automatic suspend occurs after 15 minutes without desktop or AI activity.
  The runtime Stay Awake switch overrides idle behavior and is not managed by Git.
- OpenRGB's desktop autostart entry turns off ASUS RTX 3090 lighting.
- `~/Documents/Local-AI/Models.html` retains the supplied model catalog. It is a
  reference snapshot, not live service status; model provenance is in `models/`.

## AI services and models

Follow [AI service restoration](../system/local-ai/README.md) to create the
container and install the system units. Docker, `vllm-boot.service`,
`ollama-idle-suspend.service` and `lactd.service` are enabled.

- Default backend: `vllm/vllm-openai:v0.29.0`, pinned by digest in
  `system/local-ai/compose.yaml`, serving `lued/Qwen3.8-27B-INT8-W8A16-MTP`.
  It uses both RTX 3090 GPUs, tensor parallelism 2, MTP3 and FP8 E4M3 KV cache.
  The advertised maximum context is 262144 tokens.
- vLLM listens on `0.0.0.0:8000`; API base URL is
  `http://192.168.0.181:8000/v1`. The persistent UFW rule permits TCP 8000
  from `192.168.0.0/24`. Restore it using [firewall instructions](../system/firewall/README.md).
- Ollama uses `/usr/bin/ollama` and `~/.local/share/ollama/models`. It is a manual
  alternative to vLLM; its services remain disabled while vLLM is the boot backend.
  The system unit preloads `qwen3.8:3090` when started.
- Thirteen vLLM model directories and four Ollama tags are available locally.
  Weights remain outside Git. [Model records](../models/README.md) contain sources,
  pinned revisions and download commands; restoration requires a separate model
  backup or downloading those assets.
- LACT's daemon supplies GPU control and telemetry. Both GPU power limits are 350 W.
- GPU Observatory is located at `~/code/gpu-monitor`, outside this repository.
  It reads LACT telemetry and serves `http://127.0.0.1:8765` when started using
  the command in the AI service instructions. It is not enabled at boot.

## Network wake

[Network restoration](../system/network/README.md) installs NetworkManager's
persistent magic-packet defaults: Ethernet wake-on-LAN 64 and Wi-Fi wake-on-WLAN 8.
Existing connection profiles also select magic-packet wake. Network credentials
are provisioned separately.

## Verified behavior

- All 23 managed files match live settings and restore into an empty home with
  matching contents and permissions; Chezmoi verification passes.
- vLLM starts, lists the expected model and returns a short chat completion.
  Both GPUs participate. The host's LAN-address API request succeeds.
- Ollama discovers all four tags and the custom Qwen3.8 profile returns a short
  response with MTP enabled.
- The idle plugin reports the screensaver disabled and a 300-second lock timeout.
  The AI-aware suspend guard and LACT daemon are active.
- Wi-Fi magic-packet wake is enabled; both Ethernet interfaces report `Wake-on: g`.

An actual reboot, suspend with remote wake, requests from another LAN device,
and full-context model operation still require end-to-end verification.
