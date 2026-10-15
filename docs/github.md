# GitHub access

GitHub CLI is provided by Arch's `github-cli` package:

```bash
sudo pacman -S --needed github-cli
```

The user launcher at `~/.local/bin/gh` executes `/usr/bin/gh`.
Credentials are provisioned separately from dotfiles. Put the PAT in
`~/.config/gh/pat`, with directory permissions 700 and file permissions 600.
Edit it locally; the file must contain only the token. The authentication
directory is excluded from capture, Chezmoi deployment and Git.

For a classic PAT, authenticate through standard input and set up Git:

```bash
gh auth login --hostname github.com --git-protocol https --with-token < ~/.config/gh/pat
gh auth setup-git --hostname github.com
gh auth status --hostname github.com
```

GitHub CLI recommends `GH_TOKEN` for fine-grained PATs. Use it for the command
that needs authentication, without adding the token to shell configuration:

```bash
GH_TOKEN="$(< ~/.config/gh/pat)" gh auth setup-git --hostname github.com
# After configuring an HTTPS origin for the repository:
GH_TOKEN="$(< ~/.config/gh/pat)" git -C ~/Projects/dotfiles push -u origin main
```

The `origin` remote is `https://github.com/vesanieminen/AI-box.git`, with `main`
tracking `origin/main`. Clone it on a fresh machine with:

```bash
git clone https://github.com/vesanieminen/AI-box.git ~/Projects/dotfiles
```

Publishing is an explicit step; local commits do not automatically push. A fine-grained token for an
existing repository needs Contents read/write permission to push. Provision
credentials again on a fresh installation; they are never restored from Git.

References: [GitHub CLI authentication](https://cli.github.com/manual/gh_auth_login),
[Git credential setup](https://cli.github.com/manual/gh_auth_setup-git).
