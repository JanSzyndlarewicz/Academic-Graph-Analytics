import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Semantic Scholar configuration
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
SEMANTIC_SCHOLAR_HEADERS = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY, "Accept": "application/json"}
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/"
SEMANTIC_SCHOLAR_DATASETS_BASE_URL = "datasets/v1/"
SEMANTIC_SCHOLAR_PAPERS_BASE_URL = "graph/v1/paper/"
SEMANTIC_SCHOLAR_DATASET_RELEASE_DATE = "2024-11-12"
SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME = "citations"
SEMANTIC_SCHOLAR_PAPER_IDS_DATASET_NAME = "paper-ids"
SEMANTIC_SCHOLAR_PAPERS_DATASET_NAME = "papers"

# Data configuration
DATA_FOLDER_NAME = "data"

# Neo4j configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

NEO4J_BATCH_SIZE = 1000
NEO4J_MAX_WORKERS = 1
NEO4J_MAX_TRANSACTION_RETRY_TIME = 10

# Logger configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
