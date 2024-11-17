import os
import re
from typing import Sequence
import pandas as pd

FILES = ['company.tsv', 'founder_legal.tsv', 'founder_natural.tsv']
class Preprocessor:
    '''
    Абстрактный класс для предобработки текста.'''
    def preprocess(self, text: str) -> str:
        """
        Preprocesses a list of strings, returning a new list of strings.

        The exact preprocessing operation should be implemented in subclasses.
        """
        raise NotImplementedError


class CompanyNamesMerger(Preprocessor):
    """
    Объединяет строки, не начинающиеся с цифры, с предыдущей строкой.
    """
    def preprocess(self, text: str) -> str:
        lines = text.splitlines()
    
        processed_lines = ['']

        for line in lines:
            if line.strip() and line.lstrip()[0].isdigit():  # Если строка начинается с цифры
                processed_lines.append(line.strip())  # Удаляем лишние пробелы и сохраняем строку
            else:
                # Если строка не начинается с цифры, объединяем с предыдущей
                if processed_lines:
                    processed_lines[-1] += line.strip()  # Добавляем текущую строку к предыдущей

        return '\n'.join(processed_lines)  # Возвращаем объединенные строки вместо списка строк


class QMRemover(Preprocessor):
    """
    Закрывает незакрытые кавычки в строках.
    """
    def preprocess(self, text: str) -> str:
        """
        Processes the input text, ensuring all quotes are closed.

        This method iterates over each line of the input text, checking if the line contains an unclosed quote.
        If a line has an odd number of quotes, it appends a closing quote to the end of the line.
        The processed lines are then joined and returned as a single string.

        :param text: The input string to process.
        :return: A string with all quotes properly closed.
        """
        lines = text.splitlines()
        processed_lines = []

        for line in lines:
            values = line.split('\t')
            for i, value in enumerate(values):
                if value.count('"') % 2 != 0:
                    values[i] += '"'
            line = '\t'.join(values)
            processed_lines.append(line)


        return '\n'.join(processed_lines)

def process_file(file_path: str, output_path: str, preprocessors: Sequence[Preprocessor]):
    """
    Запускает цепочку предпроцессоров над входным файлом и записывает результат в выходной файл.

    :param file_path: Путь к входному файлу.
    :param output_path: Путь к выходному файлу.
    :param preprocessors: Список предпроцессоров.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    for preprocessor in preprocessors:
        text = preprocessor.preprocess(text)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)

def preprocess_folder(folder_path: str, output_folder_path: str, preprocessors: Sequence[Preprocessor]):
    """
    Обрабатывает файлы, лежащие в директории data, и записывает результаты в processed_data.
    """

    for filename in FILES:
        file_path = os.path.join(folder_path, filename)
        output_path = os.path.join(output_folder_path, filename)
        process_file(file_path, output_path, preprocessors)

def get_dfs(company_path, founder_natural_path, founder_legal_path):
    df_company = pd.read_table(
        company_path,
        header=0,
        dtype={
            'id': 'Int64',
            'ogrn': 'string',
            'inn': 'string',
            'full_name': 'string'
        },
        na_values=['', ' ', 'NA', 'nan']
    )

    df_founder_natural = pd.read_table(
        founder_natural_path,
        header=0,
        dtype={
            'id': 'Int64',
            'company_id': 'Int64', # id компании которой владеют
            'inn': 'string',
            'last_name': 'string',
            'first_name': 'string',
            'second_name': 'string',
            'share': 'float',
            'share_percent': 'float'
        },
        na_values=['', ' ', 'NA', 'nan']
    )
    

    df_founder_legal = pd.read_table(
        founder_legal_path,
        header=0,
        dtype={
            'id': 'Int64',
            'company_id': 'Int64', # id компании которой владеют
            'ogrn': 'string',
            'inn': 'string',
            'full_name': 'string',
            'share': 'float',
            'share_percent': 'float'
        },
        na_values=['', ' ', 'NA', 'nan']
    )

    if df_company['ogrn'].duplicated().any():
        raise ValueError("Столбец 'ogrn' в df_company содержит дубликаты.")

    # * Добавляем колонку owner_id
    df_founder_legal = df_founder_legal.merge( 
        df_company[['ogrn', 'id']].rename(columns={'id': 'owner_id'}),
        on='ogrn',
        how='left'
    )

    return df_company, df_founder_legal, df_founder_natural

