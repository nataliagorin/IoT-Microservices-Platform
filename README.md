# Tema 3 SCD - Platformă IoT folosind Microservicii

### Gorin Natalia-Stefania 343C2

Structura proiectului: \
tema3 \
├── adapter \
│   ├── Dockerfile \
│   ├── main.py \
│   └── requirements.txt \
├── mosquitto.conf \
├── remove_stack.sh \
├── run.sh \
└── stack.yml 

## run.sh si remove_stack.sh

Cele 2 script-uri pentru pornirea/stergerea containerelor.

*run.sh* contine si comanda de build a imaginii adaptorului care face conexiunea intre brokerul de mesaje si baza de date influxdb. 

## stack.yml

Fisierul in care am integrat solutiile open-source + adaptorul in stack. 

*broker* - pentru acesta am folosit imaginea [eclipse-mosquitto:latest](https://hub.docker.com/_/eclipse-mosquitto). I-am atasat fisierul .conf pentru ca Mosquitto sa accepte conexiuni de la orice adresă IP si pentru a conexiuni anonime. Acesta asculta pe portul 1883 si foloseste reteua network-broker. 

*influxdb* - pentru acesta am folosit imaginea [influxdb:1.8](https://hub.docker.com/_/influxdb). Acesta asculta pe portun 8086 si foloseste retelele network-db si network-grafana. Persistenta datelor se face cu ajutorul volumului influxdb-data. 


*adapter* - acesta depinde atat de broker, cat si de influxdb, fiind intermediarul. Imaginea acestuia este construita din fisierul Dockerfile (tema3/adapter/Dockerfile). Apare si variabila de mediu DEBUG_DATA_FLOW pentru gestionarea log-urilor.

*grafana* - am folosit imaginea [grafana/grafana:latest](https://hub.docker.com/r/grafana/grafana) care asculta pe portul 3000, si utilizeaza user: admin, password: admin.

## adapter.py
Scriptul realizeaza urmatoarele actiuni: 

* se conecteaza la brokerul mqtt pe pentru a asculta toate mesajele publicate pe toate topicurile (#)
* mesajele primite sunt procesate, iar datele sunt extrase si validate conform cerintelor
* datele sunt scrise in influxdb









