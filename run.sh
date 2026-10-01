#!/bin/bash

# Background execution support
if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
    nohup "$0" > /dev/null 2>&1 &
    echo "🚀 Call Recorder iniciado en segundo plano."
    exit 0
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Check if Call Recorder is already running
RUNNING_PID=$(pgrep -f "$SCRIPT_DIR/main.py" | head -n 1)
if [ -n "$RUNNING_PID" ]; then
    echo "⚠️  Call Recorder ya está ejecutándose (PID: $RUNNING_PID)."
    osascript -e 'display notification "Call Recorder ya está activo en la barra de menú." with title "Call Recorder"' 2>/dev/null
    exit 0
fi

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
exec "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/main.py"
