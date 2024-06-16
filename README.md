# ExcelScanner

### Venv setup
Para crear un virtual environment se puede usar Pycharm que automaticamente genera una. La otra forma de hacerlo es usando directamente usando el paquete venv por medio de el comando:
```
python -m venv venv
```
Luego usando el comando en Windows:
```
.venv/Scripts/Activate
```
O en Linux:
```
source /.venv/bin/activate
```
Para luego instalar los paquetes necesarios.

### Instalar paquetes
pip install -r requirements.txt

### Instalar soporte CUDA:
Si se tiene una tarjeta NVidia se puede activar el soporte para CUDA con la siguiente instruccion:
```
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
```
