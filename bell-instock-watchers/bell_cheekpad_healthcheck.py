#!/usr/bin/env python3
import argparse
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


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


def parse_iso(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Send daily health check for cheek pad watcher.")
    parser.add_argument("--state-file", default="bell_cheekpad_watcher_state.json")
    parser.add_argument("--max-age-hours", type=int, default=24)
    args = parser.parse_args()

    sender = os.environ.get("GMAIL_ADDRESS")
    recipient = os.environ.get("NOTIFY_TO")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not sender or not recipient or not app_password:
        print("Missing GMAIL_ADDRESS, NOTIFY_TO, or GMAIL_APP_PASSWORD env vars.", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    state = load_state(Path(args.state_file))
    last_checked_raw = state.get("last_checked")
    last_checked = parse_iso(last_checked_raw) if last_checked_raw else None

    if not last_checked:
        subject = "Bell cheek pad watcher health check: no recent data"
        body = (
            "Health check could not find a valid last_checked timestamp.\n\n"
            f"State file: {args.state_file}\n"
            f"Checked at: {now.isoformat()}\n"
        )
        send_email(subject, body, sender, recipient, app_password)
        return 0

    age_hours = (now - last_checked).total_seconds() / 3600.0
    if age_hours > args.max_age_hours:
        subject = "Bell cheek pad watcher health check: stale"
        body = (
            "The watcher has not updated recently.\n\n"
            f"Last checked: {last_checked.isoformat()}\n"
            f"Age hours: {age_hours:.1f}\n"
            f"State file: {args.state_file}\n"
            f"Checked at: {now.isoformat()}\n"
        )
        send_email(subject, body, sender, recipient, app_password)
        return 0

    subject = "Bell cheek pad watcher health check: OK"
    body = (
        "Watcher is updating normally.\n\n"
        f"Last checked: {last_checked.isoformat()}\n"
        f"Age hours: {age_hours:.1f}\n"
        f"Checked at: {now.isoformat()}\n"
    )
    send_email(subject, body, sender, recipient, app_password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
