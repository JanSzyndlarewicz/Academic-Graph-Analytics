import json
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from neo4j import GraphDatabase

from config import (
    NEO4J_BATCH_SIZE,
    NEO4J_MAX_TRANSACTION_RETRY_TIME,
    NEO4J_MAX_WORKERS,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
)

class Neo4JConnector(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), max_transaction_retry_time=NEO4J_MAX_TRANSACTION_RETRY_TIME
        )
        self.batch_size = NEO4J_BATCH_SIZE * NEO4J_MAX_WORKERS
        self.max_workers = NEO4J_MAX_WORKERS
        self.total_processed = 0

    def __del__(self):
        self.close()
        
    def close(self):
        self.driver.close()
        
    def log_rows(self, batch_len):
        self.total_processed += batch_len
        if self.total_processed % 1000 == 0:
            self.logger.info(f"Processed {self.total_processed} rows so far.")
            
    def run_query(self, query, parameters={}):
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query, parameters=parameters)
                result = [record.data() for record in result]
                return result
            
    @staticmethod
    def run_query_static(query, parameters={}):
        driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), max_transaction_retry_time=NEO4J_MAX_TRANSACTION_RETRY_TIME
        )
        with driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query, parameters=parameters)
                result = [record.data() for record in result]
                return result
        driver.close()

        