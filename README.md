# Call Recorder & Transcriber para macOS 🎙️✨

Aplicación de barra de menú para macOS que graba llamadas y reuniones con audio de alta fidelidad, las organiza en subcarpetas individuales, y cuenta con un **Dashboard interactivo** para reproducir, transcribir con Google Gemini (diarización de interlocutores y timestamps) y editar nombres y textos.

---

## 🚀 Características

- **Menú en la Barra de Tareas (Menu Bar):**
  - Iniciar, Pausar, Reanudar y Detener grabación.
  - Al detener la llamada, solicita el nombre de la reunión mediante un diálogo nativo de macOS.
  - Acceso directo a **"Abrir Dashboard de Llamadas..."** y **"Abrir Carpeta en Finder"**.

- **Almacenamiento Organizado en Subcarpetas:**
  - Las llamadas se guardan por defecto en `~/Recordings/` (o la ruta configurada en `CALL_RECORDINGS_PATH`).
  - Cada llamada se almacena en su propia subcarpeta:
    ```
    ~/Recordings/
      └── 2026-09-21_10-50-00_Reunion_de_Equipo/
            ├── audio.wav        # Audio grabado
            ├── metadata.json    # Duración, fecha, nombre, estado
            └── transcript.json  # Transcripción con timestamps y speakers
    ```

- **Dashboard Web Local (`http://localhost:5050`):**
  - **Lista de llamadas:** Con buscador, fecha, duración y estado (`Grabado`, `Transcribiendo`, `Transcrito`).
  - **Reproductor de Audio:** Con scrubber interactivo, velocidades de reproducción (`1.0x`, `1.25x`, `1.5x`, `2.0x`) y soporte para saltar instantáneamente a cualquier momento.
  - **Transcripción con Gemini:**
    - Botón **"✨ Transcribir con Gemini"**.
    - Diarización automática de interlocutores (`Speaker 1`, `Speaker 2`, etc.).
    - Marcas de tiempo de inicio y fin para cada intervención.
    - Soporte para modelos como `gemini-2.5-flash`, `gemini-1.5-flash` o `gemini-2.5-pro`.
  - **Edición y Asignación de Nombres a Speakers:**
    - Asigna nombres reales a cada participante (ej. `Speaker 1` ➔ `Víctor`, `Speaker 2` ➔ `Cliente`) y aplícalos con un clic a todos los segmentos.
    - Edita libremente los textos transcritos.
    - Haz clic en cualquier timestamp `[00:15 - 00:30]` para saltar la reproducción del audio a ese segundo.
    - Añadir o eliminar segmentos manualmente.
  - **Exportación:**
    - Descarga el archivo `transcript.json`.
    - Copia el texto formateado al portapapeles.
  - **Ajustes de Gemini:**
    - Configura tu clave de API de Gemini (`GEMINI_API_KEY`) directamente desde la interfaz web o mediante variable de entorno.

---

## 🛠️ Instalación y Uso

### 1. Activar entorno virtual e instalar dependencias
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar la clave de Gemini (Opcional)
Puedes configurarla en tu entorno:
```bash
export GEMINI_API_KEY="AIzaSy..."
```
O bien ingresarla directamente en la ventana de **Ajustes** del Dashboard web.

### 3. Ejecutar la aplicación
```bash
./run.sh
# O directamente:
python3 main.py
```
Aparecerá el icono `🎙️` en la barra de menú superior de tu Mac.
