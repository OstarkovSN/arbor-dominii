import os
import pandas as pd
from app.common.structure import OwnershipStructure
from app.common.holder import HoldersList, Holder, iteratively_estimate_indirect_shares
from app.common.preprocess import preprocess_default

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
    
    # Сохраняем результаты
    os.makedirs('app/data/final', exist_ok=True)

    with open("'app/data/final/output.tsv", "w") as f:
        f.write("company_id\togrn\tinn\tfull_name\tbeneficiaries\n")
        for company_id, shares in indirect_shares.items():
            company = structure.companies[company_id]
            beneficiaries = "\n".join(
                f"{beneficiary_id}\t{share*100:.2f}%"
                for beneficiary_id, share in shares.items()
                if share > 0.25
            )
            f.write(
                f"{company_id}\t{company['ogrn']}\t{company['inn']}\t{company['full_name']}\t{beneficiaries}\n"
            )

if __name__ == "__main__":
    #preprocess_default()

    company_df = pd.read_csv("app/data/processed/company.tsv", sep="\t")
    founder_legal_df = pd.read_csv("app/data/processed/founder_legal.tsv", sep="\t")
    founder_natural_df = pd.read_csv("app/data/processed/founder_natural.tsv", sep="\t")

    # Проверка наличия несоответствий
    missing_company_ids = set(founder_legal_df['company_id']) - set(company_df['id'])
    if missing_company_ids:
        print(f"Отсутствующие company_id в company.tsv: {missing_company_ids}")


    kopeika(company_df=company_df, founder_legal_df=founder_legal_df, founder_natural_df=founder_natural_df)
