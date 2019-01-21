#!/usr/bin/env sh
docker run -it --rm --network mqttnw --network-alias broker --hostname broker mqttbroker:latest
