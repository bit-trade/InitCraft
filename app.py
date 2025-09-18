import os
import sys
from logging import getLogger
from constant import LogSet, utility_name
from utils.menu_print import Interactive
from utils.tui_mode import interactive
from utils.cli_mode import arg_settings, run_cli


main_log = getLogger(os.path.basename(__file__).removesuffix('.py'))
main_log.setLevel(LogSet['level'])
if not main_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    main_log.addHandler(handler)


def run_is_not_in_terminal():
    print(f'[WARNING] Для отображения меню, {utility_name} необходимо запускать в терминале')
    Interactive.about_settings()


if __name__ == '__main__':
    if os.geteuid() != 0:
        print(f'[ERROR] {utility_name} стартовал не от root')
        main_log.error(f'{utility_name} должен запускаться от привилегированного пользователя - \"root\"')
        sys.exit(1)

    main_log.info(f'{utility_name}: старт')
    if not sys.stdin.isatty():
        run_is_not_in_terminal()

    else:
        args = arg_settings()
        args_list = any([_ for _ in vars(args).values()])
        if args_list:
            run_cli(args)
        else:
            interactive()
