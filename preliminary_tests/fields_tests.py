from collections import defaultdict
import json
import jsonlines
import os
import matplotlib.pyplot as plt

def get_fields_occurances(path):
    fields = defaultdict(int)
    with jsonlines.open(path) as papers:
        for paper in papers:
            for key in paper.keys():
                fields[key] += 1
    fields = sorted(fields.items(), key=lambda x: x[1], reverse=False)
    return fields

def visualise_field_length_distribution(path, field="affiliation"):
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
    
def main():
    print(get_fields_occurances(moscow_path))
    visualise_field_length_distribution(pwr_agriculture_path)

if __name__ == "__main__":
    # por que no esta funcionando el path?
    json_path = os.path.join(os.getcwd(), "data", "test_batch.jsonl")
    moscow_path = r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\60021331-econ-batch.jsonl"
    pwr_agriculture_path = r"C:\Users\aleks\Pulpit\CarlosIII4sem\web analytics\final_project\Academic-Graph-Analytics\preliminary_tests\data\test_batch.jsonl"
    main()