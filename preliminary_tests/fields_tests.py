from datetime import datetime
import json
import os
import re
from collections import Counter, defaultdict
import textdistance
import jsonlines
import matplotlib.pyplot as plt
import requests

from config import country2uni_institutions_names, country2unis_names


def get_fields_occurances(path):
    fields = defaultdict(int)
    with jsonlines.open(path) as papers:
        for paper in papers:
            for key in paper.keys():
                fields[key] += 1
    fields = sorted(fields.items(), key=lambda x: x[1], reverse=False)
    return fields


def visualise_field_lengths_distribution(path, field="affiliation"):
    counts = defaultdict(int)
    with jsonlines.open(path) as papers:
        for paper in papers:
            if field not in paper:
                counts[0] += 1
            else:
                counts[len(paper[field])] += 1
    counts = sorted(counts.items(), key=lambda x: x[0], reverse=False)
    plt.bar([str(x[0]) for x in counts], [x[1] for x in counts])
    plt.title(f"Distribution of {field} field lengths in {os.path.basename(path)}")
    plt.show()


def get_mean_difference_cover_cover_display_dates_years(path):
    differences = []
    with jsonlines.open(path) as papers:
        for paper in papers:
            if "prism:coverDate" in paper and "prism:coverDisplayDate" in paper:
                try:
                    cover_date_year = int(re.findall(r"\d{4}", paper["prism:coverDate"])[0])
                    cover_display_date_year = int(re.findall(r"\d{4}", paper["prism:coverDisplayDate"])[0])
                    differences.append(cover_date_year - cover_display_date_year)
                except:
                    print(paper["prism:coverDate"], paper["prism:coverDisplayDate"], "could not be parsed")

    return sum(differences) / len(differences)


def visualise_field_value_distribution(path, field="prism:coverDate", show_every=20, regex=None):
    with jsonlines.open(path) as papers:
        if regex:
            counts = Counter(
                [
                    re.findall(regex, paper[field])[0]
                    for paper in papers
                    if field in paper and re.search(regex, paper[field])
                ]
            )
        else:
            counts = Counter([paper[field] for paper in papers if field in paper])
    counts = sorted(counts.items(), key=lambda x: x[0], reverse=False)

    x_values = [str(x[0]) for x in counts]
    y_values = [x[1] for x in counts]

    plt.bar(x_values, y_values)

    plt.xticks(ticks=range(0, len(x_values), show_every), labels=x_values[::show_every], rotation=90)

    plt.title(f"Distribution of {field} field values in {os.path.basename(path)}")
    plt.show()


def visualise_affiliation_field_values_distribution(path, sub_field="affilname", show_every=20):
    counts = defaultdict(int)
    with jsonlines.open(path) as papers:
        for paper in papers:
            if "affiliation" in paper:
                if isinstance(paper["affiliation"], list):
                    for value in paper["affiliation"]:
                        counts[value[sub_field]] += 1
                else:
                    counts[paper["affiliation"][sub_field]] += 1

    if "Russian Federation" in counts:
        del counts["Russian Federation"]
    counts = sorted(counts.items(), key=str, reverse=False)

    x_values = [str(x[0]) for x in counts]
    y_values = [x[1] for x in counts]

    # Plot the bar chart
    plt.bar(x_values, y_values)

    plt.xticks(ticks=range(0, len(x_values), show_every), labels=x_values[::show_every], rotation=90)

    plt.title(f"Distribution of affiliation field values in {os.path.basename(path)}")
    plt.show()


def get_sample_field_values(path, field="affiliation", sample_size=10):
    values = []
    with jsonlines.open(path) as papers:
        for paper in papers:
            if field in paper:
                values.extend(paper[field])
            if len(values) > sample_size:
                break
    return values


# def get_best_affils_for_uni_names(save_path, country2uni_names):
#     http_link_no_affil = "https://api.elsevier.com/content/search/affiliation?apiKey=c3818bd39b42c0db849380bbf544771e&query=affil({})"
#     for country, uni_names in country2uni_names.items():
#         for uni_name in uni_names:
#             print(http_link_no_affil.format(uni_name))
#             response = requests.get(http_link_no_affil.format(uni_name))
#             with open(save_path, "w") as file:
#                 json.dump(, file)
                

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
            headers = {"X-ELS-APIKey": SCOPUS_KEY, "Accept": "application/json"}
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
                        "name_variant": affil.get("name-variant", [])[0].get("$", "N/A") if affil.get("name-variant") else "N/A",
                        "document-count": affil.get("document-count", "N/A"),
                        "city": affil.get("city", "N/A"),
                        "eid": affil.get("eid", "N/A"),
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
        json.dump(return_dict, file, indent=4, ensure_ascii=False)

    print("Data successfully saved to 'best_affils_for_top_unis.json'")

