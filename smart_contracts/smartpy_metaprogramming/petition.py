
import smartpy as sp

class Petition(sp.Contract):
    def __init__(self):
        self.init(
            time_out = sp.timestamp(0),
            signatures = sp.map(tkey = sp.TString, tvalue = sp.TString),
            immutability = False,
            proposal = '',
            ocasion = '',
            description = ''
            )
        
    @sp.entry_point
    def origin_entry(self, params):
        
        # Verify if Proposal, Ocasion and Location weren't set already
        # Conditions in case of need for edits?
        
        sp.verify(self.data.immutability == False)
        self.data.proposal = params.proposal
        self.data.ocasion = params.ocasion
        self.data.description = params.description

        self.data.time_out = params.time_out

        # Sets immutability
        
        self.data.immutability = True

    @sp.entry_point
    def sign(self, params):
        
        # Verify if proposal is still open
        sp.verify (sp.now < self.data.time_out)
        
        # Verify if party haven't already signed
        
        sp.for e in self.data.signatures.keys():
            sp.verify( e != params.cpf )
        
        self.data.signatures[params.cpf] = params.name
        
@sp.add_test(name = "Test_Petition")
def test():
    scenario = sp.test_scenario()
    contract = Petition()
    scenario += contract
    
    scenario.h3("Definie Proposal Parameters")
    
    scenario += contract.origin_entry(description='', time_out=sp.timestamp(1596067200), proposal="PELA CRIACAO DO PARQUE DO BIXIGA: APOIO A APROVACAO E IMEDIATA SANCAO DO PROJETO DE LEI 805/2017", ocasion="Teatro Oficina Uzyna Uzona").run(sender=sp.address("tz1")) # complemento?
    
    scenario.h3("Vote")

    scenario += contract.sign(name="Name", cpf="ID").run(sender=sp.address('tz3'))

