import os
import pandas as pd
from app.common.structure import OwnershipStructure
from app.common.holder import HoldersList, Holder, iteratively_estimate_indirect_shares, build_tree
from app.common.preprocess import preprocess_default, get_dfs

def kopeika(
        company_df,
        natural_df,
        founder_legal_df,
        founder_legal_df_nonterminal,
        founder_legal_df_terminal,
        founder_natural_df,
):
    nonterminal, terminal = build_tree(
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
    )
    print('Done')
    
    # Сохраняем результаты
    os.makedirs('app/data/final', exist_ok=True)

#    with open("'app/data/final/output.tsv", "w") as f:
#        f.write("company_id\togrn\tinn\tfull_name\tbeneficiaries\n")
#        for company_id, shares in indirect_shares.items():
#            # TODO DELETE TERMINAL COMPNAIES
#            company = structure.companies[company_id]
#            beneficiaries = "\n".join(
#                f"{beneficiary_id}\t{share*100:.2f}%"
#                for beneficiary_id, share in shares.items()
#                if share > 0.25
#            )
#            f.write(
#                f"{company_id}\t{company['ogrn']}\t{company['inn']}\t{company['full_name']}\t{beneficiaries}\n"
#            )
#

def mk_natural(founder_natural_df):
    founder_natural_df['full_name'] =  \
     founder_natural_df['last_name'] + ' ' \
      + founder_natural_df['first_name'] + ' ' \
       + founder_natural_df['second_name']

    founder_natural_df['full_credentials'] = founder_natural_df['inn'].astype(str) + \
        '#' + founder_natural_df['full_name']
    
    natural_df = founder_natural_df[['full_credentials', 'inn']]
    natural_df = natural_df.drop_duplicates()
    return natural_df


if __name__ == "__main__":
    preprocess_default()

    company_df, founder_legal_df, founder_legal_df_nonterminal, founder_legal_df_terminal, founder_natural_df = get_dfs()
    natural_df = mk_natural(founder_natural_df)

    # Проверка наличия несоответствий
    missing_company_ids = set(founder_legal_df['company_id']) - set(company_df['id'])
    if missing_company_ids:
        print(f"Отсутствующие company_id в company.tsv: {missing_company_ids}")


    print('Start1')
    kopeika(
        company_df=company_df,
        natural_df=natural_df,
        founder_legal_df=founder_legal_df,
        founder_legal_df_nonterminal=founder_legal_df_nonterminal,
        founder_legal_df_terminal=founder_legal_df_terminal,
        founder_natural_df=founder_natural_df
    )
