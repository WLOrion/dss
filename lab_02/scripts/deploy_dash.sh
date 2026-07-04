#!/bin/bash

set -e

REPO="https://github.com/WLOrion/dss.git"
DIR="/home/wlorion/dss/lab_02"

gcloud compute ssh dash-node --command "
sudo apt-get update -y >/dev/null 2>&1
sudo apt-get install -y git python3 >/dev/null 2>&1

cd \$HOME

if [ -d dss/.git ]; then
    cd dss
    git pull
else
    rm -rf dss
    git clone $REPO
fi

cd $DIR

pid=\$(pgrep -f '^python3 dash.py$')
if [ -n \"\$pid\" ]; then
    kill \$pid
    sleep 1
fi

nohup python3 dash.py >/tmp/dash.log 2>&1 </dev/null &
"

echo "Dash iniciado com sucesso."