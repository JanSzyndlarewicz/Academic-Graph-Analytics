import json
import os.path
from collections import Counter

import pandas as pd
from isort.core import process
from matplotlib import pyplot as plt
from numpy.f2py.auxfuncs import throw_error
from sklearn.preprocessing import MinMaxScaler

from data_retrival.neo4j.neo4j_connector import Neo4JConnector


class NodePull(Neo4JConnector):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def get_nodes(self, type=None, limit=3000):
        if not type:
            type = self.type
        query = f"MATCH (n:{type}) RETURN n LIMIT {limit}"
        print(self.count_nodes(type))
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query)
                result = [record.data()["n"] for record in result]
                return result

    def count_nodes(self, type, condition=None):
        if condition:
            query = f"MATCH (n:{type}) WHERE {condition} RETURN COUNT(n) AS node_count"
        else:
            query = f"MATCH (n:{type}) RETURN COUNT(n) AS node_count"
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query)
                result = result.single().data()["node_count"]
                return result

    def fetch_in_batches(self, query, batch_size):
        offset = 0
        all_results = []

        while True:
            batch_query = f"{query} SKIP {offset} LIMIT {batch_size}"
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    result = tx.run(batch_query)
                    batch = [record["n"] for record in result]
                    if not batch:
                        break
                    all_results.extend(batch)
            offset += batch_size

        return all_results


