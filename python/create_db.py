#!/usr/bin/python
import MySQLdb

db = MySQLdb.connect(host="mysql-mdf",    # your host, usually localhost
                     user="root",         # your username
                     passwd="insecure")  # your password
                     #db="jonhydb")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("CREATE DATABASE mdf;")
cur.execute("USE mdf;")
cur.execute("CREATE TABLE consumidor(hash_cpf VARCHAR(256) NOT NULL, num_nfs SMALLINT, status_coleta TINYINT, data_ult_coleta DATE, PRIMARY KEY(hash_cpf));")
cur.execute("CREATE TABLE nf(hash_cpf VARCHAR(256) NOT NULL, numero VARCHAR(32) NOT NULL, municipio VARCHAR(256), razao_social VARCHAR(512), emissao DATE, PRIMARY KEY (hash_cpf, numero));")
cur.execute("CREATE TABLE nf_item(hash_cpf VARCHAR(256) NOT NULL, numero VARCHAR(32) NOT NULL, desc VARCHAR(512) NOT NULL, codigo VARCHAR(128), qtd SMALLINT, val_unit DECIMAL(15,2), val_total DECIMAL(15,2) PRIMARY KEY (hash_cpf, numero, desc));")
print 'DB Creation successful.'

# print all the first cell of all the rows
#for row in cur.fetchall():
#    print row[0]

db.close()
