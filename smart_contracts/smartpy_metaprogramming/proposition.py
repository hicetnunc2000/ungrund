
import smartpy as sp

class Proposal(sp.Contract):
    def __init__(self):
        self.init(
            time_out = sp.timestamp(0),
            votes = sp.map(tkey = sp.TAddress, tvalue = sp.TString),
            parties = sp.list(t=sp.TAddress),
            immutability = False,
            proposal = '',
            ocasion = '',
            ammendment = ''
            )
        
    @sp.entry_point
    def origin_entry(self, params):
        
        # Verify if Proposal, Ocasion and Location weren't set already
        # Conditions in case of need for edits?
        
        sp.verify(self.data.immutability == False)
        self.data.proposal = params.proposal
        self.data.ocasion = params.ocasion

        self.data.time_out = params.time_out

        # Sets immutability
        
        self.data.immutability = True

    @sp.entry_point
    def parties_join(self, params):
        
        # Verify if proposal is still open
        sp.verify (sp.now < self.data.time_out)
        
        # Verifies if party haven't already joined
        
        sp.for e in self.data.parties:
            sp.verify( e != sp.sender)
            
        self.data.parties.push(sp.sender)

    @sp.entry_point
    def vote(self, params):
        
        # Verify if proposal is still open
        sp.verify (sp.now < self.data.time_out)
        
        # Verify if a vote is of the right type
        
        sp.verify((params.vote == 'Y') | (params.vote == 'N') | (params.vote == 'Abs'))
        
        # Verify if party haven't already voted
        
        sp.for e in self.data.votes.keys():
            sp.verify( e != sp.sender )
        
        self.data.votes[sp.sender] = params.vote
        
       
    @sp.entry_point
    def ammend(self, params):
        pass
        
@sp.add_test(name = "Test_Proposal")
def test():
    scenario = sp.test_scenario()
    contract = Proposal()
    scenario += contract
    
    scenario.h3("Definie Proposal Parameters")
    
    scenario += contract.origin_entry(time_out=sp.timestamp(1596067200), proposal="PELA CRIACAO DO PARQUE DO BIXIGA: APOIO A APROVACAO E IMEDIATA SANCAO DO PROJETO DE LEI 805/2017", ocasion="Teatro Oficina Uzyna Uzona").run(sender=sp.address("tz1")) # complemento?
    
    scenario.h3("Join parties")
    
    scenario += contract.parties_join().run(sender=sp.address('tz2'))
    scenario += contract.parties_join().run(sender=sp.address('tz3'))

    scenario.h3("Vote")

    scenario += contract.vote(vote="Y").run(sender=sp.address('tz2'))
    scenario += contract.vote(vote="N").run(sender=sp.address('tz3'))

        