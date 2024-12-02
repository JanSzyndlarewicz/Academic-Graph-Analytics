import json
from collections import Counter

import matplotlib.pyplot as plt

from data_retrival.neo4j.scholar_citations import SemanticScholarCitationsBatchProcessor
from data_retrival.neo4j.semantic_scholar_papers import SemanticScholarPapersBatchProcessor
from data_retrival.semantic_scholar.papers_handler import process_and_save_chunks
from data_retrival.utils import (
    get_all_files_paths_recursively,
    merge_json_lines_files,
    process_json_lines,
    save_to_json_lines,
)

### --> In progress <-- ###
# Playground #


def main():
    # dataset_paths = get_all_files_paths_recursively("data/initial_econ_set")
    # merge_json_lines_files(dataset_paths, "data/initial_econ_set.jsonl")
    #
    # json_iterator = process_json_lines("data/initial_econ_set.jsonl")
    # chunk_size = 500
    # process_and_save_chunks(json_iterator, chunk_size, "data/initial_econ_set-citations.jsonl")

    # # Load the papers and assign countries
    # paper_countries = {}
    # for paper in process_json_lines("data/initial_econ_set.jsonl"):
    #     if "affiliation" in paper:
    #         for affiliation in paper["affiliation"]:
    #             country = affiliation.get("affiliation-country")
    #             if country:
    #                 paper_countries[paper.get("prism:doi")] = country
    #                 break
    #
    # # Count citations per country
    # country_citations = Counter()
    # for paper in process_json_lines("data/initial_econ_set-citations.jsonl"):
    #     if paper["citations"]:
    #         for citation in paper["citations"]:
    #             if citation and citation in paper_countries:
    #                 country_citations[paper_countries[citation]] += 1
    #
    # # Plot the distribution
    # plt.figure(figsize=(12, 8))
    # plt.bar(country_citations.keys(), country_citations.values(), edgecolor='black')
    # plt.xticks(rotation=90)
    # plt.title('Number of Citations for Different Countries')
    # plt.xlabel('Country')
    # plt.ylabel('Number of Citations')
    # plt.show()

    # PAPERS UPLOAD
    # processed_papers = []
    # for paper in process_json_lines("data/initial_econ_set.jsonl"):
    #     affiliations = paper.get("affiliation")
    #     if affiliations:
    #         affiliations = [affiliation.get("affiliation-country") for affiliation in affiliations if
    #                         affiliation.get("affiliation-country")]
    #     else:
    #         affiliations = []
    #
    #     processed_papers.append({
    #         "DOI": paper.get("prism:doi"),
    #         "affiliations": affiliations,
    #         "publication_date": paper.get("prism:coverDate"),
    #         # TODO Add study field
    #     })
    #
    # save_to_json_lines(processed_papers, "data/initial_econ_set_preprocessed.jsonl")
    #
    #
    # file_path = r"data/initial_econ_set_preprocessed.jsonl"
    # citations_batch_processor = SemanticScholarPapersBatchProcessor()
    # citations_batch_processor.process_file(file_path)
    # citations_batch_processor.close()

    unique_doi_in_papers = set()
    for paper in process_json_lines("data/initial_econ_set_preprocessed.jsonl"):
        unique_doi_in_papers.add(paper["DOI"])

    processed_citations = []
    for paper in process_json_lines("data/initial_econ_set-citations.jsonl"):
        if paper["citations"]:
            citations = [citation for citation in paper["citations"] if citation in unique_doi_in_papers]
            if citations:
                processed_citations.append(
                    {
                        "DOI": paper.get("DOI"),
                        "citations": citations,
                    }
                )

    save_to_json_lines(processed_citations, "data/initial_econ_set_citations_preprocessed.jsonl")

    file_path = r"data/initial_econ_set_citations_preprocessed.jsonl"
    citations_batch_processor = SemanticScholarCitationsBatchProcessor()
    citations_batch_processor.process_file(file_path)
    citations_batch_processor.close()


if __name__ == "__main__":
    main()

    # AWAITING STABLE CODEBASE
    # parser = make_a_parser()
    # args = parser.parse_args()
    # if args.command == "get-links":
    #     database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
    #     database_handler.prepare_new_database()
    # elif args.command == "get-batches":
    #     database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
    #     next_citations_dataset_link = database_handler.download_dataset_handler.get_next_url_to_download()
    #     authorized_citations_url = database_handler.get_authorized_url(next_citations_dataset_link)
    #     file_path = database_handler.pull_batch_from_url(authorized_citations_url)
    #     database_handler.download_dataset_handler.set_url_as_downloaded(next_citations_dataset_link)
    # elif args.command == "process-batches":
    #     database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
    #     next_citations_dataset_link = database_handler.download_dataset_handler.get_next_url_to_download()
    #     authorized_citations_url = database_handler.get_authorized_url(next_citations_dataset_link)
    #     file_path = database_handler.pull_batch_from_url(authorized_citations_url)
    #     database_handler.download_dataset_handler.set_url_as_downloaded(next_citations_dataset_link)
    #     convert_citations_json_to_csv(file_path, file_path + ".csv")
    # elif args.command == "build-graph":
    #     if args.graph_command == "papers":
    #         pass
    #     elif args.graph_command == "authors":
    #         pass
    #
    # # database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
    # database_handler = DatasetHandler(SEMANTIC_SCHOLAR_PAPERS_DATASET_NAME)
    #
    # database_handler.prepare_new_database()
    #
    # next_citations_dataset_link = database_handler.download_dataset_handler.get_next_url_to_download()
    # authorized_citations_url = database_handler.get_authorized_url(next_citations_dataset_link)
    # file_path = database_handler.pull_batch_from_url(authorized_citations_url)
    # # # file_path = r"files\citations_dataset\20241115_081922_00277_4pq6k_04f68738-4009-48e5-abfc-0253ad2b8a25"
    # # # citations_batch_processor = CitationBatchProcessor()
    # # # citations_batch_processor.process_json(file_path)
    # # # citations_batch_processor.close()
    # database_handler.download_dataset_handler.set_url_as_downloaded(next_citations_dataset_link)
    # # convert_citations_json_to_csv(file_path, file_path + ".csv")
