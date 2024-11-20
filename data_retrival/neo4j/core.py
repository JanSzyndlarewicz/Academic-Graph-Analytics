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


class AbstractNeo4jBatchProcessor(ABC):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), max_transaction_retry_time=NEO4J_MAX_TRANSACTION_RETRY_TIME
        )
        self.batch_size = NEO4J_BATCH_SIZE * NEO4J_MAX_WORKERS
        self.max_workers = NEO4J_MAX_WORKERS
        self.total_processed = 0

    def close(self):
        self.driver.close()

    @abstractmethod
    def process_batch(self, tx, batch):
        raise NotImplementedError

    def process_json(self, json_file_path: str) -> None:
        self.logger.info(f"Opening file: {json_file_path}")

        current_batch = []
        batch_count = 0

        with open(json_file_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                current_batch.append(data)

                if len(current_batch) >= self.batch_size:
                    self._process_batch(current_batch)
                    batch_count += 1
                    current_batch.clear()

            if current_batch:
                self._process_batch(current_batch)
                batch_count += 1

        self.logger.info(f"Processed {batch_count} batches and {self.total_processed} rows in total.")

    def _process_batch(self, batch: list) -> None:
        batches = self._split_batch_into_sub_batches(batch)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_in_thread, sub_batch) for sub_batch in batches]

            for future in futures:
                future.result()

        self.total_processed += len(batch)
        if self.total_processed % 100000 == 0:
            self.logger.info(f"Processed {self.total_processed} rows so far.")

    def _split_batch_into_sub_batches(self, batch: list) -> list:
        sub_batch_size = len(batch) // self.max_workers
        return [batch[i : i + sub_batch_size] for i in range(0, len(batch), sub_batch_size)]

    def _process_in_thread(self, sub_batch: list) -> None:
        with self.driver.session() as session:
            session.execute_write(self.process_batch, sub_batch)
