#! /usr/bin/env python
from flask import Flask
from flask import request
import MySQLdb
import sys
import mechanize
import cookielib
from bs4 import BeautifulSoup
import html2text
import urllib
from datetime import date
from datetime import datetime

app = Flask(__name__)

@app.route("/coletaNF")
def coletaNF():
	# get input arguments from request
	user = request.args.get('user', '')
	password = request.args.get('password', '')
	# scrape NFe data
	nf_count = scrapeNFdata(user, password)
	return "ColetaNF REST microservice " + user + " " + password + " " + str(nf_count)

def scrapeNFdata(user, password):
	# get db connection and cursor
	db = MySQLdb.connect(host="mysql-mdf",    # your host, usually localhost
						 user="root",         # your username
						 passwd="insecure",  # your password
						 db="mdf")        	  # name of the data base
	cur = db.cursor()
	
	### process NFe
	# Browser
	br = mechanize.Browser()

	# debug?
	#br.set_debug_http(True)

	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	br.addheaders = [('User-agent', 'Chrome')]

	# Used for POST requests using mechanize
	class PutRequest(mechanize.Request):
		"Extend the mechanize Request class to allow a http PUT"
		def get_method(self):
			return "PUT"

	### LOGIN

	# The site we will navigate into, handling its session
	br.open('https://nfg.sefaz.rs.gov.br/Login/LoginNfg.aspx')

	# View available forms
	for f in br.forms():
		print f

	# Select the first (index zero) form
	br.select_form(nr=0)

	# User credentials
	from credentials import *
	br.form['nro_cpf_loginNfg_cabec'] = USER
	br.form['senha_loginNfg_cabec'] = PASSWORD

	# Login
	br.submit()

	### CONSULTA

	DATE_BEGIN = '01012010'
	DATE_END = date.today().strftime("%d%m%Y")
	MAX_NFE_PAGE = 219
	last_date = DATE_END    # this will be used later to make new queries each MAX_NFE_PAGE NFes loop

	# NFes are paged in groups of MAX_NFE_PAGE, so we need a loop to iterate through them
	finished = False
	nfe_count = 0
	nfe_count_round = 0 # each round is >=MAX_NFE_PAGE NFEs (the max number displayed by page)
	total_nfe = 1
	while finished == False:

		# condition for completing everything
		if nfe_count == total_nfe:
			finished = True
			continue

		# if we reached the MAX_NFE_PAGE mark, let's restart the loop
		if nfe_count_round == MAX_NFE_PAGE:
			nfe_count_round = 0
			DATE_END = last_date.strftime("%d%m%Y")

		# data de emissao, todos os municipios
		q_params = { 'pTipoData': '1', 'pDtInicial': DATE_BEGIN, 'pDtFinal': DATE_END, 'pCodMunicipio': '0' }

		q_data = urllib.urlencode(q_params)
		q_url = 'https://nfg.sefaz.rs.gov.br/Cadastro/ConsultaDocumentos_Do.aspx'
		br.addheaders = [('Content-type', 'xml')]
		nfes_data =  br.open(q_url,data=q_data).read()
		#print nfes_data
		soup = BeautifulSoup(nfes_data, "lxml")

		nfes_returned = soup.find('h3', attrs={'class': 'subtitle'}).contents[4]
		if nfe_count == 0:  # do this only in first iteration, before pagination
			total_nfe = int(nfes_returned)
			print 'Attempting to process NFe count =',total_nfe

		table = soup.find('table', attrs={'id': 'areaDocumentoTab'})
		rows = table.findAll('tr')
		# iterate through each NFE
		for tr in rows:
			# if we reached the total NFE amount, get out of loop
			if nfe_count == total_nfe:
				#print 'GETTING OUT OF LOOP'
				break
			# if we reached the MAX_NFE_PAGE mark, let's restart the loop
			if nfe_count_round == MAX_NFE_PAGE:
				break
			nfe_count += 1
			nfe_count_round += 1
			print 'Processing NFE #',nfe_count
			#print 'Round #',nfe_count_round
			#print 'NFe total = ',total_nfe
			try:    # will attempt to recover from exceptions by skipping to the next NFe
				cols = tr.findAll('td')
				#print cols
				if len(cols) < 9:
					#print nfes_data
					#print table
					print '---> Cols lenght == ', len(cols),' we don\'t know how to parse it. Ignoring NFe...'
					continue
				# print NFE summary
				print '----------------------'
				print 'Municipio:',cols[0].string
				print 'Razao Social:',cols[1].string
				print 'Emissao:',cols[2].string
				print 'Numero:',cols[3].string
				#print '-->',cols[3].a['onclick']
				print 'Origem:',cols[4].string
				print 'Valor(R$):',cols[6].string
				print 'Registro:',cols[7].string
				print 'Tipo Operacao:',cols[8].string
				print 'Situacao Documento:',cols[9].string
				
				hash_cpf = user
				nf_numero = cols[3].string
				nf_municipio = cols[0].string
				nf_razao_social = cols[1].string
				nf_emissao = cols[2].string

				# ignore NFe where Tipo Operacao is different from 'Aquisicao'
				if cols[8].string[:6] != 'Aquisi':
					print 'INFO: Ignorando NFe diferente de Aquisicao.'
					continue
				# ignore NFe where Situacao Documento is different from 'Normal'
				if cols[9].string[:6] != 'Normal':
					print 'INFO: Ignorando NFe diferente de Normal.'
					continue

				# update last_date for the next round
				last_date = datetime.strptime(cols[2].string, '%d/%m/%y')
				
				# insert NFe into DB
				DBinsertNF(db, cur, hash_cpf, nf_numero, nf_municipio, nf_razao_social, nf_emissao)

				# go to NFE dialog (clicking column 'Numero')
				onclick = cols[3].a['onclick'].split('\'')
				#print onclick
				nfe_params = {'pTipoDoctoOrig': onclick[3], 'pCodIntDoctoOrig': onclick[5], 'pCodIntRmov': onclick[7], 'pNomeContrib': onclick[9], 'pNomeSitDocto': onclick[11], 'pCodSitDocto': onclick[13], 'pCodIntDoctoCpf': onclick[15], 'pPaginaOrigem': onclick[1]}
				#print nfe_params
				nfe_data = urllib.urlencode(nfe_params)
				nfe_url = 'https://nfg.sefaz.rs.gov.br/Cadastro/ConsultaDocumentosDetalhe_Do.aspx'
				br.addheaders = [('Content-type', 'xml')]
				nfe_data = br.open(nfe_url,data=nfe_data).read()
				#print nfe_data
				soup2 = BeautifulSoup(nfe_data, "lxml")
				# if origem == Cupom Fiscal, data is right here
				if cols[4].string == 'Cupom Fiscal':
					#print nfe_data
					table_items = soup2.find('table', attrs={'class': 'resultadoPesquisaCep'})
					items_rows = table_items.findAll('tr')
					for items_tr in items_rows:
						items_hdrs = items_tr.findAll('th')
						items_cols = items_tr.findAll('td')
						if len(items_hdrs) == 5:   # avoid attempting to read empty lines
							print items_hdrs[0].string , items_hdrs[1].string, items_hdrs[2].string, items_hdrs[3].string, items_hdrs[4].string
						if len(items_cols) == 5:   # avoid attempting to read empty lines
							nf_codigo = items_cols[0].string
							nf_desc = items_cols[1].string
							nf_qtd  = int(items_cols[2].string)
							nf_val_total = float(items_cols[0].string)
							nf_val_unit = nf_val_total / nf_qtd
							print items_cols[0].string , items_cols[1].string, items_cols[2].string, items_cols[3].string, items_cols[4].string
							DBinsertNFitem(db, cur, hash_cpf, nf_numero, nf_codigo, nf_desc, nf_qtd, nf_un, nf_val_unit, nf_val_total)
					continue  # We've got the data, skip the rest

				# if origem == NFe, we need to get chaveNFe here and go to next page 'Clique Aqui'
				a = soup2.find('a', attrs={'target': '_blank'})
				#print a
				#print a['href']
				target_url = a['href']
				target_data = br.open(target_url).read()
				#print target_data
				form1_url = target_url.split('?')[0]
				#print 'form1_url=',form1_url
				chaveNFe = target_url.split('=')[1]

				# FIXME: we have trouble parsing URL 'https://www.sefaz.rs.gov.br/NFE/NFE-COM.aspx',
				#        so by now we'll focus only on 'https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx'
				#        In any case, it seems redudant with a "Cupom Fiscal"
				if form1_url != 'https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx':
					print 'Ignoring this NFe, since we don\'t know yet how to parse it :-(. However, it seems redundant with a Cupom Fiscal :-)'
					print 'URL=',form1_url
					continue

				# here we get the actual NFE contents
				form1_url = 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_1.asp'
				form1_args = urllib.urlencode({'chaveNFe': chaveNFe})
				form1_html = br.open(form1_url, form1_args).read()
				#print form1_html
				br.select_form(nr=0)
				br.form['HML'] = ['false',]
				br.form['chaveNFe'] = chaveNFe
				r = br.submit()
				form1_data = r.get_data()
				#print form1_data
				soup3 = BeautifulSoup(form1_data, "lxml")
				nfe_tables = soup3.findAll('table', attrs={'class': 'NFCCabecalho'})
				if len(nfe_tables) < 4:
					print 'Number of NFE tables less than 4, we don\'t know how to parse it. Ignoring...'
					continue
				nfe_table = nfe_tables[3]
				#print nfe_table
				# print each NFE entry
				nfe_rows = nfe_table.findAll('tr')
				for nfe_tr in nfe_rows:
					nfe_cols = nfe_tr.findAll('td')
					if (nfe_cols[2].string == 'Qtde'):	# skip headers
						continue
					nf_codigo = nfe_cols[0].string
					nf_desc = nfe_cols[1].string
					nf_qtd = nfe_cols[2].string
					nf_un = nfe_cols[3].string
					nf_val_unit = nfe_cols[4].string
					nf_val_total = nfe_cols[5].string
					print nfe_cols[0].string , nfe_cols[1].string, nfe_cols[2].string, nfe_cols[3].string, nfe_cols[4].string, nfe_cols[5].string
					DBinsertNFitem(db, cur, hash_cpf, nf_numero, nf_codigo, nf_desc, nf_qtd, nf_un, nf_val_unit, nf_val_total)
			except: # let's log the error and skip this NFe...
				print "Unexpected error:", sys.exc_info()[0]
				print 'Going to next NFe'
				continue

	return 2
	
def DBinsertNF(db, cur, hash_cpf, nf_numero, nf_municipio, nf_razao_social, nf_emissao) {
	print "inserting NF into DB"
	try:
		cur.insert("INSERT INTO nf VALUES (%s,%s,%s,%s,STR_TO_DATE('%s'), '%d%m%Y')", (hash_cpf, nf_numero, nf_municipio, nf_razao_social, nf_emissao))
		db.commit()
	except:
		print "DB error inserting NF, rolling back"
	   db.rollback()
}

def DBinsertNFitem(db, cur, hash_cpf, nf_numero, nf_codigo, nf_desc, nf_qtd, nf_un, nf_val_unit, nf_val_total):
	print "inserting NF item into DB"
	try:
		cur.insert("INSERT INTO nf_item VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (hash_cpf, nf_numero, nf_desc, nf_codigo, nf_qtd, nf_val_unit, nf_val_total))
		db.commit()
	except:
		print "DB error inserting NF entry, rolling back"
	   db.rollback()
	   
if __name__ == "__main__":
    app.run(host= '0.0.0.0')