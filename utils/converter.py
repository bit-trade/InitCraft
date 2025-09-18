import os
import json
from logging import getLogger
from constant import base_dir, LogSet


conv_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
conv_log.setLevel(LogSet['level'])
if not conv_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    conv_log.addHandler(handler)


def txt_to_json(files_in: list[str]) -> list[str]:
    """
    Конвертирует список текстовых конфигурационных файлов в формат JSON.

    Для каждого указанного пути в `files_in`:
    - Проверяет существование файла
    - Считывает содержимое построчно
    - Формирует структуру словаря вида {<исходный_путь>: [<строки>]}
    - Сохраняет результат в виде JSON-файла с именем <basename>.json в директории <base_dir>/converted
    - Логирует успех или предупреждение при отсутствии файла

    :param files_in: Список путей к текстовым файлам, подлежащим конвертации
    :return: Список путей к успешно созданным JSON-файлам
    """

    converted = []

    try:
        for file in files_in:
            file_out = os.path.basename(file)
            if not os.path.isfile(file):
                conv_log.warning(f'конвертируемый файл {file} не найден')
                print(f'Файл {file_out} не найден\nВ логах детальнее')
                continue

            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            data = {file: lines}
            conv_dir = os.path.join(base_dir, 'converted')
            os.makedirs(conv_dir, exist_ok=True)
            json_file = f'{file_out}.json'
            path_file = os.path.join(conv_dir, json_file)
            with open(path_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            conv_log.info(f'{file} успешно конвертирован в {path_file}')
            converted.append(path_file)

        return converted

    except Exception as e:
        conv_log.error(f'ошибка при конвертации {f}: {e}')
        print(f'Ошибка при конвертации{f}: {e}')
        return converted

