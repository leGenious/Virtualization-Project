#!/usr/bin/env sh
docker run -it --rm --network mqttnw --hostname broker mqttbroker:latest&
docker run -it -v /home/dwalsken/Dokumente/CSIS/Virt1/Project/DBSide/DB:/DB --rm --network mqttnw databaseside:latest&
docker run -it --rm --network mqttnw numside:latest&
