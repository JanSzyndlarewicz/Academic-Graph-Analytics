import logging
import os

from config import CITATIONS_DATASET_LINKS_STATUS_FILE_NAME, FILES_FOLDER_NAME, SEMANTIC_SCHOLAR_DATASET_RELEASE_DATE
from data_retrival.download_status_handler import DownloadStatusHandler
from data_retrival.semantic_scholar.core import ScholarAPI
from data_retrival.semantic_scholar.utils import download_file, find_full_url, get_file_name_from_url, unpack_gz_file


class DatasetHandler:
    def __init__(self, dataset_name: str):
        self.logger = logging.getLogger(__name__)
        self.api = ScholarAPI()
        self.release_date = SEMANTIC_SCHOLAR_DATASET_RELEASE_DATE
        self.dataset_name = dataset_name
        self.files_dir = FILES_FOLDER_NAME
        self.download_dataset_handler = DownloadStatusHandler(
            os.path.join(self.files_dir, CITATIONS_DATASET_LINKS_STATUS_FILE_NAME)
        )
        os.makedirs(self.files_dir, exist_ok=True)

    def handle_url_download(self, url: str) -> str:
        citations_dir = os.path.join(self.files_dir, self.dataset_name)
        os.makedirs(citations_dir, exist_ok=True)
        file_path = os.path.join(citations_dir, get_file_name_from_url(url))
        self.logger.info(f"Downloading file from {url}")
        download_file(url, file_path)
        unpack_gz_file(file_path, file_path[:-3])
        os.remove(file_path)
        self.logger.info(f"File {file_path} has been downloaded")
        return file_path[:-3]

    def prepare_new_database(self):
        response = self.api.get_links_for_dataset(self.release_date, self.dataset_name)
        self.download_dataset_handler.prepare_new_db(response.get("files"))

    def get_authorized_url(self, base_url: str):
        result = self.api.get_links_for_dataset(self.release_date, self.dataset_name)
        urls = result.get("files")
        full_url = find_full_url(base_url, urls)
        return full_url
