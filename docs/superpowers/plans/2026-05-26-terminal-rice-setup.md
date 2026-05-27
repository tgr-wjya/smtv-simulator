# Terminal Rice Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure terminal with kitty, zsh, oh-my-zsh plugins, Starship prompt, Tokyo Night theme, and comprehensive modern CLI tooling.

**Architecture:** Modular zsh configuration sourced by main .zshrc. kitty and Starship configs live in XDG directories. All tools installed via Homebrew for isolation on immutable OS.

**Tech Stack:** kitty, zsh, oh-my-zsh, Starship, Homebrew, eza, bat, fd, ripgrep, zoxide, dust

---

## Task 1: Check and Install Homebrew

**Files:**
- Check: Homebrew installation status
- Create: None (Homebrew installer handles this)

- [ ] **Step 1: Check if Homebrew already installed**

Run:
```bash
which brew
```

Expected: Either `/home/linuxbrew/.linuxbrew/bin/brew` or `/opt/homebrew/bin/brew` or empty output

- [ ] **Step 2: Install Homebrew if not present**

Run (only if Step 1 returned empty):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Expected: Installation script runs, prompts for confirmation, completes successfully

- [ ] **Step 3: Add Homebrew to PATH for current session**

Run (only if Step 2 ran):
```bash
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

Expected: `which brew` now returns path

- [ ] **Step 4: Verify Homebrew works**

Run:
```bash
brew --version
```

Expected: Output like `Homebrew 4.x.x`

---

## Task 2: Install Modern CLI Tools

**Files:**
- Install: eza, bat, fd, ripgrep, zoxide, dust via Homebrew

- [ ] **Step 1: Update Homebrew**

Run:
```bash
brew update
```

Expected: Homebrew updates formula list

- [ ] **Step 2: Install modern CLI tools**

Run:
```bash
brew install eza bat fd ripgrep zoxide dust
```

Expected: All tools install successfully

- [ ] **Step 3: Verify tool installations**

Run:
```bash
eza --version && bat --version && fd --version && rg --version && zoxide --version && dust --version
```

Expected: All commands output version numbers

---

## Task 3: Install FiraCode Nerd Font

**Files:**
- Install: FiraCode Nerd Font via Homebrew cask

- [ ] **Step 1: Tap homebrew/cask-fonts**

Run:
```bash
brew tap homebrew/cask-fonts
```

Expected: Font cask repository added

- [ ] **Step 2: Install FiraCode Nerd Font**

Run:
```bash
brew install --cask font-fira-code-nerd-font
```

Expected: Font installs to `~/.local/share/fonts/` or system font directory

- [ ] **Step 3: Verify font installed**

Run:
```bash
fc-list | grep -i "FiraCode Nerd Font"
```

Expected: Output shows FiraCode Nerd Font paths

---

## Task 4: Install kitty Terminal Emulator

**Files:**
- Install: kitty via Homebrew cask

- [ ] **Step 1: Check if kitty already installed**

Run:
```bash
which kitty
```

Expected: Either path to kitty or empty output

- [ ] **Step 2: Install kitty if not present**

Run (only if Step 1 returned empty):
```bash
brew install --cask kitty
```

Expected: kitty installs successfully

- [ ] **Step 3: Verify kitty installed**

Run:
```bash
kitty --version
```

Expected: Output like `kitty 0.x.x`

---

## Task 5: Install Starship Prompt

**Files:**
- Install: Starship via Homebrew

- [ ] **Step 1: Install Starship**

Run:
```bash
brew install starship
```

Expected: Starship installs successfully

- [ ] **Step 2: Verify Starship installed**

Run:
```bash
starship --version
```

Expected: Output like `starship 1.x.x`

---

## Task 6: Install oh-my-zsh

**Files:**
- Install: oh-my-zsh via official installer
- Backup: `~/.zshrc` → `~/.zshrc.pre-oh-my-zsh` (automatic)

- [ ] **Step 1: Install oh-my-zsh**

Run:
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
```

Expected: oh-my-zsh installs to `~/.oh-my-zsh/`, creates default `.zshrc`

Note: `--unattended` flag prevents automatic shell switch

