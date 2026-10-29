FROM pytorch/pytorch:2.13.0-cuda13.0-cudnn9-runtime@sha256:db80a41f8428644cebcb3d75b0b62df334ab6c0e75785951eb25f48bfbd42407

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    XDG_CACHE_HOME=/data/cache \
    HF_HOME=/data/cache/huggingface \
    TORCH_HOME=/data/cache/torch \
    TORCHINDUCTOR_CACHE_DIR=/data/cache/torchinductor

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 python3-venv \
    && rm -rf /var/lib/apt/lists/*

# ComfyUI v0.43.0, commit 426f5eea52a7ece1dd599fff4cb6cd1f352ddd24.
ADD --checksum=sha256:8a496a7d82bd343cafdb2b867857fe8c5140e3cd9ec5cf46c6277ccb7466f202 https://github.com/Comfy-Org/ComfyUI/archive/refs/tags/v0.43.0.tar.gz /tmp/comfyui.tar.gz
RUN mkdir /opt/comfyui \
    && tar -xzf /tmp/comfyui.tar.gz --strip-components=1 -C /opt/comfyui \
    && python -m venv --system-site-packages /opt/comfyui-venv \
    && /opt/comfyui-venv/bin/python -c "import torch; assert torch.__version__.split('+')[0] == '2.13.0'; print(torch.__version__, torch.version.cuda)" \
    && /opt/comfyui-venv/bin/python -m pip install --no-cache-dir 'torch==2.13.0' -r /opt/comfyui/requirements.txt \
    && rm /tmp/comfyui.tar.gz

ENV PATH="/opt/comfyui-venv/bin:${PATH}" \
    CUDA_CACHE_PATH=/data/cache/nvidia \
    TRITON_CACHE_DIR=/data/cache/triton

WORKDIR /opt/comfyui
USER 1000:1000
ENTRYPOINT ["/opt/comfyui-venv/bin/python", "/opt/comfyui/main.py"]
CMD ["--base-directory", "/data", "--listen", "0.0.0.0", "--port", "8188", "--cuda-device", "0", "--reserve-vram", "1.0", "--offline", "--disable-all-custom-nodes"]
