# @crzypatchwork

from flask import Blueprint, request, session
from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from flask import Flask
from flask_restx import fields, Resource, Api, Namespace
from controllers.validate import Validate

import requests
import urllib

pytezos = pytezos
OperationResult = OperationResult
v = Validate()

api = Namespace('fa2', description='publish and other entrypoints')

@api.route('/publish')
@api.doc(params={'admin': 'A tz1... public key hash Address'})
class publish_fa2(Resource):
    def get(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            contract = Contract.from_file('./smart_contracts/fa2.tz')
            op = pytz.origination(script=contract.script(storage={ "administrator" : pytezos.key.public_key_hash(), "all_tokens" : 0, "ledger" : {}, "paused" : False, "tokens" : {}, "totalSupply" : 0  })).fill().sign().inject(_async=False, num_blocks_wait=2)

            return v.filter_response(op)
        except:
            return 500

@api.route('/ledger')
@api.doc(params={
    'tz' : 'tz address',
    'network' : 'network'
})
class ledger(Resource):
    def post(self):
        """ try:
            
        except:
            return 500 """
        pass