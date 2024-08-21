#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

DAEMON_JSON="${1:-/etc/docker/daemon.json}"
BACKUP_DIR="${2:-/etc/docker/backups}"
DESIRED_CONFIG='{"cdi-spec-dirs": ["/etc/cdi"]}'

# Ensure jq is installed
command -v jq >/dev/null 2>&1 || { echo "Error: jq is not installed. Please install it first."; exit 1; }

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create empty JSON object if file doesn't exist
[ -f "$DAEMON_JSON" ] || echo '{}' > "$DAEMON_JSON"

# Create a timestamped backup
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="${BACKUP_DIR}/daemon_${timestamp}.json"
cp "$DAEMON_JSON" "$backup_file"

# Check if the desired configuration already exists
if jq -e ". + $DESIRED_CONFIG == ." "$DAEMON_JSON" >/dev/null 2>&1; then
    echo "Configuration already up to date. No changes needed."
    rm "$backup_file"  # Remove the unnecessary backup
    exit 0
fi

# Update the daemon.json file with a top-level merge
if ! jq ". + $DESIRED_CONFIG" "$DAEMON_JSON" > "$DAEMON_JSON.tmp"; then
    echo "Error: jq command failed. Possible invalid JSON in daemon.json"
    exit 1
fi
mv "$DAEMON_JSON.tmp" "$DAEMON_JSON"

# Validate the JSON
jq empty "$DAEMON_JSON" 2>/dev/null || { echo "Error: Invalid JSON in updated daemon.json."; exit 1; }

echo "daemon.json updated successfully"
systemctl restart docker || { echo "Error: Failed to restart Docker"; exit 1; }

# Clean up backup files
rm "$backup_file"
echo "Backup file removed"

echo "Script completed successfully"
exit 0