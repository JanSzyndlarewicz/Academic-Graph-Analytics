import json

from semanticscholar import SemanticScholar

from config import SEMANTIC_SCHOLAR_API_KEY
from data_retrival.utils import append_to_json_lines

# Initialize the Semantic Scholar API client
ss_api = SemanticScholar(api_key=SEMANTIC_SCHOLAR_API_KEY)


def paper_to_dict(paper):
    return {
        "DOI": paper.externalIds.get("DOI"),
        "citations": [citation.externalIds.get("DOI") for citation in paper.citations if citation.externalIds],
        "authors": [{"authorId": author.authorId, "name": author.name} for author in paper.authors],
    }


def fetch_papers_by_dois(dois, fields):
    try:
        papers, not_found_paper = ss_api.get_papers(dois, fields=fields, return_not_found=True)
        return [paper_to_dict(paper) for paper in papers], not_found_paper
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return []


def process_and_save_chunks(json_iterator, chunk_size, filename):
    chunk = []
    papers_not_found_path = filename.split(".")
    papers_not_found_path.insert(-1, "not_found")
    papers_not_found_path = ".".join(papers_not_found_path)
    print(papers_not_found_path)

    for json_obj in json_iterator:
        doi = json_obj.get("prism:doi")
        if doi:
            chunk.append(doi)
            if len(chunk) == chunk_size:
                papers_dict, not_found = fetch_papers_by_dois(chunk, fields=["citations.externalIds", "externalIds", "authors"])
                append_to_json_lines(papers_dict, filename)

                if not_found:
                    append_to_json_lines(not_found, papers_not_found_path)

                chunk = []
    if chunk:
        papers_dict, not_found = fetch_papers_by_dois(chunk, fields=["citations.externalIds", "externalIds", "authors"])

        append_to_json_lines(papers_dict, filename)
        if not_found:
            append_to_json_lines(not_found, papers_not_found_path)


def count_citations(file_path):
    citations_counter = []
    papers_counter = 0
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            paper = json.loads(line)
            if paper.get("citations"):
                papers_counter += 1
                citations_counter.extend([citation for citation in paper["citations"] if citation])
    return len(citations_counter), papers_counter
