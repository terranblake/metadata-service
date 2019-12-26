from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps, loads
from types import SimpleNamespace

from integrators.sec import get_cik, get_company, get_all_units, get_filings_by_type, get_filing_metadata, get_filing_documents
from integrators.yahoo_finance import get_earnings_calendar_by_day, get_earnings_calendar_by_ticker


app = Flask(__name__)
api = Api(app)


class FILING(Resource):
    def get(self):
        args = valid_args(request.args, [ 'ticker', 'accessionNumber' ])
        if args is False:
            return 'Invalid parameters'

        return get_filing_metadata(args.ticker, args.accessionNumber)


class DOCUMENT(Resource):
    def get(self):
        args = valid_args(request.args, [ 'ticker', 'accessionNumber' ])
        if args is False:
            return 'Invalid parameters'

        return loads(get_filing_documents(args.ticker, args.accessionNumber))


class COMPANY(Resource):
    def get(self):
        args = valid_args(request.args, [ 'ticker' ])
        if args is False:
            return 'Invalid parameters'

        result = get_company(args.ticker)
        return result


class UNIT(Resource):
    def get(self):
        args = valid_args(request.args, [ ])
        if args is False:
            return 'Invalid parameters'

        result = get_all_units()
        return result


class EARNINGS(Resource):
    def get(self):
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


api.add_resource(FILING, '/filings')
api.add_resource(DOCUMENT, '/filingdocuments')
api.add_resource(COMPANY, '/companies')
api.add_resource(UNIT, '/units')
api.add_resource(EARNINGS, '/earnings')
# api.add_resource(DEI, '/dei')


if __name__ == '__main__':
     app.run(port='5000')