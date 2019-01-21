FROM python:3-alpine

RUN python -m pip install --upgrade pip

RUN pip3 install requests paho-mqtt

COPY NumSide.py /NumSide.py

CMD ["python3","/NumSide.py"]

