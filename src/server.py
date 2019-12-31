from os import getenv
from flask import Flask, request, jsonify
from json import dumps, loads
from types import SimpleNamespace

from integrators.sec import get_cik, get_company, get_all_units, get_filings_by_type, get_filing_metadata, get_filing_documents
from integrators.yahoo_finance import get_earnings_calendar_by_day, get_earnings_calendar_by_ticker


app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    return jsonify({ 'message': 'ok' })


@app.route('/filings', methods = ['GET'])
def filings():
    args = valid_args(request.args, [ 'ticker', 'accessionNumber' ])
    if args is False:
        return 'Invalid parameters'

    return get_filing_metadata(args.ticker, args.accessionNumber)


@app.route('/filingdocuments', methods = ['GET'])
def filingdocuments():
    args = valid_args(request.args, [ 'ticker', 'accessionNumber' ])
    if args is False:
        return 'Invalid parameters'

    return loads(get_filing_documents(args.ticker, args.accessionNumber))


@app.route('/companies', methods = ['GET'])
def companies():
    args = valid_args(request.args, [ 'ticker' ])
    if args is False:
        return 'Invalid parameters'

    result = get_company(args.ticker)
    return result


@app.route('/units', methods = ['GET'])
def units():
    args = valid_args(request.args, [ ])
    if args is False:
        return 'Invalid parameters'

    result = get_all_units()
    return result


@app.route('/earnings', methods = ['GET'])
def earnings():
    args = valid_args(request.args, [ ])
    if args is False:
        return 'Invalid parameters'

    if hasattr(args, 'ticker'):
        return loads(get_earnings_calendar_by_ticker(args.ticker))
    elif hasattr(args, 'date'):
        return loads(get_earnings_calendar_by_day(args.date))
    else:
        return 'Invalid parameters'


def reformat_dataframe(dei):
    keys = dei.ix[:,0].values.tolist()
    keys = [str(x) for x in keys]
    values = dei.ix[:,1].values.tolist()
    values = [str(x) for x in values]

    return dict(zip(keys, values))


def valid_args(body, expected_params):
    if body is None:
        return False

    valid_args = {}
    for param in body:
        valid_args[param] = body[param]   

    for param in expected_params:
        if not body[param]:
            return False

    return SimpleNamespace(**valid_args)


if __name__ == '__main__':
    app.run(threaded=True, port=getenv('PORT', '5000'), host='0.0.0.0')