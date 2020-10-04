
import smartpy as sp

class Crowdfunding(sp.Contract):
    def __init__(self):
        self.init(
            parties = sp.map(tkey=sp.TAddress, tvalue=sp.TMutez),
            minAmount = sp.tez(0),
            total = sp.tez(0),
            maxTime = sp.timestamp(0) #  + 345600
            )

    @sp.entry_point
    def sendFund(self, params):
        sp.verify(self.data.maxTime > sp.now)
        sp.verify(self.data.parties.contains(sp.sender) != True)
        sp.send(sp.sender, sp.amount)
        self.data.parties[sp.sender] = sp.amount
        self.data.total += sp.amount
        
    @sp.entry_point
    def payOff(self, params):
        sp.verify(sp.sender == sp.source)
        sp.verify(self.data.total > self.data.minAmount)
        sp.verify(sp.now > self.data.maxTime)
        sp.send(sp.source, self.data.total)
        self.data.total = sp.balance
    
    @sp.entry_point
    def refund(self, params):
        sp.verify(sp.now > self.data.maxTime)
        sp.verify(self.data.minAmount > sp.balance)

        parties_list = sp.local("parties_list", self.data.parties.keys())
        sp.for e in parties_list.value:
            value = self.data.parties[e]
            sp.send(e, value)
            self.data.total = sp.balance
            

@sp.add_test(name = "Test Crowd")
def test():
   
    scenario = sp.test_scenario()
    contract = Crowdfunding()
    scenario += contract

