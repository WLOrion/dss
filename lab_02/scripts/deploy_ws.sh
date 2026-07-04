#!/bin/bash

set -e

id=$1
rep="https://github.com/WLOrion/dss.git"
dir="/home/wlorion/dss/lab_02"

[ -z "$id" ] && {
    echo "Uso: $0 <id>"
    exit 1
}

ip1=$(gcloud compute instances describe ws-1 --format='value(networkInterfaces[0].networkIP)')
ip2=$(gcloud compute instances describe ws-2 --format='value(networkInterfaces[0].networkIP)')
ip3=$(gcloud compute instances describe ws-3 --format='value(networkInterfaces[0].networkIP)')
ip4=$(gcloud compute instances describe ws-4 --format='value(networkInterfaces[0].networkIP)')
dip=$(gcloud compute instances describe dash-node --format='value(networkInterfaces[0].networkIP)')

cat > nodes.csv <<EOF
1,$ip1,2
2,$ip2,3
3,$ip3,5
4,$ip4,7
EOF

gcloud compute ssh ws-$id --command "
sudo apt-get update -y >/dev/null 2>&1
sudo apt-get install -y git python3 >/dev/null 2>&1

cd ~

if [ -d dss/.git ]; then
    cd dss
    git pull
else
    rm -rf dss
    git clone $rep
fi
"

gcloud compute scp nodes.csv ws-$id:$dir/

gcloud compute ssh ws-$id --command "
set -x

cd $dir

ps -ef | grep '[b]ully.py' | awk '{print \$2}' | xargs -r kill || true
ps -ef | grep '[m]utex.py' | awk '{print \$2}' | xargs -r kill || true
ps -ef | grep '[l]amport.py' | awk '{print \$2}' | xargs -r kill || true

sleep 1

nohup python3 bully.py $id $dip 8001 >/tmp/bully.log 2>&1 &
nohup python3 mutex.py $id $dip 8002 >/tmp/mutex.log 2>&1 &
nohup python3 lamport.py $id $dip 8003 >/tmp/lamport.log 2>&1 &

sleep 2

cat /tmp/bully.log || true
cat /tmp/mutex.log || true
cat /tmp/lamport.log || true
"

echo "Instância ws-$id configurada."