# https://smartpy.io/dev/?template=oracle.py

import smartpy as sp

# An Oracle is the on-chain incarnation of an Oracle provider
# It maintains a queue of requests of type request_type containing an amount
# paid, a sender, an entry_point and a list of parameters.

# Parameters of type parameters_type is a list of (name, dict) pairs.

value_type = sp.TVariant(int = sp.TInt, string = sp.TString, bytes = sp.TBytes)

def value_string(s):
    return sp.variant("string", s)

def value_bytes(s):
    return sp.variant("bytes", s)

def value_int(s):
    return sp.variant("int", s)

# Request parameters
parameters_type = sp.TList(sp.TPair(sp.TString, sp.TMap(sp.TString, value_type)))

def specify(spec, parameters = {}):
    return [(spec, parameters)]

# Full request specification type
request_type = sp.TRecord(amount            = sp.TNat,
                          target            = sp.TAddress,
                          job_id            = sp.TBytes,
                          parameters        = parameters_type,
                          timeout           = sp.TTimestamp,
                          client_request_id = sp.TNat)

class Oracle(sp.Contract):
    def __init__(self,
                 admin,
                 token_contract,
                 token_address       = None,
                 min_timeout_minutes = 5,
                 min_amount          = 0):
        self.token_contract = token_contract
        if token_address is None:
            token_address = token_contract.address
        self.init(admin               = admin,
                  active              = True,
                  min_timeout_minutes = min_timeout_minutes,
                  min_amount          = min_amount,
                  token               = token_address,
                  next_id             = 0,
                  requests            = sp.big_map(tkey = sp.TNat, tvalue = request_type.with_fields(client = sp.TAddress)),
                  reverse_requests    = sp.big_map(tkey = sp.TRecord(client = sp.TAddress, client_request_id = sp.TNat), tvalue = sp.TNat)
        )

    @sp.entry_point
    def create_request(self, client, params):
        sp.verify(sp.sender == self.data.token)
        sp.verify(self.data.active)
        amount         = params.amount
        target         = params.target
        job_id         = params.job_id
        parameters     = params.parameters
        timeout        = params.timeout
        sp.verify(self.data.min_amount <= amount)
        sp.verify(sp.now.add_minutes(self.data.min_timeout_minutes) <= timeout)
        client_request_id  = params.client_request_id
        new_request = sp.record(client            = client,
                                target            = target,
                                job_id            = job_id,
                                parameters        = parameters,
                                amount            = amount,
                                timeout           = timeout,
                                client_request_id = client_request_id)
        reverse_request_key = sp.record(client = client, client_request_id = client_request_id)
        sp.verify(~self.data.reverse_requests.contains(reverse_request_key))
        self.data.reverse_requests[reverse_request_key] = self.data.next_id
        self.data.requests[self.data.next_id] = new_request
        self.data.next_id += 1

    @sp.entry_point
    def setup(self, active, min_timeout_minutes, min_amount):
        sp.verify(self.data.admin == sp.sender)
        self.data.active              = active
        self.data.min_timeout_minutes = min_timeout_minutes
        self.data.min_amount          = min_amount

    @sp.entry_point
    def fulfill_request(self, request_id, result):
        # Please note that the target (i.e., the requestor) could refuse to receive the data.
        # We do not want to check active here since sp.sender == admin.
        sp.verify(self.data.admin == sp.sender)
        request = sp.local('request', self.data.requests[request_id]).value
        token  = sp.contract(self.token_contract.batch_transfer.get_type(), self.data.token, entry_point = "transfer").open_some()
        sp.transfer([sp.record(from_ = sp.to_address(sp.self), txs = [sp.record(to_ = self.data.admin, token_id = 0, amount = request.amount)])],
                    sp.tez(0),
                    token)
        target = sp.contract(sp.TRecord(client_request_id = sp.TNat, result = value_type), request.target).open_some()
        sp.transfer(sp.record(client_request_id = request.client_request_id, result = result), sp.mutez(0), target)
        del self.data.requests[request_id]

    @sp.entry_point
    def cancel_request(self, client_request_id):
        # We do not want to check active here (it would be bad for the client).
        # sp.sender needs to be validated; this process is done through the use of the reverse_request_key.
        reverse_request_key = sp.record(client = sp.sender, client_request_id = client_request_id)
        request_id = sp.local('request_id', self.data.reverse_requests[reverse_request_key]).value
        request = sp.local('request', self.data.requests[request_id]).value
        sp.verify(request.timeout <= sp.now)
        token  = sp.contract(self.token_contract.batch_transfer.get_type(), self.data.token, entry_point = "transfer").open_some()
        sp.transfer([sp.record(from_ = sp.to_address(sp.self), txs = [sp.record(to_ = request.client, token_id = 0, amount = request.amount)])],
                    sp.tez(0),
                    token)
        del self.data.requests[request_id]


