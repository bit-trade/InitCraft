import os
import shutil
from glob import glob
from datetime import datetime
from logging import getLogger
from constant import base_dir, LogSet


back_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
back_log.setLevel(LogSet['level'])
if not back_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    back_log.addHandler(handler)


def create_backup(paths: list[str]) -> list[str]:
    """
    Создаёт резервные копии заданных файлов конфигурации.

    Для каждого пути из списка `paths`:
    - Проверяет наличие файла
    - Создаёт подкаталог в директории `<base_dir>/backup/<относительный_путь>`
    - Формирует имя резервной копии с временной меткой: <имя_файла>.<timestamp>.bak
    - Копирует файл в указанный путь с сохранением метаданных (через shutil.copy2)
    - Логирует каждое действие (успех или ошибку)

    :param paths: Список абсолютных или относительных путей к файлам, которые необходимо забэкапить
    :return: Список имён успешно созданных файлов-бэкапов (без абсолютного пути)
    """

    create_backups = []
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    for path in paths:
        file = os.path.basename(path)
        if not os.path.isfile(path):
            back_log.warning(f'файл не найден: {path}')
            print(f'Файл не найден: {file}\nВ логах детальнее')
            continue

        dir_path = os.path.dirname(path.strip('/'))
        dirs_tree = os.path.join(base_dir, 'backup', dir_path)
        os.makedirs(dirs_tree, exist_ok=True)
        backup_file = f"{file}.{timestamp}.bak"
        backup_path = os.path.join(dirs_tree, backup_file)
        try:
            shutil.copy2(path, backup_path)
            back_log.info(f'создана резервная копия: {file} → {backup_file}')
            create_backups.append(backup_file)
        except Exception as e:
            back_log.error(f'ошибка при создании бэкапа для {file}: {e}')
            print(f'Ошибка при создании бэкапа для {file}: {e}')

    return create_backups


def rollback_mode(backups: list[str]) -> list[str]:
    """
    Выполняет восстановление конфигурационных файлов из последних доступных резервных копий.

    Для каждого файла из переданного списка:
    - Осуществляет поиск резервных копий с маской `<имя_файла>.*.bak` в директории `base_dir/backup/` (вложенно).
    - Выбирает самый свежий (по времени модификации) файл среди найденных.
    - Восстанавливает оригинальный файл, перезаписывая его содержимым последнего бэкапа.
    - Логирует успешные и неудачные операции.

    При отсутствии бэкапов или ошибках восстановления — печатает предупреждение/ошибку и продолжает цикл.

    Args:
        backups (list[str]): Список абсолютных или относительных путей к конфигурационным файлам,
                             для которых нужно выполнить откат (восстановление из бэкапов).

    Returns:
        list[str]: Список файлов, которые были успешно восстановлены.
    """
    rollbacks = []

    for backup in backups:
        filename = os.path.basename(backup)
        pattern = os.path.join(base_dir, 'backup/**/', f"{filename}.*.bak")
        candidates = glob(pattern, recursive=True)
        if not candidates:
            back_log.warning(f'резервные копии не найдены для {backup}')
            print(f"[WARNING] Бэкапы не найдены для: {backup}")
            continue

        # Сортировка по времени последней модификации
        file_backups = sorted(candidates, key=os.path.getmtime)
        latest_backup = file_backups[-1]
        try:
            shutil.copy2(latest_backup, backup)
            rollbacks.append(backup)
            back_log.info(f'восстановлен файл конфигурации: {os.path.basename(latest_backup)} → {filename}')
            print(f"[⮌] Конфиг {filename} восстановлен из бэкапа {os.path.basename(latest_backup)}")
        except Exception as e:
            back_log.error('')
            print(f"[ERROR] Ошибка при восстановлении из бэкапа: {e}")

    return rollbacks

