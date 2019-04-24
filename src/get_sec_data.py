#   Import statements
from splinter import Browser
from selenium import webdriver
import numpy as np, time
import pandas as pd
import re, requests, string, urllib
import bs4 as bs

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1420,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)

report_identifiers = ['DOCUMENT INFO',
                      'BALANCE SHEET', 'PARENTH. BALANCE SHEET',
                      'INCOME STATEMENT',
                      'SHAREHOLDERS EQUITY',
                      'CASH FLOW', 'PARENTH. CASH FLOW',
                      'COMPANY OVERVIEW']


#   Opens a browser to be used by the script
#       {type}:         Which browser should be opened
def open_browser(type='chrome', remove_head=True, ):
    from splinter import Browser
    return Browser(type, headless=remove_head)


#   Set the stock to get filings for and navigate to SEC page
#       {ticker}:     The ticker to be queried for
def set_stock(ticker='AAPL'):
    sec_search = 'https://www.sec.gov/edgar/searchedgar/companysearch.html'

    browser.visit(sec_search)

    sec_search_ticker = '//*[@id="cik"]'
    sec_ticker_search_button = '//*[@id="cik_find"]'

    #   Find and fill html element for search element
    search_bar = browser.find_by_xpath(sec_search_ticker)[0]
    search_bar.fill(ticker)

    #   Find and click html element for search button
    search_button = browser.find_by_xpath(sec_ticker_search_button)[0]
    search_button.click()


    #   Converts any given ticker into it's corresponding SEC-given CIK value


#       {ticker}:           The symbol you want converted
def ticker_to_cik(ticker='AAPL'):
    URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
    cik_dict = {}

    f = requests.get(URL.format(ticker), stream=True)
    results = CIK_RE.findall(f.text)
    if len(results):
        results[0] = int(re.sub('\.[0]*', '.', results[0]))
        cik_dict[str(ticker).upper()] = str(results[0])
        return results[0]


#   Counts the number of given filiings
#       {num_filings}:  Number of filings to grab
#       {do_print}:     Should the results be printed?
def find_all_filings(num_filings=7, print_result=False):
    #   Pull links to sec filings
    filings_10q = find_filings_by_type('10-Q', num_filings, print_result)
    filings_10k = find_filings_by_type('10-K', num_filings, print_result)
    filings_8k = find_filings_by_type('8-K ', num_filings, print_result)

    return filings_10k, filings_10q, filings_8k


#   Finds all filings of the given type for the current ticker
#       {filing_type}:      The type of SEC filing to be pulled
#       {print_results}:    Should the results be printed?
def find_filings_by_type(filing_type='10-K', num_filings=7, print_result=False):
    sec_search_filing = '//*[@id="type"]'
    sec_filing_search_button = '//*[@id="contentDiv"]/div[2]/form/table/tbody/tr/td[6]/input[1]'

    #   Find and fill html element for search element
    search = browser.find_by_xpath(sec_search_filing)[0]
    search.fill(filing_type)

    #   Find and click html element for search button
    search = browser.find_by_xpath(sec_filing_search_button)[0]
    search.click()

    time.sleep(0.5)

    if print_result:
        #   Find all filings of selected filing type
        #results = browser.find_by_css('a#interactiveDataBtn')
        accession_numbers = filing_numbers(filing_type, num_filings)

        #   Print dates for all filings in search results
        dates(filing_type, accession_numbers)

        #   Print number of filings found for type
        count(filing_type, accession_numbers)

        print('Filing Links Saved!')

        return accession_numbers

    else:
        #   Find all filings of selected filing type
        return filing_numbers(filing_type, num_filings)


#   Gets the accession numbers for the corresponding filing type
#       {filing_type}:          The type of SEC filing to be pulled
def filing_numbers(filing_type='10K', number_of_filings=7):
    numbers = []

    for x in range(0, number_of_filings):
        temp = browser.find_by_xpath('//*[@id="seriesDiv"]/table/tbody/tr[{}]/td[2]//*[@id="documentsbutton"]'.format(x + 2))
        temp = temp['href']
        numbers.append(re.search(r'^.*\/([^-]*)/.*$', temp, re.M).group(1))

    return numbers


#   Gets all reports included in the filings corresponding to the given accession number
#       {ticker}:           The stock you want reports for
#       {accession_number}: The SEC-given number indicating which filing is which
def get_all_formatted_reports(ticker='AAPL', accession_number='000162828016020309'):
    for x in range(1, 9):
        get_formatted_report(ticker, accession_number, x)


#   Gets a report included in the filings corresponding to the given accession number
#       {ticker}:           The stock you want a report for
#       {accession_number}: The SEC-given number indicating which filing is which
#       {report_number}:    Integer value correspondig to an index in the 'report_identifiers[]'
def get_formatted_report(ticker='AAPL', accession_number='000162828016020309', report_number=1):
    if report_number is 0:
        return print('Report number cannot be 0')

    cik = ticker_to_cik(ticker)
    base = 'https://www.sec.gov/Archives/edgar/data/{}/{}/R{}.htm'.format(cik, accession_number, report_number)
    print(base + '\n')

    soup = bs.BeautifulSoup(urllib.request.urlopen(base), 'lxml')
    table_rows = soup.find('table').find_all('tr')

    dt = []

    for row in table_rows:
        row_columns = row.find_all('td')

        for column in row_columns:
            dt.append(column.text.rstrip())

    alpha_cols = list(string.ascii_lowercase)
    alpha_cols = alpha_cols[:len(row_columns)]

    rows = len(table_rows)
    columns = len(row_columns)

    dt = dt + ([''] * (int(rows * columns) - int(len(dt))))

    df = pd.DataFrame(np.array(dt).reshape((rows), columns), columns=alpha_cols)
    return df


#   Counts the number of given filiings
#       {filing_type}:          The type of SEC filing to be pulled
#       {accession_numbers}:    The accession numbers for the given filing type
def count(filing_type='10K', accession_numbers=None):
    print(str(filing_type) + '\t' +
          str(len(accession_numbers) + ' Results Found'))


#   Gets the corresponding dates that go with each filing
#       {filing_type}:          The type of SEC filing to be pulled
#       {results}:              The accession numbers for the given filing type
def dates(filing_type='10K', results=None):
    results_index = 2

    for search_result in results:
        results_date = browser.find_by_xpath(
            '//*[@id="seriesDiv"]/table/tbody/tr['
            + str(results_index) + ']/td[4]')

        print(str(filing_type) + '\t' + results_date.text +
              '\t' + search_result["href"])

        results_index = results_index + 1


def get_filing(filing_type='10-K', ticker='AAPL'):
    set_stock(ticker)

    try:
        docs_10K = find_filings_by_type('10-K', 1)
        return get_formatted_report(ticker, docs_10K[0], 1)
    except urllib.error.HTTPError:
        print('An error occurred related to HTTP. This is likely a webpage discovery issue or incorrect URL')

    browser.quit()

browser = open_browser('chrome', False)