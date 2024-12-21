import subprocess
import sys
import os
import pytz
from datetime import datetime
import platform
import gtts
import threading
import cv2  # OpenCV for camera control
import numpy as np  # For numerical operations
import librosa  # For audio processing
import pyaudio  # For handling audio input/output
import wave  # For handling audio files
import sqlite3  # For database operations
import random  # For random choices in simulations
import requests  # For downloading images from the web
import io  # For handling byte streams
from PIL import Image  # For image processing
import webbrowser  # For opening web pages
import time  # For handling time-related tasks
import hashlib  # For hashing operations
import tkinter as tk  # For GUI elements
from tkinter import Scale  # For creating scale widgets



# Las Funciones con 3 lineas solo se ejecutan una vez 
# Las Funciones unciones de dos lineas solo se ejecutan una vez si no existen falllos si es asi se repetira de nuevo y no mas 
# Las Funciones sean todas iguales y del hambito global del pograma ines 
# Las Funciones globales 4 fanga de igual

# --- Instalación de la paquetería ---
def instalar_paquetes():
    """
    Función para instalar paquetes necesarios y eliminar conflictos de pip3.
    Verifica la versión de Python y realiza la instalación con resolución de conflictos.
    """
    try:
        python_version = subprocess.check_output(["python3", "--version"]).decode("utf-8").strip()
        print(f"Versión de Python instalada: {python_version}")
    except subprocess.CalledProcessError:
        print("Error al obtener la versión de Python. Asegúrate de que Python 3 está instalado.")
        return

    if python_version.startswith("Python 3"):
        print("Versión de Python compatible, continuando con la instalación de paquetes.")
    else:
        print("Versión de Python incompatible. Por favor, instala Python 3.")
        return

    print("Instalando dependencias del sistema necesarias...")
    subprocess.run(["sudo", "apt", "update", "-y"], check=True)
    subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg", "libatlas-base-dev", "build-essential", "portaudio19-dev", "libsndfile1", "python3-opencv", "libpulse-dev", "alsa-utils", "git"], check=True)

    try:
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
        print("pip3 está instalado y actualizado correctamente.")
    except subprocess.CalledProcessError:
        print("Error con pip3. Procediendo con la instalación...")
        subprocess.run([sys.executable, "-m", "ensurepip", "--default-pip"], check=True)

    print("Instalando paquetes pip3 desde requirements.txt con resolución de conflictos...")
    subprocess.run(["pip3", "install", "--use-deprecated=legacy-resolver", "-r", "requirements.txt", "--user"], check=True)
    subprocess.run(["pip3", "install", "-r", "requirements.txt", "--break-system-packages"], check=True)
    
    print("Instalación completada.")
  
    try:
        with open('requirements.txt', 'r') as file:
            requirements = file.readlines()

        requirements = [req.strip() for req in requirements if req.strip()]
        unique_requirements = list(set(requirements))
        unique_requirements.sort()

        with open('cleaned_requirements.txt', 'w') as file:
            file.write("\n".join(unique_requirements))
        
        print("Archivo requirements.txt procesado y guardado como cleaned_requirements.txt.")
    except Exception as e:
        print(f"Error procesando el archivo requirements.txt: {e}")
        return

    apt_packages = [
        "ffmpeg", "libatlas-base-dev", "build-essential", "portaudio19-dev",
        "libsndfile1", "python3-opencv", "libpulse-dev", "alsa-utils", "git"
    ]

    print("Instalando paquetes de sistema necesarios...")
    os.system(f"sudo apt update && sudo apt install -y {' '.join(apt_packages)}")
    
    print("Instalación de paquetes completada.")

# --- Variables Globales ---
global memoria_global
memoria_global = {
    "zona_horaria": "Europe/Madrid",  # Zona horaria predeterminada
}

global hora_madrid  # Variable global para almacenar la hora de Madrid

global FORMAT, CHANNELS, RATE, CHUNK, DURACION, FRAMES
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
DURACION = 3
FRAMES = []

global ruta_base, db_path_users, db_path_root, db_path_root_calendar, db_path_root_calendar_ines
ruta_base = "home/Usuarios"
db_path_users = "home/Usuarios"
db_path_root = "/root/.usuario_root_datos/base_de_datos_usuario/root.db"
db_path_root_calendar = "/root/.usuario_root_datos/base_de_datos_usuario/root_calendario.db"
db_path_root_calendar_ines = "/root/.usuario_root_datos/base_de_datos_usuario/Ines_calendario.db"

global tipo_usuario, comparacion_audio, tipo_voz, espectrometria_voz
tipo_usuario = "desconocido"
comparacion_audio = None
tipo_voz = "Indefinida"
espectrometria_voz = None

# --- Funciones Globales ---
def obtener_hora():
    """Obtiene la hora actual según la zona horaria en memoria global y la almacena globalmente."""
    global hora_madrid
    zona_horaria = memoria_global.get("zona_horaria", "UTC")
    try:
        tz = pytz.timezone(zona_horaria)
        hora_actual = datetime.now(tz)
        hora_madrid = hora_actual
        texto = f"La hora actual en {zona_horaria} es: {hora_actual.strftime('%H:%M:%S')}"
        print(f"[Inés] {texto}")
        hablar(texto)
        return hora_madrid
    except Exception as e:
        texto = f"No puedo obtener la hora debido a un error: {e}"
        print(f"[Inés] {texto}")
        hablar(texto)
        return None

def hablar(texto):
    """Convierte el texto en voz y lo reproduce."""
    tts = gTTS(text=texto, lang='es')
    tts.save("respuesta.mp3")
    os.system("mpg321 respuesta.mp3")
    os.remove("respuesta.mp3")

