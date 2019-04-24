from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps
from src.get_sec_data import get_filing

app = Flask(__name__)
api = Api(app, default_mediatype="json")

# request.args <- params
# request.get_json()[{key}] <- body

class DEI(Resource):
    def post(self):
        body = request.json
        filing_type = body['filing_type']
        ticker = body['ticker']
        result = get_filing(filing_type, ticker)
        return formatted_dataframe(result)
        

api.add_resource(DEI, '/dei')


def formatted_dataframe(obj):
    obj.set_index(obj['a'])
    obj_dict = obj.to_dict()

    obj = {}
    for a, b in zip(obj_dict['a'], obj_dict['b']):
        obj[obj_dict['a'][a]] = obj_dict['b'][b]

    return obj

if __name__ == '__main__':
     app.run(port='5000')