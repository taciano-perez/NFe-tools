#! /usr/bin/env python
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/coletaNF")
def coletaNF():
	user = request.args.get('user', '')
	password = request.args.get('password', '')
	nf_count = scrapeNFdata(user, password)
	return "ColetaNF REST microservice " + user + " " + password + " " + str(nf_count)

def scrapeNFdata(user, password):
	return 2

	
if __name__ == "__main__":
    app.run(host= '0.0.0.0')