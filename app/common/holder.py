from collections import deque

class Holder:
    def __init__(
            self,
            id,
            holders,
    ):
        self.id = id
        self.holders = holders
        self.sum = 0
    
    def receive_income(self, new_income, terminator, tol_income=0.01, max_iter=100):
        # append and popleft
        queue = deque([(self, new_income)])
        while len(queue) > 0 and max_iter > 0:
            #print(max_iter)

            current, current_income = queue.popleft()
            current.sum += current_income

            if terminator.check():
                break

            for holder, share in current.holders:
                max_iter -= 1
                to_propagate = current_income * share 
                if to_propagate > tol_income:
                    current.sum -= to_propagate
                    queue.append((holder, to_propagate))

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
            total += self.holder[holder_id].sum
        return total
    
    def reset_income(self):
        for holder_id in self.holder:
            self.holder[holder_id].sum = 0

def join_holders_lists(holders_list1, holders_list2):
    joined = HoldersList([], [])
    joined.holder = holders_list1.holder | holders_list2.holder
    return joined

def create_nodes(df, label, blacklist=None, whitelist=None):
    def allowed(x):
        if x in blacklist:
            return False
        if whitelist is None:
            return True
        return x in whitelist
    if blacklist is None:
        blacklist = set()
    
    # ASSUMING NO DUPLICATES
    holders = []
    ids = []

    label_index = df.columns.get_loc(label) + 1
    for row in df.itertuples():
        new_id = row[label_index]
        if allowed(new_id):
            new_holder = Holder(
                id=new_id,
                holders=[] # will fill in on next step!
            )
            holders.append(new_holder)
            ids.append(new_id)

    return holders, ids


def add_edges(holders, founders_df, founder_label, property_label, share_label='share_percent'):
    founder_index = founders_df.columns.get_loc(founder_label) + 1
    property_index = founders_df.columns.get_loc(property_label) + 1
    share_index = founders_df.columns.get_loc(share_label) + 1
    for row in founders_df.itertuples():
        founder_id = row[founder_index]
        property_id = row[property_index]
        share = row[share_index]
        holders.add_relation(founder_id, property_id, share)

 
def build_tree(
        company_df,
        natural_df,
        founder_legal_df,
        founder_legal_df_nonterminal,
        founder_legal_df_terminal,
        founder_natural_df,
        ogrns
):
    # ASSUMPTIONS
    founder_legal_df = founder_legal_df.dropna()
    founder_legal_df_nonterminal = founder_legal_df_nonterminal.dropna()
    founder_legal_df_terminal = founder_legal_df_terminal.dropna()
    founder_natural_df = founder_natural_df.dropna()

    # create nodes
    print('Haha')
    nonterminals1 = HoldersList(*create_nodes(founder_legal_df_nonterminal, 'ogrn', whitelist=ogrns))
    nonterminals2 =  HoldersList(*create_nodes(company_df, 'ogrn', blacklist=set(nonterminals1.holder), whitelist=ogrns))
    nonterminals = join_holders_lists(nonterminals1, nonterminals2)
    print('Hehe')
    humans = HoldersList(*create_nodes(natural_df, 'full_credentials'))
    terminals2 = HoldersList(*create_nodes(founder_legal_df, 'ogrn', whitelist=ogrns))
    terminals = join_holders_lists(humans, terminals2)
    print('Hihi')
   
    # create edges
    all = join_holders_lists(nonterminals, terminals)
    print('A')

    #print(all.holder['1001601570410'])
    print('B')
    add_edges(all, founder_legal_df, founder_label='ogrn', property_label='company_ogrn')
    add_edges(all, founder_natural_df, founder_label='full_credentials', property_label='company_ogrn')

    return nonterminals, terminals, humans


class Terminator:
    def __init__(self, terminal, threshold, steps_until_checkpoint=10000, total_steps=1e7):
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
            print('Another million', self.total_steps)
            self.terminated = self.check_terminating_condition()
        return self.terminated
    
    def check_terminating_condition(self):
        t = self.terminal.total_income()
        #print(t)
        return t > self.threshold


def total_reset(*holders_lists):
    for holders_list in holders_lists:
        holders_list.reset_income()


def compress(holder_list):
    return dict(map(lambda p: (p[1], p[0]), enumerate(holder_list.holder.keys())))

def iteratively_estimate_indirect_shares(nonterminal, terminal, humans, start_income=1, threshold_percent=0.99):
    terminator = Terminator(terminal, threshold=threshold_percent * start_income)  
    indirect_shares_OF_IN = { holder_id : {} for holder_id in terminal.holder }

    cnt = 0
    for nonterminal_id in nonterminal.holder:
        cnt += 1
        #print('AHAHAAHA', cnt)
        total_reset(nonterminal, terminal)
        nonterminal[nonterminal_id].receive_income(start_income, terminator)
        for human_id in humans.holder:
            if humans[human_id].sum > 0.25:
                indirect_shares_OF_IN[human_id][nonterminal_id] = humans[human_id].sum
    return indirect_shares_OF_IN



