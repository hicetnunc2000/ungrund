from flask import Blueprint, request, session
from pytezos import pytezos, Contract, Key
from pytezos.operation.result import OperationResult
from flask import Flask
from flask_restx import fields, Resource, Api, Namespace

from controllers.validate import Validate
from controllers.protocol_wrapper import Protocol

import distutils.util
import requests
import urllib
import json
#import redis

pytezos = pytezos
OperationResult = OperationResult
v = Validate()
#r = redis.Redis(host='localhost', port=6379, db=0)
api = Namespace('source', description='publish and other entrypoints')

@api.route('/publish')
@api.doc(params={
    'tz' : 'tz address',
    'meta' : 'IPFS hash',
    'goal' : 'tz amount',
    'network' : 'cartha/delphi/mainnet'
})
class publish_source(Resource):
    def post(self):

        try:
            protocol = Protocol()

            payload = v.read_requests(request)
            #pytz = v.read_session(session)
            #res = r.get(payload['auth'])
            print(payload)
            op = protocol.opensource_origin(payload['tz'], payload['meta'], int(payload['goal']))
            print(op)
            return op
        except:
            return 500

@api.route('/contribute')
@api.doc(params={
    'kt' : 'opensource kt address',
    'tz' : 'tz address',
    'amount' : 'amount',
    'network' : 'cartha/delphi/mainnet'
})
class contribute(Resource):
    def post(self):
        try:
            protocol = Protocol()
            payload = v.read_requests(request)
            op = protocol.contribute(payload['kt'], payload['tz'], payload['amount'])
            return op
        except:
            return 500

@api.route('/feed')
class search_sources(Resource):
    def get(self):
        opensource_sample = "KT1VkjE83HFNsS52uQGDTegYcQrCmqxv29U8"
        network = "mainnet"

        arr = []
        res = requests.get("https://api.better-call.dev/v1/contract/{}/{}".format(network, opensource_sample))
        arr.append(res.json())
        res = requests.get("https://api.better-call.dev/v1/contract/{}/{}/same".format(network, opensource_sample))
        filter = lambda arr : [ { 'address': e['address'], 'balance' : e['balance'] } for e in arr ] # if e['network'] == 'mainnet' else None
        #print(res.json()['contracts'])
        aux_arr = []
        p = pytezos.using(shell=network)
        arr.extend(res.json()['contracts'])
        for e in arr:

            print([e['address'], e['balance'], e['network']])

            if e['network'] == 'mainnet':
                contract = p.contract(e['address'])
                print(contract.storage())
                aux_arr.append({
                    'address' : e['address'],
                    'storage' : contract.storage(),
                    'balance' : e['balance'],
                    'percentage' : ((int(e['balance']) / 1000000)*100 / int(contract.storage()['goal']))
                })
        
        for e in aux_arr:
            e['storage']['goal'] = int(e['storage']['goal'])
            print(e)
            r = requests.post('https://fmn11y0q17.execute-api.us-east-2.amazonaws.com/py-ipfslambda2' , {'hash': e['storage']['meta']})
            print(r.text)
            #e['storage']['meta'] = json.loads(r.json())
        print(aux_arr)

        return aux_arr

@api.route('/kt')
@api.doc(params={
    'kt' : 'kt address',
    'network' : 'cartha/delphi/mainnet'
})
class search_kt(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            print(payload)
            res = requests.get("https://api.better-call.dev/v1/contract/mainnet/{}".format(payload['kt']))

            e = res.json()
            print(e)
            p = pytezos.using(shell='mainnet')
            c = p.contract(payload['kt'])

            storage = c.storage()
            print(storage)
            r = requests.post('https://fmn11y0q17.execute-api.us-east-2.amazonaws.com/py-ipfslambda2', {"hash": storage['meta']})
            j = json.loads(r.json())

            storage['goal'] = int(storage['goal'])
            
            return {
                'address' : payload['kt'],
                'timestamp' : e['timestamp'],
                'balance' : e['balance'],
                'storage' : storage,
                'title' : j['title'],
                'description' : j['description']
            }

        except:
            return 500

"""
    returns information such as balance and smart contract resources
"""
@api.route('/tz')
@api.doc(params={
    'tz' : 'tz address',
    'network' : 'cartha/delphi/mainnet'
})
class search_tz(Resource):
    def post(self):
        
        opensource_sample = "KT1VkjE83HFNsS52uQGDTegYcQrCmqxv29U8"
        network = "mainnet"

        payload = v.read_requests(request)
        print(payload)
        p = pytezos.using(key=payload['tz'], shell=network)

        arr = []
        res = requests.get("https://api.better-call.dev/v1/contract/{}/{}".format(network, opensource_sample))
        arr.append(res.json())
        res = requests.get("https://api.better-call.dev/v1/contract/{}/{}/same".format(network, opensource_sample))
        filter = lambda arr : [ { 'address': e['address'], 'balance' : e['balance'] } for e in arr ] # if e['network'] == 'mainnet' else None
        #print(res.json()['contracts'])
        aux_arr = []

        arr.extend(res.json()['contracts'])
        for e in arr:

            print([e['address'], e['balance'], e['network']])

            if e['network'] == 'mainnet':
                contract = p.contract(e['address'])
                print(contract.storage())
                if contract.storage()['admin'] == payload['tz']:
                    s = contract.storage()
                    s['goal'] = float(s['goal'])
                    aux_arr.append({
                        'address' : e['address'],
                        'storage' : s,
                        'balance' : float(e['balance']),
                        'percentage' : ((int(e['balance']) / 1000000)*100 / int(contract.storage()['goal']))
                    })
            
            print(aux_arr)
        return {
            "   results" : aux_arr
        }

@api.route('/withdraw')
@api.doc(params={
    'kt' : 'kt address',
    'tz' : 'tz address',
    'amount' : 'amount of tz to withdraw',
    'network' : 'cartha/delphi/mainnet'
})
class withdraw(Resource):
    def post(self):
        pass