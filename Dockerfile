FROM ubuntu:14.04
MAINTAINER Yasser Nabi "yassersaleemi@gmail.com"
EXPOSE 53 53/udp
ENV SSH_AUTH_SOCK /ssh_auth_sock

ENV DEBIAN_FRONTEND noninteractive

RUN sed 's/main$/main universe/' -i /etc/apt/sources.list && \
        apt-get update && \
        apt-get -y install \
            python \
            python-git \
            bind9

ADD ./git_bind_update.py /git_bind_update.py
ADD ./named.conf.options /etc/bind/named.conf.options

ENTRYPOINT ["/usr/bin/python", "/git_bind_update.py"]
