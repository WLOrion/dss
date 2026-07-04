#!/bin/bash

# Uso: ./kill_node.sh <nome_da_instancia>
# Exemplo: ./kill_node.sh ws-4

if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <instancia>"
    exit 1
fi

MAQUINA=$1

echo "=== DERRUBANDO APENAS O bully.py NA MÁQUINA $MAQUINA ==="

gcloud compute ssh $MAQUINA --command "pkill -f bully.py" --quiet

echo "Processo bully.py encerrado em $MAQUINA. Os outros continuam rodando."