def check_for_duplicates(path):
    set_of_affils = defaultdict(list)
    with open("./data/best_affils_for_top_unis_05-22-15.json", encoding="utf-8") as file:
        print("Loading data...")
        countries2uni2best_affils = json.load(file)
        print("Data loaded.")
        for country, uni2best_affils in countries2uni2best_affils.items():
            for best_affils in uni2best_affils:
                for affil_name, best_affils_pars in best_affils.items():
                    for rank, best_affil_pars in enumerate(best_affils_pars):
                        print(type(best_affil_pars))
                        if best_affil_pars['affiliation-name'] in set_of_affils:
                            print(f"Duplicate found: {best_affil_pars}")
                        set_of_affils[best_affil_pars['affiliation-name']].append([rank, country, best_affil_pars])
    duplicates_pairs = {}
    for key, val in set_of_affils.items():
        if len(val) > 1:
            duplicates_pairs[key] = val
    with open("./data/duplicates.json", "w", encoding="utf-8") as file:
        json.dump(duplicates_pairs, file, indent=4, ensure_ascii=False)
        
def  check_which_unis_dont_have_exact_matches(path):
    set_of_affils = {}
    with open(path, encoding="utf-8") as file:
        print("Loading data...")
        countries2uni2best_affils = json.load(file)
        print("Data loaded.")
        for country, uni2best_affils in countries2uni2best_affils.items():
            for best_affils in uni2best_affils:
                for affil_name, best_affils_pars in best_affils.items():
                    is_exact_match = False
                    for rank, best_affil_pars in enumerate(best_affils_pars):
                        if affil_name == best_affil_pars['affiliation-name']:
                            # print(f"Exact match found:{affil_name} {best_affil_pars['affiliation-name']}")
                            is_exact_match = True
                            break
                    if not is_exact_match:
                        # print(f"No exact match found for {best_affil_pars}")
                        # best_affils_pars = sorted(best_affils_pars,
                        #                         #   key=lambda x: textdistance.levenshtein.normalized_similarity(affil_name, x['affiliation-name']),
                        #                         key = lambda x: int(x["document-count"]),
                        #                           reverse=True)
                        print("Before sorting:")
                        print(len(best_affils_pars))
                        for item in best_affils_pars:
                            print(f"{item['affiliation-name']} - {item.get('document-count')}")
                        
                        
                        # best_affils_pars = sorted(
                        #     best_affils_pars,
                        #     key=lambda x: int(x.get("document-count", 0)),
                        #     reverse=True
                        # )
                        best_affils_pars_sorted = sorted(best_affils_pars,
                                                #   key=lambda x: textdistance.levenshtein.normalized_similarity(affil_name, x['affiliation-name']),
                                                key = lambda x: int(x["document-count"]),
                                                  reverse=True)

                        print("After sorting:")
                        print(len(best_affils_pars))
                        for item in best_affils_pars:
                            print(f"{item['affiliation-name']} - {item.get('document-count')}")
                            
                        set_of_affils[affil_name] = best_affils_pars_sorted
    
    with open("./data/without_clear_match.json", "w+", encoding="utf-8") as file:
        json.dump(set_of_affils, file, indent=4, ensure_ascii=False)

def main():
    # print(get_fields_occurances(moscow_path))
    # print(get_sample_field_values(moscow_path))
    # visualise_field_length_distribution(pwr_agriculture_path)
    # print(get_mean_difference_cover_cover_display_dates_years(moscow_path))
    # visualise_field_value_distribution(moscow_path, regex=r"^.{4}", field="prism:coverDate", show_every=1)
    # sub_field = (
    #     # "affilname"
    #     "affiliation-country"
    #     # "affiliation-city"
    # )
    # visualise_affiliation_field_values_distribution(moscow_path, sub_field=sub_field, show_every=1)

    # regex allows for aggregation of months
    # visualise_field_value_distribution(pwr_agriculture_path, regex=r"(?<=-)[^-\d]*\d{2}", show_every=1)
    # pull_all_affils_matches_for_each_top_uni(country2unis_names)
    # check_for_duplicates("./data/best_affils_for_top_unis_06-02-13.json")
    check_which_unis_dont_have_exact_matches("./data/best_affils_for_top_unis_06-02-13.json")


if __name__ == "__main__":
    # por que no esta funcionando el path?
    # json_path = os.path.join(os.getcwd(), "data", "test_batch.jsonl")
    moscow_path = r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\60021331-econ-batch.jsonl"
    pwr_agriculture_path = r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\test_batch.jsonl"
    main()
    
