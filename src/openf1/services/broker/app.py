import asyncio
import os
from asyncio.subprocess import Process
from loguru import logger


async def start_broker() -> Process:
    port = os.getenv("OPENF1_BROKER_PORT", "1883")
    logger.info(f"Starting mosquitto on port {port}")
    proc = await asyncio.create_subprocess_exec(
        "mosquitto",
        "-p",
        str(port),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return proc


async def main() -> None:
    proc = await start_broker()
    try:
        await proc.wait()
    finally:
        proc.terminate()


if __name__ == "__main__":
    asyncio.run(main())
