class Holder:
    def __init__(
            self,
            id,
            holders,
    ):
        self.id = id
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


    def add_relation(self, founder_id, property_id, share):
        founder = self.holder[founder_id]
        property = self.holder[property_id]
        property.holders.append((founder, share))


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

def join_holders_lists(holders_list1, holders_list2):
    joined = HoldersList([], [])
    joined.holder = holders_list1.holder | holders_list2.holder

def create_nodes(df, label):
    # ASSUMING NO DUPLICATES
    holders = []
    ids = []

    for i, row in df.iterrows():
        new_id = row[label]
        new_holder = Holder(
            id=new_id,
            holders=[] # will fill in on next step!
        )
        holders.append(new_holder)
        ids.append(new_id)

    return holders, ids


def add_edges(holders, founders_df, founder_label, property_label, share_label='share_percent'):
    for i, row in founders_df.iterrows():
        founder_id = row[founder_label]
        property_id = row[property_label]
        share = row[share_label]
        holders.add_relation(founder_id, property_id, share)

 
def build_tree(company_df, natural_df, founder_legal_df, founder_natural_df):
    # create nodes
    # ASSUMING ALL TERMINALS ARE NATURAL
    nonterminals = HoldersList(*create_nodes(company_df, 'id'))
    terminals = HoldersList(*create_nodes(natural_df, 'full_credentials'))
   
    # create edges
    all = join_holders_lists(nonterminals, terminals)
    add_edges(all, founder_legal_df, founder_label='owner_id', property_label='company_id')
    add_edges(all, founder_natural_df, founder_label='full_credentials', property_label='company_id')

    return nonterminals, terminals


class Terminator:
    def __init__(self, terminal, threshold, steps_until_checkpoint=1000, total_steps=1e7):
        self.terminal = terminal
        self.threshold = threshold
        self.steps_until_checkpoint = steps_until_checkpoint 
        self.total_steps = total_steps

        self.steps_until_checkpoint_base_value = steps_until_checkpoint 
        self.terminated = False
    
    def check(self):
        if self.total_steps == 0:
            return True
        self.total_steps -= 1
        
        self.steps_until_checkpoint -= 1
        if self.steps_until_checkpoint == 0:
            self.terminated = self.check_terminating_condition()
        return self.terminated
    
    def check_terminating_condition(self):
        return self.terminal.total_income() > self.threshold


def total_reset(*holders_lists):
    for holders_list in holders_lists:
        holders_list.reset_income()


def iteratively_estimate_indirect_shares(nonterminal, terminal, start_income=100, threshold_percent=0.99):
    terminator = Terminator(terminal, threshold=threshold_percent * start_income)  
    indirect_shares_OF_IN = { holder_id : {} for holder_id in terminal.ids }

    for nonterminal_id in nonterminal.ids:
        total_reset(nonterminal, terminal)
        nonterminal[nonterminal_id].receive_income(start_income)
        for terminal_id in terminal.ids:
            indirect_shares_OF_IN[terminal_id][nonterminal_id] = terminal[terminal_id].sum
    return indirect_shares_OF_IN



