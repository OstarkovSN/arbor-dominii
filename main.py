import os

import pandas as pd
from app.common.holder import HoldersList, Holder, iteratively_estimate_indirect_shares, build_tree
from app.common.preprocess import preprocess_folder, get_dfs, mk_natural
from app.common.postprocess import postprocess_default
import pandas as pd

from app.common.config import Configuration
def kopeika(
        company_df,
        natural_df,
        founder_legal_df,
        founder_legal_df_nonterminal,
        founder_legal_df_terminal,
        founder_natural_df,
):
    nonterminal, terminal, humans = build_tree(
        company_df=company_df,
        natural_df=natural_df,
        founder_legal_df=founder_legal_df,
        founder_legal_df_nonterminal=founder_legal_df_nonterminal,
        founder_legal_df_terminal=founder_legal_df_terminal,
        founder_natural_df=founder_natural_df,
    )

    print('Start2')
    indirect_shares = iteratively_estimate_indirect_shares(
        nonterminal=nonterminal,
        terminal=terminal,
        humans=humans,
        use_tqdm=CONFIG['use-tqdm']
    )
    print('Done')
    
    return indirect_shares

if __name__ == "__main__":
    with open('docker.flag', 'r') as f:
        is_docker = f.read().strip() == 'True'
    if is_docker:
        CONFIG = Configuration('environment/config_docker.json') #if we are in docker
    else:
        try:
            CONFIG = Configuration('config.json') #if we are in local
        except FileNotFoundError:
            CONFIG = Configuration('app/configs/local.json') #if we are in local, try to use local config
        
    os.makedirs(CONFIG['raw/'], exist_ok=True)
    os.makedirs(CONFIG['processed/'], exist_ok=True)
    os.makedirs(CONFIG['final/'], exist_ok=True)
    
    preprocess_folder(CONFIG['raw/'],
                    CONFIG['processed/'],
                    CONFIG['preprocessing'])

    company_df, founder_legal_df, founder_legal_df_nonterminal, founder_legal_df_terminal, founder_natural_df = get_dfs(CONFIG['processed/company'], CONFIG['processed/founder_natural'], CONFIG['processed/founder_legal'])

    natural_df = CONFIG['impute'](founder_natural_df)
    
    natural_df = mk_natural(founder_natural_df)
    
    # Проверка наличия несоответствий
    missing_company_ids = set(founder_legal_df['company_id']) - set(company_df['id'])
    if missing_company_ids:
        print(f"Отсутствующие company_id в company.tsv: {missing_company_ids}")


    indirect_shares = kopeika(company_df=company_df,
                              founder_legal_df=founder_legal_df,
                              founder_natural_df=founder_natural_df,
                              natural_df=natural_df,
                              founder_legal_df_nonterminal=founder_legal_df_nonterminal,
                              founder_legal_df_terminal=founder_legal_df_terminal)
    
    postprocess_default(indirect_shares, df_companies=company_df, final_filepath=CONFIG['final/results']) #FIXME
