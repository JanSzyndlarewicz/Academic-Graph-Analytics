import gzip
import json
import os
import random
import shutil
from urllib.parse import urlparse

import requests


def get_base_url(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path


def find_full_url(base_url: str, urls: list[str]) -> str | None:
    for url in urls:
        if base_url == get_base_url(url):
            return url
    return None


def get_file_name_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.path.split("/")[-1]


def unpack_gz_file(file_path: str, output_folder: str) -> None:
    with gzip.open(file_path, "rb") as f_in:
        with open(output_folder, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def download_file(url: str, file_path: str) -> None:
    response = requests.get(url)
    with open(file_path, "wb") as file:
        file.write(response.content)


def process_json_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield json.loads(line)


def save_to_json_lines(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        for paper in data:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")


def append_to_json_lines(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a", encoding="utf-8") as f:
        for paper in data:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")


def get_all_files_paths_recursively(folder_path: str) -> list[str]:
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


def merge_json_lines_files(files: list[str], output_file: str) -> None:
    with open(output_file, "a", encoding="utf-8") as f:
        for file in files:
            with open(file, "r", encoding="utf-8") as file:
                for line in file:
                    f.write(line)


def find_all_folders(base_path):
    folders = []
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            folders.append(os.path.join(root, dir_name))
    return folders


def get_file_with_parent_folder(path):
    file_name = os.path.basename(path)
    parent_folder = os.path.basename(os.path.dirname(path))
    return f"{parent_folder}/{file_name}"


def load_dataset_mapping(mapping_file_path):
    dataset_mapping = {}
    with open(mapping_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('Total'):
                parts = line.split(':')
                if len(parts) == 2:
                    university_info, _ = parts
                    if '(' in university_info:
                        university_id, university_name = university_info.split('(', 1)
                        university_name = university_name.rstrip(') ')
                        dataset_mapping[university_id.strip()] = university_name.strip()
    return dataset_mapping

def save_citations_to_files(citations_among_dataset, output_dir, chunk_size):
    os.makedirs(output_dir, exist_ok=True)

    # shuffle the list of citations to minimalize lock during threads processign
    random.shuffle(citations_among_dataset)

    for i in range(0, len(citations_among_dataset), chunk_size):
        chunk = citations_among_dataset[i:i + chunk_size]
        file_path = os.path.join(output_dir, f"citations_{i // chunk_size + 1}.jsonl")
        with open(file_path, 'w') as f:
            for citation in chunk:
                f.write(json.dumps(citation) + "\n")