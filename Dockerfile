FROM ubuntu:22.04

RUN apt-get update && apt-get install git python3-pip -y

COPY ./src /videogram
RUN python3 -m pip install /videogram
RUN useradd -ms /bin/bash videogram

USER videogram
CMD ["videogram"]
