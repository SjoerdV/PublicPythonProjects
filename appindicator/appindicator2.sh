#!/bin/bash
export HOME=/home/$(id -nu $(id -u))
. $HOME/.bash_profile

export DISPLAY=:0
export XAUTHORITY=$HOME/.Xauthority
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export PATH=/home/$(id -nu $(id -u))/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/usr/local/sbin:/usr/sbin:/sbin

logDate=`date +"%Y-%m-%d_%H%M%S"`

if [ -r "$HOME/.dbus/Xdbus" ]; then
  . "$HOME/.dbus/Xdbus"
fi

if [ -n "$1" ]
then
    echo "${logDate} run from cronjob"
    APPEND="true"
else
    echo "${logDate} first run"
    APPEND="false"
fi

cd ~
# this file will be opened and closed on manual quitting the trayicon, triggering a graceful shutdown
touch .appindicator.quit

cd ~/Repos/MyGithub/PublicPythonProjects/appindicator
# parse the json
json=$(cat appindicator.json)
progs=$(echo "$json" | jq -r '.Processes[].Name')

# run program app indicators
count=0
for prog in $progs;
do
    echo "starting App Indicator for application '$prog' with index '$count'"
    pgrep -f "appindicator2.py -i ${count}" &>/dev/null || (([ "$APPEND" = "true" ] || > ~/appindicator${count}.log) && nohup python3 -u appindicator2.py -i $count >> ~/appindicator${count}.log 2>&1) &
    count=$((count+1))
done

# TIP: use 'crontab -e' to automatically restart on crash (checking every 5 minutes)
## */5 * * * * [this script folder path]/appindicator.sh cron >> /home/[user]/cronjobs.log 2>&1
