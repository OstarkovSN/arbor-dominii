import os

import pandas as pd
from app.common.holder import HoldersList, Holder, iteratively_estimate_indirect_shares

from app.common.preprocess import preprocess_folder, get_dfs
from app.common.postprocess import postprocess_default
import pandas as pd

from app.common.config import Configuration

def kopeika(company_df,founder_legal_df,founder_natural_df):

    # Создаем структуру владения
    structure = OwnershipStructure(company_df, founder_legal_df, founder_natural_df)

    # Преобразуем данные в формат для Holder
    holders, holder_ids = [], []
    for company_id, company in structure.companies.items():
        holders.append(
            Holder(
                id=company_id,
                shares=[
                    (owner['id'], owner['share_percent'] / 100)
                    for owner in company['owners']
                    if owner['type'] == 'legal'
                ],
                holders=[]
            )
        )
        holder_ids.append(company_id)

    # Инициализируем HoldersList
    holders_list = HoldersList(holders, holder_ids)

    # Вычисляем косвенные доли
    indirect_shares = iteratively_estimate_indirect_shares(holders_list, holders_list)
    
    return indirect_shares

if __name__ == "__main__":
    try:
        CONFIG = Configuration('environment/config.json') #if we are in docker
    except FileNotFoundError:
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

    company_df, founder_legal_df, founder_natural_df = get_dfs(CONFIG['processed/company'], CONFIG['processed/founder_legal'], CONFIG['processed/founder_natural'])

    # Проверка наличия несоответствий
    missing_company_ids = set(founder_legal_df['company_id']) - set(company_df['id'])
    if missing_company_ids:
        print(f"Отсутствующие company_id в company.tsv: {missing_company_ids}")


    indirect_shares = kopeika(company_df=company_df, founder_legal_df=founder_legal_df, founder_natural_df=founder_natural_df)
    
    postprocess_default(indirect_shares, comps, final_filepath=CONFIG['final/results']) #FIXME
