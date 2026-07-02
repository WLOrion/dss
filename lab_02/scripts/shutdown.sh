#! /bin/bash

# Deleta instâncias
gcloud compute instances delete ws-1 ws-2 ws-3 ws-4 dash-node -q

# Deleta regra de firewall
gcloud compute firewall-rules delete allow-p2p-traffic -q