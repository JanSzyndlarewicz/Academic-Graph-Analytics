from collections import defaultdict
from datetime import datetime
import json
import os
import requests
from config import top_universities_by_country

from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\.env")


import os
import json
import requests
from collections import defaultdict

top_universities = top_universities_by_country

def pull_all_affils_matches_for_each_top_uni(top_universities):
    # Load your Scopus API key (ensure you've set it in your environment variables)
    SCOPUS_KEY = os.getenv("SCOPUS_KEY")
    if not SCOPUS_KEY:
        raise ValueError("SCOPUS_KEY not found. Make sure it's defined in your environment variables.")

    base_url = "https://api.elsevier.com/content/search/affiliation"
    return_dict = defaultdict(list)

    for country, universities in top_universities.items():
        for current_university in universities:
            params = {"query": f"affil({current_university})", "apiKey": SCOPUS_KEY}
            headers = {"X-ELS-APIKey": SCOPUS_KEY}

            try:
                response = requests.get(base_url, params=params, headers=headers)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                data = response.json()

                # Parse the results
                result_affils = data.get("search-results", {}).get("entry", [])
                result_affils = [
                    {
                        "affiliation-name": affil.get("affiliation-name", "N/A"),
                        "dc:identifier": affil.get("dc:identifier", "N/A"),
                        "country": affil.get("country", "N/A"),
                        "name_variant": affil.get("name-variant", [{}])[0].get("$", "N/A") if affil.get("name-variant") and affil.get("name-variant") != [] else "N/A",
                    }
                    for affil in result_affils
                ]

                return_dict[country].append({current_university: result_affils})

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {current_university}: {e}")
            except KeyError as e:
                print(f"Unexpected data structure for {current_university}: {e}")

    timestamp = datetime.now().strftime("%d-%H-%M")
    # Write the results to a file
    with open(f"best_affils_for_top_unis_{timestamp}.json", "w", encoding="utf-8") as file:
        json.dump(return_dict, file, indent=4)

    print("Data successfully saved to 'best_affils_for_top_unis.json'")
    
    
def check_pulled_affils():
    with open(r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\best_affils_for_top_unis_01-17-42.json", "r") as file:
        data = json.load(file)
        for country, universities in data.items():
            print("country",country, "universities count", len(universities))
            


def print_info_about_sample_affils_match():
    top_unis = top_universities
    with open(
        r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\sample_affils_new.json"
    ) as file:
        data = json.load(file)
        affils = data["search-results"]["entry"]
        for affil in affils:
            if affil["country"] in top_unis:
                if affil["affiliation-name"] in top_unis[affil["country"]]:
                    if "affiliation-name" in affil:
                        print(affil["affiliation-name"])
                    if "country" in affil:
                        print(affil["country"])
                    if "dc:identifier" in affil:
                        print(affil["dc:identifier"])
                    print("\n")


def print_info_about_peking_match():
    with open(
        r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\affils_for_peking_uni.json"
    ) as file:
        data = json.load(file)
        affils = data["search-results"]["entry"]
        for affil in affils:
            print(affil["affiliation-name"])
            print(affil["country"])


def main():
    # print_info_about_sample_match()
    # print_info_about_peking_match()
    # pull_all_affils_matches_for_each_top_uni(top_universities)
    check_pulled_affils()

if __name__ == "__main__":
    main()

