FROM ubuntu:18.04

RUN mkdir /home/dump
RUN apt-get update -y
RUN apt-get install tcpdump -y
RUN apt-get install tshark -y

ENTRYPOINT ["tail", "-f", "/dev/null"]
