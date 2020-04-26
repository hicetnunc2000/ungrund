
from flask import request
from flask_restx import fields, Resource, Api, Namespace

from pytezos import Contract, Key
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from ast import literal_eval

import requests
import urllib
import json

pytezos = pytezos

api = Namespace('keys', description='generate keys, activate, reveal')

# get mnemonic / post password

@api.route('/generate')
# GET generate keys
# POST mnemonic password
class gen_keys(Resource):
    def get(self):
        key = Key.generate()
        with open('./{}.json'.format(key.public_key_hash())) as json_file:
            data = json.load(json_file)
        return data


@api.route('post_mneumonic')
@api.doc(params={ 'mneumonic' : 'wallet mneumonic', 'password' : 'wallet password' })
class load_wallet(Resource):
    def post(self):
        
        #key = Key.from_mnemonic(request.args.get('mneumonic'))
        arr = request.args.get('mneumonic')
        arr = literal_eval(arr)
        aux_str = ' '.join(arr)
        print(aux_str)
        key = Key.from_mnemonic(aux_str)

        # write a .json mneumonic + public key hash + password
        # Key.from_faucet()
        return key.public_key_hash()
        #return request.args.get('mneumonic')

# POST/LOAD FAUCET
 
# generate keys.json in local storage? delete it? 
# register user id