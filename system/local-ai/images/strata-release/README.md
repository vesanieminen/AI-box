# Strata 0.2.4.2 update

Installed separate container using Terminal Control 0.1.49.2 and Qwen engine
0.1.48. It loaded through llama-swap and passed text arithmetic, streaming and
synthetic red-image vision checks. The older beta remains available on its route.

The Compose file is `~/.local/share/strata-release/compose.yaml`, project/service
`strata-release`, container `strata-0.2.4.2`, localhost port 5816. It shares the
existing read-only Qwen assets at `~/.local/share/strata` and keeps separate
configuration and runtime files in `~/.local/share/strata-release`. The active
profile retains IQ3_S, MTP4, INT8 GPU-resident KV, 262144 context and GPU vision.
Calibration sets PCIe share 0.35 and draft confidence 0.70. The explicit
`--conversation-cache-mib 0` preserves the beta's disabled cache behavior;
engine 0.1.48 otherwise automatically enables an 8 GiB parked-conversation cache.
The expert-profile bytes match beta. The installed llama-swap route belongs to
the exclusive GPU group, and the installed suspend guard includes port 5816.
Both installed files match their retained templates. The vLLM profiles remain
unchanged. The installed boot unit selects this new route and systemd has been
reloaded. The service is enabled and its startup preload passed after restart;
a fresh boot remains unverified.

## Verified preparation

Both archives match upstream SHA256SUMS and the signed release feed (sequence
112), verified using the previously installed release's trusted keys. The engine
manifest matches the signed feed; its signature and every listed file hash
passed. Terminal `--version` reports 0.2.4.2; server `--help` imports successfully
on the host. NVIDIA driver 610.57.04 exceeds the engine minimum 580.65.
Compose passes `docker compose config --quiet` without daemon access.
The image built and the new container loaded across both RTX 3090 GPUs. Health
reports 262144 context and vision. Arithmetic returned 323, streaming returned
STREAM_OK and a synthetic red image returned red. Full-context tests and
long-workload performance remain outstanding. Placement estimates for DeepSeek
do not constitute a benchmark.

## Calibration and active validation

Calibration on 2026-10-24 took 488 seconds on the Ryzen 7 5800X, 128 GB RAM and
two RTX 3090s at 350 W each. It used the verified release binaries and the same
Qwen weights with host paths substituted into a private baseline config. The
same GPU vision encoder remained resident across engine restarts, preserving
its VRAM use. The DeepSeek download continued in the background.

The stock `tools/calibrate.py` sweep tested prompt chunks, PCIe share, draft
confidence, CPU workers and adaptive expert-cache settings. Three paired
confirmation rounds gave these generation-rate medians on its short prompts:

| Setting | Baseline | Selected |
| --- | ---: | ---: |
| PCIe share | 0.37 (automatic probe) | 0.35 |
| Draft confidence | 0.50 | 0.70 |
| Median generation | 141.7 tok/s | 146.1 tok/s |

The 3.1% improvement narrowly exceeded the stock 3% threshold. CPU worker count
remains automatic (7), prompt chunks remain automatic/default, and adaptation
remains at engine defaults. Context, quant, KV format and power were not tuned.
The measurements are a small workload-specific gain, not evidence of a general
speedup from the RAM upgrade. Full report and logs remain outside Git under
`~/.local/share/strata-release/calibration/`; the report is
`calibration-2026-10-24.json`. The tool's report-integrity/freshness review passed
before translating the selected flags into the container profile.

After reload, live metrics confirm engine 0.1.48, `pcie_frac=0.35`,
`spec_min_p=0.70`, 7 workers, `prefill_pipe=0`, `kv_resident=0` and
`conversation_cache_mib=0`. Arithmetic (323), streaming (STREAM_OK) and synthetic
red-image vision passed again. LAN monitor HTML and all four CSS/JS assets
returned HTTP 200. Llama-swap listens on all interfaces at port 8000.

The committed working baseline is `4ba9578`; a live-file backup is also retained
at `~/.local/share/strata-release/calibration/container-baseline-2026-10-24.json`.
To restore the baseline, finish active requests, close monitors, then:

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/models/unload/qwen3.8-flash-next-iq3-s-0242
git -C ~/Projects/dotfiles show 4ba9578:home/dot_local/share/strata-release/config/private_strata-iq3_s-beta.json \
  > ~/.local/share/strata-release/config/strata-iq3_s-beta.json
