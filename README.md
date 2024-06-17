# Dependencias a serem instaladas

pip install psutil
pip install tk


# Compilação dos Scripts em Executáveis

Para compilar cada script em um executável usando PyInstaller, você pode seguir os passos abaixo:
Instale o PyInstaller (se ainda não tiver instalado):

pip install pyinstaller


Compile cada script:

pyinstaller --onefile cleanup_alert.py
pyinstaller --onefile cleanup_deletion.py

