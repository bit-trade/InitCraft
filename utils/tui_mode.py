"""
Модуль TUI-интерфейса для InitCraft.

Обеспечивает текстовый пользовательский интерфейс (TUI) с использованием библиотеки `curses` для управления конфигурацией
серверной среды. Пользователь может выбрать один из нескольких режимов взаимодействия: загрузка конфигурации,
генерация начальной карты, ручной ввод путей, а также применение настроек и перезагрузка системы.

Функции и возможности:
-----------------------
- Отрисовка заголовка и пунктов меню с подсветкой выбранного элемента.
- Обработка навигации по меню (вверх/вниз, Enter, Q).
- Ввод пользовательских данных (пути к JSON-файлу или списку конфигов).
- Динамическое добавление пункта "Применить конфигурацию" после её загрузки.
- Создание резервной копии конфигурационных файлов и их применение.
- Интерактивная перезагрузка системы после внесения изменений.

Зависимости:
------------
- `curses`: для создания TUI-интерфейса.
- `ConfigMaker`: основной класс для работы с конфигурацией.
- `OSWorker`: класс для перезагрузки системы.
- `create_backup`: функция создания резервной копии файлов.
- `constant`: содержит глобальные константы `utility_name`, `LogSet`, `menu_items`.

Функции:
--------
- draw_title(stdscr, width, cursor): отрисовывает заголовок окна.
- draw_menu(stdscr, selected_idx, message, menu_items): выводит пункты меню с выделением и пояснением.
- tui_main(stdscr): основной цикл работы TUI-интерфейса, обрабатывает пользовательский ввод.
- interactive(): обёртка над curses.wrapper, запускающая интерфейс и обрабатывающая исключения.

Пример запуска:
---------------
>>> from utils.tui_mode import interactive
>>> interactive()

Файл предназначен для запуска в терминальной среде (не использовать внутри IDE).
"""
import os
import curses
from utils.editor import ConfigMaker
from utils.os_worker import OSWorker
from utils.backup import create_backup
from logging import getLogger
from constant import LogSet, utility_name, menu_items


menu_tui_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
menu_tui_log.setLevel(LogSet['level'])
if not menu_tui_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    menu_tui_log.addHandler(handler)


def draw_title(stdscr, width, cursor = 0):
    curses.curs_set(cursor)
    title = f' {utility_name} настройка '.center(width, '~')
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(1, 2, title)
    stdscr.attroff(curses.color_pair(2))


def draw_menu(stdscr, selected_idx, message, menu_items):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_title(stdscr, 76)

    for idx, (item, _) in enumerate(menu_items):
        label = f'{idx + 1}. {item}' if idx < len(menu_items) - 1 else f'Q. {item}'
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(3 + idx, 4, label)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(3 + idx, 4, label)

    stdscr.addstr(5 + len(menu_items), 2, 'Выберите вариант и нажмите Enter')
    stdscr.addstr(6 + len(menu_items), 2, '↑/↓ — навигация, Q — выход')

    if message:
        len_message = len(message)
        stdscr.addstr(len(menu_items) + 8, 2, message[:w + len_message], curses.A_BOLD)

    stdscr.refresh()


def tui_main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    selected_idx = 0
    message = ''
    map_is_load = False
    editor = None

    while True:
        items_menu = menu_items.copy()
        if map_is_load:
            items_menu.append(('Применить загруженную конфигурацию', (9, None)))

        items_menu.append(('Для завершения', (0, None)))
        draw_menu(stdscr, selected_idx, message, items_menu)
        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(items_menu) - 1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            conf_mode, config_line = items_menu[selected_idx][1]

            if conf_mode == 0:
                return None

            if conf_mode == 9:
                create_backup(editor.config_map['config_files'])
                editor.edit_file()
                stdscr.clear()
                draw_title(stdscr, 44, 1)
                stdscr.addstr(3, 4, 'Перезагрузить систему? (Y/y или N/n)#> ')
                curses.echo()
                choice = stdscr.getstr(3, 42, 60).decode('utf-8')
                curses.noecho()
                if choice.lower() == 'y':
                    OSWorker().os_reboot()
                else:
                    return None

            elif conf_mode in {1, 2}:
                editor = ConfigMaker(conf_mode, config_line)
                if conf_mode == 1:
                    message = (f'[OK] Карта конфигурации загружена\n'
                               f'  config_files: {editor.config_map["config_files"]}')
                    map_is_load = True
                else:
                    message = (f'[OK] Начальная карта конфигурации создана\n'
                               f'  {editor.environ_json}')

            elif conf_mode == 3:
                stdscr.clear()
                draw_title(stdscr, 42, 1)
                stdscr.addstr(3, 4, 'Укажите путь к файлу конфигурации,\n    например - /home/admin/env.json #> ')
                curses.echo()
                path = stdscr.getstr(4, 40, 60).decode('utf-8')
                config_line = path
                curses.noecho()
                editor = ConfigMaker(conf_mode, config_line)
                message = f'[OK] Кастомная карта конфигурации загружена\n  {path}'
                map_is_load = True

            elif conf_mode == 4:
                stdscr.clear()
                draw_title(stdscr, 66, 1)
                stdscr.addstr(3, 4, 'Введите через пробел или запятую пути к файлам конфигурации,\n'
                                    '    например - /etc/hosts,/etc/hostname,/etc/ssh/sshd_config #> ')
                curses.echo()
                inline = stdscr.getstr(4, 64, 120).decode('utf-8')
                config_line = inline
                curses.noecho()
                editor = ConfigMaker(conf_mode, config_line)
                message = '[OK] Карта конфигурации заполнена вручную'

        elif key in [ord('q'), ord('Q')]:
            return None


def interactive():
    try:
        curses.wrapper(tui_main)
    except KeyboardInterrupt:
        menu_tui_log.warning('операция отменена')
        print('\n[WARNING] Операция отменена')
