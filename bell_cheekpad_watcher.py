#!/usr/bin/env python3
# Bell cheek pad watcher
# - Runs as a oneshot systemd service + timer (see companion .service/.timer files).
# - Configure credentials via a systemd drop-in instead of hardcoding in the service:
#   sudo mkdir -p /etc/systemd/system/bell_cheekpad_watcher.service.d
#   sudo nano /etc/systemd/system/bell_cheekpad_watcher.service.d/override.conf
#   [Service]
#   Environment=GMAIL_ADDRESS=alfredo.jo82@gmail.com
#   Environment=NOTIFY_TO=alfredo.jo82@gmail.com
#   Environment=GMAIL_APP_PASSWORD=your_app_password_here
# - Manual test:
#   GMAIL_ADDRESS=alfredo.jo82@gmail.com NOTIFY_TO=alfredo.jo82@gmail.com \
#   GMAIL_APP_PASSWORD='your_app_password_here' python3 bell_cheekpad_watcher.py
import argparse
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.request import Request, urlopen


PRODUCT_URL = (
    "https://www.bellhelmets.com/product/bullitt-gt-cheek-pads/"
    "250080000500000022.html?dwvar_250080000500000022_color=0023"
)
TARGET_TEXT = "25MM M-L"

UNAVAILABLE_MARKERS = [
    "out of stock",
    "sold out",
    "unavailable",
    "notify me",
    "email me when available",
    "backordered",
]
AVAILABLE_MARKERS = [
    "add to cart",
    "in stock",
    "buy now",
]


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def evaluate_availability(html: str) -> str:
    normalized = normalize(html)
    for marker in UNAVAILABLE_MARKERS:
        if marker in normalized:
            return "unavailable"
    for marker in AVAILABLE_MARKERS:
        if marker in normalized:
            return "available"
    return "unknown"


def send_email(subject: str, body: str, sender: str, recipient: str, app_password: str) -> None:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls(context=context)
        smtp.login(sender, app_password)
        smtp.send_message(msg)


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def append_log(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Bell cheek pad availability.")
    parser.add_argument("--url", default=PRODUCT_URL)
    parser.add_argument("--target-text", default=TARGET_TEXT)
    parser.add_argument("--state-file", default="bell_cheekpad_watcher_state.json")
    parser.add_argument("--log-file", default="bell_cheekpad_watcher.log")
    args = parser.parse_args()

    sender = os.environ.get("GMAIL_ADDRESS")
    recipient = os.environ.get("NOTIFY_TO")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not sender or not recipient or not app_password:
        print("Missing GMAIL_ADDRESS, NOTIFY_TO, or GMAIL_APP_PASSWORD env vars.", file=sys.stderr)
        return 2

    log_path = Path(args.log_file)
    state_path = Path(args.state_file)
    now = datetime.now(timezone.utc).isoformat()

    try:
        html = fetch_html(args.url)
    except Exception as exc:
        append_log(log_path, f"{now} fetch_error {exc}\n")
        return 1

    availability = evaluate_availability(html)
    if args.target_text.lower() not in html.lower():
        append_log(log_path, f"{now} warning target_text_not_found\n")

    state = load_state(state_path)
    last_status = state.get("last_status", "unknown")
    state.update(
        {
            "last_status": availability,
            "last_checked": now,
        }
    )
    save_state(state_path, state)

    if availability == "available" and last_status != "available":
        subject = "Bell Bullitt GT 25MM M-L is available"
        body = (
            "The Bell Bullitt GT 25MM M-L cheek pads appear to be available.\n\n"
            f"Product URL: {args.url}\n"
            f"Checked at: {now}\n"
        )
        send_email(subject, body, sender, recipient, app_password)
        append_log(log_path, f"{now} notified available\n")
    else:
        append_log(log_path, f"{now} status {availability}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
