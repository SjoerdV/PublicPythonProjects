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
This is an AppIndicator program, which manifests itself in the system tray of a Desktop Environment.
This program will detect if a specific <process_name> is running at set intervals and changes the systray icon (from a Red Downwards arrow to a Green Upwards arrow and vice versa).
It has the following menu functions:
* Kill All '<process_name>' -> Kills *ALL* process instances of the given name
* Exit -> Stops the AppIndicator systray itself

Prerequisites:
* Python3 3.9+
* pip install psutil
* pip install pystray

References:
https://github.com/moses-palmer/pystray
https://github.com/moses-palmer/pystray/issues/17#issuecomment-872651630

Image Sources:
https://upload.wikimedia.org/wikipedia/commons/b/b7/Eo_circle_red_arrow-down.svg
https://upload.wikimedia.org/wikipedia/commons/c/c0/Eo_circle_green_arrow-up.svg

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
appindicator.py -i 0
This will start an AppIdicator for the <process_name> of the first list item in the appindicator.json file under the 'Processes' element.
"""


# Import modules
from __future__ import annotations
import sys
import getopt
import threading
import time
import json
import re
import psutil
import pystray
import PIL.Image


# Define functions
def find_procs(process):
    """_summary_

    Args:
        process (_type_): _description_

    Returns:
        _type_: _description_
    """
    found = False
    procs = []
    for proc in psutil.process_iter():
        # check whether the process name matches (non-Windows)
        if proc.name() == process:
            found = True
            procs.append(proc)
        # check whether the process name matches (Windows)
        elif proc.name() == process+'.exe':
            found = True
            procs.append(proc)
    if found is True:
        return procs
    else:
        return None


def set_image(icon,im):
    """_summary_

    Args:
        icon (_type_): _description_
        im (str): _description_
    """
    img = PIL.Image.open(im)
    icon.icon = img
    icon.visible = True


def setup(icon):
    """_summary_

    Args:
        icon (_type_): _description_
    """
    status = 'none'
    try:
        while not exit_event.is_set():  # This exits the loop if exit is ever set -> program was quit
            PROCNAME = re.match('appindicator-(.*)', str(icon.title))[1]
            print("Detecting process:", PROCNAME, "|", status)
            my_processes = find_procs(PROCNAME)
            if my_processes is None:
                if status != 'down':
                    set_image(icon, "circle_red_arrow-down.png")
                    print("Process NOT found:", PROCNAME)
                status = 'down'
            else:
                if status != 'up':
                    procs=[]
                    set_image(icon, "circle_green_arrow-up.png")
                for my_process in my_processes:
                    if my_process.pid not in procs:
                        procs.append(my_process.pid)
                        print("Process found:", PROCNAME, "with PID", str(my_process.pid))
                        if icon.HAS_NOTIFICATION:
                            msg = PROCNAME+" with PID: "+str(my_process.pid)+" detected!"
                            icon.notify(msg)
                status = 'up'
            exit_event.wait(1)  # allows exiting while waiting. time.sleep would block
    except (KeyboardInterrupt, SystemExit):
        exit_main(icon)


def exit_main(icon):
    """_summary_

    Args:
        icon (_type_): _description_
    """
    icon.visible = False
    exit_event.set()
    icon.stop()


def kill_all(icon, item):
    """_summary_

    Args:
        icon (_type_): _description_
        item (_type_): _description_
    """

    PROCNAME = re.match('.*\'(.*)\'', str(item))[1]
    my_processes = find_procs(PROCNAME)
    if my_processes is None:
        print("Process '", PROCNAME, "' not found. Continuing watching...")
    else:
        procs = []
        while my_processes is not None:
            for my_process in my_processes:
                print("Killing process:", PROCNAME, "with PID:", my_process.pid)
                procs.append(my_process.pid)
                my_process.kill()
                print("Done!")
                time.sleep(1)
            my_processes = find_procs(PROCNAME)
        if icon.HAS_NOTIFICATION:
            msg = "Killed process: "+PROCNAME+" with PID(s): "+str(procs)
            icon.notify(msg)


def main(argv):
    """_summary_

    Args:
        argv (_type_): _description_
    """
    # Processing CLI input
    input_item_number: int | None = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["help","in="])
    except getopt.GetoptError:
        print ('appindicator.py -i <input_item_number>')
        sys.exit(2)
    if not opts:
        print ('appindicator.py -i <input_item_number>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('appindicator.py -i <input_item_number>')
            sys.exit()
        elif opt in ("-i", "--in"):
            try:
                input_item_number = arg
                int(arg)
            except Exception as e:
                print(e)
                sys.exit(2)
    print ('Input item number is:', input_item_number)

    # Load JSON settings
    with open('appindicator.json', 'r',encoding='utf8') as json_data_file:
        json_object = json.load(json_data_file)

    # Fetching the right index from the list of processes in the JSON file
    try:
        process = json_object['Processes'][int(input_item_number)]
    except Exception as e:
        print(e,"\nThe JSON file only has",len(json_object['Processes']),"items, starting with index 0")
        sys.exit(2)

    # Get name variables
    process_name = process['Name']
    appindicator_id = "appindicator-" + process_name
    # Opening tray icon image
    image = PIL.Image.open("circle_red_arrow-down.png")
    # Compose tray icon and menu in a thread
    icon = pystray.Icon(appindicator_id, image, menu=pystray.Menu(
                pystray.MenuItem("Kill All '"+process_name+"' processes", kill_all),
                pystray.MenuItem("Exit", exit_main)
            ),title=appindicator_id)
    # Start the thread
    icon.run(setup=setup)


# This event is used to stop the loop.
exit_event = threading.Event()


# Start main thread
if __name__ == "__main__":
    main(sys.argv[1:])
