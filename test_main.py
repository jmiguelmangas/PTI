import pytest
from fastapi.testclient import TestClient
from main import app
from pydantic import BaseModel

client = TestClient(app)

# Modelo de datos para agregar datos
class AirQualityData(BaseModel):
    latitude: float
    longitude: float
    pm25: float

# Test para el endpoint raíz
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Air Quality API with MongoDB"}

# Test para agregar nuevos datos
def test_add_data():
    data = AirQualityData(latitude=40.7128, longitude=-74.0060, pm25=12.5)
    response = client.post("/data", json=data.dict())
    assert response.status_code == 200
    assert "id" in response.json()
    return response.json()["id"]

# Test para obtener datos por ID
def test_get_data_by_id():
    new_id = test_add_data()  # Agregar un nuevo dato y obtener el ID
    response = client.get(f"/data/{new_id}")
    assert response.status_code == 200

# Test para actualizar un dato existente
def test_update_data():
    new_id = test_add_data()  # Agregar un nuevo dato y obtener el ID
    response = client.put(f"/data/{new_id}", json={"latitude": 41.0000, "longitude": -73.0000, "pm25": 15.0})
    assert response.status_code == 200

# Test para eliminar un dato
def test_delete_data():
    new_id = test_add_data()  # Agregar un nuevo dato y obtener el ID
    response = client.delete(f"/data/{new_id}")
    assert response.status_code == 200

# Test para filtrar datos
def test_filter_data():
    test_add_data()  # Asegurarse de que haya datos disponibles para filtrar
    response = client.get("/data/filter?latitude=40.7128&longitude=-74.0060")
    assert response.status_code == 200

# Test para obtener estadísticas
def test_get_statistics():
    test_add_data()  # Asegurarse de que haya datos disponibles para estadísticas
    response = client.get("/data/stats")
    assert response.status_code == 200
