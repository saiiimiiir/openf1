# MQTT Broker

This broker relies on the `mosquitto` executable to relay messages
to MQTT topics. Ensure `mosquitto` is installed and available in your
`PATH`.

### Running the broker

```bash
python -m openf1.services.broker.app
```

The broker listens on port `1883` by default. You can override this
using the `OPENF1_BROKER_PORT` environment variable.
