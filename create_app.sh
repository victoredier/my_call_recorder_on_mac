#!/bin/bash

# Directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Call Recorder.app"
DEST_PATH="$SCRIPT_DIR/$APP_NAME"
CONTENTS_DIR="$DEST_PATH/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

echo "🔨 Creando bundle nativo de macOS para '$APP_NAME'..."

# Ensure virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "⚙️  Creando entorno virtual..."
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Error: no se encontró python en $PYTHON_BIN"
    exit 1
fi

# Extract Python compilation and link flags from venv
PY_INCDIR=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY') or '')")
PY_LIBDIR=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR') or '')")
PY_LDVERSION=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('LDVERSION') or '3.10')")

if [ -z "$PY_INCDIR" ] || [ ! -d "$PY_INCDIR" ]; then
    echo "❌ Error: no se encontraron cabeceras de Python en $PY_INCDIR"
    exit 1
fi

# Clean previous build
rm -rf "$DEST_PATH"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# 1. Create Info.plist with explicit Microphone usage description and Menu Bar settings
cat << 'EOF' > "$CONTENTS_DIR/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Call Recorder</string>
    <key>CFBundleIdentifier</key>
    <string>com.victoredier.callrecorder</string>
    <key>CFBundleName</key>
    <string>Call Recorder</string>
    <key>CFBundleDisplayName</key>
    <string>Call Recorder</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>Call Recorder necesita acceso al micrófono para grabar las llamadas y reuniones.</string>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
EOF

# Copy AppIcon.icns and assets to Resources
if [ -f "$SCRIPT_DIR/assets/AppIcon.icns" ]; then
    cp "$SCRIPT_DIR/assets/AppIcon.icns" "$RESOURCES_DIR/AppIcon.icns"
fi
if [ -d "$SCRIPT_DIR/assets" ]; then
    cp -r "$SCRIPT_DIR/assets" "$RESOURCES_DIR/"
fi

# 2. Compile native launcher executable
echo "⚙️  Compilando lanzador nativo..."
clang -O2 -Wall \
  -I"$PY_INCDIR" \
  -L"$PY_LIBDIR" \
  -lpython"$PY_LDVERSION" \
  -framework CoreFoundation \
  -DDEFAULT_PROJECT_DIR="\"$SCRIPT_DIR\"" \
  -o "$MACOS_DIR/Call Recorder" \
  "$SCRIPT_DIR/launcher.c"

if [ $? -ne 0 ]; then
    echo "❌ Error compilando el lanzador nativo con clang."
    exit 1
fi

chmod +x "$MACOS_DIR/Call Recorder"

# 3. Ad-hoc code sign the application bundle so macOS TCC remembers permissions
echo "🔏 Firmando la aplicación con codesign..."
codesign --force --deep --sign - "$DEST_PATH" 2>/dev/null || true

# 4. Reset previous TCC cache if any so macOS requests permission cleanly
tccutil reset Microphone com.victoredier.callrecorder 2>/dev/null || true

echo ""
echo "✅ ¡Lanzador nativo creado con éxito!"
echo "📍 Ubicación: $DEST_PATH"
echo ""
echo "🎙️  Al abrir la aplicación por primera vez, macOS mostrará la ventana:"
echo "   'Call Recorder quisiera acceder al micrófono' -> Haz clic en [Permitir]."
echo "   Aparecerá en Ajustes del Sistema > Privacidad y Seguridad > Micrófono."
echo ""
echo "💡 Puedes:"
echo "   1. Hacer doble clic sobre '$APP_NAME' desde Finder para abrirla."
echo "   2. Mover '$APP_NAME' a tu carpeta '/Applications' para abrirla con Spotlight (Cmd + Espacio)."
