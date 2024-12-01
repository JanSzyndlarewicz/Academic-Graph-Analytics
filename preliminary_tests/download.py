import json
import urllib.parse

import jsonlines
import requests

from config import PAPER_SEARCH_URL, SAFETY_LIMIT, SCOPUS_KEY

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
    res = requests.get(url)
    print("Querying " + res.url)
    if res.status_code == 200:
        return res.json()
    return None

def get_next_url(json_response):
    if "entry" not in json_response['search-results']:
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

    url = PAPER_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    not_done = True
    i = 0
    while not_done:
        j = get_from_api(url)
        if j is None:
            break
        not_done = save_entries_to_jsonlines(j, output_path)
        url = get_next_url(j)
        if url is None:
            not_done = False
        
        #this is just because I am paranoid that I will accidentally create an infite loop and burn all my requests
        #set SAFETY_LIMIT to whatever you feel is reasonable or just get rid of this clause if you know what you are doing
        i +=1 
        if i >= SAFETY_LIMIT:
            return

if __name__ == "__main__":
    #save_all_entries("test_batch.jsonl", query="af-id(60019987)", subj="agri", apiKey=SCOPUS_KEY)
    #save_all_entries("60021331-econ-batch.jsonl", query="af-id(60021331)", subj="econ", apiKey=SCOPUS_KEY)
    pass