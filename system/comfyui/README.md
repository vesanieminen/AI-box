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

The browser interface listens at <http://127.0.0.1:8188>. For a remote browser,
forward it with `ssh -L 8188:127.0.0.1:8188 vesanieminen@192.168.0.181`.
The container uses GPU 0 as UID/GID 1000, automatic memory offloading and a
1 GB VRAM reserve. Its root filesystem is read-only. It has no boot restart
policy, and the existing llama-swap boot selection and vLLM profiles remain
in place. Partner nodes and custom nodes are disabled.

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
sudo docker compose up -d
```

Pinned model sizes and SHA-256 values are in
[the model manifest](../../models/qwen-image-2.1.json). The workflow uses
the standard model, 1024 by 1024 pixels, 25 Euler/simple steps and CFG 1.
It accepts a detailed English scene description directly; no separate prompt
enhancer model is installed. Start with this size before trying larger images.

## GPU use and suspend

Close chat interfaces and finish active chat requests before generating images.
Unload chat models through llama-swap to free the GPUs:

```bash
curl --fail -X POST http://127.0.0.1:8000/api/models/unload
```

Avoid chat requests and upstream health polling while generating; either can
load the chat backend again. The installed llama-swap v263 does not have a pause
endpoint. After generation, release ComfyUI's models before using chat again:

```bash
curl --fail -H 'Content-Type: application/json' -d '{"unload_models":true,"free_memory":true}' http://127.0.0.1:8188/free
```

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
Strata chat backend restored. Higher resolutions, editing, multi-GPU operation
and sustained performance remain unverified. The container is left running
on demand, without automatic boot startup.
