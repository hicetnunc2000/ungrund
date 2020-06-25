# @crzypatchwork

from flask import Blueprint, request
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
            contract = Contract.from_file('./smart_contracts/fa2.tz')
            op = pytezos.origination(script=contract.script(storage={ "administrator" : pytezos.key.public_key_hash(), "all_tokens" : 0, "ledger" : {}, "paused" : False, "tokens" : {}, "totalSupply" : 0  })).fill().sign().inject(_async=False, num_blocks_wait=2)
            originated_kt = OperationResult.originated_contracts(op)
            return v.filter_response(op)
        except:
            return 500