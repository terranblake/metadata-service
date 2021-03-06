from os import getenv
from flask import Flask, request, jsonify
from json import dumps, loads
from types import SimpleNamespace

from integrations.sec import get_cik, get_company, get_all_units, get_filings_by_type, get_filing_metadata, get_filing_documents
from integrations.yahoo_finance import get_earnings_calendar_by_day, get_earnings_calendar_by_ticker


app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    return jsonify({ 'message': 'ok' })


@app.route('/filings', methods = ['GET'])
def filings():
    args = valid_args(request.args, [ 'ticker', 'accessionNumber' ])
    if args is False:
        return jsonify({ 'error': 'Invalid parameters' }), 200, { 'content-type': 'application/json' }

    return get_filing_metadata(args.ticker, args.accessionNumber), 200, { 'content-type': 'application/json' }


@app.route('/filingdocuments', methods = ['GET'])
def filingdocuments():
    args = valid_args(request.args, [ 'ticker', 'accessionNumber' ])
    if args is False:
        return jsonify({ 'error': 'Invalid parameters' }), 200, { 'content-type': 'application/json' }

    return get_filing_documents(args.ticker, args.accessionNumber), 200, { 'content-type': 'application/json' }


@app.route('/companies', methods = ['GET'])
def companies():
    args = valid_args(request.args, [ 'ticker' ])
    if args is False:
        return jsonify({ 'error': 'Invalid parameters' })

    result = get_company(args.ticker)
    return result, 200, { 'content-type': 'application/json' }


@app.route('/units', methods = ['GET'])
def units():
    args = valid_args(request.args, [ ])
    if args is False:
        return jsonify({ 'error': 'Invalid parameters' }), 200, { 'content-type': 'application/json' }

    result = get_all_units()
    return result, 200, { 'content-type': 'application/json' }


@app.route('/earnings', methods = ['GET'])
def earnings():
    args = valid_args(request.args, [ ])
    if args is False:
        return jsonify({ 'error': 'Invalid parameters' })

    if hasattr(args, 'ticker'):
        return get_earnings_calendar_by_ticker(args.ticker), 200, { 'content-type': 'application/json' }
    elif hasattr(args, 'date'):
        return get_earnings_calendar_by_day(args.date), 200, { 'content-type': 'application/json' }
    else:
        return jsonify({ 'error': 'Invalid parameters' }), 200, { 'content-type': 'application/json' }


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
    print(app.url_map)
    app.run(threaded=True, port=getenv('PORT', '5000'), host='0.0.0.0')