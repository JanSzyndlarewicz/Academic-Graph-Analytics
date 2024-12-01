import json

from semanticscholar import SemanticScholar

from config import SEMANTIC_SCHOLAR_API_KEY
from data_retrival.utils import process_json_lines, save_to_json_lines

ss_api = SemanticScholar(api_key=SEMANTIC_SCHOLAR_API_KEY)


def paper_to_dict(paper):
    return {
        "DOI": paper.externalIds.get("DOI", None),
        "citations": [
            citation.externalIds.get("DOI", None) for citation in paper.citations if citation.externalIds is not None
        ],
    }


def process_and_save_chunks(json_iterator, chunk_size, filename):
    chunk = []
    for json_obj in json_iterator:
        doi = json_obj.get("prism:doi")
        if doi:
            chunk.append(doi)
            if len(chunk) == chunk_size:
                papers = ss_api.get_papers(chunk, fields=["citations.externalIds", "externalIds"])
                papers_dict = [paper_to_dict(paper) for paper in papers]
                save_to_json_lines(papers_dict, filename)
                chunk = []
    if chunk:
        papers = ss_api.get_papers(chunk, fields=["citations.externalIds", "externalIds"])
        papers_dict = [paper_to_dict(paper) for paper in papers]
        save_to_json_lines(papers_dict, filename)


json_iterator = process_json_lines("60021331-econ-batch.jsonl")
chunk_size = 500
process_and_save_chunks(json_iterator, chunk_size, "papers_batch.jsonl")
# open json file and read the data
with open("papers_batch.jsonl", "r", encoding="utf-8") as file:
    citations_counter = []
    papers_counter = 0
    for line in file:
        paper = json.loads(line)
        if paper["citations"]:
            papers_counter += 1
        for citation in paper["citations"]:
            if citation:
                citations_counter.append(citation)
print(len(citations_counter))
print(papers_counter)
