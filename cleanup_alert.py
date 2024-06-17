import os
import sys
import time
import subprocess
import tkinter as tk
from tkinter import ttk

# Determinar o diretório atual do script, levando em conta a execução como executável
if getattr(sys, 'frozen', False):
    # Caso o script esteja empacotado como um executável
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho para o arquivo de log de depuração
logs_dir = os.path.join(script_dir, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
debug_log_path = os.path.join(logs_dir, "debug_log.txt")

# Função para registrar depuração em um arquivo de texto
def log_debug_info(message):
    with open(debug_log_path, 'a') as log_file:
        log_file.write(message + '\n')

# Caminho do script de exclusão
cleanup_deletion_script = os.path.join(script_dir, "cleanup_deletion")

delay_minutes = 0  # Tempo de adiamento em minutos
max_delays = 2
delay_count = 0
remaining_time = None

log_debug_info("Script iniciado")

# Função para exibir mensagem de alerta com botões personalizados
def show_alert(message, show_buttons=True, countdown_time=None):
    global delay_count, action, remaining_time
    action = None

    def on_apagar():
        global action
        action = "Apagar"
        root.destroy()

    def on_adiar():
        global action
        action = "Adiar"
        root.destroy()

    def on_close():
        root.destroy()
        perform_cleanup()  # Reabrir a janela imediatamente se for fechada

    def countdown_timer(label, seconds):
        global remaining_time
        remaining_time = seconds
        while remaining_time > 0:
            mins, secs = divmod(remaining_time, 60)
            timer = f'{mins:02d}:{secs:02d}'
            label.config(text=f"{message}\n\nTempo restante: {timer}")
            root.update()
            time.sleep(1)
            remaining_time -= 1
        root.destroy()
        call_cleanup_deletion_script()

    root = tk.Tk()
    root.title("AVISO")
    root.geometry("400x200")
    root.eval('tk::PlaceWindow . center')
    root.attributes('-topmost', True)
    root.protocol("WM_DELETE_WINDOW", on_close)  # Desabilitar botão de fechar

    label = tk.Label(root, text=message, wraplength=350, justify="center")
    label.pack(pady=20)

    if show_buttons:
        frame = tk.Frame(root)
        frame.pack(pady=10)
        
        btn_adiar = tk.Button(frame, text="Adiar", command=on_adiar, width=10)
        btn_adiar.pack(side="left", padx=10)
        
        btn_apagar = tk.Button(frame, text="Apagar", command=on_apagar, width=10)
        btn_apagar.pack(side="right", padx=10)
    else:
        countdown_timer(label, countdown_time if countdown_time is not None else remaining_time)

    root.mainloop()
    return action

# Função para chamar o script de exclusão
def call_cleanup_deletion_script():
    log_debug_info("Chamando o script de exclusão")
    # Verificar se cleanup_deletion.py ou cleanup_deletion.exe existe
    py_script = f"{cleanup_deletion_script}.py"
    exe_script = f"{cleanup_deletion_script}.exe"
    
    if os.path.isfile(py_script):
        log_debug_info(f"Iniciando {py_script}")
        subprocess.Popen(["python", py_script])
    elif os.path.isfile(exe_script):
        log_debug_info(f"Iniciando {exe_script}")
        subprocess.Popen([exe_script])
    else:
        log_debug_info("Nenhum script de exclusão encontrado.")
        print("Nenhum script de exclusão encontrado.")

# Função para executar a limpeza
def perform_cleanup():
    global delay_count, remaining_time

    if delay_count < max_delays:
        message = "AVISO: Todos os arquivos e pastas com mais de 24h serão apagados, realize o backup em seu diretório na nuvem dos arquivos que deseja salvar."
        action = show_alert(message)
        if action == "Apagar":
            delay_count = 0  # Resetar contagem de adiamento se o usuário escolher apagar
            call_cleanup_deletion_script()
        elif action == "Adiar":
            delay_count += 1
            time.sleep(delay_minutes * 60)
            perform_cleanup()
    else:
        message = "AVISO: Todos os arquivos e pastas com mais de 24h serão apagados em 5 minutos, realize o backup em seu diretório na nuvem dos arquivos que deseja salvar."
        if remaining_time is None:
            remaining_time = 5 * 60  # 5 minutos de contagem regressiva
        show_alert(message, show_buttons=False, countdown_time=remaining_time)

# Executar limpeza
if __name__ == "__main__":
    perform_cleanup()
