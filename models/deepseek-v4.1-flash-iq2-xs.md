# DeepSeek V4.1 Flash IQ2_XS

## Runtime and retained settings

This deployment uses the official bundled Terminal natively, independently of
the Qwen Docker containers. No host Python packages were installed. The
configuration is captured at `~/.local/share/strata-deepseek/config/deepseek-iq2-xs.json`.
It selects both GPUs, a layer split (`--tp 1`), 262144 context and
`--ssd-cache 104` (104 decimal GB, approximately 97 GiB). The automatic cache
caps itself at 48 GB; the explicit budget leaves room for the OS and runtime.
DSpark stays automatic and the engine leaves it unloaded on this hardware.
Text and tools are supported; vision is disabled.

Local text (Paris and 323), streaming and a parsed echo function call passed.
With the retained cache, a 160-token coding stream ran at 14.3 decode tok/s;
about 103 GiB total RAM was used with 22 GiB available, and each GPU used about
23 GiB. The engine reports 40.16 GB of GPU experts, 109.7 GB of CPU-lane experts,
and 0.25 GB of GPU context caches. Its 104 GB store preloaded 81.3 GB of hot
expert payloads; slot padding and other allocations consume additional memory.
Not all CPU-lane weights are simultaneously cached. These are startup and short
request measurements. Full-context requests, long-context quality and sustained
memory/performance remain unverified.

## Restore the runtime and model pack

