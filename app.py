from flask import Flask, session
from flask import jsonify
from flask import request, Blueprint
from flask_restx import fields, Resource, Api
from flask_cors import CORS, cross_origin

#from pytezos.rpc import tzkt
#from conseil.api import ConseilApi
from datetime import timedelta
import requests
import json
import time
import urllib
import sys

# ROUTES

from routes.fa12_route import api as fa12_api
from routes.fa2_route import api as fa2_api
from routes.keys_route import api as keys_api
from routes.storage import api as storage_api

app = Flask(__name__)
app.secret_key = 'session_key'

cors = CORS(app, supports_credentials=True)

api = Api()
api = Api(version = 'v1.0.0', 
          title = 'Ungrund Oracle', 
          description= 'A decentralized API for publishing smart contracts on the Tezos Blockchain.',
          contact='hicetnunc2000@protonmail.com')

# NAMESPACES

api.add_namespace(fa12_api)
api.add_namespace(fa2_api)
api.add_namespace(storage_api)
api.add_namespace(keys_api)

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    
# REFERENCES

# https://flask-restplus.readthedocs.io/en/stable/scaling.html
# https://baking-bad.github.io/pytezos/
# https://github.com/baking-bad/pytezos/blob/a4ac0b022d35d4c9f3062609d8ce09d584b5faa8/pytezos/crypto.py
# https://forum.tezosagora.org/t/implementing-fa2-an-update-on-the-fa2-specification-and-smartpy-implementation-release/1870
# https://smartpy.io/dev/index.html?template=FA2.py
# https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-7/ManagedLedger.tz (FA1.2)

# BAKING REFERENCES

# https://gitlab.com/nomadic-labs/mi-cho-coq/raw/master/src/contracts/manager.tz
# https://tezos.gitlab.io/introduction/howtorun.html?highlight=delegate