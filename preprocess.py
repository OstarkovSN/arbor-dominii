import os

def process_file(file_path: str, output_path: str):
    """
    Открывает файл, проверяет строки, и объединяет строки, не начинающиеся с цифры,
    с предыдущей строкой.

    :param file_path: Путь к входному файлу.
    :param output_path: Путь к выходному файлу.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = ['']

    for line in lines:
        if line.strip() and line.lstrip()[0].isdigit():  # Если строка начинается с цифры
            processed_lines.append(line.strip())  # Удаляем лишние пробелы и сохраняем строку
        else:
            # Если строка не начинается с цифры, объединяем с предыдущей
            if processed_lines:
                processed_lines[-1] += line.strip()  # Добавляем текущую строку к предыдущей

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write("\n".join(processed_lines))


if __name__ == '__main__':
    folder_path = 'data'
    output_folder_path = 'processed_data'

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        output_path = os.path.join(output_folder_path, filename)
        process_file(file_path=file_path, output_path=output_path)