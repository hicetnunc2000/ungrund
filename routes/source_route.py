from flask import Blueprint, request, session
from pytezos import pytezos, Contract, Key
from pytezos.operation.result import OperationResult
from flask import Flask
from flask_restx import fields, Resource, Api, Namespace

from controllers.validate import Validate
from controllers.protocol_wrapper import Protocol
from controllers.fa2_wrapper import FA2

import ipfshttpclient
import distutils.util
import requests
import urllib
import json
#import redis

protocol = Protocol()
fa2 = FA2()
client = ipfshttpclient.connect('/dns4/ipfs.infura.io/tcp/5001/https')
pytezos = pytezos
OperationResult = OperationResult
v = Validate()
#r = redis.Redis(host='localhost', port=6379, db=0)
api = Namespace('source', description='publish and other entrypoints')


@api.route('/publish')
@api.doc(params={
    'tz': 'tz address',
    'meta': 'IPFS hash',
    'goal': 'tz amount',
    'network': 'cartha/delphi/mainnet'
})
class publish_source(Resource):
    def post(self):

        payload = v.read_requests(request)
        return protocol.opensource_origin(
            payload['tz'], payload['meta']['hash'], int(payload['goal']))


@api.route('/contribute')
@api.doc(params={
    'kt': 'opensource kt address',
    'tz': 'tz address',
    'amount': 'amount',
    'network': 'cartha/delphi/mainnet'
})
class contribute(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            return protocol.contribute(
                payload['kt'], payload['tz'], payload['amount'])
        except:
            return 500


@api.route('/feed')
class search_sources(Resource):
    def get(self):

        # get opensources from bigmap
        opensource_sample = "KT1UcPh3S1K1GAFqUt212H9qjFVdxEnca1qk"
        network = "mainnet"

        arr = []
        res = requests.get(
            "https://api.better-call.dev/v1/contract/{}/{}".format(network, opensource_sample))
        arr.append(res.json())
        res = requests.get(
            "https://api.better-call.dev/v1/contract/{}/{}/same".format(network, opensource_sample))

        # if e['network'] == 'mainnet' else None
        #def filter(arr): return [
        #    {'address': e['address'], 'balance': e['balance']} for e in arr]
        # print(res.json()['contracts'])
        aux_arr = []
        p = pytezos.using(shell=network)
        arr.extend(res.json()['contracts'])
        print(arr)
        for e in arr:

            if e['network'] == 'mainnet' and e['manager'] == 'KT1Q72pNNiCnBamwttWvXGE9N2yuz6c7guSD':

                balance = requests.get('https://api.better-call.dev/v1/account/{}/{}'.format(network, e['address']))
                balance = balance.json()['balance']
                print(e['address'])
                contract = p.contract(e['address'])
                print(contract.storage())
                storage = contract.storage()
                r = requests.post(
                'https://37kpt5uorg.execute-api.us-east-1.amazonaws.com/dev/get_ipfs', {"hash": storage['meta']})
                meta = json.loads(r.json())
                aux_arr.append({
                    'address': e['address'],
                    'storage': contract.storage(),
                    'balance': int(balance),
                    'percentage': round(((int(balance) / 1000000)*100 / int(contract.storage()['goal'])), 2),
                    'meta' : meta
                })

        for e in aux_arr:
            e['storage']['goal'] = int(e['storage']['goal'])
            e['storage']['achieved'] = int(e['storage']['achieved'])
            print(e)
            #r = requests.post('https://fmn11y0q17.execute-api.us-east-2.amazonaws.com/py-ipfslambda2' , {'hash': e['storage']['meta']})
            # print(r.text)
            #e['storage']['meta'] = json.loads(r.json())
        print(aux_arr)

        return aux_arr


@api.route('/kt')
@api.doc(params={
    'kt': 'kt address',
    'network': 'cartha/delphi/mainnet'
})
class search_kt(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            print(payload)
            res = requests.get(
                "https://api.better-call.dev/v1/contract/mainnet/{}".format(payload['kt']))

            e = res.json()
            print(e)
            p = pytezos.using(shell='mainnet')
            c = p.contract(payload['kt'])

            storage = c.storage()
            print(storage)
            r = requests.post(
                'https://37kpt5uorg.execute-api.us-east-1.amazonaws.com/dev/get_ipfs', {"hash": storage['meta']})
            print(r.json())
            meta = json.loads(r.json())
            print(meta)
            storage['goal'] = int(storage['goal'])
            storage['achieved'] = int(storage['achieved'])
            print(meta['title'])
            
            balance = requests.get('https://api.better-call.dev/v1/account/{}/{}'.format('mainnet', e['address']))
            balance = balance.json()['balance']

            return {
                'address': payload['kt'],
                'timestamp': e['timestamp'],
                'balance': int(balance),
                'storage': storage,
                'title': meta['title'],
                'description': meta['description'],
                'links' : meta['links'],
                'percentage': round(((int(balance) / 1000000)*100 / storage['goal']), 2)
            }

        except:
            return 500


"""
    returns information such as balance and smart contract resources
"""


@api.route('/tz')
@api.doc(params={
    'tz': 'tz address',
    'network': 'cartha/delphi/mainnet'
})
class search_tz(Resource):
    def post(self):

        opensource_sample = "KT1UcPh3S1K1GAFqUt212H9qjFVdxEnca1qk"
        network = "mainnet"

        payload = v.read_requests(request)
        print(payload)
        p = pytezos.using(key=payload['tz'], shell=network)

        arr = []
        res = requests.get(
            "https://api.better-call.dev/v1/contract/{}/{}".format(network, opensource_sample))
        arr.append(res.json())
        res = requests.get(
            "https://api.better-call.dev/v1/contract/{}/{}/same".format(network, opensource_sample))

        # if e['network'] == 'mainnet' else None
        def filter(arr):
            return [
                {'address': e['address'], 'balance': e['balance']} for e in arr
            ]
        # print(res.json()['contracts'])
        aux_arr = []

        arr.extend(res.json()['contracts'])
        for e in arr:
            print(e['address'])

            if e['network'] == 'mainnet' and e['manager'] == 'KT1Q72pNNiCnBamwttWvXGE9N2yuz6c7guSD':
                balance = requests.get('https://api.better-call.dev/v1/account/{}/{}'.format(network, e['address']))
                balance = balance.json()['balance']
                contract = p.contract(e['address'])
                print(contract.storage())
                if contract.storage()['admin'] == payload['tz']:
                    s = contract.storage()
                    s['goal'] = int(s['goal'])
                    s['achieved'] = int(s['achieved'])
                    aux_arr.append({
                        'address': e['address'],
                        'storage': s,
                        'balance': int(balance),
                        'percentage': ((int(balance) / 1000000)*100 / int(contract.storage()['goal']))
                    })

            print(aux_arr)
            tokens_meta = fa2.get_ledger('KT1Ex8LrDbCrZuTgmWin8eEo7HFw74jAqTvz', payload['tz'], 'mainnet')
            print(tokens_meta)

        return {
            "results": aux_arr,
            "token_meta" : [e if e['address'] == payload['tz'] else None for e in tokens_meta],
            "balance" : int(p.balance())
        }


@api.route('/withdraw')
@api.doc(params={
    'kt': 'kt address',
    'tz': 'tz address',
    'amount': 'amount of tz to withdraw',
    'network': 'cartha/delphi/mainnet'
})
class withdraw(Resource):
    def post(self):
        payload = v.read_requests(request)
        print(payload)
        op = protocol.withdraw_funds(payload)
        return op


@api.route('/resources')
@api.doc(params={
    'tz': 'tz address',
    'network': 'cartha/delphi/mainnet'
})
class resources(Resource):
    def post(self):
        payload = v.read_requests(request)
        print(payload)
        r = requests.get('http://localhost:5000/source/feed')
        arr = r.json()
        print(arr)
        aux_arr = []

        for e in arr:
            #print (e)
            if e['storage']['admin'] == payload['tz']:
                aux_arr.append(e)

        return aux_arr

@api.route('/post_ipfs')
class post_json(Resource):
    def post(self):
        payload = v.read_requests(request)
        print(payload)
        cid = client.add_json(payload)
        print(cid)
        return {'hash':cid}
