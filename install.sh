#!/bin/sh
# Tiger Open API Python SDK — One-line Installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/tigerfintech/openapi-python-sdk/master/install.sh | sh
#   wget -qO- https://raw.githubusercontent.com/tigerfintech/openapi-python-sdk/master/install.sh | sh
#
# Options (via environment variables):
#   TIGEROPEN_NO_MODIFY_PATH=1  — skip PATH modification
#   TIGEROPEN_INSTALL_METHOD=uv — force install method (uv|pipx|pip)

{

set -e

# ─── Colors (only when output is a terminal) ────────────────────────────────

if [ -t 1 ] && [ "${TERM+set}" = 'set' ]; then
    bold=$(tput bold 2>/dev/null || true)
    green=$(tput setaf 2 2>/dev/null || true)
    yellow=$(tput setaf 3 2>/dev/null || true)
    red=$(tput setaf 1 2>/dev/null || true)
    cyan=$(tput setaf 6 2>/dev/null || true)
    reset=$(tput sgr0 2>/dev/null || true)
else
    bold='' green='' yellow='' red='' cyan='' reset=''
fi

info()  { printf '%s\n' "${green}info${reset}: $*"; }
warn()  { printf '%s\n' "${yellow}warn${reset}: $*" >&2; }
error() { printf '%s\n' "${red}error${reset}: $*" >&2; exit 1; }

# ─── Utility ─────────────────────────────────────────────────────────────────

has_cmd() { command -v "$1" > /dev/null 2>&1; }

need_cmd() {
    if ! has_cmd "$1"; then
        error "required command '$1' not found"
    fi
}

# ─── Banner ──────────────────────────────────────────────────────────────────

printf '%s\n' ""
printf '%s\n' "${bold}  Tiger Open API Python SDK Installer${reset}"
printf '%s\n' "  ─────────────────────────────────────"
printf '%s\n' ""

# ─── OS Detection ────────────────────────────────────────────────────────────

OS=$(uname -s)
case "$OS" in
    Linux*)  OS="linux" ;;
    Darwin*) OS="macos" ;;
    MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
    *)       warn "unrecognized OS: $OS — proceeding anyway" ;;
esac

# ─── Python Detection ───────────────────────────────────────────────────────

PYTHON=""
for candidate in python3 python; do
    if has_cmd "$candidate"; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    error "Python not found. Install Python 3.8+ first:
  macOS:   brew install python3
  Ubuntu:  sudo apt install python3 python3-pip
  Fedora:  sudo dnf install python3 python3-pip
  Website: https://www.python.org/downloads/"
fi

# Check Python version (need 3.8+)
PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null) || true
PY_MAJOR=$("$PYTHON" -c "import sys; print(sys.version_info.major)" 2>/dev/null) || true
PY_MINOR=$("$PYTHON" -c "import sys; print(sys.version_info.minor)" 2>/dev/null) || true

if [ -z "$PY_VERSION" ]; then
    error "could not determine Python version"
fi

if [ "$PY_MAJOR" -lt 3 ] 2>/dev/null || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; } 2>/dev/null; then
    error "Python 3.8+ required, found $PY_VERSION"
fi

info "found Python ${cyan}${PY_VERSION}${reset} (${PYTHON})"

# ─── Choose Install Method ───────────────────────────────────────────────────

METHOD="${TIGEROPEN_INSTALL_METHOD:-}"

if [ -z "$METHOD" ]; then
    if has_cmd uv; then
        METHOD="uv"
    elif has_cmd pipx; then
        METHOD="pipx"
    else
        METHOD="pip"
    fi
fi

info "install method: ${cyan}${METHOD}${reset}"

# ─── Install ─────────────────────────────────────────────────────────────────

case "$METHOD" in
    uv)
        need_cmd uv
        info "installing tigeropen via uv..."
        uv pip install tigeropen --upgrade 2>&1
        BIN_DIR=$(uv pip show tigeropen 2>/dev/null | grep -i "^Location" | head -1 | awk '{print $2}' || true)
        ;;
    pipx)
        need_cmd pipx
        info "installing tigeropen via pipx..."
        pipx install tigeropen --force 2>&1
        ;;
    pip)
        info "installing tigeropen via pip..."
        "$PYTHON" -m pip install tigeropen --upgrade 2>&1
        ;;
    *)
        error "unknown install method: $METHOD (use uv, pipx, or pip)"
        ;;
esac

# ─── Verify Installation ────────────────────────────────────────────────────

TIGEROPEN_BIN=""
if has_cmd tigeropen; then
    TIGEROPEN_BIN=$(command -v tigeropen)
fi

# If not on PATH yet, check common locations
if [ -z "$TIGEROPEN_BIN" ]; then
    for dir in \
        "$HOME/.local/bin" \
        "$HOME/Library/Python/${PY_VERSION}/bin" \
        "$HOME/.local/share/pipx/venvs/tigeropen/bin" \
        ; do
        if [ -x "$dir/tigeropen" ]; then
            TIGEROPEN_BIN="$dir/tigeropen"
            break
        fi
    done
