from pytezos import Key, Contract, pytezos
from pytezos.operation.result import OperationResult
from decimal import *
import datetime
import requests
import json


class Protocol:
    def __init__(self):
        self.contract = Contract.from_file('./smart_contracts/protocol.tz')
        self.protocol = 'KT1AJfwziXDgJcAmT5t2iRb422NmjYn1FCa3'
        self.oracle = ''
        self.network = 'mainnet'

    def initialize_contract_instance(self, kt, tz):
        p = pytezos.using(key=tz, shell=self.network)
        protocol = p.contract(kt)
        return protocol

    def origination(self, tz, network, fa2, oracle):
        p = pytezos.using(key=tz, shell=network)
        ret = p.origination(script=self.contract.script(storage={ "auth" : {}, "fa2" : fa2, "oracle" : oracle, "counter": 0})).autofill().forge()
        return ret
    
    def opensource_origin(self, tz, meta, goal):

        protocol = self.initialize_contract_instance(self.protocol, tz)
        print(tz)
        print([meta, goal])
        ret = protocol.opensource_origin({'meta' : meta, "goal" : goal}).operation_group.forge()
        return ret

    def contribute(self, kt, tz, amount):
        protocol = self.initialize_contract_instance(kt, tz)
        ret = protocol.contribute(None).with_amount(Decimal(amount)).operation_group.forge()
        return ret

    def withdraw(self, kt, tz, amount):

        protocol = self.initialize_contract_instance(kt, tz)
        #ret = protocol.withdraw
        pass

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