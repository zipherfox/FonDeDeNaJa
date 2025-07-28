#!/usr/bin/env bash
# Capture start time
START_TIME=$(date +%s)
# Setup Wizard for FonDeDeNaJa project (Linux shell version)

# ANSI color codes
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BLUE="\033[0;34m"
NC="\033[0m"  # No Color
CHECK_ORIGI=("answer_key.csv" "settings.toml" "user.csv")

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
required_files=("$DATA_DIR/settings.toml" "$TEMPLATES_DIR/data/settings.toml" "$STREAMLIT_DIR/secrets.toml" "$DATA_DIR/user.csv")
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
    read -p "Found required items at default locations. Apply these defaults instead? [Y/N]: " apply_ans
    if [[ "$apply_ans" =~ ^[Yy] ]]; then
      USE_DEFAULTS=true
      GEN_ENABLED=false
    else
      use_defaults=false
        echo -e "${YELLOW}Continuing with interactive setup.${NC}"
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

if [ "$SKIP_INTERACTIVE" = false ] && [ -z "$GEN_ENABLED" ]; then
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
required_files=("$DATA_DIR/settings.toml" "$TEMPLATES_DIR/data/settings.toml" "$STREAMLIT_DIR/secrets.toml" "$DATA_DIR/user.csv")

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
    echo -e "${GREEN}✔ [DIR OK]${NC}   $d"
  else
    echo -e "${RED}✗ [MISSING DIR]${NC} $d"
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
    if [ "$GEN_ENABLED" = true ]; then
      if [ "$(basename "$f")" = "secrets.toml" ]; then
        echo -e "${CYAN}Please create a secrets.toml manually with your Streamlit authentication secrets (for st.login).${NC}"
        echo -e "See Streamlit docs: ${BLUE}https://docs.streamlit.io/library/advanced-features/secrets-management${NC}"
        missing=true; missing_entries+=("$f")
      else
        mkdir -p "$(dirname "$f")"
        case "$f" in
          *.toml|*.yml) echo "# Default configuration" > "$f" ;;
          *.csv) echo "email,name,role,access,welcome_message" > "$f" ;;
          *) touch "$f" ;;
        esac
        echo -e "${GREEN}✔ [GENERATED]${NC} $f"
      fi
    else
      echo -e "${RED}✗ [MISSING]${NC}  $f"
      missing=true; missing_entries+=("$f")
    fi
  fi
done
# Check if key data files are still default (match template)
default_warn=()
for fname in "${CHECK_ORIGI[@]}"; do
  data_file="$DATA_DIR/$fname"
  template_file="$TEMPLATES_DIR/data/$fname"
  if [ -f "$data_file" ] && [ -f "$template_file" ]; then
    if diff -q "$data_file" "$template_file" >/dev/null; then
      default_warn+=("$fname")
    fi
  fi
done
if [ ${#default_warn[@]} -gt 0 ]; then
  echo -e "${YELLOW}[🛈 INFO]${NC} The following files in your data directory are still identical to their default templates:"
  for f in "${default_warn[@]}"; do
    echo -e "  - $f"
  done
  echo -e "${YELLOW}Consider editing these files to customize your configuration.${NC}"
fi

# Final summary
if [ "$missing" = true ]; then
  echo -e "\n${RED}[ERROR]${NC} Some required files or directories are missing:"
  for item in "${missing_entries[@]}"; do
    echo -e " - $item"
  done
  echo -e "\nPlease create or restore the above items before continuing."
  # Calculate and show task duration and exit code
  EXIT_CODE=1
  END_TIME=$(date +%s)
  ELAPSED=$((END_TIME - START_TIME))
  echo -e "\n${BLUE}Task completed in ${ELAPSED}s. Exit code: $EXIT_CODE${NC}"
  exit $EXIT_CODE
fi

# Final success message with "mad" factor
# Show settings.toml only if all checks passed and not mad
if [ "$mad" = true ]; then
  echo -e "\n${RED}All checks passed. Jeez I'm not paid enough for this s***!${NC}"
else
  echo -e "\n${GREEN}✔ All checks passed. Your environment looks good!${NC}"
  # Show contents of settings.toml
  SETTINGS_TOML_PATH="$DATA_DIR/settings.toml"
  if [ -f "$SETTINGS_TOML_PATH" ]; then
    echo -e "\n${CYAN}Contents of $SETTINGS_TOML_PATH (Your settings):${NC}"
    cat "$SETTINGS_TOML_PATH"
  else
    # Hopefully this won't happen since we checked earlier
    echo -e "\n${RED}settings.toml not found at $SETTINGS_TOML_PATH${NC}"
  fi
  # Show a random gimmick
  rand=$((RANDOM % ${#gimmicks[@]}))
  echo -e "${CYAN}- ${gimmicks[$rand]} -${NC}"
fi
# Check for sudo/root or docker group membership
CAN_DOCKER=false
if [ "$EUID" -eq 0 ]; then
  CAN_DOCKER=true
elif groups "$USER" 2>/dev/null | grep -q '\bdocker\b'; then
  CAN_DOCKER=true
elif sudo -n true 2>/dev/null; then
  CAN_DOCKER=true
fi

# Offer to run docker compose if possible, otherwise always attempt deploy-app
if [ "$CAN_DOCKER" = true ]; then
  echo -e "\n${CYAN}[INFO] You have sufficient privileges to run Docker Compose.${NC}"
  read -p "Would you like to run 'docker compose up -d' now? [Y/N]: " docker_ans
  if [[ "$docker_ans" =~ ^[Yy] ]]; then
    echo -e "${BLUE}Attempting to start Docker Compose...${NC}"
    if command -v docker-compose >/dev/null 2>&1; then
      sudo docker-compose up -d
    else
      sudo docker compose up -d
    fi
    DOCKER_EXIT=$?
    if [ $DOCKER_EXIT -eq 0 ]; then
      echo -e "${GREEN}Docker Compose started successfully.${NC}"
      DOCKER_OR_DEPLOYED=true
    else
      echo -e "${RED}Docker Compose failed to start."
    fi
  fi
fi

# Always attempt deploy-app if not already deployed by docker compose
if [ -z "$DOCKER_OR_DEPLOYED" ]; then
  echo -e "${BLUE}Attempting to run 'sudo deploy-app' for non-root/service account deployment...${NC}"
  FALLBACK_FAILED=false
  if command -v deploy-app >/dev/null 2>&1; then
    sudo deploy-app
    DEPLOY_EXIT=$?
    if [ $DEPLOY_EXIT -eq 0 ]; then
      echo -e "${GREEN}Fallback 'deploy-app' ran successfully.${NC}"
    else
      echo -e "${RED}Fallback 'deploy-app' failed. Please check your deployment setup.${NC}"
      FALLBACK_FAILED=true
    fi
  else
    echo -e "${RED}Fallback 'deploy-app' not found in PATH.${NC}"
    FALLBACK_FAILED=true
  fi
  if [ "$FALLBACK_FAILED" = true ]; then
    echo -e "\n${YELLOW}[INFO] If this is your service account, You can add make a script that use docker compose up -d with sudo permissions and edit your sudoers file to allow running it without a password. This script will try deploy-app for you.${NC}"
  fi
fi

# Calculate and show task duration and exit code
EXIT_CODE=0
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo -e "\n${BLUE}Task completed in ${ELAPSED}s. Exit code: $EXIT_CODE${NC}"
exit $EXIT_CODE
# End of setup script
