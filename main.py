import os
import re

from config import PAPERS_FIELDS_MAPPING
from data_retrival.neo4j.node_pull import UniDataCollector
from data_retrival.neo4j.scholar_citations import SemanticScholarCitationsBatchProcessor
from data_retrival.neo4j.semantic_scholar_papers import ScopusPapersBatchProcessor
from data_retrival.semantic_scholar.papers_handler import process_and_save_chunks
from data_retrival.utils import (
    get_all_files_paths_recursively,
    process_json_lines,
    save_to_json_lines,
    get_file_with_parent_folder,
    load_dataset_mapping,
    save_citations_to_files,
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


def extract_university_info(file_name, dataset_mapping):
    match = re.match(r"(\d+)-\w+\.jsonl", file_name)
    university_id = match.group(1) if match else "Unknown"
    university_name = dataset_mapping.get(university_id, "Unknown")
    return university_id, university_name


def process_papers_in_file(file_path, dataset_mapping):
    country = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path).split("_")[0]
    field_id = os.path.basename(file_path).split("-")[1].split(".")[0]
    field = PAPERS_FIELDS_MAPPING.get(field_id, field_id)
    _, university_name = extract_university_info(file_name, dataset_mapping)

    papers = []
    for paper in process_json_lines(file_path):
        enriched_paper = enrich_paper_data(paper, field, country, university_name)
        papers.append(enriched_paper)
    save_to_json_lines(papers, file_path)


def enrich_paper_data(paper, field, country, university):
    return {
        "field": field,
        "DOI": paper.get("prism:doi"),
        "countries": [country],
        "publication_date": paper.get("prism:coverDate"),
        "universities": [university],
        **paper,
    }


def assign_fields_to_papers(scopus_papers_dataset_path, mapping_file_path="data/dataset_mapping.txt"):
    dataset_paths = get_all_files_paths_recursively(scopus_papers_dataset_path)
    dataset_mapping = load_dataset_mapping(mapping_file_path)

    for path in dataset_paths:
        process_papers_in_file(path, dataset_mapping)


def upload_papers_to_neo4j(scopus_papers_dataset_path):
    scopus_papers_batch_processor = ScopusPapersBatchProcessor()

    dataset_paths = get_all_files_paths_recursively(scopus_papers_dataset_path)

    for path in dataset_paths:
        scopus_papers_batch_processor.process_file(path)

    scopus_papers_batch_processor.close()


def load_dois_from_scopus(scopus_papers_dataset_paths):
    all_dois = set()
    for path in scopus_papers_dataset_paths:
        for paper in process_json_lines(path):
            try:
                all_dois.add(paper["DOI"])
            except (KeyError, TypeError):
                print(f"Error processing paper: {paper}")
    return all_dois


def load_citations_from_scholar(scholar_citations_dataset_paths, all_dois):
    citations_among_dataset = []
    all_citations = []

    for path in scholar_citations_dataset_paths:
        for paper in process_json_lines(path):
            try:
                if paper["DOI"] in all_dois:
                    for citation in paper["citations"]:
                        all_citations.append(citation)
                        if citation and citation in all_dois:
                            citations_among_dataset.append({"base": paper["DOI"], "resource": citation})
            except (KeyError, TypeError):
                print(f"Error processing paper: {paper}")

    return all_citations, citations_among_dataset


def prepare_unique_citations_dataset(
    scopus_papers_dataset_path, scholar_citations_dataset_path, output_dir="data/unique_citations", chunk_size=10000
):
    scopus_papers_dataset_paths = [
        path
        for path in get_all_files_paths_recursively(scopus_papers_dataset_path)
        if not os.path.exists(path.replace(".jsonl", ".not_found.jsonl"))
    ]

    # Load DOIs from Scopus dataset
    all_dois = load_dois_from_scopus(scopus_papers_dataset_paths)

    # Load citations from Scholar dataset
    scholar_citations_dataset_paths = [
        path
        for path in get_all_files_paths_recursively(scholar_citations_dataset_path)
        if os.path.exists(path.replace(".jsonl", ".not_found.jsonl"))
    ]

    all_citations, citations_among_dataset = load_citations_from_scholar(scholar_citations_dataset_paths, all_dois)

    # Save the citations to JSONL files
    save_citations_to_files(citations_among_dataset, output_dir, chunk_size)


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
    """
    FYI, I did all the graph processing un 12 workers and batch size of 10, and it took me around 10 minutes overall.
    But before running the citations part I recommend to index the papers by DOI, it will speed up the process.
    Just open Neo4j browser and run the following query: CREATE INDEX FOR (p:Paper) ON (p.id)
    Once you will have some interesting queries you can place them in useful_neo4j_queries.txt.
    """

    # Those links should fit the paths of the datasets taken from our google drive
    scopus_papers_dataset_path = "data/data_top10/"
    scholar_citations_dataset_path = "data/data_top10_citations/"
    unique_citations_path = "data/data_top10_unique_citations/"

    # Part to skip once you have the data from our google drive
    # download_citations(scholar_citations_dataset_path, scopus_papers_dataset_path)
    #
    # Adding additional information to the papers
    # assign_fields_to_papers(scopus_papers_dataset_path)
    #
    # Uploading the papers to neo4j
    # upload_papers_to_neo4j(scopus_papers_dataset_path)
    #
    # Creating a file with unique citations that are only between papers in our dataset
    # We dont want to have citations to papers that are not in our dataset
    # prepare_unique_citations_dataset(scopus_papers_dataset_path, scholar_citations_dataset_path, unique_citations_path)
    #
    # Uploading the unique citations to neo4j
    # upload_citations_to_neo4j(unique_citations_path)

def node_pull():
    from data_retrival.neo4j.node_pull import NodePull
    node_pull = UniDataCollector("University", range=(2015, 2020), index_field="name", metric="score")
    node_pull.make_temporary_analysis_subgraphs()
    node_pull.make_df()
    node_pull.visualise()
    
    # nodes = node_pull.get_nodes("University", limit=3000, index_field="name")
    # node_pull.make_df(index_field="name")
    # print(nodes)

if __name__ == "__main__":
    main()
    node_pull()
