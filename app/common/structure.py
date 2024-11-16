import pandas as pd

class OwnershipStructure:
    def __init__(self, company_df, founder_legal_df, founder_natural_df):
        """
        Инициализация структуры данных на основе данных о компаниях, юридических и физических владельцах.
        """
        self.companies = self._load_companies(company_df)
        self.legal_owners = self._load_legal_owners(founder_legal_df)
        self.natural_owners = self._load_natural_owners(founder_natural_df)

    def _load_companies(self, df):
        """
        Загружает компании в словарь с основными данными.
        """
        return {
            row['id']: {
                'ogrn': row['ogrn'],
                'inn': row['inn'],
                'full_name': row['full_name'],
                'owners': []
            }
            for _, row in df.iterrows()
        }

    def _load_legal_owners(self, df):
        """
        Загружает юридических владельцев.
        """
        legal_owners = {}
        for _, row in df.iterrows():
            owner = {
                'company_id': row['company_id'],
                'ogrn': row['ogrn'],
                'inn': row['inn'],
                'full_name': row['full_name'],
                'share_percent': row['share_percent']
            }
            legal_owners[row['id']] = owner
            self.companies[row['company_id']]['owners'].append({
                'type': 'legal',
                'id': row['id'],
                'share_percent': row['share_percent']
            })
        return legal_owners

    def _load_natural_owners(self, df):
        """
        Загружает физических владельцев.
        """
        natural_owners = {}
        for _, row in df.iterrows():
            owner = {
                'company_id': row['company_id'],
                'inn': row['inn'],
                'last_name': row['last_name'],
                'first_name': row['first_name'],
                'second_name': row['second_name'],
                'share_percent': row['share_percent']
            }
            natural_owners[row['id']] = owner
            self.companies[row['company_id']]['owners'].append({
                'type': 'natural',
                'id': row['id'],
                'share_percent': row['share_percent']
            })
        return natural_owners

    def get_company_owners(self, company_id):
        """
        Возвращает владельцев компании (и юридических, и физических).
        """
        return self.companies[company_id]['owners']
