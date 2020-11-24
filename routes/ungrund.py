
from flask import Blueprint, request, session
from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from flask import Flask
from flask_restx import fields, Resource, Api, Namespace
import ipfshttpclient
from controllers.validate import Validate

import distutils.util
import requests
import urllib
import json
import os

pytezos = pytezos
OperationResult = OperationResult
v = Validate()

api = Namespace('objk', description='ipfs nfts minting and nft swap')


@api.route('/ipfs')
class publish_fa12(Resource):
    def post(self):
        print(request.files)
        conn = ipfshttpclient.connect('/dns4/ipfs.infura.io/tcp/5001/https')

        for e in request.files:
            path = "./{}".format(e)
            f = open(path, "wb")
            f.write(request.files[e].read())
            f.close()
            res = conn.add(path)
            os.remove(path)
        return res['Hash']
