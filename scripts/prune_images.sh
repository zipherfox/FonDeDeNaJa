#!/usr/bin/env bash
# Prune Docker images for a repository on the host, keeping the N newest images (default 2).
# Safely skips images currently used by running containers.

set -euo pipefail

REPO="ghcr.io/zipherfox/FonDeDeNaJa"
KEEP=2
DRY_RUN=1

usage() {
  cat <<EOF
Usage: $0 --repo <repository> [--keep N] [--no-dry-run]

Examples:
  $0 --repo ghcr.io/owner/repo           # dry-run, keep 2 newest
  $0 --repo myrepo/app --keep 3 --no-dry-run

This script removes image tags for the given repository, keeping the newest N tags and
skipping any tags that are currently referenced by running containers.
EOF
}

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2;;
    --keep)
      KEEP="$2"; shift 2;;
    --no-dry-run)
      DRY_RUN=0; shift 1;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2; usage; exit 2;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "Error: repo is empty. Pass --repo if you want a different repository." >&2
  usage
  exit 2
fi

echo "Repo: $REPO"
echo "Keep: $KEEP"
echo "Dry run: ${DRY_RUN}" 

# List images for repo sorted by created date (newest first)
# Format: <repo>:<tag>\t<createdAt>
mapfile -t lines < <(docker image ls --format '{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}' "$REPO" | grep -v ':<none>' | sort -r -k2)

if [[ ${#lines[@]} -eq 0 ]]; then
  echo "No images found for ${REPO}"
  exit 0
fi

count=0
for entry in "${lines[@]}"; do
  tag=$(echo "$entry" | awk -F"\t" '{print $1}')
  # Some tags may be like repo:latest or repo:sha
  count=$((count+1))
  if [[ $count -le $KEEP ]]; then
    echo "Keeping ($count) $tag"
    continue
  fi

  # skip if a running container uses this image
  if docker ps --filter "ancestor=$tag" --format '{{.ID}}' | grep -q .; then
    echo "Skipping $tag (in use by running container)"
    continue
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[DRY-RUN] Would remove $tag"
  else
    echo "Removing $tag"
    if docker rmi "$tag"; then
      echo "Removed $tag"
    else
      echo "Failed to remove $tag (may be in use or already gone)" >&2
    fi
  fi
done

echo "Done." 
