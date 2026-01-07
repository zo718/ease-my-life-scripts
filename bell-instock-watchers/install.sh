#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DIR="/etc/systemd/system"
WATCHER_SERVICE="bell_cheekpad_watcher.service"
WATCHER_TIMER="bell_cheekpad_watcher.timer"
HEALTH_SERVICE="bell_cheekpad_healthcheck.service"
HEALTH_TIMER="bell_cheekpad_healthcheck.timer"

GMAIL_ADDRESS="your_email@example.com"
NOTIFY_TO="your_email@example.com"
APP_PASSWORD="REPLACE_WITH_APP_PASSWORD"

echo "Installing Bell instock watcher systemd units from ${SCRIPT_DIR}"
sudo cp "${SCRIPT_DIR}/${WATCHER_SERVICE}" "${UNIT_DIR}/"
sudo cp "${SCRIPT_DIR}/${WATCHER_TIMER}" "${UNIT_DIR}/"
sudo cp "${SCRIPT_DIR}/${HEALTH_SERVICE}" "${UNIT_DIR}/"
sudo cp "${SCRIPT_DIR}/${HEALTH_TIMER}" "${UNIT_DIR}/"

echo "Creating systemd drop-ins for credentials"
sudo mkdir -p "${UNIT_DIR}/${WATCHER_SERVICE}.d"
sudo tee "${UNIT_DIR}/${WATCHER_SERVICE}.d/override.conf" >/dev/null <<EOF
[Service]
Environment=GMAIL_ADDRESS=${GMAIL_ADDRESS}
Environment=NOTIFY_TO=${NOTIFY_TO}
Environment=GMAIL_APP_PASSWORD=${APP_PASSWORD}
EOF

sudo mkdir -p "${UNIT_DIR}/${HEALTH_SERVICE}.d"
sudo tee "${UNIT_DIR}/${HEALTH_SERVICE}.d/override.conf" >/dev/null <<EOF
[Service]
Environment=GMAIL_ADDRESS=${GMAIL_ADDRESS}
Environment=NOTIFY_TO=${NOTIFY_TO}
Environment=GMAIL_APP_PASSWORD=${APP_PASSWORD}
EOF

echo "Reloading systemd and enabling timers"
sudo systemctl daemon-reload
sudo systemctl enable --now bell_cheekpad_watcher.timer
sudo systemctl enable --now bell_cheekpad_healthcheck.timer

echo "Done. Update APP_PASSWORD in ${SCRIPT_DIR}/install.sh and re-run if needed."
