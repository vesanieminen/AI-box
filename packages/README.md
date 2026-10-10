# Package changes

Record only deliberate package changes made after establishing this repository.
Do not list the default installation or snapshot all installed packages.

Create these files as needed, one package name per line, sorted and unique:

- `official.txt`: packages deliberately added from configured Arch/Omarchy repositories.
- `foreign.txt`: packages deliberately added from AUR or another external source.
- `removed.txt`: default packages deliberately removed from this machine.

When reverting a custom addition, remove it from its additions list. When
reinstalling a previously removed default package, remove it from `removed.txt`.
Use Git commits to preserve the history. Record unusual sources, manual binary
installations, and setup steps in `docs/machine-changes.md` or `system/`.

These lists describe changes to an Omarchy base installation. Applying them is
a deliberate restore step, not part of capturing files or `chezmoi apply`.

Restore additions using the ordinary package manager:

```bash
sudo pacman -S --needed $(cat packages/official.txt)
```

Transitive dependencies are resolved by pacman, not listed as custom additions.
The AI runtime uses `ollama-cuda` from Arch and a pinned vLLM Docker image;
see `system/local-ai/README.md`.
