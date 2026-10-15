# AI box services

Llama-swap serves the LAN API on port 8000 and manages one model at a time
using the available GPUs. Qwen3.8 Flash Next IQ3_S with GPU vision is preloaded on startup.
Other models are available on demand through vLLM, TabbyAPI, SGLang or Strata, using
pinned runtime images and existing local weights. Model switching stops the old container before loading
another model.

## Restore on a fresh Omarchy installation

1. Install the packages in `packages/official.txt` and the AUR additions in
   `packages/foreign.txt`, then apply user settings with Chezmoi. Llama-swap uses
   the normal AUR `llama-swap-bin` package: `yay -S --needed llama-swap-bin`.
   Service paths and container UID/GID target user `vesanieminen` (1000:1000).
   Adjust them for another machine.
2. Restore model weights from a separate backup or follow `models/README.md`.
   Runtime caches can be recreated.
3. Build Strata and prepare its model using the Strata instructions below, then
   create the containers using the declarative Compose file:

```bash
mkdir -p ~/.local/share/vllm/cache/{vllm,triton,huggingface}
sudo systemctl enable --now docker.service
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo docker compose -f system/local-ai/compose.yaml build qwen3.8-27b-int8-dflash2 qwen3.8-27b-int8-dflash2-w8
sudo docker compose --project-name local-ai -f system/local-ai/compose.yaml create
```

Compose pins the image digest, inference flags, environment and mounts for each
profile. INT8 uses MTP3; INT4 uses MTP2. The two Qwen 27B profiles advertise a 262144-token context,
use tensor parallelism 2 and FP8 E4M3 KV cache. The Qwen INT8 profile
accepts up to 10 images per prompt; video input remains disabled. A ten-image
chat request through llama-swap was verified successfully. vLLM backends listen only on
localhost ports 5800–5807; EXL3 backends use 5810–5813. `AI_HOME` overrides host mount paths if needed.

4. Install the configuration, units and suspend helper:

```bash
sudo install -Dm644 system/local-ai/etc/llama-swap/config.yaml /etc/llama-swap/config.yaml
sudo install -Dm755 system/local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo install -m644 system/local-ai/etc/systemd/system/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl disable --now vllm-boot.service ollama.service ollama-resume.service
sudo systemctl enable --now llama-swap.service ollama-idle-suspend.service lactd.service
```

The root system service needs Docker access to start and stop the containers;
no user Docker group membership is needed. It regenerates NVIDIA CDI discovery
and validates llama-swap configuration before starting. Its `ExecStartPost`
loads Flash Next IQ3_S through llama-swap and waits for the model health endpoint before
the system service reports startup complete. Container restart is
disabled because llama-swap owns the model lifecycle. The former direct vLLM
boot unit is retained as a disabled alternative; do not start it alongside
llama-swap. Their system units conflict to prevent simultaneous startup.

## Choosing a model

API base URL: `http://192.168.0.181:8000/v1`.
Browser UI: `http://192.168.0.181:8000/ui/`.
Strata chat/monitor/settings UI:
`http://192.168.0.181:8000/upstream/qwen3.8-flash-next-iq3-s/`
(keep the trailing slash). Opening it starts Flash Next through llama-swap if
needed. Its backend remains on localhost; the existing LAN port 8000 serves
the UI and its API requests.

Select `qwen3.8-27b-int8` or `qwen3.8-27b-int4` in the client model dropdown,
or send that ID in the request's `model` field. A request starts the selected
model and waits for it to become ready. The UI supports loading, unloading,
chat testing and viewing runtime logs. `/v1/models` lists all configured models;
`/running` reports the currently loaded/loading model.

```bash
systemctl status llama-swap.service
curl http://127.0.0.1:8000/v1/models
curl http://127.0.0.1:8000/running
```

