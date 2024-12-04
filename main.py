import json
import os

from data_retrival.neo4j.scholar_citations import SemanticScholarCitationsBatchProcessor
from data_retrival.neo4j.semantic_scholar_papers import ScopusPapersBatchProcessor
from data_retrival.semantic_scholar.papers_handler import process_and_save_chunks
from data_retrival.utils import (
    get_all_files_paths_recursively,
    process_json_lines,
    save_to_json_lines,
    get_file_with_parent_folder,
)


### --> In progress <-- ###
# Playground #

def download_citations(scholar_citations_dataset_path, scopus_papers_dataset_path):
    dataset_paths = get_all_files_paths_recursively(scopus_papers_dataset_path)

    chunk_size = 500

    for path in dataset_paths:
        json_iterator = process_json_lines(path)
        file_name = get_file_with_parent_folder(path)
        full_path = os.path.join(scholar_citations_dataset_path, file_name)
        process_and_save_chunks(json_iterator, chunk_size, full_path)


def assign_countries_to_papers(scopus_papers_dataset_path):
    dataset_paths = get_all_files_paths_recursively(scopus_papers_dataset_path)

    for paths in dataset_paths:
        country = os.path.basename(os.path.dirname(paths))
        papers = []
        for paper in process_json_lines(paths):
            paper["country"] = country
            papers.append(paper)
        save_to_json_lines(papers, paths)

def assign_fields_to_papers(scopus_papers_dataset_path, field):
    dataset_paths = get_all_files_paths_recursively(scopus_papers_dataset_path)

    for paths in dataset_paths:
        papers = []
        for paper in process_json_lines(paths):
            paper["field"] = field
            paper["DOI"] = paper.get("prism:doi")
            paper["countries"] = list(
                {affiliation.get("affiliation-country") for affiliation in paper.get("affiliation", []) if
                 affiliation.get("affiliation-country")})
            paper["publication_date"] = paper.get("prism:coverDate")
            paper["universities"] = list(
                {affiliation.get("affilname") for affiliation in paper.get("affiliation", []) if
                 affiliation.get("affilname")})
            paper["cities"] = list(
                {affiliation.get("affiliation-city") for affiliation in paper.get("affiliation", []) if
                 affiliation.get("affiliation-city")})
            papers.append(paper)
        save_to_json_lines(papers, paths)


def upload_papers_to_neo4j(scopus_papers_dataset_path):
    scopus_papers_batch_processor = ScopusPapersBatchProcessor()

    dataset_paths = get_all_files_paths_recursively(scopus_papers_dataset_path)

    for path in dataset_paths:
        scopus_papers_batch_processor.process_file(path)

    scopus_papers_batch_processor.close()


def prepare_unique_citations_dataset(scopus_papers_dataset_path, scholar_citations_dataset_path, output_dir="data/unique_citations", chunk_size=10000):
    all_dois = set()

    scopus_papers_dataset_paths = [
        path for path in get_all_files_paths_recursively(scopus_papers_dataset_path)
        if not os.path.exists(path.replace('.jsonl', '.not_found.jsonl'))
    ]

    for path in scopus_papers_dataset_paths:
        for paper in process_json_lines(path):
            try:
                all_dois.add(paper["DOI"])
            except (KeyError, TypeError):
                print(paper)

    dataset_paths = get_all_files_paths_recursively(scholar_citations_dataset_path)

    citations = []
    all_citations = []
    for path in dataset_paths:
        for paper in process_json_lines(path):
            try:
                if paper["DOI"] in all_dois:
                    for citation in paper["citations"]:
                        all_citations.append(citation)
                        if citation and citation in all_dois:
                            citations.append({"base": paper["DOI"], "resource": citation})
            except (KeyError, TypeError):
                print(paper)

    os.makedirs(output_dir, exist_ok=True)

    for i in range(0, len(citations), chunk_size):
        chunk = citations[i:i + chunk_size]
        file_path = os.path.join(output_dir, f"citations_{i // chunk_size + 1}.jsonl")
        with open(file_path, 'w') as f:
            for citation in chunk:
                f.write(json.dumps(citation) + "\n")


def upload_citations_to_neo4j(citations_dataset_path):
    scholar_citations_batch_processor = SemanticScholarCitationsBatchProcessor()

    dataset_paths = get_all_files_paths_recursively(citations_dataset_path)

    for path in dataset_paths:
        scholar_citations_batch_processor.process_file(path)

    scholar_citations_batch_processor.close()


def main():
    """
    Before running the script you may want to play with the values for the NEO4J_MAX_WORKERS in config.py.
    The default value is 1, but you can increase it to speed up the process, it shouldnt be higher that
    the number of threads your CPU can handle. There are some errors while making it in parallel, so you want
    to make sure that the data is uploaded correctly to the neo4j database keeping the number of workers to 1.
    The whole process of uploading the data to neo4j can take a few hours ~4 hours in one worker mode.
    So just run it through the night and you should be fine.
    In case of any errors there is one thing that can be done, and it will fix the problem. You just have to ...
    """

    # Those links should fit the paths of the datasets taken from our google drive
    scopus_papers_dataset_path = "data/econ_data_top3/"
    scholar_citations_dataset_path = "data/scholar_citations/"
    unique_citations_path = "data/unique_citations/"
    field = "economics"

    # Part to skip once you have the data from our google drive
    download_citations(scholar_citations_dataset_path, scopus_papers_dataset_path)

    # Adding additional information to the papers
    assign_fields_to_papers(scopus_papers_dataset_path, field)

    # Uploading the papers to neo4j
    upload_papers_to_neo4j(scopus_papers_dataset_path)

    # Creating a file with unique citations that are only between papers in our dataset
    # We dont want to have citations to papers that are not in our dataset
    prepare_unique_citations_dataset(scopus_papers_dataset_path, scholar_citations_dataset_path, unique_citations_path)

    # Uploading the unique citations to neo4j
    upload_citations_to_neo4j(unique_citations_path)

if __name__ == "__main__":
    main()
