# create client DB container
FROM ubuntu:16.04
MAINTAINER Taciano Perez <tdperez@hotmail.com>
RUN apt-get update && apt-get install -y python-mysqldb mysql-client-5.7
ADD python/create_db.py python/create_db.py
#RUN git clone https://github.com/taciano-perez/NFe-tools
#RUN python NFe-tools/python/create_db.py
