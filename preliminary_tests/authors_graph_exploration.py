from collections import defaultdict
import json
import os
import jsonlines
import matplotlib.pyplot as plt
import networkx as nx

def get_distinct_authors(path):
    authors = set()
    with jsonlines.open(path) as reader:
        for paper in reader:
            for author in paper["authors"]:
                authors.add(author["authorId"])
    return authors


def count_authors_appearances(path):
    authors = defaultdict(int)
    with jsonlines.open(path) as reader:
        for paper in reader:
            for author in paper["authors"]:
                authors[author["authorId"]] += 1
    return authors


def generate_report(path):
    distinct_authors = get_distinct_authors(path)
    print(f"Number of distinct authors: {len(distinct_authors)}")
    
    authors_appearances = count_authors_appearances(path)    
    authors_appearances = dict(sorted(authors_appearances.items(), key=lambda item: item[1]))
    visualise_distribution(authors_appearances)
    print(f"top authors: {dict(list(authors_appearances.items())[-10:])}")


def visualise_distribution(data):
    plt.figure(figsize=(10, 6))
    plt.hist(data.values(), bins=50, edgecolor='black')
    plt.title('Distribution')
    plt.xlabel('Number of Appearances')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
    
def make_networkX_viable_structure(path):
    # paper to authors
    paper_authors = {}
    
    with jsonlines.open(path) as reader:
        for paper in reader:
            if 'authors' in paper and 'DOI' in paper and paper['DOI'] is not None:  
                paper_authors[paper['DOI']] = [
                    author['authorId'] for author in paper['authors'] 
                    if author is not None and 'authorId' in author and author['authorId'] is not None
                ]
    
    # constructing the edges list
    authors_graph_edges = defaultdict(int)
    i =0
    with jsonlines.open(path) as reader:
        for paper in reader:
            for citing_this in paper["citations"] :
                if citing_this is not None:
                    for author in [author['authorId'] for author in paper['authors'] 
                                   if author is not None and 'authorId' in author and author['authorId'] is not None]:
                        authors_citing_this = paper_authors.get(citing_this, None)
                        if authors_citing_this is not None:
                            for author_citing_this in authors_citing_this:
                                authors_graph_edges[(author_citing_this, author)] += 1
    
    authors_graph_edges = [(k[0], k[1], v) for k, v in authors_graph_edges.items()]
    
    save_path = os.path.join(os.path.dirname(path), "edges_file.json")
    with open(save_path, "w+",encoding="utf-8") as file:
        json.dump(authors_graph_edges, file, ensure_ascii=False, indent=4)
    return authors_graph_edges

def graph_creation(path):
    edges = None
    with open(path, "r") as file:
        json_file = json.load(file)
        edges = [tuple(l) for l in json_file]
        
    print(edges)
    G = nx.DiGraph()
    return G.add_weighted_edges_from(edges) 

def pre_main():
    path = "data/whole_pwr_citations/whole_pwr/pwr_citations.jsonl"
    # generate_report(path)
    make_networkX_viable_structure(path)

def main():
    edges_path = "data/whole_pwr_citations/whole_pwr/edges_file.json"
    G = graph_creation(edges_path)
    print(nx.approximation.maximum_independent_set(G))
    
    
if __name__ == "__main__":
    # pre_main()
    main()    