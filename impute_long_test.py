# from app.common.impute import impute_df
import pandas as pd
import numpy as np

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


for el in companies:
    df_unique = founder_natural_df.loc[founder_natural_df['company_id'] == el]
    sum_unique_percent = df_unique['share_percent'].sum()
    if df_unique['share'].isnull().any():
        print(sum_unique_percent)
        print(df_unique)




# we should look only at share if confused
# filtered_df_sh = founder_natural_df[founder_natural_df['share'].isnull()]
# filtered_df_percent = filtered_df_sh[filtered_df_sh['share_percent'].notnull()]
# print(filtered_df_percent)


# ---------------------------------------- found max share_percent
# max_p = 0
# for el in companies:
#     df_unique = founder_natural_df.loc[founder_natural_df['company_id'] == el]

#     sum_percent = df_unique['share_percent'].sum()

#     if sum_percent < 0.5 and sum_percent > 0.1:
#         # print(df_unique)
#         pass

#     if sum_percent > max_p:
#         max_p = sum_percent
#         max_df_u = df_unique

# print(max_p) 
# print(max_df_u)

# оценка капитала
# ! АККУРАТНО
# ? Че делать
# TODO можно включить NaN = 