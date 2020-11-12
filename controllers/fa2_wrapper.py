from pytezos import pytezos, Key, Contract
import requests
import json

class FA2:
    def __init__(self):
        #self.contract = Contract.from_file('../smart_contracts/fa2.tz')
        self.symbol = lambda e: e[3]['value']

    # some of the parameters are left blank, but they can be edited or accessed by other methods
    def publish(self, network, tz, admin, **session):

        #forge case
        p = pytezos.using(key=tz, shell=network)
        fa2op = p.origination(script=self.contract.script(storage={"administrator": p.key.public_key_hash(
        ), "all_tokens": 0, "ledger": {}, "paused": False, "tokens": {}, "totalSupply": 0})).autofill().sign()
        fa2op.forge()


    def mint(self, fa2i, address, amount, symbol, token_id):
        fa2i.mint({"address": address, "amount": amount,
                "symbol": symbol, "token_id": token_id}).inject()


    # tz address might be relative
    def initialize_contract_instance(self, kt, tz, network):
        p = pytezos.using(key=tz, shell=network)
        fa2i = p.contract(kt)
        return fa2i

    # from_ / to_ ?
    def transfer(self, kt, tz, network, from_, to_, amount, token_id):
        fa2i = self.initialize_contract_instance(kt, tz, network)
        ret = fa2i.transfer([{"from_": from_, "to_": to_, "amount": amount, "token_id": token_id}])
        return ret

    def update_operators_some_tk(self, kt, tz, network, operator, owner, tokens):
        fa2i = self.initialize_contract_instance(kt, tz, network)
        fa2i.update_operators([{"Add_operator" : {"operator" : k2.public_key_hash(), "owner" : p.key.public_key_hash(), "tokens" : {"Some_tokens" : [2]}}}]).inject()
        return ret

    def get_ledger(self, kt, tz, network):
        fa2i = self.initialize_contract_instance(kt, tz, network)
        r_cartha = requests.get(
            "https://api.better-call.dev/v1/bigmap/{}/{}/keys".format(network, fa2i.storage()['ledger']))
        r_cartha = json.loads(r_cartha.content)
        # return [ e3['value'] for e3 in [ e2['children'][0] for e2 in [ e['data']['key'] for e in r_cartha ]]]
        return [{
            'address': e['data']['key']['children'][0]['value'],
            'id': int(e['data']['key']['children'][1]['value']),
            'balance': int(e['data']['value']['value'])
        } for e in r_cartha]


    def tokens_metadata(self, kt, tz, network):

        tokens = self.get_tokens(kt, tz, network)

        return [
            {
                'id': int(e['key']['value']),
                'total_supply': int(e['value']['children'][1]['value']),
                'metadata': self.symbol(e['value']['children'][0]['children'])
            } for e in tokens
        ]

    def get_tokens(self, kt, tz, network):
        fa2i = self.initialize_contract_instance(kt, tz, network)
        r = requests.get("https://api.better-call.dev/v1/bigmap/{}/{}/keys".format(network, fa2i.storage()['tokens']))
        # timestamps
        r = json.loads(r.content)
        return [e['data'] for e in r]

    def set_administrator(self, kt, tz, network, admin):
        fa2i = self.initialize_contract_instance(kt, tz, network)
        ret = fa2i.set_administrator(admin).operation_group.forge()
        return ret

    def set_pause(self, kt, tz, network, boolean):
        fa2i = self.initialize_contract_instance(kt, tz, network)
        ret = fa2i.set_pause(boolean).operation_group.forge()
        return ret
