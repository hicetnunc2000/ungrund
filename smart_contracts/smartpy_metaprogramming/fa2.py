# FA2
# ===
#
# Multi-asset contract.
#
# Cf. https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-12/fa2_interface.mligo
#
# WARNING: as of now this script requires a unreleased version of SmartPy
# (it's only for the test scenario though, contract itself should be fine
# with /dev)


import smartpy as sp


################################################################################
# Global Parameters
#
def global_parameter(env_var, default):
    try:
        if os.environ[env_var] == "true" :
            return True
        if os.environ[env_var] == "false" :
            return False
        return default
    except:
        return default


debug_mode = global_parameter("debug_mode", False)
# Use map instead of big-maps and things like that

readable = global_parameter("carthage_pairs", True)
# User-accounts are big-maps: (user-address * token-id) -> ownership-info
#
# For Babylon, one should use `readable = False` to use `PACK` on the pair:
#

force_layouts = global_parameter("force_layouts", False)
# The spec requires records to be right-combs; we keep this parameter around
# to be able to compare performance & code-size.


support_operator = global_parameter("support_operator", True)
# The operator entry-points have to be there, but there is definitely a use-case
# for completely not having them.

assume_consecutive_token_ids = global_parameter(
    "assume_consecutive_token_ids", True)
# If true we don't need a set of token ids, just the last one.

if debug_mode:
    my_map = sp.map
else:
    my_map = sp.big_map

################################################################################

token_id_type = sp.TNat
# This is the type from the spec:
#
#     type transfer = {
#       from_ : address;
#       to_ : address;
#       token_id : token_id;
#       amount : nat;
#     }
#
class Transfer:
    def get_from(t): return t.from_
    def get_to(t): return t.to_
    def get_token_id(t): return t.token_id
    def get_amount(t): return sp.set_type(t.amount, sp.TNat)
    def get_type():
        return sp.TRecord(from_ = sp.TAddress,
                          to_ = sp.TAddress,
                          token_id = token_id_type,
                          amount = sp.TNat)
    def set_type_and_layout(expr):
        sp.set_type(expr, Transfer.get_type())
        if force_layouts:
            sp.set_record_layout(expr, ("from_", ("to_", ("token_id", "amount"))))
    def make(f,t,a,i):
        r = sp.record(from_ = f, to_ = t, token_id = i, amount = a)
        Transfer.set_type_and_layout(r)
        return r

class Operator_param:
    def get_operator_tokens_type():
        return sp.TVariant(All_tokens = sp.TUnit,
                           Some_tokens = sp.TSet(token_id_type))
    def get_type():
        return sp.TRecord(
            owner = sp.TAddress,
            operator = sp.TAddress,
            tokens = Operator_param.get_operator_tokens_type())
    def set_type_and_layout(expr):
        sp.set_type(expr, Operator_param.get_type())
        if force_layouts:
            sp.set_record_layout(expr, ("owner", ("operator", "tokens")))
    def make(owner, operator, tokens = None):
        r = sp.record(owner = owner,
                      operator = operator,
                      tokens =
                          sp.variant("All_tokens", sp.unit)
                          if tokens == None else
                              sp.variant("Some_tokens", tokens))
        Operator_param.set_type_and_layout(r)
        return r
    def is_operator_response_type():
        return sp.TRecord(
            operator = Operator_param.get_type(),
            is_operator = sp.TBool
            )
    def make_is_operator_response(operator, is_operator):
        return sp.record(operator = operator, is_operator = is_operator)
    def is_operator_request_type():
        return sp.TRecord(
            operator = Operator_param.get_type(),
            callback = sp.TContract(Operator_param.is_operator_response_type())
            )

class Ledger_value:
    def get_type():
        if support_operator:
            return sp.TRecord(
                       balance = sp.TNat,
                       operators = sp.TSet(sp.TAddress))
        else:
            return sp.TRecord(balance = sp.TNat)
    def make(balance):
        if support_operator:
            return sp.record(balance = balance, operators = sp.set())
        else:
            return sp.record(balance = balance)
    def add_operator(r, addr):
        r.operators.add(addr)
    def remove_operator(r, addr):
        r.operators.remove(addr)

class Ledger_key:
    def make(user, token):
        sp.set_type(user, sp.TAddress)
        sp.set_type(token, token_id_type)
        result = sp.pair(user, token)
        if readable:
            return result
        else:
            return sp.pack(result)

