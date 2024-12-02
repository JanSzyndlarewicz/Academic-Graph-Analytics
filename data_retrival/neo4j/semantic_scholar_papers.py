from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class SemanticScholarPapersBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            if data.get("DOI"):
                tx.run(
                    """
                    MERGE (paper:Paper {DOI: $doi})
                    SET paper.affiliations = $affiliations,
                        paper.publication_date = $publication_date
                """,
                    doi=data["DOI"],
                    affiliations=data["affiliations"],
                    publication_date=data["publication_date"],
                )
