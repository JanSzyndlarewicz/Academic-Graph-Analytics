from config import SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME
from data_retrival.csv_handler import convert_citations_json_to_csv
from data_retrival.download_dataset_handler import DatasetHandler
from parser import make_a_parser

### --> In progress <-- ###
# Playground #


def main():
    pass
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

    database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
    next_citations_dataset_link = database_handler.download_dataset_handler.get_next_url_to_download()
    authorized_citations_url = database_handler.get_authorized_url(next_citations_dataset_link)
    file_path = database_handler.pull_batch_from_url(authorized_citations_url)
    # file_path = r"files\citations_dataset\20241115_081922_00277_4pq6k_04f68738-4009-48e5-abfc-0253ad2b8a25"
    # citations_batch_processor = CitationBatchProcessor()
    # citations_batch_processor.process_json(file_path)
    # citations_batch_processor.close()
    database_handler.download_dataset_handler.set_url_as_downloaded(next_citations_dataset_link)
    convert_citations_json_to_csv(file_path, file_path + ".csv")

if __name__ == "__main__":
    main()