# A Client is a smart contract that expects to be called by oracles.
# The simplest form of a Client contains a receive entry point (custom
# names are possible) with an arbitrary parameter type and expects to
# be called by the operator of an oracle called oracle_admin.

class Client_requester():
    def request_helper(self, amount, job_id, parameters, oracle, waiting_request_id, target, timeout_minutes = 5):
        sp.verify(~ waiting_request_id.is_some())
        target = sp.set_type_expr(target, sp.TContract(sp.TRecord(client_request_id = sp.TNat, result = value_type)))
        waiting_request_id.set(sp.some(self.data.next_request_id))
        token  = sp.contract(sp.TRecord(oracle = sp.TAddress, params = request_type), self.data.token, entry_point = "proxy").open_some()
        params = sp.record(amount        = amount,
                           target        = sp.to_address(target),
                           job_id        = job_id,
                           parameters    = parameters,
                           timeout       = sp.now.add_minutes(timeout_minutes),
                           client_request_id = self.data.next_request_id)
        sp.transfer(sp.record(oracle = oracle, params = params), sp.mutez(0), token)
        self.data.next_request_id += 1

    def cancel_helper(self, oracle, waiting_request_id):
        sp.verify(waiting_request_id.is_some())
        oracle_contract = sp.contract(sp.TNat, oracle, entry_point = "cancel_request").open_some()
        sp.transfer(waiting_request_id.open_some(), sp.mutez(0), oracle_contract)
        waiting_request_id.set(sp.none)

class Client_receiver():
    def check_receive(self, oracle, client_request_id, waiting_request_id, result):
        sp.verify(sp.sender == oracle)
        sp.verify(waiting_request_id.is_some() & (waiting_request_id.open_some() == client_request_id))
        waiting_request_id.set(sp.none)
        sp.set_type(client_request_id, sp.TNat)
        sp.set_type(result, value_type)

    def read_int(self, x):
        return x.open_variant("int")

    def read_bytes(self, x):
        return x.open_variant("bytes")

    def read_string(self, x):
        return x.open_variant("string")

# Example client, XTZUSD
class Client(sp.Contract, Client_requester, Client_receiver):
    def __init__(self, token, oracle, admin):
        self.init(admin          = admin,
                  oracle         = oracle,
                  token          = token,
                  xtzusd         = 0,
                  next_request_id    = 1,
                  waiting_xtzusd_id = sp.none,
                  )

    @sp.entry_point
    def set_xtzusd(self, client_request_id, result):
        self.check_receive(self.data.oracle, client_request_id, self.data.waiting_xtzusd_id, result)
        self.data.xtzusd = self.read_int(result)

    @sp.entry_point
    def request_xtzusd(self):
        self.request_helper(2, sp.bytes("0x"), specify("XTZUSD"), self.data.oracle, self.data.waiting_xtzusd_id, sp.self_entry_point("set_xtzusd"))

    @sp.entry_point
    def cancel_xtzusd(self):
        self.cancel_helper(self.data.oracle, self.data.waiting_xtzusd_id)

    @sp.entry_point
    def change_oracle(self, oracle):
        sp.verify(self.data.admin == sp.sender)
        sp.verify(~ self.data.waiting_xtzusd_id.is_some())
        self.data.oracle = oracle

# Oracle Requests are paid with tokens handled in an FA2 contract.
# The FA2 contract template is extended by a proxy entry point to
# ensure transfers to Oracle and payments are synchronized.

FA2 = sp.import_template("FA2.py")
class Link_token(FA2.FA2):
    @sp.entry_point
    def proxy(self, oracle, params):
        self.transfer.f(self, [sp.record(from_ = sp.sender, txs = [sp.record(to_ = oracle, token_id = 0, amount = params.amount)])])
        oracle_contract = sp.contract(sp.TRecord(client = sp.TAddress, params = request_type),
                                      oracle,
                                      entry_point = "create_request").open_some()
        sp.transfer(sp.record(client = sp.sender, params = params), sp.mutez(0), oracle_contract)

