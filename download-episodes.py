#!/usr/bin/env python3
import argparse
import json
import os
import sys
from argparse import RawTextHelpFormatter
from configparser import ConfigParser
from datetime import datetime
from glob import glob
from urllib import request

INSTRUCTIONS = '''
This can be used to download latest episodes from stations belonging to 
global radio network. 
'''

DOWNLOAD_PATH = '~/Downloads'
MAX_PROGRESS_BAR_BLOCKS = 10


class Episode:
    def __init__(self, episode):
        self.id = episode['id']
        self.start_date = episode['startDate']
        self.date = datetime.strptime(episode['startDate'][0:10], '%Y-%m-%d')
        self.stream_url = episode['streamUrl']
        self.title = episode['title']
        self.title_with_date = episode['titleWithDate']

    def __str__(self):
        return f'Episode{{id:"{self.id}", date:"{self.date}", start_date:"{self.start_date}", ' \
               f'title:"{self.title}", title_with_date:"{self.title_with_date}"}}'


class Download:
    def __init__(self, download_file):
        self.file_name = download_file
        self.date = datetime.strptime(download_file[0:8], '%Y%m%d')

    def __str__(self):
        return f'Download{{file:"{self.file_name}", date:"{self.date}"}}'


def _get_channel_catchup_response():
    verbose('Calling channel catchup endpoint...')
    response = request.urlopen(show_config['station_catchup_url']).read().decode('utf-8')
    return json.loads(response)


def _read_catchup_response_from_file():
    verbose('Reading a fake response from file...')
    with open('fake-response.json') as f:
        file_data = f.read()
        return json.loads(file_data)


def _get_show_response():
    if args.with_fake_response:
        channel_response = _read_catchup_response_from_file()
    else:
        channel_response = _get_channel_catchup_response()

    for show in channel_response:
        if show['showId'] == show_config['show_id']:
            return show


def _get_file_format():
    if show_config['file_format']:
        return show_config['file_format']
    else:
        return 'm4a'


def _get_episode_downloads_folder():
    if show_config['download_folder']:
        download_folder = show_config['download_folder']
    else:
        download_folder = DOWNLOAD_PATH

    download_folder = download_folder.strip()

    os.makedirs(name=os.path.expanduser(download_folder), exist_ok=True)

    if download_folder.endswith("/"):
        return download_folder
    else:
        return download_folder + "/"


def get_downloaded_episodes():
    verbose('Getting list of all downloaded episodes...')
    download_folder = os.path.expanduser(_get_episode_downloads_folder())
    os.chdir(download_folder)

    files = glob('*.' + _get_file_format())

    verbose(f'Found {len(files)} downloads in the folder...')
    downloads = []
    for file in files:
        downloaded_file = Download(file)
        downloads.append(downloaded_file)

    return downloads


def _parse_episodes(show):
    parsed_episodes = []
    for episode in show['episodes']:
        parsed = Episode(episode)
        parsed_episodes.append(parsed)

    return parsed_episodes


def get_latest_episodes():
    show = _get_show_response()
    verbose(f'Show json response: {json.dumps(show, indent=2)}')
    episodes = _parse_episodes(show)
    verbose(f'Found {len(episodes)} episodes in show response...')
    for e in episodes:
        verbose(e)
    return episodes


def download(episode):
    if args.with_fake_response:
        progress_complete(episode.title_with_date, 100)
        return

    url_request = request.Request(episode.stream_url)
    url_connect = request.urlopen(url_request)

    file_size = int(url_connect.info()['Content-Length'])
    download_block_size = 8192
    downloaded_size = 0

    out_file_name = datetime.strftime(episode.date, "%Y%m%d") + '.' + _get_file_format()
    download_folder = os.path.expanduser(_get_episode_downloads_folder())
    tmp_folder = download_folder + 'tmp'

    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)
    os.chdir(tmp_folder)

    with open(out_file_name, 'wb') as out_file:
        while True:
            buffer = url_connect.read(download_block_size)
            downloaded_size += len(buffer)
            if not buffer:
                break
            out_file.write(buffer)
            progress(episode.title_with_date, file_size, downloaded_size)

    os.rename(out_file_name, os.path.join(download_folder, out_file_name))

    progress_complete(episode.title_with_date, file_size)


def progress(file_name, total_len, current_size):
    progress_blocks = int(total_len / MAX_PROGRESS_BAR_BLOCKS)
    current_position = int(current_size / progress_blocks)
    sys.stdout.write('\r%s: [%s%s] %s/%s %s'
                     % (file_name,
                        '=' * current_position,
                        ' ' * (MAX_PROGRESS_BAR_BLOCKS - current_position),
                        current_size,
                        total_len,
                        ''
                        ))
    sys.stdout.flush()


def progress_complete(file_name, total_len):
    print('\r%s: [%s] %s/%s => ✅ Done' % (file_name, '=' * MAX_PROGRESS_BAR_BLOCKS, total_len, total_len))


def get_episodes_to_download():
    episodes = get_latest_episodes()
    downloaded = get_downloaded_episodes()
    downloaded_dates = {file.date for file in downloaded}

    episodes_to_download = []
    for episode in episodes:
        if episode.date not in downloaded_dates:
            episodes_to_download.append(episode)

    return episodes_to_download


def download_latest():
    verbose('Checking for latest episodes..')

    pending_downloads = get_episodes_to_download()
    if not pending_downloads:
        print(f'Nothing to download, all up to date 🙌')
        return

    print(f'Found {len(pending_downloads)} new episodes to download.')

    for i in range(0, len(pending_downloads)):
        print(f'Downloading {i + 1} of {len(pending_downloads)}:')
        download(pending_downloads[i])

    print(f'Downloads complete 🏁')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                     description=INSTRUCTIONS)
    parser.add_argument('--with-fake-response', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args(sys.argv[1:])
    if args.verbose:
        verbose = print
    else:
        def verbose(*arg, **kw):
            pass

    verbose(f'Called download latest episodes with args: {args}')

    config_file = os.path.expanduser('~/.global_radio_downloader.cfg')
    if not os.path.exists(config_file):
        parser.print_help()
        sys.exit(1)

    config = ConfigParser(default_section='radio-station')
    config.read(config_file)
    show_config = config['radio-station']

    download_latest()
