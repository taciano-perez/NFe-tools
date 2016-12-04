#!/bin/bash

cd ..

# create and run MySQL container
# FIXME: need to secure MySQL password
docker run --name mysql-mdf -e MYSQL_ROOT_PASSWORD=insecure -d mysql/mysql-server:5.7
sleep 5

# create DB
docker build -f docker/Dockerfile -t tacianoperez/dbclient .
docker run --rm --link mysql-mdf:mysql-mdf tacianoperez/dbclient sh -c "exec python python/create_db.py"

# interactive MySQL client
#docker run -it --link mysql-mdf:mysql-mdf tacianoperez/dbclient sh -c "mysql --host=mysql-mdf --password=insecure mdf"

# create and run microservice 'ColetaNF'
docker build -f docker/Dockerfile_ColetaNF -t tacianoperez/coletanf .
docker run -d --link mysql-mdf:mysql-mdf -p:5000:5000 --name ms_coletanf tacianoperez/coletanf sh -c "exec python python/REST_coleta_nf.py"

# interactive microservice container
#docker run -it --rm --link mysql-mdf:mysql-mdf -p:5000:5000 tacianoperez/coletanf sh -c "exec python NFe-tools/python/REST_coleta_nf.py"