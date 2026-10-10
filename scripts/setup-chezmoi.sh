#!/usr/bin/env bash
set -euo pipefail
dotfiles_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if ! command -v chezmoi >/dev/null; then
  echo 'Install chezmoi first from a terminal: omarchy pkg add chezmoi' >&2
  exit 1
fi
chezmoi_config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/chezmoi"
for config_format in toml yaml yml json jsonc; do
  if [[ -e "$chezmoi_config_dir/chezmoi.$config_format" ]]; then
    echo "Existing chezmoi config found; use chezmoi --source '$dotfiles_root' diff or review the config manually." >&2
    exit 1
  fi
done
mkdir -p "$chezmoi_config_dir"
python3 - "$dotfiles_root" "$chezmoi_config_dir/chezmoi.toml" <<'PY'
import json
import sys
from pathlib import Path
with Path(sys.argv[2]).open('x') as config:
    config.write('sourceDir = ' + json.dumps(sys.argv[1]) + '\n')
PY
chezmoi diff
