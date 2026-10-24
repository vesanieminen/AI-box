# DeepSeek V4.1 Flash IQ2_XS

The Strata variant is `IST-DAS-2.25bpw`. Weights and shared files total
273,803,809,901 bytes and live in `~/.local/share/strata-deepseek/models`.
[The manifest](deepseek-v4.1-flash-iq2-xs.json) records every pinned URL, size and
SHA-256. Download completion, packing and inference are not yet verified.
The model is not an active llama-swap route.

## Download and resume

Use the verified Control archive from the [Strata release instructions](../system/local-ai/images/strata-release/README.md).
This downloads only weights, using the release's pinned revisions and hashes;
it does not install packages, pack a model or start an engine:

```bash
cd ~/.cache/strata-0.2.4-build/terminal
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
