import json
import signal
import sys

import httpx
import sseclient
from kafka import KafkaProducer

WIKI_SSE_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
KAFKA_TOPIC = "wiki.recentchanges"
KAFKA_BOOTSTRAP = "localhost:9094"

def main():
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    def shutdown(sig, frame):
        print("\nShutting down...")
        producer.flush()
        producer.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    headers = {"User-Agent": "paimon-guide-lab/1.0 (https://github.com/paimon-guide; data-engineering-study)"}

    print(f"Connecting to {WIKI_SSE_URL}...")
    with httpx.Client(timeout=None) as client:
        with client.stream("GET", WIKI_SSE_URL, headers=headers, follow_redirects=True) as response:
            print("Connected. Streaming events...")
            sse = sseclient.SSEClient(response.iter_bytes())

            count = 0
            for event in sse.events():
                if event.event == "message" and event.data:
                    try:
                        data = json.loads(event.data)
                        producer.send(KAFKA_TOPIC, value=data)
                        count += 1
                        if count % 100 == 0:
                            print(f"Sent {count} events to Kafka")
                    except json.JSONDecodeError:
                        continue

if __name__ == "__main__":
    main()
