import logging
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pymongo
import os
from bson import ObjectId

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar la conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    logger.info("MongoDB connected successfully.")
except pymongo.errors.ServerSelectionTimeoutError as e:
    logger.error(f"Could not connect to MongoDB: {e}")
    client = None

db = client["air_quality_db"] if client is not None else None
collection = db["pm25_data"] if db is not None else None

# Crear la aplicación FastAPI
app = FastAPI()

@app.on_event("startup")
def startup_event():
    if client is None or db is None or collection is None:
        logger.error("MongoDB is not properly configured or connected.")

@app.get("/")
def read_root():
    return {"message": "Welcome to Air Quality API"}

@app.get("/data/{id}")
def get_data_by_id(id: str):
    try:
        logger.info(f"Request received for data ID: {id}")
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
        data = collection.find_one({"_id": ObjectId(id)}) if collection is not None else None
        if data is None:
            logger.error("Item not found in the database.")
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Data found for ID: {id}")
        data["_id"] = str(data["_id"])
        return data
    except Exception as e:
        logger.error(f"Error retrieving data by ID: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while retrieving data.")

@app.post("/data")
def add_data(latitude: float, longitude: float, pm25: float):
    try:
        logger.info(f"Request received to add data: latitude={latitude}, longitude={longitude}, pm25={pm25}")
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        new_entry = {"latitude": latitude, "longitude": longitude, "pm25": pm25}
        result = collection.insert_one(new_entry)
        logger.info("New data added successfully.")
        return {"message": "Data added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error adding data: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while adding data.")

@app.put("/data/{id}")
def update_data(id: str, latitude: float = None, longitude: float = None, pm25: float = None):
    try:
        logger.info(f"Request received to update data ID: {id}")
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        update_fields = {}
        if latitude is not None:
            update_fields["latitude"] = latitude
        if longitude is not None:
            update_fields["longitude"] = longitude
        if pm25 is not None:
            update_fields["pm25"] = pm25
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
        if result.matched_count == 0:
            logger.error("Item not found for update.")
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info("Data updated successfully.")
        return {"message": "Data updated successfully"}
    except Exception as e:
        logger.error(f"Error updating data: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while updating data.")

@app.delete("/data/{id}")
def delete_data(id: str):
    try:
        logger.info(f"Request received to delete data ID: {id}")
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        result = collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            logger.error("Item not found for deletion.")
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info("Data deleted successfully.")
        return {"message": "Data deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting data: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while deleting data.")

@app.get("/data/filter")
def filter_data(latitude: float = Query(None), longitude: float = Query(None), limit: int = 100):
    try:
        logger.info(f"Request received to filter data: latitude={latitude}, longitude={longitude}")
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        query = {}
        if latitude is not None:
            query["latitude"] = latitude
        if longitude is not None:
            query["longitude"] = longitude
        cursor = collection.find(query).limit(limit)
        results = [{"_id": str(item["_id"]), "latitude": item["latitude"], "longitude": item["longitude"], "pm25": item["pm25"]} for item in cursor]
        if not results:
            logger.error("No data found with the given filters.")
            raise HTTPException(status_code=404, detail="No data found with the given filters")
        logger.info("Filter operation completed successfully.")
        return results
    except Exception as e:
        logger.error(f"Error retrieving filtered data: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while filtering data.")

@app.get("/data/stats")
def get_statistics():
    try:
        logger.info("Request received to get dataset statistics.")
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        count = collection.count_documents({})
        if count == 0:
            logger.error("Dataset not available for statistics.")
            raise HTTPException(status_code=404, detail="Dataset not available")
        avg_pm25 = collection.aggregate([{ "$group": { "_id": None, "avg_pm25": { "$avg": "$pm25" }, "min_pm25": { "$min": "$pm25" }, "max_pm25": { "$max": "$pm25" }}}])
        stats = next(avg_pm25, None)
        if stats is None:
            raise HTTPException(status_code=404, detail="Statistics could not be calculated")
        logger.info("Statistics calculated successfully.")
        return {
            "count": count,
            "mean_pm25": stats["avg_pm25"],
            "min_pm25": stats["min_pm25"],
            "max_pm25": stats["max_pm25"]
        }
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while retrieving statistics.")