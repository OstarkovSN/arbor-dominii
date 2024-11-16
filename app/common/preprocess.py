import os
import re
from typing import Sequence

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


class QMCloser(Preprocessor):
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
            if line.count('"') % 2 != 0:  # Проверяем, есть ли незакрытая кавычка в третьем значении
                for i, value in enumerate(values):
                    try:
                        float(value)
                    except ValueError:
                        values[i] += '"'  # Закрываем кавычку
                        break
            processed_lines.append('\t'.join(values))

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

def preprocess_default():
    """
    Processes files in the "data" folder using the CompanyNamesMerger preprocessor
    and writes the results to the "processed_data" folder.
    """
    folder_path = ''
    output_folder_path = 'app/data/processed'
    preprocessors = [CompanyNamesMerger(), QMCloser()]
    preprocess_folder(folder_path, output_folder_path, preprocessors)

if __name__ == '__main__':
    preprocess_default()