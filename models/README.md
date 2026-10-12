# Model assets

Weights are stored outside Git. The original 13 model directories and four Ollama tags were copied from the SSD on 2026-10-10, avoiding another download. vLLM model files total approximately 248 GB (231 GiB), plus approximately 39 GiB of Ollama data. Cache files are optional and excluded from the inventory.

The additional W8 DFlash2 companion draft is stored in
`~/.local/share/vllm/models/qwen3.8-dflash2-draft-w8` and pinned to
`f454fa8e6a84387bf006f849584f72541cc29118`. Its 2,172,742,656-byte weight file
was downloaded from Hugging Face and verified against published SHA-256
`72223787fbfe7e01c4a940f80f98cf3d7a803e9b79aa4ec7bc28a461d767fa18`.
The BF16 and W8 llama-swap entries reuse the target model previously verified
during download to the external SSD and then copied to this machine's M.2 drive.
No target weights were redownloaded.

## Default boot model

`qwen3.8-27b-int8`: Qwen3.8 27B INT8 W8A16 with MTP, served through llama-swap on port 8000 across two RTX 3090 GPUs.
The complete chat models are configured for on-demand switching through vLLM,
TabbyAPI or SGLang. The Gemma 26B 8bpw folder contains configuration but no
weights; the DFlash2 draft is a companion, not a standalone chat model. See [service restoration](../system/local-ai/README.md).

## Hugging Face models

`vllm.json` records each repository, exact revision, file sizes and a download command. Folder names preserve the SSD naming; EXL3 folders use TabbyAPI or SGLang through llama-swap; they are not vLLM model formats. Some SSD folders were pruned to model files; downloading the pinned repository can restore additional documentation.

