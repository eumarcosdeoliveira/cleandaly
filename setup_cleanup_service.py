import os
import sys
from datetime import datetime

# Determinar o diretório atual do script, levando em conta a execução como executável
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Definir o nome do arquivo de serviço de limpeza
service_name = "cleanup_service"
service_extension = ".exe" if getattr(sys, 'frozen', False) else ".py"
cleanup_service_name = service_name + service_extension

# Caminho completo para o cleanup_service
cleanup_service_path = os.path.join(script_dir, cleanup_service_name)

# Caminho para a pasta de inicialização do Windows
startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

# Caminho para o arquivo .bat na pasta de inicialização
bat_startup_path = os.path.join(startup_folder, "Cleanupinit.bat")

# Conteúdo do arquivo Cleanupinit.bat
if service_extension == ".exe":
    bat_content = f"""@echo off
cd /d {script_dir}
start /min {cleanup_service_path}"""
else:
    bat_content = f"""@echo off
cd /d {script_dir}
start /min pythonw {cleanup_service_path}"""

# Criar o arquivo .bat diretamente na pasta de inicialização com o conteúdo especificado
try:
    with open(bat_startup_path, 'w') as bat_file:
        bat_file.write(bat_content)
    print(f"Arquivo .bat criado em {bat_startup_path}")
except Exception as e:
    print(f"Erro ao criar o arquivo .bat: {e}")

# Função para registrar depuração em um arquivo de texto
def log_debug_info(message):
    debug_log_path = os.path.join(script_dir, "debug_log.txt")
    with open(debug_log_path, 'a') as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} DEBUG: {message}\n")

# Log da criação do arquivo .bat
log_debug_info(f"Arquivo .bat criado em {bat_startup_path} com conteúdo: {bat_content}")

print("Script concluído.")
