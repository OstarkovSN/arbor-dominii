class Holder:
    def __init__(
            self,
            id,
            shares,
            holders,
    ):
        self.id = id
        self.shares = shares
        self.holders = holders
        self.sum = 0
    
    def propagate(self, sum=1, tol_percent=0.01):
        tol_sum = sum * tol_percent
        self.receive_income(sum, tol_sum)
        
    def receive_income(self, sum, tol_sum):
       self.sum += sum 
       for holder, share in self.holders:
           to_propagate = holder * share 
           if to_propagate > tol_sum:
               self.sum -= to_propagate
               holder.receive_income(sum=to_propagate, tol_sum=tol_sum)

class HoldersList:
    def __init__(
            self,
            holders,
            holder_ids,
    ):
        self.get_holder = { holder_ids[i] : holders[i] for i in range(len(holders)) }
        self.ids = holder_ids

def total_robbery(*holders_lists):
    for holders_list in holders_lists:
        for holder_id in holders_list.ids:
            holders_list.get_holder[holder_id].sum = 0


def iteratively_estimate_indirect_shares(nonterminal_holders, terminal_holders):
    total_robbery(nonterminal_holders, terminal_holders)
    indirect_shares_OF_IN = { holder_id : {} for holder_id in nonterminal_holders.ids }

    for propagator_id in nonterminal_holders.ids:
        nonterminal_holders[propagator_id].propagate()
        for receiver_id in nonterminal_holders.ids:
            indirect_shares_OF_IN[receiver_id][propagator_id] = nonterminal_holders[receiver_id].sum
        total_robbery(all_holders_with_ids)
