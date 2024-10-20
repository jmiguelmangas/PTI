import pymongo
import os
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar la conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = pymongo.MongoClient(MONGO_URI)
db = client["air_quality_db"]
collection = db["pm25_data"]

def create_indexes():
    try:
        # Crear índices en los campos latitude y longitude para mejorar la búsqueda
        start_time = time.time()
        logger.info("Starting to create index on 'latitude'.")
        collection.create_index([("latitude", pymongo.ASCENDING)], background=True)
        logger.info("Index on 'latitude' created.")
        
        logger.info("Starting to create index on 'longitude'.")
        collection.create_index([("longitude", pymongo.ASCENDING)], background=True)
        logger.info("Index on 'longitude' created.")
        
        end_time = time.time()
        logger.info(f"Indexes created for 'latitude' and 'longitude' in {end_time - start_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

if __name__ == "__main__":
    create_indexes()
