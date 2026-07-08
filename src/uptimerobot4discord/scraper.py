import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from uptimerobot4discord.state import MonitorRecord, StateDict
# Constant

REQUEST_TIMEOUT = 15  # seconds

# CSS classes / HTML attributes used by Uptime Robot status pages
_UP_CLASSES = {"up", "operational"}
_DOWN_CLASSES = {"down", "outage", "degraded", "paused", "error", "offline"}

# User-Agent string
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; uptimerobot4discord/1.0; "
        "+https://github.com/ourpxi/UptimeRobot4Discord)"
    )
}

def scrape_all(urls: list[str]) -> StateDict:
    # Scrape each URL and merge results into a single state dict.
    combined: StateDict = {}
    for url in urls:
        try:
            page_monitors = _scrape_page(url)
            combined.update(page_monitors)
        except Exception as exc:  # noqa: BLE001 – intentional broad catch
            print(
                f"[uptimerobot4discord] Error scraping {url}: {exc}",
                file=sys.stderr,
            )
    return combined

def _scrape_page(base_url: str) -> StateDict:
    # Fetch and parse a single Uptime Robot status page.
    response = requests.get(base_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    monitors: StateDict = {}

    # ook for every element that carries a monitor identifier.
    # Uptime Robot's own hosted pages use  <li class="monitor ...">  blocks.
    # Custom-domain pages may differ — we try several selector patterns.
    candidates = (
        soup.select("li[data-id]")            # standard data-id attribute
        or soup.select("li.monitor")          # class-based fallback
        or soup.select("[class*='monitor']")  # partial-class wildcard
    )

    for element in candidates:
        monitor_id, record = _parse_monitor_element(element, base_url)
        if monitor_id and record:
            monitors[monitor_id] = record

    if not monitors:
        raise RuntimeError(
            f"No monitors found on page {base_url}"
            f"URL: {base_url}"
        )

    return monitors


def _parse_monitor_element(
    element, base_url: str
) -> tuple[str | None, MonitorRecord | None]:
    # Extract a monitor ID, name, and status from a single HTML element.
    monitor_id = (
        element.get("data-id")
        or element.get("id", "").replace("monitor-", "").strip()
        or None
    )

    # Fallback: derive a slug from the monitor's anchor href if present
    if not monitor_id:
        anchor = element.find("a", href=True)
        if anchor:
            path = urlparse(anchor["href"]).path.strip("/")
            monitor_id = path.split("/")[-1] if path else None

    if not monitor_id:
        return None, None

    # --- Determine display name ---
    name_el = (
        element.find(class_="monitor-name")
        or element.find(class_="name")
        or element.find("h3")
        or element.find("h4")
        or element.find("strong")
    )
    name = name_el.get_text(strip=True) if name_el else f"Monitor {monitor_id}"

    # --- Determine status ---
    status = _resolve_status(element)

    record: MonitorRecord = {
        "name": name,
        "status": status,
        "page_base_url": base_url,
    }
    return monitor_id, record


def _resolve_status(element) -> bool:
    # Resolve the monitor status (up/down)
    all_classes: set[str] = set()
    for node in [element] + element.find_all(True):
        all_classes.update(c.lower() for c in (node.get("class") or []))

    if all_classes & _UP_CLASSES:
        return True
    if all_classes & _DOWN_CLASSES:
        return False
    text = element.get_text(" ", strip=True).lower()
    if any(word in text for word in ("operational", "up", "online")):
        return True
    if any(word in text for word in ("down", "outage", "degraded", "paused", "error")):
        return False
    return True
