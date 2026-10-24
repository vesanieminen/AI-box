# Strata 0.2.4.2 update

Prepared upgrade for the existing Qwen route and container, using Terminal
Control 0.1.49.2 and Qwen engine 0.1.48. **Not yet activated:** Docker build,
container replacement and inference validation require administrator access.
The running installation remains 0.2.0-beta. No DeepSeek weights or engine have
been downloaded.

The new Compose file is `~/.local/share/strata-release/compose.yaml`. Its project,
service and container names intentionally match the existing deployment so
llama-swap continues to manage the same container and port. It mounts the new
configuration directory while retaining the existing model assets and runtime
directory. Inference arguments and the expert-profile bytes are unchanged;
only the vision executable's versioned path changes. The vLLM profiles, boot
unit and suspend guard are untouched.

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

## Activate after building

Finish requests and close model UI tabs first. Unload through llama-swap, replace
the stopped container, and request its health through the same route to load it:

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/models/unload/qwen3.8-flash-next-iq3-s-beta
sudo docker compose -f ~/.local/share/strata-release/compose.yaml create --force-recreate
curl --max-time 900 -fsS http://127.0.0.1:8000/upstream/qwen3.8-flash-next-iq3-s-beta/health
```

Validate model discovery, text, streaming and vision before considering the
upgrade complete. The historical `beta` route/container names remain for
compatibility. To restore the old runtime, unload the same route, recreate using
`~/.local/share/strata-beta/compose.yaml`, then request the same health endpoint.
Its image and original configuration have been retained.
