#!/usr/bin/env python3

"""
License:
This file is part of the 'PublicPythonProjects' distribution (https://github.com/sjoerdv or http://sjoerdv.github.io).
Copyright (C) 2022  Sjoerd de Valk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Description:
This program will make make an archive (i.e. backup) of your mastodon account(s) content,
generating a html report (html) and show statistics (report).
Further external enhancements (not included here!) include compressing and encrypting the data
to a single archive and save the contents to a git repo or (cloud) storage.

Prerequisites:
* Python3 3.9+
* pip install mastodon-archive

References:
* https://github.com/kensanata/mastodon-archive

Image Sources:
None

Tested on:
* Linux
** OS: LMDE 5 (elsie) x86_64
** Kernel: 6.0.0-0.deb11.2-amd64
** WM: Cinnamon 5.4.12
** Python3: 3.9.2
* Windows
** OS: Windows 10 21H2
** Python3: 3.9.5

Example:
mastodon_archiver.py
This will start the 'Dry-Run' process of archiving the mastodon accounts specified in the 'mastodon.json' file.
mastodon_archiver.py --confirm
This will start the 'Real Destructive' process of archiving the mastodon accounts specified in the 'mastodon.json' file.
"""


# Import modules
from __future__ import annotations
import sys
import os
import getopt
import json


# Define functions
def main(argv):
    """_summary_

    Args:
        argv (_type_): _description_
    """
    # Init Variables
    help_message: str = 'mastodon_archiver.py OR mastodon_archiver.py --confirm'
    confirm_cmd: str = ''

    # Processing CLI input
    try:
        opts, args = getopt.getopt(argv,"hc",["help","confirm"])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    if not opts:
        print("NOTE: Expiring will only do dry-run operations. No data will be changed.")
    for opt, arg in opts:
        if opt == '-h':
            print(help_message)
            sys.exit()
        elif opt in ("-c", "--confirm"):
            print("WARNING: Expiring will execute FOR REAL! Make sure the dry-run produces no errors or terminate now. Data will be cleaned up for your mastodon account.")
            confirm_cmd = ' --confirmed'

    # Load JSON settings
    ## Try to find the right path
    settings_file_name = "../mastodon.json"
    if os.path.exists(settings_file_name) is False:
        settings_file_name = "./mastodon.json"
    try:
        # Load JSON settings
        input("Press Enter to continue...")
        with open(settings_file_name, 'r',encoding='utf8') as json_data_file:
            json_object = json.load(json_data_file)
    except Exception as error:
        print(error)
        sys.exit()

    try:
        cmd = "mastodon-archive -h"
        os.system(cmd)
    except Exception as error:
        print(error)
        print("\r\n\r\nInstall mastodon-archive first. Run: pip install mastodon-archive")
        sys.exit()

    # Archive Mastodon
    print("\r\nDownload Archive Statuses, Favourites, Mentions")
    for acc in json_object['accounts']:
        print(acc)
        user=acc['user']
        cmd = f'mastodon-archive archive --with-followers --with-following --with-mentions --pace {user}'
        os.system(cmd)

    print("\r\nDownload Media")
    for acc in json_object['accounts']:
        print(acc)
        user=acc['user']
        cmd = f'mastodon-archive media --pace {user}'
        os.system(cmd)
        cmd = f'mastodon-archive media --collection favourites --pace {user}'
        os.system(cmd)
        cmd = f'mastodon-archive media --collection bookmarks --pace {user}'
        os.system(cmd)

    # BEGIN WARNING: After the following code has been run in 'confirm' mode, data can not be recovered!

    print('\r\nExpire Statuses')
    for acc in json_object['accounts']:
        print(acc)
        print("\r\nBe patient, this can take a LONG time! REF: https://docs.joinmastodon.org/api/rate-limits/#deleting-statuses")
        user=acc['user']
        cmd = f'mastodon-archive expire --older-than 8 --collection statuses --pace {confirm_cmd} {user}' # needs '--confirmed' to work
        os.system(cmd)

    print("\r\nExpire Favourites")
    for acc in json_object['accounts']:
        print(acc)
        user=acc['user']
        cmd = f'mastodon-archive expire --older-than 8 --collection favourites --pace{confirm_cmd} {user}' # needs '--confirmed' to work
        os.system(cmd)

    print("\r\nDismiss Notifications")
    for acc in json_object['accounts']:
        print(acc)
        user=acc['user']
        cmd = f'mastodon-archive expire --older-than 8 --collection mentions --delete-other-notifications --pace{confirm_cmd} {user}' # needs '--confirmed' to work
        os.system(cmd)

    # END WARNING

    print("\r\nGenerate HTML")
    for acc in json_object['accounts']:
        print(acc)
        user=acc['user']
        cmd = f'mastodon-archive html {user}'
        os.system(cmd)

    print("\r\nShow Statistics")
    for acc in json_object['accounts']:
        print(acc)
        user=acc['user']
        cmd = f'mastodon-archive report --newer-than 8 {user}'
        os.system(cmd)


# Start main thread
if __name__ == "__main__":
    main(sys.argv[1:])
