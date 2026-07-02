#!/bin/bash

# Uso: ./restore_node.sh <nome_da_instancia> <id_do_no>
# Exemplo: ./restore_node.sh ws-4 4

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <instancia> <id_do_no>"
    exit 1
fi

MAQUINA=$1
ID_NO=$2
PROJECT_DIR="/home/wlorion/dss/lab_02"


DASH_IP=$(gcloud compute instances describe dash-node --format='value(networkInterfaces[0].networkIP)')

echo "=== RESTAURANDO bully.py EM $MAQUINA (NÓ $ID_NO) ==="

# O comando entra na pasta e sobe o bully.py de novo
gcloud compute ssh $MAQUINA --command "cd $PROJECT_DIR && 
    pkill -f bully.py; 
    nohup python3 bully.py $ID_NO $DASH_IP > /dev/null 2>&1 &" --quiet

echo "Processo bully.py restaurado com sucesso em $MAQUINA."