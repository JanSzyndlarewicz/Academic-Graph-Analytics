import json


class DownloadStatusHandler:
    def __init__(self, download_status_file):
        self.download_status_file = download_status_file

    def get_next_url_to_download(self) -> str | None:
        with open(self.download_status_file, "r") as file:
            links_status = json.load(file)

        for url, status in links_status.items():
            if not status.get("downloaded"):
                return url

    def set_url_as_downloaded(self, url: str):
        with open(self.download_status_file, "r") as file:
            links_status = json.load(file)

        links_status[url]["downloaded"] = True

        with open(self.download_status_file, "w") as file:
            json.dump(links_status, file, indent=4)

    def get_all_urls(self):
        with open(self.download_status_file, "r") as file:
            links_status = json.load(file)

        return links_status.keys()

    def get_all_urls_to_download(self):
        with open(self.download_status_file, "r") as file:
            links_status = json.load(file)

        return [url for url, status in links_status.items() if not status.get("downloaded")]

    def prepare_new_db(self, urls):
        links_status = {}
        for url in urls:
            links_status[url] = {"downloaded": False}

        with open(self.download_status_file, "w") as file:
            json.dump(links_status, file, indent=4)
