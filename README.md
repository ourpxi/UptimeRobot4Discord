# UptimeRobot4Discord

A lightweight Python utility that scrapes UptimeRobot public status pages and sends real-time **UP** / **DOWN** alerts directly to Discord via webhooks.

## Features

- Scrapes one or more UptimeRobot public status pages
- Detects status changes (UP → DOWN, DOWN → UP) between runs
- Sends rich Discord embed notifications with monitor name, status colour, and direct link
- Supports Discord role mentions for critical alerts (`@here`-style pings)
- Persists monitor state in `~/.uptimerobot4discord_state.json` to avoid duplicate alerts
- Simple configuration via `~/.uptimerobot4discord_config`

## Installation

```bash
pip install uptimerobot4discord
```

## Quick Start

1. Run the tool once to generate the config file:

```bash
uptimerobot4discord
```

2. Edit the generated config at `~/.uptimerobot4discord_config`:

```
STATUS_PAGE_URLS=https://status.example.com,https://status2.example.com
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456/abcdef
MENTION_ROLE_ID=123456789012345678
```

3. Run it again:

```bash
uptimerobot4discord
```

Set up a cron job (every 5 minutes) to poll continuously:

```cron
*/5 * * * * /usr/local/bin/uptimerobot4discord
```

## How It Works

1. Reads configuration from `~/.uptimerobot4discord_config`
2. Scrapes the configured UptimeRobot public status pages using BeautifulSoup/lxml
3. Compares current monitor states with the last known state on disk
4. Sends a Discord webhook embed for every monitor that changed status
5. Persists the new state for the next run

## Configuration

| Key | Required | Description |
|---|---|---|
| `STATUS_PAGE_URLS` | Yes | Comma-separated UptimeRobot public status page URLs |
| `DISCORD_WEBHOOK_URL` | Yes | Full Discord channel webhook URL |
| `MENTION_ROLE_ID` | No | Discord Role ID to ping on alerts (numeric string) |

## License

MIT
