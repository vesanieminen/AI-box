#!/usr/bin/env python3
"""Capture explicitly selected regular dotfiles in chezmoi source format."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home().resolve()
MANIFEST = ROOT / "tracked-files.json"
BLOCKED = {".ssh", ".aws", ".gnupg", ".codex", ".cache", ".git"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def target_path(name):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"Invalid target path: {name}")
    if relative.parts[0] in BLOCKED:
        raise ValueError(f"Authentication/runtime directory excluded: {name}")
    path = HOME / relative
    if not path.resolve().is_relative_to(HOME):
        raise ValueError(f"Path escapes HOME: {name}")
    # A symlinked parent could restore the file into a different location.
    if any(p.is_symlink() for p in [path, *path.parents] if p != HOME):
        raise ValueError(f"Use chezmoi directly for symlink paths: {name}")
    if not path.is_file():
        raise ValueError(f"Missing regular file (review deletion explicitly): {name}")
    return path


def source_name(relative, mode):
    parts = ["dot_" + p[1:] if p.startswith(".") else p for p in Path(relative).parts]
    prefix = ""
    if not mode & (stat.S_IRGRP | stat.S_IROTH):
        prefix += "private_"
    if mode & stat.S_IXUSR:
        prefix += "executable_"
    parts[-1] = prefix + parts[-1]
    return str(Path(*parts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--add", nargs="+", default=[], metavar="FILE")
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    args = parser.parse_args()
    if args.check and args.add:
        parser.error("--check cannot be combined with --add")
    entries = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for name in args.add:
        path = Path(os.path.abspath(os.path.expanduser(name)))
        if not path.is_relative_to(HOME):
            raise ValueError(f"Target is outside HOME: {name}")
        relative = str(path.relative_to(HOME))
        if relative not in entries:
            entries[relative] = {}

    plans = []
    drift = []
    # Validate everything before writing any snapshot files.
    for name, entry in sorted(entries.items()):
        target = target_path(name)
        mode = stat.S_IMODE(target.stat().st_mode)
        if mode not in (0o600, 0o644, 0o700, 0o755):
            raise ValueError(f"Unsupported permissions {mode:o}: {name}; use chezmoi directly")
        data = target.read_bytes()
        encoded = source_name(name, mode)
        old_encoded = entry.get("source", encoded)
        old_relative = Path(old_encoded)
        if old_relative.is_absolute() or ".." in old_relative.parts:
            raise ValueError(f"Invalid manifest source: {old_encoded}")
        old_source = ROOT / "home" / old_relative
        source = ROOT / "home" / encoded
        for candidate in (old_source, source):
            if not candidate.resolve().is_relative_to(ROOT / "home"):
                raise ValueError(f"Source escapes home tree: {candidate}")
            if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != ROOT):
                raise ValueError(f"Source must be a regular path: {candidate}")
        if entry.get("sha256") and not old_source.exists():
            raise ValueError(f"Source was deleted: {old_source}; reconcile before capture")
        if old_source.exists():
            previous = old_source.read_bytes()
            if digest(previous) != entry.get("sha256", digest(data)) and previous != data:
                raise ValueError(f"Source has pending edits: {old_source}; reconcile before capture")
        if (not source.exists() or source.read_bytes() != data or
                stat.S_IMODE(source.stat().st_mode) != mode or old_encoded != encoded):
            drift.append(name)
        plans.append((name, old_source, source, encoded, data, mode))

    if args.check:
        for name in drift:
            print(f"Changed: {name}")
        if not drift:
            print(f"All {len(entries)} captured files match live configuration.")
        return bool(drift)

    for name, old_source, source, encoded, data, mode in plans:
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(data)
        source.chmod(mode)
        if old_source != source and old_source.exists():
            old_source.unlink()
        entries[name] = {"source": encoded, "sha256": digest(data)}
    MANIFEST.write_text(json.dumps(dict(sorted(entries.items())), indent=2) + "\n")
    print(f"Captured {len(entries)} files; {len(drift)} new or changed. Review git diff before committing.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"capture: {error}", file=sys.stderr)
        sys.exit(1)
