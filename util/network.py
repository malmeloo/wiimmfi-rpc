import base64
import logging

import requests

from .threading import Thread

github_headers = {
    'Accept': 'application/vnd.github.v3+json'
}


class GithubDownloadThread(Thread):
    friendly_progress = "Downloading file..."
    permanent = False

    def __init__(self, method, url, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.method = method
        self.url = url

        self.data = None

    def execute(self):
        file = self.url.split('/')[-1]
        file = file.split('?')[0]  # remove url params
        self.emit_message(f'Downloading {file}')

        resp = requests.request(self.method, self.url, headers=github_headers)

        resp.raise_for_status()

        data = resp.json()
        content = base64.b64decode(data['content'])

        self.log(logging.INFO, f'Successfully fetched file: {file}')
        self.emit_data({'file': file, 'content': content.decode()})
