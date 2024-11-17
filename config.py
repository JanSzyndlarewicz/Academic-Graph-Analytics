import logging

from dotenv import load_dotenv
import os

load_dotenv()

SEMANTIC_SCHOLAR_API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY')

SEMANTIC_SCHOLAR_HEADERS = {
    'x-api-key': SEMANTIC_SCHOLAR_API_KEY,
    'Accept': 'application/json'
}

SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/datasets/v1/"
SEMANTIC_SCHOLAR_DATASET_RELEASE_DATE = "2024-11-12"
SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME = "citations"
SEMANTIC_SCHOLAR_PAPER_IDS_DATASET_NAME = "paper-ids"
SEMANTIC_SCHOLAR_PAPERS_DATASET_NAME = "papers"

FILES_FOLDER_NAME = "files"
CITATIONS_DATASET_LINKS_STATUS_FILE_NAME = "citations_dataset_links_status.json"

# Logger configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

