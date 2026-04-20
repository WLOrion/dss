#! /bin/bash

apt-get update
apt-get install -y apache2

# Cria a página personalizada com o nome da instância para o test
echo '<h1>Servidor: '$(hostname)'</h1>' > /var/www/html/index.html
