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
This program will detect if a specific <process_name> is running or is closed through inotify hooks and changes the systray icon (from a Red Downwards arrow to a Green Upwards arrow and vice versa).
It has the following menu functions:
* Kill All '<process_name>' -> Kills *ALL* process instances of the given name
* Exit -> Stops the AppIndicator systray itself

Prerequisites:
* Python3 3.9+
* pip install psutil
* pip install pystray
* pip install pyinotify

References:
https://github.com/giampaolo/psutil
https://github.com/moses-palmer/pystray
https://github.com/moses-palmer/pystray/issues/17#issuecomment-872651630
https://github.com/seb-m/pyinotify

Image Sources:
https://upload.wikimedia.org/wikipedia/commons/b/b7/Eo_circle_red_arrow-down.svg
https://upload.wikimedia.org/wikipedia/commons/c/c0/Eo_circle_green_arrow-up.svg

Tested on:
* Linux
** OS: Debian 13 (trixie/testing) x86_64
** Kernel: 6.7.12-amd64
** WM: XFCE 4.18
** Python3: 3.11.9
* Windows
** Not Supported, because of lack of file monitoring capability

Example:
appindicator2.py -i 0
This will start an AppIdicator for the <process_name> of the first list item in the appindicator.json file under the 'Processes' element.
"""


# Import modules
from __future__ import annotations
from pathlib import Path
import sys
import getopt
import threading
import time
import logging
import json
import re
from shutil import which
import psutil
import pystray
import pyinotify
import PIL.Image


# Define classes
class EventHandler(pyinotify.ProcessEvent):
    """_summary_

    Args:
        pyinotify (_type_): _description_
    """
    def process_IN_ACCESS(self, event):
        """_summary_

        Args:
            event (_type_): _description_
        """
        if not re.search(str(QUITFILE), str(event.pathname)):
            logging.info(f"Executable was started: {event.pathname}")
        global FOUND
        FOUND = 1
    def process_IN_CLOSE_NOWRITE(self, event):
        """_summary_

        Args:
            event (_type_): _description_
        """
        if not re.search(str(QUITFILE), str(event.pathname)):
            logging.info(f"File was closed without writing: {event.pathname}")
        global FOUND
        FOUND = 1


# Define functions
def handle_read_callback(notifier):
    """_summary_

    Args:
        notifier (_type_): _description_

    Returns:
        bool: When True, the original process is stopped
    """
    try:
        global FOUND
        if FOUND == 1:
            logging.info(f"Handling inotify callback")
            return True
        return False
    except Exception as error:
        logging.error(f"Failed to handle a watch callback")
        print(error)


def watch(filename):
    """_summary_

    Args:
        filename (_type_): _description_
    """
    try:
        global QUITFILE
        wm = pyinotify.WatchManager()
        eh = EventHandler()
        notifier = pyinotify.Notifier(watch_manager=wm, default_proc_fun=eh)

        mask = pyinotify.IN_ACCESS | pyinotify.IN_CLOSE_NOWRITE
        wm.add_watch(filename, mask)
        wm.add_watch(QUITFILE, mask) # this file will be opened and closed on manual quitting the trayicon, triggering a graceful shutdown

        logging.info(f"Started Watching: {filename}")
        notifier.loop(callback=handle_read_callback) # this is a blocking process
    except Exception as error:
        logging.error(f"Failed to add a watch")
        print(error)
    finally:
        if exit_event.is_set():
            exit_inotify(notifier)


def find_procs(process):
    """_summary_

    Args:
        process (_type_): _description_

    Returns:
        array: all the found process names
    """
    try:
        found_procs = False
        procs = []
        for proc in psutil.process_iter():
            # check whether the process name matches (non-Windows)
            if proc.name() == process:
                found_procs = True
                procs.append(proc)
        if found_procs is True:
            return procs
        else:
            return None
    except Exception as error:
        logging.error(f"Failed to find processes")
        print(error)


def set_image(icon, image):
    """_summary_

    Args:
        icon (_type_): _description_
        image (_type_): _description_
    """
    try:
        img = PIL.Image.open(image)
        icon.icon = img
        icon.visible = True
    except Exception as error:
        logging.error(f"Failed to set image to App icon")
        print(error)


def toggle_app_icon(icon, process, status):
    """_summary_

    Args:
        icon (_type_): _description_
        process (_type_): _description_
        status (_type_): _description_

    Returns:
        status (_type_): can be either 'up' or 'down'
    """
    try:
        if not exit_event.is_set():
            my_processes = find_procs(process)
            if my_processes is None:
                if status != 'down':
                    set_image(icon, "circle_red_arrow-down.png")
                    logging.info(f"Process NOT found: {process}")
                status = 'down'
            else:
                if status != 'up':
                    procs=[]
                    set_image(icon, "circle_green_arrow-up.png")
                for my_process in my_processes:
                    if my_process.pid not in procs:
                        procs.append(my_process.pid)
                        logging.info(f"Process found: {process} with PID %s",str(my_process.pid))
                        if icon.HAS_NOTIFICATION:
                            msg = f"{process} with PID: %s detected!",str(my_process.pid)
                            icon.notify(msg)
                status = 'up'
        return status
    except Exception as error:
        logging.error(f"Failed to toggle App icon")
        print(error)


def kill_all(icon, item):
    """_summary_

    Args:
        icon (_type_): _description_
        item (_type_): _description_
    """
    try:
        PROCNAME = re.match('.*\'(.*)\'', str(item))[1]
        my_processes = find_procs(PROCNAME)
        if my_processes is None:
            logging.info(f"Process '{PROCNAME}' not found. Continuing watching...")
        else:
            procs = []
            while my_processes is not None:
                for my_process in my_processes:
                    logging.info(f'Killing process: {PROCNAME} with PID: {my_process.pid}')
                    procs.append(my_process.pid)
                    my_process.kill()
                    logging.info(f"Done!")
                    time.sleep(1)
                my_processes = find_procs(PROCNAME)
            if icon.HAS_NOTIFICATION:
                msg = "Killed process: "+PROCNAME+" with PID(s): "+str(procs)
                icon.notify(msg)
    except Exception as error:
        logging.error(f"Failed to kill processes")
        print(error)


def setup(icon):
    """_summary_

    Args:
        icon (_type_): _description_
    """
    STATUS = 'none'
    PROCNAME = re.match('appindicator-(.*)', str(icon.title))[1]
    try:
        logging.info(f"Detecting process: {PROCNAME} | {STATUS}")
        set_image(icon, "circle_red_arrow-down.png")
        while not exit_event.is_set():  # This exits the loop if exit is ever set -> program was quit
            # Set initial inotify count
            global FOUND
            FOUND = 0
            # Set the inotify watch
            watch(which(PROCNAME))
            # Toggle the Trayicon image
            STATUS = toggle_app_icon(icon, PROCNAME, STATUS)
            # Wait for exit event
            exit_event.wait(1)  # allows exiting while waiting. time.sleep would block
    except (KeyboardInterrupt, SystemExit):
        logging.info(f"EXITING Gracefully")
    except Exception as error:
        logging.error(f"RESTARTING Forcibly")
        print(error)
    finally:
        exit_main(icon)


def exit_main(icon):
    """_summary_

    Args:
        icon (_type_): _description_
    """
    try:
        logging.info(f"Stopping main icon thread...")

        #Trigger the graceful shutdown of the pyinotify thread
        f = open(f"{QUITFILE}", "r")
        f.close()

        icon.visible = False
        exit_event.set()

        icon.stop()
    except Exception as error:
        logging.error(f"Failed to exit the application")
        print(error)


def exit_inotify(notifier):
    """_summary_

    Args:
        notifier (_type_): _description_
    """
    try:
        logging.info(f"Stopping notifier thread...")
        notifier.stop()
    except Exception as error:
        logging.error(f"Failed to exit the inotify thread")
        print(error)


def start_main(process_name):
    """_summary_

    Args:
        process_name (str): _description_
    """
    # Cleanup
    exit_event.clear()
    # Get name variables
    appindicator_id = "appindicator-" + process_name
    # Opening tray icon image
    image = PIL.Image.open("circle_red_arrow-down.png")
    # Compose tray icon and menu in a thread
    icon = pystray.Icon(
        appindicator_id, image, menu=pystray.Menu(
            pystray.MenuItem("Kill All '"+process_name+"' processes", kill_all),
            pystray.MenuItem("Exit", exit_main)),
        title=appindicator_id)
    # Start the thread
    icon.run(setup=setup)


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
                logging.error(e)
                sys.exit(2)
    logging.info(f"Input item number is: {input_item_number}")

    # Load JSON settings
    process: str | None = None
    with open('appindicator.json', 'r',encoding='utf8') as json_data_file:
        json_object = json.load(json_data_file)

        # Fetching the right index from the list of processes in the JSON file
        try:
            process = json_object['Processes'][int(input_item_number)]
        except Exception as e:
            logging.error("{e}\nThe JSON file only has %s items, starting with index 0",len(json_object['Processes']))
            sys.exit(2)

    # Get name variables
    process_name = process['Name']

    # Start the program
    start_main(process_name)


# Setup logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


# This event is used to stop the main loop.
exit_event = threading.Event()


# Amount of inotify loops
FOUND = 0


# File to use when quiting the app, this will close the pyinotify thread gracefully at the expense of creating a single empty file.
MYHOME = str(Path.home())
QUITFILE = f"{MYHOME}/.appindicator.quit"


# Start main thread
if __name__ == "__main__":
    main(sys.argv[1:])
