import numpy as np, time
import pandas as pd
import re, requests, string, urllib
import bs4 as bs
import xml.etree.ElementTree as ET
import xmltodict
from lxml import html, etree
from bs4 import BeautifulSoup
import json
import xml.dom.minidom
from collections import namedtuple
import os


xbrl_units_registry = "http://www.xbrl.org/utr/utr.xml"
sec_company_details = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
sec_base = 'https://www.sec.gov/Archives/edgar/data/'

filings_namespaces = { 'ns0': None, '@text': None }
units_namespaces = { 
    'ns0': None, 
    'ns1': None, 
    '@id': 'id',
}

xbrl_types = {
    'presentation': 'pre',
    'calculation': 'calc',
    'definition': 'def',
    'label': 'lab'
}


def nodash(d): return ''.join(d.split('-'))
def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)


def pretty_print_xml(xml_string):
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml()


def get_companies_csv():
    path = './raw/cik_ticker.csv'
    return pd.read_csv(path, '|')


def __xml_to_json(xml_obj, namespaces):
    return json.dumps(xmltodict.parse(ET.tostring(xml_obj), namespaces=namespaces))


def get_filing_metadata(ticker='AAPL', accession_number="0000320193-17-000070"):
    company = get_company(ticker)
    print(company)

    base_link = '{}{}/{}/'.format(sec_base, get_cik(ticker), nodash(accession_number))
    filing_link = '{}{}-index.htm'.format(base_link, accession_number)
    print('base', base_link)

    extensions = pd.read_html(filing_link)
    extensions = pd.concat(extensions)
    extensions.rename(
        columns={
            'Seq': 'sequence', 
            'Description': 'description',
            'Document': 'fileName',
            'Type': 'fileType',
            'Size': 'fileSize',
            },
        inplace=True
    )
    extensions['url'] = base_link + extensions.fileName
    print(extensions)
    extensions = extensions.to_json(orient='records')
    return extensions


def get_xbrl(ticker='AAPL', accession_number="0000320193-17-000070", xbrl_type="presentation"):
    filing_link = '{}{}/{}/{}-index.htm'.format(sec_base, get_cik(ticker), nodash(accession_number), accession_number)
    filing_detail = pd.read_html(filing_link)
    return filing_detail

# TODO :: Implement polling system to check
#            for new tickers on an interval
# http://rankandfiled.com/#/data/tickers
def get_cik(ticker='AAPL'):
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')

    print(sec_company_details)
    f = requests.get(sec_company_details.format(ticker), stream=True)
    results = CIK_RE.findall(f.text)
    if len(results):
        return int(re.sub('\.[0]*', '.', results[0]))
    else:
        print('An error occurred while retrieving the CIK for {}'.format(ticker))


def get_company(ticker='AAPL'):
    print('getting identifiers for {}'.format(ticker))
    try:
        f = requests.get(sec_company_details.format(ticker), stream=True)
        t = html.fromstring(f.content)

        company = {}
        company['sic'] = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/p/a[1]')[0].text
        cik = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/span/a')[0].text.split(' ')[0]
        company['cik'] = cik
        company['state'] = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/p/a[2]')[0].text
        company['name'] = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/span/text()[1]')[0]
        company['ticker'] = ticker
        return company
    except IndexError as e:
        print('there was a problem fetching data for {}'.format(ticker))
        return None, None


def get_all_units():
    try:
        f = requests.get(xbrl_units_registry, stream=True)
        root = ET.fromstring(f.text)
        root = root[0]

        result = __xml_to_json(root, units_namespaces)
        result = json.loads(result)
        return { 'units': result['units']['unit'] }
    except IndexError as e:
        print('there was a problem units from xbrl registry')
        return None, None


def all_exchanges_to_json(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                exchange = file.split('/')[-1].split('.txt')[0]
                print(exchange)
                exchange_to_json(exchange)


def exchange_to_json(exchange=None):
    import os, json
    base_path = os.path.abspath('./')
    input_path = '{}/raw/{}.txt'.format(base_path, exchange)

    companies = {}
    with open(input_path) as open_file:
        print('opened {}'.format(input_path))
        open_file.readline()
        line = open_file.readline()
        cnt = 1
        while line and cnt:
            split_line = line.split()
            ticker = split_line[0]
            company_name = ' '.join(split_line[1:])
            company_info = get_company(ticker)

            line = open_file.readline()
            cnt += 1
        
        open_file.close()
        print('closed {}'.format(input_path))

    output_path = '{}/json/{}.json'.format(base_path, exchange)
    output_file = open(output_path, "w")
    print('opened {}'.format(output_path))
    output_file.write(json.dumps(companies, indent=4, sort_keys=True))
    output_file.close()
    print('closed {}'.format(output_path))


def get_filings_by_type(ticker="AAPL", filing_type="10-K", limit="1"):
    cik = get_cik(ticker)
    
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb=&owner=exclude&start=0&count={}&output=atom'.format(cik, filing_type, limit)
    print(url)
    f = requests.get(url.format(cik, filing_type, limit), stream=True)

    root = ET.fromstring(f.text)
    [root[1].insert(node, i) for node, i in enumerate(root[2:])]
    root[1][1].text = "filings"

    return __xml_to_json(root[1], filings_namespaces)


# has ticker lists that are processed
# using exchange_to_json
# http://www.eoddata.com/symbols.aspx
# exchange_to_json('NASDAQ')
# all_exchanges_to_json('./raw')
# companies = get_companies_csv().to_json(orient='records')
# output_file = open('./json/all_companies.json', "w")
# output_file.write(companies)