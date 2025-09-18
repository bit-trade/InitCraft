import os
import sys
import argparse
from utils.editor import ConfigMaker
from utils.backup import create_backup, rollback_mode
from utils.os_worker import OSWorker
from utils.converter import txt_to_json
from logging import getLogger
from constant import LogSet, utility_name, menu_items, utility_version


cli_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
cli_log.setLevel(LogSet['level'])
if not cli_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    cli_log.addHandler(handler)


def exit_with_error(log_message: str, message: str):
    cli_log.error(log_message)
    print(message)
    sys.exit(1)


def str2bool(value):
    if isinstance(value, bool):
        return value

    if value.lower() in ('yes', 'y', 'true', 't', '1'):
        return True
    elif value.lower() in ('no', 'n', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected (yes/y, true/t or 1).')


def arg_settings():
    parser = argparse.ArgumentParser(
        prog='initcraft',
        description=f'{utility_name} v{utility_version} — утилита для первичной настройки VPS-серверов и хост-машин',
        epilog='Примеры использования:\n'
               '    python3 initcraft -m 1 --apply\n'
               '    python3 initcraft --mode 2\n'
               '    python3 initcraft -m 3 -a --config /home/admin/env.json\n'
               '    python3 initcraft -m 4 --config "/etc/hosts /etc/hostname /etc/ssh/sshd_config"\n'
               '    python3 initcraft -b --config "/etc/hosts /etc/hostname /etc/ssh/sshd_config"\n'
               '    python3 initcraft --convert true --config /etc/hostname,/etc/fstab,/etc/nftables.conf\n'
               '    python3 initcraft --rollback --config "/etc/fstab, /etc/nftables.conf, /etc/ssh/sshd_config"\n'
               '\n'
               'Если аргументы не указаны - запустится TUI-режим.\n'
               ' ',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-m', '--mode', type=int, choices=[1, 2, 3, 4],
                        help='Режим запуска:\n'
                             f'  1 (default): {menu_items[0][0]}\n'
                             f'  2 (generate): {menu_items[1][0]}\n'
                             f'  3 (file): {menu_items[2][0]}\n'
                             f'  4 (inline): {menu_items[3][0]}\n')
    parser.add_argument('--config', type=str,
                        help='Путь к файлу JSON формата (для режима "file") или\n'
                             'список путей к конфиг-файлам (для режима "inline")')
    parser.add_argument('-b', '--backup', type=str2bool, nargs='?', const=True,
                        help='Создать резервные копии конфигурационных файлов (yes/y, true/t или 1)')
    parser.add_argument('--convert', type=str2bool, nargs='?', const=True,
                        help='Преобразовать текстовые конфигурационные файлы в формат JSON')
    parser.add_argument('--rollback', type=str2bool, nargs='?', const=True,
                        help='Восстановить конфиг-файлы из последних (по времени) созданных бэкапов,\n'
                             'расположенных в каталоге "backup"')
    parser.add_argument( '-a', '--apply', type=str2bool, nargs='?', const=True,
                         help='Применить настройки из карты конфигурации')
    parser.add_argument('-r', '--reboot', type=str2bool, default=False, nargs='?', const=True,
                        help='Перезагрузка системы (обычно после применения настроек на сервере)')

    return parser.parse_args()


def run_cli(args):
    config_mode = args.mode
    config_line = args.config or ''
    if config_mode in {3, 4} and not config_line:
        exit_with_error(f'для режима {config_mode} не задана строка параметров config_line (--config)',
                        f'[ERROR] Для режима "{args.mode}" необходимо указать --config')
    elif not config_mode and args.apply:
        exit_with_error(f'аргумент --apply используется без заданного режима',
                        f'[ERROR] Для применения настроек необходимо указать режим')

    def paths():
        path_list = ConfigMaker(config_mode or 1, config_line).config_map['config_files']
        return path_list

    if args.backup:
        print('[INFO] Резервное копирование конфиг-файлов')
        cli_log.info('резервное копирование конфигурационных файлов')
        return create_backup(paths())

    if args.convert:
        print('[INFO] Конвертация конфиг-файлов в JSON')
        cli_log.info('конвертация файлов в JSON формат')
        return txt_to_json(paths())

    if args.rollback:
        print('[INFO] Восстановление конфиг-файлов из бэкапов')
        cli_log.info('восстановление конфигурационных файлов из резервных копий')
        return rollback_mode(paths())

    if config_mode:
        editor = ConfigMaker(config_mode, config_line)
        if args.apply:
            editor.edit_file()

    if args.reboot:
        worker = OSWorker()
        worker.os_reboot()
