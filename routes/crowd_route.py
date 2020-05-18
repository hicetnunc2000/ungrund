from flask import Blueprint, request
from flask_restx import fields, Resource, Api, Namespace

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
import requests
import urllib

pytezos = pytezos

api = Namespace('evote', description='publish, originate details, sign')
pytezos = pytezos
OperationResult = OperationResult

crowd_api = Blueprint('crowd_api', __name__)

@crowd_api.route('/publish_crowd', methods = ['GET'])
def publish_crowd():
    
    contract = Contract.from_file('./smart_contracts/crowd.tz')    
    op = pytezos.origination(script=contract.script()).autofill().sign().inject(_async=False, num_blocks_wait=2)    
    originated_kt = OperationResult.originated_contracts(op)
    return { 'kt' : originated_kt[0] }

@crowd_api.route
def send_fund():
    pass

@crowd_api.route
def pay_off():
    pass

@crowd_api.route
def refund():
    pass