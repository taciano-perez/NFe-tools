##################################### Method 1
import mechanize
import cookielib
from bs4 import BeautifulSoup
import html2text
import urllib

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

#print(br.open('https://nfg.sefaz.rs.gov.br/cadastro/ConsultaDocumentos.aspx').read())
br.open('https://nfg.sefaz.rs.gov.br/cadastro/ConsultaDocumentos.aspx').read()

### CONSULTA

# data de emissao, todos os municipios
q_params = { 'pTipoData': '1', 'pDtInicial': '01012010', 'pDtFinal': '03112016', 'pCodMunicipio': '0' }

class PutRequest(mechanize.Request):
    "Extend the mechanize Request class to allow a http PUT"
    def get_method(self):
        return "PUT"

q_data = urllib.urlencode(q_params)
q_url = 'https://nfg.sefaz.rs.gov.br/Cadastro/ConsultaDocumentos_Do.aspx'
br.addheaders = [('Content-type', 'xml')]
#print br.open(PutRequest(q_url),data=q_data).read()
#response = mechanize.urlopen(request, data=data)
nfes_data =  br.open(q_url,data=q_data).read()
#print nfes_data
soup = BeautifulSoup(nfes_data, "lxml")

#table = soup.find('table')
#print 'soup.table =',soup.table

table = soup.find('table', attrs={'id': 'areaDocumentoTab'})
rows = table.findAll('tr')
# iterate through each NFE
for tr in rows:
    #tr = rows[1]
    cols = tr.findAll('td')
    # print NFE summary
    print '----------------------'
    print 'Municipio:',cols[0].string
    print 'Razao Social:',cols[1].string
    print 'Emissao:',cols[2].string
    print 'Numero:',cols[3].string
    #print '-->',cols[3].a['onclick']
    #print 'Origem:',cols[4].string
    print 'Valor(R$):',cols[6].string
    print 'Registro:',cols[7].string
    print 'Tipo Operacao:',cols[8].string

    # ignore NFe that are different than 'Aquisicao'
    if cols[8].string[:6] != 'Aquisi':
        print 'INFO: Ignorando NFe diferente de AquisiÃ§Ã£o.'
        continue

    # intermediate screen, we need to get chaveNFe here
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
    a = soup2.find('a', attrs={'target': '_blank'})
    #print a
    #print a['href']
    target_url = a['href']
    target_data = br.open(target_url).read()
    #print target_data

    chaveNFe = target_url.split('=')[1]

    # here we get the actual NFE contents
    form1_url = 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_1.asp'
    form1_args = urllib.urlencode({'chaveNFe': chaveNFe})
    br.open(form1_url, form1_args)
    br.select_form(nr=0)
    br.form['HML'] = ['false',]
    br.form['chaveNFe'] = chaveNFe
    r = br.submit()
    form1_data = r.get_data()
    soup3 = BeautifulSoup(form1_data, "lxml")
    nfe_table = soup3.findAll('table', attrs={'class': 'NFCCabecalho'})[3]
    #print nfe_table
    # print each NFE entry
    nfe_rows = nfe_table.findAll('tr')
    for nfe_tr in nfe_rows:
        nfe_cols = nfe_tr.findAll('td')
        print nfe_cols[0].string , nfe_cols[1].string, nfe_cols[2].string, nfe_cols[3].string, nfe_cols[4].string, nfe_cols[5].string
