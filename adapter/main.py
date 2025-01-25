import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import re  
import json
import os
from datetime import datetime

# Configurări MQTT
BROKER = "broker"  
BROKER_PORT = 1883
TOPIC = "#"  # Abonare la toate topicurile

# Configurări InfluxDB
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = "eB0aRChbrT5l278d8YNX14fHYqSNuc34lB1iVmKrDJOxLmOa3deAfKYD8Nwj39dDGZhxdPy2yT9tMrAQv256nA=="
INFLUXDB_ORG = "scd"
INFLUXDB_BUCKET = "iot"

# Inițializare client InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Expresia regulată pentru validarea subiectului
TOPIC_REGEX = re.compile(r"^[^/\s]+/[^/\s]+$")   # Format: <locație>/<stat>

# Variabila de mediu pentru debugging
DEBUG_DATA_FLOW = os.getenv("DEBUG_DATA_FLOW", "False").lower() == "true"

# Funcție pentru loguri
def log_message(message):
    if DEBUG_DATA_FLOW == True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formatul dorit pentru timestamp
        print(f"{timestamp} - {message}", flush=True)

# Funcție pentru procesarea mesajelor primite
def on_message(client, userdata, message):
    try:
        # Decodifică payload-ul mesajului
        payload = message.payload.decode("utf-8")
        log_message(f"Received a message by topic [{message.topic}]")

        # Validează formatul subiectului
        if not TOPIC_REGEX.match(message.topic):
            log_message(f"Invalid topic: {message.topic}. Ignored.")
            return

        # Parsează payload-ul ca JSON
        try:
            data = json.loads(payload)  # Parsează JSON-ul
        except json.JSONDecodeError:
            log_message(f"Invalid payload received: {payload}. Ignored.")
            return
        
        if not data:
            log_message(f"Empty payload received. Ignored.")
            return

        # Verifică dacă payload-ul este un dicționar cu un singur nivel
        if not isinstance(data, dict):
            log_message(f"Invalid payload structure (not a dictionary): {payload}. Ignored.")
            return

        if any(isinstance(value, dict) for value in data.values()):
            log_message(f"Payload with nested data found: {payload}. Ignored.")
            return
        
        if not all(isinstance(value, (int, float)) for key, value in data.items() if key != "timestamp"):
            log_message(f"Payload contains non-numeric values: {payload}. Ignored.")
            return
        
        
        # Extrage timestamp-ul din payload sau folosește timpul curent
        data_timestamp = data.get("timestamp", "NOW")
        log_message(f"Data timestamp is {data_timestamp}")

        # Parsează locația și starea din subiect
        location, status = message.topic.split("/")
        data["location"] = location
        data["status"] = status

        # Scrie datele în InfluxDB
        write_to_influxdb(data)

    except Exception as e:
        log_message(f"Error processing message: {e}")



# Funcție pentru parsarea payload-ului
def parse_payload(payload):
    try:
        data = json.loads(payload)  # Parsează JSON-ul
        valid_data = {}

        # Verifică fiecare câmp să fie numeric (int sau float)
        for key, value in data.items():
            if isinstance(value, (int, float)):  # Numai valori numerice
                valid_data[key] = value

        # Verifică dacă există o cheie timestamp
        timestamp = data.get("timestamp")
        if timestamp:
            try:
                # Convertește timestamp-ul în format ISO 8601
                valid_data["timestamp"] = datetime.fromisoformat(timestamp)
            except ValueError:
                log_message(f"Timestamp invalid: {timestamp}. Ignorat.")
                return None

        return valid_data if valid_data else None
    except json.JSONDecodeError:
        log_message(f"Payload invalid: {payload}. Ignorat.")
        return None

# Funcție pentru scrierea datelor în InfluxDB
def write_to_influxdb(data):
    try:
        # Creează puncte de date în InfluxDB
        for key, value in data.items():
            if key != "timestamp":  # Ignoră timestamp-ul la scrierea în baza de date
                point = Point("iot_measurements") \
                    .field(key, value) #.tag("location", data["location"]) \ .tag("status", data["status"]) \

                if "timestamp" in data:
                    point = point.time(data["timestamp"])

                # Scrie punctul de date în InfluxDB
                write_api.write(bucket=INFLUXDB_BUCKET, record=point)
                log_message(f"Datele au fost scrise în InfluxDB: {key} = {value}")

    except Exception as e:
        log_message(f"Eroare la scrierea datelor în InfluxDB: {e}")

# Funcție principală pentru inițializarea adaptorului
def main():
    # Creează un client MQTT
    print("Creare client MQTT...", flush=True)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    print("Client MQTT creat", flush=True)

    # Configurează callback-ul pentru mesajele primite
    client.on_message = on_message

    # Conectează-te la broker
    print("Conectare la broker...", flush=True)
    client.connect(BROKER, BROKER_PORT, 60)

    # Abonează-te la toate topicurile
    client.subscribe(TOPIC)
    print(f"Abonat la toate topicurile", flush=True)

    # Pornește bucla principală pentru primirea mesajelor
    client.loop_forever()

if __name__ == "__main__":
    main()


# http://localhost:3000/ --> InfluxDB