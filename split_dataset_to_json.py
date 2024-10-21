import logging
import pandas as pd
import netCDF4
import numpy as np
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to split dataset into JSON fragments
def split_dataset_to_json():
    try:
        dataset_path = "2000.nc"
        output_dir = "json_fragments"
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"Dataset path: {dataset_path}")
        nc = netCDF4.Dataset(dataset_path, mode='r')
        logger.info("Dataset opened successfully.")
        
        
        latitudes = nc.variables['lat'][:]
        longitudes = nc.variables['lon'][:]
        pm25_levels = nc.variables['GWRPM25'][:]

        data = {
            'latitude': [],
            'longitude': [],
            'pm25': []
        }

        logger.info("Starting to iterate over latitudes and longitudes to extract data.")
        
        for i in range(len(latitudes)):
            for j in range(len(longitudes)):
                pm25 = pm25_levels[i, j]
                if not np.isnan(pm25):
                    data['latitude'].append(latitudes[i])
                    data['longitude'].append(longitudes[j])
                    data['pm25'].append(pm25)
        logger.info("Data extraction completed.")

        df = pd.DataFrame(data)
        logger.info("Data loaded into DataFrame.")
        
        # Dividing the df in chunks
        chunk_size = 10000  # Tamaño del fragmento
        num_chunks = len(df) // chunk_size + 1

        # creating the index file
        index_data = []

        logger.info("Starting to split the DataFrame into fragments.")
        for i in range(num_chunks):
            try:
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, len(df))
                fragment = df[start_idx:end_idx]
                fragment_file = f"{output_dir}/fragment_{i}.json"
                
                # Saving the chunk as a Json File
                fragment.to_json(fragment_file, orient='records', indent=2)
                logger.info(f"Fragment {i} saved to {fragment_file}.")

                # Adding info to the index file
                index_data.append({
                    'fragment': fragment_file,
                    'start_idx': start_idx,
                    'end_idx': end_idx
                })

            except Exception as e:
                logger.error(f"Error while processing fragment {i}: {e}")

        # Saving the index as a Json File
        try:
            index_file_path = f"{output_dir}/index.json"
            with open(index_file_path, 'w') as index_file:
                json.dump(index_data, index_file, indent=2)
            logger.info(f"Index file saved to {index_file_path}.")
        except Exception as e:
            logger.error(f"Error while saving index file: {e}")

    except Exception as e:
        logger.error(f"Error during dataset splitting: {e}")

if __name__ == "__main__":
    split_dataset_to_json()
