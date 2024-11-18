import json
import logging
import os

logger = logging.getLogger(__name__)


def convert_citations_json_to_csv(input_file_path: str, output_file_path: str):
    logger.info(f"Converting {input_file_path} to {output_file_path}.")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    row_counter = 0

    with open(input_file_path, "r", encoding="utf-8") as input_file, open(
        output_file_path, "w", encoding="utf-8"
    ) as output_file:

        output_file.write("citingcorpusid,citedcorpusid,citationid,isinfluential\n")

        for line in input_file:
            try:
                data = json.loads(line)

                if data["citingcorpusid"] is not None and data["citedcorpusid"] is not None:
                    output_file.write(
                        f"{data['citingcorpusid']},{data['citedcorpusid']},{data['citationid']},{data.get('isinfluential', False)}\n"
                    )
                    row_counter += 1
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
            except Exception as e:
                logger.error(f"Error processing line: {e}")

    logger.info(f"Finished processing {row_counter} lines into {output_file_path}.")


def merge_csv_files(input_folder: str, output_file_path: str):
    logger.info(f"Merging CSV files from {input_folder} into {output_file_path}.")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("citingcorpusid,citedcorpusid,citationid,isinfluential\n")

        for file_name in os.listdir(input_folder):
            if file_name.endswith(".csv"):
                with open(os.path.join(input_folder, file_name), "r", encoding="utf-8") as input_file:
                    next(input_file)
                    for line in input_file:
                        output_file.write(line)

    logger.info(f"Finished merging CSV files into {output_file}.")
