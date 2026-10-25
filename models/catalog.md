# Current local model catalog

Measured on 2026-10-25 from the installed files. Sizes are **logical file bytes**,
not RAM/VRAM requirements or filesystem allocated blocks. Directory totals include
configuration/tokenizer files and retained preparation assets, excluding download
completion markers and Hugging Face caches. The Maya directory includes its pack;
Qwen MTP preparation assets are listed separately. Hardlinked HyperQwen files and
shared Ollama blobs count once in the aggregate. Btrfs reflinks/compression are not
accounted for. Runtime images, engine binaries, download archives, logs and
conversation caches are excluded. This is a size/presence inventory, not a new
checksum or inference-quality verification.

Paths below are relative to `/home/vesanieminen/.local/share/`.

| Model / component | Status / purpose | Bytes | GB | GiB | Location |
| --- | --- | ---: | ---: | ---: | --- |
| gemma-4-26b-a4b-exl3-8bpw.2x | Configuration only; weights absent | 49,327 | 0.000 | 0.000 | `vllm/models/gemma-4-26b-a4b-exl3-8bpw.2x` |
| gemma-4-26b-a4b.tabbyapi.64k | Chat model | 20,298,847,630 | 20.299 | 18.905 | `vllm/models/gemma-4-26b-a4b.tabbyapi.64k` |
| gemma-4-31b-int4-tp2 | Chat model | 20,936,927,653 | 20.937 | 19.499 | `vllm/models/gemma-4-31b-int4-tp2` |
| gemma-4-31b-int8-tp2 | Chat model | 35,122,584,505 | 35.123 | 32.710 | `vllm/models/gemma-4-31b-int8-tp2` |
| Qwen3.8-27B-DFlash2-W4A16 | Prepared HyperQwen; companion draft | 1,280,638,845 | 1.281 | 1.193 | `vllm/models/hyperqwen/Qwen3.8-27B-DFlash2-W4A16` |
| Qwen3.8-27B-W4A16-AutoRound | Prepared HyperQwen; serving unverified | 16,765,239,778 | 16.765 | 15.614 | `vllm/models/hyperqwen/Qwen3.8-27B-W4A16-AutoRound` |
| Qwen3.8-27B-W4A16-AutoRound-fast | Prepared HyperQwen; serving unverified | 15,812,337,109 | 15.812 | 14.726 | `vllm/models/hyperqwen/Qwen3.8-27B-W4A16-AutoRound-fast` |
| ornith-1.5-35b-a3b.tabbyapi.128k | Chat model | 19,833,966,474 | 19.834 | 18.472 | `vllm/models/ornith-1.5-35b-a3b.tabbyapi.128k` |
| ornith-1.5-35b-int4-tp2 | Chat model | 26,165,777,721 | 26.166 | 24.369 | `vllm/models/ornith-1.5-35b-int4-tp2` |
| ornith-1.5-9b.tabbyapi.128k | Chat model | 7,208,829,561 | 7.209 | 6.714 | `vllm/models/ornith-1.5-9b.tabbyapi.128k` |
| qwen3.6-35b-a3b.vllm.128k.2x | Chat model | 21,549,137,359 | 21.549 | 20.069 | `vllm/models/qwen3.6-35b-a3b.vllm.128k.2x` |
| qwen3.8-27b-int4-mtp | Chat model | 18,224,427,719 | 18.224 | 16.973 | `vllm/models/qwen3.8-27b-int4-mtp` |
| qwen3.8-27b-int8 | Chat model | 31,636,520,343 | 31.637 | 29.464 | `vllm/models/qwen3.8-27b-int8` |
| qwen3.8-27b-int8-dflash2 | Chat model | 29,555,451,193 | 29.555 | 27.526 | `vllm/models/qwen3.8-27b-int8-dflash2` |
| qwen3.8-27b.sglang.208k | Chat model | 13,843,803,198 | 13.844 | 12.893 | `vllm/models/qwen3.8-27b.sglang.208k` |
| qwen3.8-dflash2-draft | Companion draft | 3,849,113,002 | 3.849 | 3.585 | `vllm/models/qwen3.8-dflash2-draft` |
| qwen3.8-dflash2-draft-w8 | Companion draft | 2,172,758,237 | 2.173 | 2.024 | `vllm/models/qwen3.8-dflash2-draft-w8` |
| Qwen3.8 Flash Next IQ3_S | Strata; shared by all three containers | 84,525,205,664 | 84.525 | 78.720 | `strata/models` |
| Qwen Flash Next MTP assets | Companion + preparation assets | 6,927,659,014 | 6.928 | 6.452 | `strata/mtp` |
| DeepSeek V4.1 Flash IQ2_XS | Strata; four main shards | 155,225,824,256 | 155.226 | 144.565 | `strata-deepseek/models/deepseek-v4.1-flash-IST-DAS-2.25bpw` |
| DeepSeek shared Engram / DSpark / metadata | Required shared assets; DSpark currently unloaded | 118,577,985,645 | 118.578 | 110.434 | `strata-deepseek/models/deepseek-v4.1-flash-shared` |
| Nemotron 3.5 Bolt IQ2 | llama.cpp; includes projector and drafter | 24,750,261,824 | 24.750 | 23.050 | `llama.cpp/models/nemotron-bolt` |
| GLM-5.3 Flash Maya-S24 IQ2_XXS_S | Project Maya; includes vision and prepared pack | 96,790,790,000 | 96.791 | 90.143 | `project-maya/models/Maya-S24` |
| GLM Flash DFlash2 Q4_K_M | Optional companion draft | 697,017,248 | 0.697 | 0.649 | `project-maya/models/GLM-5.3-Flash-DFlash2` |

## Ollama tags

Tag sizes include their referenced configuration and layers. The two Qwen3.8 tags
share their model/projector blobs, so these rows must not be added together.
The Ollama service is a retained alternative, not the selected boot service.

| Tag | Referenced bytes | GB | GiB |
| --- | ---: | ---: | ---: |
| `qwen3.5:27b` | 17,420,432,728 | 17.420 | 16.224 |
| `qwen3.5:9b` | 6,594,474,711 | 6.594 | 6.142 |
| `qwen3.8:27b` | 17,741,872,154 | 17.742 | 16.523 |
| `qwen3.8:3090` | 17,741,872,135 | 17.742 | 16.523 |

Unique referenced Ollama blobs: **41,756,768,483 bytes (38.889 GiB)**.

All cataloged assets, counting shared inodes/blobs once: **798,698,871,588 bytes
(798.699 GB / 743.846 GiB)**.

The complete DeepSeek seven-file set is **273,803,809,901 bytes** (255.000 GiB).
Its installed configuration and running engine both use `--ssd-cache 112`, with
262144 context. Startup preloaded 87.7 GB of hot expert payloads; one short request
passed after restart. Sustained memory/performance at 112 GB and full-context
operation remain unverified. Qwen Strata 0.2.4.2 remains the boot default.

Pinned sources, revisions and download/restore commands are linked from
[the model index](README.md). The empty Gemma 8bpw folder is not a usable model.
The same Qwen weights are shared by the stable, beta and release Strata routes;
those routes do not represent three separate downloads.
