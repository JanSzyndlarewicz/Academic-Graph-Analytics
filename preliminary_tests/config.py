import os
from dotenv import load_dotenv

load_dotenv()

SCOPUS_KEY = os.getenv('SCOPUS_KEY')
PAPER_SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'
SAFETY_LIMIT = 50