- [ ] **Step 2: Verify oh-my-zsh installed**

Run:
```bash
test -d ~/.oh-my-zsh && echo "oh-my-zsh installed" || echo "oh-my-zsh NOT installed"
```

Expected: Output `oh-my-zsh installed`

---

## Task 7: Install oh-my-zsh Plugins

**Files:**
- Clone: zsh-autosuggestions to `~/.oh-my-zsh/custom/plugins/zsh-autosuggestions`
- Clone: zsh-syntax-highlighting to `~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting`

- [ ] **Step 1: Install zsh-autosuggestions**

Run:
```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
```

Expected: Plugin cloned successfully

- [ ] **Step 2: Install zsh-syntax-highlighting**

Run:
```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
```

Expected: Plugin cloned successfully

- [ ] **Step 3: Verify plugins installed**

Run:
```bash
ls ~/.oh-my-zsh/custom/plugins/
```

Expected: Output shows `zsh-autosuggestions` and `zsh-syntax-highlighting` directories

---

## Task 8: Create kitty Configuration

**Files:**
- Create: `~/.config/kitty/kitty.conf`

- [ ] **Step 1: Create kitty config directory**

Run:
```bash
mkdir -p ~/.config/kitty
```

Expected: Directory created

- [ ] **Step 2: Write kitty.conf with Tokyo Night theme**

Create file `~/.config/kitty/kitty.conf`:

```conf
# Font configuration
font_family      FiraCode Nerd Font
bold_font        FiraCode Nerd Font Bold
italic_font      FiraCode Nerd Font Italic
bold_italic_font FiraCode Nerd Font Bold Italic
font_size 11.0

# Tokyo Night color scheme
foreground #a9b1d6
background #1a1b26
selection_foreground #1a1b26
selection_background #33467C

# Black
color0 #32344a
color8 #444b6a

# Red
color1 #f7768e
color9 #ff7a93

# Green
color2  #9ece6a
color10 #b9f27c

# Yellow
color3  #e0af68
color11 #ff9e64

# Blue
color4  #7aa2f7
color12 #7da6ff

# Magenta
color5  #ad8ee6
color13 #bb9af7

# Cyan
color6  #449dab
color14 #0db9d7

# White
color7  #787c99
color15 #acb0d0

# Window layout
window_padding_width 4
window_margin_width 0
single_window_margin_width 0

# Tab bar
tab_bar_edge top
tab_bar_style powerline
tab_powerline_style slanted

# Keybinds
map ctrl+shift+c copy_to_clipboard
map ctrl+shift+v paste_from_clipboard
map ctrl+shift+equal change_font_size all +1.0
map ctrl+shift+minus change_font_size all -1.0
map ctrl+shift+backspace change_font_size all 0

# Cursor
cursor_shape block
cursor_blink_interval 0

# Performance
repaint_delay 10
input_delay 3
sync_to_monitor yes
```

- [ ] **Step 3: Verify kitty.conf created**

Run:
```bash
test -f ~/.config/kitty/kitty.conf && echo "kitty.conf created" || echo "kitty.conf NOT created"
```

Expected: Output `kitty.conf created`

---

## Task 9: Create Starship Configuration

**Files:**
- Create: `~/.config/starship.toml`

- [ ] **Step 1: Generate Tokyo Night preset**

Run:
```bash
starship preset tokyo-night -o ~/.config/starship.toml
```

Expected: Starship generates config file with Tokyo Night theme

- [ ] **Step 2: Verify starship.toml created**

Run:
```bash
test -f ~/.config/starship.toml && echo "starship.toml created" || echo "starship.toml NOT created"
```

Expected: Output `starship.toml created`

- [ ] **Step 3: Customize config for single-line compact mode**

Append to `~/.config/starship.toml`:

```toml
# Custom overrides
format = """
[┌](bold green) $directory$git_branch$git_status$nodejs$python$rust$time
[└](bold green) $character"""

[character]
success_symbol = "[➜](bold green)"
error_symbol = "[✗](bold red)"

[directory]
truncation_length = 3
truncate_to_repo = true
format = "[$path]($style)[$read_only]($read_only_style) "

[git_branch]
format = "on [$symbol$branch]($style) "

[git_status]
format = '([\[$all_status$ahead_behind\]]($style) )'

[time]
disabled = false
format = "[$time]($style) "
time_format = "%T"

[cmd_duration]
min_time = 500
format = "took [$duration]($style) "
```

