import asyncio
import os
import socket

# ruff: noqa: E402

import paho.mqtt.client as mqtt
import pytest


def _free_port() -> int:
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


from openf1.services.broker.app import start_broker


@pytest.mark.asyncio
async def test_publish_to_local_broker():
    port = _free_port()
    os.environ["OPENF1_BROKER_PORT"] = str(port)
    broker = await start_broker()
    os.environ["OPENF1_MQTT_URL"] = "localhost"
    os.environ["OPENF1_MQTT_PORT"] = str(port)
    os.environ["OPENF1_MQTT_TLS"] = "0"
    from openf1.util.mqtt import publish_messages_to_mqtt

    received: list[str] = []

    await asyncio.sleep(0.5)

    def on_message(client, userdata, msg):
        received.append(msg.payload.decode())

    client = mqtt.Client()
    client.on_message = on_message
    client.connect("localhost", port)
    client.subscribe("test/topic")
    client.loop_start()

    await asyncio.sleep(0.1)
    assert await publish_messages_to_mqtt("test/topic", ["ping"])
    await asyncio.sleep(0.5)

    client.loop_stop()
    client.disconnect()
    broker.terminate()
    await broker.wait()

    assert "ping" in received
