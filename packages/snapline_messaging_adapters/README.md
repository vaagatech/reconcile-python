# snapline-messaging-adapters

Messaging queue adapters for Snapline Python — in-memory queues and custom publisher/consumer protocols.

## Install

```bash
pip install snapline-messaging-adapters
```

## Quick start

```python
from snapline.messaging_adapters import messaging
from snapline.core import run_publish_and_poll

queue = messaging.memory()

result = await run_publish_and_poll({
    "publish": {
        "publisher": queue["publisher"],
        "topic": "jobs.submit",
        "payload": {"jobId": "JOB-42"},
    },
    "poll": {"file": {"directory": "/var/results"}},
    "expected": {"jobId": "JOB-42", "status": "COMPLETE"},
})
```

See [Snapline docs](https://vaagatech.github.io/snapline-python/guide.html) for DB polling and `test_suite` integration.
