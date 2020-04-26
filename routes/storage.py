
from flask import request

from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult

from flask import Flask
from flask_restx import fields, Resource, Api, Namespace

pytezos = pytezos

api = Namespace('storage', description='get kt storage')

@api.route('/full')
@api.doc(params={'kt': 'An KT Address' })
class Storage(Resource):

    def get(self):

        ci = pytezos.contract(request.args.get('kt', ''))
            
        return ci.storage()