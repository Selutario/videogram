FROM ubuntu:22.04

ARG UID=1000
ARG GID=1000
LABEL maintainer="Selutario <selutario@gmail.com>"

RUN apt-get update && apt-get install git python3-pip -y
COPY ./src /videogram
RUN python3 -m pip install /videogram

RUN groupadd -g "${GID}" videogram && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" videogram
USER videogram

CMD ["videogram"]
