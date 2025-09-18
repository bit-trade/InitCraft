import os
import sys
import json
from logging import getLogger
from constant import base_dir, LogSet
from utils.converter import txt_to_json


edit_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
edit_log.setLevel(LogSet['level'])
if not edit_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    edit_log.addHandler(handler)


class ConfigMaker:
    """
    Класс ConfigMaker управляет логикой обработки и редактирования системных конфигурационных файлов на основе различных
     режимов и источников данных.

    Возможности:
    - Поддержка четырёх режимов загрузки конфигураций: default, generate, file, inline
    - Работа с файлом `env.json` (чтение, создание, редактирование)
    - Поддержка ввода путей к конфигам как строка (режим inline)
    - Интеграция с конвертером текстовых конфигураций в JSON
    - Прямое редактирование целевых конфигурационных файлов по карте конфигурации
    - Логгирование всех операций

    Используется для первичной инициализации и автоматического применения настроек на сервере (VPS/ServerPC).
    """

    def __init__(self, conf_mode: int, config_line: str) -> None:
        self.config_mode = None
        self.environ_json = os.path.join(base_dir, 'env.json')
        self.inline_paths = []
        self.config_map = {}

        if conf_mode in {1, 2, 4} and not self.check_line(self.environ_json):
            self.create_json(self.environ_json)

        if conf_mode in {1, 2}:
            self.config_mode = {1: 'default', 2: 'generate'}[conf_mode]
            self.config_map = self.load_json(self.environ_json)

        elif conf_mode == 3:
            if self.check_line(config_line):
                self.config_mode = 'file'
                self.environ_json = config_line
                self.config_map = self.load_json(self.environ_json)
            else:
                self.exit_with_error(f'путь к файлу конфигурации либо его формат неверны: {config_line}',
                                     f'[ERROR] Неверный путь или формат конфигурации: {config_line}')

        elif conf_mode == 4:
            if self.inline_path_list(config_line):
                self.config_mode = 'inline'
                self.inline_paths = self.parse_path_list(config_line)
                self.config_map = self.load_json(self.environ_json)
                self.config_map['config_files'] = (self.config_map['config_files'] + self.inline_paths
                                                   if self.config_map.get('config_files') else self.inline_paths)
                converter = txt_to_json(self.config_map['config_files'])
                self.edit_json(converter)
                self.config_map = self.load_json(self.environ_json)
            else:
                self.exit_with_error(f'одно или несколько недопустимых имён фалов конфигурации: {config_line}',
                                     f'[ERROR] Недопустимое имя конфигурационного файла: {config_line}')

        else:
            self.exit_with_error(f'в строке конфигурации {config_line or "None"} недопустимые значения',
                                 f'[ERROR] Недопустимое значение config_line: {config_line or "None"}')

    def exit_with_error(self, log_message: str, message: str):
        edit_log.error(log_message)
        print(message)
        sys.exit(1)

    def check_line(self, line: str) -> bool:
        if os.path.isfile(line) and line.endswith('.json'):
            return True
        else:
            return False

    def parse_path_list(self, value: str) -> list[str]:
        cleaned = value.replace(', ', ',').replace(' ,', ',').replace(' ', ',')
        return [p.strip() for p in cleaned.split(',') if p.strip()]

    def inline_path_list(self, value: str) -> bool:
        candidates = self.parse_path_list(value)
        return all(not p.endswith(("/", "\0", "*", "?", "[", "]", "$", "!", "\"", "'", "\\", "|", ">", "<", "&", ",", ";", "`")) for p in candidates)

    def create_json(self, path):
        if not os.path.exists(path) and os.path.dirname(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)

        json_string = '{"_comment": "You can find examples of properly formatted JSON files in repository: https://github.com/bit-trade/InitCraft", "config_files": []}'
        data = json.loads(json_string)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
            edit_log.debug(f'автоматическое создание карты конфигурации: {path}')

    def load_json(self, path) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data.pop("_comment", None)
        return data

    def edit_json(self, path_list: list):
        with open(self.environ_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data['config_files'] = self.config_map['config_files']
        for path in path_list:
            with open(path, 'r', encoding='utf-8') as f:
                convert_data = json.load(f)

            for key, value in convert_data.items():
                data[key] = value

        with open(self.environ_json, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            edit_log.info(f'файл конфигурации {self.environ_json} обновлена актуальными данными')
            print(f"[OK] Карта конфигурации {self.environ_json} перезаписана")

    def edit_file(self):
        self.config_map.pop("config_files", None)
        for key, value in self.config_map.items():
            edit_log.info(f'редактирование файла конфигурации {key}')
            print(f'[INFO] Редактирование файла: {key}')
            self.update_file(key, value)

    def update_file(self, file_path: str, new_entry: list[str]):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_entry)
                edit_log.info(f'файл {file_path} обновлен актуальными данными')
                print(f"[OK] Файл {file_path} перезаписан")

        except Exception as e:
            edit_log.error(f'перезапись {file_path} не удалась: {e}')
            print(f'[ERROR] Ошибка при записи {file_path}')
