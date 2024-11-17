import json
import logging
import os

import requests

from config import SEMANTIC_SCHOLAR_HEADERS, SEMANTIC_SCHOLAR_BASE_URL, FILES_FOLDER_NAME


class ScholarAPI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = SEMANTIC_SCHOLAR_BASE_URL
        self.headers = SEMANTIC_SCHOLAR_HEADERS
        self.files_dir = FILES_FOLDER_NAME
        os.makedirs(self.files_dir, exist_ok=True)

    def get_available_releases(self) -> dict:
        url = f"{self.base_url}releases"
        self.logger.info("Retrieving available releases")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            with open(os.path.join(self.files_dir, 'releases.json'), 'w') as file:
                json.dump(data, file, indent=4)
            return data
        else:
            self.logger.info("Failed to retrieve data:", response.status_code)
            raise RuntimeError(f"Failed to retrieve data: {response.status_code}")

    def get_datasets_listing(self, release_date: str) -> dict:
        url = f"{self.base_url}release/{release_date}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            with open(os.path.join(self.files_dir, 'datasets.json'), 'w') as file:
                json.dump(data, file, indent=4)
            return data
        else:
            self.logger.info("Failed to retrieve data:", response.status_code)
            raise RuntimeError(f"Failed to retrieve data: {response.status_code}")

    def get_links_for_dataset(self, release_date: str, dataset_name: str) -> dict:
        url = f"{self.base_url}release/{release_date}/dataset/{dataset_name}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            with open(os.path.join(self.files_dir, 'links.json'), 'w') as file:
                json.dump(data, file, indent=4)
            return data
        else:
            self.logger.info("Failed to retrieve data:", response.status_code)
            raise RuntimeError(f"Failed to retrieve data: {response.status_code}")