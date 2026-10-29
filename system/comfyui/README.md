# Local Qwen image generation

ComfyUI 0.43.0 runs on demand in Docker with PyTorch 2.13.0 / CUDA 13.0.
The Dockerfile pins the base image digest and verifies the ComfyUI source
archive. No ComfyUI host package or Python environment is required.
Dependencies use a virtual environment inside the image, sharing the base
image's PyTorch installation. CUDA and Triton caches stay in the data directory.

All persistent application data lives in `~/.local/share/comfyui`: models,
input, output, user workflows, temporary images and caches. Docker retains
the image and bounded container logs in its normal storage. Model weights,
runtime data and generated images stay outside Git.

Open <http://192.168.0.181:8000/comfyui/> from the home LAN. This native
llama-swap route starts the container and unloads the active chat backend.
The interface also listens on `0.0.0.0:8188` while the container is running;
use the port 8000 route for automatic startup and GPU switching. Direct port
8188 does not start the container. Docker's published port is reachable on
all host IPv4 interfaces; it is not restricted by the existing UFW port 8000 rule.

The container configuration exposes both RTX 3090 GPUs as UID/GID 1000, with
automatic memory offloading and a 1 GB VRAM reserve. The ordinary workflow uses
GPU 0; the separate two-GPU workflow uses sequence parallelism. Its root
filesystem is read-only. Partner nodes and other custom nodes are disabled;
only the retained queue guard and pinned Qwen sequence-parallel loader are
whitelisted. The Pi can keep hosting LiteLLM/Open WebUI while GPU execution
stays on this AI box.

## Restore

Docker and NVIDIA Container Toolkit use the existing
[AI service installation](../local-ai/README.md). Commands below run from
`~/Projects/dotfiles/system/comfyui`.

```bash
mkdir -p "$HOME/.local/share/comfyui"/{models,input,output,temp,cache,user/default/workflows}
sudo docker compose build
```

Download just the three core BF16 files (32,440,124,920 bytes), using the same
temporary download helper verified during installation. It is removed after
the transfer; ComfyUI itself runs entirely in Docker. Downloading can take a
substantial time; rerunning the download reuses completed files and cached
chunks. The weights are repackaged by Comfy-Org from
[Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1), under the
Qwen Research License for noncommercial use.

```bash
comfy_download_tools="$(mktemp -d)"
python -m venv "$comfy_download_tools"
"$comfy_download_tools/bin/pip" --disable-pip-version-check --no-cache-dir install huggingface_hub==2.4.0 hf_xet==1.7.1
HF_HUB_DISABLE_TELEMETRY=1 HF_XET_HIGH_PERFORMANCE=1 HF_XET_CACHE="$HOME/.local/share/comfyui/cache/xet" "$comfy_download_tools/bin/hf" download Comfy-Org/Qwen-Image-2.1 diffusion_models/qwen_image_2.1_bf16.safetensors text_encoders/qwen3vl_8b_bf16.safetensors vae/qwen_image_2.1_vae_bf16.safetensors --revision 0217efd1d9c9452e84f6448903d6e21bfa171ffd --local-dir "$HOME/.local/share/comfyui/models"
rm -rf -- "$comfy_download_tools"
unset comfy_download_tools
cp workflows/qwen-image-2.1.json "$HOME/.local/share/comfyui/user/default/workflows/"
```

Pinned model sizes and SHA-256 values are in
[the model manifest](../../models/qwen-image-2.1.json). The workflow uses
the standard model, 1024 by 1024 pixels, 25 Euler/simple steps and CFG 1.
It accepts a detailed English scene description directly; no separate prompt
enhancer model is installed. Start with this size before trying larger images.

## Two-GPU extension and benchmark

The separate `qwen-image-2.1-2gpu.json` browser workflow and
`qwen-image-2.1-2gpu-api.json` API workflow replace only the diffusion loader
with `QwenImage21SPUNETLoader`, `world_size=2`, `devices=0,1`. It distributes
attention and token computation using NCCL/Ulysses sequence parallelism. Each
GPU keeps a copy of the BF16 diffusion model; this does not combine the cards
into a single 48 GB memory pool. The standard workflow remains available for
one-GPU operation. Both use the same model files, 25 steps and CFG 1.

