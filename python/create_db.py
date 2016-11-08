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
cur.execute("CREATE TABLE consumidor(hash_cpf VARCHAR(256), num_nfs SMALLINT, status_coleta TINYINT, data_ult_coleta DATE);")
print 'DB Creation successful.'

# print all the first cell of all the rows
#for row in cur.fetchall():
#    print row[0]

db.close()
