#!/bin/bash

#create MySQL container
# FIXME: need to secure MySQL password
docker run --name mysql-mdf -e MYSQL_ROOT_PASSWORD=insecure -d mysql/mysql-server:5.7
sleep 5

# create DB
docker build -t tacianoperez/dbclient .
docker run --rm --link mysql-mdf:mysql-mdf tacianoperez/dbclient sh -c "exec python NFe-tools/python/create_db.py"

# interactive MySQL client
#docker run -it --link mysql-mdf:mysql-mdf tacianoperez/dbclient /bin/bash
