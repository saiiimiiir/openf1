
Créer un broker pour données temps réel
22 juin
saiiimiiir/openf1
codex/créer-un-broker-pour-données-temps-réel
+47
-0

Archiver

Partager
Afficher la demande d’extraction


crée moi un broker qui peut se connecter a ce projet pour recevoir les données temps réel.
et montre moi comment parametrer ce projet pour qu'il envoie les données temps réel vers un broker en local
Copier
Le projet intègre déjà un module de publication vers MQTT.
La fonction publish_messages_to_mqtt() est utilisée lorsque la variable d’environnement OPENF1_MQTT_URL est définie :

if "OPENF1_MQTT_URL" in os.environ:
    from openf1.util.mqtt import publish_messages_to_mqtt
...
if "OPENF1_MQTT_URL" in os.environ:
    docs_mongo_json = [json.dumps(d, default=json_serializer) for d in docs_mongo]
    await publish_messages_to_mqtt(topic=f"v1/{collection}", messages=docs_mongo_json)

Les paramètres utilisés pour se connecter au broker sont lus depuis ces variables d’environnement :

_url = os.getenv("OPENF1_MQTT_URL")
_port = int(os.getenv("OPENF1_MQTT_PORT"))
_username = os.getenv("OPENF1_MQTT_USERNAME")
_password = os.getenv("OPENF1_MQTT_PASSWORD")

1. Mettre en place un broker MQTT local
Une solution rapide consiste à lancer Mosquitto via Docker :

docker run -it -p 1883:1883 -p 8883:8883 --name mqtt-broker eclipse-mosquitto
Mosquitto écoutera sur le port 1883 (sans TLS) et sur le port 8883 (avec TLS).
Pour un test local simple, vous pouvez laisser la configuration par défaut (port 1883).

2. Configurer OpenF1 pour publier vers ce broker
Définissez les variables d’environnement avant de démarrer l’ingestion temps réel :

export OPENF1_MQTT_URL="localhost"
export OPENF1_MQTT_PORT="1883"        # port du broker
export OPENF1_MQTT_USERNAME=""        # facultatif
export OPENF1_MQTT_PASSWORD=""        # facultatif
(Si vous activez TLS sur votre broker, utilisez le port 8883 et assurez-vous que la connexion TLS fonctionne avec le certificat utilisé.)

3. Lancer l’ingestion temps réel
Dans le dépôt, le module d’ingestion se lance ainsi :

python -m openf1.services.ingestor_livetiming.real_time.app

Une fois l’ingestion démarrée, chaque message traité sera publié sur le broker local (topics v1/<nom_de_collection>). Il vous suffit alors de vous connecter à ce broker avec un client MQTT pour recevoir les données en temps réel.

oui je sais que le projet peut envoyer des donnée vers un broker, moi je veux créer ce broker en nodejs
Copier
To publish OpenF1’s real‑time data to your own MQTT broker, you can create a simple Node.js server. OpenF1 reads the MQTT connection parameters from the environment:

_url = os.getenv("OPENF1_MQTT_URL")
_port = int(os.getenv("OPENF1_MQTT_PORT"))
_username = os.getenv("OPENF1_MQTT_USERNAME")
_password = os.getenv("OPENF1_MQTT_PASSWORD")

During ingestion, if these variables are set, each document is published to MQTT:

if "OPENF1_MQTT_URL" in os.environ:
    docs_mongo_json = [json.dumps(d, default=json_serializer) for d in docs_mongo]
    await publish_messages_to_mqtt(topic=f"v1/{collection}", messages=docs_mongo_json)

1. Create a Node.js MQTT broker
Install Node.js (v16 or later) and initialize a project:

npm init -y
npm install aedes
Create broker.js:

const aedes = require('aedes')();
const server = require('net').createServer(aedes.handle);

const PORT = 1883;
server.listen(PORT, () => {
  console.log('MQTT broker listening on port', PORT);
});
Run the broker:

node broker.js
2. Configure OpenF1 to send data to your broker
Before starting OpenF1’s ingestion service, set the environment variables:

export OPENF1_MQTT_URL="localhost"
export OPENF1_MQTT_PORT="1883"
export OPENF1_MQTT_USERNAME=""     # optional
export OPENF1_MQTT_PASSWORD=""     # optional
Then start the real-time ingestor:

python -m openf1.services.ingestor_livetiming.real_time.app
OpenF1 will connect to your Node.js broker and publish messages to topics like v1/car_data, v1/session, etc. You can use any MQTT client to subscribe to these topics and receive the data in real time.

je travaille avec powershell
Copier
Pour publier les messages temps réel d’OpenF1 vers un broker local en utilisant PowerShell, voici comment procéder :

1. Installer et démarrer un petit broker MQTT en Node.js
Ouvrez PowerShell et créez un dossier pour votre broker :

mkdir openf1-broker
cd openf1-broker
Initialisez un projet Node.js et installez la bibliothèque Aedes, qui sert de broker MQTT léger :

npm init -y
npm install aedes
Créez un fichier broker.js (avec votre éditeur habituel) et copiez le code suivant :

const aedes = require('aedes')();
const server = require('net').createServer(aedes.handle);

const PORT = 1883;
server.listen(PORT, () => {
  console.log('MQTT broker listening on port', PORT);
});
Lancez le broker :

