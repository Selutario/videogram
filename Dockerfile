FROM ubuntu:20.04

COPY ./src /videogram

RUN apt-get update && apt-get install git python3-pip -y
RUN pip3 install /videogram

CMD ["videogram"]