# This code was used to originate test contracts and is kept as an example
if False:
    @sp.add_test(name = "Origination")
    def test():
        scenario = sp.test_scenario()
        link_admin_address = sp.address('tz1UBSgsJTTBQWGieRPZmwG3gpAy3kHd7N4y')
        link_token = Link_token(FA2.FA2_config(), link_admin_address)
        scenario += link_token
        link_token_address = sp.address('KT1U313dYFyMiU2aQnVCLgsFYUodz3JcdAMy')

        oracle1_admin_address = sp.address('tz1fextP23D6Ph2zeGTP8EwkP5Y8TufeFCHA')
        oracle1 = Oracle(oracle1_admin_address, link_token, token_address = link_token_address)
        scenario += oracle1
        oracle1_address = sp.address('KT1VDAWUJr3ZjJ4rsaXqsR4Y9VrrUN2u6GJX')

        client1_admin_address = sp.address('tz1axGtTkg1hJvGenTrhqpFbW1S8GcQpPdve')
        client1 = Client(link_token_address, oracle1_address, client1_admin_address)
        scenario += client1
        client1_address = sp.address('KT1Q9TX4D6irwQwMiQJR8MGXEWKbFtD7hwTn')


if "templates" not in __name__:
    @sp.add_test(name = "Oracle")
    def test():
        scenario = sp.test_scenario()

        scenario.table_of_contents()

        scenario.h2("Accounts")
        admin = sp.test_account("Administrator")
        oracle1 = sp.test_account("Oracle1")

        client1_admin = sp.test_account("Client1 admin")
        client2_admin = sp.test_account("Client2 admin")

        scenario.show([admin, oracle1, client1_admin, client2_admin])

        scenario.h2("Link Token")
        link_token = Link_token(FA2.FA2_config(), admin.address)
        scenario += link_token
        scenario += link_token.mint(address = admin.address,
                                    amount = 100,
                                    symbol = 'tzLINK',
                                    token_id = 0).run(sender = admin)

        scenario.h2("Oracle")
        oracle = Oracle(oracle1.address, link_token)
        scenario += oracle

        scenario.h2("Client1")
        client1 = Client(link_token.address, oracle.address, client1_admin.address)
        scenario += client1

        scenario.h2("Client2")
        client2 = Client(link_token.address, oracle.address, client2_admin.address)
        scenario += client2

        scenario.h2("Tokens")
        scenario += link_token.transfer([sp.record(from_ = admin.address, txs = [sp.record(to_ = client1.address, token_id = 0, amount = 20)])]).run(sender = admin)
        scenario += link_token.transfer([sp.record(from_ = admin.address, txs = [sp.record(to_ = client2.address, token_id = 0, amount = 20)])]).run(sender = admin)
        scenario += link_token.transfer([sp.record(from_ = admin.address, txs = [sp.record(to_ = oracle.address , token_id = 0, amount = 1)])]).run(sender = admin)
        scenario += link_token.transfer([sp.record(from_ = admin.address, txs = [sp.record(to_ = oracle1.address, token_id = 0, amount = 1)])]).run(sender = admin)

        scenario.h2("Client1 sends a request that gets fulfilled")
        scenario.h3("A request")
        scenario += client1.request_xtzusd()

        scenario.h3("Ledger")
        scenario.show(link_token.data.ledger)

        scenario.h3("Oracle consumes the request")
        scenario.verify_equal(oracle.data.requests[0].parameters, [('XTZUSD', {})])
        scenario += oracle.fulfill_request(request_id = 0, result = value_int(2500000)).run(sender = oracle1)

        scenario.h2("Client1 sends a request that gets cancelled")
        scenario.h3("A request")
        scenario += client1.request_xtzusd()

        scenario.h3("Ledger")
        scenario.show(link_token.data.ledger)

        scenario.h3("Client1 cancels the request")
        scenario.verify_equal(oracle.data.requests[1].parameters, [('XTZUSD', {})])
        scenario += client1.cancel_xtzusd().run(now = sp.timestamp(400))

        scenario.h2("Client2 sends a request that gets fulfilled")
        scenario.h3("A request")
        scenario += client2.request_xtzusd()

        scenario.h3("Ledger")
        scenario.show(link_token.data.ledger)

        scenario.h3("Oracle consumes the request")
        scenario.verify_equal(oracle.data.requests[2].parameters, [('XTZUSD', {})])
        scenario += oracle.fulfill_request(request_id = 2, result = value_int(2500000)).run(sender = oracle1)