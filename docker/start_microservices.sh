#!/bin/bash
cd ..
docker build -f docker/Dockerfile_ColetaNF -t tacianoperez/coletanf .
#docker run -d --link mysql-mdf:mysql-mdf -p:5000:5000 --name ms_coletanf tacianoperez/coletanf sh -c "exec python NFe-tools/python/REST_coleta_nf.py"
docker run -it --link mysql-mdf:mysql-mdf -p:5000:5000 --name ms_coletanf tacianoperez/coletanf sh -c "exec python python/REST_coleta_nf.py"