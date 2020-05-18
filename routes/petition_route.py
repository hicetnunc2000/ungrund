from flask import Blueprint, request
from flask import Flask

from flask_restx import fields, Resource, Api, Namespace

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult

import requests
import urllib

pytezos = pytezos
OperationResult = OperationResult

api = Namespace('petition', description='publish, originate details, sign')

@api.route('/publish')
class Petition(Resource):
    def get(self):
        contract = Contract.from_file('./smart_contracts/petition.tz')    
        op = pytezos.origination(script=contract.script()).autofill().sign().inject(_async=False, num_blocks_wait=2)    
        originated_kt = OperationResult.originated_contracts(op)
        return { 'kt' : originated_kt[0] }

@api.route('/original_details')
@api.doc(params={'kt': 'An KT Address', 'ocasion' : 'Details on Ocasion',
'proposal' : 'Details of Proposal', 'description' : 'Description', 'time_out' : 'YYYY-MM-DD'})
class OriginCrowd(Resource):

    def post(self):
        t = int(requests.get('http://hicetnunc.glitch.me/api/timestamp/' + \
                                                request.args.get('time_out', '')).json().get('unix') / 1000)
        ci = pytezos.contract(request.args.get('kt', ''))
        ci.origin_entry(ocasion = urllib.parse.unquote(request.args.get('ocasion', '')), \
                        proposal = urllib.parse.unquote(request.args.get('proposal', '')), \
                        time_out = t, \
                        description = urllib.parse.unquote(request.args.get('description'))).inject()
        return { 'status' : 'applied' }

@api.route('/sign')
@api.doc(params={'kt': 'An KT Address', 'name' : 'Name of the party', 'id' : 'ID of the party'})
class SignPetition(Resource):

    def post(self):
        ci = pytezos.contract(request.args.get('kt', ''))
        ci.sign(name = request.args.get('name', ''), \
                cpf = request.args.get('id', '')).inject()

        return { 'status' : 'applied' }
