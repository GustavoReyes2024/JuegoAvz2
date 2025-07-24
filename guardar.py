import json
import os
from datetime import datetime

SAVES_DIR = "saves" # El nombre de nuestra carpeta de guardado

def save_game(data):
    """
    Guarda el estado del juego en un nuevo archivo JSON con una marca de tiempo.
    
    Args:
        data (dict): Un diccionario que contiene el estado del juego a guardar.
    """
    # 1. Asegura que la carpeta 'saves' exista
    try:
        if not os.path.exists(SAVES_DIR):
            os.makedirs(SAVES_DIR)
    except OSError as e:
        print(f"Error al crear la carpeta de guardado '{SAVES_DIR}': {e}")
        return

    # 2. Crea un nombre de archivo único con la fecha y hora actual
    # Usamos la hora actual de Honduras si es relevante, o simplemente la local.
    # Dado que `datetime.now()` ya usa la hora local del sistema donde se ejecuta, esto es suficiente.
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"save_{timestamp}.json"
    filepath = os.path.join(SAVES_DIR, filename)

    # 3. Guarda los datos en el nuevo archivo
    try:
        with open(filepath, 'w', encoding='utf-8') as f: # Añadir encoding='utf-8' para compatibilidad con caracteres especiales
            json.dump(data, f, indent=4) # indent=4 para una mejor legibilidad del JSON
        print(f"Partida guardada con éxito en: {filepath}")
    except IOError as e:
        print(f"Error de E/S al guardar la partida en '{filepath}': {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al guardar la partida: {e}")

def load_game(filename):
    """
    Carga una partida específica desde la carpeta 'saves'.
    
    Args:
        filename (str): El nombre del archivo de guardado (ej. "save_YYYY-MM-DD_HH-MM-SS.json").
        
    Returns:
        dict or None: Un diccionario con los datos del juego si la carga fue exitosa, None en caso contrario.
    """
    filepath = os.path.join(SAVES_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"Error: No se encontró el archivo de guardado '{filename}'.")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f: # Añadir encoding='utf-8'
            data = json.load(f)
            print(f"Partida '{filename}' cargada con éxito.")
            return data
    except json.JSONDecodeError as e:
        print(f"Error de formato JSON al cargar la partida '{filename}': {e}")
        return None
    except IOError as e:
        print(f"Error de E/S al cargar la partida de '{filepath}': {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar la partida '{filename}': {e}")
        return None

def get_saved_games():
    """
    Devuelve una lista de todos los archivos de partidas guardadas en la carpeta 'saves',
    ordenadas de la más reciente a la más antigua.
    
    Returns:
        list: Una lista de nombres de archivo de las partidas guardadas.
    """
    if not os.path.exists(SAVES_DIR):
        return [] # Devuelve una lista vacía si no existe la carpeta de guardado

    try:
        # Obtiene todos los archivos .json de la carpeta de guardado
        files = [f for f in os.listdir(SAVES_DIR) if f.endswith(".json")]
        
        # Filtra para asegurar que solo sean archivos (no subdirectorios) y ordena por fecha de modificación
        # Usamos un try-except dentro del lambda para manejar posibles errores si un archivo se corrompe o no se puede acceder
        def get_mtime(f_name):
            try:
                return os.path.getmtime(os.path.join(SAVES_DIR, f_name))
            except Exception:
                return 0 # Si hay un error, lo pone al principio (más antiguo) para no romper la lista
        
        files.sort(key=get_mtime, reverse=True) # El más nuevo primero
        
        return files
    except Exception as e:
        print(f"Error al obtener la lista de partidas guardadas: {e}")
        return []