- [ ] **Step 4: Verify customization applied**

Run:
```bash
grep -q "Custom overrides" ~/.config/starship.toml && echo "Customization applied" || echo "Customization NOT applied"
```

Expected: Output `Customization applied`

---

## Task 10: Create Zsh Exports Module

**Files:**
- Create: `~/.config/zsh/exports.zsh`

- [ ] **Step 1: Create zsh config directory**

Run:
```bash
mkdir -p ~/.config/zsh
```

Expected: Directory created

- [ ] **Step 2: Write exports.zsh**

Create file `~/.config/zsh/exports.zsh`:

```bash
# Homebrew environment
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null || /opt/homebrew/bin/brew shellenv 2>/dev/null || true)"

# Default editors
export EDITOR="vim"
export VISUAL="vim"

# XDG Base Directory
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_CACHE_HOME="$HOME/.cache"

# Less colors for man pages
export LESS_TERMCAP_mb=$'\e[1;32m'
export LESS_TERMCAP_md=$'\e[1;32m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_se=$'\e[0m'
export LESS_TERMCAP_so=$'\e[01;33m'
export LESS_TERMCAP_ue=$'\e[0m'
export LESS_TERMCAP_us=$'\e[1;4;31m'

# History
export HISTFILE=~/.zsh_history
export HISTSIZE=50000
export SAVEHIST=50000
```

- [ ] **Step 3: Verify exports.zsh created**

Run:
```bash
test -f ~/.config/zsh/exports.zsh && echo "exports.zsh created" || echo "exports.zsh NOT created"
```

Expected: Output `exports.zsh created`

---

## Task 11: Create Zsh Aliases Module

**Files:**
- Create: `~/.config/zsh/aliases.zsh`

- [ ] **Step 1: Write aliases.zsh**

Create file `~/.config/zsh/aliases.zsh`:

```bash
# Modern tool replacements
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first'
alias lt='eza --tree --icons --group-directories-first'
alias cat='bat --style=auto'
alias find='fd'
alias grep='rg'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gaa='git add --all'
alias gc='git commit'
alias gcm='git commit -m'
alias gp='git push'
alias gpl='git pull'
alias gl='git log --oneline --graph --decorate'
alias gd='git diff'
alias gco='git checkout'
alias gb='git branch'
alias gba='git branch -a'

# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias ~='cd ~'
alias -- -='cd -'

# Bazzite system updates
alias update='rpm-ostree upgrade && flatpak update -y && brew upgrade'
alias update-check='rpm-ostree upgrade --check && flatpak remote-ls --updates && brew outdated'

# Docker/Podman
alias dps='docker ps'
alias dpsa='docker ps -a'
alias dimg='docker images'
alias dlog='docker logs -f'
alias dex='docker exec -it'
alias dstop='docker stop'
alias drm='docker rm'
alias drmi='docker rmi'

# Safety nets
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Quick info
alias ports='netstat -tuln'
alias myip='curl -s ifconfig.me'
alias speedtest='curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -'

# Directory listing
alias la='eza -la --icons'
alias l='eza -l --icons'
alias lh='eza -lah --icons'

# System info
alias df='df -h'
alias du='dust'
alias free='free -h'
alias psg='ps aux | grep -v grep | grep -i -e VSZ -e'

# Quick edits
alias zshrc='$EDITOR ~/.zshrc'
alias zshreload='source ~/.zshrc'
alias aliases='$EDITOR ~/.config/zsh/aliases.zsh'
```

- [ ] **Step 2: Verify aliases.zsh created**

Run:
```bash
test -f ~/.config/zsh/aliases.zsh && echo "aliases.zsh created" || echo "aliases.zsh NOT created"
```

Expected: Output `aliases.zsh created`

---

## Task 12: Create Zsh Functions Module

**Files:**
- Create: `~/.config/zsh/functions.zsh`

- [ ] **Step 1: Write functions.zsh**

