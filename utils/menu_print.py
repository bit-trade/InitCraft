import os
import sys
from utils.editor import ConfigMaker
from utils.os_worker import OSWorker
from utils.backup import create_backup
from logging import getLogger
from constant import LogSet, utility_name, menu_items


menu_print_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
menu_print_log.setLevel(LogSet['level'])
if not menu_print_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    menu_print_log.addHandler(handler)


class Interactive:
    @staticmethod
    def user_choice() -> bool:
        while True:
            choise = input('Введите yes/y или no/n: ').strip().lower()
            if choise == 'yes' or choise == 'y':
                return True
            elif choise == 'no' or choise == 'n':
                return False
            else:
                print('[ERROR] Неверный ввод. Повторите попытку.')

    @staticmethod
    def about_settings() -> tuple[int, str]:
        map_is_load = False
        editor = None
        while True:
            print(' ', f' {utility_name} настройка '.center(76, '~'), ' ', sep='\n')
            if map_is_load:
                print(f'  1. {menu_items[0][0]}\n  2. {menu_items[1][0]}\n  3. {menu_items[2][0]}\n  4. {menu_items[3][0]}')
                print('  5. Применить загруженную конфигурацию')
                choice = input('  Введите 1, 2, 3, 4, 5 или exit (quit, cancel - для завершения)#> ').strip()
            else:
                print(f'  1. {menu_items[0][0]}\n  2. {menu_items[1][0]}\n  3. {menu_items[2][0]}\n  4. {menu_items[3][0]}')
                choice = input('  Введите 1, 2, 3, 4 или exit (quit, cancel - для завершения)#> ').strip()

            if choice == '5' and map_is_load:
                create_backup(editor.config_map['config_files'])
                editor.edit_file()
                print('Перезагрузить систему?')
                choice = input('Введите Y/y или N/n#> ').strip()
                if choice.lower() == 'y':
                    OSWorker().os_reboot()
                else:
                    return None

            if choice in {'1', '2'}:
                conf_mode = {'1': 1, '2': 2}[choice]
                config_line = {'1': 'default', '2': 'generate'}[choice]
                editor = ConfigMaker(conf_mode, config_line)
                if conf_mode == 1:
                    menu_print_log.debug('выбран вариант использования существующего файла конфигурации (env.json)')
                    print(f'[OK] Карта конфигурации загружена\n'
                          f'config_files: {editor.config_map["config_files"]}')
                    map_is_load = True
                elif conf_mode == 2:
                    print(f'[OK] Начальная карта конфигурации создана\n'
                          f'{editor.environ_json}')

            elif choice == '3':
                print('Укажите путь к файлу конфигурации,')
                path = input('например - /home/admin/env.json #> ').strip()
                if not 'json' in path:
                    print('[WARNING] В указанном пути нет файла JSON.\nПопробуйте снова')
                    continue

                editor = ConfigMaker(3, path)
                print(f'[OK] Кастомная карта конфигурации загружена\n{editor.environ_json}')
                map_is_load = True

            elif choice == '4':
                menu_print_log.debug('выбран вариант генерации нового файла конфигурации (env.json)')
                print('Введите через пробел или запятую пути к файлам конфигурации,')
                inline = input('например - /etc/hosts,/etc/hostname,/etc/ssh/sshd_config #> ')
                editor = ConfigMaker(4, inline)
                print(f'[OK] Карта конфигурации заполнена вручную\n{editor.config_map["config_files"]}')

            elif choice == 'exit' or choice == 'quit' or choice == 'cancel':
                menu_print_log.info(f'пользователь завершил работу {utility_name}')
                sys.exit(0)
            else:
                print('[ERROR] Неверный ввод. Повторите попытку.')

    @staticmethod
    def about_write_config_file() -> bool:
        print(f'[{utility_name}] Перезаписать файлы конфигурации?')
        return Interactive.user_choice()

    @staticmethod
    def about_reboot() -> bool:
        print(f'[{utility_name}] Хотите перезагрузить систему?')
        return Interactive.user_choice()