The extension is a third-party community project, not an official Qwen or
ComfyUI extension. Its source is
[buqi-qwen-image-2.1-multigpu](https://github.com/buqi-code/buqi-qwen-image-2.1-multigpu/tree/081b20eedf57cbaa6cb1dd3cab0434914f625a00),
pinned at `081b20eedf57cbaa6cb1dd3cab0434914f625a00`. Its archive SHA-256 is
`2d3b6972c93e46fb296c49983f282653da7f1a9dff596aa492bdfd69ad8564b6`.
A retained [compatibility patch](patches/attention-container.patch) consumes
ComfyUI 0.43's attention tensor containers before the distributed collectives.
Source stays under the ComfyUI data directory and is mounted read-only;
no host Python packages or additional model weights are installed.

Restore the source before creating/recreating the container:

```bash
comfy_sp_archive="$(mktemp)"
curl --fail --location https://github.com/buqi-code/buqi-qwen-image-2.1-multigpu/archive/081b20eedf57cbaa6cb1dd3cab0434914f625a00.tar.gz --output "$comfy_sp_archive"
printf '%s  %s\n' 2d3b6972c93e46fb296c49983f282653da7f1a9dff596aa492bdfd69ad8564b6 "$comfy_sp_archive" | sha256sum --check
mkdir -p "$HOME/.local/share/comfyui/extensions/qwen-image21-sp"
tar -xzf "$comfy_sp_archive" --strip-components=1 -C "$HOME/.local/share/comfyui/extensions/qwen-image21-sp"
patch --directory="$HOME/.local/share/comfyui/extensions/qwen-image21-sp" -p1 < patches/attention-container.patch
rm -- "$comfy_sp_archive"
unset comfy_sp_archive
cp workflows/qwen-image-2.1-2gpu.json "$HOME/.local/share/comfyui/user/default/workflows/"
```

After restoring the extension and workflows, create the container and install
the lifecycle helper and selector:

```bash
mkdir -p "$HOME/.local/share/comfyui/runtime"
sudo install -Dm755 usr/local/libexec/comfyui-lifecycle.py /usr/local/libexec/comfyui-lifecycle.py
sudo docker compose create
sudo install -Dm644 ../local-ai/etc/llama-swap/config.yaml /etc/llama-swap/config.yaml
sudo systemctl restart llama-swap.service
```

Benchmark from this directory with no other GPU work or dashboards polling
upstream chat model endpoints:

```bash
python benchmark.py workflows/qwen-image-2.1-api.json --label single-gpu-bf16 --output "$HOME/.local/share/comfyui/runtime/benchmark-single-gpu.json"
python benchmark.py workflows/qwen-image-2.1-2gpu-api.json --label two-gpu-bf16 --output "$HOME/.local/share/comfyui/runtime/benchmark-two-gpu.json"
```

Each command restarts ComfyUI through llama-swap, runs one cold job and three
warm jobs with seeds 424200–424203, and records ComfyUI execution timestamps,
request elapsed time and sampled GPU memory/utilization. Changing the seed
forces actual sampling on every run. Model loading is included in the cold
execution time; container startup is measured separately. Raw results and
benchmark images stay outside Git. BF16 kernel layouts can produce small pixel
differences between GPU counts, so bit-identical images are not assumed.

Verified on 2026-10-29 with two RTX 3090 24 GB cards over PCIe/PHB, without
NVLink. Times include 1024-square BF16 sampling, VAE decode and PNG save:

| Configuration | Cold job | Warm jobs | Warm mean |
| --- | ---: | --- | ---: |
| One GPU | 30.285 s | 15.938 / 15.977 / 16.022 s | 15.979 s |
| Two GPUs, sequence parallel | 30.896 s | 12.004 / 12.068 / 12.100 s | 12.057 s |

Two GPUs reduced warm execution time by 24.54% (1.325 times the throughput);
cold generation time was similar. Warm runs reuse the same prompt conditioning
and vary the seed; changed-prompt performance was not separately benchmarked.
Sampled memory peaks were 23,670 MiB on GPU 0 with one GPU, and 23,922 /
14,781 MiB on GPUs 0 / 1 with two GPUs. Both cards reached 100% utilization
in the two-GPU runs. These are sampled observations, not guaranteed peak bounds.

The paired seed-424201 outputs were visually inspected and looked consistent.
Across all four identical-seed pairs, mean absolute RGB channel differences
were 0.485–0.796 on the 0–255 scale; these outputs are not pixel-identical.
The two-GPU workflow is the preferred option for repeated image generation;
load `qwen-image-2.1-2gpu.json` from ComfyUI's workflow browser. Keep
`qwen-image-2.1.json` for single-GPU use. The alternative of placing the text
encoder/VAE on one card and diffusion on the other is not installed or tested.

A real distributed image job also passed the queue-safe chat handover test:
new submissions received HTTP 503 during draining, the accepted image finished,
the container and distributed worker stopped, chat returned `4` for `2+2`,
and restarting ComfyUI restored successful history and served the resulting PNG.

## Repeatable images

Both saved browser workflows set KSampler's seed control to `fixed` (seed 42
by default). Keep the seed, prompt, negative prompt, workflow, resolution,
sampler, scheduler, steps, CFG, model files, GPU count and software versions
unchanged to reproduce a render. Save the workflow JSON with the seed.