curl --max-time 900 -fsS http://127.0.0.1:8000/upstream/qwen3.8-flash-next-iq3-s-0242/health
```

Capture and commit the deliberately restored configuration afterward.

## PLE table in RAM

The active release profile adds `--ple-io ram`. It loads the IQ4_NL
`per_layer_token_embd.weight` table (28,800,138,240 bytes, 26.82 GiB) into
system RAM and locks its pages instead of reading table rows directly from SSD.
The retained config restores this setting; conversation caching remains disabled.

On 2026-10-25 the engine confirmed `PLE table locked in RAM` in 11.1 seconds.
Health retained 262144 context and vision; arithmetic (323), streaming
(STREAM_OK) and the LAN monitor metrics passed. After loading, about 39 GiB of
system RAM remained available; engine VmSwap was zero and VmLck was 26.82 GiB.
One identical 73-token coding prompt with 256 output tokens measured 117.1 tok/s
before reload and 121.3 tok/s afterward; this single pair does not establish a
repeatable speedup. The RAM-mode request incurred only 4096 bytes of physical
engine reads. Full-context memory headroom and sustained performance with this
setting remain unverified. Runtime test results and the pre-change config remain
outside Git in `~/.cache/strata-ple-ram-test/`.

## Boot default

The retained unit preloads `qwen3.8-flash-next-iq3-s-0242` and requires its
configuration/runtime mount. Install it without interrupting the running model:

```bash
sudo install -Dm644 ~/Projects/dotfiles/system/local-ai/etc/systemd/system/llama-swap.service \
  /etc/systemd/system/llama-swap.service
sudo systemctl daemon-reload
```

Llama-swap is already enabled. The new preload takes effect at the next service
start or boot. Unit syntax validation passed; installation and a fresh boot are
not yet verified. Old stable and beta containers remain available on demand.

## Restore the build context

Restore configuration with Chezmoi and first build the existing base image using
the beta installation instructions in `../../README.md`. Download the following
files from `https://github.com/Niko1221/Strata/releases/download/v0.2.4/` into
`~/.cache/strata-0.2.4-downloads/`:

| Archive | SHA-256 |
| --- | --- |
| `strata-control-0.1.49.2-linux-x86_64.tar.gz` | `2f905fe9e7f0c0f7e1d055a414acc0b3dae6db2d42e7f6a97e57e8ff7d3cf9c6` |
| `strata-engine-0.1.48-linux-x86_64-cuda-cuda13.tar.gz` | `3e11a82e325cf4968a1734446e8945d7918a5657e964c6c5d2c262aa59258f57` |

Verify these hashes before unpacking. Control source commit is
`dfa3f4025c9f1bc4af8cee201b20a2d223061813`; Qwen engine build is
`6f8800aefe27+cuda13.0`.

```bash
mkdir -p ~/.cache/strata-0.2.4-build/terminal \
  ~/.cache/strata-0.2.4-build/engine/0.1.48-linux-x86_64-cuda-cuda13
tar -xzf ~/.cache/strata-0.2.4-downloads/strata-control-0.1.49.2-linux-x86_64.tar.gz \
  -C ~/.cache/strata-0.2.4-build/terminal
tar -xzf ~/.cache/strata-0.2.4-downloads/strata-engine-0.1.48-linux-x86_64-cuda-cuda13.tar.gz \
  -C ~/.cache/strata-0.2.4-build/engine/0.1.48-linux-x86_64-cuda-cuda13
cp ~/Projects/dotfiles/system/local-ai/images/strata-release/Dockerfile \
  ~/.cache/strata-0.2.4-build/Dockerfile
sudo docker compose -f ~/.local/share/strata-release/compose.yaml build
```

## Create and integrate

After building, create a stopped container. This leaves the beta intact and
allocates no GPU memory:

```bash
sudo docker compose -f ~/.local/share/strata-release/compose.yaml create
```

Install the retained llama-swap configuration and suspend guard after finishing
active inference. Restarting llama-swap interrupts serving. Install the boot unit above to
select the new release at startup.

```bash
cd ~/Projects/dotfiles
sudo install -Dm644 system/local-ai/etc/llama-swap/config.yaml /etc/llama-swap/config.yaml
sudo install -Dm755 system/local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo systemctl restart llama-swap.service ollama-idle-suspend.service
curl --max-time 900 -fsS http://127.0.0.1:8000/upstream/qwen3.8-flash-next-iq3-s-0242/health
```

Validate model discovery, text, streaming and vision before considering the
installation complete. To return to beta, select its existing route
`qwen3.8-flash-next-iq3-s-beta`. Both remain managed by the exclusive GPU group;
do not manually start either GPU container beside a running backend.

To measure Docker usage (shared image layers are not duplicated per container):

```bash
sudo docker system df -v
sudo docker inspect --size strata-0.2.0-beta
```

Host beta files currently occupy 944 MiB, mostly its 943 MiB extracted engine
package. Shared Qwen assets occupy 87 GiB. Those numbers exclude Docker image
layers and build caches, which could not be inspected without authentication.
