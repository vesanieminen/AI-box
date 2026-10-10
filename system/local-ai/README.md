# AI box services

The main boot backend is Qwen3.8 27B INT8 with MTP under vLLM, matching the SSD.
It uses both RTX 3090 GPUs and serves an OpenAI-compatible API on port 8000.
Ollama is installed through Arch's `ollama-cuda` package and retains the SSD's
model directory, preload profile and environment. Ollama is available manually;
it does not preload another model alongside the two-GPU vLLM boot service.

## Restore on a fresh Omarchy installation

1. Install deliberate package additions using `packages/official.txt` and apply
   the user settings with chezmoi. On a different username, change all service
   paths, `User`/`Group` and the Compose UID/GID. These files target user
   `vesanieminen` and two NVIDIA RTX 3090 GPUs.
2. Restore model weights from a separate backup, or follow `models/README.md`.
   Runtime caches can be recreated; they are not required downloads.
3. Create the container using the declarative Compose file:

```bash
mkdir -p ~/.local/share/vllm/cache/{vllm,triton,huggingface}
sudo systemctl enable --now docker.service
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo docker compose -f system/local-ai/compose.yaml create
```

Compose pins the exact SSD image digest for `vllm/vllm-openai:v0.29.0`, all
server flags, environment variables and mounts. `AI_HOME` can override its home
path. `server-config.json` and optional profiles preserve the SSD configuration;
the boot service starts the already-created container rather than rebuilding it.
Do not run `launch.py` when that container already exists. Docker is managed
through privileged commands; no Docker group access is needed.

4. Install the system units and idle helper using standard tools:

```bash
sudo install -Dm755 system/local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo install -m644 system/local-ai/etc/systemd/system/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vllm-boot.service ollama-idle-suspend.service
```

The vLLM unit regenerates NVIDIA CDI device discovery at startup, starts the
container and waits for the expected model to appear in `/v1/models`. Container
restart is disabled because systemd owns its boot/start/stop lifecycle.

```bash
systemctl status vllm-boot.service
curl http://127.0.0.1:8000/v1/models
sudo docker logs --tail 100 qwen38-vllm
```

## Ollama when needed

The Arch package replaces the SSD's standalone Ollama installation. The SSD
binary was version 0.35.0; the configured Arch repository offered 0.33.3 at import.
Arch Ollama 0.33.3 discovers all copied tags and returned a short response from
the custom Qwen3.8 profile with MTP. Full-context operation remains untested.
The package manager provides future updates. Model manifests and blobs stay in
`~/.local/share/ollama/models`, outside Git.

To switch backends manually and avoid concurrent GPU allocations:

```bash
sudo systemctl stop vllm-boot.service
sudo systemctl start ollama.service
ollama list
# Switch back:
sudo systemctl stop ollama.service
sudo systemctl start vllm-boot.service
```

The system Ollama unit preloads `qwen3.8:3090`. The imported user Ollama unit is
an alternative and remains disabled; do not run both on port 11434. Enable
`ollama-resume.service` only if selecting system Ollama as an active backend.
The imported LAN proxy remains disabled: its SSD address and separate gateway
key need provisioning before use. Credentials were not copied.

## Idle, lighting and monitoring

As requested, retain the SSD's automatic suspend behavior: the cloned Omarchy
idle plugin publishes desktop activity, and the guard suspends after 15 minutes
without desktop or AI activity. It checks Ollama and vLLM. Omarchy's existing
150-second screensaver and 300-second lock remain. For machines running without
a desktop session, revisit the desktop heartbeat dependency before relying on
this policy.

LACT is installed normally and `lactd.service` is enabled. GPU limits are left
at the existing defaults; the SSD power-limit scripts were declined. OpenRGB's
user autostart entry turns off the ASUS RTX 3090 lighting.

GPU Observatory is copied to `~/code/gpu-monitor`, outside this repository,
for its future separate repository. It reads LACT telemetry and runs locally at
http://127.0.0.1:8765. Its current user service is transient, not a boot service.
To start it in a later session:

```bash
systemd-run --user --unit=gpu-observatory --property=WorkingDirectory="$HOME/code/gpu-monitor" /usr/bin/python3 "$HOME/code/gpu-monitor/gpu_monitor.py" --interval 2
```

No SSD path is required by the restored services. One-off copying and installation
helpers are excluded from Git. Model data, Docker images, caches, generated CDI
files, credentials and application source code are also outside this repository.
