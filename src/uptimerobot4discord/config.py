import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIG_PATH = Path.home() / ".uptimerobot4discord_config"

_CONFIG_TEMPLATE = """\
# uptimerobot4discord configuration
# ---------------------------------------------------------------
# Fill in the values below, then re-run `uptimerobot4discord`.
#
# STATUS_PAGE_URLS
#   Comma-separated list of public Uptime Robot status page URLs
#   to scrape.  Each URL should point to a page like:
#       https://status.example.com
#
# DISCORD_WEBHOOK_URL
#   The full Discord webhook URL that notifications are posted to.
#   Example: https://discord.com/api/webhooks/123456/abcdef
#
# MENTION_ROLE_ID  (optional)
#   A Discord Role ID (numeric string).  When present, the bot will
#   prepend <@&ROLE_ID> to every alert so the role gets pinged.
#   Leave the value empty or omit the line entirely to disable.
# ---------------------------------------------------------------

STATUS_PAGE_URLS=

DISCORD_WEBHOOK_URL=

MENTION_ROLE_ID=
"""


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def ensure_config() -> dict[str, str]:
    """Return parsed config values, or exit after creating a blank file.

    Raises:
        SystemExit: with code 1 when the config file was just created or
                    when required keys are missing / empty.
    """
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(_CONFIG_TEMPLATE, encoding="utf-8")
        print(
            f"[uptimerobot4discord] Config file created at {CONFIG_PATH}\n"
            "Please fill in the required values and re-run the command.",
            file=sys.stderr,
        )
        sys.exit(1)

    return _parse_config(CONFIG_PATH)


def _parse_config(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE config file, ignoring blank lines and comments.

    Returns:
        dict mapping key strings to raw value strings.

    Raises:
        SystemExit: with code 1 when required keys are absent or empty.
    """
    raw: dict[str, str] = {}

    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            print(
                f"[uptimerobot4discord] Warning: skipping malformed line {lineno} "
                f"in {path}: {line!r}",
                file=sys.stderr,
            )
            continue
        key, _, value = line.partition("=")
        raw[key.strip()] = value.strip()

    _validate(raw)
    return raw


def _validate(cfg: dict[str, str]) -> None:
    """Abort with a descriptive message if required config keys are missing."""
    required = ("STATUS_PAGE_URLS", "DISCORD_WEBHOOK_URL")
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        print(
            f"[uptimerobot4discord] The following required config values are "
            f"missing or empty in {CONFIG_PATH}: {', '.join(missing)}\n"
            "Please edit the file and re-run the command.",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_urls(raw_value: str) -> list[str]:
    """Split and clean a comma-separated list of URLs."""
    return [u.strip().rstrip("/") for u in raw_value.split(",") if u.strip()]
