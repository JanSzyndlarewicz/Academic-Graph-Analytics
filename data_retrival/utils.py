import gzip
import json
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
    with open(filename, "a", encoding="utf-8") as f:
        for paper in data:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
