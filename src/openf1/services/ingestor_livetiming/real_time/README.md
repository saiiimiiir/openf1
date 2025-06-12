# Ingesting real-time data

Start the broker in a separate terminal:

```bash
python -m openf1.services.broker.app
```

Then start ingesting a session in progress:

```bash
python -m openf1.services.ingestor_livetiming.real_time.app
```

The recording must be started at least 1h before the start of the session for races,
and at least 15 minutes before the start of the session for practice and qualifying.
