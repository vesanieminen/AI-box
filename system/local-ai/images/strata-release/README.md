# Strata 0.2.4.2 update

Prepared separate container using Terminal Control 0.1.49.2 and Qwen engine
0.1.48. **Not yet created:** Docker build, container creation and inference
validation require administrator access. The running beta remains unchanged.

The Compose file is `~/.local/share/strata-release/compose.yaml`, project/service
`strata-release`, container `strata-0.2.4.2`, localhost port 5816. It shares the
existing read-only Qwen assets at `~/.local/share/strata` and keeps separate
configuration and runtime files in `~/.local/share/strata-release`. Inference
arguments and expert-profile bytes match beta; the vision executable path, port
and model name identify the new installation. The prepared llama-swap template
adds `qwen3.8-flash-next-iq3-s-0242` to the exclusive GPU group. The suspend-guard
template includes port 5816. Existing boot selection and vLLM profiles are
unchanged; installing these two templates remains pending.

## Verified preparation

Both archives match upstream SHA256SUMS and the signed release feed (sequence
112), verified using the previously installed release's trusted keys. The engine
manifest matches the signed feed; its signature and every listed file hash
passed. Terminal `--version` reports 0.2.4.2; server `--help` imports successfully
on the host. NVIDIA driver 610.57.04 exceeds the engine minimum 580.65.
Compose passes `docker compose config --quiet` without daemon access.
Image build, GPU startup, text, streaming, vision and long-context tests remain
outstanding. Placement estimates for DeepSeek do not constitute a benchmark.

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
active inference. Restarting llama-swap interrupts serving and retains the
installed service's existing boot selection; no boot-unit installation is part
of this task.

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
