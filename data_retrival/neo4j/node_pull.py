import json
import os.path
from collections import Counter

import pandas as pd
from matplotlib import pyplot as plt
from numpy.f2py.auxfuncs import throw_error

from data_retrival.neo4j.neo4j_connector import Neo4JConnector
from global_constants import GlobalConstants


class DataCollector:
    def __init__(self, range, type):
        self.connector = Neo4JConnector()
        self.range: tuple[int, int] = range
        self.type = type



class UniDataCollector(DataCollector):
    def __init__(self, range, index_field, metric):
        super().__init__(range, "University")
        self.metric = metric
        self.index_field = index_field
        

    def make_time_series_analysis_subgraphs(self, field_filter=None):
        for i in range(self.range[0], self.range[1] + 1):
            self.connector.run_query(
                f"""
                MATCH (n:University_{str(i)}) DETACH DELETE n"""
            )
            print(f"Deleted nodes for {i}")

        for i in range(self.range[0], self.range[1] + 1):
            if field_filter is None:
                self.connector.run_query(
                    f"""
                MATCH (base:Paper)-[:CITES]->(cited:Paper)
                WHERE DATE(base.publication_date) < DATE("{str(i+1)}-01-01") AND DATE(base.publication_date) >= DATE("{str(i)}-01-01")
                WITH base.universities AS base_universities, cited.universities AS cited_universities
                //base.countries AS base_country, cited.countries AS cited_country
                UNWIND base_universities AS base_university
                UNWIND cited_universities AS cited_university
                MERGE (bc:University_{str(i)} {{name: base_university}})
                MERGE (cc:University_{str(i)} {{name: cited_university}})
                MERGE (bc)-[r:UNIVERSITY_CITES]->(cc)
                ON CREATE SET r.weight = 1
                ON MATCH SET r.weight = r.weight + 1
                """
                )
            else:
                self.connector.run_query(
                    f"""
                MATCH (base:Paper)-[:CITES]->(cited:Paper)
                WHERE DATE(base.publication_date) < DATE("{str(i+1)}-01-01") AND DATE(base.publication_date) >= DATE("{str(i)}-01-01")
                AND base.field = "{field_filter}"
                WITH base.universities AS base_universities, cited.universities AS cited_universities
                //base.countries AS base_country, cited.countries AS cited_country
                UNWIND base_universities AS base_university
                UNWIND cited_universities AS cited_university
                MERGE (bc:University_{str(i)} {{name: base_university}})
                MERGE (cc:University_{str(i)} {{name: cited_university}})
                MERGE (bc)-[r:UNIVERSITY_CITES]->(cc)
                ON CREATE SET r.weight = 1
                ON MATCH SET r.weight = r.weight + 1
                """
                )
            
            for uni, country in GlobalConstants.econ_uni2country.items():
                r = self.node_pull.run_query(
                    f"""
                    MATCH (n:University_{str(i)})
                    WHERE n.name = "{uni}" 
                    SET n.countries = ["{country}"]
            """)

    def drop_temporary_graph(self):
        type = self.type
    
        for i in range(self.range[0], self.range[1] + 1):
            query_drop_graph = f"""
            CALL gds.graph.drop('myGraph{str(type)}_{str(i)}')
            """
            try:
                self.node_pull.run_query(query=query_drop_graph)
            except Exception as e:
                print(f"Error dropping graph for type {type}_{i}: {e}")

            
    def create_temporary_graph(self):
        type = self.type

        for i in range(self.range[0], self.range[1] + 1):
            query = f"""
            CALL gds.graph.project(
            'myGraph{str(type)}_{str(i)}',
            '{str(type)}_{str(i)}',
            'UNIVERSITY_CITES',
            {{ relationshipProperties: ['weight'] }}
            )
            """
            try:
                self.node_pull.run_query(query=query)
            except Exception as e:
                print(f"Error creating temporary graph for type {type}_{i}: {e}")
        
            
            
    def get_page_rank_from_temp_graphs(self):
        type = self.type

        query = f"""
        CALL gds.pageRank.stream('myGraph{str(type)}', {{
          maxIterations: 20,
          dampingFactor: 0.85,
          relationshipWeightProperty: 'weight',
          scaler: "MinMax"
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).name AS name, score, gds.util.asNode(nodeId).countries AS countries
        ORDER BY score DESC, name ASC
        
        
        """
        result = self.connector.run_query(query=query)
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
            
            data = [(record[index_field], record['score'], record['countries'][0])for record in result]
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

        df = df.T
        df.index.name = "Year"  
        # df = df[-16:]

        bucket_size = 2
        upper_bound = df.index.max()
        lower_bound = df.index.min()
        if upper_bound < lower_bound:
            upper_bound, lower_bound = lower_bound, upper_bound
        bins = range(lower_bound, upper_bound, bucket_size)  # Bin edges

        labels = [i for i in range(lower_bound, upper_bound, bucket_size)]  # Labels for the bins
        labels = labels[:-1]

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

     
        grouped_data = {}
        for i, part in enumerate(last_part):
            if part not in grouped_data:
                grouped_data[part] = []
            grouped_data[part].append(df.iloc[:, i])

     
        aggregated_df = {}
        for part, columns in grouped_data.items():
            aggregated_df[part] = pd.concat(columns, axis=1).sum(axis=1)

     
        aggregated_df = pd.DataFrame(aggregated_df)
        aggregated_df = aggregated_df.loc[:, ["States", "Russia"]]

        aggregated_df.plot(figsize=(10, 6))
        plt.title("Metrics Over Years")
        plt.xlabel("Year")
        plt.ylabel("Metric")
        plt.legend(title="Universities", bbox_to_anchor=(1.05, 1), loc="upper left") 
        plt.grid()
        plt.show()

    def visualise_aggr_by_countries(self, df=None, bucketed=False, bucket_size=2, picked_countries=None, aggregated_for_countries=None):
        if df is None:
            df = self.df
       
        df = df.T
        df.index.name = "Year" 
        # df = df[-16:]

        if bucketed:
            upper_bound = df.index.max()
            lower_bound = df.index.min()
            if upper_bound < lower_bound:
                upper_bound, lower_bound = lower_bound, upper_bound
            bins = range(lower_bound, upper_bound, bucket_size) 

            labels = [i for i in range(lower_bound, upper_bound, bucket_size)] 
            labels = labels[:-1]
            
            df["decade"] = pd.cut(df.index, bins=bins, labels=labels, right=False)

            aggregated_df = df.groupby("decade").sum()

            aggregated_df = aggregated_df.reset_index().set_index('decade')
                
            if aggregated_for_countries:
                country_name = [col.split(' IN ')[-1] for col in df.columns]

       
                grouped_data = {}
                for i, part in enumerate(country_name):
                    if part not in grouped_data:
                        grouped_data[part] = []
                    grouped_data[part].append(df.iloc[:, i])

     
                aggregated_df = {}
                for part, columns in grouped_data.items():
                    aggregated_df[part] = pd.concat(columns, axis=1).sum(axis=1)

         
                df = pd.DataFrame(aggregated_df)
                if picked_countries:
                    df = df.loc[:, picked_countries]
            else:
                if picked_countries:
                    print(df.columns)
                    df = df.loc[:, df.columns.str.contains('|'.join(picked_countries))]
            # aggregated_df = aggregated_df.loc[:, ['States', 'Russia']]
            self.plot(df)

    def plot(self, df=None):
        if df is None:
            df = self.df
        df.plot(figsize=(10, 6))
        plt.title("Page Rank Over Years")
        plt.xlabel("Year")
        plt.ylabel("Metric")
        plt.legend(title="Universities", bbox_to_anchor=(1.05, 1), loc="upper left") 
        plt.grid()
        plt.show()


class PaperDataCollector(DataCollector):
    def __init__(self, range):
        super().__init__(range, "Paper")


    def pull(self, limit=100):
        queried_fields = ["closeness", "degree", "pagerank", "articlerank", "louvain", "approxBetweenness"]
        queried_fields = ["pagerank"]
        with self.connector.driver.session() as session:
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
        """example of result:
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
        labels = self.connector.get_unique_vals("Paper", for_type)
        df = pd.DataFrame(columns=labels)

        with open("statistics.json", "r", encoding="utf-8") as file:
            stats = json.load(file)
            for label, metrics in stats.items():
                for metric, data in metrics.items():

                    if metric != picked_metric:
                        continue
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

            # os.makedirs(f"top_n/{picked_metric}/", exist_ok=True)
            # df.to_csv(f"top_n/{picked_metric}/statistics_{label}_{picked_metric}_{for_type}.csv")

            df.plot(kind="line", marker="o")
            plt.title("Line Plot of Multiple Rows")
            plt.xlabel("Index")
            plt.ylabel("Values")
            plt.show()
