from flask import Flask
from flask import jsonify
from flask import request

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
# from pytezos.rpc import tzkt

#from conseil.api import ConseilApi
from conseil.core import ConseilClient

import requests
import json
#import time
import urllib
import sys
from routes.petition_route import petition_api


app = Flask(__name__)
app.register_blueprint(petition_api)

conseil = ConseilClient()
pytezos = pytezos
OperationResult = OperationResult

# Set network
pytezos.using('babylonnet')

# Get wallet
with open('./faucets/tz1bm376dA6jG5yqyyWU984w9jws7xYc6pqJ.json') as json_file:
    data = json.load(json_file)

# Reveal/activate
# hicetnunc glitch microservice implements ConseilJS to activate faucet wallets
r = requests.post('http://hicetnunc.glitch.me/api/reveal', json=data)
 
pytezos.using(key=r.json().get('privateKey'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')