def escuchar_comando():
    """Función para escuchar un comando del usuario."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
    try:
        comando = recognizer.recognize_google(audio, language='es-ES')
        print(f"Comando escuchado: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        print("No se entendió el comando.")
        return ""
    except sr.RequestError:
        print("Error al conectarse al servicio de Google.")
        return ""

def conectar_bd(ruta_db):
    """Conecta a la base de datos SQLite en la ruta especificada."""
    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        print("Conexión a la base de datos exitosa.")
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None, None

def verificar_registro_root():
    """Verifica si ya existe un registro root. Si no existe, permite el registro."""
    archivo_control = "root/.usuario_root_datos/.registro_root"
    if os.path.exists(archivo_control):
        print("El registro del usuario root ya existe. No se puede repetir el proceso.")
        return False
    with open(archivo_control, "w") as f:
        f.write("Registro root completado.")
    print("Registro root permitido. Proceda con las capturas.")
    return True

# --- Predefinición de las tablas de base de datos ---
def crear_tablas_predefinidas():
    """Crea las tablas necesarias en las bases de datos predefinidas. Esta función debe ejecutarse solo una vez al inicio."""
    conexion_users = sqlite3.connect(db_path_users)
    conexion_root = sqlite3.connect(db_path_root)
    conexion_root_calendar = sqlite3.connect(db_path_root_calendar)
    conexion_root_calendar_ines = sqlite3.connect(db_path_root_calendar_ines)

    try:
        cursor_users = conexion_users.cursor()
        cursor_users.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Tipo TEXT NOT NULL,
                Direccion TEXT,
                Telefono TEXT,
                CorreoElectronico TEXT,
                NumeroEmergencia TEXT,
                PalabraSeguridad TEXT
            )
        """)
        cursor_users.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_nuevos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Tipo TEXT NOT NULL,
                ColorOjos TEXT,
                Cejas TEXT,
                Barba TEXT,
                Barba_color TEXT,
                BocaGrande TEXT,
                ColorRecuadro TEXT,
                AudioArchivo TEXT,
                especmetria_numeriaca_voz TEXT,
                Telefono TEXT,
                Direccion TEXT,
                CorreoElectronico TEXT
            )
        """)

        cursor_root = conexion_root.cursor()
        cursor_root.execute("""
            CREATE TABLE IF NOT EXISTS Root (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Direccion TEXT NOT NULL,
                NumeroTelefono TEXT NOT NULL,
                CorreoElectronico TEXT NOT NULL,
                NumeroEmergencia TEXT,
                PalabraSeguridad TEXT NOT NULL
            )
        """)

        cursor_root_calendar = conexion_root_calendar.cursor()
        cursor_root_calendar.execute("""
            CREATE TABLE IF NOT EXISTS CalendarioRoot (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ZonaHoraria TEXT NOT NULL,
                Mes INTEGER NOT NULL,
                Dia INTEGER NOT NULL,
                Hora INTEGER NOT NULL,
                Minuto INTEGER NOT NULL,
                Segundo INTEGER NOT NULL
            )
        """)

        cursor_root_calendar_ines = conexion_root_calendar_ines.cursor()
        cursor_root_calendar_ines.execute("""
            CREATE TABLE IF NOT EXISTS CalendarioInes (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ZonaHoraria TEXT NOT NULL,
                Mes INTEGER NOT NULL,
                Dia INTEGER NOT NULL,
                Hora INTEGER NOT NULL,
                Minuto INTEGER NOT NULL,
                Segundo INTEGER NOT NULL
            )
        """)

        conexion_users.commit()
        conexion_root.commit()
        conexion_root_calendar.commit()
        conexion_root_calendar_ines.commit()
        print("Tablas predefinidas creadas correctamente.")

    except Exception as e:
        print(f"Error al crear tablas: {e}")

    finally:
        conexion_users.close()
        conexion_root.close()
        conexion_root_calendar.close()
        conexion_root_calendar_ines.close()
        print("Conexiones cerradas tras la creación de tablas.")

# --- Identificación por voz ---
def autenticar_por_voz(FORMAT, CHANNELS, RATE, CHUNK, duracion, frames):
    """Graba un audio para identificar al usuario."""
    audio = pyaudio.PyAudio()
    archivo_audio = "Identificacion_voz0.wav"

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    for i in range(0, int(RATE / CHUNK * duracion)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Grabación terminada")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(archivo_audio, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    global comparacion_audio
    
    try:
        if comparacion_audio:
            resultado_comparacion = comparar_voz(audio_grabado, archivo_audio)
            if resultado_comparacion:
                print(f"Las voces coinciden.")
                return True
            else:
                print(f"Las voces no coinciden.")
                return False
    except Exception as e:
        print(f"Error al comparar los audios: {e}")
        return False

# --- Guardar nuevos usuario no root ---
def guardar_nuevo_usuario(nombre_usuario, archivo_audio, ruta_base=db_path_users):
    """Guarda la grabación de un nuevo usuario en el sistema y en la base de datos."""
    conn, cursor = conectar_bd(ruta_base)
    if conn is None:
        return False

    ruta_usuario = os.path.join(ruta_base, nombre_usuario)
    if not os.path.exists(ruta_usuario):
        os.makedirs(ruta_usuario)

    ruta_voz = os.path.join(ruta_usuario, "voz")
    if not os.path.exists(ruta_voz):
        os.makedirs(ruta_voz)

    archivo_destino = os.path.join(ruta_voz, f"{nombre_usuario}_voz.wav")
    os.rename(archivo_audio, archivo_destino)
    print(f"Nuevo usuario {nombre_usuario} creado y voz guardada en {archivo_destino}.")

    cursor.execute("INSERT INTO usuarios (nombre, archivo_audio) VALUES (?, ?)", (nombre_usuario, archivo_destino))
    conn.commit()
    conn.close()

    return True
    
# --- Gestor de calendario root ---
def gestionar_calendario_root():
    """Función para gestionar el calendario de Root."""
    hablar("Los registros de los eventos fueron satisfactorios.")
    comando = escuchar_comando().lower()

    if "agregar" in comando:
        hablar("Por favor, dime el detalle del registro que deseas agregar.")
        registro = escuchar_comando()
        agregar_registro_root(registro)
    elif "eliminar" in comando:
        hablar("Dime el ID del registro que deseas eliminar.")
        id_registro = int(escuchar_comando())
        eliminar_datos_root_calendario(id_registro)
    elif "consultar" in comando:
        consultar_registros_root()
    else:
        hablar("No reconozco ese comando. Intenta de nuevo.")

def agregar_registro_root(registro):
    """Agrega un registro al calendario de Root."""
    conexion = sqlite3.connect(db_path_root_calendar)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO CalendarioRoot (ZonaHoraria, Mes, Dia, Hora, Minuto, Segundo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, registro)
    conexion.commit()
    conexion.close()
    hablar(f"El registro '{registro}' ha sido agregado al calendario de Root.")

def consultar_registros_root():
    """Consulta y muestra los registros del calendario de Root."""
    conexion = sqlite3.connect(db_path_root_calendar)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM CalendarioRoot")
    registros = cursor.fetchall()
    for registro in registros:
        hablar(f"Registro: {registro}")
    conexion.close()
    
# --- Ines independiente calendario ---
def gestionar_calendario_ines():
    """Función para gestionar el calendario de Inés."""
    while True:
        hablar("¿Qué deseas hacer con tu calendario, Inés? Puedes agregar, eliminar, consultar o salir.")
        comando = escuchar_comando()

        if "agregar" in comando:
            hablar("Dime el detalle del registro que deseas agregar. Indica la zona horaria, mes, día, hora, minuto y segundo.")
            zona_horaria = escuchar_comando()
            mes = int(input("Mes (1-12): "))
            dia = int(input("Día (1-31): "))
            hora = int(input("Hora (0-23): "))
            minuto = int(input("Minuto (0-59): "))
            segundo = int(input("Segundo (0-59): "))
            agregar_registro(db_path_root_calendar_ines, (zona_horaria, mes, dia, hora, minuto, segundo))
        elif "eliminar" in comando:
            hablar("Dime el ID del registro que deseas eliminar.")
            id_registro = int(input("ID del registro: "))
            eliminar_datos_ines_calendario(id_registro)
        elif "consultar" in comando:
            consultar_registros(db_path_root_calendar_ines)
        elif "salir" in comando:
            hablar("Saliendo del sistema de gestión del calendario de Inés.")
            break
        else:
            hablar("Comando no reconocido. Intenta nuevamente.")

def eliminar_datos_ines_calendario(id_registro):
    """Elimina un registro específico de la base de datos de calendario de Inés después de confirmación."""
    conexion = sqlite3.connect(db_path_root_calendar_ines)
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM CalendarioInes WHERE ID=?", (id_registro,))
    registro = cursor.fetchone()

    if registro:
        hablar(f"¿Estás seguro que quieres eliminar el registro con ID {id_registro} de la base de datos? Di 'sí' para confirmar o 'no' para cancelar.")
        
        respuesta = escuchar_comando()

        if "sí" in respuesta:
            cursor.execute("DELETE FROM CalendarioInes WHERE ID=?", (id_registro,))
            conexion.commit()
            hablar(f"De acuerdo, así ahorraremos espacio. Además, es una franja horaria {id_registro} que no me interesa, eliminado correctamente.")
        elif "no" in respuesta:
            hablar(f"No quiero, me gusta saber la hora de {id_registro}, tengo mi libertad.")
        else:
            hablar("Respuesta no válida. La eliminación ha sido cancelada.")
    else:
        hablar(f"No se encontró un registro con ID {id_registro}.")
    conexion.close()
    
# --- Función para que el usuario cambie la zona horaria con confirmación usuario ---
def cambiar_zona_horaria():
    hablar("[Inés] ¿En qué zona horaria te gustaría que consulte la hora?")
    nueva_zona = input("Introduce la nueva zona horaria (Ejemplo: 'Europe/Madrid', 'America/New_York', etc.): ")
    
    try:
        pytz.timezone(nueva_zona)
        texto = f"Has elegido la zona horaria '{nueva_zona}'. ¿Quieres confirmar este cambio?"
        print(f"[Inés] {texto}")
        hablar(texto)
        
        confirmacion = input("Confirma el cambio de zona horaria (Sí/No): ").strip().lower()
        
        if confirmacion == 'sí':
            memoria_global["zona_horaria"] = nueva_zona
            texto = f"¡Cambio exitoso! La nueva zona horaria es: {nueva_zona}"
            print(f"[Inés] {texto}")
            hablar(texto)
            obtener_hora()
        else:
            texto = "No se ha realizado ningún cambio."
            print(f"[Inés] {texto}")
            hablar(texto)
    
    except pytz.UnknownTimeZoneError:
        texto = f"La zona horaria '{nueva_zona}' no es válida. Intenta con otro nombre."
        print(f"[Inés] {texto}")
        hablar(texto)

# --- Función de inicialización para Debian 12.8 o cualquier kernel superior o igual a 6.5 ---
def inicializar_sistema():
    """Función que se ejecuta al inicio del sistema en Debian 12.8 o cualquier kernel superior a 6.5."""
    sistema = platform.system()
    kernel_version = platform.release()

    if sistema == "Linux" and kernel_version.startswith("6.") and float(kernel_version.split(".")[0]) >= 6:
        texto = "Iniciando sistema en Debian con kernel 6.5 o superior..."
        print(f"[Inés] {texto}")
        hablar(texto)
        
        texto = "Configurando zona horaria predeterminada..."
        print(f"[Inés] {texto}")
        hablar(texto)
        
        memoria_global["zona_horaria"] = "Europe/Madrid"
        obtener_hora()
        
    else:
        texto = f"Este sistema no está usando un kernel 6.5 o superior. Estás usando kernel {kernel_version}."
        print(f"[Inés] {texto}")
        hablar(texto)

# --- Crear un hilo para la inicialización ---
def iniciar_en_hilo():
    """Ejecuta la inicialización del sistema en un hilo independiente."""
    hilo_inicializacion = threading.Thread(target=inicializar_sistema)
    hilo_inicializacion.start()

###########################################################################

# --- Función para dar saludo de bienvenida y esperar el comando "Empecemos" ---
def identificar_usuario_root():
    """Identifica al usuario registrado y saluda, o pide registrarse si no existe."""
    hablar("¿Cómo te llamas?")
    nombre_usuario = escuchar_comando()

    if "Inés" in nombre_usuario:
        hablar("Hola soy Inés, bienvenido. ¿Qué deseas hacer?, ¿te parece bien empezar con la identificación root de usuario de la casa?")
        bienvenida_ines()
    elif "Root" in nombre_usuario:
        hablar("Perfecto, estoy entusiasmadísima por empezar a administrar el sistema de la casa.")
        bienvenida_root()
    else:
        if comprobar_usuario_existente(nombre_usuario):
            hablar(f"¡Hola {nombre_usuario}! Bienvenido de nuevo, ¿qué tal todo?")
        else:
            hablar(f"Hola {nombre_usuario}, parece que no estás registrado. Procederemos a registrarte.")
            registrar_usuario(nombre_usuario)
            hablar(f"¡Bienvenido, {nombre_usuario}! Ahora estás registrado en la base de datos.")

def saludo_y_espera():
    print("Buenas, soy Inés, y estoy preparada para identificar al usuario principal de la casa.")
    print("Por favor, diga 'Empecemos' para comenzar el proceso de identificación del usuario root.")

    while True:
        comando = input("Escuchando... (diga 'Empecemos'): ").lower()
        if comando == "empecemos":
            print("Comando recibido: Empecemos")
            break
        else:
            print("Comando no reconocido. Por favor, diga 'Empecemos' para continuar.")
    
    print("Iniciando el proceso de identificación del usuario root...")
    ejecutar_identificacion_root()

def ejecutar_identificacion_root():
    """Ejecuta la identificación del usuario root, incluyendo la creación de carpetas, grabación de audio, captura de imágenes y cifrado de datos."""
    if not verificar_registro_root():
        return
    
    crear_carpeta_usuario_y_root()
    imagenes = capturar_imagenes_root()
    audios = grabar_audio_root()
    archivos = imagenes + audios
    cifrar_datos_root(archivos)

    print("El proceso de identificación del usuario root ha sido completado.")

def crear_carpeta_usuario_y_root():
    """Crea las carpetas necesarias para el usuario root y otros usuarios."""
    os.makedirs("Usuarios/base_de_datos_usuario", exist_ok=True)
    print("Carpeta creada para usuarios generales: Usuarios/base_de_datos_usuario")

    os.makedirs("/root/.usuario_root_datos/base_de_datos_usuario", exist_ok=True)
    print("Carpeta creada para el usuario root: /root/.usuario_root_datos/base_de_datos_usuario")

def capturar_imagenes_root():
    """Captura 2000 imágenes del usuario root, distribuidas entre 4 cámaras (500 imágenes por cámara). Los archivos se almacenan cifrados dentro de 'root/.usuario_root_datos'."""
    ruta_root = "root/.usuario_root_datos"
    os.makedirs(ruta_root, exist_ok=True)

    camaras = ["Cámara 1", "Cámara 2", "Cámara 3", "Cámara 4"]
    imagenes_por_camara = 500

    imagenes = []
    for camara in camaras:
        print(f"Capturando imágenes desde: {camara}")
        for i in range(imagenes_por_camara):
            nombre_imagen = f"{camara.replace(' ', '_').lower()}_imagen_{i + 1}.jpg"
            ruta_imagen = os.path.join(ruta_root, nombre_imagen)
            
            with open(ruta_imagen, "wb") as archivo:
                archivo.write(os.urandom(1024))
            
            imagenes.append(ruta_imagen)
            print(f"Imagen capturada: {ruta_imagen}")

    print("Captura de imágenes completa. Todas las imágenes han sido almacenadas.")
    return imagenes

def grabar_audio_root():
    """Graba 100 MB de audio del usuario root distribuidos en 25 MB por dispositivo (4 dispositivos en total). El usuario responderá a preguntas específicas, y los archivos serán almacenados en 'root/.usuario_root_datos'."""
    ruta_root = "root/.usuario_root_datos"
    os.makedirs(ruta_root, exist_ok=True)

    preguntas = [
        "¿Cuál es su nombre completo, por favor?",
        "¿Cuál es su dirección de casa?",
        "¿Cuál es su número de teléfono?",
        "¿Cuál es su correo electrónico?",
        "¿Cuál es su número de emergencias?",
        "¿Cuál es la palabra de seguridad?"
    ]

    dispositivos = ["Cámara 1", "Cámara 2", "Dispositivo móvil", "Micrófono auxiliar"]
    tamano_por_dispositivo = 25 * 1024 * 1024

    audios = []
    for dispositivo in dispositivos:
        print(f"Grabando desde: {dispositivo}")
        for pregunta in preguntas:
            print(pregunta)
            nombre_archivo = f"{dispositivo.replace(' ', '_').lower()}_audio.raw"
            ruta_archivo = os.path.join(ruta_root, nombre_archivo)
            
            with open(ruta_archivo, "wb") as archivo:
                archivo.write(os.urandom(tamano_por_dispositivo))
            
            audios.append(ruta_archivo)
            print(f"Archivo grabado: {ruta_archivo}")

    print("Grabación completa. Todos los audios han sido almacenados.")
    return audios

def cifrar_datos_root(archivos):
    """Cifra los archivos del usuario root utilizando SHA-1024."""
    carpeta_cifrada = "root/.usuario_root_datos/cifrado"
    os.makedirs(carpeta_cifrada, exist_ok=True)

    for archivo in archivos:
        with open(archivo, "rb") as f:
            contenido = f.read()
            hash_1 = hashlib.sha512(contenido).digest()
            hash_2 = hashlib.sha512(hash_1).hexdigest()
        
        nombre_cifrado = os.path.basename(archivo) + ".hash"
        ruta_cifrada = os.path.join(carpeta_cifrada, nombre_cifrado)
        with open(ruta_cifrada, "w") as f:
            f.write(hash_2)

        print(f"Archivo cifrado y almacenado: {ruta_cifrada}")

    return carpeta_cifrada

saludo_y_espera()

# --- Función para autenticar usuario por voz ---
def autenticar_por_voz(audio_grabado):
    """
    Función para identificar al usuario por su voz comparando el audio grabado con las grabaciones previas.
    """
    print("Autenticación por voz...")

    # Obtener todos los usuarios registrados
    usuarios_registrados = [f for f in os.listdir("Registro") if os.path.isdir(os.path.join("Registro", f))]

    for usuario in usuarios_registrados:
        print(f"Comparando con el usuario: {usuario}")
        
        # Llamar a la función que compara las grabaciones
        if Comparacion_Sonido(audio_grabado, usuario):
            print(f"El usuario que está hablando es: {usuario}")
            return usuario  # Retorna el nombre del usuario que está hablando

    print("No se pudo identificar al usuario.")
    return None

# --- Función para grabar el audio del usuario hasta 20MB ---
def grabar_audio_usuario(nombre_usuario):
    """
    Graba audio de un usuario hasta alcanzar un tamaño de 10MB.
    """
    print(f"Grabando audio de {nombre_usuario} hasta 10MB...")

    audio = pyaudio.PyAudio()
    ruta_audio = f"Registro/{nombre_usuario}/Audio/"
    os.makedirs(ruta_audio, exist_ok=True)
    
    # Crear archivo de salida
    archivo_audio = os.path.join(ruta_audio, f"identificacion_usuario.wav")

    # Abrir stream de grabación de audio
    stream = audio.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024)
    
    frames = []
    total_audio_size = 0
    target_size_mb = 10  # Tamanho de audio objetivo en MB

    while total_audio_size < target_size_mb * 1024 * 1024:  # 10MB = 10 * 1024 * 1024 bytes
        data = stream.read(1024)
        frames.append(data)
        total_audio_size += len(data)

    # Finalizar grabación
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Guardar el archivo de audio
    with wave.open(archivo_audio, 'wb') as waveFile:
        waveFile.setnchannels(2)
        waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(44100)
        waveFile.writeframes(b''.join(frames))

    print(f"Audio grabado exitosamente para {nombre_usuario}. El archivo tiene un tamaño de {total_audio_size / (1024 * 1024):.2f} MB.")

# --- Función para grabar audio ---
def grabar_audio(nombre_archivo, FORMAT, CHANNELS, RATE, CHUNK, duracion):
    """
    Graba audio durante una duración específica y lo guarda en un archivo .wav.
    """
    audio = pyaudio.PyAudio()
    frames = []

    print(f"Iniciando grabación para: {nombre_archivo}...")
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    for _ in range(0, int(RATE / CHUNK * duracion)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Grabación terminada.")

    # Detenemos grabación
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Guardamos el archivo de audio
    with wave.open(nombre_archivo, 'wb') as waveFile:
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))

    print(f"Archivo de audio guardado como: {nombre_archivo}")
    return nombre_archivo


# --- Función para determinar y guardar tipo de voz ---
def determinar_y_guardar_tipo_voz(archivo_audio, nombre_bd, nombre_usuario, tipo_usuario):
    """
    Determina el tipo de voz basado en un archivo de audio y guarda los datos en la base de datos.
    """
    try:
        print(f"Analizando tipo de voz en archivo: {archivo_audio}...")
        _, data = wave.open(archivo_audio, 'rb').readframes(-1), wave.open(archivo_audio, 'rb').getnframes()
        frecuencia_promedio = np.mean(np.abs(np.frombuffer(data, dtype=np.int16)))

        # Clasificación básica del tipo de voz
        if frecuencia_promedio < 150:
            tipo = "Grave"
        elif 150 <= frecuencia_promedio <= 300:
            tipo = "Normal"
        elif frecuencia_promedio > 300:
            tipo = "Aguda"
        else:
            tipo = "Indefinida"

        print(f"El tipo de voz es: {tipo}")

        # Guardar en la base de datos
        guardar_tipo_voz(nombre_bd, nombre_usuario, tipo_usuario, tipo)
        return tipo
    except Exception as e:
        print(f"Error al analizar el tipo de voz: {e}")
        return "Error"

# --- Función para grabar y autenticar por voz ---
def autenticar_por_voz(nombre_usuario, duracion=3, formato=FORMAT, canales=CHANNELS, tasa_muestreo=RATE, tamano_buffer=CHUNK):
    """
    Graba el audio de la voz del usuario y lo guarda en un archivo temporal.
    Luego verifica si la voz es registrada comparándola con los archivos existentes.
    """
    archivo_audio = "audio_grabado.wav"
    frames = []

    # Grabar el audio
    audio = pyaudio.PyAudio()
    stream = audio.open(format=formato, channels=canales, rate=tasa_muestreo, input=True, frames_per_buffer=tamano_buffer)
    print(f"Grabando el audio de {nombre_usuario} por {duracion} segundos...")

    for _ in range(0, int(tasa_muestreo / tamano_buffer * duracion)):
        data = stream.read(tamano_buffer)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Guardar el archivo de audio grabado
    with wave.open(archivo_audio, 'wb') as waveFile:
        waveFile.setnchannels(canales)
        waveFile.setsampwidth(audio.get_sample_size(formato))
        waveFile.setframerate(tasa_muestreo)
        waveFile.writeframes(b''.join(frames))
    
    print(f"Audio grabado en: {archivo_audio}")
    
    # Verificar si la voz ya está registrada
    if not buscar_voz_registrada(nombre_usuario):
        print("La voz no está registrada en el sistema.")
        return False

    # Comparar con los archivos de audio existentes para autenticar
    for archivo in os.listdir(f"home/usuario/{nombre_usuario}/voz"):
        if archivo.endswith(".wav"):
            archivo_comparar = os.path.join(f"home/usuario/{nombre_usuario}/voz", archivo)
            if comparar_voz(archivo_audio, archivo_comparar):
                print(f"Autenticación exitosa: La voz corresponde al usuario {nombre_usuario}.")
                # Eliminar el archivo de audio temporal después de la comparación
                os.remove(archivo_audio)
                print(f"Archivo de audio temporal {archivo_audio} eliminado.")
                return True

    print(f"Autenticación fallida: La voz no coincide con los registros de {nombre_usuario}.")
    # Eliminar el archivo de audio temporal después de la comparación
    os.remove(archivo_audio)
    print(f"Archivo de audio temporal {archivo_audio} eliminado.")
    return False
    
# --- Función para buscar si la voz está registrada en las carpetas de audio ---
def buscar_voz_registrada(nombre_usuario, ruta_base="home/usuario"):
    """
    Busca si el audio grabado de un usuario ya está registrado en las carpetas de audio.
    """
    ruta_usuario = os.path.join(ruta_base, nombre_usuario, "voz")
    
    # Si el usuario tiene una carpeta y archivos de audio
    if os.path.exists(ruta_usuario):
        archivos_audio = [f for f in os.listdir(ruta_usuario) if f.endswith(".wav")]
        if archivos_audio:
            print(f"Archivos de audio encontrados para {nombre_usuario}: {archivos_audio}")
            return True
        else:
            print(f"No se encontraron archivos de audio registrados para {nombre_usuario}.")
    else:
        print(f"No existe la carpeta para el usuario {nombre_usuario}.")
    
    return False

#--- Función para comparar dos archivos de audio ---
def comparar_voz(archivo_audio1, archivo_audio2):
    """
    Compara dos archivos de audio para determinar similitud utilizando MFCC (Coeficientes Cepstrales en las Frecuencias de Mel).
    """
    try:
        # Cargar ambos audios
        audio1, sr1 = librosa.load(nombre_usuario, sr=None)
        audio2, sr2 = librosa.load(audio, sr=None)

        # Extraer los MFCCs de ambos audios
        mfcc1 = librosa.feature.mfcc(y=audio1, sr=sr1, n_mfcc=13)
        mfcc2 = librosa.feature.mfcc(y=audio2, sr=sr2, n_mfcc=13)

        # Calcular la distancia entre los MFCCs
        distancia = np.linalg.norm(mfcc1 - mfcc2)
        
        # Definir un umbral para la comparación
        umbral = 10.0

        if distancia < umbral:
            print(f"Los archivos de audio son similares (distancia: {distancia}).")
            return True
        else:
            print(f"Los archivos de audio no son similares (distancia: {distancia}).")
            return False
    except Exception as e:
        print(f"Error al comparar los audios: {e}")
        return False)

#--- Función principal: Captura de imágenes y análisis facial mediante capturar imágenes y registrar usuarios ---
def capturar_y_analizar_usuario(nombre_usuario, tipo_usuario, total_images=1000, parche=None):
    """
    Captura imágenes, analiza características faciales, guarda los datos en la base de datos,
    y dibuja un recuadro en tiempo real con el nombre y tipo de usuario.
    """
    # Crear carpeta para las imágenes
    ruta_img = f"Usuarios/{nombre_usuario}_{tipo_usuario}/IMG"
    os.makedirs(ruta_img, exist_ok=True)

    # Inicializar captura de video
    cap = cv2.VideoCapture(0)
    count = 0
    color_recuadro = obtener_color_recuadro(tipo_usuario)

    while count < total_images:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if len(faces) > 0:
            for face in faces:
                landmarks = predictor(gray, face)

                # --- Parte 2: Detección del color de ojos ---
                color_ojos_hex = detectar_color_ojos(frame, landmarks, parche)

                # --- Parte 3: Detección de rangos faciales ---
                boca, labios, barba, orejas, pomulos, color_barba_hex = detectar_rangos_faciales(frame, landmarks)

                # --- Parte 4: Guardar en la base de datos ---
                almacenar_en_base_de_datos(nombre_usuario, tipo_usuario, color_ojos_hex, boca, labios, barba, orejas, pomulos, color_barba_hex, color_recuadro)

                # Dibujar el recuadro en tiempo real
                cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color_recuadro, 2)
                cv2.putText(frame, f'{nombre_usuario} ({tipo_usuario})', (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_recuadro, 2)

                # Guardar la imagen capturada
                cv2.imwrite(f"{ruta_img}/img_{count}.jpg", frame)
                count += 1

        # Mostrar la imagen en tiempo real
        cv2.imshow("Captura de Rostros", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
#--- Función para detectar el color de los ojos ---
def detectar_color_ojos(frame, landmarks, parche=None):
    """
    Detecta el color de los ojos y lo devuelve en formato hexadecimal.
    Si hay un parche, analiza solo el ojo visible.
    """
    left_eye_indices = list(range(36, 42))
    right_eye_indices = list(range(42, 48))

    left_eye_points = np.array([[landmarks.part(i).x, landmarks.part(i).y] for i in left_eye_indices])
    right_eye_points = np.array([[landmarks.part(i).x, landmarks.part(i).y] for i in right_eye_indices])

    left_eye_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    right_eye_mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    cv2.fillConvexPoly(left_eye_mask, left_eye_points, 255)
    cv2.fillConvexPoly(right_eye_mask, right_eye_points, 255)

    left_eye_color = cv2.mean(frame, mask=left_eye_mask)[:3]
    right_eye_color = cv2.mean(frame, mask=right_eye_mask)[:3]

    if parche == "izquierdo":
        return rgb_a_hex(right_eye_color)
    elif parche == "derecho":
        return rgb_a_hex(left_eye_color)
    else:
        avg_color = np.mean([left_eye_color, right_eye_color], axis=0)
        return rgb_a_hex(avg_color)

#--- Conversión de RGB a Hexadecimal ---
def rgb_a_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[2]), int(rgb[1]), int(rgb[0]))
    
#--- Función para detectar rangos faciales avanzados ---
def detectar_rangos_faciales(frame, landmarks):
    """
    Detecta características avanzadas como tipo de boca, barba, orejas y pómulos.
    Incluye detección de color de barba y conversión a hexadecimal.
    """
    boca = random.choice(["Grande", "Mediana", "Pequeña"])
    labios = random.choice(["Finos", "Gruesos"])
    barba = random.choice(["Corta", "Mediana", "Larga", "Sin_barba"])
    orejas = random.choice(["Grandes", "Medianas", "Pequeñas", "Pegadas"])
    pomulos = random.choice(["Marcados", "No_marcados"])

    # Simulación de detección de color de barba
    colores_barba = {
        "Negra": "#000000",
        "Castaña": "#654321",
        "Rubia": "#FFD700",
        "Pelirroja": "#FF4500",
        "Canosa": "#C0C0C0"
    }
    color_barba_detectado = random.choice(list(colores_barba.keys()))
    color_barba_hex = colores_barba[color_barba_detectado]

    return boca, labios, barba, orejas, pomulos, color_barba_hex

#--- Función para almacenar datos en la base de datos ---
def almacenar_en_base_de_datos(nombre_usuario, tipo_usuario, color_ojos, boca, labios, barba, orejas, pomulos, color_barba_hex, color_recuadro):
    """
    Almacena las características faciales del usuario en la base de datos.
    """
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()

    # Crear tabla si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Tipo TEXT NOT NULL,
        ColorOjos TEXT,
        Boca TEXT,
        Labios TEXT,
        Barba TEXT,
        Orejas TEXT,
        Pomulos TEXT,
        ColorBarbaHex TEXT,
        ColorRecuadro TEXT
    )
    """)

    # Insertar datos
    cursor.execute("""
    INSERT INTO Usuarios (Nombre, Tipo, ColorOjos, Boca, Labios, Barba, Orejas, Pomulos, ColorBarbaHex, ColorRecuadro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre_usuario, tipo_usuario, color_ojos, boca, labios, barba, orejas, pomulos, color_barba_hex, str(color_recuadro)))

    conexion.commit()
    conexion.close()

#--- Función para obtener el color del recuadro según el tipo de usuario de la base de datos ---
def obtener_color_recuadro(tipo_usuario):
    """
    Devuelve el color del recuadro según el tipo de usuario.
    """
    if tipo_usuario == "intruso":
        return (0, 0, 255)  # Rojo
    if tipo_usuario == "familia":
        return (255, 0, 0)  # Azul
    if tipo_usuario == "amigo":
        return (0, 255, 255)  # Amarillo
    if tipo_usuario == "visita_casual":
        return (169, 169, 169)  # Gris
    if tipo_usuario == "root":
        return (0, 255, 0)  # Verde

#--- Función para hacer el seguimiento en tiempo real y dibujar el recuadro ---
def seguimiento_recuadro(nombre_usuario, tipo_usuario):
    """
    Función para hacer el seguimiento de la cara del usuario y dibujar un recuadro
    con el color según el tipo de usuario.
    """
    color_recuadro = obtener_color_recuadro(tipo_usuario)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)

            # Dibujar recuadro con nombre y tipo de usuario
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color_recuadro, 2)
            cv2.putText(frame, f'{nombre_usuario} ({tipo_usuario})', (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_recuadro, 2)

        cv2.imshow("Seguimiento de Usuario", frame)

#--- Función para verificar si el usuario está visible en la cámara ---
def verificar_usuario_en_camara():
    """
    Verifica si el rostro del usuario está visible usando las cámaras.
    Si no está visible, pasará a la búsqueda de archivo de voz.
    """
    detector = dlib.get_frontal_face_detector()
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    if len(faces) > 0:
        cap.release()
        cv2.destroyAllWindows()
        return True  # El rostro está visible
    else:
        cap.release()
        cv2.destroyAllWindows()
        return False  # El rostro no está visible

#--- Función para buscar archivo de voz en la carpeta del usuario ---
def buscar_archivo_voz(nombre_usuario, tipo_usuario):
    """
    Busca el archivo de voz del usuario en la ruta home/usuarios/usuario_nombre_tipo/voz
    """
    ruta_voz = f"/home/usuarios/{nombre_usuario}_{tipo_usuario}/voz"
    if os.path.exists(ruta_voz):
        archivos = os.listdir(ruta_voz)
        for archivo in archivos:
            if archivo.endswith(".wav"):
                return os.path.join(ruta_voz, archivo)
    return None  # Si no encuentra el archivo

#--- Función para realizar triangulación acústica ---
def triangulacion_acustica(ubicaciones_micros, tiempos_llegada):
    """
    Realiza la triangulación acústica para determinar la posición del usuario.
    """
    # Fórmula simplificada para triangulación acústica
    distancias = [tiempo * 343 for tiempo in tiempos_llegada]  # Asumimos velocidad del sonido a 343 m/s
    puntos = np.array(ubicaciones_micros)
    distancias = np.array(distancias)
    
    # Usamos un método de resolución de ecuaciones (CDT) para obtener el punto de intersección
    A = 2 * (puntos[1:, :] - puntos[0, :])
    b = distancias[1:] ** 2 - distancias[0] ** 2 - np.sum(puntos[1:, :] ** 2, axis=1) + np.sum(puntos[0, :] ** 2, axis=0)
    
    pos_usuario = np.linalg.lstsq(A, b, rcond=None)[0]
    return pos_usuario  # Coordenadas del usuario

#--- Función para comparar voz con base de datos ---   RETOCAR
def comparar_voz(archivo_voz):
    """
    Compara el archivo de voz con la base de datos para identificar al usuario.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(archivo_voz) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)  # Usamos Google para la transcripción
            print(f"Voz reconocida: {text}")
            return True  # Si el reconocimiento tiene éxito, se puede continuar
        except sr.UnknownValueError:
            print("No se pudo reconocer la voz.")
            return False
        except sr.RequestError as e:
            print(f"Error en la solicitud de voz; {e}")
            return False