class Balance_of:
    def request_type():
        return sp.TRecord(
            owner = sp.TAddress,
            token_id = token_id_type)
    def response_type():
        return sp.TList(
            sp.TRecord(
                request = Balance_of.request_type(),
                balance = sp.TNat))

class Total_supply:
    def request_type():
        return token_id_type
    def response_type():
        return sp.TList(
            sp.TRecord(
                token_id = token_id_type,
                total_supply = sp.TNat))

class Token_meta_data:
    def get_type():
        return sp.TRecord(
            token_id = token_id_type,
            symbol = sp.TString,
            name = sp.TString,
            decimals = sp.TNat,
            extras = sp.TMap(sp.TString, sp.TString)
        )
    def request_type():
        return Total_supply.request_type()

class Permissions_descriptor:
    def get_type():
        self_transfer_policy = sp.TVariant(
            Self_transfer_permitted = sp.TUnit,
            Self_transfer_denied = sp.TUnit)
        operator_transfer_policy = sp.TVariant(
            Operator_transfer_permitted = sp.TUnit,
            Operator_transfer_denied = sp.TUnit)
        owner_transfer_policy =  sp.TVariant(
            Owner_no_op = sp.TUnit,
            Optional_owner_hook = sp.TUnit,
            Required_owner_hook = sp.TUnit)
        custom_permission_policy = sp.TRecord(
            tag = sp.TString,
            config_api = sp.TOption(sp.TAddress))
        return sp.TRecord(
            self_    = self_transfer_policy,
            operator = operator_transfer_policy,
            receiver = owner_transfer_policy,
            sender   = owner_transfer_policy,
            custom   = sp.TOption(custom_permission_policy))
    def make():
        def uv(s):
            return sp.variant(s, sp.unit)
        v = sp.record(
            self_ = uv("Self_transfer_permitted"),
            operator =
                uv("Operator_transfer_permitted")
                if support_operator else
                    uv("Operator_transfer_denied"),
            receiver = uv("Owner_no_op"),
            sender = uv("Owner_no_op"),
            custom = sp.none
            )
        sp.set_type(v, Permissions_descriptor.get_type())
        return v

class Token_id_set:
    def empty():
        if assume_consecutive_token_ids:
            return sp.nat(0)
        else:
            return sp.set(t = token_id_type)
    def add(metaset, v):
        if assume_consecutive_token_ids:
            metaset.set(sp.max(metaset, v))
        else:
            metaset.add(v)
    def iter_on_operator(metaset, ledger, upd, action):
        if assume_consecutive_token_ids:
            sp.for tok in sp.range(0, metaset + 1):
                user = Ledger_key.make(upd.owner, tok)
                action(ledger[user], upd.operator)
        else:
            sp.for tok in metaset.elements():
                user = Ledger_key.make(upd.owner, tok)
                action(ledger[user], upd.operator)

