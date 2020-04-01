import base64
import io
import json
import logging
import sys
from pathlib import Path

import requests
from PyQt5 import QtCore as Qc

from . import checks
from .msgboxes import MsgBoxes
from .threading import Thread

logging.getLogger(__name__)

data_dir = Path(sys.argv[0]).parent / 'data'
github_headers = {
    'Accept': 'application/vnd.github.v3+json'
}


class UpdateSignals(Qc.QObject):
    update_available = Qc.pyqtSignal(str)
    download_finished = Qc.pyqtSignal(io.BytesIO)


class Updater:
    def __init__(self, thread_manager, config):
        self.thread_manager = thread_manager
        self.config = config

        self.auto_download = config.preferences['config']['updates']['auto_download']
        self.auto_install = config.preferences['config']['updates']['auto_install']
        self.release_type = config.preferences['config']['updates']['release_type']

        self.current_version = config.version_info['version']

    def check_updates(self):
        """Check for and install updates."""
        update_zip = (data_dir / 'update.zip')
        if update_zip.is_file():  # local update installed
            with update_zip.open('r') as file:
                self.apply_update(file)
            update_zip.unlink()

        check_thread = UpdateCheckThread(self.config)
        check_thread.update_signals.update_available.connect(self.download_available)
        self.thread_manager.add_thread(check_thread)

    def apply_update(self, file=None):
        if not self.auto_install or checks.is_bundled():  # always show notif when we're bundled.
            msg = 'A new update is ready! Install it now?'
            if checks.is_bundled():
                msg += '\n\nWARNING: You\'re using the bundled version of this program,' \
                       'which might cause issues when performing an update. If this update' \
                       'renders the program unable to boot, please redownload it.'

            do_install = MsgBoxes.promptyesno(msg)
            if not do_install:
                return

        file.close()

    def download_update(self):
        download_thread = UpdateDownloadThread(self.config)
        download_thread.update_signals.download_finished.connect(self.apply_update)
        self.thread_manager.add_thread(download_thread)

    def download_available(self, new_version):
        if not self.auto_download:
            msg = 'A new update was found! Do you want to download it?\n\n'
            msg += f'New version:     {new_version}\n'
            msg += f'Current version: {self.current_version}'

            do_update = MsgBoxes.promptyesno(msg)
            if not do_update:
                return

        self.download_update()

    def install_available(self):
        msg = 'A new update is ready to be installed. Do you want to install it now?'
        if checks.is_bundled():
            msg += '\n\nWARNING: You\'re using the bundled version of this program. Updates might render it unusable.'

        do_install = MsgBoxes.promptyesno(msg)
        if do_install:
            self.apply_update()


class UpdateCheckThread(Thread):
    friendly_progress = 'Checking for updates...'
    permanent = False
    name = 'UpdateCheckThread'

    """Checks for and applies updates"""

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        self.update_signals = UpdateSignals()

        self.release_type = config.preferences['config']['updates']['release_type']

        self.current_version = config.version_info['version']

        self.github_user = config.version_info['git']['username']
        self.repo = config.version_info['git']['repo']

    def execute(self):
        new_version = self.check_latest_live_version()

        self.log(logging.INFO, f'Newest version: {new_version}')

        if new_version > self.current_version:
            self.update_signals.update_available.emit(new_version)

    def check_latest_live_version(self):
        if self.release_type == 'latest':
            ref = 'gui-rewrite'
        elif self.release_type == 'experimental':
            ref = 'prerelease'
        else:
            self.log(logging.WARNING, 'Update failed: invalid version type!')
            return

        url = f'https://api.github.com/repos/{self.github_user}/{self.repo}/contents/' \
              f'data/version_info.json?ref={ref}'
        resp = requests.request('GET', url, headers=github_headers)

        try:
            resp.raise_for_status()
        except requests.RequestException:
            logging.critical('Failed to check for version!')

        data = resp.json()
        content = base64.b64decode(data['content']).decode()

        version = json.loads(content).get('version')

        return version


class UpdateDownloadThread(Thread):
    friendly_progress = 'Downloading update...'
    permanent = False
    name = 'UpdateDownloadThread'

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        self.update_signals = UpdateSignals()

        self.release_type = config.preferences['config']['updates']['release_type']
        self.github_user = config.version_info['git']['username']
        self.repo = config.version_info['git']['repo']

    def execute(self):
        if self.release_type == 'latest':
            self.download_latest_release()
        elif self.release_type == 'experimental' and not checks.is_bundled():
            self.download_latest_experimental()
        else:
            self.log(logging.WARNING, 'Update failed: invalid version type!')
            return

    def download_latest_experimental(self):
        url = f'https://api.github.com/repos/{self.github_user}/{self.repo}/zipball/wiimmfi-rpc'
        resp = requests.get(url, headers=github_headers)

        try:
            resp.raise_for_status()
        except requests.RequestException:
            logging.critical('Update download failed!')

        buf = io.BytesIO(resp.content)

        self.update_signals.download_finished.emit(buf)

    def download_latest_release(self):
        url = f'https://api.github.com/repos/{self.github_user}/{self.repo}/releases/latest'
        resp = requests.get(url)

        try:
            resp.raise_for_status()
        except requests.RequestException:
            logging.critical('Update download failed!')

        data = resp.json()
        asset = data['assets'][0]  # TODO: automatic platform detection for correct asset

        resp = requests.get(asset['url'], stream=True)
        try:
            resp.raise_for_status()
        except requests.RequestException:
            logging.critical('Update download failed!')

        buf = io.BytesIO()
        size = asset['size']
        dl = 0
        for chunk in resp.iter_content(chunk_size=1024):
            self.emit_progress(dl // size * 100)
            buf.write(chunk)

        self.update_signals.download_finished.emit(buf)