Verified on 2026-10-29: the two-GPU BF16 workflow at seed 424200 was generated
again after a container restart. ComfyUI reported no cached nodes, and the
result had pixel-identical decoded output to the original cold benchmark
image. PNG file bytes need not match because metadata can differ. This is a
verified repeat on this pinned setup, not a guarantee across versions, hardware,
GPU counts or all possible workflows. The one-versus-two-GPU comparison above
showed small pixel differences even with identical seeds.

## GPU use and suspend

The reserved `comfyui_auto` model belongs to llama-swap's existing exclusive
GPU group. An image request unloads chat; a chat request drains and stops the
image container before loading chat. The boot service still preloads its
selected Strata 0.2.4.2 model. Idle browser WebSockets do not keep the image
backend active or restart it after a switch.

The lifecycle helper sets a drain marker before shutdown. The local extension
rejects new prompt submissions with HTTP 503 while draining, counts accepted
submissions still being parsed, and waits for queued/running work and history
writes to finish. It then requires five seconds of idle before stopping Docker.
An unavailable queue check or failed history write prevents shutdown. The last
20 completed jobs are saved in `runtime/history.json` so results remain
available after a restart. Generated PNG files remain in `output/`.

ComfyUI has no idle TTL because submissions return before generation finishes.
It stops when another GPU backend is selected or all models are unloaded:

```bash
curl --fail -X POST http://127.0.0.1:8000/api/models/unload
```

The ComfyUI unload timeout is 24 hours to allow image queues to drain. Avoid
queues that take longer than this. Direct `docker stop`, service shutdown,
forced termination and power loss do not receive this queue protection.
Do not start the container manually alongside a chat model; use the proxy.

The suspend guard checks ComfyUI's queue and latest execution timestamps.
Queued/running images prevent suspend, and completed jobs reset the existing
15-minute idle grace. Merely opening the UI does not count as generation.
Install the retained guard with:

```bash
sudo install -Dm755 ../local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo systemctl restart ollama-idle-suspend.service
python3 /usr/local/libexec/ollama-idle-suspend.py --check
```

## Stop and remove

```bash
sudo docker compose down
sudo docker image rm local-ai/comfyui:0.43.0-cu130
```

The data directory remains available for reuse. Delete
`~/.local/share/comfyui` only when its models and generated images are no
longer wanted. No AUR package, dedicated system account or `/opt/comfyui`
directory is used by this Docker installation.

## Verification

Verified on 2026-10-29: container build and localhost API, PyTorch
2.13.0+cu130 on an RTX 3090, all nine workflow nodes in the browser, and all
three model SHA-256 hashes. A cold 1024 by 1024 BF16 generation with the saved
workflow, seed 42 and 25 Euler/simple steps completed successfully in 29.257
seconds according to ComfyUI's execution timestamps. The resulting cabin
still-life PNG was visually inspected. GPU memory polling observed 22,362 MiB
in use; this is a sampled observation, not a guaranteed peak bound.

Live image activity was detected by the installed suspend guard; all 28 guard
regression tests pass. Image models were released afterwards and the existing
Strata chat backend restored. Higher resolutions, editing and sustained performance remain unverified. The container has no independent boot restart policy.

The installed llama-swap integration and LAN port publication were verified on
2026-10-29. The browser loaded all nine workflow nodes through the LAN proxy;
the host listener was `0.0.0.0:8188`. A real 1024-square image completed in
29.754 seconds while a simultaneous chat request waited. The drain guard
rejected new submissions with HTTP 503, stopped the container after completion,
and chat inference succeeded with its GPU memory released. Restarting ComfyUI
restored that job's successful history and served its PNG through the proxy.
The installed helper and selector match these templates. Compose/selector
validation and all 36 regression tests passed.