| Local directory | Download source | Revision | Copied GiB |
| --- | --- | --- | --- |
| `qwen3.8-27b-int8` | [lued/Qwen3.8-27B-INT8-W8A16-MTP](https://huggingface.co/lued/Qwen3.8-27B-INT8-W8A16-MTP/tree/7c12373712d1363e2b76655cb3332c9c124627d7) | `7c12373712d1363e2b76655cb3332c9c124627d7` | 29.5 |
| `qwen3.6-35b-a3b.vllm.128k.2x` | [Twu31/Qwen3.6-35B-A3B-GPTQ-INT4-W4A16-LowLatency](https://huggingface.co/Twu31/Qwen3.6-35B-A3B-GPTQ-INT4-W4A16-LowLatency/tree/d14fd7339b09364ea2aabc542ea20f7dccd97ca1) | `d14fd7339b09364ea2aabc542ea20f7dccd97ca1` | 20.1 |
| `qwen3.8-27b-int4-mtp` | [Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency](https://huggingface.co/Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency/tree/75e632dd5cc71fa0ee3a000f99f6840afc0375e2) | `75e632dd5cc71fa0ee3a000f99f6840afc0375e2` | 17.0 |
| `qwen3.8-dflash2-draft` | [z-lab/Qwen3.8-27B-DFlash2](https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2/tree/50307d4c4cde6860d4eee73e2547cd786fe8e8a4) | `50307d4c4cde6860d4eee73e2547cd786fe8e8a4` | 3.6 |
| `qwen3.8-27b-int8-dflash2` | [lued/Qwen3.8-27B-INT8-W8A16-DFlash2](https://huggingface.co/lued/Qwen3.8-27B-INT8-W8A16-DFlash2/tree/2971c64ba386dd3faa6884cc215f67b3b2477a3e) | `2971c64ba386dd3faa6884cc215f67b3b2477a3e` | 27.5 |
| `ornith-1.5-35b-int4-tp2` | [cyankiwi/Ornith-1.5-35B-A3B-AWQ-INT4](https://huggingface.co/cyankiwi/Ornith-1.5-35B-A3B-AWQ-INT4/tree/8cace5667cfc076c9f06b36854a1dbe255b79600) | `8cace5667cfc076c9f06b36854a1dbe255b79600` | 24.4 |
| `gemma-4-31b-int4-tp2` | [cyankiwi/gemma-4-31B-it-AWQ-4bit](https://huggingface.co/cyankiwi/gemma-4-31B-it-AWQ-4bit/tree/6f1b616c64bca2a05d67fdd6437c5500a8509327) | `6f1b616c64bca2a05d67fdd6437c5500a8509327` | 19.5 |
| `gemma-4-31b-int8-tp2` | [cyankiwi/gemma-4-31B-it-AWQ-8bit](https://huggingface.co/cyankiwi/gemma-4-31B-it-AWQ-8bit/tree/34ca187d836de874b2c7e3edf48f439b9f583772) | `34ca187d836de874b2c7e3edf48f439b9f583772` | 32.7 |
| `gemma-4-26b-a4b-exl3-8bpw.2x` | [UnstableLlama/gemma-4-26B-A4B-it-exl3-8.00bpw](https://huggingface.co/UnstableLlama/gemma-4-26B-A4B-it-exl3-8.00bpw/tree/198e29717e14fbd92bb47c08ce593d4331f27141) | `198e29717e14fbd92bb47c08ce593d4331f27141` | 0.0 |
| `gemma-4-26b-a4b.tabbyapi.64k` | [turboderp/gemma-4-26B-A4B-it-exl3](https://huggingface.co/turboderp/gemma-4-26B-A4B-it-exl3/tree/241bce8ff2259445258144a660678c47030867cf) | `241bce8ff2259445258144a660678c47030867cf` | 18.9 |
| `ornith-1.5-35b-a3b.tabbyapi.128k` | [ultimatechris/Ornith-1.5-35B-A3B-EXL3-4bpw](https://huggingface.co/ultimatechris/Ornith-1.5-35B-A3B-EXL3-4bpw/tree/875ac67dae8e793770396908c575c507f4cd5f75) | `875ac67dae8e793770396908c575c507f4cd5f75` | 18.5 |
| `ornith-1.5-9b.tabbyapi.128k` | [ultimatechris/Ornith-1.5-9B-EXL3-4bpw](https://huggingface.co/ultimatechris/Ornith-1.5-9B-EXL3-4bpw/tree/8d1e89ef430f9ba3a12789b198abf1385670ceb0) | `8d1e89ef430f9ba3a12789b198abf1385670ceb0` | 6.7 |
| `qwen3.8-27b.sglang.208k` | [turboderp/Qwen3.8-27B-exl3](https://huggingface.co/turboderp/Qwen3.8-27B-exl3/tree/6fe61ad620abfe97c5b49f9722c2bceeea4ccc28) | `6fe61ad620abfe97c5b49f9722c2bceeea4ccc28` | 12.9 |

The W8 draft source is [lued/Qwen3.8-27B-DFlash2-W8](https://huggingface.co/lued/Qwen3.8-27B-DFlash2-W8/tree/f454fa8e6a84387bf006f849584f72541cc29118); its pinned download command and file inventory are in `vllm.json`.

Install the Arch `python-huggingface-hub` package for `hf` only when downloads are needed. It is not required to serve the already copied models. Download only missing assets; already copied assets do not need redownloading. For example:

```bash
hf download lued/Qwen3.8-27B-INT8-W8A16-MTP --revision 7c12373712d1363e2b76655cb3332c9c124627d7 --local-dir "$HOME/.local/share/vllm/models/qwen3.8-27b-int8"
```

For all models, run the individual `download_command` entries in `vllm.json`. Hugging Face authentication, if required by a repository, must be provisioned separately; no tokens are recorded here. See the [official CLI documentation](https://huggingface.co/docs/huggingface_hub/en/guides/cli).

## Ollama models

`ollama.json` records the four tag manifests, their SHA-256 hashes and referenced blob digests. The copied data lives in `~/.local/share/ollama/models`. Registry tags can change; the preserved manifests and blobs retain the SSD versions.

- [qwen3.5:9b and qwen3.5:27b](https://ollama.com/library/qwen3.5)
- [qwen3.8:27b](https://ollama.com/library/qwen3.8)
- `qwen3.8:3090`, a custom profile derived from `qwen3.8:27b`, with a 118000-token context and the saved Modelfile.

To rebuild missing Ollama assets while the configured Ollama server is running:

```bash
ollama pull qwen3.5:9b
ollama pull qwen3.5:27b
ollama pull qwen3.8:27b
ollama create qwen3.8:3090 -f "$HOME/.local/share/ollama/Qwen38-3090.Modelfile"
```

The configured server sets `OLLAMA_MODELS` to the copied user directory. Do not run an unconfigured server that uses a different model directory. Model weights are not backed up by this repository; retain a separate disk backup if preserving these exact downloads is required.

## Original HTML catalog

The SSD’s `Documents/Local-AI/Models.html` is copied and managed under `home/`.
It lists eight selected two-GPU model components; the other five archived
variants are on disk and recorded in `vllm.json`. The HTML is the original SSD
snapshot: its old addresses, server-status text, verification labels and 175 W
manual benchmark plans do not describe changes applied to this box. GPU power
limits remain 350 W, and model service configuration and current validation are documented separately
in `system/local-ai/README.md`.

## HyperQwen prepared assets

The pinned [HyperQwen source](https://github.com/syv-ai/HyperQwen/tree/7af097b5ea3acfecd60aabbff5bc457e503b2dc5)
is retained at `~/Projects/HyperQwen`. Three prepared model components are stored
under `~/.local/share/vllm/models/hyperqwen`, with the project's `models` symlink
pointing there. Hardlinks between the base and fast variants are preserved;
the unique model files occupy 17.74 GiB. A recursive checksum comparison against
the SSD found no differences. [hyperqwen.json](hyperqwen.json) records the source
commit, original runtime digest, known input revisions and file inventory.

Restore the source and model link with:

```bash
git clone https://github.com/syv-ai/HyperQwen.git ~/Projects/HyperQwen
git -C ~/Projects/HyperQwen checkout 7af097b5ea3acfecd60aabbff5bc457e503b2dc5
# Restore the prepared model folders from their separate backup first:
ln -s "$HOME/.local/share/vllm/models/hyperqwen" "$HOME/Projects/HyperQwen/models"
```

The original runtime image is
`ghcr.io/syv-ai/hyperqwen@sha256:25bfa39ca4b71d5ba5ea32e5486c841dd4fb8b6429846c012ec5d1b06b2457a6`.
The copied source documents preparation and Docker restoration. Exact prepared
weights require their separate backup; input download commands in `hyperqwen.json`
restore raw sources rather than the prepared target folders. The fast-variant
Hub input revision remains unconfirmed. Serving these prepared assets on this
installation is outstanding; the active llama-swap setup uses the separate
lued INT8 checkpoints.

Eleven original recipe JSON files for retained model families are preserved in
`~/.local/share/vllm/recipes/` as reference data. Current service flags and pinned
weights are recorded in this repository's service and model records.
