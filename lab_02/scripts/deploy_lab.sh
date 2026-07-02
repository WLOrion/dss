#!/bin/bash

PROJECT_DIR="~"

echo "=== MAPEANDO REDE E GERANDO NODES.CSV ==="

# 1 - Captura os IPs internos das 4 máquinas
IP1=$(gcloud compute instances describe ws-1 --format='value(networkInterfaces[0].networkIP)')
IP2=$(gcloud compute instances describe ws-2 --format='value(networkInterfaces[0].networkIP)')
IP3=$(gcloud compute instances describe ws-3 --format='value(networkInterfaces[0].networkIP)')
IP4=$(gcloud compute instances describe ws-4 --format='value(networkInterfaces[0].networkIP)')
DASH_IP=$(gcloud compute instances describe dash-node --format='value(networkInterfaces[0].networkIP)')

# 2 - Cria o arquivo nodes.csv localmente
cat <<EOF > nodes.csv
1,$IP1,8001,2
2,$IP2,8001,3
3,$IP3,8001,5
4,$IP4,8001,7
EOF

echo "Arquivo nodes.csv gerado:"
cat nodes.csv

# 3 - Copia o arquivo e inicia os processos em cada nó
for i in {1..4}; do
    echo "-> Configurando ws-$i..."

    gcloud compute scp nodes.csv ws-$i:$PROJECT_DIR/ --quiet

    gcloud compute ssh ws-$i --command "pkill -f python3; 
        cd $PROJECT_DIR && 
        nohup python3 bully.py $i $DASH_IP > /dev/null 2>&1 &
        nohup python3 mutex.py $i $DASH_IP > /dev/null 2>&1 &
        nohup python3 lamport.py $i $DASH_IP > /dev/null 2>&1 &" --quiet
done

# 4 - Inicia o Dashboard
echo "-> Subindo Dashboard..."
gcloud compute ssh dash-node --command "pkill -f dash.py; nohup python3 /home/wlorion/dss/lab_02/dash.py > /dev/null 2>&1 &" --quiet

echo -e "\n=== TUDO PRONTO! ==="