Create file `~/.config/zsh/functions.zsh`:

```bash
# wtfjusthappen - Show recent system logs and errors
wtfjusthappen() {
    echo "=== Recent System Logs (last 5 minutes) ==="
    journalctl --since "5 minutes ago" --no-pager | tail -50
    echo ""
    echo "=== Recent Kernel Messages ==="
    dmesg -T | tail -50
    echo ""
    echo "=== Recent Failed Services ==="
    systemctl --failed --no-pager
}

# mkcd - Make directory and cd into it
mkcd() {
    if [ -z "$1" ]; then
        echo "Usage: mkcd <directory>"
        return 1
    fi
    mkdir -p "$1" && cd "$1"
}

# extract - Universal archive extractor
extract() {
    if [ -z "$1" ]; then
        echo "Usage: extract <file>"
        return 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "Error: '$1' is not a valid file"
        return 1
    fi
    
    case "$1" in
        *.tar.bz2)   tar xjf "$1"     ;;
        *.tar.gz)    tar xzf "$1"     ;;
        *.tar.xz)    tar xJf "$1"     ;;
        *.bz2)       bunzip2 "$1"     ;;
        *.rar)       unrar x "$1"     ;;
        *.gz)        gunzip "$1"      ;;
        *.tar)       tar xf "$1"      ;;
        *.tbz2)      tar xjf "$1"     ;;
        *.tgz)       tar xzf "$1"     ;;
        *.zip)       unzip "$1"       ;;
        *.Z)         uncompress "$1"  ;;
        *.7z)        7z x "$1"        ;;
        *)           echo "Error: '$1' cannot be extracted via extract()" ;;
    esac
}

# fcd - Fuzzy cd with fzf (if available)
if command -v fzf &> /dev/null; then
    fcd() {
        local dir
        dir=$(find ${1:-.} -type d 2> /dev/null | fzf +m) && cd "$dir"
    }
fi

# Quick directory size
dirsize() {
    dust -d 1 ${1:-.}
}

# Find large files
large() {
    local size=${1:-100M}
    find . -type f -size +$size -exec ls -lh {} \; | awk '{ print $9 ": " $5 }'
}
```

- [ ] **Step 2: Verify functions.zsh created**

Run:
```bash
test -f ~/.config/zsh/functions.zsh && echo "functions.zsh created" || echo "functions.zsh NOT created"
```

Expected: Output `functions.zsh created`

---

## Task 13: Create Zsh Plugins Module

**Files:**
- Create: `~/.config/zsh/plugins.zsh`

- [ ] **Step 1: Write plugins.zsh**

Create file `~/.config/zsh/plugins.zsh`:

```bash
# oh-my-zsh plugins configuration
# These must be loaded by .zshrc BEFORE sourcing oh-my-zsh

# Plugin list
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    colored-man-pages
    command-not-found
)

# zsh-autosuggestions configuration
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=8"
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

# zsh-syntax-highlighting configuration
ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets pattern cursor)

# Colored man pages configuration
export LESS_TERMCAP_mb=$'\e[1;32m'
export LESS_TERMCAP_md=$'\e[1;32m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_se=$'\e[0m'
export LESS_TERMCAP_so=$'\e[01;33m'
export LESS_TERMCAP_ue=$'\e[0m'
export LESS_TERMCAP_us=$'\e[1;4;31m'
```

- [ ] **Step 2: Verify plugins.zsh created**

Run:
```bash
test -f ~/.config/zsh/plugins.zsh && echo "plugins.zsh created" || echo "plugins.zsh NOT created"
```

Expected: Output `plugins.zsh created`

---

## Task 14: Create Main .zshrc

**Files:**
- Create: `~/.zshrc` (overwrites oh-my-zsh default)

- [ ] **Step 1: Backup existing .zshrc**

Run:
```bash
if [ -f ~/.zshrc ]; then cp ~/.zshrc ~/.zshrc.backup-$(date +%Y%m%d-%H%M%S); fi
```

Expected: Backup created with timestamp

- [ ] **Step 2: Write new .zshrc**

Create file `~/.zshrc`:

