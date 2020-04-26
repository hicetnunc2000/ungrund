
from flask import request
from flask_restx import fields, Resource, Api, Namespace

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
import requests
import urllib

pytezos = pytezos

api = Namespace('evote', description='publish, originate details, sign')

@api.route('/publish_evote')
class Evote(Resource):
    def get(self):
        
        contract = Contract.from_file('./smart_contracts/proposition.tz')    
        op = pytezos.origination(script=contract.script()).autofill().sign().inject(_async=False, num_blocks_wait=2)    
        originated_kt = OperationResult.originated_contracts(op)
        return { 'kt' : originated_kt[0] }

@api.route('/origin_evote')
@api.doc(params={'kt': 'A KT Address', 'ocasion' : 'Details on Ocasion',
'proposal' : 'Details of Proposal', 'time_out' : 'YYYY-MM-DD'})
class OriginEvote(Resource):
    def post(self):

        # https://baking-bad.github.io/pytezos/#access-storage
        t = int(requests.get('http://hicetnunc.glitch.me/api/timestamp/' + \
                                                request.args.get('time_out', '')).json().get('unix') / 1000)
        ci = pytezos.contract(request.args.get('kt', ''))
        ci.origin_entry(ocasion = urllib.parse.unquote(request.args.get('ocasion', '')), \
                        proposal = urllib.parse.unquote(request.args.get('proposal', '')), \
                        time_out = t).inject()
        
        return { 'status' : 'applied' }

@api.route('/join_party')
@api.doc(params={'kt' : 'A KT Address'})
class JoinEvote(Resource):
    def post(self):
        
        ci = pytezos.contract(request.args.get('kt', ''))
        ci.parties_join(None).inject()
        
        return { 'status' : 'applied' }

@api.route('/vote')
@api.doc(params={'vote' : 'Y / N / Abs'})
class Vote(Resource):
    def post(self):
        ci = pytezos.contract(request.args.get('kt', ''))
        ci.vote(request.args.get('vote', '')).inject()
        
        return { 'status' : 'applied' }