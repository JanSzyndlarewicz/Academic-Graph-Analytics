from data_retrival.neo4j.core import AbstractNeo4jBatchProcessor


class CitationBatchProcessor(AbstractNeo4jBatchProcessor):

    def process_batch(self, tx, batch):
        for data in batch:
            if data.get("citingcorpusid") and data.get("citedcorpusid"):
                tx.run(
                    """
                    MERGE (citing:Corpus {corpusid: $citingcorpusid})
                    MERGE (cited:Corpus {corpusid: $citedcorpusid})
                    MERGE (citing)-[:CITES {
                        citationid: $citationid,
                        isinfluential: $isinfluential
                    }]->(cited)
                """,
                    citingcorpusid=int(data["citingcorpusid"]),
                    citedcorpusid=int(data["citedcorpusid"]),
                    citationid=int(data["citationid"]),
                    isinfluential=bool(data.get("isinfluential", False)),
                )
