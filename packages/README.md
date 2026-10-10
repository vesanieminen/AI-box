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

Geekbench 7 uses the standard AUR package `geekbench` (7.1.0-1 at import).
Restore with `yay -S --needed geekbench`. Its package recipe downloads the
vendor archive and verifies SHA-256 before packaging; build scripts stay in the
AUR build cache, outside this repository. [AUR package](https://aur.archlinux.org/packages/geekbench),
[vendor downloads](https://www.geekbench.com/download/). Benchmark runs are manual.

Llama-swap uses AUR `llama-swap-bin`. Install with
`yay -S --needed llama-swap-bin`; its recipe verifies the upstream release
archive checksum. Configuration and service restoration are in
`system/local-ai/README.md`. [AUR package](https://aur.archlinux.org/packages/llama-swap-bin),
[upstream project](https://github.com/mostlygeek/llama-swap).

GitHub CLI uses Arch `github-cli`: `sudo pacman -S --needed github-cli`.
PAT provisioning and HTTPS Git authentication are documented in `docs/github.md`.
