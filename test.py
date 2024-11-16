# from app.common.impute import impute_df
import pandas as pd
import numpy as np

def impute_df(df):
    

    df_out = df
    return df_out

founder_natural_df = pd.read_csv('founder_natural.tsv', sep='\t')

# опционально, мы оставляем только последние данные по одинаковым записям для отдельных компаний
# founder_natural_df = founder_natural_df.drop_duplicates(subset=['company_id', 'inn', 'last_name', 'first_name', 'second_name'], keep='last')
companies = founder_natural_df['company_id'].unique()


# --------------------------------------- found 
for el in companies[1:10]:
    df_unique = founder_natural_df.loc[founder_natural_df['company_id'] == el]

    if not df_unique['share'].isnull().any():
        sum_unique = df_unique['share'].sum()
        sum_unique_percent = df_unique['share_percent'].sum()


        if df_unique['share_percent'].isnull().any():
            # print(df_unique)
            pass
            
            # print(founder_natural_df[founder_natural_df.loc[founder_natural_df['inn'] == man]])


    else:
        sum_unique = np.NaN
        # print(df_unique)
        # print(sum_unique)





# we should look only at share if confused
# filtered_df_sh = founder_natural_df[founder_natural_df['share'].isnull()]
# filtered_df_percent = filtered_df_sh[filtered_df_sh['share_percent'].notnull()]
# print(filtered_df_percent)


# ---------------------------------------- found max share_percent
max_p = 0
for el in companies:
    df_unique = founder_natural_df.loc[founder_natural_df['company_id'] == el]

    sum_percent = df_unique['share_percent'].sum()

    if sum_percent < 0.5 and sum_percent > 0.1:
        # print(df_unique)
        pass

    if sum_percent > max_p:
        max_p = sum_percent
        max_df_u = df_unique

print(max_p) 
print(max_df_u)

# оценка капитала