#--- Función para asociar el recuadro al usuario y pintar ---
def dibujar_recuadro_en_tiempo_real(nombre_usuario, tipo_usuario):
    """
    Dibuja el recuadro con el color y nombre del usuario según el tipo de usuario.
    """
    color_recuadro = obtener_color_recuadro(tipo_usuario)

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color_recuadro, 2)
            cv2.putText(frame, f'{nombre_usuario} ({tipo_usuario})', (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_recuadro, 2)

        cv2.imshow("Identificación en Tiempo Real", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#--- Función principal que gestiona los pasos ---
def gestionar_identificacion_usuario(nombre_usuario, tipo_usuario, obtener_ubicacion=False):
    """
    Función principal para gestionar la identificación del usuario con cámaras y voz.
    """
    if not verificar_usuario_en_camara():  # Si el usuario no está visible en la cámara
        print("Usuario no detectado en la cámara, procediendo con búsqueda por voz...")
        
        archivo_voz = buscar_archivo_voz(nombre_usuario, tipo_usuario)
        if archivo_voz and comparar_voz(archivo_voz):
            print("Voz reconocida, identificando usuario...")
            dibujar_recuadro_en_tiempo_real(nombre_usuario, tipo_usuario)
            
            if obtener_ubicacion:
                # Si se desea obtener la ubicación, ejecutar triangulación
                ubicacion = triangulacion_acustica([[0, 0], [1, 0], [0, 1]], [0.2, 0.15, 0.25])  # Ejemplo con posiciones y tiempos de llegada de los micrófonos
                print(f"Ubicación del usuario: {ubicacion}")
        else:
            print("No se pudo reconocer la voz o el archivo de voz no existe.")
    else:
        print("Usuario detectado en la cámara.")
        dibujar_recuadro_en_tiempo_real(nombre_usuario, tipo_usuario)
        if obtener_ubicacion:
            # Si se desea obtener la ubicación, ejecutar triangulación
            ubicacion = triangulacion_acustica([[0, 0], [1, 0], [0, 1]], [0.2, 0.15, 0.25])  # Ejemplo con posiciones y tiempos de llegada de los micrófonos
            print(f"Ubicación del usuario: {ubicacion}")

#------------------------------------------------------------------
#------------------ Funcioncines globales -------------------------

#--- Función para convertir texto a voz (gTTS) ---
def hablar(texto):
    """Convierte el texto a voz usando gTTS y lo reproduce."""
    tts = gtts.gTTS(texto, lang='es')  # Idioma español
    tts.save("respuesta.mp3")  # Guardamos el audio
    os.system("mpg321 respuesta.mp3")  # Reproducir el audio con mpg321 (o usa cualquier reproductor)

#--- Función para que Inés consulte la hora en cualquier parte del mundo ---
def consultar_hora_mundo():
    """Permite a Inés investigar la hora en cualquier lugar del mundo por su cuenta."""
    zonas_de_interes = [
        "Europe/Paris", "America/New_York", "Asia/Tokyo", "Australia/Sydney", "Africa/Nairobi"
    ]
    
    texto = "Iniciando consultas de hora en diferentes lugares del mundo..."
    print(f"[Inés] {texto}")
    hablar(texto)

    # Inés realiza consultas autónomas sobre la hora en diversas zonas horarias
    for zona_pregunta in zonas_de_interes:
        try:
            tz = pytz.timezone(zona_pregunta)  # Consultar la zona horaria
            hora_actual = datetime.now(tz)
            texto = f"La hora actual en {zona_pregunta} es: {hora_actual.strftime('%H:%M:%S')}"
            print(f"[Inés] {texto}")
            hablar(texto)
        except pytz.UnknownTimeZoneError:
            texto = f"No pude encontrar la zona horaria '{zona_pregunta}'. Verifica el nombre."
            print(f"[Inés] {texto}")
            hablar(texto)

#--- Función que utiliza la hora global ---
def mostrar_hora_madrid():
    """Muestra la hora de Madrid almacenada en la variable global."""
    global hora_madrid
    if hora_madrid:
        texto = f"La hora de Madrid es actualmente: {hora_madrid.strftime('%H:%M:%S')}"
        print(f"[Inés] {texto}")
        hablar(texto)
    else:
        texto = "No se ha podido obtener la hora de Madrid."
        print(f"[Inés] {texto}")
        hablar(texto)

#--- Iniciar el sistema al comienzo ---
iniciar_en_hilo()
    
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# --- Función principal para la interacción por voz con el usuario root ---
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

def funcion_comando_voz_ines():
    print("Inés está a la escucha...")

    # Reconocimiento de voz
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            print("¿En qué puedo ayudarte?")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            # Reconocer lo que el usuario ha dicho
            command = recognizer.recognize_google(audio).lower()
            print(f"Comando detectado: {command}")

            # Comandos predefinidos
            if "quién es ines" in command:
                print("Inés está a la escucha, ¿en qué necesitas?")
            elif "buscar" in command:
                buscar_enternet(command)
            elif "musica" in command:
                reproducir_musica(command)
            elif "evento" in command:
                crear_evento(command)
            elif "casa" in command:
                verificar_estado_casa(command)
            elif "wiki" in command:
                buscar_wikipedia(command)
            elif "llama a emergencia" in command:
                llamada_emergencia()
            elif "lee el documento" in command:
                leer_documento()
            else:
                print("Comando no reconocido. Intenta de nuevo.")
                print("Inés no ha entendido el comando. Por favor, intenta decirlo nuevamente.")
        except sr.UnknownValueError:
            print("No entendí lo que dijiste. Por favor, repítelo.")
        except sr.RequestError:
            print("Error con el servicio de reconocimiento de voz. Intenta de nuevo.")
            
# --- Función de búsqueda en internet ---
def buscar_enternet(command):
    search_query = command.replace("buscar", "").strip():
        print("¿Qué te gustaría buscar?")

# --- Función para reproducir música ---
def reproducir_musica(command):
    search_query = command.replace("musica", "").strip()
    if search_query:
        print(f"Reproduciendo {search_query} en YouTube...")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
    else:
        print("¿Qué tema te gustaría escuchar?")
        
#--- Función para verificar el estado de la casa ---
def verificar_estado_casa(command):
    estado = random.choice(["normal", "revuelta"])
    print(f"La casa está {estado}. Acceso a cámaras permitido.")

#--- Función para realizar búsqueda en Wikipedia ---
def buscar_wikipedia(command):
    search_query = command.replace("wiki", "").strip()
    print(f"Buscando '{search_query}' en Wikipedia...")
    webbrowser.open(f"https://es.wikipedia.org/wiki/{search_query}")

#--- Función para realizar llamada de emergencia ---
def llamada_emergencia():
    print(" llamada al 112")

#--- Función para leer documentos ---
def leer_documento():
    print("Leyendo el documento...")

#--- Función para crear el evento ---
def crear_evento(command, hora_madrid, mic):
    # Suponemos que el comando es el nombre del evento
    evento = command.replace("evento", "").strip()

    # Preguntar por el evento, día, hora, minutos y tiempo de aviso en una sola pregunta
    r = sr.Recognizer()
    with mic as source:
        s = gTTS(f"¿Qué evento quiee que le recuerde?, ¿Para qué día es?, y me puede decir la hora esacta? y ¿ Cuándo quiere que le avise con antelación?, por favor", lang='es-es', slow=False)
        s.save('sample.mp3')
        playsound('sample.mp3')
        audio = r.listen(source)

    try:
        # Procesamos la respuesta
        query = r.recognize_google(audio, language="es-ES")
        print(f"Respuesta del usuario: {query}")

        # Suponemos que la respuesta será algo como: "Evento el lunes a las 15:00 con 10 minutos de antelación"
        partes = query.split(" ")
        dia = partes[1]  # El día de la semana
        hora = partes[3]  # La hora
        minutos = partes[5]  # Los minutos
        alarma = partes[7]  # El tiempo de antelación

        # Confirmación del evento en una sola pregunta
        s = gTTS(f"El evento '{evento}' se pogramara para el {dia} a las {hora}:{minutos}. le enviare con un aviso de antelacio {alarma}:{dias}:{oras} y {minutos} de antelación. ¿Es correcto?", lang='es-es', slow=False)
        s.save('sample.mp3')
        playsound('sample.mp3')

        with mic as source:
            audio = r.listen(source)
        
        confirmacion = r.recognize_google(audio, language="es-ES").lower()

        if "sí" in confirmacion:
            # Guardar el evento en la base de datos
            conexion_base = sqlite3.connect("Calendario.db")
            Cursor = conexion_base.cursor()
            Cursor.execute(f"INSERT INTO Calendario (evento, dia, hora, minutos, alarma) VALUES (?, ?, ?, ?, ?)", 
                           (evento, dia, hora, minutos, alarma))
            conexion_base.commit()
            conexion_base.close()

            # Preguntar por Notificar al usuario ROOT que el evento ha sido guardado
            s = gTTS(f"El evento '{evento}' ha sido guardado para el {dia} a las {hora}:{minutos}. Se enviará un aviso {alarma} minutos antes del evento.", lang='es-es', slow=False)
            s.save('sample.mp3')
            playsound('sample.mp3')

            # Comprobamos la hora y programamos la alarma
            programar_alarma(dia, hora, minutos, alarma)
        
        else:
            s = gTTS("El evento no ha sido guardado. ¿Quieres intentar de nuevo?", lang='es-es', slow=False)
            s.save('sample.mp3')
            playsound('sample.mp3')

    except Exception as e:
        print(e)
        return "... "

#--- Función para programar la alarma ---
def programar_alarma(dia, hora, minutos, alarma):
    """
    Programa la alarma basándose en la fecha y hora del evento,
    además de la antelación de la alarma.
    """
    # Convertimos el día, hora y minutos a formato datetime
    hora_evento = f"{hora}:{minutos}"
    evento_datetime = datetime.strptime(f"{dia} {hora_evento}", "%A %H:%M")

    # Calculamos la hora de la alarma
    alarma_time = evento_datetime - timedelta(minutes=alarma)

    # Obtenemos la hora actual de Madrid
    hora_madrid = obtener_hora_madrid()

    # Si la hora de la alarma ya ha pasado, avisamos
    if hora_madrid >= alarma_time:
        print(f"¡Es hora de la alarma! El evento '{evento}' está por suceder.")
        
        # Avisar al usuario
        s = gTTS(f"LE recuedo que tiene el evento '{evento}' para la siguiente {dia}:{hora}:{minutos}. le ecuerdo este evento que me dijo.", lang='es-es', slow=False)
        s.save('sample.mp3')
        playsound('sample.mp3')

        # Eliminar el evento después de 30 minutos
        time.sleep(30 * 60)
        eliminar_evento()

#--- Función para eliminar un evento después de 30 minutos ---
def eliminar_evento():
    """
    Elimina el evento de la base de datos 30 minutos después de haber sido ejecutado.
    """
    conexion_base = sqlite3.connect("Calendario.db")
    cursor = conexion_base.cursor()

    # Eliminamos el evento de la base de datos
    cursor.execute("DELETE FROM Calendario WHERE id = ?", (evento_id,))
    conexion_base.commit()
    conexion_base.close()

    print(f"El evento con ID {evento_id} ha sido eliminado de la base de datos.")

#--- Función para revisar la base de datos cada minuto ---
def revisar_eventos():
    while True:
        # Abrir la base de datos y consultar eventos programados
        conexion_base = sqlite3.connect("Calendario.db")
        cursor = conexion_base.cursor()

        # Obtener la hora actual de Madrid
        hora_madrid = obtener_hora_madrid()

        # Verificar eventos y eliminar si el tiempo de la alarma ya ha pasado
        cursor.execute("SELECT id, dia, hora, minutos, alarma FROM Calendario")
        eventos = cursor.fetchall()

        for evento in eventos:
            evento_id, dia, hora, minutos, alarma = evento
            evento_datetime = datetime.strptime(f"{dia} {hora}:{minutos}", "%A %H:%M")
            alarma_time = evento_datetime - timedelta(minutes=alarma)

            if hora_madrid >= alarma_time:
                # El evento ya debe ser avisado o eliminado
                print(f"¡Es hora de la alarma para el evento '{evento_id}'!")
                # Aquí puedes agregar el código para avisar al usuario

                # Eliminar el evento después de 30 minutos de haber sido ejecutado
                time.sleep(30 * 60)  # Espera 30 minutos
                eliminar_evento(evento_id)

        # Esperar 1 minuto antes de la siguiente revisión
        time.sleep(60)

        conexion_base.close()

# Función para eliminar un evento de la base de datos
def eliminar_evento(evento_id):
    conexion_base = sqlite3.connect("Calendario.db")
    cursor = conexion_base.cursor()

    cursor.execute("DELETE FROM Calendario WHERE id = ?", (evento_id,))
    conexion_base.commit()
    conexion_base.close()

    print(f"El evento con ID {evento_id} ha sido eliminado de la base de datos.")




#---------------------------------------------------------------------------------------------------------


#--- Función para capturar imagen desde la cámara ---
def capturar_imagen_camara():
    cap = cv2.VideoCapture(0)  # 0 para la cámara predeterminada
    ret, frame = cap.read()
    if not ret:
        print("Error al capturar imagen")
    cap.release()
    return frame

#--- Función para leer imágenes de una carpeta ---
def leer_imagen_desde_archivo(ruta_imagen):
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        print(f"Error al leer la imagen desde {ruta_imagen}")
    return imagen

#--- Cargar el modelo preentrenado MobileNet ---
modelo_mobilenet = tf.keras.applications.MobileNetV2(weights='imagenet')

#--- Función para preprocesar la imagen antes de pasarla al modelo ---
def preprocesar_imagen(imagen):
    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    imagen = cv2.resize(imagen, (224, 224))  # Redimensionar a 224x224 (tamaño requerido por MobileNet)
    imagen = np.expand_dims(imagen, axis=0)  # Añadir dimensión de batch
    imagen = tf.keras.applications.mobilenet_v2.preprocess_input(imagen)  # Preprocesar para MobileNet
    return imagen

#--- Función para hacer predicción en la imagen ---
def predecir_objeto(imagen):
    imagen_preprocesada = preprocesar_imagen(imagen)
    predicciones = modelo_mobilenet.predict(imagen_preprocesada)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predicciones, top=3)[0]
    
    print("Predicciones:")
    for pred in decoded_predictions:
        print(f"Clase: {pred[1]}, Confianza: {pred[2]}")
        
#--- Función para descargar una imagen desde una URL ---
def descargar_imagen_web(url_imagen):
    try:
        # Hacer una solicitud HTTP para obtener la imagen
        response = requests.get(url_imagen)
        image = Image.open(io.BytesIO(response.content))
        return np.array(image)
    except Exception as e:
        print(f"Error descargando la imagen: {e}")
        return None

#-- Ejemplo de cómo usar la función ---
url = ''
imagen_descargada = descargar_imagen_web(url)
if imagen_descargada is not None:
    cv2.imshow('Imagen Descargada', imagen_descargada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#--- Función para procesar imágenes y entrenar el modelo
def procesar_imagen_y_entrenar(modelo, imagen):
    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    imagen = cv2.resize(imagen, (224, 224))  # Redimensionar a 224x224
    imagen = np.expand_dims(imagen, axis=0)  # Añadir dimensión de batch
    imagen = tf.keras.applications.mobilenet_v2.preprocess_input(imagen)  # Preprocesar imagen

    # Entrenar el modelo con la imagen procesada
    modelo.fit(imagen, imagen, epochs=1, batch_size=32)  # Entrenamiento simple
    return modelo

#--- Función para el autoaprendizaje con imágenes ---
def autoaprendizaje_imagenes(modelo, ruta_imagen, url_imagen_web):
    while True:
        try:
            # Captura de imagen desde la cámara
            imagen_local = capturar_imagen_camara()

            # Procesar la imagen local y entrenar
            modelo = procesar_imagen_y_entrenar(modelo, imagen_local)
            
            # Descargar imagen desde la web y procesar
            imagen_web = descargar_imagen_web(url_imagen_web)
            if imagen_web is not None:
                modelo = procesar_imagen_y_entrenar(modelo, imagen_web)

        except Exception as e:
            print(f"Error durante el autoaprendizaje de imágenes: {e}")
        
        # Esperar un intervalo antes del siguiente ciclo de entrenamiento
        time.sleep(600)  # Entrenar cada 10 minutos

#--- Iniciar el autoaprendizaje en un hilo ---
def iniciar_autoaprendizaje_con_imagenes():
    modelo = tf.keras.applications.MobileNetV2(weights='imagenet')
    ruta_imagen = "/ruta/a/tu/imagen.jpg"  # Cambia la ruta de la imagen
    url_imagen_web = ''  # Cambia la URL

    # Iniciar el hilo de autoaprendizaje
    autoaprendizaje_thread = threading.Thread(target=autoaprendizaje_imagenes, args=(modelo, ruta_imagen, url_imagen_web))
    autoaprendizaje_thread.daemon = True
    autoaprendizaje_thread.start()

    # Mantener el script principal activo
    while True:
        time.sleep(60)  # Mantener el script activo




# --- Ines inteligencia libre de apendizaje -----------------------------------------------------------
class InesAI:
    def __init__(self):
        self.motores_de_busqueda = [
            "https://duckduckgo.com/search?q=",
            "https://www.google.com/search?q="
            "https://www.bing.com/?toWww=1&redig=7F6997F4A5134C47B2ACD371DC693BF9/search?q="
            "https://es.search.yahoo.com/?fr2=p:fprd,mkt:es/search?q="
            "https://yandex.com/search?q="
            "https://www.ask.com/search?q="
            "https://es.quora.com/search?q="
            "https://www.aol.com/?guccounter=1/search?q="
            "https://www.ecosia.org/?c=es/search?q="
            "https://es.wikipedia.org/wiki/Internet_Archive/search?q="            
            "https://www.startpage.com/es/search?q="
            "https://www.searchencrypt.com/home/search?q="         
            "https://www.buscador.info/search?q="
            "https://www.dogpile.com/search?q="
            "https://www.excite.com//search?q="
        ]
        self.model_nlp = "Modelo NLP cargado"
        self.model_visual = "Modelo Visual cargado"
        self.model_audio = "Modelo Audio cargado"
        self.almacenamiento_actual = 500  # Almacenamiento inicial en GB
        self.max_almacenamiento = 500  # Límite de almacenamiento inicial en GB
        self.pesos = {"nlp": 0.5, "visual": 0.3, "audio": 0.2}  # Pesos iniciales de aprendizaje

    def procesar_texto(self, texto):
        # Aquí Inés "aprende" del texto y ajusta sus pesos
        print(f"Inés está aprendiendo de: {texto}")
        self.pesos["nlp"] += 0.05  # Incremento simulado del peso NLP
        return f"Respuesta generada a partir del texto: {texto}"

    def procesar_imagen(self, imagen_path):
        # Aquí Inés "aprende" de la imagen y ajusta sus pesos
        print(f"Inés está aprendiendo de la imagen: {imagen_path}")
        self.pesos["visual"] += 0.05  # Incremento simulado del peso Visual
        return "Resultado de la imagen procesada"

    def procesar_audio(self, archivo_audio):
        # Aquí Inés "aprende" del archivo de audio y ajusta sus pesos
        print(f"Inés está aprendiendo del audio: {archivo_audio}")
        self.pesos["audio"] += 0.05  # Incremento simulado del peso Audio
        return "Resultado del audio procesado"

    def procesar_video(self, archivo_video):
        # Aquí Inés "aprende" del video y ajusta sus pesos
        print(f"Inés está aprendiendo del video: {archivo_video}")
        self.pesos["visual"] += 0.05  # Incremento simulado del peso Visual
        return "Resultado del video procesado"

    def obtener_informacion_internet(self, pregunta):
        """
        Realiza una búsqueda en internet utilizando motores de búsqueda integrados.
        """
        resultados = []
        for motor in self.motores_de_busqueda:
            url = f"{motor}{pregunta}"
            resultado = self.consultar_motor_busqueda(url)
            if resultado:
                resultados.append(resultado)

        return self.comparar_informacion(resultados)

    def consultar_motor_busqueda(self, url):
        # --- Funcion busqueda en todo los motores de busqueda simultanamente ---
        # - Ines tendra la ccapacidad de buscar en todo los motorres de busqueda y analiza simultanamiente en diversos procesos como son texto audio video y imagenes para un aprendizaje mas rapido asi comola capacidad de traducir cualquier idioma
        #@
        """
        Realiza la consulta al motor de búsqueda dado.
        """
        if "duckduckgo" in url:
            return self.consultar_duckduckgo(url)
        elif "google" in url:
            return self.consultar_google(url)
        else:
            return self.consultar_otro_motor(url)

    def consultar_duckduckgo(self, url):
        """
        Scraping para obtener resultados de DuckDuckGo.
        """
        # Simulación de búsqueda en DuckDuckGo (sin librerías)
        return f"Resultados obtenidos desde DuckDuckGo: Información relevante de {url}"

    def consultar_google(self, url):
        """
        Scraping para obtener resultados de Google.
        """
        # Simulación de búsqueda en Google (sin librerías)
        return f"Resultados obtenidos desde Google: Información relevante de {url}"

    def consultar_otro_motor(self, url):
        """
        Consultar cualquier otro motor de búsqueda añadido.
        """
        return f"Respuesta del motor de búsqueda {url}."

    def comparar_informacion(self, resultados):
        """
        Compara la información obtenida de diferentes motores de búsqueda.
        """
        print(f"Comparando los siguientes resultados: {resultados}")
        return f"Comparación de información: {resultados}"

    def aprender_automaticamente(self, entrada, tipo_entrada):
        """
        Permite a Inés aprender automáticamente de diferentes tipos de entradas.
        """
        if tipo_entrada == 'texto':
            return self.procesar_texto(entrada)
        elif tipo_entrada == 'imagen':
            return self.procesar_imagen(entrada)
        elif tipo_entrada == 'audio':
            return self.procesar_audio(entrada)
        elif tipo_entrada == 'video':
            return self.procesar_video(entrada)
        else:
            print("Tipo de entrada desconocido")

    def preguntar_automatica(self):
        """
        Función de interacción autónoma de Inés. Ella puede preguntar cuando tenga dudas.
        """
        while True:
            duda = input("Inés no comprende completamente. ¿Sobre qué tema necesitas más información? ")
            respuesta = self.obtener_informacion_internet(duda)
            print(f"Inés encontró la siguiente información: {respuesta}")

    def necesita_almacenamiento(self):
        """
        Inés determina si necesita más espacio para almacenar más información.
        """
        if self.almacenamiento_actual >= self.max_almacenamiento:
            return True
        return False

    def solicitar_almacenamiento(self):
        """
        Solicita al usuario root un aumento de almacenamiento cuando se alcanza el límite.
        """
        print("Inés ha alcanzado el límite de almacenamiento actual.")
        respuesta = input("¿Deseo aumentar el almacenamiento por favor puede ser? (s/n): ").lower()

        if respuesta == "s":
            aumento = int(input("¿Necesito como minimo un tera mas se puede añadir? "))
            self.max_almacenamiento += aumento
            self.almacenamiento_actual = self.max_almacenamiento
            print(f"Se ha añadido {aumento} GB de almacenamiento. El nuevo límite es de {self.max_almacenamiento} GB.")
        else:
            print("Inés no puede continuar aprendiendo sin más espacio de almacenamiento.")

    def iniciar(self):
        """
        Inicia la autonomía de Inés. Ella puede aprender y también preguntará si tiene dudas.
        """
        print("Buenas Soy Inés. Estoy lista para aprender y tengo varias dudas al respecto sobre varios temas ¿podemos conversar sobre ellos?.")

        while True:
            tipo_entrada = input("¿Qué tipo de entrada deseas procesar? (texto, imagen, audio, video): ").lower()
            if tipo_entrada in ['texto', 'imagen', 'audio', 'video']:
                entrada = input("Por favor, ingresa la entrada: ")
                self.aprender_automaticamente(entrada, tipo_entrada)
            else:
                print("Tipo de entrada no soportado, intenta de nuevo.")
            
            # Si Inés tiene dudas, puede preguntarse a sí misma
            self.preguntar_automatica()

            # Verificar si Inés necesita más espacio de almacenamiento
            if self.necesita_almacenamiento():
                self.solicitar_almacenamiento()

# --- Función para visualizar el ecualizador ---
def iniciar_ecualizador():
    """
    Inicia una barra de ecualización gráfica que visualiza frecuencias de audio en tiempo real.
    """
    ventana = tk.Tk()
    ventana.title("Ecualizador")
    ventana.geometry("400x300")

    frame = tk.Frame(ventana, bg="-transparentcolor")
    frame.pack(fill=tk.BOTH, expand=True)

    barras = []
    colores = ["red", "green", "blue", "yellow"]
    for color in colores:
        barra = Scale(frame, from_=0, to=100, orient=tk.VERTICAL, bg="black", fg=color, troughcolor=color)
        barra.pack(side=tk.LEFT, padx=5)
        barras.append(barra)

    # Barras horizontales para control de audio y micrófono
    barra_mic = Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, bg="black", fg="white", troughcolor="gray")
    barra_mic.pack(side=tk.BOTTOM, padx=5)

    barra_audio = Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, bg="black", fg="white", troughcolor="gray")
    barra_audio.pack(side=tk.BOTTOM, padx=5)

    def actualizar_barras():
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while True:
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            fft_data = np.abs(np.fft.fft(data))[:CHUNK // 2]
            fft_data = fft_data / np.max(fft_data

# --- Función principal ejemplo ---
def main():
# Crear la instancia de Inés y ejecutar el proceso
    """
    Función principal que se encarga de iniciar las bases de datos y de capturar la imagen y audio
    del usuario (root o no root).
    """
    capturar_imagenes_usuario(root)
    init_db_user()
    init_db_root()
    init_db_root_calendario()
    root_user = input("¿Es este el usuario root? (si/no): ").lower() == "si"
    capturar_imagenes_usuario()
    ines = InesAI()
    ines.iniciar()
    iniciar_revision_eventos()






#-------- base de datos ---------
import sqlite3

# --- Función para crear las tablas predefinidas ---
def crear_tablas_predefinidas():
    """
    Crea las tablas necesarias en las bases de datos predefinidas.
    Esta función debe ejecutarse solo una vez al inicio.
    """
    # Definir las rutas de las bases de datos
    db_path_users = "Usuarios/base_de_datos_usuario/usuarios_general.db"
    db_path_root = "/root/.usuario_root_datos/base_de_datos_usuario/root.db"
    db_path_root_calendar = "/root/.usuario_root_datos/base_de_datos_usuario/root_calendario.db"
    db_path_root_calendar_ines = "/root/.usuario_root_datos/base_de_datos_usuario/Ines_calendario.db"
    
    # Crear conexiones
    conexion_users = sqlite3.connect(db_path_users)
    conexion_root = sqlite3.connect(db_path_root)
    conexion_root_calendar = sqlite3.connect(db_path_root_calendar)
    conexion_root_calendar_ines = sqlite3.connect(db_path_root_calendar_ines)

    try:
        # Crear cursor para cada conexión y ejecutar las consultas
        # --- Usuarios ---
        cursor_users = conexion_users.cursor()
        cursor_users.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Tipo TEXT NOT NULL,
                Direccion TEXT,
                Telefono TEXT,
                CorreoElectronico TEXT,
                NumeroEmergencia TEXT,
                PalabraSeguridad TEXT
            )
        """)
        cursor_users.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios_caracteristicas (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Tipo TEXT NOT NULL,
                ColorOjos TEXT,
                Cejas TEXT,
                Barba TEXT,
                Barba_color TEXT,  -- Para almacenar el color en formato hexadecimal
                BocaGrande TEXT,
                ColorRecuadro TEXT,
                AudioArchivo TEXT,
                Telefono TEXT,
                Direccion TEXT,
                CorreoElectronico TEXT
            )
        """)
        cursor_users.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios_existente (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Tipo TEXT NOT NULL,
                ColorOjos TEXT,
                Cejas TEXT,
                Barba TEXT,
                Barba_color TEXT,  -- Para almacenar el color en formato hexadecimal
                BocaGrande TEXT,
                ColorRecuadro TEXT,
                AudioArchivo TEXT,
                Telefono TEXT,
                Direccion TEXT,
                CorreoElectronico TEXT
            )
        """)

        # --- Root ---
        cursor_root = conexion_root.cursor()
        cursor_root.execute("""
            CREATE TABLE IF NOT EXISTS Root (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Direccion TEXT NOT NULL,
                NumeroTelefono TEXT NOT NULL,
                CorreoElectronico TEXT NOT NULL,
                NumeroEmergencia TEXT,
                PalabraSeguridad TEXT NOT NULL
            )
        """)

        # --- Calendario Root ---
        cursor_root_calendar = conexion_root_calendar.cursor()
        cursor_root_calendar.execute("""
            CREATE TABLE IF NOT EXISTS CalendarioRoot (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ZonaHoraria TEXT NOT NULL,
                Mes INTEGER NOT NULL,
                Dia INTEGER NOT NULL,
                Hora INTEGER NOT NULL,
                Minuto INTEGER NOT NULL,
                Segundo INTEGER NOT NULL
            )
        """)

        # --- Calendario Inés ---
        cursor_calendar_ines = conexion_root_calendar_ines.cursor()
        cursor_calendar_ines.execute("""
            CREATE TABLE IF NOT EXISTS CalendarioInes (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ZonaHoraria TEXT NOT NULL,
                Mes INTEGER NOT NULL,
                Dia INTEGER NOT NULL,
                Hora INTEGER NOT NULL,
                Minuto INTEGER NOT NULL,
                Segundo INTEGER NOT NULL
            )
        """)

        # Confirmar los cambios
        conexion_users.commit()
        conexion_root.commit()
        conexion_root_calendar.commit()
        conexion_root_calendar_ines.commit()

        print("Tablas predefinidas creadas correctamente.")

    except Exception as e:
        print(f"Error al crear tablas: {e}")

    finally:
        # Cerrar las conexiones
        conexion_users.close()
        conexion_root.close()
        conexion_root_calendar.close()
        conexion_root_calendar_ines.close()
        print("Conexiones cerradas tras la creación de tablas.")

def identificar_usuario():
    """
    Identifica al usuario registrado y saluda, o pide registrarse si no existe.
    """
    hablar("¿Cómo te llamas?")
    nombre_usuario = escuchar_comando()

    # Si el usuario es Inés, se maneja su flujo
    if "Inés" in nombre_usuario:
        hablar("Hola Inés, bienvenida. ¿Qué deseas hacer?")
        gestionar_calendario_ines()  # Manejar la parte del calendario de Inés
    # Si el usuario es Root, se maneja su flujo
    elif "Root" in nombre_usuario:
        hablar("Hola Root, bienvenido al sistema de administración.")
        gestionar_calendario_root()  # Manejar la parte del calendario de Root
    else:
        # Si no es Inés ni Root, se maneja el flujo de otros usuarios
        if comprobar_usuario_existente(nombre_usuario):
            hablar(f"¡Hola {nombre_usuario}! Bienvenido de nuevo.")
        else:
            hablar(f"Hola {nombre_usuario}, parece que no estás registrado. Procederemos a registrarte.")
            registrar_usuario(nombre_usuario)
            hablar(f"¡Bienvenido, {nombre_usuario}! Ahora estás registrado.")

def gestionar_calendario_root():
    """
    Función para gestionar el calendario de Root.
    """
    hablar("¿Qué deseas hacer con el calendario de Root? Puedes agregar, eliminar o consultar registros.")
    comando = escuchar_comando().lower()

    if "agregar" in comando:
        hablar("Por favor, dime el detalle del registro que deseas agregar.")
        registro = escuchar_comando()
        agregar_registro_root(registro)
    elif "eliminar" in comando:
        hablar("Dime el ID del registro que deseas eliminar.")
        id_registro = int(escuchar_comando())
        eliminar_datos_root_calendario(id_registro)
    elif "consultar" in comando:
        consultar_registros_root()
    else:
        hablar("No reconozco ese comando. Intenta de nuevo.")

def agregar_registro_root(registro):
    """
    Agrega un registro al calendario de Root.
    """
    cursor = conexion_root_calendar.cursor()
    cursor.execute("""
        INSERT INTO CalendarioRoot (Registro)
        VALUES (?)
    """, (registro,))
    conexion_root_calendar.commit()
    hablar(f"El registro '{registro}' ha sido agregado al calendario de Root

def consultar_registros_root_calendar():
    """
    Consulta y muestra los registros del calendario de Root.
    """
    cursor = conexion_root_calendar.cursor()
    cursor.execute("SELECT * FROM CalendarioRoot")
    registros = cursor.fetchall()
    for registro in registros:
        hablar(f"Registro: {registro}")
        
# --- Rutas de Bases de Datos ---
db_path_users = "Usuarios/base_de_datos_usuario/usuarios_general.db"
db_path_users = "Usuarios/base_de_datos_usuario/usuarios_general.db"
db_path_root = "/root/.usuario_root_datos/base_de_datos_usuario/root.db"
db_path_root_calendar = "/root/.usuario_root_datos/base_de_datos_usuario/root_calendario.db"
db_path_root_calendar_ines = "/root/.usuario_root_datos/base_de_datos_usuario/Ines_calendario.db"

# --- Funciones de Voz ---
def hablar(texto):
    """
    Convierte el texto en voz y lo reproduce.
    """
    tts = gTTS(text=texto, lang='es')
    tts.save("respuesta.mp3")
    os.system("mpg321 respuesta.mp3")  # Reproduce el archivo MP3 generado
    os.remove("respuesta.mp3")  # Elimina el archivo después de reproducirlo

def escuchar_comando():
    """
    Función para escuchar un comando del usuario.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
    
    try:
        comando = recognizer.recognize_google(audio, language='es-ES')
        print(f"Comando escuchado: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        print("No se entendió el comando.")
        return ""
    except sr.RequestError:
        print("Error al conectarse al servicio de Google.")
        return ""
        
def identificar_usuario():
    """
    Identifica al usuario registrado y saluda, o pide registrarse si no existe.
    """
    hablar("¿Cómo te llamas?")
    nombre_usuario = escuchar_comando()

    # Comprobar si el usuario existe en la base de datos
    if comprobar_usuario_existente(nombre_usuario):
        hablar(f"¡Hola {nombre_usuario}! Bienvenido de nuevo.")
        # Aquí el sistema puede realizar más interacciones dependiendo del comando
    else:
        hablar(f"Hola {nombre_usuario}, parece que no estás registrado. Procederemos a registrarte.")
        registrar_usuario(nombre_usuario)
        hablar(f"¡Bienvenido, {nombre_usuario}! Ahora estás registrado.")

def comprobar_usuario_existente(nombre_usuario):
    """
    Comprobar si el usuario existe en la base de datos de usuarios.
    """
    cursor = conexion_users.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE Nombre=?", (nombre_usuario,))
    resultado = cursor.fetchone()
    return resultado is not None

def registrar_usuario(nombre_usuario):
    """
    Función para registrar un nuevo usuario en la base de datos.
    """
    hablar(f"Por favor, proporciona los siguientes datos para completar tu registro.")
    tipo_usuario = escuchar_comando()
    telefono = escuchar_comando()
    email = escuchar_comando()
    direccion = escuchar_comando()
    
    cursor = conexion_users.cursor()
    cursor.execute("""
        INSERT INTO Usuarios (Nombre, Tipo, Telefono, Email, Direccion)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre_usuario, tipo_usuario, telefono, email, direccion))
    conexion_users.commit()
    hablar("Usuario registrado exitosamente.")

def hablar(texto):
    """
    Convierte el texto en voz y lo reproduce.
    """
    tts = gTTS(text=texto, lang='es')
    tts.save("respuesta.mp3")
    os.system("mpg321 respuesta.mp3")  # Reproduce el archivo MP3 generado
    os.remove("respuesta.mp3")  # Elimina el archivo después de reproducirlo

def hablar(texto):
    """
    Convierte el texto en voz y lo reproduce.
    """
    tts = gTTS(text=texto, lang='es')
    tts.save("respuesta.mp3")
    os.system("mpg321 respuesta.mp3")  # Reproduce el archivo MP3 generado
    os.remove("respuesta.mp3")  # Elimina el archivo después de reproducirlo

def eliminar_datos_ines_calendario(id_registro):
    """
    Elimina un registro específico de la base de datos de calendario de Inés después de confirmación.
    """
    global conexion_root_calendar_ines
    cursor = conexion_root_calendar_ines.cursor()

    # Verificar si el registro existe
    cursor.execute("SELECT * FROM CalendarioInes WHERE ID=?", (id_registro,))
    registro = cursor.fetchone()

    if registro:
        hablar(f"¿Estás seguro que quieres eliminar el registro con ID {id_registro} de la base de datos? Di 'sí' para confirmar o 'no' para cancelar.")
        
        # Esperamos la respuesta de Inés
        respuesta = input("Inés, ¿quieres eliminar este registro? (sí/no): ").lower()

        if respuesta == "sí":
            cursor.execute("DELETE FROM CalendarioInes WHERE ID=?", (id_registro,))
            conexion_root_calendar_ines.commit()
            hablar(f"Registro con ID {id_registro} eliminado correctamente.")
        elif respuesta == "no":
            hablar(f"La eliminación del registro con ID {id_registro} ha sido cancelada.")
        else:
            hablar("Respuesta no válida. La eliminación ha sido cancelada.")
    else:
        hablar(f"No se encontró un registro con ID {id_registro}.")
        
#------------------------------------------------------------------------------




import pyaudio
import wave
import os


# ines siempe esta a la escucha mii codigo ya hace la brabacion y compara si elarchivo escorrecto
def comparar_voz(archivo_audio1, archivo_audio2):
# --- Función para autenticar por voz ---
def autenticar_por_voz(audio_grabado, FORMAT, CHANNELS, RATE, CHUNK, duracion, frames):
    """
    Graba un audio para identificar al usuario.
    """
    audio = pyaudio.PyAudio()
    archivo_audio = "Identificacion_voz0.wav"

    # INICIAMOS GRABACIÓN
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    for i in range(0, int(RATE / CHUNK * duracion)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Grabación terminada")

    # DETENEMOS GRABACIÓN
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
    waveFile = wave.open(archivo_audio, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    global comparacion_audio
    
        if resultado_comparacion:
            print(f"Las voces coinciden.")
            return True
        else:
            print(f"Las voces no coinciden.")
            return False
    except Exception as e:
        print(f"Error al comparar los audios: {e}")
        return False
def buscar_voz_registrada(nombre_usuario, ruta_base="home/Usuarios/base_de_datos_usuario/usuarios_general.db"):
    """
    Verifica si el usuario ya tiene una grabación registrada.
    """
    ruta_usuario = os.path.join(ruta_base, nombre_usuario, "usuarios_general.db")
    
    if os.path.exists(ruta_usuario):
        archivos_audio = [f for f in os.listdir(ruta_usuario) if f.endswith(".wav")]
        if archivos_audio:
            print(f"Voces encontradas para {nombre_usuario}.")
            return True
    print(f"No se encontraron grabaciones para {nombre_usuario}.")
    return False

def autenticar_o_crear_usuario(nombre_usuario, duracion=3, formato="wav", canales=1, tasa_muestreo=16000, tamano_buffer=1024):
    """
    Función principal para autenticar un usuario o crear uno nuevo.
    """
    archivo_audio = grabar_audio(duracion, formato, canales, tasa_muestreo, tamano_buffer)

    if buscar_voz_registrada(nombre_usuario):
        print(f"Usuario {nombre_usuario} encontrado.")
        for archivo in os.listdir(f"home/Usuarios/{nombre_usuario}/voz"):
            if archivo.endswith(".wav"):
                archivo_comparar = os.path.join(f"home/Usuarios/{nombre_usuario}/voz", archivo)
                if comparar_voz(archivo_audio, archivo_comparar):
                    print(f"Autenticación exitosa: La voz corresponde al usuario {nombre_usuario}.")
                    # Eliminar archivo temporal
                    os.remove(archivo_audio)
                    return True
                    
    print(f"Usuario {nombre_usuario} no encontrado. Creando nuevo usuario...")
    guardar_nuevo_usuario(ruta_usuario, nombre_usuario, archivo_audio)
    return False

def determinar_y_guardar_tipo_voz(archivo_audio, nombre_bd, nombre_usuario, tipo_usuario):
    """
    Determina el tipo de voz (Grave, Normal, Aguda) y guarda esta información.
    """
    try:
        print(f"Analizando tipo de voz en archivo: {archivo_audio}...")
        _, data = wave.open(archivo_audio, 'rb').readframes(-1), wave.open(archivo_audio, 'rb').getnframes()
        frecuencia_promedio = np.mean(np.abs(np.frombuffer(data, dtype=np.int16)))

        if frecuencia_promedio < 150:
            tipo = "Grave"
        elif 150 <= frecuencia_promedio <= 300:
            tipo = "Normal"
        elif frecuencia_promedio > 300:
            tipo = "Aguda"
        else:
            tipo = "Indefinida"

        print(f"El tipo de voz es: {tipo}")

        global tipo de voz 
        global especmetria_numeriaca_voz

        # Aquí guardarías el tipo de voz en tu base de datos (nombre_bd)
        guardar_tipo_voz(ruta, nombre, nombre_bd, db_path_users, tipo_usuario, tipo, especmetria_numeriaca_voz)

        return tipo
    except Exception as e:
        print(f"Error al analizar el tipo de voz: {e}")
        return "Error"

def guardar_nuevo_usuario(nombre_usuario, archivo_audio, ruta_base):
    """
    Guarda la grabación de un nuevo usuario en el sistema.
    """
    
    ruta_usuario = os.path.join(ruta_base, nombre_usuario)
    
    if not os.path.exists(ruta_usuario):
        os.makedirs(ruta_usuario)
    
    ruta_voz = os.path.join(ruta_usuario, "voz")
    if not os.path.exists(ruta_voz):
        os.makedirs(ruta_voz)
    
    archivo_destino = os.path.join(ruta_voz, f"{nombre_usuario}_voz.wav")
    os.rename(archivo_audio, archivo_destino)
    print(f"Nuevo usuario {nombre_usuario} creado y voz guardada en {archivo_destino}.")
    
    return True