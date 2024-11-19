import argparse


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
