# Example: Binance BTC trades

Pulls the most recent BTCUSDT trades from Binance's public API every 5 minutes into
`pipelines.example-binance-trades.trades`. Runs on the platform as the connector
`lc-example-binance-trades`.

## The choices, and why

- **Endpoint:** `GET /api/v3/trades?symbol=BTCUSDT&limit=100` — the latest 100 trades,
  newest last. No API key needed.
- **Interval:** 5 minutes. BTCUSDT trades far more than 100 times in 5 minutes, so this
  samples the market rather than capturing every trade. To capture everything you would
  page with `fromId` (`/api/v3/historicalTrades`) — a good next project.
- **Offset:** `key=/id, timestamp=/time`. Every trade has a unique, increasing `id`, so a
  poll that overlaps the previous one does not produce duplicates.
- **Topic:** under this project's prefix, one topic for one kind of record.

## Try the endpoint first

In a notebook, before writing any connector config:

```python
import requests
requests.get("https://api.binance.com/api/v3/trades",
             params={"symbol": "BTCUSDT", "limit": 3}).json()
```

## Contract

A contract for the topic belongs in
[`data-contracts`](https://github.com/datapg-labs/data-contracts) — writing it is a good
first contribution.
