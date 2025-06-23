import asyncio
import json
from datetime import datetime

from openf1.services.ingestor_livetiming.historical import main as historical
from openf1.util.mqtt import publish_messages_to_mqtt
from openf1.util.misc import json_serializer

YEAR = 2024
MEETING_KEY = 1239
SESSION_KEY = 9549

# >>>> AJOUT DU FILTRE TIMEPOINT <<<<
IGNORE_BEFORE = "2024-06-29T09:57:52.000000+00:00"  # À personnaliser
IGNORE_BEFORE_DT = datetime.fromisoformat(IGNORE_BEFORE)

# Liste de topics exemptés du filtrage timepoint
EXEMPT_TOPICS = [
    "Session.Info",
    "RaceControl",
    "Weather",
    # Ajoute ici d'autres topics à exempter si besoin
]
# >>>> -------------------------- <<<<

async def main() -> None:
    topics = historical.list_topics(
        year=YEAR, meeting_key=MEETING_KEY, session_key=SESSION_KEY
    )
    print(f"Found {len(topics)} topics: {topics}")

    messages = historical.get_messages(
        year=YEAR,
        meeting_key=MEETING_KEY,
        session_key=SESSION_KEY,
        topics=topics,
        verbose=True,
    )
    print(f"Publishing {len(messages)} messages")
    prev = None
    for m in messages:
        # FILTRAGE SUR LE TIMEPOINT sauf pour certains topics
        if m.topic not in EXEMPT_TOPICS:
            msg_timepoint = m.timepoint
            if isinstance(msg_timepoint, str):
                msg_timepoint = datetime.fromisoformat(msg_timepoint)
            if msg_timepoint < IGNORE_BEFORE_DT:
                continue  # Ignore les messages avant la date/heure choisie
        if prev is not None:
            delta = (msg_timepoint - prev).total_seconds()
            if delta > 0:
                await asyncio.sleep(delta)
        msg = json.dumps(
            {
                "topic": m.topic,
                "timepoint": m.timepoint,
                "session_key": SESSION_KEY,
                "content": m.content,
            },
            default=json_serializer,
        )
        await publish_messages_to_mqtt(topic=f"historical/{m.topic}", messages=[msg])
        prev = m.timepoint
    print("Replay completed")


if __name__ == "__main__":
    asyncio.run(main())

# ---
# KPIs associés :
# - Nombre de messages publiés après le filtre.
# - Pourcentage de messages ignorés.
# - Temps de traitement total avant/après optimisation.
#
# Questions pour aller plus loin :
# - As-tu besoin que le filtre soit dynamique (par exemple via une variable d'environnement ou un argument CLI) ?
# - Dois-tu logguer le nombre de messages ignorés pour suivi analytique ?
#
# Sources méthodo :
# - https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
# - https://www.hivemq.com/mqtt-essentials/
# ---
# Si tu veux la gestion avancée (log, reporting, CLI, etc.), dis-moi !
