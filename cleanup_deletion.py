import os
import sys
import time
import shutil
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Determinar o diretório atual do script, levando em conta a execução como executável
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho para o arquivo de log na pasta logs
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
temp_log_file_path = os.path.join(log_dir, "temp_cleanup.log")
debug_log_path = os.path.join(log_dir, "debug_log.txt")

# Função para registrar depuração em um arquivo de texto
def log_debug_info(message):
    with open(debug_log_path, 'a') as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} DEBUG: {message}\n")

# Função para exibir janela de progresso
def perform_deletion_window():
    root = tk.Tk()
    root.title("Progresso de Exclusão")
    root.geometry("400x200")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)

    label = tk.Label(root, text="Apagando arquivos...", wraplength=350, justify="center")
    label.pack(pady=20)

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    progress_label = tk.Label(root, text="")
    progress_label.pack(pady=5)

    root.update()
    perform_deletion_with_progress(progress, progress_label, root)

# Função para apagar arquivos e pastas listados no log temporário com barra de progresso
def perform_deletion_with_progress(progress_bar, progress_label, root):
    log_debug_info("Iniciando a exclusão com progresso")
    if os.path.exists(temp_log_file_path):
        with open(temp_log_file_path, 'r') as file:
            lines = file.readlines()
        
        total_items = len(lines)
        progress_bar["maximum"] = total_items

        for i, line in enumerate(lines):
            item_path = line.strip()
            if os.path.exists(item_path):
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        log_deletion(f"Deleted file: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        log_deletion(f"Deleted directory: {item_path}")
                except Exception as e:
                    log_error(f"Failed to delete {item_path}. Error: {e}")
            else:
                log_error(f"Path does not exist: {item_path}")
            
            progress_bar["value"] = i + 1
            progress_label.config(text=f"Apagando: {item_path}")
            root.update()
            time.sleep(0.1)  # Pequena pausa para visualização do progresso

        # Após a exclusão inicial, verificar e excluir pastas vazias
        delete_empty_directories()

        # Fechar a janela após a conclusão
        root.after(1000, root.destroy)
    else:
        log_error("Temporary log file not found.")

# Função para excluir diretórios vazios
def delete_empty_directories():
    log_debug_info("Iniciando exclusão de diretórios vazios")
    for root_dir, dirs, files in os.walk(script_dir, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root_dir, dir)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    log_deletion(f"Deleted empty directory: {dir_path}")
            except Exception as e:
                log_error(f"Failed to delete empty directory {dir_path}. Error: {e}")

# Função para registrar logs de exclusão
def log_deletion(message):
    with open(temp_log_file_path, 'a') as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} DELETION: {message}\n")

# Função para registrar erros
def log_error(message):
    with open(temp_log_file_path, 'a') as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} ERROR: {message}\n")

# Executar limpeza
if __name__ == "__main__":
    log_debug_info("Script de exclusão iniciado")
    perform_deletion_window()
