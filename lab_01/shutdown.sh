#! /bin/bash

# Deleta as regras de encaminhamento e pools
gcloud compute forwarding-rules delete lb-mc714 --region us-central1 -q
gcloud compute target-pools delete pool-mc714 --region us-central1 -q

# Deleta as máquinas
gcloud compute instances delete ws-1 ws-2 ws-3 -q

# Limpa regras de firewall e health-check
gcloud compute firewall-rules delete allow-http-mc714 -q
gcloud compute http-health-checks delete check-distribuidos -q
