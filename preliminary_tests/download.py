import jsonlines
import json
import logging
import os
from pathlib import Path
import requests
import sys
import urllib.parse


from config import PAPER_SEARCH_URL, SAFETY_LIMIT, SCOPUS_KEY

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

fileHandler = logging.FileHandler("download.log")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

#Note on API parameters:
#query - we can use:
#        af-id([ID]) to get papers from a specific institutions, with ID being Scopus' internal 
#           identificator for this institution, for example af-id(60019987) queries papers from
#           the Wroclaw University of Science and Technology. Use affiliation search 
#           (https://dev.elsevier.com/documentation/AffiliationSearchAPI.wadl) to obtain the id
#           based on name
#        affilcountry([COUNTRY]) to get papers from a specific country, mind that sometimes there
#           might be incosistent names, e.g. we can use russia* to catch both 'russia' and 'russian federation'
#subj - field of research, see https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl for a list
#cursor - handles pagination, use * to begin iteration, then each resposnse will contain url of the next
#        page
#httpAccept - use application/json to get json rather then the default xml
#apiKey - self explanatory
#view - use standard to get 200 papers per requests rather than just 25
#count - number of papers in a request, can go up to 200 with view=standard

def save_entries_to_jsonlines(json_response, output_path):
    entries = json_response.get("search-results", []).get("entry", [])
    if entries:
        with jsonlines.open(output_path, 'a') as writer:
            writer.write_all(entries)
        return True
    return False 

def get_from_api(url):
    logger.info(f"Querying {url}")
    res = requests.get(url)
    #print("Querying " + res.url)
    if res.status_code == 200:
        logger.info(f"Query {url} succesfull!")
        return res.json()
    logger.warning(f"Query {url} failed")
    return None

def get_next_url(json_response, expected_entries : int) -> str | None:
    if ("entry" not in json_response['search-results']) or (len(json_response['search-results']['entry']) < expected_entries):
        return None
    for link in json_response['search-results']['link']:
        if link['@ref']=='next':
            return link['@href']
    

def save_all_entries(output_path, **params):
    #default settings that can be overriden if needed
    if not "cursor" in params: params["cursor"] = "*"
    if not "view" in params: params["view"] = "standard"
    if not "count" in params: params["count"] = "200"
    if not "httpAccept" in params: params["httpAccept"] = "application/json"

    logger.info(f"Beginning a query series, parameters {params}")

    url = PAPER_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    not_done = True
    i = 0
    while not_done:
        j = get_from_api(url)
        if j is None:
            logger.warning(f"Query failed, query series aborted.")
            break
        not_done = save_entries_to_jsonlines(j, output_path)
        url = get_next_url(j, int(params["count"]))
        if url is None:
            logger.info(f"Query series finished.")
            not_done = False
        
        #this is just because I am paranoid that I will accidentally create an infite loop and burn all my requests
        #set SAFETY_LIMIT to whatever you feel is reasonable or just get rid of this clause if you know what you are doing
        i +=1 
        if i >= SAFETY_LIMIT:
            logger.warning(f"Safety limit reached, query series aborted.")
            return
        
def save_by_institutions_and_fields(institutions : list[str], fields : list[str], apiKey : str, country_mapping : dict = None):
    for institution in institutions:
        dir_path = Path(__file__).parent / "data"
        if country_mapping is not None:
            dir_path = dir_path / country_mapping.get(institution, "unknown")
        if not dir_path.exists():
            dir_path.mkdir()
        for field in fields:           
            output_path = dir_path / f"{institution}-{field}.jsonl"
            logger.info(f"Beginning data collection for institution {institution} and field {field}, output file: {output_path}")
            query = f"af-id({institution})"
            save_all_entries(output_path, query=query, subj=field, apiKey=apiKey)

def read_unis_file(path, countries):
    with open(path, "r") as file:
        data = json.load(file)
    institutions = []
    country_mapping = {}
    for entry in data:
        if entry['country'] in countries:
            institutions.append(entry['id'])
            country_mapping[entry['id']] = entry['country']
    return institutions, country_mapping

if __name__ == "__main__":

    #DOWNLOAD DATA FOR UNIS FROM JSON
    # countries = ["United States", "Russia"]
    # institutions, country_mapping = read_unis_file("preliminary_tests\\best_affils_for_top_unis_01-17-42_transformed.json", countries)
    # save_by_institutions_and_fields(institutions, ["econ"], SCOPUS_KEY, country_mapping=country_mapping)

    #DOWNLAOD DATA FOR UNIS FROM LIST
    # fields = ["mult", "vete"]
    # institutions = ["60019987", "60008555"]
    # country_mapping = {"60019987" : "Poland", "60008555" : "Poland"}
    # save_by_institutions_and_fields(institutions, fields, SCOPUS_KEY, country_mapping)
    pass