# Strata 0.2.7 alongside the existing backends

Terminal 0.2.7, Control 0.1.52 and both CUDA 13 engines 0.1.52 are installed
under `~/.local/share/strata-0.2.7`. These are isolated native runtimes using
the official bundled Python and GPU libraries; no host packages were added.
Existing Qwen and DeepSeek weights, tokenizers and packs are shared in place.
Installed files occupy about 2.1 GB (2.0 GiB), excluding runtime logs. Model
weights and binaries stay outside Git. [Pinned archives](strata-0.2.7.json)
record upstream sources, sizes, hashes and build IDs.

| Selector entry | Local port | Profile |
| --- | --- | --- |
| `qwen3.8-flash-next-iq3-s-027` | 5820 | Qwen IQ3_S, MTP4, 256K, INT8 KV, GPU vision, PLE in RAM |
| `deepseek-v4.1-flash-iq2-xs-027` | 5821 | DeepSeek IQ2_XS, 256K, two GPUs, TP1, 112 GB expert store |

The profiles retain the existing explicit tuning values; those values have not
been recalibrated against 0.1.52. New engine defaults apply to settings that are
not explicitly pinned. Qwen uses `prlimit --memlock=unlimited` before dropping
to the user's identity so its 26.82 GiB PLE table can be locked in RAM. The second GPU has an explicit
1136 MiB reserve (`--vram-reserve-later-mib`) for generation workspace. DeepSeek
retains text/tools support; this profile does not provision the new vision tower.
The two routes join the existing exclusive GPU group. The suspend guard includes
both ports. The selected boot service, Qwen 0.2.4.2 preload and default vLLM
profile are preserved. Select these models through llama-swap on port 8000;
do not start GPU backends separately while another is loaded.

## Restore

Restore existing Qwen and DeepSeek model assets first, then apply the two
Chezmoi-managed profiles under `~/.local/share/strata-0.2.7/config/`. From this
repository root, download and verify the pinned archives and unpack them:

```bash
python - <<'PYRESTORE'
import hashlib, json, pathlib, tarfile, urllib.request
r = json.loads(pathlib.Path('system/local-ai/strata-0.2.7.json').read_text())
base = pathlib.Path(r['directory']).expanduser()
cache = pathlib.Path('~/.cache/strata-0.2.7-downloads').expanduser()
cache.mkdir(parents=True, exist_ok=True)
folders = {'control': 'terminal',
           'engine': 'engine/0.1.52-linux-x86_64-cuda-cuda13',
           'dsv41': 'engine-dsv41/0.1.52-linux-x86_64-cuda-cuda13'}
for a in r['packages']:
    archive = cache / a['archive']
    urllib.request.urlretrieve(r['download_base'] + a['archive'], archive)
    with archive.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == a['sha256']
    target = base / folders[a['component']]
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as bundle:
        bundle.extractall(target, filter='data')
(base / 'runtime').mkdir(exist_ok=True)
PYRESTORE
llama-swap -config system/local-ai/etc/llama-swap/config.yaml -validate
sudo install -Dm644 system/local-ai/etc/llama-swap/config.yaml /etc/llama-swap/config.yaml
sudo install -Dm755 system/local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo systemctl kill --kill-whom=main --signal=HUP llama-swap.service
sudo systemctl restart ollama-idle-suspend.service
```

Reloading the selector unloads its current backend; wait for active inference
to finish first. The boot unit is not changed. The archives can be removed from
the download cache after successful extraction and verification.

## Verification

The release feed (sequence 115) was verified with the previously installed
release's trusted key `5d1bc23abbeffd0d`. All three archives match the signed
feed and upstream SHA256SUMS. Both engine manifests match the feed; their
signatures and every listed file hash passed using the prior Control's verifier.
Terminal reports 0.2.7/build 0.1.52; server imports and both engine help commands
pass. Configured model paths are readable and all native shared libraries resolve.
The selector configuration validates with 20 models. Both new entries are visible
in the running selector; installed selector and suspend-guard files match the
retained templates, and both services are active. Qwen loaded with 262144 context,
vision and a locked PLE table. Generation checks are pending.
Full-context stability, long-running performance and new-version calibration
remain unverified.
