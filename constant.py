import os
import logging


base_dir = os.path.dirname(os.path.abspath(__file__))

utility_name = 'InitCraft'
utility_version = '1.0.0-beta'

LogSet = {
    'level': logging.INFO,
    'handler': logging.FileHandler(f'{os.path.join(base_dir, utility_name)}.log', mode='w'),
    'formatter': logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'),
}

menu_items = [
    (f'Загрузить карту конфигурации env.json из корневого каталога {utility_name}', (1, 'default')),
    ('Сгенерировать начальную карту конфигурации JSON формата', (2, 'generate')),
    ('Использовать свою карту конфигурации JSON формата', (3, None)),
    (f'Заполнить карту конфигурации в корневом каталоге {utility_name}', (4, None))
]
