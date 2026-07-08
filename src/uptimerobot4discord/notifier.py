import sys

import requests

REQUEST_TIMEOUT = 10  # seconds

_UP_COLOR = 4052080
_DOWN_COLOR = 14502475
_UP_THUMBNAIL = "https://resources.ourpxi.dev/up32.webp"
_DOWN_THUMBNAIL = "https://resources.ourpxi.dev/down32.webp"

def send_alert(
    *,
    webhook_url: str,
    monitor_id: str,
    monitor_name: str,
    page_base_url: str,
    is_up: bool,
    mention_role_id: str | None = None,
) -> None:
    # POST a Discord embed alert for a single monitor status change.
    payload = _build_payload(
        monitor_id=monitor_id,
        monitor_name=monitor_name,
        page_base_url=page_base_url,
        is_up=is_up,
        mention_role_id=mention_role_id,
    )

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(
            f"[] Failed to send Discord alert for "
            f"'{monitor_name}': {exc}",
            file=sys.stderr,
        )

def _build_payload(
    *,
    monitor_id: str,
    monitor_name: str,
    page_base_url: str,
    is_up: bool,
    mention_role_id: str | None,
) -> dict:
    # Construct the Discord webhook JSON payload.
    status_label = "UP" if is_up else "DOWN"
    color = _UP_COLOR if is_up else _DOWN_COLOR
    thumbnail_url = _UP_THUMBNAIL if is_up else _DOWN_THUMBNAIL

    embed = {
        "title": f"{monitor_name} | {status_label}",
        "color": color,
        "thumbnail": {"url": thumbnail_url},
        "url": f"{page_base_url}/{monitor_id}",
    }

    payload: dict = {"embeds": [embed]}

    # Append role mention as top-level content so Discord sends a ping to the role
    if mention_role_id:
        payload["content"] = f"<@&{mention_role_id}>"

    return payload
