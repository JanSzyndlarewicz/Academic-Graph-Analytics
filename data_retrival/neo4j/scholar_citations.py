from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class SemanticScholarCitationsBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            if data.get("DOI") and data.get("citations"):
                base_doi = data["DOI"]
                base_result = tx.run("MATCH (base:Paper {DOI: $base_doi}) RETURN base", base_doi=base_doi)
                if base_result.single():
                    for citation in data["citations"]:
                        if citation:
                            cited_result = tx.run(
                                "MATCH (cited:Paper {DOI: $citation_doi}) RETURN cited", citation_doi=citation
                            )
                            if cited_result.single():
                                tx.run(
                                    """
                                    MATCH (base:Paper {DOI: $base_doi})
                                    MATCH (cited:Paper {DOI: $citation_doi})
                                    MERGE (base)-[:CITES]->(cited)
                                    """,
                                    base_doi=base_doi,
                                    citation_doi=citation,
                                )
