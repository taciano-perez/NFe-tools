# NFe-tools
Tools for scraping info from the NFe website (with your user/password).

Currently tested with Python 2.7.

# Required packages
* mechanize
* cookielib
* BeautifulSoup4
* html2text
* urllib
* lxml

## Installing dependencies (on Ubuntu 16.04)
1. Install PIP: `sudo apt install python-pip`
2. Install Mechanize: `pip install mechanize`
3. Install BeautifulSoup4: `pip install BeautifulSoup4`
4. Install html2text: `pip install html2text`
5. Install LXML: `pip install lxml`

# How to run
* Edit `credentials.py` to set your username/password
* Run `python python/scrape_nfe.py`
