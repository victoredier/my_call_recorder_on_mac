#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Check if the virtual environment exists, if not create it automatically
if [ ! -d "venv" ]; then
    echo "⚙️  No se encontró entorno virtual. Creando venv en $SCRIPT_DIR/venv..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo crear el entorno virtual. Verifica que tengas Python 3 instalado."
        exit 1
    fi
    echo "📦 Instalando dependencias desde requirements.txt..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando dependencias. Revisa los errores anteriores."
        exit 1
    fi
    echo "✅ Entorno virtual y dependencias listas."
else
    # Activate existing virtual environment
    source venv/bin/activate
    # Check if rumps is installed, if not install requirements
    if ! python3 -c "import rumps" &>/dev/null; then
        echo "📦 Instalando dependencias faltantes en el entorno virtual..."
        pip install -r requirements.txt
    fi
fi

# Run the application using the virtual environment's python
exec python3 main.py
