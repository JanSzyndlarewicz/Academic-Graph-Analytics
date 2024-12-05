from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class SemanticScholarCitationsBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            if data.get("base") and data.get("resource"):
                base_doi = data["base"]
                citation_doi = data["resource"]

                base_result = tx.run("MATCH (base:Paper {id: $base_doi}) RETURN base", base_doi=base_doi)
                if base_result.single():
                    cited_result = tx.run(
                        "MATCH (cited:Paper {id: $citation_doi}) RETURN cited", citation_doi=citation_doi
                    )
                    if cited_result.single():
                        tx.run(
                            """
                            MATCH (base:Paper {id: $base_doi})
                            MATCH (cited:Paper {id: $citation_doi})
                            MERGE (base)-[:CITES]->(cited)
                            """,
                            base_doi=base_doi,
                            citation_doi=citation_doi,
                        )
