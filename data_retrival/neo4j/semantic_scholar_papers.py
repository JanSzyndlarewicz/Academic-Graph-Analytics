from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class ScopusPapersBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            doi = data.get("DOI")
            if not doi:
                continue

            tx.run(
                """
                MERGE (paper:Paper {id: $doi})
                SET paper.publication_date = COALESCE($publication_date, paper.publication_date),
                    paper.countries = 
                        CASE 
                            WHEN paper.countries IS NULL 
                                THEN $countries
                            ELSE 
                                [country IN $countries WHERE NOT country IN paper.countries] + paper.countries
                        END,
                    paper.universities = 
                        CASE 
                            WHEN paper.universities IS NULL 
                                THEN $universities
                            ELSE 
                                [university IN $universities WHERE NOT university IN paper.universities] + paper.universities
                        END,
                    paper.field = COALESCE($field, paper.field)
                """,
                doi=data["DOI"],
                publication_date=data.get("publication_date"),
                countries=data.get("countries", []),
                universities=data.get("universities", []),
                field=data.get("field", "Unknown"),
            )
