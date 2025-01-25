# Imagine de bază cu Python
FROM python:3.10-slim
# Setăm directorul de lucru în container
WORKDIR /app

# Copiem fișierele proiectului în container
COPY . /app

# Instalăm dependențele din requirements.txt
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y mosquitto-clients

RUN pip install --no-cache-dir -r requirements.txt

# Setăm comanda de rulare pentru container
CMD ["python3", "main.py"]