class FA2(sp.Contract):
    def __init__(self, admin):
        self.init(
            paused = False,
            ledger =
                my_map(tvalue = Ledger_value.get_type()),
            tokens =
                my_map(tvalue = sp.TRecord(
                    total_supply = sp.TNat,
                    metadata = Token_meta_data.get_type()
                )),
            administrator = admin,
            all_tokens = Token_id_set.empty(),
            totalSupply = 0)

    @sp.entry_point
    def set_pause(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.data.paused = params

    @sp.entry_point
    def set_administrator(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.data.administrator = params

    @sp.entry_point
    def mint(self, params):
        sp.verify(sp.sender == self.data.administrator)
        # We don't check for pauseness because we're the admin.
        user = Ledger_key.make(params.address, params.token_id)
        Token_id_set.add(self.data.all_tokens, params.token_id)
        sp.if self.data.ledger.contains(user):
            self.data.ledger[user].balance += params.amount
        sp.else:
            self.data.ledger[user] = Ledger_value.make(params.amount)
        #self.data.ledger[user] = sp.record(balance = params.amount,)
        sp.if self.data.tokens.contains(params.token_id):
             self.data.tokens[params.token_id].total_supply += params.amount
        sp.else:
             self.data.tokens[params.token_id] = sp.record(
                 total_supply = params.amount,
                 metadata = sp.record(
                     token_id = params.token_id,
                     symbol = params.symbol,
                     name = "", # Consered useless here
                     decimals = 0,
                     extras = sp.map()
                 )
             )

    @sp.entry_point
    def transfer(self, params):
        sp.verify( ~self.data.paused )
        sp.set_type(params, sp.TList(Transfer.get_type()))
        sp.for transfer in params:
           Transfer.set_type_and_layout(transfer)
           from_user = Ledger_key.make(Transfer.get_from(transfer),
                                        Transfer.get_token_id(transfer))
           to_user = Ledger_key.make(Transfer.get_to(transfer),
                                      Transfer.get_token_id(transfer))
           if support_operator:
               sp.verify(
                   (sp.sender == self.data.administrator) |
                   (Transfer.get_from(transfer) == sp.sender) |
                   self.data.ledger[from_user].operators.contains(sp.sender))
           else:
               sp.verify(
                   (sp.sender == self.data.administrator) |
                   (Transfer.get_from(transfer) == sp.sender))
           sp.verify(
               self.data.ledger[from_user].balance
               >= Transfer.get_amount(transfer))
           self.data.ledger[from_user].balance = sp.as_nat(
               self.data.ledger[from_user].balance - Transfer.get_amount(transfer))
           sp.if self.data.ledger.contains(to_user):
               self.data.ledger[to_user].balance += Transfer.get_amount(transfer)
           sp.else:
               self.data.ledger[to_user] = Ledger_value.make(
                   Transfer.get_amount(transfer))

    @sp.entry_point
    def balance_of(self, params):
        # paused may mean that balances are meaningless:
        sp.verify( ~self.data.paused )
        res = sp.local("responses", [])
        sp.set_type(res.value, Balance_of.response_type())
        sp.for req in params.requests:
            user = Ledger_key.make(req.owner, req.token_id)
            balance = self.data.ledger[user].balance
            res.value.push(
                sp.record(
                    request = sp.record(
                        owner = sp.set_type(req.owner, sp.TAddress),
                        token_id = sp.set_type(req.token_id, sp.TNat)),
                    balance = balance))
        destination = sp.set_type(params.callback,
                                  sp.TContract(Balance_of.response_type()))
        sp.transfer(res.value.rev(), sp.mutez(0), destination)

    @sp.entry_point
    def total_supply(self, params):
        sp.verify( ~self.data.paused )
        res = sp.local("responses", [])
        sp.set_type(res.value, Total_supply.response_type())
        sp.for req in params.token_ids:
            res.value.push(
                sp.record(
                    token_id = req,
                    total_supply = self.data.tokens[req].total_supply))
        destination = sp.set_type(params.callback,
                                  sp.TContract(Total_supply.response_type()))
        sp.transfer(res.value.rev(), sp.mutez(0), destination)

    @sp.entry_point
    def token_metadata(self, params):
        sp.verify( ~self.data.paused )
        res = sp.local("responses", [])
        sp.set_type(res.value, sp.TList(Token_meta_data.get_type()))
        sp.for req in params.token_ids:
            res.value.push(self.data.tokens[req].metadata)
        destination = sp.set_type(params.callback,
                                  sp.TContract(
                                      sp.TList(Token_meta_data.get_type())))
        sp.transfer(res.value.rev(), sp.mutez(0), destination)


    def lambda_on_operator(self, upd, tokens, action):
        sp.for tok in tokens.elements():
            user = Ledger_key.make(upd.owner, tok)
            action(self.data.ledger[user], upd.operator)

    def make_operator_update(self, upd, action):
        Operator_param.set_type_and_layout(upd)
        sp.verify((upd.owner == sp.sender) |
                  (sp.sender == self.data.administrator))
        sp.if upd.tokens.is_variant("All_tokens"):
            Token_id_set.iter_on_operator(self.data.all_tokens,
                                          self.data.ledger, upd, action)
        sp.else:
            self.lambda_on_operator(upd,
                                    upd.tokens.open_variant("Some_tokens"),
                                    action)

    @sp.entry_point
    def update_operators(self, params):
        sp.set_type(params, sp.TList(
            sp.TVariant(
                Add_operator = Operator_param.get_type(),
                Remove_operator = Operator_param.get_type())))
        if support_operator:
            sp.for update in params:
                sp.if update.is_variant("Add_operator"):
                    upd = update.open_variant("Add_operator")
                    self.make_operator_update(
                        upd,
                        Ledger_value.add_operator)
                sp.else:
                    upd = update.open_variant("Remove_operator")
                    self.make_operator_update(
                        upd,
                        Ledger_value.remove_operator)
        else:
            sp.failwith("N/A")

    def update_local_variable_because_python_lambdas_suck(res, ledger_entry, operator):
        sp.if ledger_entry.operators.contains(operator):
            pass
        sp.else:
            res.value = res.value & False

    @sp.entry_point
    def permissions_descriptor(self, params):
        sp.set_type(params, sp.TContract(Permissions_descriptor.get_type()))
        v = Permissions_descriptor.make()
        sp.transfer(v, sp.mutez(0), params)

    @sp.entry_point
    def is_operator(self, params):
        sp.set_type(params, Operator_param.is_operator_request_type())
        res = sp.local("response", True)
        action = lambda a,b : FA2.update_local_variable_because_python_lambdas_suck(res, a, b)
        if support_operator:
            sp.if params.operator.tokens.is_variant("All_tokens"):
                Token_id_set.iter_on_operator(self.data.all_tokens,
                                              self.data.ledger,
                                              params.operator, action)
            sp.else:
                self.lambda_on_operator(params.operator,
                                        params.operator.tokens.open_variant("Some_tokens"),
                                        action)
            returned = sp.record(
                operator = params.operator,
                is_operator = res.value)
            sp.transfer(returned, sp.mutez(0), params.callback)
            #user = Ledger_key.make(params.operator.owner,
            #                       params.operator.tokens)
        else:
            sp.failwith("N/A")

class View_consumer(sp.Contract):
    def __init__(self):
        self.init(last_sum = 0,
                  last_acc = "",
                  last_operator = True,
                  operator_support =  False if support_operator else True)

    @sp.entry_point
    def receive_balances(self, params):
        sp.set_type(params, Balance_of.response_type())
        self.data.last_sum = 0
        sp.for resp in params:
            self.data.last_sum += resp.balance

    @sp.entry_point
    def receive_total_supplies(self, params):
        sp.set_type(params, Total_supply.response_type())
        self.data.last_sum = 0
        sp.for resp in params:
            self.data.last_sum += resp.total_supply

    @sp.entry_point
    def receive_metadata(self, params):
        sp.set_type(params, sp.TList(Token_meta_data.get_type()))
        self.data.last_acc = ""
        sp.for resp in params:
            self.data.last_acc += resp.symbol

    @sp.entry_point
    def receive_is_operator(self, params):
        sp.set_type(params, Operator_param.is_operator_response_type())
        self.data.last_operator = params.is_operator

    @sp.entry_point
    def receive_permissions_descriptor(self, params):
        sp.set_type(params, Permissions_descriptor.get_type())
        sp.if params.operator.is_variant("Operator_transfer_permitted"):
            self.data.operator_support = True
        sp.else:
            self.data.operator_support = False

def arguments_for_balance_of(receiver, reqs):
    return (sp.record(
        callback = sp.contract(Balance_of.response_type(),
                               sp.contract_address(receiver),
                               entry_point = "receive_balances").open_some(),
        requests = reqs))


if "templates" not in __name__:
    @sp.add_test(name = "FA2")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Simple FA2 Contract")
        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob   = sp.test_account("Robert")
        # Let's display the accounts:
        scenario.h2("Accounts")
        scenario.show([admin, alice, bob])
        c1 = FA2(admin.address)
        scenario += c1
        scenario.h2("Initial Minting")
        scenario.p("The administrator mints 100 token-0's to Alice.")
        scenario += c1.mint(address = alice.address,
                            amount = 100,
                            symbol = 'TK0',
                            token_id = 0).run(sender = admin)
        scenario.h2("Transfers Alice -> Bob")
        scenario += c1.transfer(
            [
                Transfer.make(alice.address,
                              bob.address,
                              a = 10,
                              i = 0)
            ]).run(sender = alice)
        scenario.verify(
            c1.data.ledger[Ledger_key.make(alice.address, 0)].balance == 90)
        scenario.verify(
            c1.data.ledger[Ledger_key.make(bob.address, 0)].balance == 10)
        scenario += c1.transfer(
            [
                Transfer.make(alice.address,
                              bob.address,
                              a = 10,
                              i = 0),
                Transfer.make(alice.address,
                              bob.address,
                              a = 11,
                              i = 0)
            ]).run(sender = alice)
        scenario.verify(
            c1.data.ledger[Ledger_key.make(alice.address, 0)].balance
            == 90 - 10 - 11)
        scenario.verify(
            c1.data.ledger[Ledger_key.make(bob.address, 0)].balance
            == 10 + 10 + 11)
        scenario.h2("More Token Types")
        scenario += c1.mint(address = bob.address,
                            amount = 100,
                            symbol = 'TK1',
                            token_id = 1).run(sender = admin)
        scenario += c1.mint(address = bob.address,
                            amount = 200,
                            symbol = 'TK2',
                            token_id = 2).run(sender = admin)
        scenario.h3("Multi-token Transfer Bob -> Alice")
        scenario += c1.transfer(
            [
                Transfer.make(bob.address,
                              alice.address,
                              a = 10,
                              i = 0),
                Transfer.make(bob.address,
                              alice.address,
                              a = 10,
                              i = 1),
                Transfer.make(bob.address,
                              alice.address,
                              a = 10,
                              i = 2)
            ]).run(sender = bob)
        scenario.h2("Other Basic Permission Tests")
        scenario.h3("Bob cannot transfer Alice's tokens.")
        scenario += c1.transfer(
            [
                Transfer.make(alice.address,
                              bob.address,
                              a = 10,
                              i = 0),
                Transfer.make(alice.address,
                              bob.address,
                              a = 11,
                              i = 0)
            ]).run(sender = bob, valid = False)
        scenario.h3("Admin can transfer anything.")
        scenario += c1.transfer(
            [
                Transfer.make(alice.address,
                              bob.address,
                              a = 10,
                              i = 0),
                Transfer.make(alice.address,
                              bob.address,
                              a = 10,
                              i = 1),
                Transfer.make(bob.address,
                              alice.address,
                              a = 11,
                              i = 0)
            ]).run(sender = admin)
        scenario.h3("Even Admin cannot transfer too much.")
        scenario += c1.transfer(
            [
                Transfer.make(alice.address,
                              bob.address,
                              a = 1000,
                              i = 0)
            ]).run(sender = admin, valid = False)
        scenario.h3("Consumer Contract for Callback Calls.")
        consumer = View_consumer()
        scenario += consumer
        scenario.p("Consumer virtual address: "
                   + sp.contract_address(consumer).export())
        scenario.h2("Balance-of.")
        scenario += c1.balance_of(arguments_for_balance_of(consumer, [
            sp.record(owner = alice.address, token_id = 0),
            sp.record(owner = alice.address, token_id = 1),
            sp.record(owner = alice.address, token_id = 2)
        ]))
        scenario.verify(consumer.data.last_sum == 90)
        scenario.h2("Total Supply.")
        scenario += c1.total_supply(
            sp.record(
                callback = sp.contract(
                    Total_supply.response_type(),
                    sp.contract_address(consumer),
                    entry_point = "receive_total_supplies").open_some(),
                token_ids = [0, 1]))
        scenario.verify(consumer.data.last_sum == 200)
        scenario.h2("Token Metadata.")
        scenario += c1.token_metadata(
            sp.record(
                callback = sp.contract(
                    sp.TList(Token_meta_data.get_type()),
                    sp.contract_address(consumer),
                    entry_point = "receive_metadata").open_some(),
                token_ids = [0, 1]))
        scenario.verify(consumer.data.last_acc == "TK0TK1")
        scenario.h2("Operators")
        if not support_operator:
            scenario.h3("This version was compiled with no operator support")
            scenario.p("Calls should fail even for the administrator:")
            scenario += c1.update_operators([]).run(sender = admin, valid = False)
            scenario += c1.permissions_descriptor(
                sp.contract(
                    Permissions_descriptor.get_type(),
                    sp.contract_address(consumer),
                    entry_point = "receive_permissions_descriptor").open_some())
            scenario.verify(consumer.data.operator_support == False)
        else:
            scenario.p("This version was compiled with operator support")
            scenario += c1.update_operators([]).run(sender = admin)
            scenario.h3("Operator Accounts")
            op0 = sp.test_account("Operator0")
            op1 = sp.test_account("Operator1")
            op2 = sp.test_account("Operator2")
            scenario.show([op0, op1, op2])
            scenario.p("Admin can change Alice's operator.")
            scenario += c1.update_operators([
                sp.variant("Add_operator", Operator_param.make(
                    owner = alice.address,
                    operator = op1.address))
            ]).run(sender = admin)
            scenario.p("Operator1 can transfer Alice's tokens")
            scenario += c1.transfer(
                [
                    Transfer.make(alice.address,
                                  bob.address,
                                  a = 2,
                                  i = 0),
                    Transfer.make(alice.address,
                                  op1.address,
                                  a = 2,
                                  i = 2)
                ]).run(sender = op1)
            scenario.p("Operator1 cannot transfer Bob's tokens")
            scenario += c1.transfer(
                [
                    Transfer.make(bob.address,
                                  op1.address,
                                  a = 2,
                                  i = 1)
                ]).run(sender = op1, valid = False)
            scenario.p("Operator2 cannot transfer Alice's tokens")
            scenario += c1.transfer(
                [
                    Transfer.make(alice.address,
                                  bob.address,
                                  a = 2,
                                  i = 1)
                ]).run(sender = op2, valid = False)
            scenario.p("Alice can remove their operator")
            scenario += c1.update_operators([
                sp.variant("Remove_operator", Operator_param.make(
                    owner = alice.address,
                    operator = op1.address))
            ]).run(sender = alice)
            scenario.p("Operator1 cannot transfer Alice's tokens any more")
            scenario += c1.transfer(
                [
                    Transfer.make(alice.address,
                                  op1.address,
                                  a = 2,
                                  i = 1)
                ]).run(sender = op1, valid = False)
            scenario.p("Bob can add Operator0 only for token 0 and 1.")
            scenario += c1.update_operators([
                sp.variant("Add_operator", Operator_param.make(
                    owner = bob.address,
                    operator = op0.address,
                    tokens = sp.set([0,1])
                ))
            ]).run(sender = bob)
            scenario.p("Operator0 can transfer Bob's tokens '0' and '1'")
            scenario += c1.transfer(
                [
                    Transfer.make(bob.address,
                                  alice.address,
                                  a = 1,
                                  i = 0),
                    Transfer.make(bob.address,
                                  alice.address,
                                  a = 1,
                                  i = 1)
                ]).run(sender = op0)
            scenario.p("Operator0 cannot transfer Bob's tokens '2'")
            scenario += c1.transfer(
                [
                    Transfer.make(bob.address,
                                  alice.address,
                                  a = 1,
                                  i = 2)
                ]).run(sender = op0, valid = False)
            scenario.p("Bob cannot add Operator0 for Alice's tokens.")
            scenario += c1.update_operators([
                sp.variant("Add_operator", Operator_param.make(
                    owner = alice.address,
                    operator = op0.address,
                    tokens = sp.set([0,1])
                ))
            ]).run(sender = bob, valid = False)
            scenario.h3("Testing is_operator")
            scenario.p("Operator0 is still active for Bob's 0 and 1, \
            Alice has no operator")
            def test_is_operator(scenario, owner, operator, tokens, valid, comment):
                scenario.p("test_is_operator: " + comment )
                is_operator = Operator_param.make(
                    owner = owner.address,
                    operator = operator.address,
                    tokens = tokens)
                scenario += c1.is_operator(
                    sp.record(
                        callback = sp.contract(
                            Operator_param.is_operator_response_type(),
                            sp.contract_address(consumer),
                            entry_point = "receive_is_operator").open_some(),
                        operator = is_operator
                    ))
                scenario.verify(consumer.data.last_operator == valid)
            test_is_operator(scenario, bob, op0, sp.set([0, 1]), True,
                             "bob, op0, [0,1]")
            test_is_operator(scenario, bob, op0, sp.set([0]), True,
                             "bob, op0, [0]")
            test_is_operator(scenario, bob, op0, sp.set([0, 2]), False,
                             "bob, op0, [0,2]")
            test_is_operator(scenario, bob, op0, None, False,
                             "bob, op0, all")
            test_is_operator(scenario, alice, op0, None, False,
                             "alice, op0, all")
            scenario.h3("Testing permissions_descriptor")
            scenario.verify(consumer.data.operator_support == False)
            scenario += c1.permissions_descriptor(
                sp.contract(
                    Permissions_descriptor.get_type(),
                    sp.contract_address(consumer),
                    entry_point = "receive_permissions_descriptor").open_some())
            scenario.verify(consumer.data.operator_support == True)