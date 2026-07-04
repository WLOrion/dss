#!/bin/bash

gcloud config set compute/zone us-central1-a

echo "=== CRIANDO INFRAESTRUTURA PARA SISTEMAS DISTRIBUÍDOS ==="

# 1 - Criação das Instâncias
echo "Criando instâncias (ws-1, ws-2, ws-3, ws-4 e dash-node)..."
gcloud compute instances create ws-1 ws-2 ws-3 ws-4 dash-node \
    --machine-type=e2-medium \
    --tags=p2p-node \
    --metadata=startup-script='#! /bin/bash
    apt-get update
    apt-get install -y python3 python3-pip git
    '

# 2 - Firewall para comunicação P2P e Dash
echo "Configurando Firewall..."
gcloud compute firewall-rules create allow-p2p-traffic \
    --allow tcp:8000-9368 \
    --target-tags=p2p-node

# 3 - Acesso ao Dashboard
echo "IP Interno do Dashboard (para passar como argumento): $(gcloud compute instances describe dash-node --format='value(networkInterfaces[0].networkIP)')"
echo -e "\n=== INFRAESTRUTURA PRONTA ===\n"