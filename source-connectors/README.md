# Source connectors

Kafka Connect **source** connectors, as JSON — one folder per project. Merged
connectors are **deployed** to the learners' Connect worker and run continuously.

Start from [`example-binance-trades`](example-binance-trades/): it pulls recent BTC
trades from Binance every 5 minutes into `pipelines.example-binance-trades.trades`.

## What a project folder contains

```
binance-eth-trades/
  README.md        what it pulls, how often, into which topic — and why those choices
  connector.json   the configuration
```

## What happens after merge

Every 15 minutes the Airflow DAG `learner_connectors` reads `source-connectors/` on
`main`, validates each `connector.json`, and deploys it as the connector
`lc-<project>`. Change the file and the connector is updated; delete the folder and
the connector is removed. The run's log in Airflow shows each connector's state — and,
if a config was rejected, exactly why.

## The rules a config must follow

| | |
|---|---|
| Connector | `com.github.castorm.kafka.connect.http.HttpSourceConnector` (you may omit it) — the only one available |
| Settings | Only `http.*` settings and `kafka.topic`. No `http.auth.*`, no proxy settings, no transforms, converters or `${...}` providers |
| Source | `https://` on `api.binance.com`, `data-api.binance.vision`, or `query1`/`query2.finance.yahoo.com` |
| Topic | Must start with `pipelines.<your-project>.` — e.g. `pipelines.binance-eth-trades.trades` |
| Polling | No faster than once a minute (`http.timer.interval.millis` ≥ 60000); one task |

Anything else is rejected before it reaches the worker. No credentials — the allowed
APIs don't need any.

## The settings you will use most

| Setting | What it does |
|---|---|
| `http.request.url` | The endpoint |
| `http.request.params` | Query string, as `name=value&name2=value2` |
| `http.timer.interval.millis` | How often to poll |
| `http.response.list.pointer` | JSON Pointer to the array of records in the response (`/` if the response *is* the array) |
| `http.response.record.offset.pointer` | Which fields identify a record and its time, e.g. `key=/id, timestamp=/time` — used to skip records already seen |
| `kafka.topic` | Where the records go |

The connector is [castorm/kafka-connect-http](https://github.com/castorm/kafka-connect-http)
(v0.8.11); its README lists every setting.

## Reading the messages

Each record arrives wrapped: the message value is `{"value": "<the API record as a JSON
string>"}`, and the key is `{"key": "<the offset key>"}`. Parse twice:

```python
record = json.loads(json.loads(message.value)["value"])
```

## Things to know

- **Explain the choices** in your README: why this endpoint, this interval, this offset
  key; what a duplicate looks like; what happens after a restart. That is what the review
  is about.
- **Add a data contract** for the topic, in
  [`data-contracts`](https://github.com/datapg-labs/data-contracts), and link it from the
  README.
- **Be gentle with the APIs.** Every connector shares one outbound address with everyone
  else's; poll only as often as the data actually changes.
