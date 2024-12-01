import json

import jsonlines


def test_field_presence(fields, file_path):
    for field_name in fields:
        i = 0
        j = 0
        with jsonlines.open(file_path) as papers:
            for paper in papers:
                field_value = paper.get(field_name, None)
                if field_value: i += 1 
                j += 1
                #print(field_value)
        print(f"Field  {field_name} present in  {100 * i / j:.2f}% records.")

fields = ["prism:doi", "prism:coverDate"]
#test_field_presence(fields, 'test_batch.jsonl')
test_field_presence(fields, '60021331-econ-batch.jsonl')