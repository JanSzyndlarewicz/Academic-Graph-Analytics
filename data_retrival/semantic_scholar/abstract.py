import json
import logging
import os

import requests

from config import FILES_FOLDER_NAME, SEMANTIC_SCHOLAR_BASE_URL, SEMANTIC_SCHOLAR_HEADERS


class APIClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = SEMANTIC_SCHOLAR_BASE_URL
        self.headers = SEMANTIC_SCHOLAR_HEADERS
        self.files_dir = FILES_FOLDER_NAME
        os.makedirs(self.files_dir, exist_ok=True)

    def fetch_data(self, endpoint: str, output_filename: str = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"Retrieving data from {url}")
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            if output_filename:
                file_path = os.path.join(self.files_dir, output_filename)
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
                self.logger.info(f"Data saved to {file_path}")
            return data
        else:
            self.logger.error(f"Failed to retrieve data from {url}: {response.status_code}")
            raise RuntimeError(f"Failed to retrieve data: {response.status_code}")
