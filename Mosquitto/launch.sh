#!/usr/bin/env sh
echo "docker run -it --rm --network mqttnw --network-alias broker --hostname broker mqttbroker:latest"
docker run -it --rm --network mqttnw --network-alias broker --hostname broker mqttbroker:latest
