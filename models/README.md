# Model assets

[Qwen-Image-2.1](qwen-image-2.1.json) records the three BF16 image-generation
components and pinned download command. Its on-demand Docker runtime and
restoration are documented in [ComfyUI](../system/comfyui/README.md).

[Current catalog: exact sizes, locations and shared assets](catalog.md) records
the installed inventory measured on 2026-10-25, including DeepSeek and all
companion models.

Weights are stored outside Git. The original 13 model directories and four Ollama tags were copied from the SSD on 2026-10-10, avoiding another download. vLLM model files total approximately 248 GB (231 GiB), plus approximately 39 GiB of Ollama data. Cache files are optional and excluded from the inventory.

The additional W8 DFlash2 companion draft is stored in
`~/.local/share/vllm/models/qwen3.8-dflash2-draft-w8` and pinned to
`f454fa8e6a84387bf006f849584f72541cc29118`. Its 2,172,742,656-byte weight file
was downloaded from Hugging Face and verified against published SHA-256
`72223787fbfe7e01c4a940f80f98cf3d7a803e9b79aa4ec7bc28a461d767fa18`.
The BF16 and W8 llama-swap entries reuse the target model previously verified
during download to the external SSD and then copied to this machine's M.2 drive.
No target weights were redownloaded.

## Strata Flash Next assets