fi

if [ -z "$TIGEROPEN_BIN" ]; then
    warn "tigeropen installed but CLI binary not found on PATH"
    warn "you may need to add pip's bin directory to your PATH"
else
    info "CLI installed at: ${cyan}${TIGEROPEN_BIN}${reset}"
fi

# ─── Verify import ──────────────────────────────────────────────────────────

SDK_VERSION=$("$PYTHON" -c "from tigeropen import __VERSION__; print(__VERSION__)" 2>/dev/null) || true
if [ -z "$SDK_VERSION" ]; then
    error "installation failed — could not import tigeropen"
fi

info "tigeropen ${cyan}v${SDK_VERSION}${reset} installed successfully"

# ─── PATH Setup ─────────────────────────────────────────────────────────────

if [ -n "$TIGEROPEN_BIN" ] && [ "${TIGEROPEN_NO_MODIFY_PATH:-}" != "1" ]; then
    BIN_DIR=$(dirname "$TIGEROPEN_BIN")

    # Check if already on PATH
    case ":$PATH:" in
        *":$BIN_DIR:"*) ;;  # already on PATH
        *)
            # Detect shell and rc file
            CURRENT_SHELL=$(basename "${SHELL:-/bin/sh}")
            RC_FILE=""
            case "$CURRENT_SHELL" in
                zsh)  RC_FILE="$HOME/.zshrc" ;;
                bash)
                    if [ -f "$HOME/.bashrc" ]; then
                        RC_FILE="$HOME/.bashrc"
                    elif [ -f "$HOME/.bash_profile" ]; then
                        RC_FILE="$HOME/.bash_profile"
                    else
                        RC_FILE="$HOME/.profile"
                    fi
                    ;;
                fish) RC_FILE="$HOME/.config/fish/config.fish" ;;
                *)    RC_FILE="$HOME/.profile" ;;
            esac

            PATH_LINE="export PATH=\"$BIN_DIR:\$PATH\""
            if [ "$CURRENT_SHELL" = "fish" ]; then
                PATH_LINE="set -gx PATH $BIN_DIR \$PATH"
            fi

            if [ -n "$RC_FILE" ]; then
                if [ -f "$RC_FILE" ] && grep -qF "$BIN_DIR" "$RC_FILE" 2>/dev/null; then
                    : # already in rc file
                else
                    printf '\n# Added by tigeropen installer\n%s\n' "$PATH_LINE" >> "$RC_FILE"
                    info "added ${cyan}${BIN_DIR}${reset} to PATH in ${cyan}${RC_FILE}${reset}"
                fi
            fi

            # Also handle GitHub Actions
            if [ -n "${GITHUB_PATH:-}" ]; then
                printf '%s\n' "$BIN_DIR" >> "$GITHUB_PATH"
            fi
            ;;
    esac
fi

# ─── Success Message ─────────────────────────────────────────────────────────

printf '%s\n' ""
printf '%s\n' "${bold}${green}  Installation complete!${reset}"
printf '%s\n' ""
printf '%s\n' "  Getting started:"
printf '%s\n' ""
printf '%s\n' "    ${cyan}# Set up your API credentials${reset}"
printf '%s\n' "    tigeropen config init"
printf '%s\n' ""
printf '%s\n' "    ${cyan}# Or set environment variables${reset}"
printf '%s\n' "    export TIGEROPEN_TIGER_ID=\"your_tiger_id\""
printf '%s\n' "    export TIGEROPEN_PRIVATE_KEY=\"your_private_key\""
printf '%s\n' "    export TIGEROPEN_ACCOUNT=\"your_account\""
printf '%s\n' ""
printf '%s\n' "    ${cyan}# Query market data${reset}"
printf '%s\n' "    tigeropen quote briefs AAPL TSLA"
printf '%s\n' "    tigeropen quote bars AAPL --period day --limit 10"
printf '%s\n' ""
printf '%s\n' "    ${cyan}# Manage orders${reset}"
printf '%s\n' "    tigeropen trade order list"
printf '%s\n' "    tigeropen account assets"
printf '%s\n' ""
printf '%s\n' "  Documentation: ${cyan}https://docs.itigerup.com/docs/${reset}"
printf '%s\n' "  GitHub:        ${cyan}https://github.com/tigerfintech/openapi-python-sdk${reset}"
printf '%s\n' ""

# Remind to restart shell if PATH was modified
if [ -n "${RC_FILE:-}" ] && ! has_cmd tigeropen; then
    printf '%s\n' "  ${yellow}Restart your shell or run:${reset}"
    printf '%s\n' "    source ${RC_FILE}"
    printf '%s\n' ""
fi

}
