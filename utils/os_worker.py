import os
import logging
import subprocess
from constant import LogSet


osworker_log = logging.getLogger(os.path.basename(__file__).removesuffix('.py'))
osworker_log.setLevel(LogSet['level'])
if not osworker_log.handlers:
    handler = LogSet['handler']
    handler.setFormatter(LogSet['formatter'])
    osworker_log.addHandler(handler)


class OSWorker:
    def restart_service(self, service: str) -> bool:
        if not service:
            return True
        try:
            subprocess.run(["systemctl", "restart", service], check=True)
            subprocess.run(["systemctl", "is-active", "--quiet", service], check=True)
            print(f"[✓] Служба {service} успешно перезапущена")
            return True
        except subprocess.CalledProcessError:
            print(f"[✗] Ошибка при перезапуске службы: {service}")
            return False

    def os_reboot(self):
        print('[INFO] Система уходит в перезагрузку')
        osworker_log.info('будет выполнена перезагрузка системы')
        logging.shutdown()
        subprocess.Popen(['systemctl', 'reboot'])
