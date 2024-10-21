import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test para el endpoint de la raiz

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Air Quality API"}

# Test para agregar un nuevo dato

def test_add_data():
    response = client.post("/data", params={"latitude": 40.7128, "longitude": -74.0060, "pm25": 12.5})
    assert response.status_code == 200
    assert "id" in response.json()

# Test para obtener un dato por ID (debe proporcionar un ID valido)

def test_get_data_by_id():
    test_id = "6714e8144c8f4f6755659ca8"  # Ejemplo de ID
    response = client.get(f"/data/{test_id}")
    if response.status_code == 200:
        assert "latitude" in response.json()
        assert "longitude" in response.json()
        assert "pm25" in response.json()
    else:
        assert response.status_code == 404

# Test para actualizar un dato existente

def test_update_data():
    test_id = "6714e8144c8f4f6755659ca8"  # Ejemplo de ID
    response = client.put(f"/data/{test_id}", params={"latitude": 41.0})
    if response.status_code == 200:
        assert response.json() == {"message": "Data updated successfully"}
    else:
        assert response.status_code == 404

# Test para eliminar un dato

def test_delete_data():
    test_id = "6714e8144c8f4f6755659ca8"  # Ejemplo de ID
    response = client.delete(f"/data/{test_id}")
    if response.status_code == 200:
        assert response.json() == {"message": "Data deleted successfully"}
    else:
        assert response.status_code == 404

# Test para filtrar datos

def test_filter_data():
    response = client.get("/filter_data/", params={"latitude": 40.7128, "limit": 5})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test para obtener las estadisticas del dataset

def test_get_statistics():
    response = client.get("/statistics/")
    if response.status_code == 200:
        assert "count" in response.json()
        assert "mean_pm25" in response.json()
        assert "min_pm25" in response.json()
        assert "max_pm25" in response.json()
    else:
        assert response.status_code == 404
