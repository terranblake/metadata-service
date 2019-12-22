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

filings_namespaces = {
    'ns0': None, 
    '@text': None
}

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


def __xml_to_json(xml_obj, namespaces):
    return json.dumps(xmltodict.parse(ET.tostring(xml_obj), namespaces=namespaces))


def get_filing_metadata(ticker='AAPL', accession_number=""):
    company = get_company(ticker)

    base_link = '{}{}/{}/'.format(sec_base, get_cik(ticker), nodash(accession_number))
    filing_link = '{}{}-index.htm'.format(base_link, accession_number)
    filing = {}

    res = requests.get(filing_link, stream=True)
    root = html.fromstring(res.content)

    filing['source'] = 'sec'
    filing['refCompanyId'] = root.xpath('//*[@id="filerDiv"]/div[3]/span/a')[0].text.split(' ')[0]
    filing['type'] = root.xpath('//*[@id="filerDiv"]/div[3]/p/strong[4]')[0].text
    filing['refId'] = accession_number
    filing['period'] = root.xpath('//*[@id="formDiv"]/div[2]/div[2]/div[2]')[0].text
    filing['fiscalYearEnd'] = root.xpath('//*[@id="filerDiv"]/div[3]/p/strong[3]')[0].text
    filing['url'] = filing_link
    filing['name'] = root.xpath('//*[@id="formName"]/strong')[0].text
    filing['filedAt'] = root.xpath('//*[@id="formDiv"]/div[2]/div[1]/div[2]')[0].text
    filing['acceptedAt'] = root.xpath('//*[@id="formDiv"]/div[2]/div[1]/div[4]')[0].text
    filing['internalReveneServiceNumber'] = root.xpath('//*[@id="filerDiv"]/div[3]/p/strong[1]')[0].text

    return filing


def get_filing_documents(ticker='AAPL', accession_number="0000320193-17-000070"):
    company = get_company(ticker)

    base_link = '{}{}/{}/'.format(sec_base, get_cik(ticker), nodash(accession_number))
    filing_link = '{}{}-index.htm'.format(base_link, accession_number)

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
    extensions = extensions.to_json(orient='records')
    return extensions


def get_xbrl(ticker='AAPL', accession_number="0000320193-17-000070", xbrl_type="presentation"):
    filing_link = '{}{}/{}/{}-index.htm'.format(sec_base, get_cik(ticker), nodash(accession_number), accession_number)
    filing_detail = pd.read_html(filing_link)
    return filing_detail


def get_cik(ticker='AAPL'):
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
    f = requests.get(sec_company_details.format(ticker), stream=True)
    results = CIK_RE.findall(f.text)
    if len(results):
        return int(re.sub('\.[0]*', '.', results[0]))
    else:
        print('An error occurred while retrieving the CIK for {}'.format(ticker))


def get_company(ticker='AAPL'):
    try:
        f = requests.get(sec_company_details.format(ticker), stream=True)
        t = html.fromstring(f.content)

        company = {}
        company['ref'] = 'sec'
        company['refIndustryId'] = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/p/a[1]')[0].text.strip().lower()
        cik = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/span/a')[0].text.split(' ')[0].strip().lower()
        company['refId'] = cik.strip().lower()
        company['state'] = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/p/a[2]')[0].text.strip().lower()
        company['name'] = t.xpath('//*[@id="contentDiv"]/div[1]/div[3]/span/text()[1]')[0].strip().lower()
        company['ticker'] = ticker.strip().lower()
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
                exchange_to_json(exchange)


def exchange_to_json(exchange=None):
    import os, json
    base_path = os.path.abspath('./')
    input_path = '{}/raw/{}.txt'.format(base_path, exchange)

    companies = {}
    with open(input_path) as open_file:
        open_file.readline()
        line = open_file.readline()
        cnt = 1
        while line and cnt:
            split_line = line.split()
            ticker = split_line[0].strip().lower()
            company_name = ' '.join(split_line[1:]).strip().lower()
            company_info = get_company(ticker)

            line = open_file.readline()
            cnt += 1
        
        open_file.close()

    output_path = '{}/json/{}.json'.format(base_path, exchange)
    output_file = open(output_path, "w")
    output_file.write(json.dumps(companies, indent=4, sort_keys=True))
    output_file.close()


def get_filings_by_type(ticker="AAPL", filing_type="10-K", limit="1"):
    cik = get_cik(ticker)
    
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb=&owner=exclude&start=0&count={}&output=atom'.format(cik, filing_type, limit)
    f = requests.get(url.format(cik, filing_type, limit), stream=True)

    root = ET.fromstring(f.text)
    [root[1].insert(node, i) for node, i in enumerate(root[2:])]
    root[1][1].text = "filings"

    return __xml_to_json(root[1], filings_namespaces)