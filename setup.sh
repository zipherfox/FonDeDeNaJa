#!/usr/bin/env bash
# Setup Wizard for FonDeDeNaJa project (Linux shell version)

# ANSI color codes
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BLUE="\033[0;34m"
NC="\033[0m"  # No Color
  
# Gimmicks messages (for fun!)
gimmicks=(
  "Asking docker if it can get your app to space"
  "Asking Fuji to receive Zipher's Steam gifts"
  "Bond, James Bond"
  "She sells sea shells by the shea sho DAMMIT!"
  "Why are you gay? -w- Does that make you gay???"
)

# Parse script flags
SKIP_INTERACTIVE=false
for arg in "$@"; do
  case $arg in
    --skip-interactive|-s)
      SKIP_INTERACTIVE=true; shift;;
  esac
done
# Load environment variables from .env if present
if [ -f ".env" ]; then
  # shellcheck disable=SC1091
  source .env
fi

# Default directories from env or hardcoded
DATA_DIR="${DATA_DIR:-data}"
IMG_DIR="${IMAGE_DIR:-img}"
TEMPLATES_DIR="${TEMPLATES_DIR:-templates}"
STREAMLIT_DIR="${STREAMLIT_DIR:-.streamlit}"
APP_DIR="${APP_DIR:-app}"

# Auto-detect defaults: if all required dirs/files exist, offer to use them
USE_DEFAULTS=false
required_dirs=("$APP_DIR" "$APP_DIR/pages" "$DATA_DIR" "$TEMPLATES_DIR" "$IMG_DIR" "$STREAMLIT_DIR")
required_files=("$DATA_DIR/settings.yaml" "$TEMPLATES_DIR/settings.yaml" "$STREAMLIT_DIR/secrets.toml" "$DATA_DIR/user.csv")
if [ "$SKIP_INTERACTIVE" = false ]; then
  all_present=true
  for d in "${required_dirs[@]}"; do
    if [ ! -d "$d" ]; then all_present=false; break; fi
  done
  if [ "$all_present" = true ]; then
    for f in "${required_files[@]}"; do
      if [ ! -f "$f" ]; then all_present=false; break; fi
    done
  fi
  if [ "$all_present" = true ]; then
    read -p "All required items found at default locations. Apply these defaults? [Y/N]: " apply_ans
    if [[ "$apply_ans" =~ ^[Yy] ]]; then
      USE_DEFAULTS=true
    fi
  fi
fi

if [ "$SKIP_INTERACTIVE" = false ] && [ "$USE_DEFAULTS" = false ]; then
  # Interactive prompts for custom paths
  echo -e "=== Interactive Setup ==="
  echo -e "(Leave blank to use the default shown in [brackets])"
  read -p "Data directory [${DATA_DIR}]: " input && [ -n "$input" ] && DATA_DIR="$input"
  read -p "Image directory [${IMG_DIR}]: " input && [ -n "$input" ] && IMG_DIR="$input"
  read -p "Templates directory [${TEMPLATES_DIR}]: " input && [ -n "$input" ] && TEMPLATES_DIR="$input"
  read -p "Streamlit directory [${STREAMLIT_DIR}]: " input && [ -n "$input" ] && STREAMLIT_DIR="$input"
  read -p "App directory [${APP_DIR}]: " input && [ -n "$input" ] && APP_DIR="$input"
else
  # Non-interactive: skip prompts
  GEN_ENABLED=false
fi

if [ "$SKIP_INTERACTIVE" = false ]; then
  # Prompt for auto-generation with a 'mad' flag on invalid entries
  mad=false
  while true; do
    read -p "Auto-generate missing files and directories? [Y/N]: " gen_ans
    case "$gen_ans" in
      [Yy]) GEN_ENABLED=true; break;;
      [Nn]) GEN_ENABLED=false; break;;
      "") echo -e "${YELLOW}Please enter Y or N.${NC}";;
      *) echo -e "${RED}I ASKED Y OR N GODDAMMIT. HOW IS IT SO HARD TO UNDERSTAND SUCH A SIMPLE INSTRUCTION!${NC}"; mad=true;;
    esac
  done
fi

# Required items
required_dirs=("$APP_DIR" "$APP_DIR/pages" "$DATA_DIR" "$TEMPLATES_DIR" "$IMG_DIR" "$STREAMLIT_DIR")
required_files=("$DATA_DIR/settings.yaml" "$TEMPLATES_DIR/settings.yaml" "$STREAMLIT_DIR/secrets.toml" "$DATA_DIR/user.csv")

# Summary of used paths
echo -e "\nUsing paths:"
echo -e " • data: $DATA_DIR"
echo -e " • img: $IMG_DIR"
echo -e " • templates: $TEMPLATES_DIR"
echo -e " • streamlit: $STREAMLIT_DIR"
echo -e " • app: $APP_DIR\n"

missing=false
missing_entries=()

# Check directories
echo -e "Checking required directories:"
for d in "${required_dirs[@]}"; do
  if [ -d "$d" ]; then
    echo -e "${GREEN}✔ [OK DIR]${NC}   $d"
  else
    echo -e "${YELLOW}✗ [MISSING DIR]${NC} $d"
    if [ "$GEN_ENABLED" = true ]; then
      if mkdir -p "$d"; then
        echo -e "${GREEN}✔ [CREATED DIR]${NC} $d"
      else
        echo -e "${RED}✗ [ERROR]${NC} Could not create directory $d"
        missing=true; missing_entries+=("$d")
      fi
    else
      missing=true; missing_entries+=("$d")
    fi
  fi
done

# Check files
echo -e "\nChecking required files:"
for f in "${required_files[@]}"; do
  if [ -f "$f" ]; then
    echo -e "${GREEN}✔ [OK]${NC}       $f"
  else
    echo -e "${YELLOW}✗ [MISSING]${NC} $f"
    if [ "$GEN_ENABLED" = true ]; then
      if [ "$(basename "$f")" = "secrets.toml" ]; then
        echo -e "${CYAN}Please create a secrets.toml manually with your Streamlit authentication secrets (for st.login).${NC}"
        echo -e "See Streamlit docs: ${BLUE}https://docs.streamlit.io/library/advanced-features/secrets-management${NC}"
        missing=true; missing_entries+=("$f")
      else
        mkdir -p "$(dirname "$f")"
        case "$f" in
          *.yaml|*.yml) echo "# Default configuration" > "$f" ;;
          *.csv) echo "email,name,role,access,welcome_message" > "$f" ;;
          *) touch "$f" ;;
        esac
        echo -e "${GREEN}✔ [GENERATED]${NC} $f"
      fi
    else
      missing=true; missing_entries+=("$f")
    fi
  fi
done

# Final summary
if [ "$missing" = true ]; then
  echo -e "\nSome required files or directories are missing:"
  for item in "${missing_entries[@]}"; do
    echo -e " - $item"
  done
  echo -e "\nPlease create or restore the above items before continuing."
  exit 1
fi

# Final success message with "mad" factor
if [ "$mad" = true ]; then
  echo -e "\n${RED}All checks passed. Jeez I'm not paid enough for this s***!${NC}"
else
  echo -e "\n${GREEN}✔ All checks passed. Your environment looks good!${NC}"
  # Show a random gimmick
  rand=$((RANDOM % ${#gimmicks[@]}))
  echo -e "${CYAN}- ${gimmicks[$rand]} -${NC}"
fi
exit 0
