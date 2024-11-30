from collections import defaultdict
import json
import os

def getFieldsAppearance(path):
    fields = defaultdict(int)
    with open(path, 'r') as file:
        for line in file:
            line = json.loads(line)
            for key in line.keys():
                fields[key] += 1
    fields = sorted(fields.items(), key=lambda x: x[1], reverse=True)

def main():
    print(getFieldsAppearance(json_path))

if __name__ == "__main__":
    json_path = os.path.join(os.getcwd(), "data", "test_batch.jsonl")
    main()