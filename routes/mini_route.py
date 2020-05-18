# -*- coding: utf-8 -*-
from flask import request, g
from flask_restx import fields, Resource, Api, Namespace
from werkzeug import FileStorage
#from mini import key
from pytezos import Contract, Key
from pytezos import pytezos
from pytezos.operation.result import OperationResult

import requests
import urllib
import json
import os

pytezos = pytezos

api = Namespace('fa2', description='publish, mint, sign')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                       type=FileStorage, required=True)


@api.route('/publish_fa2')
#@api.doc(params={'kt': 'A KT Address', 'ocasion' : 'Details on Ocasion',
#'proposal' : 'Details of Proposal', 'time_out' : 'YYYY-MM-DD'})
@api.expect(upload_parser)
class FA2(Resource):
    def post(self):
        
        # Initialize key configuration
        args = upload_parser.parse_args() # upload a file
        uploaded_file = json.loads(args['file'].read())
        
        path = './faucets/{}.json'.format(uploaded_file['pkh'])
        mne = ' '.join(uploaded_file['mnemonic'])
        #uploaded_file['mnemonic'] = mne
        data = {}
        
        with open(path, 'w') as outfile:
            json.dump(uploaded_file, outfile)
            
        #print (uploaded_file)
        #print (os.system('pwd'))
        k = Key.from_faucet('./faucets/{}.json'.format(uploaded_file['pkh']))
        
        # Pytezos config
        
        p = pytezos.using(key=k, shell='https://carthagenet.SmartPy.io')
        
        # Describe arguments
        
        contract = Contract.from_file('./smart_contracts/crowd.tz')    
        op = p.origination(script=contract.script()).autofill().sign().inject(_async=False, num_blocks_wait=2)    
        originated_kt = OperationResult.originated_contracts(op)
        return { 'kt' : originated_kt[0] }

# Describe entrypoints
    
# Upload ledger



