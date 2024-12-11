import json
from typing import Any, List, Tuple

import requests
from semanticscholar import SemanticScholar

from config import SEMANTIC_SCHOLAR_API_KEY, SEMANTIC_SCHOLAR_PAPERS_BASE_URL
from data_retrival.semantic_scholar.abstract import APIClient
from data_retrival.utils import append_to_json_lines


class PapersScholarAPI(APIClient):
    def __init__(self):
        super().__init__()
        self.base_url += SEMANTIC_SCHOLAR_PAPERS_BASE_URL

    def get_papers(self, dois: list, fields: str, limit: int = 500) -> tuple[list[dict], list[str]]:
        self.logger.info(f"Retrieving papers from Semantic Scholar API")
        url = f"{self.base_url}batch"
        params = {"fields": fields}
        all_results = []
        not_found = []

        for i in range(0, len(dois), limit):
            chunk = dois[i : i + limit]
            payload = {"ids": chunk}

            response = requests.post(url, params=params, json=payload, headers=self.headers)

            if response.status_code == 200:
                all_results.extend(response.json())

                chunk = [
                    doi
                    for doi in chunk
                    if not any(paper.get("externalIds", {}).get("DOI") == doi for paper in response.json() if paper)
                ]

                not_found.extend(chunk)

            else:
                self.logger.error(f"Failed to retrieve data from {url}: {response.status_code}")
                raise RuntimeError(f"Failed to retrieve data: {response.status_code}")

        return all_results, not_found

    def fetch_papers_by_dois(self, dois, fields):
        try:
            papers, not_found_paper = self.get_papers(dois, fields=fields)
            return [paper_to_dict(paper) for paper in papers], not_found_paper
        except Exception as e:
            self.logger.info(f"Error fetching papers: {e}")
            return [], dois


def paper_to_dict(paper):
    if not paper:
        return {}
    external_ids = paper.get("externalIds", {})
    citations = paper.get("citations", [])
    return {
        "DOI": external_ids.get("DOI"),
        "citations": [
            citation.get("externalIds", {}).get("DOI") for citation in citations if citation.get("externalIds")
        ],
    }


def fetch_papers_by_dois(semantic_scholar_connector, dois, fields):
    try:
        papers, not_found_paper = semantic_scholar_connector.get_papers(dois, fields=fields)
        return [paper_to_dict(paper) for paper in papers], not_found_paper
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return [], dois


def process_and_save_chunks(json_iterator, chunk_size, filename):
    semantic_scholar_connector = PapersScholarAPI()
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
                papers_dict, not_found = fetch_papers_by_dois(
                    semantic_scholar_connector, chunk, fields="citations.externalIds,externalIds"
                )

                append_to_json_lines(papers_dict, filename)

                if not_found:
                    append_to_json_lines(not_found, papers_not_found_path)

                chunk = []
    if chunk:
        papers_dict, not_found = fetch_papers_by_dois(
            semantic_scholar_connector, chunk, fields="citations.externalIds,externalIds"
        )

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
