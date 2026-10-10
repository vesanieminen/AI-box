# Recording machine changes

For changes to this user's machine configuration, use the dotfiles repository at
`~/Projects/dotfiles`. Read its `AGENTS.md` before making machine changes.

- The starting point is a default Omarchy installation. Track only deliberate
  changes made from now on; do not import untouched defaults or package inventories.
- Inspect live configuration before editing. Keep temporary backups outside the
  repository. Add newly changed files AFTER editing, using `scripts/capture.py --add`.
- After changing a tracked live file, run `scripts/capture.py`, review the Git
  diff, validate the affected application, and commit that task's changes locally.
  Do not include unrelated changes.
- Record deliberate package additions/removals according to `packages/README.md`.
- Record system-wide changes as configuration templates in `system/`,
  with instructions and validation. Record manual actions in `docs/machine-changes.md`.
- Keep secrets, authentication state, caches, logs, and generated files out of Git.
- Do not publish or push the repository unless the user requests it.

These instructions apply to machine configuration work. Application repositories
should continue to follow their own development instructions.

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
