import sys

from uptimerobot4discord import config as cfg
from uptimerobot4discord import notifier, scraper, state

def main() -> None:
    # Config
    app_config = cfg.ensure_config()

    urls = cfg.parse_urls(app_config["STATUS_PAGE_URLS"])
    if not urls:
        print(
            "[uptimerobot4discord] STATUS_PAGE_URLS is empty. "
            "Please add at least one URL to the config file.",
            file=sys.stderr,
        )
        sys.exit(1)

    webhook_url = app_config["DISCORD_WEBHOOK_URL"]
    mention_role_id = app_config.get("MENTION_ROLE_ID") or None

    # Load previous state
    previous_state = state.load()
    # Scrape live state
    print(f"[uptimerobot4discord] Scraping {len(urls)} status page(s)...")
    live_state = scraper.scrape_all(urls)

    if not live_state:
        print(
            "[uptimerobot4discord] No monitors were scraped. "
            "Check your STATUS_PAGE_URLS and network connectivity.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[uptimerobot4discord] Found {len(live_state)} monitor(s) in live state.")

    # Compare and notify
    alerts_sent = 0
    new_monitors = 0

    for monitor_id, live_record in live_state.items():
        prev_record = previous_state.get(monitor_id)

        if prev_record is None:
            new_monitors += 1
            continue

        prev_status: bool = bool(prev_record.get("status"))
        live_status: bool = bool(live_record["status"])

        if prev_status == live_status:
            continue

        # fire an alert
        print(
            f"[uptimerobot4discord] Status change detected for "
            f"'{live_record['name']}' ({monitor_id}): "
            f"{'UP' if live_status else 'DOWN'}"
        )

        notifier.send_alert(
            webhook_url=webhook_url,
            monitor_id=monitor_id,
            monitor_name=str(live_record["name"]),
            page_base_url=str(live_record["page_base_url"]),
            is_up=live_status,
            mention_role_id=mention_role_id,
        )
        alerts_sent += 1

    # Persist new state
    try:
        state.save(live_state)
    except OSError as exc:
        print(
            f"[uptimerobot4discord] Failed to write state file: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Summary log
    print(
        f"[uptimerobot4discord] Done. "
        f"Alerts sent: {alerts_sent}, "
        f"New monitors initialised: {new_monitors}, "
        f"Total tracked: {len(live_state)}."
    )
