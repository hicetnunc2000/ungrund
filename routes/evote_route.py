from flask import Blueprint
from flask import request

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
import requests
import urllib

evote_api = Blueprint('evote_api', __name__)

@evote_api.route('/publish_evote', methods = ['GET'])
def publish():
    
    contract = Contract.from_file('./smart_contracts/proposition.tz')    
    op = pytezos.origination(script=contract.script()).autofill().sign().inject(_async=False, num_blocks_wait=2)    
    originated_kt = OperationResult.originated_contracts(op)
    return { 'kt' : originated_kt[0] }

@evote_api.route('/origin_evote', methods = ['GET'])
def origin():

    # https://baking-bad.github.io/pytezos/#access-storage
    t = int(requests.get('http://hicetnunc.glitch.me/api/timestamp/' + \
                                            request.args.get('time_out', '')).json().get('unix') / 1000)
    ci = pytezos.contract(request.args.get('kt', ''))
    ci.origin_entry(ocasion = urllib.parse.unquote(request.args.get('ocasion', '')), \
                    proposal = urllib.parse.unquote(request.args.get('proposal', '')), \
                    time_out = t).inject()
    
    return { 'status' : 'applied' }

@evote_api.route('/parties_evote', methods = ['GET'])
def parties_entry():
    
    ci = pytezos.contract(request.args.get('kt', ''))
    ci.parties_join(None).inject()
    
    return { 'status' : 'applied' }

@evote_api.route('/vote', methods = ['GET'])
def vote():
    ci = pytezos.contract(request.args.get('kt', ''))
    ci.vote(request.args.get('vote', '')).inject()
    
    return { 'status' : 'applied' }