```bash
# oh-my-zsh configuration
export ZSH="$HOME/.oh-my-zsh"

# Disable oh-my-zsh themes (using Starship instead)
ZSH_THEME=""

# Load plugin configuration before oh-my-zsh
source ~/.config/zsh/plugins.zsh

# Initialize oh-my-zsh
source $ZSH/oh-my-zsh.sh

# Load modular configuration
source ~/.config/zsh/exports.zsh
source ~/.config/zsh/aliases.zsh
source ~/.config/zsh/functions.zsh

# Initialize Starship prompt
eval "$(starship init zsh)"

# Initialize zoxide (smart cd)
eval "$(zoxide init zsh)"

# History configuration
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FIND_NO_DUPS
setopt HIST_SAVE_NO_DUPS
setopt SHARE_HISTORY
setopt EXTENDED_HISTORY

# Completion configuration
setopt COMPLETE_IN_WORD
setopt AUTO_MENU
setopt ALWAYS_TO_END

# Directory navigation
setopt AUTO_PUSHD
setopt PUSHD_IGNORE_DUPS
setopt PUSHD_SILENT

# Misc options
setopt CORRECT
setopt INTERACTIVE_COMMENTS
```

- [ ] **Step 3: Verify .zshrc created**

Run:
```bash
test -f ~/.zshrc && echo ".zshrc created" || echo ".zshrc NOT created"
```

Expected: Output `.zshrc created`

---

## Task 15: Disable Bazzite Banner

**Files:**
- Create: `~/.config/no-show-user-motd`

- [ ] **Step 1: Create no-show-user-motd file**

Run:
```bash
touch ~/.config/no-show-user-motd
```

Expected: Empty file created

- [ ] **Step 2: Verify file created**

Run:
```bash
test -f ~/.config/no-show-user-motd && echo "Banner disabled" || echo "Banner NOT disabled"
```

Expected: Output `Banner disabled`

---

## Task 16: Change Default Shell to Zsh

**Files:**
- Modify: System user database (via chsh)

- [ ] **Step 1: Verify zsh is installed**

Run:
```bash
which zsh
```

Expected: Output like `/usr/bin/zsh` or `/bin/zsh`

- [ ] **Step 2: Change default shell**

Run:
```bash
chsh -s $(which zsh)
```

Expected: Password prompt, then "Shell changed"

Note: Change takes effect after logout/login

- [ ] **Step 3: Verify shell change recorded**

Run:
```bash
grep "^$USER:" /etc/passwd | cut -d: -f7
```

Expected: Output shows zsh path

---

## Task 17: Verification - Test Starship Prompt

**Files:**
- Test: Starship prompt appears in new shell

- [ ] **Step 1: Open new shell session**

Run:
```bash
zsh
```

Expected: New zsh session starts with Starship prompt (colored, with icons)

- [ ] **Step 2: Verify no Bazzite banner appears**

Expected: No "Bazzite" ASCII art or MOTD shown

- [ ] **Step 3: Exit test session**

Run:
```bash
exit
```

Expected: Return to previous shell

---

## Task 18: Verification - Test Modern CLI Tools

**Files:**
- Test: Modern tool aliases work correctly

- [ ] **Step 1: Test ls → eza**

Run in new zsh session:
```bash
zsh -c 'source ~/.zshrc && ls'
```

Expected: Directory listing with icons and colors (eza output)

- [ ] **Step 2: Test cat → bat**

Run in new zsh session:
```bash
zsh -c 'source ~/.zshrc && cat ~/.zshrc | head -5'
```

Expected: Syntax-highlighted output with line numbers

- [ ] **Step 3: Test cd tracking with zoxide**

Run in new zsh session:
```bash
zsh -c 'source ~/.zshrc && cd /tmp && cd - && pwd'
```

Expected: Returns to original directory, zoxide records jump

---

## Task 19: Verification - Test Git Aliases

**Files:**
- Test: Git aliases work correctly

- [ ] **Step 1: Test gs (git status)**

Run in new zsh session:
```bash
zsh -c 'source ~/.zshrc && cd /tmp && git init test-repo && cd test-repo && gs'
```

Expected: Git status output shown

- [ ] **Step 2: Test gl (git log)**

