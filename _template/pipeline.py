"""
A worked Kafka example for the datapg teaching cluster.

Copy this file into your own directory (e.g. ingestion/pg0025/) and change
PG_ID. Everything else should run unchanged.

Run it from a JupyterHub notebook or the platform VS Code — `kafka-learn` only
resolves inside the platform network, so this will not run from your laptop.

First, in a notebook cell:

    !pip install --quiet kafka-python

The image does not ship a Kafka client.
"""

import os

from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

# --- who you are -------------------------------------------------------------
# Your platform ID, lowercase. Everything you own must start with "<PG_ID>."
PG_ID = "pg0025"

# Never paste the password into a file you are going to commit. Set it in the
# notebook first:  os.environ["KAFKA_PASSWORD"] = "..."
# Get it from https://datapg.dev/credentials
PASSWORD = os.environ["KAFKA_PASSWORD"]

TOPIC = f"{PG_ID}.events"
GROUP = f"{PG_ID}.demo"

conf = dict(
    bootstrap_servers="kafka-learn:9092",
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=PG_ID,
    sasl_plain_password=PASSWORD,
)

# --- 1. create the topic -----------------------------------------------------
# Auto-creation is switched off on this cluster. Skip this and the producer
# below will hang for 60 seconds and then complain about metadata, which is a
# confusing way to be told "that topic does not exist".
admin = KafkaAdminClient(**conf)
try:
    admin.create_topics([NewTopic(TOPIC, num_partitions=1, replication_factor=1)])
    print(f"created {TOPIC}")
except TopicAlreadyExistsError:
    print(f"{TOPIC} already exists, carrying on")

# --- 2. produce --------------------------------------------------------------
producer = KafkaProducer(**conf)
for i in range(10):
    producer.send(TOPIC, f"event {i}".encode())
producer.flush()
print(f"produced 10 messages to {TOPIC}")

# --- 3. consume --------------------------------------------------------------
# consumer_timeout_ms makes this terminate instead of blocking forever, which is
# what you want in a notebook.
consumer = KafkaConsumer(
    TOPIC,
    group_id=GROUP,
    auto_offset_reset="earliest",
    consumer_timeout_ms=10_000,
    **conf,
)
for message in consumer:
    print(message.offset, message.value.decode())

# --- what happens if you stray outside your prefix ---------------------------
# Uncomment to see the error you will get. It is worth seeing once, because the
# message is not obvious the first time:
#
#   admin.create_topics([NewTopic("someone-elses.topic", 1, 1)])
#   -> TopicAuthorizationFailedError
#
# And a topic belonging to someone else is reported as "does not exist" rather
# than "forbidden" — Kafka will not confirm that it exists at all.