Loading can take several minutes. The readiness timeout is 900 seconds and the
container stop deadline is 60 seconds. Models stay loaded until a switch,
manual unload or service stop; there is no automatic model-unload TTL.
Restarting llama-swap preloads Flash Next IQ3_S again. No weights are redownloaded during
normal switching. Configuration is in `etc/llama-swap/config.yaml`; container
definitions are in `compose.yaml`.

### Available model IDs

All entries belong to one exclusive GPU group. Switching waits for active
inference and stops the previous backend before starting another.

| Model ID | Backend | Context limit |
| --- | --- | --- |
| `qwen3.8-flash-next-iq3-s` | Strata, IQ3_S, MTP4, GPU vision; boot default | 262144 |
| `nemotron-bolt` | llama.cpp CUDA, native IQ2, GPU vision, LiLiCorr DFlash7 | 262144 |
| `qwen3.8-27b-int8` | vLLM, MTP3, TP2 | 262144 |
| `qwen3.8-27b-int4` | vLLM, MTP2, TP2 | 262144 |
| `qwen3.8-27b-int8-dflash2` | vLLM, shared BF16 DFlash2 draft, TP2 | 212992 |
| `qwen3.8-27b-int8-dflash2-w8` | vLLM, W8 DFlash2 draft, TP2 | 262144 |
| `qwen3.6-35b-a3b-int4` | vLLM, TP2 | 131072 |
| `ornith-1.5-35b-int4` | vLLM, TP2 | 262144 |
| `gemma-4-31b-int4` | vLLM, TP2, automatic KV dtype | 73728 |
| `gemma-4-31b-int8` | vLLM, TP2, automatic KV dtype | 8192 |
| `gemma-4-26b-a4b-exl3` | TabbyAPI / ExLlamaV3, automatic GPU split | 65536 |
| `ornith-1.5-35b-exl3` | TabbyAPI / ExLlamaV3, automatic GPU split | 131072 |
| `ornith-1.5-9b-exl3` | TabbyAPI / ExLlamaV3, automatic GPU split | 131072 |
| `qwen3.8-27b-exl3` | SGLang EXL3, original single-GPU recipe | 212992 |