class UniDataCollector:
    def __init__(self, type, range, index_field, metric):
        self.node_pull = NodePull(type)
        self.range: tuple[int, int] = range
        self.metric = metric
        self.index_field = index_field

    def make_time_series_analysis_subgraphs(self, field_filter=None):
        for i in range(self.range[0], self.range[1] + 1):
            self.node_pull.run_query(
                f"""
                MATCH (n:University_{str(i)}) DETACH DELETE n"""
            )
            print(f"Deleted nodes for {i}")

        for i in range(self.range[0], self.range[1] + 1):
            if field_filter is None:
                self.node_pull.run_query(
                    f"""
                    MATCH (base:Paper)-[:CITES]->(cited:Paper)
                    WHERE DATE(base.publication_date) < DATE("{str(i+1)}-01-01") AND DATE(base.publication_date) >= DATE("{str(i)}-01-01")
                    WITH base.universities AS base_universities, cited.universities AS cited_universities,
                    base.countries AS base_country, cited.countries AS cited_country
                    UNWIND base_universities AS base_university
                    UNWIND cited_universities AS cited_university
                    MERGE (bc:University_{str(i)} {{name: base_university, country: base_country}})
                    MERGE (cc:University_{str(i)} {{name: cited_university, country: cited_country}})
                    MERGE (bc)-[r:UNIVERSITY_CITES]->(cc)
                    ON CREATE SET r.weight = 1
                    ON MATCH SET r.weight = r.weight + 1
                    """
                )
            else:
                self.node_pull.run_query(
                    f"""
                    MATCH (base:Paper)-[:CITES]->(cited:Paper)
                    WHERE DATE(base.publication_date) < DATE("{str(i+1)}-01-01") AND DATE(base.publication_date) >= DATE("{str(i)}-01-01")
                    AND base.field == {field_filter}
                    WITH base.universities AS base_universities, cited.universities AS cited_universities,
                    base.countries AS base_country, cited.countries AS cited_country
                    UNWIND base_universities AS base_university
                    UNWIND cited_universities AS cited_university
                    MERGE (bc:University_{str(i)} {{name: base_university, country: base_country}})
                    MERGE (cc:University_{str(i)} {{name: cited_university, country: cited_country}})
                    MERGE (bc)-[r:UNIVERSITY_CITES]->(cc)
                    ON CREATE SET r.weight = 1
                    ON MATCH SET r.weight = r.weight + 1
                    """
                )

    def drop_temporary_graph(self, type=None, for_range=False):
        if not type:
            type = self.node_pull.type
        if for_range:
            for i in range(self.range[0], self.range[1] + 1):
                query_drop_graph = f"""
                CALL gds.graph.drop('myGraph{str(type)}_{str(i)}')
                """
                self.node_pull.run_query(query=query_drop_graph)
        else:
            query_drop_graph = f"""
                CALL gds.graph.drop('myGraph{str(type)}')
                """
            self.node_pull.run_query(query=query_drop_graph)

    def create_temporary_graph(self, type=None, for_range=False):
        if not type:
            type = self.node_pull.type
        if for_range:
            for i in range(self.range[0], self.range[1] + 1):
                query = f"""
                CALL gds.graph.project(
                'myGraph{str(type)}_{str(i)}',
                '{str(type)}',
                'UNIVERSITY_CITES',
                {{ relationshipProperties: ['weight'] }}
                )
                """
                self.node_pull.run_query(query=query)
        else:
            query = f"""
                CALL gds.graph.project(
              'myGraph{str(type)}', 
              '{str(type)}',  
              'UNIVERSITY_CITES',  
              {{ relationshipProperties: ['weight'] }}
            )"""
            self.node_pull.run_query(query=query)

    def get_page_rank_from_temp_graphs(self, type=None):
        if type is None:
            type = self.node_pull.type

        query = f"""
        CALL gds.pageRank.stream('myGraph{str(type)}', {{
          maxIterations: 20,
          dampingFactor: 0.85,
          relationshipWeightProperty: 'weight',
          scaler: "MinMax"
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).name AS name, score, gds.util.asNode(nodeId).country AS country
        ORDER BY score DESC, name ASC
        
        
        """
        result = self.node_pull.run_query(query=query)
        return result

    def make_df(self, index_field=None):
        if not index_field:
            index_field = self.index_field
        df = None
        for i in range(self.range[0], self.range[1] + 1):
            scoped_type = self.node_pull.type + "_" + str(i)

            try:
                result = self.get_page_rank_from_temp_graphs(type=scoped_type)
                result = sorted(result, key=lambda x: x["name"])
                print(result)
            except Exception as e:
                print(f"Error fetching nodes for type {scoped_type}: {e}")
                continue

            data = [(record[index_field], record["score"], record["country"][0]) for record in result]
            appended_df = pd.DataFrame(
                {
                    i: [tup[1] for tup in data],
                },
                index=[tup[0] + " IN " + tup[2] for tup in data],
            )
            if df is None:
                df = appended_df
            else:
                df = pd.concat([df, appended_df], axis=1)
        self.df = df
        return df

    # this is work zone, playground u can copy it to make ur own
    def visualise(self, df=None):
        if df is None:
            df = self.df
        # Transpose the DataFrame to make years the index
        df = df.T
        df.index.name = "Year"  # Rename the index to 'Year'
        # df = df[-16:]
        # Bucket the years into decades using integer division
        # Define the bins and labels correctly
        bucket_size = 2
        upper_bound = df.index.max()
        lower_bound = df.index.min()
        if upper_bound < lower_bound:
            upper_bound, lower_bound = lower_bound, upper_bound
        bins = range(lower_bound, upper_bound, bucket_size)  # Bin edges

        labels = [i for i in range(lower_bound, upper_bound, bucket_size)]  # Labels for the bins
        labels = labels[:-1]
        # Ensure the number of labels is one less than the number of bins
        # df['decade'] = pd.cut(df.index, bins=bins, labels=labels, right=False)

        # # Group by decade and aggregate (e.g., sum the values)
        # aggregated_df = df.groupby('decade').sum()

        # # Set the 'decade' as the new index
        # aggregated_df = aggregated_df.reset_index().set_index('decade')

        # see trend of all universities
        # aggregated_df = df
        # aggregated_df.fillna(aggregated_df.mean(), inplace=True)
        # aggregated_df = aggregated_df.filter(regex="States")
        # aggregated_df = aggregated_df.mean(axis=1)
        # aggregated_df = aggregated_df.to_frame()

        last_part = [col.split(" ")[-1] for col in df.columns]

        # Aggregate columns based on the last word of their names
        # Group the columns based on the last part of the column names
        grouped_data = {}
        for i, part in enumerate(last_part):
            if part not in grouped_data:
                grouped_data[part] = []
            grouped_data[part].append(df.iloc[:, i])

        # Sum the columns in each group (you can use other aggregation methods)
        aggregated_df = {}
        for part, columns in grouped_data.items():
            aggregated_df[part] = pd.concat(columns, axis=1).sum(axis=1)

        # Convert to DataFrame
        aggregated_df = pd.DataFrame(aggregated_df)
        aggregated_df = aggregated_df.loc[:, ["States", "Russia"]]
        # Plot
        aggregated_df.plot(figsize=(10, 6))
        plt.title("Metrics Over Years")
        plt.xlabel("Year")
        plt.ylabel("Metric")
        plt.legend(title="Universities", bbox_to_anchor=(1.05, 1), loc="upper left")  # Move legend outside plot
        plt.grid()
        plt.show()

    def visualise_aggr_by_countries(self, df=None, bucketed=False, bucket_size=2, picked_countries=None):
        if df is None:
            df = self.df
        # Transpose the DataFrame to make years the index
        df = df.T
        df.index.name = "Year"  # Rename the index to 'Year'
        # df = df[-16:]

        if bucketed:
            upper_bound = df.index.max()
            lower_bound = df.index.min()
            if upper_bound < lower_bound:
                upper_bound, lower_bound = lower_bound, upper_bound
            bins = range(lower_bound, upper_bound, bucket_size)  # Bin edges

            labels = [i for i in range(lower_bound, upper_bound, bucket_size)]  # Labels for the bins
            labels = labels[:-1]
            # Ensure the number of labels is one less than the number of bins
            df["decade"] = pd.cut(df.index, bins=bins, labels=labels, right=False)

            # Group by decade and aggregate (e.g., sum the values)
            aggregated_df = df.groupby("decade").sum()

            # Set the 'decade' as the new index
            aggregated_df = aggregated_df.reset_index().set_index("decade")

        country_name = [col.split(" IN ")[-1] for col in df.columns]

        # Aggregate columns based on the last part of their names
        grouped_data = {}
        for i, part in enumerate(country_name):
            if part not in grouped_data:
                grouped_data[part] = []
            grouped_data[part].append(df.iloc[:, i])

        # Sum the columns in each group (you can use other aggregation methods)
        aggregated_df = {}
        for part, columns in grouped_data.items():
            aggregated_df[part] = pd.concat(columns, axis=1).sum(axis=1)

        # Convert to DataFrame
        aggregated_df = pd.DataFrame(aggregated_df)
        if picked_countries:
            aggregated_df = aggregated_df.loc[:, picked_countries]
        # aggregated_df = aggregated_df.loc[:, ['States', 'Russia']]
        # Plot
        self.plot(aggregated_df)

    def plot(self, df=None):
        if df is None:
            df = self.df
        df.plot(figsize=(10, 6))
        plt.title("Page Rank Over Years")
        plt.xlabel("Year")
        plt.ylabel("Metric")
        plt.legend(title="Universities", bbox_to_anchor=(1.05, 1), loc="upper left")  # Move legend outside plot
        plt.grid()
        plt.show()