First restore the model files below and the captured configuration with Chezmoi.
Use Control archive `strata-control-0.1.49.2-linux-x86_64.tar.gz` with SHA-256
`2f905fe9e7f0c0f7e1d055a414acc0b3dae6db2d42e7f6a97e57e8ff7d3cf9c6` from the
[Strata release](https://github.com/Niko1221/Strata/releases/tag/v0.2.4).
Unpack it without installing host dependencies:

```bash
mkdir -p ~/.local/share/strata-deepseek/terminal
tar -xzf ~/.cache/strata-0.2.4-downloads/strata-control-0.1.49.2-linux-x86_64.tar.gz \
  -C ~/.local/share/strata-deepseek/terminal
```

Download `strata-dsv41-0.1.49.2-linux-x86_64-cuda-cuda13.tar.gz` from the same
release into `~/.cache/strata-deepseek-downloads/`. Its SHA-256 is
`918a2155ad6bad0ef6d54e57280dfc7cf6fe713838ca9303300bccaebf275283`.
Check the hash before installing; the vendor installer additionally checks the
package signature and every listed file:

```bash
cd ~/.local/share/strata-deepseek/terminal
./python/bin/python3 - <<'PY'
from pathlib import Path
from strata_control.dsv41_engine import install_package
base = Path.home() / '.local/share/strata-deepseek'
archive = Path.home() / '.cache/strata-deepseek-downloads/strata-dsv41-0.1.49.2-linux-x86_64-cuda-cuda13.tar.gz'
assert install_package(base / 'engine-dsv41', archive)
PY
./python/bin/python3 - <<'PY'
from pathlib import Path
import setup, subprocess, shutil
base = Path.home() / '.local/share/strata-deepseek'
model = base / 'models/deepseek-v4.1-flash-IST-DAS-2.25bpw'
shared = base / 'models/deepseek-v4.1-flash-shared'
pack = base / 'packs/iq2_xs'
spec = setup.MULTI_FILE_FAMILIES['deepseek41']['models']['IST-DAS-2.25bpw']
subprocess.run(setup.dsv41_pack_cmd(model, spec['shards'], shared / setup.DSV41_ISTA_ENGRAM,
    shared / setup.DSV41_SHARD.format(i=1), shared / setup.DSV41_DSPARK, pack), check=True)
shutil.copy2(setup.DSV41_PROFILES / spec['profile'], pack / 'expert-profile.bin')
PY
mkdir -p ~/.local/share/strata-deepseek/runtime
```

## Llama-swap integration

The retained route is `deepseek-v4.1-flash-iq2-xs` on localhost port 5818.
It launches the bundled server as UID 1000 and belongs to the existing exclusive
GPU group. Qwen remains the boot default. The monitor uses the existing LAN
listener on all interfaces at port 8000:

`http://192.168.0.181:8000/upstream/deepseek-v4.1-flash-iq2-xs/`

The selector, suspend guard and boot unit are installed and match the retained
templates. Switching from Qwen to DeepSeek through llama-swap passed; LAN health,
monitor HTML and all four CSS/JS assets returned HTTP 200. Restore after closing
model monitors and finishing active requests:

```bash
cd ~/Projects/dotfiles
sudo install -Dm644 system/local-ai/etc/llama-swap/config.yaml /etc/llama-swap/config.yaml
sudo install -Dm755 system/local-ai/usr/local/libexec/ollama-idle-suspend.py /usr/local/libexec/ollama-idle-suspend.py
sudo install -Dm644 system/local-ai/etc/systemd/system/llama-swap.service /etc/systemd/system/llama-swap.service
sudo systemctl daemon-reload
sudo systemctl restart llama-swap.service ollama-idle-suspend.service
curl --max-time 900 -fsS http://127.0.0.1:8000/upstream/deepseek-v4.1-flash-iq2-xs/health
```

Do not start the temporary validation server beside llama-swap-managed models.
Only keep the selected model's monitor open: model-specific polling can switch
the active backend. The installed suspend guard includes backend port 5818;
serving and switching stay under llama-swap.

## Download provenance

The Strata variant is `IST-DAS-2.25bpw`. Weights and shared files total
273,803,809,901 bytes and live in `~/.local/share/strata-deepseek/models`.
[The manifest](deepseek-v4.1-flash-iq2-xs.json) records every pinned URL, size and
SHA-256. The download passed pinned integrity checks, the pack passed the engine's
file/kernel checks, and local text, streaming and tool calls passed. The
llama-swap route and suspend guard are installed; managed loading, LAN monitor
access and an arithmetic response (323) through the LAN API are verified.

## Download and resume

Use the verified Control archive from the [Strata release instructions](../system/local-ai/images/strata-release/README.md).
This downloads only weights, using the release's pinned revisions and hashes;
it does not install packages, pack a model or start an engine:

```bash
cd ~/.local/share/strata-deepseek/terminal
./python/bin/python3 -u - <<'PY'
from pathlib import Path
import setup
base = Path.home() / '.local/share/strata-deepseek/models'
model = base / 'deepseek-v4.1-flash-IST-DAS-2.25bpw'
shared = base / 'deepseek-v4.1-flash-shared'
spec = setup.MULTI_FILE_FAMILIES['deepseek41']['models']['IST-DAS-2.25bpw']
for name in spec['shards']:
    setup.download(spec['hf'] + name, model / name)
for name in spec['shared']:
    setup.download(setup.DSV41_SHARED[name] + name, shared / name)
PY
```

Stop any existing downloader before manually resuming. Keep the machine awake
while using the foreground restore command. The initially launched background
job uses a transient user service, resumes automatically after transfer errors,
and temporarily uses the existing machine stay-awake flag. It does not survive
a reboot. No permanent system suspend policy was changed.

```bash
systemctl --user status strata-deepseek-download.service
journalctl --user -u strata-deepseek-download.service -f
systemctl --user stop strata-deepseek-download.service
```

The downloader writes its completion markers only after checking each pinned
file. To independently verify completed files against the retained manifest:

```bash
python - <<'PY'
import hashlib, json
from pathlib import Path
manifest = Path.home() / 'Projects/dotfiles/models/deepseek-v4.1-flash-iq2-xs.json'
for item in json.loads(manifest.read_text())['files']:
    path = Path(item['path']).expanduser()
    assert path.stat().st_size == item['bytes'], path
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert actual == item['sha256'], path
    print('Verified:', path.name)
PY
```
