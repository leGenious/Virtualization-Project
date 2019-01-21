FROM alpine:latest

RUN ["apk", "--update", "add", "python2", "py2-pip"]
RUN ["pip2", "install", "--upgrade", "pip"]
RUN ["pip2", "install", "paho-mqtt"]

RUN ["mkdir", "src"]

CMD ["python2", "/src/database.py"]
