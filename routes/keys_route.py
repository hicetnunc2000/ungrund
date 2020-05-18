
from flask import request, session
from flask_restx import fields, Resource, Api, Namespace
from werkzeug import FileStorage
from pytezos import Contract, Key
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from ast import literal_eval

import requests
import urllib
import json
import os

pytezos = pytezos

api = Namespace('keys', description='generate keys, activate, reveal')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                       type=FileStorage, required=True)

@api.route('/generate')
@api.doc(params={'password' : 'wallet password'})
# GET generate keys / password?
class gen_keys(Resource):
    def post(self):

        if (request.args.get('password', '') == None):
            key = Key.generate()
        else:
            key = Key.generate(request.args.get('password', ''))
        
        file_name = './{}.json'.format(key.public_key_hash())
        with open(file_name) as json_file:
            data = json.load(json_file)

        os.remove(file_name)

        data['secret_key'] = key.secret_key()

        return data

@api.route('/post_mneumonic')
@api.doc(params={ 'mneumonic' : 'wallet mneumonic', 'password' : 'wallet password' })
# POST mnemonic
class mneumonics(Resource):
    def post(self):
        
        #key = Key.from_mnemonic(request.args.get('mneumonic'))
        if (request.args.get('mneumonic', '') != None):
            arr = request.args.get('mneumonic', '')
            arr = literal_eval(arr)
            aux_str = ' '.join(arr)
            if (request.args.get('password', '') == None):
                key = Key.from_mnemonic(aux_str)
            else:
                key = Key.from_mnemonic(aux_str, request.args.get('password', ''))

            return key.public_key_hash()


# POST faucet / ledgers

# REVEAL ACTIVATION FAUCET WALLETS - TESTNET TOOL

@api.route('/activate')
@api.doc(params={'mneumonic' : "wallet's mneumonic", 'password': 'password'})
class activate(Resource):
    def post(self):
        if (request.args.get('mneumonic', '') != None):
            arr = request.args.get('mneumonic', '')
            arr = literal_eval(arr)
            aux_str = ' '.join(arr)
            if (request.args.get('password', '') == None):
                key = Key.from_mnemonic(aux_str)
            else:
                key = Key.from_mnemonic(aux_str, request.args.get('password', ''))

            p = pytezos.using(key=key, shell='https://carthagenet.SmartPy.io')
            p.activate_account.fill().sign().inject()
            return key.public_key_hash()

# Upload wallet

@api.route('/faucet')
@api.expect(upload_parser)
class faucet(Resource):
    @api.expect(type)
    def post(self):
        args = upload_parser.parse_args() # upload a file
        uploaded_file = args['file']
        return uploaded_file      
    

# generate keys.json in local storage? delete it? 
# register user id