Run in new zsh session:
```bash
zsh -c 'source ~/.zshrc && cd /tmp/test-repo && touch test.txt && git add . && git commit -m "test" && gl'
```

Expected: Git log graph output shown

- [ ] **Step 3: Clean up test repo**

Run:
```bash
rm -rf /tmp/test-repo
```

Expected: Test repo removed

---

## Task 20: Verification - Test wtfjusthappen Function

**Files:**
- Test: wtfjusthappen function shows system logs

- [ ] **Step 1: Test wtfjusthappen**

Run in new zsh session:
```bash
zsh -c 'source ~/.zshrc && wtfjusthappen'
```

Expected: Three sections output:
1. Recent System Logs (journalctl)
2. Recent Kernel Messages (dmesg)
3. Recent Failed Services (systemctl --failed)

- [ ] **Step 2: Verify output contains data**

Expected: At least journalctl and dmesg sections show log entries (may be empty if system quiet)

---

## Task 21: Verification - Test kitty Configuration

**Files:**
- Test: kitty loads with Tokyo Night theme and FiraCode font

- [ ] **Step 1: Launch kitty terminal**

Run:
```bash
kitty &
```

Expected: New kitty window opens

- [ ] **Step 2: Verify Tokyo Night colors**

Visual check: Background should be dark blue-gray (#1a1b26), text light blue-white

- [ ] **Step 3: Verify FiraCode Nerd Font renders icons**

Run in kitty window:
```bash
echo " "
```

Expected: Icons render correctly (not boxes/question marks)

- [ ] **Step 4: Close test kitty window**

Expected: Window closes

---

## Task 22: Final Verification - Full Terminal Session

**Files:**
- Test: Complete terminal experience in kitty with zsh

- [ ] **Step 1: Launch kitty and verify shell**

Open kitty terminal, run:
```bash
echo $SHELL
```

Expected: Output shows zsh path

Note: If output shows bash, logout/login required for shell change

- [ ] **Step 2: Verify Starship prompt appears**

Expected: Prompt shows directory, git info (if in repo), with icons and colors

- [ ] **Step 3: Test navigation aliases**

Run:
```bash
cd /tmp && .. && pwd
```

Expected: Returns to home directory

- [ ] **Step 4: Test update alias**

Run:
```bash
update-check
```

Expected: Shows available updates for rpm-ostree, flatpak, and brew

- [ ] **Step 5: Verify completion and syntax highlighting**

Type (don't run):
```bash
git st
```

Expected: Command syntax-highlighted in red (invalid), suggestions appear

---

## Task 23: Documentation - Record Installation

**Files:**
- Create: Installation record or commit message

- [ ] **Step 1: Create installation notes**

Optional: Create `~/.config/terminal-rice-install-notes.txt`:

```text
Terminal Rice Setup Completed: $(date)

Installed components:
- kitty terminal emulator
- Starship prompt
- oh-my-zsh with plugins: git, zsh-autosuggestions, zsh-syntax-highlighting
- Modern CLI tools: eza, bat, fd, ripgrep, zoxide, dust
- FiraCode Nerd Font

Configuration files:
- ~/.config/kitty/kitty.conf
- ~/.config/starship.toml
- ~/.config/zsh/{exports,aliases,functions,plugins}.zsh
- ~/.zshrc

Theme: Tokyo Night
```

- [ ] **Step 2: Verify all config files exist**

Run:
```bash
ls -la ~/.config/kitty/kitty.conf ~/.config/starship.toml ~/.config/zsh/*.zsh ~/.zshrc
```

Expected: All files listed with sizes

---

## Post-Installation Notes

**Shell activation:** If verification Task 22 Step 1 shows bash instead of zsh, the shell change requires logout/login. Run:
```bash
logout
```

Then log back in. New sessions will use zsh.

**kitty as default terminal:** To set kitty as default terminal on KDE Plasma:
1. Open System Settings
2. Navigate to Applications → Default Applications
3. Set Terminal to kitty

**Homebrew updates:** Run `brew update && brew upgrade` periodically, or use the `update` alias which updates all package managers.

**Customization:** All configs live in `~/.config/`. Edit individual zsh modules in `~/.config/zsh/` then run `zshreload` to apply changes.
