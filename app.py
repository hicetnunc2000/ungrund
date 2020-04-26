from flask import Flask
from flask import jsonify
from flask import request, Blueprint
from flask_restx import fields, Resource, Api

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from conseil.core import ConseilClient

#from pytezos.rpc import tzkt
#from conseil.api import ConseilApi

import requests
import json
#import time
import urllib
import sys

# ROUTES

from routes.petition_route import api as petition_api
from routes.storage import api as storage_api
from routes.evote_route import api as evote_api
from routes.keys_route import api as key_api
from routes.t10_route import api as t10_api

# INIT 5000 SERVER

app = Flask(__name__)
api = Api()
api = Api(version = 'zero', title = 'Ungrund dAPI', description= 'A decentralized API for querying and publishing immutable codes within the blockchain.')

# NAMESPACES

api.add_namespace(petition_api)
api.add_namespace(storage_api)
api.add_namespace(evote_api)
api.add_namespace(key_api)
api.add_namespace(t10_api)

# INIT TZ CONFIG
# singleton / config admin ???

conseil = ConseilClient()
pytezos = pytezos
OperationResult = OperationResult

# Set network
pytezos.using('https://carthagenet.SmartPy.io')

# Get wallet
with open('./faucets/tz1bm376dA6jG5yqyyWU984w9jws7xYc6pqJ.json') as json_file:
    data = json.load(json_file)

# Reveal/activate
# hicetnunc glitch microservice implements ConseilJS to activate faucet wallets
r = requests.post('http://hicetnunc.glitch.me/api/reveal', json=data)
 
pytezos.using(key=r.json().get('privateKey'))

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')