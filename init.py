import os
import sys
import psutil
import subprocess

# Obter o diretório atual do script
if getattr(sys, 'frozen', False):
    # Caso o script esteja empacotado como um executável
    script_dir = os.path.dirname(sys.executable)
else:
    # Caso o script esteja sendo executado diretamente
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Nome dos arquivos de serviço e configuração
cleanup_config_name_exe = "cleanup_config.exe"
cleanup_config_name_py = "cleanup_config.py"
setup_script_name_exe = "setup_cleanup_service.exe"
setup_script_name_py = "setup_cleanup_service.py"

# Caminho completo para os arquivos
cleanup_config_path_exe = os.path.join(script_dir, cleanup_config_name_exe)
cleanup_config_path_py = os.path.join(script_dir, cleanup_config_name_py)
setup_script_path_exe = os.path.join(script_dir, setup_script_name_exe)
setup_script_path_py = os.path.join(script_dir, setup_script_name_py)

# Função para verificar se um processo está em execução
def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            return True
    return False

# Verificar e executar cleanup_config se não estiver em execução
if not is_process_running(cleanup_config_name_exe) and not is_process_running(cleanup_config_name_py):
    if os.path.exists(cleanup_config_path_exe):
        subprocess.Popen(cleanup_config_path_exe)
    elif os.path.exists(cleanup_config_path_py):
        subprocess.Popen([sys.executable, cleanup_config_path_py])
    else:
        print(f"Erro: Nenhum arquivo {cleanup_config_name_exe} ou {cleanup_config_name_py} encontrado.")
        sys.exit(1)

# Verificar e executar setup_cleanup_service se não estiver em execução
if not is_process_running(setup_script_name_exe) and not is_process_running(setup_script_name_py):
    if os.path.exists(setup_script_path_exe):
        subprocess.Popen(setup_script_path_exe)
    elif os.path.exists(setup_script_path_py):
        subprocess.Popen([sys.executable, setup_script_path_py])
    else:
        print(f"Erro: Nenhum arquivo {setup_script_name_exe} ou {setup_script_name_py} encontrado.")
        sys.exit(1)

print("Script concluído.")
