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
import json

pytezos = pytezos
OperationResult = OperationResult
v = Validate()
api = Namespace('fa12', description='publish and other entrypoints')

@api.route('/publish')
@api.doc({
    'total_supply' : 'total supply of tokens'
})
class publish_fa12(Resource):
    def post(self):

        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            contract = Contract.from_file('./smart_contracts/fa12.tz')
            op = pytz.origination(script=contract.script(storage={'ledger': {}, 'admin': pytz.key.public_key_hash(
                ), 'paused': False, 'totalSupply': payload['total_supply']})).fill().sign().inject(_async=False, num_blocks_wait=2)
                # originated_kt = OperationResult.originated_contracts(op)
                # op['contents'][0]['metadata']
                # op['hash']

            #return OperationResult.originated_contracts(op)[0]
            return v.filter_response(op)
        except:
            return 500

@api.route('/transfer')
@api.doc(params={'contract': 'fa12 contract address',
                 'from': 'public key hash',
                 'to': 'public key hash',
                 'value': 'amount (nat)'
                 })
class transfer_fa12(Resource):
    def post(self):
        
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            ci = pytz.contract(payload['contract'])
            r = ci.transfer({'from' : payload['from'], "to" : payload['to'], "value" : payload['value']}).inject()

            return r
        except:
            return 500

@api.route('/approve')
@api.doc(params={
    'contract': 'fa12 KT contract address',
    'spender': 'tz address',
    'value': 'value (nat)'
})
class approve_fa12(Resource):
    def post(self):

        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            ci = pytz.contract(payload['contract'])
            r = ci.approve({"spender" : payload['spender'], "value" : int(payload['value'])}).inject()

            #ret = v.filter_response(r)

            return r
        except:
            return 500

@api.route('/get_allowance')
@api.doc(params={
    'contract': 'fa12 KT contract address',
    'owner': 'tz address',
    'spender': 'tz address'
#    'contract_2': 'response view KT address'
})
class get_allowance_fa12(Resource):
    def post(self):

        payload = v.read_requests(request)
        pytz = v.read_session(session)
        
        ci = pytz.contract(payload['contract'])

        j = {}
        j['owner'] = payload['owner']
        j['approvals']['spender'] = ci.big_map_get(payload['owner']['approvals'][payload['spender']])
        
        return j

# Maintance View
@api.route("/get_balance")
@api.doc({
    'contract': 'fa12 KT contract address',
    'owner': 'tz address'
#    'contract_1': 'callback KT address'
})
# "contract_1": $contract (nat)
class get_balance_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            ci = pytz.contract(payload['contract'])
            
            j = {}
            j['owner'] = payload['owner']
            j['balance'] = ci.big_map_get(payload['owner'])['balance']

            return j
        except:
            return 500

# Maintence View
@api.route('/get_total_supply')
@api.doc({
    'contract' : 'fa12 KT contract address'
})
class get_total_supply_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            ci = pytz.contract(payload['contract'])
            
            r = {}
            aux = ci.storage()
            r['total_supply'] = aux['totalSupply']
            
            return r
        except:
            return 500

@api.route('/set_pause')
@api.doc({
    "contract" : "fa12 KT contract address",
    "bool" : "boolean True or False"
})
class set_pause_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            ci = pytz.contract(payload['contract'])
            r = ci.setPause(json.loads(payload['bool'].lower())).inject()

            # ret = v.filter_response(r)
            
            return r
        except:
            return 500

@api.route('/set_administrator')
@api.doc({
    'contract' : 'fa12 KT contract address',
    'adm' : 'tz address'
})
class set_administrator_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            ci = pytz.contract(payload['contract'])
            r = ci.setAdministrator(payload['adm']).inject()

            # ret = v.filter_response(r)

            return r
        except:
            return 500

# Maintence
# Get adm
@api.route('/get_administrator')
@api.doc({
    'kt' : 'fa12 KT contract address'
})
class get_administrator_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            
            ci = pytz.contract(payload['contract'])
            
            r = {}
            aux = ci.storage()
            r['admin'] = aux['admin']

            return r
        except:
            return 500

@api.route('/mint')
@api.doc({
    'contract' : 'fa12 kt address',
    'to' : 'tz address destination',
    'value' : 'nat'
})
class mint_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            ci = pytz.contract(payload['contract'])
            r = ci.mint({"to" : payload['to'], "value": int(payload['amount'])}).inject()
            #ret = v.filter_response(r)
            return r
        except:
            return 500

@api.route('/burn')
@api.doc({
    'contract' : 'fa12 kt address',
    'from' : 'tz address',
    'value' : 'nat'
})
class burn_fa12(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            ci = pytz.contract(payload['contract'])
            r = ci.burn({"from" : payload['from'], "value": int(payload['amount'])}).inject()

            #ret = v.filter_response(r)
            return r
        except:
            return 500

