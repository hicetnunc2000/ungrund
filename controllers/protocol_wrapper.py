from pytezos import Key, Contract, pytezos
from pytezos.operation.result import OperationResult
from decimal import *
import datetime
import requests
import json

class Protocol:
    def __init__(self):
        self.contract = Contract.from_file('./smart_contracts/protocol.tz')
        self.protocol = 'KT1BESj6UfiHbHGQo2aWzktRjxguBd1mrbYG'  
        #self.protocol = 'KT1NKPzq6Rz1Kv5L4MbXdh5hE7rmV2NGbYkH' #cartha
        self.oracle = ''
        self.network = 'mainnet'

    def initialize_contract_instance(self, kt, tz):
        p = pytezos.using(key=tz, shell=self.network)
        protocol = p.contract(kt)
        return protocol

    def origination(self, tz, network, fa2, oracle):
        
        p = pytezos.using(key=tz, shell=network)
        op = p.origination(script=self.contract.script(storage={"fa2" : fa2, "opensources" : {}, "oracle" : oracle, "paused" : False, "tk_counter" : 1})).autofill()
        forge = op.forge()
        print([op, forge])
        return [op, forge]
    
    def opensource_origin(self, tz, meta, goal):

        protocol = self.initialize_contract_instance(self.protocol, tz)
        print(tz)
        print([meta, goal])
        
        op = protocol.originate_opensource({"goal" : goal, 'meta' : meta}).operation_group
        forge = op.forge()
        payload = op.json_payload()
        print ([forge, payload])
        return [forge, payload]

    def contribute(self, kt, tz, amount):
        protocol = self.initialize_contract_instance(kt, tz)
        ret = protocol.contribute(None).with_amount(Decimal(amount)).operation_group.forge()
        return ret

    def withdraw(self, kt, tz, address, amount):
        protocol = self.initialize_contract_instance(kt, tz)
        ret = protocol.withdraw([{"address" : address, "amount" : amount}]).operation_group.forge()
        return ret

    def get_opensources(self, contract_i):

        r = requests.get('https://api.better-call.dev/v1/bigmap/{}/{}/keys'.format(self.network, contract_i.storage()['auth']))
        return [ {
            "key" : e['data']['key']['value'],
            "value" : e['data']['value']['value'] # add a tz address + token id record
        } for e in json.loads(r.content) ]

    # administrator
    def update_adm(self, kt, tz, adm):
        protocol = self.initialize_contract_instance(kt, tz)
        ret = protocol.update_adm(adm).operation_group.forge()
        return ret