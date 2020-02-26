
import smartpy as sp

class Transaction(sp.Contract):
    def __init__(self):
        self.init(
            origin = sp.address('tz1'),
            destiny = sp.address('tz2'),
            amount = sp.tez(0),
            immutability = sp.bool(False)
            )


    @sp.entry_point
    def transaction(self, params):
        
        sp.verify(self.data.immutability == False)
        
        # Transfer transaction amount to contract's balance (forwarding)
        
        sp.balance = sp.amount
        
        # Register transaction
        
        self.data.origin = sp.sender
        self.data.destiny = params.destiny
        self.data.amount = sp.amount
        
        # Execute transaction
        
        sp.send(params.destiny, sp.amount)
        
        # Set immutability
        
        self.data.immutability = True
        
@sp.add_test(name = "Test_Transaction")
def test():
    scenario = sp.test_scenario()
    contract = Transaction()
    scenario += contract
    
    scenario.h3("Transact")
    scenario += contract.transaction(destiny=sp.address("tz1")).run(sender=sp.address("tz2"), amount=sp.tez(3000))
