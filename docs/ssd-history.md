# SSD history findings

Read shell and pacman history on 2026-10-10. Raw histories and credentials are not retained.

The shell history references the custom `qwen3.8:3090` Ollama profile, Docker model-serving commands and LACT. These confirm the service configuration and model receipts retained elsewhere. Model repository revisions and file inventories are derived from the download manifests and recipe metadata, rather than guessing from shell commands.

Relevant package-manager events:

| Date | Action | Package | Version |
| --- | --- | --- | --- |
| 2025-11-16T13:38:41+0200 | installed | `docker` | `1:28.5.1-1` |
| 2025-11-16T13:38:41+0200 | installed | `docker-compose` | `2.40.3-1` |
| 2026-10-02T20:37:44+0300 | installed | `nvidia-container-toolkit` | `1.20.0-1` |
| 2026-10-06T22:34:24+0300 | installed | `openrgb` | `1.0rc3-3` |
| 2026-10-07T13:10:03+0300 | installed | `lact` | `0.10.1-1` |

The SSD used standalone Ollama, so it has no Ollama pacman installation event. This rebuild uses the normal Arch package as requested. Service-history references are clues, not instructions to enable every old experiment.
