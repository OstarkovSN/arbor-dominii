# from app.common.impute import impute_df
import pandas as pd

def impute_data_fast(founder_natural_df):
    preserve_df = founder_natural_df.copy()
    founder_natural_df['company_id_inn'] = founder_natural_df['company_id'].apply(str) + founder_natural_df['inn'].apply(str)
    founder_natural_df = founder_natural_df[::-1]
    founder_natural_df['evaluate'] = founder_natural_df['share'] / founder_natural_df['share_percent']
    founder_natural_df['company_id_inn'] = founder_natural_df['company_id'].apply(str) + founder_natural_df['inn'].apply(str)
    founder_natural_df = founder_natural_df[founder_natural_df['share_percent'] != 0]
    founder_natural_df = founder_natural_df.dropna(subset=['share', 'share_percent', 'evaluate'])
    founder_natural_df = founder_natural_df.drop_duplicates(subset=['company_id'])

    merged_df = preserve_df.merge(founder_natural_df, on='company_id')
    merged_df['share_percent'] = merged_df['share_x'] / merged_df['evaluate']
    lol_df = merged_df.drop(columns=['id_y','inn_y','last_name_y','first_name_y','second_name_y','share_y','share_percent_y'])
    lol_df = lol_df.rename(columns={'id_x': 'id', 'inn_x': 'inn', 'last_name_x':'last_name', 'first_name_x':'first_name', 'second_name_x':'second_name', 'share_x':'share'})
    return lol_df.drop_duplicates(subset=['company_id_inn'])

founder_natural_df = pd.read_csv('founder_natural.tsv', sep='\t')

result = impute_data_fast(founder_natural_df)

print(result.head(20))

companies = result['company_id'].unique()

print(companies)

for el in companies[0:40]:
    df_unique = result.loc[result['company_id'] == el]
    sum_unique_percent = df_unique['share_percent'].sum()
    print(sum_unique_percent)
    print(df_unique)