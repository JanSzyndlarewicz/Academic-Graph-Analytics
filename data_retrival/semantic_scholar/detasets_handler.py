from config import SEMANTIC_SCHOLAR_DATASETS_BASE_URL
from data_retrival.semantic_scholar.abstract import APIClient


class DatasetsScholarAPI(APIClient):
    def __init__(self):
        super().__init__()
        self.base_url += SEMANTIC_SCHOLAR_DATASETS_BASE_URL
