FROM python:3-alpine

RUN python -m pip install --upgrade pip

RUN pip3 install requests paho-mqtt

RUN mkdir DB

COPY DBSide.py /DBSide.py

CMD ["python3","/DBSide.py"]

