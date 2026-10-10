#!/usr/bin/env python3
"""Publish the desktop idle monitor's state for the system sleep guard."""
import json
import os
from pathlib import Path
import sys
import time

folder = Path.home() / '.local/state/ollama'
folder.mkdir(parents=True, exist_ok=True)
target = folder / 'desktop-idle.json'
temp = folder / f'.desktop-idle.{os.getpid()}'
temp.write_text(json.dumps({'idle': sys.argv[1] == 'true', 'at': time.time()}))
temp.replace(target)
