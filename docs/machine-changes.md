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
| github-cli | GitHub CLI and HTTPS Git authentication |
| ethtool | Inspect and configure Ethernet wake support |
| lact | GPU control application and `lactd.service` telemetry daemon |
| nvidia-container-toolkit | Expose NVIDIA GPUs to the vLLM container through CDI |
| ollama-cuda | Package-managed Ollama with NVIDIA acceleration |
| openrgb | Turn off ASUS RTX 3090 lighting at desktop login |
| stress-ng | Manual system stress testing |
| ttf-cascadia-mono-nerd | Configured terminal font |

Install AUR additions with `yay -S --needed geekbench llama-swap-bin`.
Geekbench 7 provides manual benchmarking; llama-swap provides LAN model switching. Package sources and
restoration commands are in [packages](../packages/README.md); installed versions
are recorded in [versions.txt](../packages/versions.txt).

## User configuration

Chezmoi manages 24 files. Configure it with `scripts/setup-chezmoi.sh` from this
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
containers and install the system units. Docker, `llama-swap.service`,
`ollama-idle-suspend.service` and `lactd.service` are enabled. The direct
`vllm-boot.service` is disabled. Llama-swap preloads INT8 on boot and manages
one model at a time; GPU placement follows the selected backend profile.

- Default backend: `vllm/vllm-openai:v0.29.0`, pinned by digest in
  `system/local-ai/compose.yaml`, serving `lued/Qwen3.8-27B-INT8-W8A16-MTP`.
  It uses both RTX 3090 GPUs, tensor parallelism 2, MTP3 and FP8 E4M3 KV cache.
  The advertised maximum context is 262144 tokens.
- Llama-swap listens on `0.0.0.0:8000`; API base URL is
  `http://192.168.0.181:8000/v1` and browser UI is
  `http://192.168.0.181:8000/ui/`. INT8 and INT4 vLLM backends listen only on
  localhost ports 5800 and 5801. Other vLLM backends use 5802–5807;
  EXL3 backends use 5810–5813. Selecting `qwen3.8-27b-int4` unloads INT8 and
  loads the INT4 MTP2 profile; selecting `qwen3.8-27b-int8` switches back.
  Active inference finishes before a queued switch. Existing OpenCode clients
  keep the same endpoint and select models through `/models`. The persistent UFW rule permits TCP 8000
  from `192.168.0.0/24`. Restore it using [firewall instructions](../system/firewall/README.md).
- Two DFlash2 entries share the previously checksum-verified Qwen3.8 INT8
  target weights: `qwen3.8-27b-int8-dflash2` uses the BF16 draft with 212992-token
  context; `qwen3.8-27b-int8-dflash2-w8` uses the separately downloaded W8 draft
  with 262144-token context. Both target and draft use TP2. The W8 profile has
  a dedicated vLLM 0.27.1 image with the published DFlash2 backport, its sampler
  compatibility shim, the packed-embedding constructor fix and the author's
  Mamba safety patch. Its weight checksum is verified. Runtime caches are separate.
  The W8 entry uses the published community profile (0.975 memory utilization,
  prefix caching disabled) and passed short-response serving with the desktop
  stopped. A synthetic 262080-input-token request generated eight output tokens
  without error; general long-context quality and multimodal behavior remain
  unverified.
  Qwen INT8 MTP remains the boot default.
- Ollama uses `/usr/bin/ollama` and `~/.local/share/ollama/models`. It is a manual
  alternative to llama-swap; its services remain disabled while llama-swap
  manages the GPUs.
  The system unit preloads `qwen3.8:3090` when started.
- The model directories and four Ollama tags are available locally.
  Weights remain outside Git. [Model records](../models/README.md) contain sources,
  pinned revisions and download commands; restoration requires a separate model
  backup or downloading those assets.
- LACT's daemon supplies GPU control and telemetry. Both GPU power limits are 350 W.
- GPU Observatory is located at `~/code/gpu-monitor`, outside this repository.
  It reads LACT telemetry and serves `http://127.0.0.1:8765` when started using
  the command in the AI service instructions. It is not enabled at boot.

### Model switching and timing metadata

Llama-swap configuration declares 12 complete chat-model routes through vLLM,
TabbyAPI and SGLang. Runtime images are pinned in `system/local-ai/compose.yaml`;
weights remain outside Git. The shared DFlash2 draft is used with its Qwen
INT8 target. The incomplete Gemma 26B 8bpw folder is excluded because it has
no weights. The model table and restoration steps are in
[AI services](../system/local-ai/README.md).

All vLLM profiles include per-request timing metrics. The W8 DFlash2 profile's
clients should request `stream_options.include_usage` for final streaming token
counts; the other profiles force that field through llama-swap. Llama-swap
Activity displays prompt/decode throughput for new responses.
Streaming vLLM and TabbyAPI responses report rates in Activity. SGLang reports
streaming token usage, with throughput available through its separate native
Prometheus endpoint. Its response format does not expose Activity-compatible
per-request rates. A remote OpenCode response also reported both vLLM rates.
Chezmoi restoration was verified for all 24 files and their permissions.
The idle guard's 12 regression checks pass.

## Network wake

[Network restoration](../system/network/README.md) installs NetworkManager's
persistent magic-packet defaults: Ethernet wake-on-LAN 64 and Wi-Fi wake-on-WLAN 8.
Existing connection profiles also select magic-packet wake. Network credentials
are provisioned separately.

## GitHub access

`github-cli` provides `/usr/bin/gh`; the managed user launcher uses that binary.
The PAT is provisioned separately at `~/.config/gh/pat` (directory 700, file 600).
The authentication directory is excluded from capture, Chezmoi and Git.
[GitHub access](github.md) documents authentication and push commands.

## Verified behavior

- All 24 managed files match live settings and restore into an empty home with
  matching contents and permissions; Chezmoi verification passes.
- All 11 selectable models generate a short response through llama-swap.
  Both Qwen MTP profiles return `OK`; INT8 → INT4 → INT8
  switching is verified. Each uses both GPUs and one model runs at a time.
  The browser UI returns HTTP 200. API and UI requests from other LAN devices
  succeed; OpenCode streaming inference is also verified.
- Ollama discovers all four tags and the custom Qwen3.8 profile returns a short
  response with MTP enabled.
- The idle plugin reports the screensaver disabled and a 300-second lock timeout.
  The AI-aware suspend guard and LACT daemon are active.
- Wi-Fi magic-packet wake is enabled; both Ethernet interfaces report `Wake-on: g`.

An actual reboot, suspend with remote wake and full-context model operation
still require end-to-end verification.
