#!/usr/bin/env sh
echo "docker run -it -v /home/dwalsken/Dokumente/CSIS/Virt1/Project/DBSide/DB:/DB --rm --network mqttnw databaseside:latest"
docker run -it -v /home/dwalsken/Dokumente/CSIS/Virt1/Project/DBSide/DB:/DB --rm --network mqttnw databaseside:latest
