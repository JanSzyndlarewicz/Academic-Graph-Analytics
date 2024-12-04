from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class ScopusPapersBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            if data.get("DOI"):
                tx.run(
                    """
                    MERGE (paper:Paper {id: $doi})
                    SET paper.publication_date = $publication_date,
                        paper.countries = $countries,
                        paper.universities = $universities,
                        paper.cities = $cities,
                        paper.field = $field
                    """,
                    doi=data["DOI"],
                    publication_date=data.get("publication_date"),
                    countries=data.get("countries", []),
                    universities=data.get("universities", []),
                    cities=data.get("cities", []),
                    field=data.get("field", "Unknown"),
                )

