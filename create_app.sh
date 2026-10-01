#!/bin/bash

# Directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Call Recorder.app"
DEST_PATH="$SCRIPT_DIR/$APP_NAME"

echo "🔨 Creando lanzador nativo '$APP_NAME'..."

# Compilar la aplicación usando osacompile nativo de macOS
osacompile -o "$DEST_PATH" -e "do shell script \"'$SCRIPT_DIR/run.sh' > /dev/null 2>&1 &\""

if [ $? -eq 0 ]; then
    # Ocultar del Dock para que corra como app de barra de menú pura
    plutil -replace LSUIElement -bool true "$DEST_PATH/Contents/Info.plist" 2>/dev/null || true
    echo "✅ ¡Lanzador creado con éxito!"
    echo "📍 Ubicación: $DEST_PATH"
    echo ""
    echo "Puedes:"
    echo "  1. Hacer doble clic sobre '$APP_NAME' desde Finder para abrirla."
    echo "  2. Mover '$APP_NAME' a tu carpeta '/Applications' para abrirla con Spotlight (Cmd + Espacio)."
    echo "  3. Anclarla al Dock si deseas."
else
    echo "❌ Error al crear el lanzador."
    exit 1
fi
