# from app.common.impute import impute_df
import pandas as pd

def impute_data_long(founder_natural_df):
    founder_natural_df = pd.read_csv('founder_natural.tsv', sep='\t')
    founder_natural_df['company_id_inn'] = founder_natural_df['company_id'].apply(str) + founder_natural_df['inn'].apply(str)

    # опционально, мы оставляем только последние данные по одинаковым записям для отдельных компаний
    founder_natural_df = founder_natural_df.drop_duplicates(subset=['company_id', 'inn', 'last_name', 'first_name', 'second_name'], keep='last')
    companies = founder_natural_df['company_id'].unique()

    # --------------------------------------- found 
    # ? ебаная хуйня считает 10 минут пошла она нахуй
    for el in companies:
        df_unique = founder_natural_df.loc[founder_natural_df['company_id'] == el]

        if not df_unique['share'].isnull().any():
            sum_unique = df_unique['share'].sum()
            sum_unique_percent = df_unique['share_percent'].sum()
            people = df_unique['company_id_inn'].unique()
            for man in people:
                if sum_unique < 0.00000001:
                    founder_natural_df.loc[founder_natural_df['company_id_inn'] == man, 'share_percent'] = 0
                else:
                    founder_natural_df.loc[founder_natural_df['company_id_inn'] == man, 'share_percent'] = df_unique.loc[df_unique['company_id_inn'] == man, 'share'].iloc[0]/(sum_unique)
        else:
            df_unique_no_nan = df_unique.dropna(subset=['share'])
            if not df_unique_no_nan.shape[0] == 0:
                sum_unique = df_unique['share'].sum()
                sum_unique_percent = df_unique['share_percent'].sum()
                people = df_unique['company_id_inn'].unique()
                for man in people:
                    if sum_unique < 0.00000001:
                        founder_natural_df.loc[founder_natural_df['company_id_inn'] == man, 'share_percent'] = 0
                    else:
                        founder_natural_df.loc[founder_natural_df['company_id_inn'] == man, 'share_percent'] = df_unique.loc[df_unique['company_id_inn'] == man, 'share'].iloc[0]/(sum_unique)
            else:
                pass
    return founder_natural_df


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
    return lol_df

founder_natural_df = pd.read_csv('founder_natural.tsv', sep='\t')
result = impute_data_fast(founder_natural_df).drop_duplicates(subset=['company_id_inn'])
print(result.head(20))

companies = result['company_id'].unique()
print(companies)

for el in companies[0:40]:
    df_unique = result.loc[result['company_id'] == el]
    sum_unique_percent = df_unique['share_percent'].sum()
    print(sum_unique_percent)
    print(df_unique)