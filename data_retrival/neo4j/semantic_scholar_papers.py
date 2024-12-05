from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class ScopusPapersBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            doi = data.get("DOI")
            if not doi:
                continue
            if "DOI" in data:
                tx.run(
                    """
                    MERGE (paper:Paper {id: $doi})
                    SET paper.publication_date = COALESCE($publication_date, paper.publication_date),
                        paper.countries = COALESCE($countries, paper.countries),
                        paper.universities = COALESCE($universities, paper.universities),
                        paper.cities = COALESCE($cities, paper.cities),
                        paper.field = COALESCE($field, paper.field)
                    """,
                    doi=data["DOI"],
                    publication_date=data.get("publication_date"),
                    countries=data.get("countries", []),
                    universities=data.get("universities", []),
                    cities=data.get("cities", []),
                    field=data.get("field", "Unknown"),
                )


