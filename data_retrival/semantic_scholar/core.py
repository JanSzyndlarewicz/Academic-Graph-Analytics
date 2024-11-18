from data_retrival.semantic_scholar.abstract import APIClient


class ScholarAPI(APIClient):
    def __init__(self):
        super().__init__()

    def get_available_releases(self) -> dict:
        return self.fetch_data("releases", "releases.json")

    def get_datasets_listing(self, release_date: str) -> dict:
        return self.fetch_data(f"release/{release_date}", "datasets.json")

    def get_links_for_dataset(self, release_date: str, dataset_name: str) -> dict:
        return self.fetch_data(f"release/{release_date}/dataset/{dataset_name}", "links.json")
