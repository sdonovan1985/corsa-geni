FROM ubuntu:16.04

RUN apt update && apt install -y git python-virtualenv pypy python-pip

# Virtualenv setup
RUN virtualenv -p /usr/bin/pypy /appenv
RUN . /appenv/bin/activate

ENV PYTHONPATH $PYTHONPATH:/corsa-geni

RUN git clone https://github.com/sdonovan1985/corsa-geni.git

RUN pip install requests flask

COPY corsa-a.config /


CMD /bin/bash
