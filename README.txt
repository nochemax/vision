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

## Python Libraries

The project uses several Python libraries. Install them using pip:

```bash
pip install -r requirements.txt
```

If you encounter any issues with package conflicts, use the following command:

```bash
pip install --use-deprecated=legacy-resolver -r requirements.txt --user
```

## AI Agent Setup

The project includes an AI agent named Inés. Ensure Inés has access to all functions and can operate independently. Follow these steps:

1. Run the `instalar_paquetes()` function to install necessary packages and resolve any conflicts.
2. Execute the `verificar_registro_root()` function to ensure root registration is complete.
3. Initialize the databases by running the `crear_tablas_predefinidas()` function.

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

## Troubleshooting

- Ensure your system's Python version is compatible (Python 3.x).
- If you encounter permission issues, consider running commands with `sudo`.
- For any issues related to audio, ensure your microphone and speakers are configured correctly.
- If Inés does not respond as expected, verify that all functions are accessible and that the AI agent is properly initialized.

## Contact

For further assistance, please contact the project maintainer.