import json
import os
import re
from collections import Counter, defaultdict

import jsonlines
import matplotlib.pyplot as plt


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
                    cover_date_year = int(re.findall(r'\d{4}', paper["prism:coverDate"])[0])
                    cover_display_date_year = int(re.findall(r'\d{4}', paper["prism:coverDisplayDate"])[0])
                    differences.append(cover_date_year - cover_display_date_year)
                except:
                    print(paper["prism:coverDate"], paper["prism:coverDisplayDate"], "could not be parsed")
                
    return sum(differences) / len(differences)


def visualise_field_value_distribution(path, field="prism:coverDate", show_every=20, regex=None):
    with jsonlines.open(path) as papers:
        if regex:
            counts = Counter([re.findall(regex, paper[field])[0] for paper in papers if field in paper and re.search(regex, paper[field])])
        else:
            counts = Counter([paper[field] for paper in papers if field in paper])
    counts = sorted(counts.items(), key=lambda x: x[0], reverse=False)
    
    x_values = [str(x[0]) for x in counts]
    y_values = [x[1] for x in counts]
    
    plt.bar(x_values, y_values)
    
    plt.xticks(ticks=range(0, len(x_values), show_every), labels=x_values[::show_every], rotation=45)
    
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
        
    if 'Russian Federation' in counts:
        del counts['Russian Federation']
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


def main():
    # print(get_fields_occurances(moscow_path))
    # print(get_sample_field_values(moscow_path))
    # visualise_field_length_distribution(pwr_agriculture_path)
    # print(get_mean_difference_cover_cover_display_dates_years(moscow_path))
    # visualise_field_value_distribution(moscow_path)
    sub_field = (
        # "affilname" 
        "affiliation-country"
        # "affiliation-city"
        )
    # visualise_affiliation_field_values_distribution(moscow_path, sub_field=sub_field, show_every=1)
    
    # regex allows for aggregation of months
    visualise_field_value_distribution(pwr_agriculture_path, regex=r"(?<=-)[^-\d]*\d{2}", show_every=1)

    

if __name__ == "__main__":
    # por que no esta funcionando el path?
    # json_path = os.path.join(os.getcwd(), "data", "test_batch.jsonl")
    moscow_path = r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\60021331-econ-batch.jsonl"
    pwr_agriculture_path = r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\test_batch.jsonl"
    main()