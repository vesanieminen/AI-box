# Dotfiles workflow

The starting point is a default Omarchy installation. Record only deliberate
changes made from now on. Do not import untouched defaults or full installed
package inventories.

Live configuration lives under HOME; chezmoi source files live under `home/`
(see `.chezmoiroot`).

1. Read `README.md` and inspect Git status before changing machine configuration.
2. Inspect the existing live config. Keep any needed temporary backup outside
   this repository. Make the requested change and validate the affected app,
   following the Omarchy skill when applicable. Never edit `/usr/share/omarchy`.
3. After changing a NEW configuration file, review it for secrets/runtime state
   and run `./scripts/capture.py --add "$HOME/.config/example/config"`.
   Capture only deliberately changed files. Whole edited files are retained for
   restoration; untouched Omarchy defaults stay outside this repository.
4. For tracked files, run `./scripts/capture.py`, review the diff, and avoid
   including unrelated live changes. The helper handles regular files only and
   refuses to overwrite pending source edits. Manage symlinks, templates, and
   encrypted files through chezmoi once installed, outside the capture manifest.
5. Record deliberate package additions/removals according to `packages/README.md`.
   Record system changes as configuration templates in `system/`; document
   manual actions in `docs/machine-changes.md`.
6. Stage specific files for this task and commit locally after validation.
   Do not stage unrelated changes or push without a user request.

Keep credentials, private keys, tokens, browser profiles, history, caches, logs,
generated theme output, and authentication directories out of Git. Document
secret provisioning without recording the secrets themselves.

Use normal Arch repository/AUR package installation for applications and record
only deliberate additions. Do not retain one-off SSD copying or installation
scripts. Keep model weights outside Git; record model sources, pinned revisions,
and download commands. This machine primarily serves AI models; preserve the
selected llama-swap boot service and default vLLM profile and AI-aware automatic suspend behavior.

Documentation describes the final working installation: installed programs and
their purpose, retained settings, restore commands and verified behavior. Update
existing entries when the configuration changes. Do not append troubleshooting
chronology, failed attempts, temporary workarounds or superseded settings. Keep
model provenance and clearly identify verification that is still outstanding.
