import os

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from data_retrival.neo4j.neo4j_connector import Neo4JConnector

def purge_countries(conn):
    query = f"MATCH (n:Country) DETACH DELETE n"
    conn.run_query(query)

def divide_into_year_buckets(conn, start, end):
    _divide_into_year_buckets(conn, [str(x) for x in list(range(start,end))])

def _divide_into_year_buckets(conn, years):
    query = f"""with {years} as years
            unwind years as year
            MATCH (base:Paper)<-[:CITED_BY]-(cited:Paper)
            WHERE DATE(base.publication_date) <= DATE(year+'-12-31')
            WITH year, base.countries AS base_countries, cited.countries AS cited_countries
            UNWIND base_countries AS base_country
            UNWIND cited_countries AS cited_country
            MERGE (bc:Country {{name: base_country, bucket: year}})
            MERGE (cc:Country {{name: cited_country, bucket: year}})
            MERGE (bc)-[r:COUNTRY_CITES]->(cc)
            ON CREATE SET r.weight = 1
            ON MATCH SET r.weight = r.weight + 1
            MERGE (cc)-[s:COUNTRY_CITED_BY]->(bc)
            ON CREATE SET s.weight = 1
            ON MATCH SET s.weight = s.weight + 1"""
    conn.run_query(query)

def get_citation_fractions_years(conn, start, end):
    result = None
    for year in [str(x) for x in list(range(start,end))]:
        if result is None:
            result = get_citation_fractions_year(conn, year)
        else:
            tmp = get_citation_fractions_year(conn, year)
            result = pd.concat([result,tmp], ignore_index=True)
    result = result.fillna(0)
    return result

def get_citation_fractions_year(conn, year):
    query = f"""match (n:Country {{bucket:"{year}"}})<-[e:COUNTRY_CITED_BY]-(k:Country)
               return n.bucket as Year, n.name as Citing, k.name as Cited, e.weight as Count"""
    result = conn.run_query(query)
    result = pd.DataFrame(result)
    result["Year"] = result["Year"].astype("int32")
    sums = result.groupby(["Citing"])[["Count"]].sum()
    result["Proportion"] = result.apply(lambda x : x["Count"] / sums.loc[x["Citing"]], axis=1)
    return result

def get_foreign_citation_per_paper_ratio_years(conn, start, end):
    result = None
    for year in [str(x) for x in list(range(start,end))]:
        if result is None:
            result = get_foreign_citation_per_paper_ratio_year(conn, year)
        else:
            tmp = get_foreign_citation_per_paper_ratio_year(conn, year)
            result = pd.concat([result,tmp], ignore_index=True)
    result = result.fillna(0)
    return result

def get_foreign_citation_per_paper_ratio_year(conn, year):
    query = f"""match (n:Country {{bucket : "{year}"}})
                with n as country
                match (n:Paper) where country.name in n.countries and Date(n.publication_date) <= Date("{year+"-12-31"}")
                with country, count(distinct n) as papers
                match (n:Paper)-[e:CITED_BY]->(k:Paper)
                where country.name in n.countries and not country.name in k.countries and Date(k.publication_date) <= Date("{year+"-12-31"}")
                return country.name as Country, country.bucket as Year, papers as Papers, count(e) as Foreign_citations, count(e) * 1.0 / papers as Ratio"""
    result = conn.run_query(query)
    result = pd.DataFrame(result)
    result["Year"] = result["Year"].astype("int32")
    return result

def plot_self_citation_fractions(df):
    _plot_self_citations_fractions_join(df)
    _plot_self_citations_fractions_seperate(df)


def _plot_self_citations_fractions_join(df):
    data = df[(df["Citing"] == df["Cited"])]
    sns.lineplot(data, x="Year", y="Proportion", hue="Citing").set(title=f"Proportions of self-citations")
    os.makedirs("plots/self_proportion",exist_ok=True)
    plt.savefig(f"plots/self_proportion/self_proportions.jpg")
    plt.clf()

def _plot_self_citations_fractions_seperate(df):
    for country in df["Citing"].unique():
        data = df[(df["Citing"] == country) & (df["Cited"] == country)]
        sns.lineplot(data, x="Year", y="Proportion").set(title=f"{country}-{country}")
        os.makedirs("plots/self_proportion",exist_ok=True)
        plt.savefig(f"plots/self_proportion/{country}_self_proportion.jpg")
        plt.clf()

def plot_citation_fractions_to_country(df, country):
    _plot_citation_fractions_to_country_join(df, country)
    _plot_citation_fractions_to_country_seperate(df, country)

def _plot_citation_fractions_to_country_join(df, country):
    data = df[(df["Cited"] == country) & (df["Citing"] != country)]
    sns.lineplot(data, x="Year", y="Proportion", hue="Citing").set(title=f"Proportions of citations to Russia")
    os.makedirs("plots/russia_proportion",exist_ok=True)
    plt.savefig(f"plots/russia_proportion/russia_proportions.jpg")
    plt.clf()

def _plot_citation_fractions_to_country_seperate(df, target_country):
    for country in df["Citing"].unique():
        data = df[(df["Citing"] == country) & (df["Cited"] == target_country)]
        sns.lineplot(data, x="Year", y="Proportion").set(title=f"{country}-{target_country}")
        os.makedirs("plots/russia_proportion",exist_ok=True)
        plt.savefig(f"plots/russia_proportion/{country}_{target_country}_proportion.jpg")
        plt.clf()

def plot_foreign_citation_to_paper_ratio(df):
    _plot_foreign_citation_to_paper_ratio_join(df)
    _plot_foreign_citation_to_paper_ratio_seperate(df)

def _plot_foreign_citation_to_paper_ratio_join(df):
    sns.lineplot(df, x="Year", y="Ratio", hue="Country").set(title=f"Foreign citations to papers ratio.")
    os.makedirs("plots/citation_to_paper_ratio",exist_ok=True)
    plt.savefig(f"plots/citation_to_paper_ratio/foregin_citations_to_paper_ratios.jpg")
    plt.clf()

def _plot_foreign_citation_to_paper_ratio_seperate(df):
    for country in df["Country"].unique():
        data = df[df["Country"] == country]
        sns.lineplot(data, x="Year", y="Ratio").set(title=f"{country} - foreing citations to papers ratio")
        os.makedirs("plots/citation_to_paper_ratio",exist_ok=True)
        plt.savefig(f"plots/citation_to_paper_ratio/{country}_foreign_citations_to_papers_ratio.jpg")
        plt.clf()

def generate_data_and_visualisations():
    conn = Neo4JConnector()

    purge_countries(conn)
    divide_into_year_buckets(conn, 2010,2025)
    
    df = (get_citation_fractions_years(conn,2010,2025))
    df.to_json("dataframe.json")

    plot_self_citation_fractions(df)

    plot_citation_fractions_to_country(df, "Russia")

    df = get_foreign_citation_per_paper_ratio_years(conn, 2010, 2025)
    df.to_json("dataframe2.json")

    plot_foreign_citation_to_paper_ratio(df)
