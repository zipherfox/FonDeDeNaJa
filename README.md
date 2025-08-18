FonDeDeNaJa 🚀 Rust Edition Available! 🚀
===================
This program is built for validating scores from image input or zip file.

## 🚀 NEW: Memory Safe Rust Implementation 🚀

FonDeDeNaJa now includes a **🚀 Memory Safe 🚀** Rust wrapper that provides the same functionality with enhanced safety and performance!

### Quick Start with Rust

```bash
# Build the Rust edition
make install

# Use the Memory Safe CLI
./fon-de-de-na-ja-rust --help
./fon-de-de-na-ja-rust -i inputs -o outputs --debug
```

**Benefits of the Rust Edition:**
- 🚀 **Memory Safety** - No buffer overflows or memory leaks
- ⚡ **Performance** - ~1.26% faster startup times
- 🛡️ **Reliability** - Compile-time error prevention
- 🔧 **Modern Tooling** - Cargo build system

> See [README_RUST.md](README_RUST.md) for detailed Rust documentation

---

## Original Python Implementation

## Configuration: `resources/developers.csv`

**Variables:**

1. **access**: User access level
    - `1`: Student
    - `2`: Teacher
    - `3`: Administrator
    - `4`: Developer
    - `5`: Administrator and developer (Superadmin)
2. **email**: Your email address
3. **name**: Your name
4. **role**: Your role (e.g., Website Developer)
5. **welcome_message** (optional): Custom welcome message
    - If left empty, a default message defined in 'data/settings.toml' will be used.

**How to use:**

1. Add a new developer by appending a new line with the format:
   ```csv
   access,email,name,role,welcome_message
   ```
   - ⚠️ **If any field contains whitespace, enclose the value in double quotes.**
     For example: `2,dev@example.com,"Jane Doe","Lead Developer","Welcome, Jane!"`
2. Ensure the email is unique to avoid conflicts.
3. The `welcome_message` can be customized for each developer.
4. The CSV file will be read by the application to display developer information.

## Configuration: `settings.toml`

This file will be used for application-wide settings.

**Example:**
```toml
[app]
default_welcome = "Welcome Back Developer! {name} ({role})\nYou are logged in as: {email}"
# Add more configuration variables as needed
```

- Edit `config.toml` to customize default messages and other settings.

---

For more details, see the code or contact the project maintainer.

---

## Deploy: `deploy-app`

A small deployment helper script you can install on a host to build and bring up the project using the current working directory as the project directory.

Recommended `deploy-app` script:

```bash
#!/bin/bash
# deploy-app
# Uses current working directory as project directory
set -euo pipefail

PROJECT_DIR="$(pwd)"
COMPOSE_CMD="docker compose"
LOG_FILE="/var/log/deploy-app.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$DATE] $1" | tee -a "$LOG_FILE"
}
log "Using project directory: $PROJECT_DIR"
ls -l "$PROJECT_DIR/Dockerfile"
main() {
    log "🚀 Starting deployment in $PROJECT_DIR..."

    if [[ ! -f "$PROJECT_DIR/docker-compose.yml" ]]; then
        log "❌ docker-compose.yml not found in $PROJECT_DIR"
        exit 1
    fi

    if [[ ! -f "$PROJECT_DIR/Dockerfile" ]]; then
        log "❌ Dockerfile not found in $PROJECT_DIR"
        exit 1
    fi
    log "📦 Pulling and rebuilding Docker images (if necessary)..."
    $COMPOSE_CMD pull || true
    $COMPOSE_CMD build

    log "📡 Bringing up the application..."
    $COMPOSE_CMD up -d

    log "✅ Deployment completed successfully"
}

main "$@"
```

Installation and usage notes
- Save the script as `/usr/local/bin/deploy-app` and make it executable:

```bash
sudo install -m 0755 deploy-app /usr/local/bin/deploy-app
```

- Then run it from your project directory:

```bash
cd /path/to/project
sudo deploy-app
```

Allowing `deploy-app` via `sudo` (optional)
- If you'd like non-root users to invoke `deploy-app` with `sudo` without a password prompt, add a limited sudoers rule using `visudo`.
  Example (very selective):

```text
# Allow user `deployuser` to run only /usr/local/bin/deploy-app without a password
deployuser ALL=(root) NOPASSWD: /usr/local/bin/deploy-app
```

Edit with `sudo visudo` and place the rule in the file or in a new file under `/etc/sudoers.d/deploy-app`.

Security notes
- Be careful granting passwordless sudo; restrict the allowed command path to the exact script and keep the script secure (root-owned, not writable by others).
- Consider additional safeguards such as checking `$PROJECT_DIR` against an allowlist inside the script, or requiring invocation from a specific directory.


## Host-side image pruning (scripts/prune_images.sh)

This repository includes a small host-side helper script `scripts/prune_images.sh` that
removes older local Docker image tags for the repository while keeping the newest N tags
(default: 2). It's intended to be run on the host where images are stored to reclaim space
but is conservative by default (dry-run) and skips images currently used by running
containers.

Why use it
- Keeps your host tidy by removing older images that are no longer needed for rollbacks.
- Defaults to a safe dry-run; you must explicitly opt-in to destructive deletion.

Basic usage (dry-run, keep 2 newest):
```bash
bash scripts/prune_images.sh --repo ghcr.io/zipherfox/FonDeDeNaJa
```

Delete older images (keep 2 newest):
```bash
bash scripts/prune_images.sh --repo ghcr.io/zipherfox/FonDeDeNaJa --no-dry-run
```

Keep 3 newest and delete older:
```bash
bash scripts/prune_images.sh --repo ghcr.io/zipherfox/FonDeDeNaJa --keep 3 --no-dry-run
```

Notes and safety
- The script defaults the `--repo` to `ghcr.io/zipherfox/FonDeDeNaJa` for this project, so you can run it with no arguments on a host configured for this repo.
- It will not remove images that are in use by running containers.
- Deleting tags from the local Docker engine does not affect remote registries.

Integration with `deploy-app`
- The included `deploy-app` script will offer to run the prune script interactively after a successful deploy when executed from a TTY. The prompt is conservative and runs the prune script in dry-run mode unless you explicitly choose to perform deletion.

Scheduling
- If you want automated pruning on a host, add a cron entry or systemd timer to run the script periodically. See `scripts/prune_images.sh` and `docs/prune_images.md` for details.

"Made by Zipherfox, NessShadow, Film"