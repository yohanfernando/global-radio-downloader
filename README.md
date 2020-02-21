Global Radio Downloader
===

A simple python script to download episodes from your favorite global radio station (www.global.com/radio).

This will download all the latest episodes from the configured radio station for offline listening and you no longer
need to worry about old episodes expiring any more!


### Requirements
You need python 3 correctly installed for the script to run.


## Install & Setup
Simply download the `download-episodes.py` script to your executable folder or where ever you keep your 
python scripts.


### Setup
You need to configure the download script to give details of the station/show that you listen/follow. Once you 
add necessary configurations, save the config file to your home directly with name `.global_radio_downloader.cfg`. 

You can use `sample-config-file.cfg` as a template.

#### Config Options
1. `station_catchup_url`: The URL where catch up shows/episodes are listed
2. `show_id`: The radio show ID you listen/follow
3. `file_format`: The episode file format, usually they are in `.m4a` format
4. `download_folder`: The destination folder , if not provided will use `~/Downloads`


## How to run
Please follow "Install & Setup" step to correctly setup the download script.

You can simply call it as any other python script by calling `./path-to-script/download-episodes.py`

This will download all missing episodes to the specified `download_folder`, episodes will be named using the day
it was aired (e.g. episode on 14th of February 2020 will appear as `20200214.m4a`).

**Note**: remember to delete old episodes to stop running out of disk space.


### Options
`--verbose`: print debug statements


## Future plans
- Add a `--dry-run` mode to test setup
- Add a configuration helper with options to:
    - find the station
    - find the show 
    - auto generate the config file
- Download episodes from multiple stations
- Trim episodes before a given day
- Play episodes from here
    - Pause/stop & resume from last played position
    - Trim episodes as finished playing
- Add bash auto completion



