from matplotlib import pyplot as plt
from data_retrival.neo4j.neo4j_connector import Neo4JConnector
import pandas as pd

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
                result = [record.data()['n'] for record in result]                    
                return result
            
    def count_nodes(self, type, condition=None):
        if condition:
            query = f"MATCH (n:{type}) WHERE {condition} RETURN COUNT(n) AS node_count"
        else:
            query = f"MATCH (n:{type}) RETURN COUNT(n) AS node_count"
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query)
                result = result.single().data()['node_count']
                return result
        
    def fetch_in_batches(self, query, batch_size):
        offset = 0
        all_results = []

        while True:
            batch_query = f"{query} SKIP {offset} LIMIT {batch_size}"
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    result = tx.run(batch_query)
                    batch = [record['n'] for record in result] 
                    if not batch:
                        break 
                    all_results.extend(batch)
            offset += batch_size

        return all_results
    

            
class UniDataCollector():
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
            
    def make_df(self, metric, index_field=None):
        if not index_field:
            index_field = self.index_field
        df = None
        for i in range(self.range[0], self.range[1] + 1):
            scoped_type = self.node_pull.type + "_" + str(i)
            
            try:
                result = self.get_page_rank_from_temp_graphs(type=scoped_type)
                result = sorted(result, key=lambda x: x['name'])
                print(result)
            except Exception as e:
                print(f"Error fetching nodes for type {scoped_type}: {e}")
                continue
            
            data = [(record[index_field], record['score'], record['country'][0])for record in result]
            appended_df = pd.DataFrame(
                {
                        i: [tup[1] for tup in data],                        
                },
                index=[tup[0]+" IN "+tup[2] for tup in data]
            )
            if df is None:
                df = appended_df
            else:
                df = pd.concat([df, appended_df], axis=1) 
        self.df = df
        return df
    
    def visualise(self, df=None):
        if df is None:
            df = self.df
        # Transpose the DataFrame to make years the index
        df = df.T
        df.index.name = 'Year'  # Rename the index to 'Year'
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
        
        last_part = [col.split(' ')[-1] for col in df.columns]

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
        aggregated_df = aggregated_df.loc[:, ['States', 'Russia']]
        # Plot
        aggregated_df.plot(figsize=(10, 6))
        plt.title("Metrics Over Years")
        plt.xlabel("Year")
        plt.ylabel("Metric")
        plt.legend(title="Universities", bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside plot
        plt.grid()
        plt.show()
    
    def append_to_df(self, ):
        pass
        
    