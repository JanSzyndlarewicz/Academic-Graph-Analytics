import logging
import os

from config import DATA_FOLDER_NAME, SEMANTIC_SCHOLAR_DATASET_RELEASE_DATE
from data_retrival.download_status_handler import DownloadStatusHandler
from data_retrival.semantic_scholar.core import ScholarAPI
from data_retrival.utils import download_file, find_full_url, get_base_url, get_file_name_from_url, unpack_gz_file


class DatasetHandler:
    def __init__(self, dataset_name: str):
        self.logger = logging.getLogger(__name__)
        self.api = ScholarAPI()
        self.release_date = SEMANTIC_SCHOLAR_DATASET_RELEASE_DATE
        self.dataset_name = dataset_name
        self.download_dataset_handler = DownloadStatusHandler(
            os.path.join(DATA_FOLDER_NAME, f"{dataset_name}_dataset_links_status.json")
        )
        os.makedirs(DATA_FOLDER_NAME, exist_ok=True)

    def pull_batch_from_url(self, url: str) -> str:
        dataset_storage_path = os.path.join(DATA_FOLDER_NAME, self.dataset_name)
        os.makedirs(dataset_storage_path, exist_ok=True)
        batch_path = os.path.join(dataset_storage_path, get_file_name_from_url(url))
        self.logger.info(f"Downloading file from {url}")
        download_file(url, batch_path)
        unpack_gz_file(batch_path, batch_path[:-3])
        os.remove(batch_path)
        self.logger.info(f"File {batch_path} has been downloaded")
        return batch_path[:-3]

    def prepare_new_database(self, overwrite: bool = False) -> None:
        if not overwrite and self.download_dataset_handler.db_exists():
            self.logger.info("Database already exists and overwrite is set to False. Skipping creation.")
            return

        response = self.api.get_links_for_dataset(self.release_date, self.dataset_name)
        base_urls = [get_base_url(link) for link in response.get("files")]
        self.download_dataset_handler.prepare_new_db(base_urls)

    def get_authorized_url(self, base_url: str) -> str:
        result = self.api.get_links_for_dataset(self.release_date, self.dataset_name)
        urls = result.get("files")
        return find_full_url(base_url, urls)
