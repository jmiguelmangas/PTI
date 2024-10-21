# Air Quality API

This repository contains a REST API that allows adding, updating, deleting, and filtering air quality data, as well as calculating basic statistics of the dataset stored in a MongoDB database.

## Requirements

- Docker
- Docker Compose
- Python 3.10 (optional if running locally)
- MongoDB (local or in Docker)

## Instructions to Run the API

### 1. Clone the Repository
```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_NAME>
```

### 2. Transform the Data from .nc to JSON
The `.nc` file contains air quality data that needs to be transformed into a JSON format so that it can be inserted into the MongoDB database. Use the `install_database.py` script to perform this transformation and load the data into MongoDB in two steps.

```bash
python split_dataset_to_json.py
python json_to_mongodb.py
```

Make sure MongoDB is running before executing the script.

### 3. Run with Docker

#### a. Build and Run the Containers
Run the following command to build and start the services defined in `docker-compose.yml`.
```bash
docker-compose up --build
```
This command will start the container for the air quality API (`air_quality_api`) and the MongoDB database.

#### b. Verify Connection to MongoDB
Make sure MongoDB is running correctly and the connection has been successfully established before using the API.

### 4. Run Locally (Optional)
If you want to run the API locally without Docker, install the dependencies and run the server:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

1. **GET /**: Shows a welcome message.
   - **URL**: `/`
   - **Method**: `GET`

2. **POST /data**: Adds a new air quality data entry.
   - **URL**: `/data`
   - **Method**: `POST`
   - **Parameters**: `latitude`, `longitude`, `pm25`

3. **GET /data/{id}**: Retrieves a data entry by its ID.
   - **URL**: `/data/{id}`
   - **Method**: `GET`

4. **PUT /data/{id}**: Updates an existing data entry.
   - **URL**: `/data/{id}`
   - **Method**: `PUT`
   - **Parameters**: `latitude` (optional), `longitude` (optional), `pm25` (optional)

5. **DELETE /data/{id}**: Deletes a data entry by its ID.
   - **URL**: `/data/{id}`
   - **Method**: `DELETE`

6. **GET /filter_data/**: Filters the data by specific parameters.
   - **URL**: `/filter_data/`
   - **Method**: `GET`
   - **Parameters**: `latitude` (optional), `longitude` (optional), `limit` (optional, default 100)

7. **GET /statistics/**: Retrieves statistics of the dataset.
   - **URL**: `/statistics/`
   - **Method**: `GET`

## Testing
The `test_main.py` file contains automated tests for the API endpoints. To run the tests, use `pytest`.

```bash
pytest test_main.py
```

## Additional Notes
- The `.gitignore` file has been configured to ignore generated JSON fragments (`data/json-fragments/`).
- Make sure the MongoDB database is running before using the API or running tests.
