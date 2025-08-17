# Host-side Docker image pruning

This document describes the host-side pruning script `scripts/prune_images.sh` which
keeps the N newest image tags for a repository and removes older tags that are not in use
by running containers.

Usage

```bash
# Dry-run (default) keeping 2 newest tags
# Example for this repo using GitHub Container Registry (adjust registry if you use Docker Hub)
./scripts/prune_images.sh --repo ghcr.io/zipherfox/FonDeDeNaJa

# Keep 3 newest, actually delete
./scripts/prune_images.sh --repo ghcr.io/zipherfox/FonDeDeNaJa --keep 3 --no-dry-run
```

Design notes

- The script lists images for the repository and sorts them by creation time (newest first).
- It preserves the `KEEP` newest images (default 2). This matches the "latest + previous"
  behavior commonly desired for rollback.
- It skips removal of any image tag that is currently used by a running container.
- The default `--no-dry-run` flag is required to perform destructive deletes; by default the
  script is safe and only prints what it would remove.

Recommended scheduling

If you want this to run periodically on a host, you can add a cron job or systemd timer.
Example cron (runs daily at 2:30am):

```
30 2 * * * /workspaces/FonDeDeNaJa/scripts/prune_images.sh --repo ghcr.io/OWNER/REPO --no-dry-run >> /var/log/docker-prune.log 2>&1
```

Caveats

- Deleting tags from the local Docker engine does not affect remote registries.
- Some registries require garbage collection to free storage after deleting tags.
- Avoid running this at the exact same time as deploys; consider lock or CI-coordination to
  avoid race conditions where a newly-pushed image might be pruned.

Safety checklist

- Run with `--repo` set and without `--no-dry-run` first to verify output.
- Ensure your deployment system references images by immutable tag (SHA) or uses the
  promoted `latest` tag logic described in your CI.

