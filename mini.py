# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify
from flask import request, Blueprint
from flask_restx import fields, Resource, Api

from pytezos import Contract, Key
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from conseil.core import ConseilClient

#from pytezos.rpc import tzkt
#from conseil.api import ConseilApi

import requests
import json
import time
import urllib
import sys

# ROUTES

from routes.mini_route import api as mini_api

# INIT 5000 SERVER

app = Flask(__name__)
api = Api()
api = Api(version = 'zero', title = 'Ungrund Oracle', description= 'A decentralized API for querying and publishing immutable codes within the blockchain.')

# NAMESPACES

api.add_namespace(mini_api)

# INIT TZ CONFIG


conseil = ConseilClient()
pytezos = pytezos
OperationResult = OperationResult
#key = Key
# Set network
pytezos.using('https://carthagenet.SmartPy.io')

# Get wallet
with open('./faucets/tz1bm376dA6jG5yqyyWU984w9jws7xYc6pqJ.json') as json_file:
    data = json.load(json_file)

# Reveal/activate
# hicetnunc glitch microservice implements ConseilJS to activate faucet wallets
#r = requests.post('http://hicetnunc.glitch.me/api/reveal', json=data)

# Multiple key configurations

#pytezos.using(key=r.json().get('privateKey'))

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    