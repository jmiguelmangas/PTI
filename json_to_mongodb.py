import logging
import os
import json
import pymongo
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Ajusta la URL si utilizas un servidor diferente
db = client['air_quality_db']
collection = db['pm25_data']

# Directorio donde se encuentran los fragmentos JSON
json_dir = "json_fragments"

# Iterar sobre todos los archivos JSON en el directorio
def load_json_to_mongodb():
    try:
        if not os.path.exists(json_dir):
            raise Exception(f"Directory {json_dir} not found.")

        json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]
        total_files = len(json_files)

        for idx, filename in enumerate(json_files):
            file_path = os.path.join(json_dir, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                # Insertar los datos en la colección de MongoDB
                if isinstance(data, list):
                    collection.insert_many(data)
                else:
                    collection.insert_one(data)
            percentage = ((idx + 1) / total_files) * 100
            logger.info(f"Progress: {percentage:.2f}% - {filename} loaded into MongoDB successfully.")
    except Exception as e:
        logger.error(f"Error loading JSON files into MongoDB: {e}")

if __name__ == "__main__":
    load_json_to_mongodb()