The standard IQ3_S model and BF16 vision projector are installed under
`~/.local/share/strata/models`; generated packs and the extracted MTP subset
remain under the same data directory. The two GGUF shards total 77.88 GiB.
[strata.json](strata.json) records their source revision, published hashes, the pinned Strata
runtime and MTP checkpoint. Local shard sizes match the published inventory;
independent full-shard SHA-256 verification is outstanding. Text and image
requests through llama-swap passed; full-context capacity is unverified.
[Build, download and preparation commands](../system/local-ai/README.md#strata-flash-next-with-vision)
reuse existing assets when present. No host Hugging Face CLI is needed.

## Default boot model

`qwen3.8-flash-next-iq3-s-0242`: calibrated Strata 0.2.4.2 Qwen3.8 Flash Next IQ3_S with MTP4 and GPU vision, served by Strata through llama-swap on port 8000 across two RTX 3090 GPUs.
The complete chat models are configured for on-demand switching through vLLM,
TabbyAPI, SGLang or Strata. The Gemma 26B 8bpw folder contains configuration but no
weights; the DFlash2 draft is a companion, not a standalone chat model. See [service restoration](../system/local-ai/README.md).

## Hugging Face models

`vllm.json` records each repository, exact revision, file sizes and a download command. Folder names preserve the SSD naming; EXL3 folders use TabbyAPI or SGLang through llama-swap; they are not vLLM model formats. Some SSD folders were pruned to model files; downloading the pinned repository can restore additional documentation.

The Strata entry uses `~/.local/share/strata/models`; its size covers the two
IQ3_S GGUF shards. Its projector, MTP assets and preparation steps are documented
in [Strata Flash Next assets](#strata-flash-next-assets) above. Other directory
names below are relative to `~/.local/share/vllm/models`.

| Local directory / model | Runtime | Download source | Revision | Stored GiB |
| --- | --- | --- | --- | --- |
| `~/.local/share/strata/models` — Qwen3.8 Flash Next IQ3_S (Strata), boot default | Strata | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) | `ed59f92082b1e93c0e96d60a8b11aab089b52f09` | 77.88 |
| `qwen3.8-27b-int8` | vLLM | [lued/Qwen3.8-27B-INT8-W8A16-MTP](https://huggingface.co/lued/Qwen3.8-27B-INT8-W8A16-MTP/tree/7c12373712d1363e2b76655cb3332c9c124627d7) | `7c12373712d1363e2b76655cb3332c9c124627d7` | 29.5 |
| `qwen3.6-35b-a3b.vllm.128k.2x` | vLLM | [Twu31/Qwen3.6-35B-A3B-GPTQ-INT4-W4A16-LowLatency](https://huggingface.co/Twu31/Qwen3.6-35B-A3B-GPTQ-INT4-W4A16-LowLatency/tree/d14fd7339b09364ea2aabc542ea20f7dccd97ca1) | `d14fd7339b09364ea2aabc542ea20f7dccd97ca1` | 20.1 |
| `qwen3.8-27b-int4-mtp` | vLLM | [Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency](https://huggingface.co/Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency/tree/75e632dd5cc71fa0ee3a000f99f6840afc0375e2) | `75e632dd5cc71fa0ee3a000f99f6840afc0375e2` | 17.0 |
| `qwen3.8-dflash2-draft` | vLLM (companion draft) | [z-lab/Qwen3.8-27B-DFlash2](https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2/tree/50307d4c4cde6860d4eee73e2547cd786fe8e8a4) | `50307d4c4cde6860d4eee73e2547cd786fe8e8a4` | 3.6 |
| `qwen3.8-27b-int8-dflash2` | vLLM | [lued/Qwen3.8-27B-INT8-W8A16-DFlash2](https://huggingface.co/lued/Qwen3.8-27B-INT8-W8A16-DFlash2/tree/2971c64ba386dd3faa6884cc215f67b3b2477a3e) | `2971c64ba386dd3faa6884cc215f67b3b2477a3e` | 27.5 |
| `ornith-1.5-35b-int4-tp2` | vLLM | [cyankiwi/Ornith-1.5-35B-A3B-AWQ-INT4](https://huggingface.co/cyankiwi/Ornith-1.5-35B-A3B-AWQ-INT4/tree/8cace5667cfc076c9f06b36854a1dbe255b79600) | `8cace5667cfc076c9f06b36854a1dbe255b79600` | 24.4 |
| `gemma-4-31b-int4-tp2` | vLLM | [cyankiwi/gemma-4-31B-it-AWQ-4bit](https://huggingface.co/cyankiwi/gemma-4-31B-it-AWQ-4bit/tree/6f1b616c64bca2a05d67fdd6437c5500a8509327) | `6f1b616c64bca2a05d67fdd6437c5500a8509327` | 19.5 |
| `gemma-4-31b-int8-tp2` | vLLM | [cyankiwi/gemma-4-31B-it-AWQ-8bit](https://huggingface.co/cyankiwi/gemma-4-31B-it-AWQ-8bit/tree/34ca187d836de874b2c7e3edf48f439b9f583772) | `34ca187d836de874b2c7e3edf48f439b9f583772` | 32.7 |
| `gemma-4-26b-a4b-exl3-8bpw.2x` | TabbyAPI / ExLlamaV3 (weights absent) | [UnstableLlama/gemma-4-26B-A4B-it-exl3-8.00bpw](https://huggingface.co/UnstableLlama/gemma-4-26B-A4B-it-exl3-8.00bpw/tree/198e29717e14fbd92bb47c08ce593d4331f27141) | `198e29717e14fbd92bb47c08ce593d4331f27141` | 0.0 |
| `gemma-4-26b-a4b.tabbyapi.64k` | TabbyAPI / ExLlamaV3 | [turboderp/gemma-4-26B-A4B-it-exl3](https://huggingface.co/turboderp/gemma-4-26B-A4B-it-exl3/tree/241bce8ff2259445258144a660678c47030867cf) | `241bce8ff2259445258144a660678c47030867cf` | 18.9 |
| `ornith-1.5-35b-a3b.tabbyapi.128k` | TabbyAPI / ExLlamaV3 | [ultimatechris/Ornith-1.5-35B-A3B-EXL3-4bpw](https://huggingface.co/ultimatechris/Ornith-1.5-35B-A3B-EXL3-4bpw/tree/875ac67dae8e793770396908c575c507f4cd5f75) | `875ac67dae8e793770396908c575c507f4cd5f75` | 18.5 |
| `ornith-1.5-9b.tabbyapi.128k` | TabbyAPI / ExLlamaV3 | [ultimatechris/Ornith-1.5-9B-EXL3-4bpw](https://huggingface.co/ultimatechris/Ornith-1.5-9B-EXL3-4bpw/tree/8d1e89ef430f9ba3a12789b198abf1385670ceb0) | `8d1e89ef430f9ba3a12789b198abf1385670ceb0` | 6.7 |
| `qwen3.8-27b.sglang.208k` | SGLang / ExLlamaV3 | [turboderp/Qwen3.8-27B-exl3](https://huggingface.co/turboderp/Qwen3.8-27B-exl3/tree/6fe61ad620abfe97c5b49f9722c2bceeea4ccc28) | `6fe61ad620abfe97c5b49f9722c2bceeea4ccc28` | 12.9 |

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

## Nemotron 3.5 Bolt assets

The native IQ2 model and vision projector are downloaded directly from
`nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF` revision
`724e3fee41becc4048998e2204748147876ed56b`, into
`~/.local/share/llama.cpp/models/nemotron-bolt`. They total 23,752,019,264 bytes
(22.12 GiB). [nemotron-bolt.json](nemotron-bolt.json) records each published
SHA-256, file size and exact resumable curl command. Weights remain outside Git.
The matching 998242560-byte LiLiCorr draft is installed in the same directory,
from `nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-LiLiCorr-GGUF` revision
`182d2987939e12f458298b5d5f6ef98912f4ad6c`. Its source, hash and download
command are also recorded in `nemotron-bolt.json`. All three files are
downloaded and their local sizes and SHA-256 hashes match the pinned inventory.
Text, synthetic image-color identification and a 262012-input-token capacity
test passed with NVIDIA's DFlash7 recipe. General quality, tool use and
maximum-context multimodal capacity remain unverified. Serving configuration,
benchmarks and restore commands are in [the Bolt service record](../system/local-ai/README.md#nemotron-35-bolt).

## Project Maya assets

GLM-5.3-Flash Maya-S24 IQ2_XXS_S and its BF16 vision encoder are stored under
`~/.local/share/project-maya/models/Maya-S24` on the internal NVMe.
[maya-s24.json](maya-s24.json) records the pinned Hugging Face revision, file
sizes, published SHA-256 hashes, resumable download commands and runtime commit.
The model shards total 94,701,676,224 bytes (88.20 GiB); the vision projector and
vocabulary add 1,137,473,824 bytes. Generated packs, tokenizer files, logs and
conversation state remain outside Git. The optional DFlash2 Q4_K_M drafter
(697017248 bytes) is cached separately, pinned and checksum-verified in the
same inventory. It uses CC BY-NC-ND 4.0 (non-commercial); the retained serving
profile uses the built-in MTP block after the speed comparison.

[Installation and restoration](../system/local-ai/README.md#project-maya) describe
the source build and model preparation. All five downloaded files passed size
and SHA-256 verification against the pinned inventory. Serving validation is
recorded separately in the service instructions.

## DeepSeek V4.1 Flash assets

The seven IQ2_XS / IST-DAS 2.25 bpw files occupy 273,803,809,901 bytes
(255.000 GiB) under `~/.local/share/strata-deepseek/models`.
[Runtime and restoration](deepseek-v4.1-flash-iq2-xs.md) and
[the pinned manifest](deepseek-v4.1-flash-iq2-xs.json) record sources and hashes.
The native Strata engine uses both GPUs, 262144 context and a 112 GB expert
RAM-store limit; startup and a short request passed at that limit.

## Qwen Flash Next UD-Q4_K_XL acquisition

The four checksum-verified Unsloth GGUF shards are installed at
`~/.local/share/strata-unsloth/models/UD-Q4_K_XL`, separately from the existing
Docker-owned IQ3_S model directory. [Pinned files](strata-qwen-ud-q4-k-xl.json)
record revision `38bb39ee97821de2c9009abb7e93950eec396e66`, exact sizes and SHA-256.
The set totals **111,334,654,784 bytes** (111.335 GB / 103.688 GiB).
The existing Qwen projector and MTP assets are retained for reuse.
All four local sizes and downloader SHA-256 completion markers match the pins.
Model preparation and serving validation are outstanding;
the current DeepSeek backend and llama-swap entries are unchanged.

The completed resumable, checksum-verifying download used the transient user unit
`strata-q4-download.service`. Its runtime-only log is
`~/.cache/strata-q4-download/download.log`. The downloader creates the Omarchy
stay-awake indicator only if absent, then removes its own indicator on exit;
it does not remove an existing user indicator. No permanent suspend settings change.

To resume/reacquire with the installed official Terminal's downloader:

```bash
cd ~/.local/share/strata-deepseek/terminal
./python/bin/python3 - <<'PYTHON'
from pathlib import Path
import setup
base = Path.home() / '.local/share/strata-unsloth/models/UD-Q4_K_XL'
repo = 'unsloth/Qwen3.8-Flash-Next-GGUF'
assert setup.HF_REVISIONS[repo] == '38bb39ee97821de2c9009abb7e93950eec396e66'
for name in setup.UNSLOTH_SHARDS:
    setup.download(setup.hf(repo) + 'UD-Q4_K_XL/' + name, base / name)
PYTHON
```

## Swift IQ3_S and Qwen UD-Q5_K_XL acquisition plans

[Swift IQ3_S pins](strata-swift-iq3-s.json) record the two model shards and its
vision projector (84,651,280,640 bytes total), with destination
`~/.local/share/strata-swift/models/IQ3_S`. The Swift download is active at unrestricted speed, resuming partial files;
it is not yet a complete or verified model.
[Qwen UD-Q5_K_XL pins](strata-qwen-ud-q5-k-xl.json) record its six shards
(158,286,406,650 bytes total), with planned destination
`~/.local/share/strata-unsloth/models/UD-Q5_K_XL`; it is queued after Swift
finishes and verifies. The transient user unit `strata-next-downloads.service`
runs both downloads sequentially without an automatic restart policy. It holds
an owned stay-awake indicator during acquisition and removes it on exit.
The current model server and llama-swap configuration are unchanged.

To resume or reacquire, use the installed official
Terminal's `setup.download(url, destination)` with each manifest's pinned URLs;
it resumes partial files and verifies each pinned size and SHA-256 as above.

Pause the download queue with `systemctl --user stop strata-next-downloads.service`.
Partial files and chunk metadata are retained. While the transient unit remains
loaded, `systemctl --user start strata-next-downloads.service` resumes it; after
a reboot the transient unit must be recreated. The runtime-only queue and script
live in `~/.cache/strata-next-downloads/`, and can be reconstructed from the pinned
manifests. Each completed file is checksum-verified before moving on.

The queue is **unrestricted**, with `limit-mbps` set to zero. The optional
runtime-only response-read limiter remains available in its cached script. All download connections share one
schedule; the model files, official downloader and checksum logic are unchanged.
`~/.cache/strata-next-downloads/limit-mbps` contains the MB/s limit; zero removes
the limit without restarting. When enabled, the cap applies to Swift and then Q5 and does not
limit inference traffic. A cap may permit brief network-buffer bursts. The user
requested full speed; no bandwidth cap is currently applied.
