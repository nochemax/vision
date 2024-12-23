README.txt

# Vision Project Setup Guide

This document provides instructions for setting up the development environment for the Vision project. Follow these steps to ensure all necessary dependencies are installed and configured correctly.

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:

- Python 3.x
- pip (Python package manager)
- Git

## System Dependencies

The project requires several system-level dependencies. Install them using the following commands:

```bash
sudo apt update
sudo apt install -y ffmpeg libatlas-base-dev build-essential portaudio19-dev libsndfile1 python3-opencv libpulse-dev alsa-utils git
```

### Additional System Dependencies

Ensure the following system dependencies are installed:

- `libasound2-dev`: For ALSA sound library.
- `libffi-dev`: For Foreign Function Interface library.
- `libssl-dev`: For SSL/TLS support.

Install any missing system dependencies using apt:

```bash
sudo apt install -y libasound2-dev libffi-dev libssl-dev
```

## Python Libraries

The project uses several Python libraries. Install them using pip:

```bash
pip install -r requirements.txt
```

If you encounter any issues with package conflicts, use the following command:

```bash
pip install --use-deprecated=legacy-resolver -r requirements.txt --user
```

### Additional Libraries

Ensure the following Python libraries are installed:

- `pytz`: For timezone calculations.
- `gtts`: For text-to-speech conversion.
- `pyaudio`: For audio processing.
- `opencv-python`: For image processing.
- `numpy`: For numerical operations.
- `librosa`: For audio analysis.
- `dlib`: For facial recognition.
- `tensorflow`: For machine learning models.
- `requests`: For HTTP requests.
- `Pillow`: For image handling.
- `playsound`: For playing sound files.
- `sqlite3`: For database operations (built-in with Python).

Install any missing libraries using pip:

```bash
pip install pytz gtts pyaudio opencv-python numpy librosa dlib tensorflow requests Pillow playsound
```

## Database Setup

The project uses SQLite databases. Ensure the following databases are initialized:

- `Usuarios/base_de_datos_usuario/usuarios_general.db`
- `/root/.usuario_root_datos/base_de_datos_usuario/root.db`
- `/root/.usuario_root_datos/base_de_datos_usuario/root_calendario.db`
- `/root/.usuario_root_datos/base_de_datos_usuario/Ines_calendario.db`

Run the `crear_tablas_predefinidas()` function in the code to create the necessary tables.

## Running the Project

To run the project, execute the main script:

```bash
python vision_contrucion_ultimo_1.py
```

## Additional Notes

- Ensure your system's Python version is compatible (Python 3.x).
- If you encounter permission issues, consider running commands with `sudo`.
- For any issues related to audio, ensure your microphone and speakers are configured correctly.

## Contact

For further assistance, please contact the project maintainer.