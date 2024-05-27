import pyttsx3
import mysql.connector
import time
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import logging

# Carga las variables de entorno
load_dotenv()

# Configuración del logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("notificaciones.log"),
                        logging.StreamHandler()
                    ])

def read_text_aloud(text):
    try:
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 50)
        volume = engine.getProperty('volume')
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        logging.info(f"Leyendo texto: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error(f"Error al leer el texto en voz alta: {e}")

def get_new_records(last_checked):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST_DOCKER"),
            user=os.getenv("DB_USER_DOCKER"),
            password=os.getenv("DB_PASS_DOCKER"),
            database=os.getenv("DB_NAME_DOCKER")
        )
        cursor = conn.cursor()

        # Carga la consulta desde la variable de entorno
        query = os.getenv("QUERY")
        cursor.execute(query, (last_checked,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        logging.info(f"Encontrados {len(results)} nuevos registros")
        return results
    except mysql.connector.Error as err:
        logging.error(f"Error al conectar a la base de datos: {err}")
        return []
    except Exception as e:
        logging.error(f"Error al obtener registros: {e}")
        return []

if __name__ == "__main__":
    last_checked = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    logging.info("Iniciando el monitor de nuevos registros")
    while True:
        try:
            new_records = get_new_records(last_checked)
            if new_records:
                for record in new_records:
                    id, contenido, fechaInsert = record
                    read_text_aloud(contenido)
                    last_checked = max(last_checked, fechaInsert.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(10)  # Espera 10 segundos antes de verificar nuevamente
        except Exception as e:
            logging.error(f"Error en el bucle principal: {e}")
