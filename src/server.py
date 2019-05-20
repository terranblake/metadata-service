from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps, loads
from types import SimpleNamespace

from get_sec_data import get_cik, get_company, get_filings_by_type, get_filing_metadata


app = Flask(__name__)
api = Api(app)


class FILING(Resource):
    def get(self):
        args = valid_args(request.args, [ 'ticker' ])
        if args is False:
            return 'Invalid parameters'

        # if (hasattr(args, 'filing_type') and args.accessionNumber is None):
        #     result = get_filings_by_type(args.ticker, args.filing_type)
        # else:
        result = get_filing_metadata(args.ticker, args.accessionNumber)
        return loads(result)


class COMPANY(Resource):
    def get(self):
        args = valid_args(request.args, [ 'ticker' ])
        if args is False:
            return 'Invalid parameters'

        result = get_company(args.ticker)
        return result


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
api.add_resource(COMPANY, '/companies')
# api.add_resource(DEI, '/dei')


if __name__ == '__main__':
     app.run(port='5000')