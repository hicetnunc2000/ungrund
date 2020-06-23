
from flask import request, session, make_response
from flask_restx import fields, Resource, Api, Namespace
from flask_cors import CORS, cross_origin
from werkzeug import FileStorage
from werkzeug.datastructures import ImmutableMultiDict
from pytezos import Contract, Key
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from ast import literal_eval
from controllers.validate import Validate
import redis
import requests
import urllib
import json
import os
import uuid

pytezos = pytezos

api = Namespace('keys', description='generate keys, activate, reveal')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                       type=FileStorage, required=True)
                       
# POST key configuration from faucet wallet

@api.route('/faucet')
@api.expect(upload_parser)
@api.doc(params={ 
    'network' : 'mainnet / carthagenet' 
    })
class faucet(Resource):
    
    @api.expect(type)
    def post(self):
        try:
            args = upload_parser.parse_args()
            uploaded_faucet = args['file'].read()

            session['auth'] = 'faucet'
            session['faucet'] = uploaded_faucet
            session['network'] = request.args.get('network')
                
            p = Validate().read_session(session)
            
            return session

        except:
            return 500
    
# POST key configuration from mneumonic

@api.route('/post_mnemonic')
@api.doc(params = {
    'mnemonic' : 'wallet mnemonic', 
    'password' : 'wallet password' , 
    'email': 'wallet email',
    'network' : 'mainnet / carthagenet'
    })
class mnemonics(Resource):
    def post(self):
        try:

            session['auth'] = 'mnemonic'
            session['mnemonic'] = request.args.get('mnemonic')
            session['password'] = request.args.get('password')
            session['email'] = request.args.get('email')
            session['network'] = request.args.get('network', '')
                
            #p = Validate().read_session(session)

            return session

        except:
            return 500

@api.route('/post_secret')
@api.doc(params = { 
    'secret' : 'wallet secret key', 
    'password' : 'wallet password', 
    'network' : 'mainnet / carthagenet' 
    })
class secret_key(Resource):
    def post(self):
        uid = str(uuid.uuid4())
        #print(uid)
        #print(request.get_json())
        if (request.data.__len__() == 0):
            req = request.args.to_dict(flat=True)
            req['auth'] = 'secret'
            req['id'] = uid
            session['auth'] = 'secret'
            session['secret'] = req['secret']
            session['password'] = req['password']
            session['network'] = req['network']

        else:
            req = json.loads(request.data)
            req['id'] = uid
            session['auth'] = 'secret'
            session['secret'] = req['secret']
            session['password'] = req['password']
            session['network'] = req['network']
            #print(req)
        
        v = Validate()
        p = v.read_session(session)
        #session['id'] = uid
        #r.set(uid, json.dumps(req))
        
        return p.key.public_key_hash()

# POST password, return a faucet wallet
        
@api.route('/generate')
@api.doc(params={'password' : 'wallet password'})
class gen_keys(Resource):
    def post(self):

        if (request.data.__len__() == 0):
            if (request.args.get('password', '') == None):
                key = Key.generate()
            else:
                key = Key.generate(request.args.get('password', ''))
        else:
            password = json.loads(request.data).get("password")
            if (password != "") :
                key = Key.generate(password)
            else:
                key = Key.generate()

        file_name = './{}.json'.format(key.public_key_hash())
        
        with open(file_name) as json_file:
            data = json.load(json_file)

        os.remove(file_name)
        
        #activate / reveal

        data['secret_key'] = key.secret_key()

        return data

@api.route('/test_session')
class test_session(Resource):
    def get(self):
        return session['secret']
