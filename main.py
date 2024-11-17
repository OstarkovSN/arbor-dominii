# main.py

import os
from app.common.preprocess import preprocess_folder, get_dfs, CompanyNamesMerger, QMRemover
from app.common.impute import impute_data_fast
from app.common.matrix import (
    build_entity_index, 
    build_ownership_relations, 
    build_ownership_matrix, 
    compute_ultimate_ownership, 
    get_natural_to_company_ownership, 
    get_company_to_natural_ownership
)
import pandas as pd

def main():
    # Определяем пути к данным
    raw_data_folder = 'app/data/raw'
    processed_data_folder = 'app/data/processed'
    
    # Определяем последовательность предобработчиков
    preprocessors = [CompanyNamesMerger(), QMRemover()]
    
    # Предобрабатываем данные
    preprocess_folder(raw_data_folder, processed_data_folder, preprocessors)
    
    # Пути к предобработанным файлам
    company_path = os.path.join(processed_data_folder, 'company.tsv')
    founder_natural_path = os.path.join(processed_data_folder, 'founder_natural.tsv')
    founder_legal_path = os.path.join(processed_data_folder, 'founder_legal.tsv')
    
    # Получаем DataFrame'ы
    df_company, df_founder_legal, df_founder_legal_nonterminal, df_founder_legal_terminal, df_founder_natural = get_dfs(
        company_path, founder_natural_path, founder_legal_path
    )
    
    # Выполняем импутацию данных (если необходимо)
    df_founder_natural = impute_data_fast(df_founder_natural)
    
    # Строим индекс сущностей
    entity_to_idx, idx_to_entity, natural_person_indices = build_entity_index(
        df_company, df_founder_natural, df_founder_legal
    )
    
    # Строим отношения владения
    ownership_relations = build_ownership_relations(
        df_founder_natural, df_founder_legal, entity_to_idx
    )
    
    # Строим матрицу владения
    num_entities = len(entity_to_idx)
    M = build_ownership_matrix(num_entities, ownership_relations)
    
    # Вычисляем итоговое владение
    ultimate_ownership = compute_ultimate_ownership(M, natural_person_indices)
    
    # Извлекаем владение от физических лиц к компаниям
    natural_to_company = get_natural_to_company_ownership(
        ultimate_ownership, natural_person_indices, idx_to_entity
    )
    
    # Извлекаем владение компаниями от физических лиц
    company_to_natural = get_company_to_natural_ownership(
        ultimate_ownership, natural_person_indices, idx_to_entity
    )
    
    # Преобразуем результаты в удобный формат для вывода
    # Для каждого физического лица: список компаний с процентами владения
    natural_ownership_df = []
    for person_idx, companies in natural_to_company.items():
        person_id = idx_to_entity[person_idx]
        inn = person_id.replace("natural_", "")
        for company_idx, percent in companies.items():
            company_id = idx_to_entity[company_idx].replace("company_", "")
            natural_ownership_df.append({
                'natural_inn': inn, 
                'company_ogrn': company_id, 
                'share_percent': percent
            })
    
    df_natural_ownership = pd.DataFrame(natural_ownership_df)
    
    # Для каждой компании: список физических лиц с процентами владения
    company_ownership_df = []
    for company_idx, persons in company_to_natural.items():
        company_id = idx_to_entity[company_idx].replace("company_", "")
        for person_idx, percent in persons.items():
            inn = idx_to_entity[person_idx].replace("natural_", "")
            company_ownership_df.append({
                'company_ogrn': company_id, 
                'natural_inn': inn, 
                'share_percent': percent
            })
    
    df_company_ownership = pd.DataFrame(company_ownership_df)
    
    # Создаём папку для результатов, если её нет
    os.makedirs('app/data/results', exist_ok=True)
    
    # Сохраняем результаты в CSV файлы
    df_natural_ownership.to_csv('app/data/results/natural_to_company_ownership.csv', index=False)
    df_company_ownership.to_csv('app/data/results/company_to_natural_ownership.csv', index=False)
    
    print("Вычисление владения завершено и результаты сохранены.")

if __name__ == '__main__':
    main()
