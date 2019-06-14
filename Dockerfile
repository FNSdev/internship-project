FROM phusion/baseimage:0.11

RUN mkdir /sandbox
WORKDIR /sandbox

RUN apt -y update
RUN apt -y upgrade
RUN apt install -y \
    python3.7 \
    python3-pip \
    python3.7-venv

COPY requirements.txt /sandbox/
COPY scripts/ /sandbox/scripts

RUN python3.7 -m venv /sandbox/venv
RUN bash /sandbox/scripts/pip_install.sh /sandbox

COPY sandbox/ /sandbox/sandbox
COPY runit/application /etc/service/application
RUN chmod +x /etc/service/application/run
COPY runit/celery /etc/service/celery
RUN chmod +x /etc/service/celery/run

EXPOSE 80