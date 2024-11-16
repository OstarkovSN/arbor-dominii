import os

import pandas as pd
from app.common.structure import OwnershipStructure
from app.common.holder import HoldersList, Holder, iteratively_estimate_indirect_shares

from app.common.preprocess import preprocess_folder
from app.common.postprocess import postprocess_default
import pandas as pd

from app.common.config import Configuration

try:
    CONFIG = Configuration('environment/config.json')
except FileNotFoundError:
    CONFIG = Configuration('app/configs/local.json')

def preprocess():
    """
    Processes files in the "data" folder using the CompanyNamesMerger preprocessor
    and writes the results to the "processed_data" folder.
    """

    preprocess_folder(CONFIG['raw/'],
                      CONFIG['processed/'],
                      CONFIG['preprocessing'])
    

def get_dfs():

    df_company = pd.read_table(
        CONFIG['processed/company'],
        header=0,
        dtype={
            'id': 'Int64',
            'ogrn': 'string',
            'inn': 'string',
            'full_name': 'string'
        },
        na_values=['', ' ', 'NA', 'nan']
    )

    df_founder_natural = pd.read_table(
        CONFIG['processed/founder_natural'],
        header=0,
        dtype={
            'id': 'Int64',
            'company_id': 'Int64', # id компании которой владеют
            'inn': 'string',
            'last_name': 'string',
            'first_name': 'string',
            'second_name': 'string',
            'share': 'float',
            'share_percent': 'float'
        },
        na_values=['', ' ', 'NA', 'nan']
    )
    

    df_founder_legal = pd.read_table(
        CONFIG['processed/founder_legal'],
        header=0,
        dtype={
            'id': 'Int64',
            'company_id': 'Int64', # id компании которой владеют
            'ogrn': 'string',
            'inn': 'string',
            'full_name': 'string',
            'share': 'float',
            'share_percent': 'float'
        },
        na_values=['', ' ', 'NA', 'nan']
    )

    if df_company['ogrn'].duplicated().any():
        raise ValueError("Столбец 'ogrn' в df_company содержит дубликаты.")

    # * Добавляем колонку owner_id
    df_founder_legal = df_founder_legal.merge( 
        df_company[['ogrn', 'id']].rename(columns={'id': 'owner_id'}),
        on='ogrn',
        how='left'
    )

    return df_company, df_founder_legal, df_founder_natural


os.makedirs(CONFIG['raw/'], exist_ok=True)
os.makedirs(CONFIG['processed/'], exist_ok=True)
os.makedirs(CONFIG['final/'], exist_ok=True)

with open(CONFIG['final/results'], 'w', encoding='utf-8') as f:
    f.write('test')

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
    preprocess()

    company_df, founder_legal_df, founder_natural_df = get_dfs()

    # Проверка наличия несоответствий
    missing_company_ids = set(founder_legal_df['company_id']) - set(company_df['id'])
    if missing_company_ids:
        print(f"Отсутствующие company_id в company.tsv: {missing_company_ids}")


    #indirect_shares = kopeika(company_df=company_df, founder_legal_df=founder_legal_df, founder_natural_df=founder_natural_df)
    
    #postprocess_default(indirect_shares, comps) #FIXME
