import os

import pandas as pd
from app.common.structure import OwnershipStructure
from app.common.holder import HoldersList, Holder, iteratively_estimate_indirect_shares

from app.common.preprocess import preprocess
from app.common.postprocess import postprocess_default
import pandas as pd

os.makedirs('environment', exist_ok=True)

with open('environment/results.tsv', 'w', encoding='utf-8') as f:
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
    #preprocess_default()

    company_df = pd.read_csv("app/data/processed/company.tsv", sep="\t")
    founder_legal_df = pd.read_csv("app/data/processed/founder_legal.tsv", sep="\t")
    founder_natural_df = pd.read_csv("app/data/processed/founder_natural.tsv", sep="\t")

    # Проверка наличия несоответствий
    missing_company_ids = set(founder_legal_df['company_id']) - set(company_df['id'])
    if missing_company_ids:
        print(f"Отсутствующие company_id в company.tsv: {missing_company_ids}")


    indirect_shares = kopeika(company_df=company_df, founder_legal_df=founder_legal_df, founder_natural_df=founder_natural_df)
    
    postprocess_default(indirect_shares, comps) #FIXME
