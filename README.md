# DSS - Distributed Systems Study (MC714)

Este repositório armazena os estudos e implementações práticas da disciplina **MC714 - Sistemas Distribuídos** do Instituto de Computação (IC) da UNICAMP, referente ao 1º Semestre de 2026.

## 📂 Estrutura do Repositório

O projeto é organizado em diretórios independentes para cada laboratório, facilitando a manutenção e a reprodutibilidade dos experimentos.

- **Laboratório 01**: Implantação de infraestrutura Web escalável utilizando Google Cloud Platform (GCP). O foco reside na configuração de redundância, regras de firewall e monitorização de ativos.

## 🧠 Conceitos e Fundamentação Teórica

Para a realização das atividades, exploramos conceitos fundamentais que sustentam arquiteturas distribuídas modernas:

### 1. Infraestrutura como Serviço (IaaS)

Neste modelo, abstraímos o hardware físico e gerimos recursos de computação (CPU, RAM, Disco) via software.

- **Regiões e Zonas**: Definimos o contexto geográfico (ex: `us-central1-a`) para otimizar custos e garantir que a aplicação resida em data centers específicos, reduzindo latências.

### 2. Automação e Provisionamento

- **Startup Scripts**: Utilizamos scripts (`startup.sh`) para garantir que cada instância do Compute Engine seja configurada de forma idêntica e automática no momento do boot.
- **Idempotência**: O processo de provisionamento foi desenhado para ser repetível, garantindo que o estado final do servidor Apache seja sempre consistente.

### 3. Camada de Rede e Segurança

- **Firewalls**: Implementamos regras de entrada (_ingress_) baseadas no modelo de segurança mínima, permitindo apenas tráfego TCP na porta 80.
- **Tags de Instância**: Utilizamos marcadores lógicos (`http-server`) para aplicar políticas de segurança de forma seletiva apenas aos nós que compõem o serviço web.

### 4. Gestão de Disponibilidade e Tráfego

Em vez de depender de um único servidor, a solução utiliza técnicas de distribuição para aumentar a resiliência:

- **Load Balancing**: O balanceador atua como uma fachada única (IP externo único) que distribui as requisições entre os nós ativos.
- **Health Checks**: Mecanismo de monitorização proativa que verifica a integridade do serviço. Se um host falha (torna-se _unhealthy_), ele é removido automaticamente do pool de encaminhamento para evitar que o utilizador receba erros.

## 🚀 Como Executar

Para reproduzir o ambiente de qualquer laboratório, siga os passos abaixo:

1.  **Permissões**: Garanta que os scripts podem ser executados:
    ```bash
    chmod +x *.sh
    ```
2.  **Execução**: Inicie o provisionamento automático:
    ```bash
    ./run.sh
    ```
3.  **Limpeza**: Ao finalizar, é **obrigatório** desalocar os recursos para preservar o voucher de faturamento e evitar surpresas:
    ```bash
    ./shutdown.sh
    ```

## 👥 Autores

- [Anita Almeida](https://github.com/anitainfo)
- [Wellington da Silva](https://github.com/WLOrion)

---

_Repositório para fins acadêmicos - IC/UNICAMP._
