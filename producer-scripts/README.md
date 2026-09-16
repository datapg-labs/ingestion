# Producer scripts

Python programs that produce to (and read back from) the teaching Kafka cluster — one
folder per project.

## Start a project

Copy the worked example to a folder named after what your producer does:

```bash
cp -r producer-scripts/example-kafka-producer producer-scripts/btc-price-alerts
```

[`example-kafka-producer`](example-kafka-producer/) creates its topic, writes ten
messages, reads them back, and stops. Change `PROJECT` and build from there.

## What a project folder contains

```
btc-price-alerts/
  README.md       what it does, where the data comes from, who built it, what you learned
  pipeline.py     the producer — this is the file the platform runs
```

In the README, link the **data contract** for the topic you produce to — see
[`data-contracts`](https://github.com/datapg-labs/data-contracts).

## What happens after merge

Every folder with a `pipeline.py` on `main` runs **once an hour** on the platform, in the
Airflow DAG `learner_producers`. You can watch the runs and read the logs in Airflow.

It runs in a locked-down sandbox, so write it for that:

| | |
|---|---|
| Identity | Kafka user `pipelines`: `PG_ID=pipelines` and `KAFKA_PASSWORD` are set in the environment |
| Topics | Must start with `pipelines.` — use `pipelines.<your-project>.<topic>` so projects don't collide |
| Runtime | Must finish and exit within **5 minutes**; it is stopped after that |
| Network | Only the teaching Kafka. **No internet** — generate data rather than calling an API |
| Resources | 512 MB memory, half a CPU, read-only filesystem except `/tmp` |
| Packages | What the notebook image ships (`kafka-python` included); nothing can be installed |
| Logs | Visible to everyone in Airflow — never print credentials |

The example already does all of this: it reads `PG_ID` and the password from the
environment and puts the project name in its topic.

## Things to know

- **Try it in JupyterHub first.** `kafka-learn:9092` only resolves inside the platform
  network, so it will not run from your laptop. In a notebook, `PG_ID` is your own
  platform ID.
- **Your prefix.** Topics and consumer groups must start with the running identity and a
  dot — `pgXXXX.` in your notebook, `pipelines.` after merge.
- **No credentials in files.** Read the password from the environment:
  `os.environ["KAFKA_PASSWORD"]`.
