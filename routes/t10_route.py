from flask import Blueprint, request
from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult

from flask import Flask
from flask_restx import fields, Resource, Api, Namespace

import requests
import urllib

pytezos = pytezos
OperationResult = OperationResult

api = Namespace('t10', description='publish, torrent entrypoints')

@api.route('/publish')
@api.doc(params={'kt': 'A KT Address', 'ocasion' : 'Details on Ocasion',
'proposal' : 'Details of Proposal', 'time_out' : 'YYYY-MM-DD'})
class publish_t10(Resource):

    def get(self):
        contract = Contract.from_file('./smart_contracts/t10.tz')
        op = pytezos.origination(script=contract.script(storage={"admin":pytezos.key.public_key_hash(), "storage" : []})).autofill().sign().inject(_async=False, num_blocks_wait=2)    
        originated_kt = OperationResult.originated_contracts(op)
        return { 'kt' : originated_kt[0] }

@api.route('/insert')
@api.doc(params={'kt': 'A KT Address', 'info hash' : "torrent's info hash", 'magnet' : "torrent's magnet"})
class insert_t10(Resource):
    def post(self):

        ci = pytezos.contract(request.args.get('kt', ''))
        ci.call(addr = pytezos.key.public_key_hash(), info_hash = "a", magnet = "a").inject()
        print(ci)
        return { 'status' : 'applied' }