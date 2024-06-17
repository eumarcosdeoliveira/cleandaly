import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

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
# Caminho para o arquivo de log de depuração
debug_log_path = os.path.join(logs_dir, "debug_log.txt")

# Função para registrar depuração em um arquivo de texto
def log_debug_info(message):
    with open(debug_log_path, 'a') as log_file:
        log_file.write(message + '\n')

log_debug_info("Script iniciado")

# Função para salvar as configurações em um arquivo JSON
def save_config(config):
    try:
        with open(config_file_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        messagebox.showinfo("Configuração Salva", "As configurações foram salvas com sucesso.")
        log_debug_info("Configurações salvas com sucesso")
        start_cleanup_service()
        root.destroy()  # Fechar a janela após salvar
    except Exception as e:
        log_debug_info(f"Erro ao salvar configurações: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")

# Função para carregar as configurações do arquivo JSON
def load_config():
    try:
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r') as config_file:
                log_debug_info("Configurações carregadas com sucesso")
                return json.load(config_file)
        log_debug_info("Arquivo de configuração não encontrado, carregando configuração padrão")
        return {"days": 0, "directories": []}
    except Exception as e:
        log_debug_info(f"Erro ao carregar configurações: {e}")
        messagebox.showerror("Erro", f"Erro ao carregar configurações: {e}")
        return {"days": 0, "directories": []}

# Função para adicionar um diretório à lista de configurações
def add_directory():
    directory = filedialog.askdirectory()
    if not directory:
        messagebox.showwarning("Entrada Inválida", "Por favor, selecione um diretório.")
        return
    if directory not in config["directories"]:
        config["directories"].append(directory)
        update_listbox()
        log_debug_info(f"Diretório adicionado: {directory}")

# Função para remover o diretório selecionado da lista de configurações
def remove_directory():
    selected_index = listbox.curselection()
    if selected_index:
        directory = config["directories"][selected_index[0]]
        del config["directories"][selected_index[0]]
        update_listbox()
        log_debug_info(f"Diretório removido: {directory}")

# Função para atualizar a listbox com as configurações
def update_listbox():
    listbox.delete(0, tk.END)
    for item in config["directories"]:
        listbox.insert(tk.END, item)

# Função para validar e salvar as configurações
def save_settings():
    days = days_entry.get()
    if not config["directories"] or not days:
        messagebox.showwarning("Entrada Inválida", "Por favor, adicione pelo menos um diretório e insira um número válido de dias.")
        log_debug_info("Tentativa de salvar com entrada inválida")
        return
    try:
        days = int(days)
        if days < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Entrada Inválida", "Por favor, insira um número válido de dias.")
        log_debug_info("Entrada inválida de dias")
        return
    
    config["days"] = days
    save_config(config)

# Função para iniciar o serviço de limpeza
def start_cleanup_service():
    service_file_path_py = os.path.join(script_dir, "cleanup_service.py")
    service_file_path_exe = os.path.join(script_dir, "cleanup_service.exe")
    
    # Verificar o diretório atual e listar arquivos para depuração
    log_debug_info(f"Diretório atual do script: {script_dir}")
    log_debug_info("Arquivos no diretório atual:")
    log_debug_info("\n".join(os.listdir(script_dir)))
    
    try:
        if os.path.exists(service_file_path_py):
            log_debug_info(f"Iniciando {service_file_path_py}")
            subprocess.Popen(["python", service_file_path_py], cwd=script_dir)
        elif os.path.exists(service_file_path_exe):
            log_debug_info(f"Iniciando {service_file_path_exe}")
            subprocess.Popen([service_file_path_exe], cwd=script_dir)
        else:
            log_debug_info("Arquivo cleanup_service.py ou cleanup_service.exe não encontrado.")
            messagebox.showerror("Erro", "Arquivo cleanup_service.py ou cleanup_service.exe não encontrado.")
    except Exception as e:
        log_debug_info(f"Falha ao iniciar o serviço de limpeza: {e}")
        messagebox.showerror("Erro", f"Falha ao iniciar o serviço de limpeza: {e}")

# Carregar a configuração inicial
config = load_config()

# Configuração da interface gráfica
root = tk.Tk()
root.title("Configuração de Limpeza")
root.geometry("400x450")
root.eval('tk::PlaceWindow . center')
root.attributes('-topmost', True)

tk.Label(root, text="Insira a Quantidade de Dias:").pack(pady=10)
days_entry = tk.Entry(root, width=10)
days_entry.pack(pady=5)
days_entry.insert(0, str(config.get("days", 0)))

tk.Button(root, text="Adicionar Diretório", command=add_directory).pack(pady=5)

tk.Label(root, text="Diretórios Configurados:").pack(pady=10)
listbox = tk.Listbox(root, width=50, height=10)
listbox.pack(pady=5)

tk.Button(root, text="Remover Diretório Selecionado", command=remove_directory).pack(pady=5)

tk.Button(root, text="Salvar Configurações", command=save_settings).pack(pady=20)

# Atualizar a listbox com a configuração inicial
update_listbox()

root.mainloop()