node broker.js
Votre broker écoute maintenant sur localhost:1883.

2. Paramétrer OpenF1 pour publier vers ce broker
Le code du projet lit les paramètres MQTT via les variables d’environnement :

_url = os.getenv("OPENF1_MQTT_URL")
_port = int(os.getenv("OPENF1_MQTT_PORT"))
_username = os.getenv("OPENF1_MQTT_USERNAME")
_password = os.getenv("OPENF1_MQTT_PASSWORD")

Dans PowerShell, définissez ces variables avant de lancer l’ingestion :

$env:OPENF1_MQTT_URL  = "localhost"
$env:OPENF1_MQTT_PORT = "1883"
$env:OPENF1_MQTT_USERNAME = ""  # facultatif
$env:OPENF1_MQTT_PASSWORD = ""  # facultatif
Démarrez ensuite l’ingesteur temps réel d’OpenF1 :

python -m openf1.services.ingestor_livetiming.real_time.app

OpenF1 se connectera à votre broker Node.js local et publiera les messages sur des topics du type v1/<nom_de_collection> (par exemple v1/car_data, v1/session, etc.). Vous pouvez désormais utiliser un client MQTT pour vous abonner à ces topics et recevoir les données en temps réel.

ok comment je peux faire un test d'envoie de données en temps réel si il n'ya pas de course actuellement ?
Copier
Le dépôt explique comment récupérer et traiter des sessions passées via le module historical :

# Fetching and ingesting historical data
...
To list the available topics for session `9574` (meeting `1242`, year `2024`):

  python -m openf1.services.ingestor_livetiming.historical.main list-topics 2024 1242 9574

To get the messages of topic `DriverList` for that session:

  python -m openf1.services.ingestor_livetiming.historical.main get-messages 2024 1242 9574 DriverList

Vous pouvez aussi ingérer toutes les collections d’une session passée :

python -m openf1.services.ingestor_livetiming.historical.main ingest-session 2024 1242 9574

Les publications vers MQTT s’appuient sur les variables d’environnement suivantes :

_url = os.getenv("OPENF1_MQTT_URL")
_port = int(os.getenv("OPENF1_MQTT_PORT"))
_username = os.getenv("OPENF1_MQTT_USERNAME")
_password = os.getenv("OPENF1_MQTT_PASSWORD")

Pour tester l’envoi de données vers votre broker, vous pouvez donc :

Choisir une session passée (par exemple via list-topics et get-messages).

Traiter cette session avec ingest-session pour obtenir les documents.

Écrire un petit script qui lit ces documents et utilise la fonction publish_messages_to_mqtt() afin de les diffuser vers votre broker local.

Ainsi vous simulez un flux temps réel même en dehors des courses.

ok écris moi ce script de test pour l'année 2025 le meeting 1263 et la session 9963.
Le but sera d'envoyer les données de tous les topics présents vers le broker pour tester la bonne connexion et l'envoie de données verse le broker
Copier
Notes

This update adds a script to send historical session data to an MQTT broker. The script gathers all topics for a session and publishes the messages to historical/<topic> on the configured broker. It can be run with your environment variables pointing to a local broker.

Summary

Created an example script replay_historical_to_mqtt.py that lists topics for year 2025 meeting 1263 session 9963, retrieves all messages, and publishes them to MQTT

Testing

✅ black examples/replay_historical_to_mqtt.py

✅ ruff examples/replay_historical_to_mqtt.py

✅ pytest -q (no tests ran)


Fichier (1)
je veux que le test pour les données n'envoie plus les données en masse mais avec la même fréquence que si elles étaient streamer en direct explique moi comment on peut faire ça
Copier
Notes

Le script replay_historical_to_mqtt.py diffuse maintenant chaque message avec la même cadence que lors de la diffusion originale. Pour chaque message, on calcule le délai depuis le message précédent et on attend cette durée avant de l’envoyer vers le broker. On conserve ainsi la fréquence réelle d’émission.

Summary

Ajout d’une attente basée sur l’écart entre deux messages pour reproduire la cadence d’origine

Testing

✅ ruff check examples/replay_historical_to_mqtt.py

✅ black --check examples/replay_historical_to_mqtt.py

✅ pytest -q (aucun test exécuté)

Network access

Some requests were blocked due to network access restrictions. Consider granting access in environment settings.

github.com


Fichier (1)

examples/replay_historical_to_mqtt.py
Nouveau


Diff
Journaux
examples/replay_historical_to_mqtt.py
Nouveau
+47
-0

import asyncio
import json

from openf1.services.ingestor_livetiming.historical import main as historical
from openf1.util.mqtt import publish_messages_to_mqtt
from openf1.util.misc import json_serializer

YEAR = 2025
MEETING_KEY = 1263
SESSION_KEY = 9963


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
        if prev is not None:
            delta = (m.timepoint - prev).total_seconds()
            if delta > 0:
                await asyncio.sleep(delta)
        msg = json.dumps(
            {
                "topic": m.topic,
                "timepoint": m.timepoint,
                "content": m.content,
            },
            default=json_serializer,
        )
        await publish_messages_to_mqtt(topic=f"historical/{m.topic}", messages=[msg])
        prev = m.timepoint
    print("Replay completed")


if __name__ == "__main__":
    asyncio.run(main())