These are configured limits, not verified end-to-end full-context operation
or quality. Model discovery
advertises each limit before loading through llama-swap capabilities, so clients
can account for the different context sizes. Gemma INT8 uses a smaller context
and 0.96 GPU memory utilization to fit its 16-bit KV cache.
The Gemma 26B 8bpw folder has no weights and is excluded. The shared DFlash2
draft is mounted with its target; it is not listed as a standalone chat model.
The DFlash2 profile uses a locally built image from the same pinned vLLM base.
`images/vllm-qwen-embedding/Dockerfile` connects Qwen's embedding constructor to
vLLM's existing packed-embedding loader. Weights stay unchanged. The BF16 draft
profile uses a 212992-token context, a 2048-token prefill batch and 0.96 GPU
memory utilization. No additional large image download is needed for this build.
[Model author's deployment reference](https://huggingface.co/lued/Qwen3.8-27B-INT8-W8A16-DFlash2/blob/2971c64ba386dd3faa6884cc215f67b3b2477a3e/TECHNICAL.md).

The W8 DFlash2 entry shares the same previously checksum-verified target weights
with the BF16 entry. Its separate 2.02 GiB draft is pinned in `models/vllm.json`.
Target TP2 and seven speculative tokens follow the published deployment.
The W8 entry uses the published community setup for the same target and W8
companion: 262144 tokens, TP2, seven speculative tokens, a 2048-token prefill
batch, four sequences, FP8 E4M3 KV, explicit FlashInfer and 0.975 GPU memory
utilization. Prefix caching is disabled. The recipe requests Mamba `align` and
prefix matching unit 16; vLLM selects Mamba cache mode `none` with prefix caching
disabled. The expandable CUDA allocator uses `max_split_size_mb:512`.
There is no explicit KV-memory cap. The local model IDs, read-only mounts and
localhost port 5807 integrate the recipe with llama-swap.

The dedicated image uses the vLLM 0.27.1 base pinned by digest. Its DFlash2
backport and sampler compatibility shim are vendored unchanged from
`noonghunna/club-3090` revision `33e19a3b282d53990f729601ef45cf4457625be1`,
path `models/qwen3.8-27b/vllm/patches/vllm-dflash2-backport`. The image also applies
the author's Mamba safety patch from revision
`e4d525aa6503d1798a047210225862345b9e1a2e` and the packed-embedding constructor
fix. [The published community deployment](https://github.com/noonghunna/club-3090/discussions/1080)
records its long-context verification and the differences from the original
model-card recipe: the runtime, 0.975 memory budget and disabled prefix caching.
The bundled backport supports both W4 and W8 packed draft projection weights.

Select either DFlash2 ID in the llama-swap UI or the client model selector.
Flash Next IQ3_S is the boot default. Qwen INT8 MTP remains available on its existing vLLM 0.29.0 runtime.
The W8 entry returned the expected short response through llama-swap on this
machine with the desktop stopped. Its KV pool contains 268290 tokens. A
near-maximum-context capacity test completed: 262080 input tokens plus eight
generated tokens, with a correct `4` at the start of the answer to `2 + 2`.
The synthetic prompt repeated a sentence; this verifies capacity, not general
long-context quality. Prefill took 284.6 seconds. Long-context quality and
multimodal behavior remain unverified. The BF16 entry's runtime validation is
outstanding.

Two greedy prose runs with 2048 input tokens and 512 output tokens measured
66.34 and 66.10 decode tokens/second, excluding prefill. End-to-end response
times were 9.09 and 8.98 seconds. These measurements establish local behavior
for that workload; they do not establish a speed advantage over the MTP profile.

This profile was validated with SDDM stopped, leaving both GPUs available for
inference. SDDM remains enabled for normal boot. From SSH or a text console,
stop graphics with `sudo systemctl stop sddm` before selecting the W8 entry.
To restore graphics, finish any active request, unload the model using the
llama-swap UI, then run `sudo systemctl start sddm`. Desktop applications close
when SDDM stops; llama-swap and Docker continue as system services.

TabbyAPI configuration is stored in `etc/tabbyapi/` and mounted by Compose.
Its model loads at process startup, so llama-swap owns all backend lifecycles.
The EXL3 containers use the user configured by their image; the vLLM containers
run as host UID/GID 1000:1000. All containers drop Linux capabilities and set
`no-new-privileges`.
The EXL3 images are the immutable image digests recorded in the SSD recipes;
normal `docker compose ... create` downloads missing runtime images. Model
weights are reused from local folders and never downloaded on a model switch.

### Strata Flash Next with vision

`qwen3.8-flash-next-iq3-s` uses the standard ISTA-DASLab IQ3_S quantization,
Strata v0.1.43.1, automatic splitting across GPUs 0 and 1, four speculative
MTP tokens, INT8 KV cache and 262144 configured context tokens. GPU vision
uses the published BF16 projector, a 700 MiB VRAM reserve and 1024 image tokens.
Model discovery advertises text and image input, text output and `vision: true`.
Backend port 5808 is localhost only. The container explicitly passes the host
and port to `serve.server` and uses the installer's retained config in
`etc/strata/strata-iq3_s.json`. It runs directly without invoking setup during
model switches. The system service preloads this profile on startup and waits
for its health endpoint. A fresh boot with this default remains unverified.
The Strata UI is proxied through the LAN URL above. Its page, JavaScript, CSS,
status/settings endpoints and a chat request with the LAN browser Origin were
verified through the machine's LAN address from this host. Remote-browser
access from 192.168.0.75 is also confirmed by successful page/metrics requests.

Restore the pinned source and build the official Dockerfile for the RTX 3090:

```bash
git clone https://github.com/Niko1221/Strata ~/Projects/Strata
git -C ~/Projects/Strata checkout a0116b2782a5b82622358c04a06496485d12b2d6
sudo docker build --build-arg CUDA_ARCHITECTURES=86 -t local-ai/strata:0.1.43.1 ~/Projects/Strata
mkdir -p ~/.local/share/strata
sudo docker run --rm --device nvidia.com/gpu=all \
  -v "$HOME/.local/share/strata:/data" \
  --entrypoint /bin/bash local-ai/strata:0.1.43.1 -lc '
set -e
/opt/strata/.venv/bin/python /opt/strata/setup.py \
  --setup --yes --family qwen --model IQ3_S --gpus 0,1 \
  --context 262144 --vision gpu --data-dir /data \
  --host 127.0.0.1 --port 5808 --no-start
mkdir -p /data/config
cp /opt/strata/strata-iq3_s.json /data/config/
'
sudo install -Dm644 system/local-ai/etc/strata/strata-iq3_s.json \
  "$HOME/.local/share/strata/config/strata-iq3_s.json"
```

The setup downloads missing model assets and generates packs and the MTP draft
subset. Restoring the existing data directory avoids downloading the weights
again. Sources, revisions and published shard hashes are in `models/strata.json`.
No unattended updates are configured: updating requires a deliberate source
update, image rebuild, settings refresh and container recreation.

Verified with the desktop stopped: loading on both RTX 3090 GPUs, text and
image requests through llama-swap, and streaming timing statistics in Activity.
A 111-output-token text test reported 133.8 decode tokens/second and 104.3
prompt tokens/second; short tests do not predict sustained coding performance.
The image test read the letters and digits of `VISION-7426` but replaced the
hyphen with a space. Full-context capacity, long-context quality and operation
with the desktop running remain unverified. Startup loads about 46.84 GiB of
experts into system RAM before filling the GPU expert cache; allow several
minutes when switching to this model.

### OpenCode clients

On an OpenCode 2.x client, merge [the complete example](examples/opencode.llama-swap.json)
into `~/.config/opencode/opencode.json` or `opencode.jsonc`. It declares all 13 IDs
and their configured context limits under the custom provider `llama-swap`.
The saved example's output budgets use the model catalog's separate output field, bounded by the
configured local context. Qwen3.8 profiles use 32768 output tokens; Qwen3.6
uses 65536; Gemma 4 uses 32768, except the locally constrained Gemma INT8
profile is bounded to 8192. Context limits remain the configured backend sizes.
Input and generated output share the total context, so a prompt reduces the
remaining generation budget. Full-length generation is not verified.
These are client budgets, not verified hard generation limits for the self-hosted
backends. Larger budgets can be configured in OpenCode without adding matching
limits to LiteLLM or llama-swap. The suggested 131072-token Qwen budget is an
optional client choice, not a model maximum; it is not applied by this example.

Sources: [Qwen3.8](https://github.com/anomalyco/models.dev/blob/dev/models/alibaba/qwen3.8-27b.toml),
[Qwen3.6](https://github.com/anomalyco/models.dev/blob/dev/models/alibaba/qwen3.6-35b-a3b.toml),
[Gemma 31B](https://github.com/anomalyco/models.dev/blob/dev/models/google/gemma-4-31b-it.toml),
[Gemma 26B](https://github.com/anomalyco/models.dev/blob/dev/models/google/gemma-4-26b-a4b-it.toml).
The OpenCode card rounds Qwen3.8's 32768-token output to 33K; its 262144-token
context is a different limit. Ornith 1.5 35B's catalog has no output limit,
and no Ornith 1.5 9B catalog entry was found. The example leaves their output
field unspecified, using OpenCode's custom-model fallback rather than claiming
a verified maximum. [OpenCode model fallbacks](https://opencode.ai/v2/docs/models).
No API key is required for the direct LAN endpoint.

The default `qwen3.8-27b-int8` entry explicitly enables text/image input, text
output and tools, with `compatibility.reasoningField: "reasoning_content"`.
Ten small images in one chat request were verified through llama-swap. vLLM
enforces the ten-image limit across the entire prompt, including prior messages;
OpenCode needs no separate image-count setting. Other model entries have not
been given image overrides on the basis of this test.

When using the Raspberry Pi's LiteLLM proxy, keep the client's existing provider
ID (for example `litellm`) and set `settings.baseURL` to
`http://192.168.0.218:4000/v1` and `settings.apiKey` to
`"{env:LITELLM_API_KEY}"`. Provision a valid proxy key outside Git. Merge the
model entries into that provider and select `litellm/qwen3.8-27b-int8` if its ID
is `litellm`. The proxy's own timeout settings remain independent of OpenCode's.

Run `/models` in OpenCode and select a `llama-swap/...` entry. The root `model`
setting sets the default for new work; a session selection takes precedence.
For an existing working provider, keep its provider ID, package and request
settings, update `baseURL` to `http://192.168.0.181:8000/v1`, and merge the example's
`models` entries. Use that provider ID instead of `llama-swap` in model references.
The example's 900000 ms header/chunk timeouts accommodate cold startup.

List these models explicitly: OpenCode's built-in vLLM discovery filters for
`owned_by: vllm`, while llama-swap reports `owned_by: llama-swap`. A custom
provider's explicit model list avoids relying on that filter. Carry over existing
working sampling settings and review tool/reasoning settings when merging the
default Qwen entry. Short generation and
streaming checks do not establish end-to-end agent/tool reliability for each model.

If using the Raspberry Pi's LiteLLM gateway, set the client URL to that gateway's
actual OpenAI-compatible endpoint and use its configured model aliases. LiteLLM's
upstream for this box is `http://192.168.0.181:8000/v1`; provisioning the gateway
and testing its wake-on-WLAN hook are separate from this machine's setup.

The first request after a switch waits for model loading. Set any existing
client/proxy request timeout long enough for cold startup. Only one configured
model runs at a time, shared by all LAN clients.
[OpenCode provider documentation](https://opencode.ai/v2/docs/providers).

### Timing metrics

All vLLM profiles enable `--enable-per-request-metrics` and
`--enable-force-include-usage`. Streaming responses therefore include final
usage and timing data even when the client omits `stream_options.include_usage`.
Clients should still set `stream_options.include_usage: true`; the llama-swap
playground already does so. These flags are part of the recorded Compose
configuration and persist when containers are recreated.

Llama-swap calculates approximate prompt throughput from input tokens and time
to first token, and decode throughput from mean inter-token latency. New requests
populate Activity-table speeds; old requests without timings do not gain them
retroactively. Single-token output may have no decode timing.
[vLLM per-request metrics](https://raw.githubusercontent.com/vllm-project/vllm/v0.29.0/docs/features/per_request_metrics.md).

TabbyAPI explicitly allows request streaming. Its routes set
`stream_options.include_usage: true` automatically, including for clients that
omit it, so its native prompt/decode rates reach llama-swap's Activity view.
SGLang starts with `--enable-metrics`, `--enable-request-time-stats-logging`,
`--stream-response-default-include-usage` and `--enable-cache-report`.
Its OpenAI responses report token usage and cached tokens, while the pinned
SGLang image does not put per-request throughput in the fields llama-swap reads.
Its timing logs and Prometheus metrics are available separately; inspect metrics
through `http://192.168.0.181:8000/upstream/qwen3.8-27b-exl3/metrics`.
Do not interpret a blank Activity speed for that backend as missing streaming.
[TabbyAPI usage](https://github.com/theroyallab/tabbyAPI/wiki/03.-Usage).

OpenCode already requests streaming. Keep using the OpenAI-compatible provider
and the same `/v1` base URL. Generic clients should send `stream: true` and
`stream_options: {"include_usage": true}` when streaming; leave `stream: false`
available for ordinary JSON responses. Streaming changes response delivery and
enables live output; it does not itself increase model generation speed.

Apply the subnet-specific UFW rule in [firewall restoration](../firewall/README.md).
The LAN endpoint has no API key, matching the configured local network access.

## Ollama when needed

Arch's `ollama-cuda` provides `/usr/bin/ollama` and uses
`~/.local/share/ollama/models`. It is a manual alternative and is not a
llama-swap model entry. Stop llama-swap before running Ollama:

```bash
sudo systemctl stop llama-swap.service
sudo systemctl start ollama.service
ollama list
# Switch back:
sudo systemctl stop ollama.service
sudo systemctl start llama-swap.service
```

The system Ollama unit preloads `qwen3.8:3090`. The alternative user unit remains
disabled. Enable `ollama-resume.service` only when choosing system Ollama as the
active backend. The optional LAN proxy remains disabled; its address and gateway
key require provisioning separately.

## Idle, lighting and monitoring

The cloned Omarchy idle plugin publishes desktop activity. The guard requires
15 minutes without desktop or AI activity before suspending. It checks Ollama
connections, backend connections, llama-swap loading/unloading state, in-flight
requests and recent completed inference/model-management requests. Keeping the
UI or model list open does not count as inference activity. Failure to verify
activity prevents suspend. The Stay Awake switch overrides the idle policy.

Remote SSH login sessions also block the guard, even when idle. The managed
`~/.local/bin/disconnect-ssh` command prints current incoming SSH connection
processes and SSH login sessions (user, remote host and state), then terminates
those sessions and closes the captured SSH connection processes, including
tunnels. It requests sudo privileges when disconnecting. Run it from a local
terminal: an SSH session used to invoke it is also disconnected, and processes
inside terminated login sessions are stopped. The SSH listener stays running
and new connections remain possible.

```bash
~/.local/bin/disconnect-ssh --list  # Print only; --dry-run is equivalent
~/.local/bin/disconnect-ssh         # Print and disconnect current incoming SSH
```

Restore the command with `chezmoi apply` after configuring this dotfiles
checkout. This command does not request suspend or change the guard: desktop
activity, AI activity and Stay Awake continue to apply. Live listing was
verified against two SSH sessions; syntax and mocked list/disconnect checks
passed. Live session termination and subsequent automatic suspend remain
unverified.

The screensaver is disabled; the lock timeout is 300 seconds. Both settings are
managed by Chezmoi. On a headless machine, review the desktop heartbeat policy.
Persistent network wake is in [network restoration](../network/README.md).

LACT's daemon supplies telemetry and GPU control. Both GPU power limits are
350 W. OpenRGB's desktop autostart entry turns off ASUS RTX 3090 lighting.

GPU Observatory is located at `~/code/gpu-monitor`, outside this repository,
and serves `http://127.0.0.1:8765` when its transient user service is started:

```bash
systemd-run --user --unit=gpu-observatory --property=WorkingDirectory="$HOME/code/gpu-monitor" /usr/bin/python3 "$HOME/code/gpu-monitor/gpu_monitor.py" --interval 2
```

Model weights, runtime logs, caches, generated CDI files, credentials and
application source remain outside this repository. Model provenance and download
commands are in `models/README.md`.

## Validation

Check each model with a short chat request and verify switching stops the
previous container. The suspend guard's regression checks are
`python3 -B -m unittest discover -s tests -v`. A real reboot, full-context model
operation and wake from another LAN device require end-to-end testing.
All 11 selectable models returned a short generated response. INT8 → INT4 →
INT8 switching was verified. Flash Next is currently selected and its health
endpoint reports the model loaded with vision enabled. Streaming with automatic final usage was verified across vLLM,
TabbyAPI and SGLang. vLLM and TabbyAPI rates reach Activity; SGLang's native
Prometheus endpoint returns HTTP 200, including generation-throughput metrics.
Other LAN clients successfully reached the API and web UI, including an OpenCode
streaming request.

## Nemotron 3.5 Bolt

The on-demand `nemotron-bolt` profile uses NVIDIA's native IQ2 GGUF and its
matching vision projector, mounted read-only from
`~/.local/share/llama.cpp/models/nemotron-bolt`. Model revisions, sizes,
SHA-256 checksums and resumable download commands are in
`models/nemotron-bolt.json`. Create the directory before running those commands.
No Hugging Face package or host build tools are required.

`images/llama-bolt/Dockerfile` builds llama-server from llama.cpp revision
`620d2225cc436ab0b001e3200e590e3b286ef9ab` (v0.7.0), which includes Bolt support
from PR #30520. The CUDA 12.8.1 build targets the RTX 3090's architecture 86,
uses two compile jobs, and produces a server image without an embedded web UI.
The llama-swap UI remains available. NVIDIA's matching LiLiCorr GGUF draft
is installed in the same model directory and pinned in the model record.

The backend binds only `127.0.0.1:5809`, uses both GPUs with equal layer splitting,
one sequence, 262144 context, FP16 K/V caches, Flash Attention, temperature 1.0
and top_p 0.95. It follows NVIDIA's published 256K recipe: a 4096-token batch,
2048-token microbatch and `draft-dflash` with up to seven draft tokens. Both
target and draft are GPU offloaded. This fits the two RTX 3090s; the measured
loaded allocation after testing was approximately 18.9 and 19.5 GiB. The model
is in the existing exclusive GPU group and has no container restart policy;
llama-swap owns loading and unloading. Flash Next IQ3_S remains the boot default.
The suspend guard includes port 5809 alongside existing backend ports.

Restore after downloading and verifying the target, projector and draft files:

```bash
sudo docker compose -f system/local-ai/compose.yaml build nemotron-bolt
sudo docker compose -f system/local-ai/compose.yaml create nemotron-bolt
llama-swap -config system/local-ai/etc/llama-swap/config.yaml -validate
sudo install -Dm644 system/local-ai/etc/llama-swap/config.yaml /etc/llama-swap/config.yaml
sudo install -Dm755 system/local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo systemctl restart ollama-idle-suspend.service llama-swap.service
```

Select `nemotron-bolt` in the llama-swap UI or set the API request's `model` to
`nemotron-bolt` at `http://192.168.0.181:8000/v1`.

```bash
curl --fail http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"nemotron-bolt","messages":[{"role":"user","content":"What is 2 + 2?"}],"max_tokens":128,"chat_template_kwargs":{"enable_thinking":false}}'
```

All three GGUF files passed size and SHA-256 verification against their pinned
Hugging Face inventory. Compose and llama-swap configuration validation passed.
The image built successfully. Short text generation, streaming with final
usage counts and synthetic image-color identification passed through llama-swap; the red image was identified as red.
Switching between Flash Next and Bolt passed, and the service restart
successfully preloaded Flash Next. All 12 suspend-guard regression tests passed.
A near-limit synthetic request accepted 262012 input tokens and generated the
correct answer `4` to a final arithmetic question. Prefill took 216.0 seconds
(1212.9 tokens/second). This verifies text capacity, not long-context quality
or maximum-context multimodal capacity. General vision quality and tool use
remain unverified.

Two greedy tutorial-generation runs with 2265 prompt tokens and 512 output
tokens each measured 109.0 and 113.2 decode tokens/second, compared with
90.2 and 90.3 without the draft and with q8_0 KV and 2048/512 prefill batches.
The same prompts, temperature 0, seed 42 and disabled thinking were used;
results describe this workload rather than all tasks. Average end-to-end time
was 6.54 versus 7.04 seconds. The full recipe improved decode about 23%, while
prompt processing was slower: the same near-limit prompt took 128.4 seconds
without the draft, versus 216.0 seconds with the full recipe. Runtime defaults
remain NVIDIA's temperature 1.0 and top_p 0.95.

Close Strata UI tabs before selecting Bolt: model-specific upstream requests
from those tabs can request Flash Next again. Use the llama-swap UI to switch
models.