class PaperDataCollector(Neo4JConnector):
    def __init__(self, range):
        super().__init__()
        self.range: tuple[int, int] = range

    def pull(self, limit=100):

        queried_fields = ["closeness", "degree", "pagerank", "articlerank", "louvain", "approxBetweenness"]

        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for i in range(self.range[0], self.range[1] + 1):
                    for field in queried_fields:
                        query = f"""
                                MATCH (n:Paper_{str(i)})
                                WHERE n.{field} IS NOT NULL
                                RETURN n
                                ORDER BY n.{field} DESC
                                LIMIT {limit}
                                """
                        results = tx.run(query)
                        results = [record.data() for record in results]
                        fetched_results = [record["n"] for record in results]

                        self.process(fetched_results, field, f"Paper_{str(i)}")

    def process(self, result, metric, label):

        ex = """
        {'articlerank': 0.2233492857159228,
         'louvain': 43430, 'approxBetweenness': 0.0,
        'universities': ['University College London'], 
        'field': 'pharmacy', 'closeness': 0.5, 'degree': 5.0, 
        'publication_date': '2015-05-05', 'id': '10.1177/0269881114568041', 
        'countries': ['United Kingdom'], 
        'pagerank': 0.242138696490995}"""
        if not os.path.exists("statistics.json"):
            with open("statistics.json", "w") as file:
                json.dump({}, file)

        with open("statistics.json", "r+", encoding="utf-8") as file:
            stats = json.load(file)
            if label in stats:
                stats[label][f"{metric}_top"] = result

            else:
                stats[label] = {f"{metric}_top": result}
            file.seek(0)
            json.dump(stats, file, ensure_ascii=False)
            file.truncate()

    def visualise(self, picked_cols=None, picked_metric="pagerank_top", for_type="countries"):
        labels = self.get_unique_vals("Paper", for_type)
        df = pd.DataFrame(columns=labels)

        with open("statistics.json", "r", encoding="utf-8") as file:
            stats = json.load(file)
            for label, metrics in stats.items():
                for metric, data in metrics.items():

                    if metric != picked_metric:
                        continue
                    print(len(data))

                    print(label, metric, (data))
                    if isinstance(data[0][for_type], list):
                        values_occurrences = Counter([country for paper in data for country in paper[for_type]])
                    else:
                        values_occurrences = Counter([paper[for_type] for paper in data])

                    for col in df.columns:
                        values_occurrences.setdefault(col, 0)
                    df.loc[label] = values_occurrences

            if picked_cols:
                print(df.columns)
                df = df[picked_cols]
            if not picked_cols or len(picked_cols) > 1:
                scaler = MinMaxScaler()

                scaled_values = scaler.fit_transform(df)

                df = pd.DataFrame(scaled_values, columns=df.columns, index=df.index)

            os.makedirs(f"top_n/{picked_metric}/", exist_ok=True)

            df.to_csv(f"top_n/{picked_metric}/statistics_{label}_{picked_metric}_{for_type}.csv")
            df.index = df.index.map(lambda x: x.split("_")[-1])
            df.plot(kind="line")
            plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
            plt.tight_layout()
            plt.gcf().set_size_inches(10, 7)
            plt.title("occurrences of countries in top 1000 page rank for papers normalised")
            plt.xlabel("Years")
            plt.ylabel("Values")
            plt.savefig(f"statistics_{label}_{picked_metric}_{for_type}.png")
            plt.show()
