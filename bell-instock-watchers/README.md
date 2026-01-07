# Bell Instock Watchers

Scripts and systemd units to check the Bell Helmets product page every 20 minutes and
email when the 25MM M-L cheek pads appear available. Includes a daily health check email.

## Files
- `bell_cheekpad_watcher.py` - fetches the product page and emails on availability change
- `bell_cheekpad_watcher.service` - systemd oneshot service
- `bell_cheekpad_watcher.timer` - systemd timer (20-minute schedule)
- `bell_cheekpad_healthcheck.py` - daily health check email
- `bell_cheekpad_healthcheck.service` - health check service
- `bell_cheekpad_healthcheck.timer` - health check timer
- `install.sh` - installs units and creates credential drop-ins

## How it decides "available"
- Looks for common availability markers like "add to cart" or "in stock".
- Treats "out of stock" / "sold out" / "notify me" as unavailable.
- If the page text changes, tune markers in `bell_cheekpad_watcher.py`.

## CentOS 9 setup (systemd)
1) Ensure Python is installed:
   - `python3 --version`
2) Copy this folder to your CentOS box:
   - `/home/ajo/my-git-repos/ease-my-life-scripts/bell-instock-watchers`
3) Confirm the service paths inside:
   - `bell_cheekpad_watcher.service`
   - `bell_cheekpad_healthcheck.service`
4) Install with the helper script:
   - Edit `install.sh` and set `APP_PASSWORD=your_app_password`
   - `bash /home/ajo/my-git-repos/ease-my-life-scripts/bell-instock-watchers/install.sh`

## Security note (recommended)
This uses systemd drop-in files so the Gmail app password does not live in version control.
The installer creates:
- `/etc/systemd/system/bell_cheekpad_watcher.service.d/override.conf`
- `/etc/systemd/system/bell_cheekpad_healthcheck.service.d/override.conf`

## Manual test
Run once to confirm it can reach the page and email you:
```
GMAIL_ADDRESS=your_email@example.com \
NOTIFY_TO=your_email@example.com \
GMAIL_APP_PASSWORD='your_app_password_here' \
python3 /home/ajo/my-git-repos/ease-my-life-scripts/bell-instock-watchers/bell_cheekpad_watcher.py
```

## Logs and state
- Log file: `/home/ajo/my-git-repos/ease-my-life-scripts/bell-instock-watchers/bell_cheekpad_watcher.log`
- State file: `/home/ajo/my-git-repos/ease-my-life-scripts/bell-instock-watchers/bell_cheekpad_watcher_state.json`

## Troubleshooting
- If no emails arrive:
  - Verify Gmail app password is correct (no spaces).
  - Check the log file for `fetch_error` or `status unknown`.
  - Run the manual test above to confirm SMTP access.
- If it always shows unavailable:
  - The site HTML may have changed. Update markers in `bell_cheekpad_watcher.py`.
- If you need a different schedule:
  - Edit `bell_cheekpad_watcher.timer` and change `OnUnitActiveSec=20min`, then:
    - `sudo systemctl daemon-reload`
    - `sudo systemctl restart bell_cheekpad_watcher.timer`
