#!/bin/bash
export HOME=/home/$(id -nu $(id -u))
. $HOME/.bash_profile

export DISPLAY=:0
export XAUTHORITY=$HOME/.Xauthority
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export PATH=/home/$(id -nu $(id -u))/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/usr/local/sbin:/usr/sbin:/sbin
if [ -r "$HOME/.dbus/Xdbus" ]; then
  . "$HOME/.dbus/Xdbus"
fi

if [ -n "$1" ]
then
    echo "run from cronjob"
    APPEND="true"
else
    echo "first run"
    APPEND="false"
fi

cd ~/Repos/MyGithub/PublicPythonProjects/appindicator
pgrep -f 'appindicator.py -i 0' &>/dev/null || (([ "$APPEND" = "true" ] || > ~/appindicator0.log) && nohup python3 -u appindicator.py -i 0 >> ~/appindicator0.log 2>&1) &
pgrep -f 'appindicator.py -i 1' &>/dev/null || (([ "$APPEND" = "true" ] || > ~/appindicator1.log) && nohup python3 -u appindicator.py -i 1 >> ~/appindicator1.log 2>&1) &
pgrep -f 'appindicator.py -i 2' &>/dev/null || (([ "$APPEND" = "true" ] || > ~/appindicator2.log) && nohup python3 -u appindicator.py -i 2 >> ~/appindicator2.log 2>&1) &

# TIP: use 'crontab -e' to automatically restart on crash (checking every 5 minutes)
## */5 * * * * [this script folder path]/appindicator.sh cron >> /home/[user]/cronjobs.log 2>&1
