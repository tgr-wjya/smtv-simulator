# Terminal Rice Setup Design

## Overview

Configure terminal environment with modern tooling, Tokyo Night theme, and comprehensive aliases. Modular configuration structure for maintainability.

## Requirements

- kitty terminal emulator with Tokyo Night theme
- zsh + oh-my-zsh (plugins only) + Starship prompt
- Modern CLI tool replacements (eza, bat, fd, ripgrep, zoxide, dust)
- FiraCode Nerd Font for icon support
- Comprehensive aliases covering git, docker/podman, navigation, system management
- `wtfjusthappen` function for quick log inspection
- Disable Bazzite banner on shell startup
- All tools installed via Homebrew for isolation

## File Structure

```
~/.config/
├── kitty/
│   └── kitty.conf           # Terminal emulator config (Tokyo Night theme, FiraCode font)
├── starship.toml            # Prompt config (Tokyo Night preset)
└── zsh/
    ├── aliases.zsh          # All command shortcuts
    ├── functions.zsh        # Complex logic (wtfjusthappen, etc)
    ├── exports.zsh          # Environment variables (PATH, defaults)
    └── plugins.zsh          # oh-my-zsh plugin loading

~/.zshrc                     # Main entry point, sources all zsh/*.zsh files
~/.config/no-show-user-motd  # Empty file to disable Bazzite banner
```

### Shell Bootstrap Order

1. oh-my-zsh initialization (with `ZSH_THEME=""` to disable built-in themes)
2. Source modular configs: exports → aliases → functions → plugins
3. Initialize Starship last (overrides prompt)

## Components

### kitty Configuration

**`~/.config/kitty/kitty.conf`:**
- Tokyo Night color scheme (16 ANSI colors + foreground/background)
- FiraCode Nerd Font, size 11
- Window padding for visual breathing room
- Tab bar styling
- Standard copy/paste keybinds (Ctrl+Shift+C/V)

### Starship Configuration

**`~/.config/starship.toml`:**
- Tokyo Night preset as base
- Active modules: directory, git, language runtimes (Node.js, Python, Rust), execution time, battery
- Compact single-line mode
- Overrides oh-my-zsh prompt completely

### Zsh Modular Configuration

**`~/.config/zsh/exports.zsh`:**
- Homebrew paths
- Default editors (EDITOR, VISUAL)
- XDG base directory variables
- Language-specific environment variables (if needed)

**`~/.config/zsh/aliases.zsh`:**
- Modern tool replacements:
  - `ls` → `eza --icons --group-directories-first`
  - `ll` → `eza -la --icons --group-directories-first`
  - `cat` → `bat --style=auto`
  - `find` → `fd`
  - `grep` → `rg`
- Git shortcuts:
  - `gs` = git status
  - `ga` = git add
  - `gc` = git commit
  - `gp` = git push
  - `gl` = git log --oneline --graph
  - `gd` = git diff
- Navigation:
  - `..` = cd ..
  - `...` = cd ../..
  - `....` = cd ../../..
- Bazzite-specific:
  - `update` = rpm-ostree upgrade + flatpak update + brew upgrade (sequential)
- Docker/Podman:
  - `dps` = docker ps
  - `dimg` = docker images
  - `dlog` = docker logs -f
  - `dex` = docker exec -it
- Safety nets:
  - `rm` → `rm -i`
  - `cp` → `cp -i`
  - `mv` → `mv -i`
- Quick info:
  - `ports` = netstat -tuln
  - `myip` = curl ifconfig.me

**`~/.config/zsh/functions.zsh`:**
- `wtfjusthappen`: Display last 50 lines from journalctl and dmesg, filtered to last 5 minutes. Shows recent system events and errors.
- `mkcd <dir>`: Create directory and cd into it in one command
- `extract <file>`: Universal archive extractor supporting tar, zip, gz, bz2, rar, 7z

**`~/.config/zsh/plugins.zsh`:**
- oh-my-zsh plugins:
  - `git` - git aliases and completions
  - `zsh-autosuggestions` - fish-style command suggestions based on history
  - `zsh-syntax-highlighting` - real-time command validation with color
  - `colored-man-pages` - syntax highlighting for man pages
  - `command-not-found` - suggests package installation when command missing

### Main .zshrc

**`~/.zshrc`:**
1. Set oh-my-zsh path and theme (ZSH_THEME="")
2. Initialize oh-my-zsh
3. Source modular configs in order: exports → aliases → functions → plugins
4. Initialize Starship: `eval "$(starship init zsh)"`
5. Initialize zoxide (if installed): `eval "$(zoxide init zsh)"`

## Installation Steps

### 1. Install Homebrew
Check if Homebrew exists. If not, install via official script.

### 2. Install CLI Tools
```bash
brew install eza bat fd ripgrep zoxide dust starship
brew install --cask font-fira-code-nerd-font
brew install --cask kitty  # or skip if already installed
```

### 3. Install oh-my-zsh
Run official installer. Backs up existing `.zshrc` to `.zshrc.pre-oh-my-zsh`.

### 4. Install oh-my-zsh Plugins
Clone into `~/.oh-my-zsh/custom/plugins/`:
- zsh-autosuggestions
- zsh-syntax-highlighting

### 5. Generate Configurations
Create all config files as specified in File Structure section.

### 6. Disable Bazzite Banner
Create empty file: `touch ~/.config/no-show-user-motd`

### 7. Change Default Shell
```bash
chsh -s $(which zsh)
```
Requires logout/login to take effect.

## Verification

- Open new terminal → Starship prompt appears, no Bazzite banner
- Test `ls` → shows eza output with icons
- Test `cat <file>` → shows bat syntax highlighting
- Test `wtfjusthappen` → displays recent system logs
- Verify font → icons render correctly in prompt and eza output
- Test git aliases: `gs`, `gl`, `gd`
- Test navigation aliases: `..`, `...`

## Why This Approach

**Modular over monolithic:** Easier to maintain, share specific pieces, track changes in git, understand at a glance.

**oh-my-zsh for plugins, Starship for prompt:** Starship is faster and more featureful than oh-my-zsh themes. oh-my-zsh provides excellent plugin ecosystem. Use each tool for its strength.

**Homebrew for all packages:** On immutable systems like Bazzite (rpm-ostree), Homebrew provides isolated, easily updatable tools without requiring system reboots.

**FiraCode Nerd Font:** Excellent ligature support + full icon set for Starship and eza. JetBrains Mono already reserved for editor.

**Tokyo Night theme:** Popular, muted color scheme with good contrast. Widely supported across tools.

## Trade-offs

**Learning curve:** More files to understand than single `.bashrc`. Mitigated by clear naming and comments.

**oh-my-zsh overhead:** Adds ~100ms startup time. Acceptable for feature set gained.

**Brew vs system packages:** Brew packages are user-space only, may duplicate system libraries. Acceptable for isolation and easy updates on immutable OS.

**Nerd Font requirement:** Icons won't render without patched font. Must configure terminal emulator and ensure font installed.
