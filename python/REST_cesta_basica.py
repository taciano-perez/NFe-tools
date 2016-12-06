#! /usr/bin/env python
from flask import Flask
from flask import request
import MySQLdb
import sys
from datetime import date
from datetime import datetime

app = Flask(__name__)

@app.route("/cestabasica")
def cesta_basica():
	# get input arguments from request
	hash_cpf = request.args.get('hash_cpf', '')
	
	# get db connection and cursor
	db = MySQLdb.connect(host="mysql-mdf",    # your host, usually localhost
						 user="root",         # your username
						 passwd="insecure",  # your password
						 db="mdf")        	  # name of the data base
	cur = db.cursor()
	
	# dictionary with weighted products
	prods = {}

	# get min month/year and now
	# SELECT MONTH(min(nf.emissao)), YEAR(min(nf.emissao)) FROM nf;
	cur.execute("SELECT MONTH(min(nf.emissao)), YEAR(min(nf.emissao)) FROM nf")
	row = cur.fetchone()
	min_month = row[0]
	min_year = row[1]
	print "MIN",min_month, min_year
	now = datetime.now()
	print "NOW",now.year, now.month
	# traverse all months from min to now
	for year in range (min_year, now.year+1):
		mstart = 1
		mend = 13
		if year == min_year:
			mstart = min_month
		elif year == now.year:
			mend = now.month+1
		for month in range (mstart, mend):
			print "==============MONTH/YEAR==============", month, year
			# SELECT nf_item.descr, nf_item.qtd, nf_item.val_total FROM nf_item INNER JOIN nf ON nf.hash_cpf=nf_item.hash_cpf AND nf.numero=nf_item.numero WHERE MONTH(nf.emissao) = 11 AND YEAR(nf.emissao) = 2016;
			#cur.execute("SELECT nf_item.descr, nf_item.qtd, nf_item.val_unit, nf_item.val_total FROM nf_item INNER JOIN nf ON nf.hash_cpf=nf_item.hash_cpf AND nf.numero=nf_item.numero WHERE MONTH(nf.emissao) = %s AND YEAR(nf.emissao) = %s", (month, year))
			# TODO: add SUM(nf_item.qtd) ????
			cur.execute("SELECT DISTINCT nf_item.descr FROM nf_item INNER JOIN nf ON nf.hash_cpf=nf_item.hash_cpf AND nf.numero=nf_item.numero WHERE MONTH(nf.emissao) = %s AND YEAR(nf.emissao) = %s", (month, year))
			row = cur.fetchone()
			while row is not None:
				#print row[0], row[1], row[2], row[3]
				print row[0]
				descr = row[0]
				#qtd = float(row[1])
				#val_unit = float(row[2])
				#val_total = float(row[3])
				if descr not in prods:
					# add product to dictionary
					prods[descr] = 1 # score begins as 1
				else:
					# product already in dictionary, update score and qtd
					score = prods[descr]
					score = score+1
					prods[descr] = score
				row = cur.fetchone()
	
	# print products by score
	print '+++++++++++++++++ SCORE +++++++++++++++++++'
	prods_by_score = sorted(prods, key=prods.get, reverse=True)
	for descr in prods_by_score:
		print descr,prods[descr]
	
	# cleanup DB connection and cursor
	cur.close()
	db.close()
	
	# return results
	return "CestaBasica REST microservice " + hash_cpf

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
