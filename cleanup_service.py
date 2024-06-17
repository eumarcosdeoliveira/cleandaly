import os
import sys
import json
import time
import subprocess
import psutil
from datetime import datetime, timedelta

# Determinar o diretório atual do script, levando em conta a execução como executável
if getattr(sys, 'frozen', False):
    # Caso o script esteja empacotado como um executável
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho para a pasta de logs
logs_dir = os.path.join(script_dir, "logs")
# Criar a pasta de logs se não existir
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Caminho para o arquivo de configuração JSON
config_file_path = os.path.join(logs_dir, "cleanup_config.json")
# Caminho para o arquivo de log temporário
temp_log_file_path = os.path.join(logs_dir, "temp_cleanup.log")
# Caminho para o arquivo de log de depuração
debug_log_path = os.path.join(logs_dir, "debug_log.txt")

# Função para registrar depuração em um arquivo de texto
def log_debug_info(message):
    with open(debug_log_path, 'a') as log_file:
        log_file.write(message + '\n')

log_debug_info("Script iniciado")

# Função para carregar a configuração
def load_config():
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        log_debug_info("Configurações carregadas com sucesso")
        return config
    else:
        log_debug_info("Arquivo de configuração não encontrado")
        return None

# Função para verificar se um arquivo ou pasta é antigo
def is_old(item_path, days):
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    item_stat = os.stat(item_path)
    creation_time = datetime.fromtimestamp(item_stat.st_ctime)
    modification_time = datetime.fromtimestamp(item_stat.st_mtime)
    return creation_time < cutoff or modification_time < cutoff

# Função para verificar se o script de alerta já está em execução
def is_alert_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] in ('python.exe', 'pythonw.exe', 'cleanup_alert.exe', 'cleanup_deletion.exe'):
            for cmdline in proc.info['cmdline']:
                if any(script in cmdline for script in ['cleanup_alert.py', 'cleanup_alert.exe', 'cleanup_deletion.py', 'cleanup_deletion.exe']):
                    return True
    return False

# Função para iniciar o script de alerta
def start_cleanup_alert():
    if is_alert_running():
        log_debug_info("Script de alerta já está em execução")
        return
    alert_file_path_py = os.path.join(script_dir, "cleanup_alert.py")
    alert_file_path_exe = os.path.join(script_dir, "cleanup_alert.exe")
    try:
        if os.path.exists(alert_file_path_py):
            log_debug_info(f"Iniciando {alert_file_path_py}")
            subprocess.Popen(["python", alert_file_path_py])
        elif os.path.exists(alert_file_path_exe):
            log_debug_info(f"Iniciando {alert_file_path_exe}")
            subprocess.Popen([alert_file_path_exe])
        else:
            log_debug_info("Arquivo cleanup_alert.py ou cleanup_alert.exe não encontrado.")
            print("Arquivo cleanup_alert.py ou cleanup_alert.exe não encontrado.")
    except Exception as e:
        log_debug_info(f"Falha ao iniciar o script de alerta: {e}")
        print(f"Falha ao iniciar o script de alerta: {e}")

# Função para registrar arquivos e pastas antigos no log
def log_old_items(directory, days):
    old_items_found = False
    files_list = []
    dirs_list = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            item_path = os.path.join(root, name)
            if is_old(item_path, days):
                files_list.append(item_path)
                old_items_found = True
        for name in dirs:
            item_path = os.path.join(root, name)
            if is_old(item_path, days):
                dirs_list.append(item_path)
                old_items_found = True

    with open(temp_log_file_path, 'a') as log_file:
        for item_path in files_list:
            log_file.write(f"{item_path}\n")
        for item_path in dirs_list:
            log_file.write(f"{item_path}\n")
    
    log_debug_info(f"Arquivos antigos registrados no diretório {directory}")
    return old_items_found

# Loop principal
def main_loop():
    while True:
        config = load_config()
        if config:
            days = config.get("days")
            directories = config.get("directories", [])
            old_items_found = False
            with open(temp_log_file_path, 'w') as log_file:
                for directory in directories:
                    if log_old_items(directory, days):
                        old_items_found = True
            if old_items_found:
                start_cleanup_alert()
        else:
            log_debug_info("Nenhuma configuração encontrada")
        time.sleep(30)

if __name__ == "__main__":
    main_loop()
