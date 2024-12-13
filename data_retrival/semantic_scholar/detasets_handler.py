from config import SEMANTIC_SCHOLAR_DATASETS_BASE_URL
from data_retrival.semantic_scholar.abstract import ScholarAPIClient


class DatasetsScholarScholarAPI(ScholarAPIClient):
    def __init__(self):
        super().__init__()
        self.base_url += SEMANTIC_SCHOLAR_DATASETS_BASE_URL

    def get_available_releases(self) -> dict:
        return self.fetch_data("releases", "releases.json")

    def get_datasets_listing(self, release_date: str) -> dict:
        return self.fetch_data(f"release/{release_date}", "datasets.json")

    def get_links_for_dataset(self, release_date: str, dataset_name: str) -> dict:
        return self.fetch_data(f"release/{release_date}/dataset/{dataset_name}", "links.json")
