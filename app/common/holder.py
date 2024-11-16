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
        self.income = 0
    
    def receive_income(self, new_income, terminator):
        self.income += new_income 
        if not terminator.check():
            for holder, share in self.holders:
                to_propagate = new_income * share 
                self.income -= to_propagate
                holder.receive_income(to_propagate, terminator)

class HoldersList:
    def __init__(
            self,
            holders,
            holder_ids,
    ):
        self.holder = { holder_ids[i] : holders[i] for i in range(len(holders)) }
        self.ids = holder_ids
    
    def __getitem__(self, holder_id):
        return self.holder[holder_id]
    
    def total_income(self):
        total = 0
        for holder_id in self.holder:
            total += self.holder[holder_id]
        return total
    
    def reset_income(self):
        for holder_id in self.holder:
            self.holder[holder_id] = 0

class Terminator:
    def __init__(self, terminal, threshold, steps_until_checkpoint=1000, ):
        self.terminal = terminal
        self.threshold = threshold
        self.steps_until_checkpoint = steps_until_checkpoint 

        self.steps_until_checkpoint_base_value = steps_until_checkpoint 
        self.terminated = False
    
    def check(self):
        self.steps_until_checkpoint -= 1
        if self.steps_until_checkpoint == 0:
            self.terminated = self.check_terminating_condition()
        return self.terminated
    
    def check_terminating_condition(self):
        return self.terminal.total_income() > self.threshold


def total_reset(*holders_lists):
    for holders_list in holders_lists:
        holders_list.reset_income()


def iteratively_estimate_indirect_shares(nonterminal, terminal, start_income=1, threshold=0.99):
    terminator = Terminator(terminal, threshold=threshold)  
    indirect_shares_OF_IN = { holder_id : {} for holder_id in terminal.ids }

    for nonterminal_id in nonterminal.ids:
        total_reset(nonterminal, terminal)
        nonterminal[nonterminal_id].receive_income(start_income)
        for terminal_id in terminal.ids:
            indirect_shares_OF_IN[terminal_id][nonterminal_id] = terminal[terminal_id].sum
    return indirect_shares_OF_IN