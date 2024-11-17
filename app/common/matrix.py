# app/common/matrix.py

import pandas as pd
from scipy.sparse import dok_matrix, csr_matrix
import numpy as np

def build_entity_index(df_company, df_founder_natural, df_founder_legal):
    """
    Назначает уникальные целочисленные индексы всем сущностям (компаниям и физическим лицам).

    Возвращает:
        entity_to_idx: словарь, сопоставляющий идентификаторы сущностей с уникальными индексами
        idx_to_entity: словарь, сопоставляющий уникальные индексы с идентификаторами сущностей
        natural_person_indices: множество индексов, соответствующих физическим лицам
    """
    entity_to_idx = {}
    idx_to_entity = {}
    current_idx = 0
    
    # Добавляем компании на основе 'ogrn'
    for _, row in df_company.iterrows():
        ogrn = row['ogrn']
        company_id = f"company_{ogrn}"
        if company_id not in entity_to_idx:
            entity_to_idx[company_id] = current_idx
            idx_to_entity[current_idx] = company_id
            current_idx += 1
    
    # Добавляем физические лица
    for _, row in df_founder_natural.iterrows():
        inn = row['inn']
        # Предполагаем, что 'inn' уникально идентифицирует физическое лицо
        person_id = f"natural_{inn}"
        if person_id not in entity_to_idx:
            entity_to_idx[person_id] = current_idx
            idx_to_entity[current_idx] = person_id
            current_idx += 1
    
    # Добавляем юридические лица (другие компании) на основе 'ogrn'
    for _, row in df_founder_legal.iterrows():
        ogrn = row['ogrn']
        legal_id = f"company_{ogrn}"
        if legal_id not in entity_to_idx:
            entity_to_idx[legal_id] = current_idx
            idx_to_entity[current_idx] = legal_id
            current_idx += 1
    
    # Сбор индексов, соответствующих физическим лицам
    natural_person_indices = set()
    for entity, idx in entity_to_idx.items():
        if entity.startswith("natural_"):
            natural_person_indices.add(idx)
    
    return entity_to_idx, idx_to_entity, natural_person_indices

def build_ownership_relations(df_founder_natural, df_founder_legal, entity_to_idx):
    """
    Строит список кортежей (owner_idx, company_idx, share_percent), представляющих отношения владения.
    """
    ownership_relations = []
    
    # Владение физическими лицами
    for _, row in df_founder_natural.iterrows():
        inn = row['inn']
        person_id = f"natural_{inn}"
        owner_idx = entity_to_idx.get(person_id)
        if owner_idx is None:
            continue  # Пропускаем, если физическое лицо не найдено
        company_ogrn = row.get('company_ogrn')
        if pd.isna(company_ogrn):
            continue
        company_identifier = f"company_{company_ogrn}"
        company_idx = entity_to_idx.get(company_identifier)
        if company_idx is None:
            continue
        share_percent = row['share_percent'] / 100.0
        ownership_relations.append((owner_idx, company_idx, share_percent))
    
    # Владение юридическими лицами (другими компаниями)
    for _, row in df_founder_legal.iterrows():
        ogrn = row['ogrn']
        legal_id = f"company_{ogrn}"
        owner_idx = entity_to_idx.get(legal_id)
        if owner_idx is None:
            continue
        company_ogrn = row.get('company_ogrn')
        if pd.isna(company_ogrn):
            continue
        company_identifier = f"company_{company_ogrn}"
        company_idx = entity_to_idx.get(company_identifier)
        if company_idx is None:
            continue
        share_percent = row['share_percent'] / 100.0
        ownership_relations.append((owner_idx, company_idx, share_percent))
    
    return ownership_relations

def build_ownership_matrix(num_entities, ownership_relations):
    """
    Строит разреженную матрицу владения.

    M[i,j] = процент владения j, принадлежащий i
    """
    M = dok_matrix((num_entities, num_entities), dtype=np.float64)
    for owner, company, share in ownership_relations:
        if share > 0:
            M[owner, company] += share
    return M.tocsr()

def compute_ultimate_ownership(M, natural_person_indices, max_iterations=100, tol=1e-6):
    """
    Вычисляет итоговое владение как сумму M + M^2 + M^3 + ...

    Args:
        M: матрица владения (разреженная csr матрица)
        natural_person_indices: множество индексов, соответствующих физическим лицам
        max_iterations: максимальное число итераций
        tol: порог сходимости
    Returns:
        ultimate_ownership: csr матрица с итоговыми процентами владения от физических лиц к компаниям
    """
    # Инициализируем итоговую матрицу владения нулями
    num_entities = M.shape[0]
    ultimate_ownership = csr_matrix((num_entities, num_entities), dtype=np.float64)
    
    # Текущие владения для распространения
    current_ownership = M.copy()
    
    iteration = 0
    while iteration < max_iterations:
        # Добавляем текущие владения к итоговым
        ultimate_ownership += current_ownership
        
        # Вычисляем следующие владения
        current_ownership = current_ownership.dot(M)
        
        # Проверяем сходимость
        max_increment = current_ownership.max()
        if max_increment < tol:
            break
        iteration += 1
    return ultimate_ownership

def get_natural_to_company_ownership(ultimate_ownership, natural_person_indices, idx_to_entity):
    """
    Извлекает проценты владения от физических лиц к компаниям.
    """
    natural_to_company = {}
    for person_idx in natural_person_indices:
        ownerships = ultimate_ownership[person_idx].tocoo()
        for j, v in zip(ownerships.col, ownerships.data):
            if idx_to_entity[j].startswith("company_"):
                if person_idx not in natural_to_company:
                    natural_to_company[person_idx] = {}
                natural_to_company[person_idx][j] = v * 100.0  # Преобразуем в проценты
    return natural_to_company

def get_company_to_natural_ownership(ultimate_ownership, natural_person_indices, idx_to_entity):
    """
    Извлекает проценты владения компаниями от физических лиц.
    """
    company_to_natural = {}
    for j in range(ultimate_ownership.shape[1]):
        if not idx_to_entity[j].startswith("company_"):
            continue
        ownerships = ultimate_ownership[:, j].tocoo()
        for i, v in zip(ownerships.row, ownerships.data):
            if i in natural_person_indices:
                if j not in company_to_natural:
                    company_to_natural[j] = {}
                company_to_natural[j][i] = v * 100.0  # Преобразуем в проценты
    return company_to_natural
