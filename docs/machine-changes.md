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

Chezmoi manages 26 files. Configure it with `scripts/setup-chezmoi.sh` from this
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
  The guard template ignores ended SSH sessions in `State=closing`, even when
  Orca retains background processes; connected SSH sessions still block suspend.
  The policy is installed, its service is active, and all 22 regression tests pass.
  The runtime Stay Awake switch overrides idle behavior and is not managed by Git.
- `~/.local/bin/disconnect-ssh` prints and closes incoming SSH connections and
  login sessions that can block the suspend guard. Use `--list` to inspect them
  without disconnecting. Chezmoi restores the executable; usage and verification
  are in [idle behavior](../system/local-ai/README.md#idle-lighting-and-monitoring).
- OpenRGB's desktop autostart entry turns off ASUS RTX 3090 lighting.
- `~/Documents/Local-AI/Models.html` retains the supplied model catalog. It is a
  reference snapshot, not live service status; model provenance is in `models/`.

## Shell prompt

`~/.config/starship.toml` prefixes every interactive Bash prompt with the short
hostname, including local and SSH sessions. On this machine the prefix is
`ai-box`. Starship rendering was verified; existing shells pick up the change
at the next prompt. The configuration is managed by Chezmoi.

## AI services and models

Follow [AI service restoration](../system/local-ai/README.md) to create the
containers and install the system units. Docker, `llama-swap.service`,
`ollama-idle-suspend.service` and `lactd.service` are enabled. The direct
`vllm-boot.service` is disabled. The retained llama-swap unit preloads calibrated Strata 0.2.4.2 Flash Next IQ3_S on boot and manages
one model at a time; GPU placement follows the selected backend profile.

- Qwen INT8 alternative: `vllm/vllm-openai:v0.29.0`, pinned by digest in
  `system/local-ai/compose.yaml`, serving `lued/Qwen3.8-27B-INT8-W8A16-MTP`.
  It uses both RTX 3090 GPUs, tensor parallelism 2, MTP3 and FP8 E4M3 KV cache.
  The advertised maximum context is 262144 tokens.
- Llama-swap listens on `0.0.0.0:8000`; API base URL is
  `http://192.168.0.181:8000/v1` and browser UI is
  `http://192.168.0.181:8000/ui/`. INT8 and INT4 vLLM backends listen only on
  localhost ports 5800 and 5801. Other vLLM backends use 5802–5807;
  Strata uses localhost 5808; EXL3 backends use 5810–5813. Selecting `qwen3.8-27b-int4` unloads INT8 and
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
  Strata 0.2.4.2 Flash Next IQ3_S is the retained boot default.
- Strata v0.1.44.1 serves standard Qwen3.8 Flash Next IQ3_S as the on-demand
  `qwen3.8-flash-next-iq3-s` entry, with both RTX 3090 GPUs, MTP4, INT8 KV,
  262144 configured context and GPU vision. Its official Dockerfile is built
  for CUDA architecture 86 from a pinned source revision. The model assets,
  generated packs and MTP subset are in `~/.local/share/strata`, outside Git.
  Text, image input and Activity timing statistics passed through llama-swap
  with the desktop stopped. Full-context capacity and desktop coexistence
  remain unverified. Runtime version and retained settings are verified; text,
  streaming with final usage and synthetic image-color identification passed
  on v0.1.44.1. Sustained performance remains unbenchmarked on this version.
  Resident-expert mode and asynchronous updates remain off. Runtime updates
  are manual. The retained system service waits for
  the Strata 0.2.4.2 Flash Next health endpoint on startup; a fresh boot remains unverified.
  The suspend guard watches port 5808 as well as the DFlash backend on 5807.
  Strata's web UI is served to the LAN through llama-swap at
  `http://192.168.0.181:8000/upstream/qwen3.8-flash-next-iq3-s/`.
  Page/assets, status/settings and browser-Origin chat passed through the LAN
  address from this host. Browser access from 192.168.0.75 is confirmed by
  successful page/metrics requests. No new listener or firewall rule is needed.
- Strata 0.2.0-beta is installed alongside stable with official engine package
  0.1.45.3 and separate Compose configuration in
  `~/.local/share/strata-beta/compose.yaml`. Port 5815 is localhost only; IQ3_S
  assets are reused read-only and beta runtime state is separate. The container
  runs as UID/GID 1000:1000 with dropped capabilities and readable public image
  payload. Package hashes, local Terminal packaging and Compose validation pass.
  Model loading on both RTX 3090s, health/model discovery, text arithmetic,
  streaming with final usage/timings and synthetic image-color identification
  passed. The active beta uses the pinned expert arena, KV fully in VRAM,
  serial decode windows and no parked-conversation cache; its model, context,
  INT8 KV, MTP4 and expert profile match stable. All nine sm_86 optimizations and
  model-card sampling remain active; both GPUs remain at 350 W. Reload and
  text arithmetic passed; live metrics confirm a 47962 MiB expert arena,
  kv_resident=0, conversation_cache_mib=0 and 16187 expert slots.
  The optional `strata-iq3_s-beta-mmap.json` preset retains two pipeline windows,
  32768 resident KV cells, an 8192 MiB conversation-cache budget and mapped
  experts. It passed text/streaming/vision and cache checks. Recorded generation
  was 136.3 tok/s for the default versus 140.8 for the optional preset, while
  prefill was 1311.7 versus 879.7 tok/s across different observed workloads.
  Preset selection, reload commands and the measurement limits are documented
  in `system/local-ai/README.md`.
  Full-context capacity, general vision quality and comparative performance remain
  unverified. Restoration and manual testing with a sleep inhibitor are in
  `system/local-ai/README.md`; provenance is in `models/strata-beta.json`.
  The beta route `qwen3.8-flash-next-iq3-s-beta` is installed in the exclusive
  llama-swap group, with UI path `/upstream/qwen3.8-flash-next-iq3-s-beta/` on
  existing LAN port 8000 on all interfaces. Port 5815 is in the installed suspend
  guard. Both system templates match live files and both services are active.
  Beta loading through the selector, LAN health and remote beta
  HTML access passed. Installed LAN HTML/assets and browser-Origin chat checks passed. Keep only one Strata model UI open so
  model-specific monitoring requests do not switch to an unwanted backend. Beta
  remains available on demand; the retained boot unit selects Strata 0.2.4.2.
- Nemotron 3.5 Bolt is installed as the on-demand `nemotron-bolt` entry on
  localhost port 5809, using a dedicated llama.cpp v0.7.0 CUDA image, native IQ2
  target, vision projector and NVIDIA's LiLiCorr draft. All three files are
  pinned and checksum verified. NVIDIA's 256K recipe uses both RTX 3090 GPUs,
  one sequence, FP16 K/V caches, 4096/2048 prefill batches and DFlash7.
  The installed suspend guard includes its port. Text, streaming with final
  usage counts, synthetic image-color identification and model switching passed.
  A near-limit request accepted 262012 input tokens and correctly answered a
  final arithmetic question. General long-context quality, maximum-context
  multimodal capacity and tool use remain unverified. Two 512-token greedy
  runs measured 109.0 and 113.2 decode tokens/second; the detailed benchmark
  and prefill tradeoff are in the service record. Strata 0.2.4.2 Flash Next IQ3_S is the retained
  boot default; fresh-boot verification remains outstanding.
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

The retained llama-swap template declares 16 chat-model routes through vLLM,
TabbyAPI, SGLang, Strata, llama.cpp and Maya. Runtime images are pinned in
`system/local-ai/compose.yaml`; Maya source is pinned in `models/maya-s24.json`;
the running selector advertises all 16 routes. Model weights remain outside Git.
The shared DFlash2 draft is used with its Qwen INT8 target. The incomplete
Gemma 26B 8bpw folder is excluded because it has no weights. The model table and restoration steps are in
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

- All 27 managed files match live settings and restore into an empty home with
  matching contents and permissions (umask 022); Chezmoi verification passes.
- The vLLM, TabbyAPI and SGLang routes generate short responses through llama-swap.
  Model-specific Strata, Bolt and Maya validation is recorded in the service instructions.
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

## Project Maya

Project Maya is installed from pinned upstream source to serve GLM-5.3-Flash
Maya-S24 with MTP and GPU vision on both RTX 3090 GPUs. Its private Python
environment and generated build stay in `~/Projects/project-maya`; model
weights and packs stay on the internal NVMe under
`~/.local/share/project-maya/models`. No new system packages are required.
The optional llama-swap entry uses localhost port 5814 and the existing
exclusive GPU group; the boot service and Flash Next default are retained.
The installed suspend guard reads Maya's inference activity so idle dashboard
polling does not prevent automatic suspend. The selector exposes Maya at 256K
with text and image input.

[Runtime, settings and restoration](../system/local-ai/README.md#project-maya)
and [pinned model provenance](../models/maya-s24.json) record the retained
installation. All five downloaded files passed size and SHA-256 verification;
upstream setup and calibration completed. Standalone text, streaming and
synthetic image checks passed. The retained context is 262144 tokens with
INT8 KV streaming and 8 GiB requested RAM headroom. Synthetic text-capacity
tests passed at 128K and 256K; the INT8-KV test accepted 261651 input tokens
and produced the expected short answer at 256K.
Text, image and streaming requests through llama-swap and live suspend-guard
activity detection passed. Maya → Nemotron Bolt → Maya switching passed; Maya
was left loaded at 256K. The boot default remains Flash Next.

## Strata 0.2.4.2 separate installation

Strata Terminal 0.2.4.2 and Qwen engine 0.1.48 are installed as the separate
`strata-0.2.4.2` container on localhost port 5816, sharing Qwen model files and
keeping its own settings and runtime directory. Its installed selector route is
`qwen3.8-flash-next-iq3-s-0242` in the exclusive GPU group. The installed suspend
guard includes port 5816; both installed files match the retained templates.
Health, arithmetic (323), streaming (STREAM_OK) and synthetic red-image vision
passed, including after calibration. Calibration took 488 seconds and selected
PCIe share 0.35 and draft confidence 0.70; paired short-prompt generation medians
rose from 141.7 to 146.1 tok/s (+3.1%). Workers (7), prompt chunks and adaptation
retain defaults. The explicit conversation-cache setting of zero preserves the
beta's disabled behavior despite the newer engine's automatic default. Context,
quant, KV and 350 W GPU power limits are retained. LAN HTML and all four CSS/JS
assets passed. The previous baseline is committed as `4ba9578`; the full report
and a live-file backup remain outside Git under the release calibration directory.
Older containers remain available. The installed, enabled boot unit selects the
new route; systemd was reloaded and the Qwen preload passed after a service
restart. Full-context, sustained-workload and fresh-boot checks remain
outstanding. Restore commands and verified provenance are in
[the release instructions](../system/local-ai/images/strata-release/README.md).

## DeepSeek V4.1 Flash IQ2_XS

The IST-DAS 2.25 bpw model and shared files (273.8 GB) are downloaded under
`~/.local/share/strata-deepseek/models`. The downloader verified pinned sizes and
SHA-256; all seven completion markers record the expected hashes. Strata Control
0.1.49.2 (Terminal 0.2.4.2) and the signed DeepSeek CUDA 13 engine 0.1.49.2 are
installed independently of the Qwen containers under the same DeepSeek base
directory. No host packages or Python dependencies were installed. The 8.6 MiB
model pack references the weights rather than copying them; pack-info confirms
all files and kernels are present.

The retained profile uses 262144 context, both RTX 3090s in a layer split,
`--tp 1`, 8 automatic CPU threads and a saved 112 GB (decimal) expert RAM-store
ceiling. This applies on the next full backend start; the current engine was
left running with 104 GB. Memory headroom, performance and full-context stability
at 112 GB remain unverified. The automatic store is capped at 48 GB. DSpark remains automatic and the
engine chooses not to load it on this rig. Local Paris, arithmetic (323), streamed
code and parsed echo tool-call checks passed. The validated 104 GB profile's 160-token
coding stream measured 14.3 decode tok/s; total RAM used was about 103 GiB with
22 GiB available, and each GPU used about 23 GiB. These are short checks, not a
full-context or sustained performance benchmark.

The `deepseek-v4.1-flash-iq2-xs` selector entry uses localhost port 5818 and joins
the exclusive GPU group; the installed suspend guard includes that port. Both
installed files and the installed boot unit match their retained templates.
Qwen-to-DeepSeek switching, loaded health and LAN monitor HTML plus all four
CSS/JS assets passed, as did arithmetic (323) through the LAN API.
Calibrated Qwen remains the installed boot default; the
service is enabled and its preload passed after restart, with fresh boot still
unverified. DeepSeek was left loaded through llama-swap. Do not start a standalone
test server beside a managed GPU backend. Weights, generated packs, logs and
test backups remain outside Git.
[Sources and restore instructions](../models/deepseek-v4.1-flash-iq2-xs.md) and
[the pinned manifest](../models/deepseek-v4.1-flash-iq2-xs.json) record the runtime.
