#!/bin/bash

# Função para criar pausas e separação visual
pause_and_clear() {
    echo -e "\n--------------------------------------------"
    read -p "--- Pressione Enter para o próximo passo ---"
    clear
}

clear
echo "=== INÍCIO DA DEMONSTRAÇÃO: MC714 - SISTEMAS DISTRIBUÍDOS ==="
echo "Participantes: Anita Almeida e Wellington da Silva" 
echo -e "\n------------------------------------------------"

# --- TAREFA 1 ---
echo -e "\n[TAREFA 1] Configurando a Região e Zona Padrão...\n"
echo -e "Comando:\n$ gcloud config set compute/region us-central1 && gcloud config set compute/zone us-central1-a\n"
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
echo -e "\nResultado da Configuração:"
gcloud config list
pause_and_clear

# --- TAREFA 2 ---
echo -e "\n[TAREFA 2.1] Criando Instâncias de VM (e2-medium) e instalando Apache...\n"
echo -e "Comando:\n$ gcloud compute instances create ws-1 ws-2 ws-3 --machine-type=e2-medium --tags=http-server --metadata-from-file startup-script=startup.sh\n"
gcloud compute instances create ws-1 ws-2 ws-3 \
    --machine-type=e2-medium \
    --tags=http-server \
    --metadata-from-file startup-script=startup.sh
pause_and_clear

echo -e "\n[TAREFA 2.2] Criando Regra de Firewall para Tráfego HTTP (Porta 80)...\n"
echo -e "Comando:\n$ gcloud compute firewall-rules create allow-http-mc714 --allow tcp:80 --target-tags=http-server\n"
gcloud compute firewall-rules create allow-http-mc714 \
    --allow tcp:80 \
    --target-tags=http-server
pause_and_clear

echo -e "\n[TAREFA 2.3] Verificando acesso individual às instâncias...\n"
gcloud compute instances list
pause_and_clear

# --- TAREFA 3 ---
echo -e "\n[TAREFA 3] Configurando o Serviço de Balanceamento de Carga...\n"
echo -e "1- Criando Verificação de Integridade (Health Check)...\n"
echo -e "Comando:\n$ gcloud compute http-health-checks create check-distribuidos\n"
gcloud compute http-health-checks create check-distribuidos

echo -e "\n2.1- Criando Pool de Destino...\n"
echo -e "Comando:\n$ gcloud compute target-pools create pool-mc714 --region us-central1 --http-health-check check-distribuidos\n"
gcloud compute target-pools create pool-mc714 --region us-central1 --http-health-check check-distribuidos

echo -e "\n2.2- Adicionando instâncias a Pool de Destino...\n"
echo -e "Comando:\n$ gcloud compute target-pools add-instances pool-mc714 --instances ws-1,ws-2,ws-3\n"
gcloud compute target-pools add-instances pool-mc714 --instances ws-1,ws-2,ws-3

echo -e "\n3. Criando Regra de Encaminhamento (IP do Load Balancer)...\n"
echo -e "Comando:\n$ gcloud compute forwarding-rules create lb-mc714 --region us-central1 --ports 80 --target-pool pool-mc714\n"
gcloud compute forwarding-rules create lb-mc714 --region us-central1 --ports 80 --target-pool pool-mc714
pause_and_clear

# --- DEMONSTRAÇÃO DE FUNCIONAMENTO ---
echo -e "\n=== TESTANDO O BALANCEAMENTO DE CARGA (LOAD BALANCING) ===\n"
LB_IP=$(gcloud compute forwarding-rules describe lb-mc714 --region us-central1 --format='value(IPAddress)')
echo "IP do Balanceador: $LB_IP"
echo -e "Executando 15 requisições para mostrar a distribuição...\n"
for i in {1..15}; do curl -s $LB_IP | grep "Servidor"; sleep 0.5; done
pause_and_clear

# --- DETECÇÃO DE UNHEALTHY HOST ---
echo -e "\n=== TESTANDO DETECÇÃO DE UNHEALTHY HOST ==="
echo -e "Derrubando o serviço Apache na máquina ws-1 via SSH..."
gcloud compute ssh ws-1 --command "sudo systemctl stop apache2" --quiet
echo -e "\nVerificando o tráfego agora (ws-1 deve parar de responder):\n"
for i in {1..15}; do curl -s $LB_IP | grep "Servidor"; sleep 0.5; done
echo -e "\nObserve que o tráfego agora é distribuído apenas entre os hosts saudáveis."
pause_and_clear

echo "=== DEMONSTRAÇÃO CONCLUÍDA ==="
echo -e "Não esqueça de rodar o seu script de shutdown agora para economizar o voucher!"
