FROM vllm/vllm-openai@sha256:0a51ea5b4ae2dc5d81890e5173f54203d2a3ae0cfffe51b8fd2afd4391bfd967
COPY . /etc/club3090/dflash2/
RUN python3 /etc/club3090/dflash2/patch_mamba_drop_eagle_block.py && bash /etc/club3090/dflash2/install.sh && python3 /etc/club3090/dflash2/patch_embedding.py
