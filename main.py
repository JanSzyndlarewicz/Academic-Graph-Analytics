import argparse
from config import SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME
from data_retrival.csv_handler import convert_citations_json_to_csv
from data_retrival.download_dataset_handler import DatasetHandler

### --> In progress <-- ###
# Playground #

def make_a_parser():
    argParser = argparse.ArgumentParser(description="Download and process Semantic Scholar citations dataset")

    subparsers = argParser.add_subparsers(dest="command", help="Manage the download and processing of the Semantic Scholar citations dataset")

    # DOWNLOADS
    download_links_parser = subparsers.add_parser("get-links", help="Download links for batches download")

    download_batches_parser = subparsers.add_parser("get-batches", help="Download batches of citations dataset")
    download_batches_parser.add_argument(
        "--all", action="store_true", help="Download all batches of citations dataset, otherwise download only next batch"
    )
    # PROCESSING
    process_batches_parser = subparsers.add_parser("process-batches", help="Process downloaded batches of citations dataset from json to csv")
    process_batches_parser.add_argument(
        "--all", action="store_true", help="Process all downloaded batches to csv of citations dataset, otherwise process only next batch"
    )

    # GRAPH BUILDING
    build_on_graph_parser = subparsers.add_parser("build-on-graph", help="Build on graph from processed csv files")
    build_on_graph_parser_subparsers = build_on_graph_parser.add_subparsers(dest="graph_command", help="Manage the building of the graph")

    # this saves to different db
    build_on_papers_graph_parser = build_on_graph_parser_subparsers.add_parser("papers", help="Build on graph of papers from processed csv files")
    build_on_papers_graph_parser.add_argument("using", choices=["papers", "citations"], help="Build on graph of papers from citations csv files")
    # could be used with pipeline from other scripts that calculate interesting seeds
    build_on_papers_graph_parser.add_argument("--from-seeds", nargs="+", help="Build on graph of papers from seeds paper id")
    build_on_papers_graph_parser.add_argument("--by-fields", nargs="+", help="Build on graph of papers by fields and their nbrs")
    build_on_papers_graph_parser.add_argument("--depth", type=int, default=5, help="Depth of the graph to build, default is 5")
    build_on_papers_graph_parser.add_argument("--limit", type=int, default=1000,help="Limit of papers to Build on graph from, default is 1000")
    build_on_papers_graph_parser.add_argument("--no-expansions", action="store_true", help="Only add more information to existing resources")

    # this saves to different db TODO: add new db?, specify uri?
    build_on_authors_graph_parser = build_on_graph_parser_subparsers.add_parser("authors", help="Build on graph of authors from processed csv files")
    # could be used with pipeline from other scripts that calculate interesting seeds
    build_on_authors_graph_parser.add_argument("--from-seeds", nargs="+", help="Build on graph of papers from seeds paper id")
    build_on_authors_graph_parser.add_argument("--by-fields", nargs="+", help="Build on graph of papers by fields and their nbrs")
    build_on_authors_graph_parser.add_argument("--depth", type=int, default=5, help="Depth of the graph to build, default is 5")
    build_on_authors_graph_parser.add_argument("--limit", type=int, default=1000,help="Limit of papers to Build on graph from, default is 1000")

    return argParser

def main():
    parser = make_a_parser()
    args = parser.parse_args()
    if args.command == "get-links":
        database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
        database_handler.prepare_new_database()
    elif args.command == "get-batches":
        database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
        next_citations_dataset_link = database_handler.download_dataset_handler.get_next_url_to_download()
        authorized_citations_url = database_handler.get_authorized_url(next_citations_dataset_link)
        file_path = database_handler.pull_batch_from_url(authorized_citations_url)
        database_handler.download_dataset_handler.set_url_as_downloaded(next_citations_dataset_link)
    elif args.command == "process-batches":
        database_handler = DatasetHandler(SEMANTIC_SCHOLAR_CITATIONS_DATASET_NAME)
        next_citations_dataset_link = database_handler.download_dataset_handler.get_next_url_to_download()
        authorized_citations_url = database_handler.get_authorized_url(next_citations_dataset_link)
        file_path = database_handler.pull_batch_from_url(authorized_citations_url)
        database_handler.download_dataset_handler.set_url_as_downloaded(next_citations_dataset_link)
        convert_citations_json_to_csv(file_path, file_path + ".csv")
    elif args.command == "build-graph":
        if args.graph_command == "papers":
            pass
        elif args.graph_command == "authors":
            pass



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
