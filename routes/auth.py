# @crzypatchwork

from flask import Blueprint, request, session
from pytezos import pytezos, Key, Contract
from pytezos.operation.result import OperationResult
from flask import Flask
from flask_restx import fields, Resource, Api, Namespace

from controllers.validate import Validate

import redis
import distutils.util
import requests
import urllib
import json
import uuid

pytezos = pytezos
OperationResult = OperationResult
v = Validate()
r = redis.Redis(host='localhost', port=6379, db=0)
api = Namespace('auth', description='forge operatioins to be signed')


@api.route('/origination')
@api.doc(params={
    'tz': 'tz address for which operation will be forged',
    'kt': 'kt address'
    # other possible parameters depending on the entrypoint
})
class forge_origination(Resource):
    def post(self):

        print(request.data)
        payload = v.read_requests(request)
        print(payload)

        pytz = pytezos.using(
            key=payload['tz'], 
            shell="mainnet"
            )


        #contract = Contract.from_file('./smart_contracts/fa12.tz')
        #op = pytz.origination(script=contract.script(storage={'ledger': {}, 'admin': pytz.key.public_key_hash(), 'paused': False, 'totalSupply': 1000000})).fill()
        contract = Contract.from_file('./smart_contracts/transaction2.tz')
        op = pytz.origination(script=contract.script(storage=2)).fill()
        print(op.json_payload())

        print(op.forge())
        # return op.json_payload()['contents'][0]
        res = {
            "code": [op.json_payload()['contents'][0]['script']['code']],
            "storage": op.json_payload()['contents'][0]['script']['storage'],
            "bytes": op.forge(),
            "operation": op.json_payload()
        }
        print(res)
        return res


@api.route('/sign')
@api.doc(params={
    'op': 'op to be signed',
    'sig': 'edsig...',
    'tz': 'tz1 address origin',
    'network' : 'network'
    # other possible parameters depending on the entrypoint
})

class sign_operation(Resource):
    def post(self):
        payload = v.read_requests(request)
        print(payload)
        signature = payload['sig']
        print(signature)
        payload['op']['signature'] = signature

        pytz = pytezos.using(key=payload['tz'], shell=payload['network'])
        op = pytz.operation_group(
            protocol=payload['op']['protocol'],
            branch=payload['op']['branch'],
            contents=payload['op']['contents'],
            #signature="edsig{}".format(payload['sig'])
            signature=signature
            )
        print(op.json_payload())
        res = op.fill().inject()
        print(res)
        return v.filter_response(res)

@api.route('/verify')
@api.doc(params={
    'msg': 'message',
    'pk': 'public key hash'
    # other possible parameters depending on the entrypoint
})
class verify_message(Resource):
    def post(self):
        
        payload = v.read_requests(request)
        v = Key.verify(payload['pk'], payload['msg'])
        pass


@api.route('/auth')
@api.doc(params={
    'tz' : 'tz address',
    'auth' : 'uuid'
})
class auth(Resource):
    def post(self):
        payload = v.read_requests(request)
        print(payload)

        uuid_tz = str(uuid.uuid4())
        r.set(uuid_tz, payload['tz'])
        r.expire(uuid_tz, 3600)
        return uuid_tz

