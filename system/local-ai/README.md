# AI box services

Llama-swap serves the LAN API on port 8000 and manages one model at a time
using the available GPUs. Qwen3.8 27B INT8 MTP is preloaded on startup.
Other models are available on demand through vLLM, TabbyAPI or SGLang, using
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
3. Create the containers using the declarative Compose file:

```bash
mkdir -p ~/.local/share/vllm/cache/{vllm,triton,huggingface}
sudo systemctl enable --now docker.service
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo docker compose -f system/local-ai/compose.yaml build qwen3.8-27b-int8-dflash2
sudo docker compose -f system/local-ai/compose.yaml create
```

Compose pins the image digest, inference flags, environment and mounts for each
profile. INT8 uses MTP3; INT4 uses MTP2. The two default Qwen profiles advertise a 262144-token context,
use tensor parallelism 2 and FP8 E4M3 KV cache. vLLM backends listen only on
localhost ports 5800–5806; EXL3 backends use 5810–5813. `AI_HOME` overrides host mount paths if needed.

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
loads Qwen INT8 through llama-swap and waits for the model health endpoint before
the system service reports startup complete. Container restart is
disabled because llama-swap owns the model lifecycle. The former direct vLLM
boot unit is retained as a disabled alternative; do not start it alongside
llama-swap. Their system units conflict to prevent simultaneous startup.

## Choosing a model

API base URL: `http://192.168.0.181:8000/v1`.
Browser UI: `http://192.168.0.181:8000/ui/`.

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
Restarting llama-swap preloads INT8 again. No weights are redownloaded during
normal switching. Configuration is in `etc/llama-swap/config.yaml`; container
definitions are in `compose.yaml`.

### Available model IDs

All entries belong to one exclusive GPU group. Switching waits for active
inference and stops the previous backend before starting another.

| Model ID | Backend | Context limit |
| --- | --- | --- |
| `qwen3.8-27b-int8` | vLLM, MTP3, TP2; boot default | 262144 |
| `qwen3.8-27b-int4` | vLLM, MTP2, TP2 | 262144 |
| `qwen3.8-27b-int8-dflash2` | vLLM, shared BF16 DFlash2 draft, TP2 | 212992 |
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

TabbyAPI configuration is stored in `etc/tabbyapi/` and mounted by Compose.
Its model loads at process startup, so llama-swap owns all backend lifecycles.
The EXL3 containers use the user configured by their image; the vLLM containers
run as host UID/GID 1000:1000. All containers drop Linux capabilities and set
`no-new-privileges`.
The EXL3 images are the immutable image digests recorded in the SSD recipes;
normal `docker compose ... create` downloads missing runtime images. Model
weights are reused from local folders and never downloaded on a model switch.

### OpenCode clients

On an OpenCode 2.x client, merge [the complete example](examples/opencode.llama-swap.json)
into `~/.config/opencode/opencode.json` or `opencode.jsonc`. It declares all 11 IDs
and their configured context limits under the custom provider `llama-swap`.
The example chooses output budgets of 8192 tokens, or 2048 for Gemma INT8's
8192-token context; these are client budgets, not tested maximum output lengths.
No API key is required for the direct LAN endpoint.

Run `/models` in OpenCode and select a `llama-swap/...` entry. The root `model`
setting sets the default for new work; a session selection takes precedence.
For an existing working provider, keep its provider ID, package and request
settings, update `baseURL` to `http://192.168.0.181:8000/v1`, and merge the example's
`models` entries. Use that provider ID instead of `llama-swap` in model references.
The example's 900000 ms header/chunk timeouts accommodate cold startup.

List these models explicitly: OpenCode's built-in vLLM discovery filters for
`owned_by: vllm`, while llama-swap reports `owned_by: llama-swap`. A custom
provider's explicit model list avoids relying on that filter. The example does
not change a client's existing tool or reasoning overrides; carry over the
settings that already work with the relevant backend. Short generation and
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
INT8 switching was verified, and the default INT8 profile is selected after
validation. Streaming with automatic final usage was verified across vLLM,
TabbyAPI and SGLang. vLLM and TabbyAPI rates reach Activity; SGLang's native
Prometheus endpoint returns HTTP 200, including generation-throughput metrics.
Other LAN clients successfully reached the API and web UI, including an OpenCode
streaming request.
