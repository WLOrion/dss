# Guia de Desenvolvimento e Integração (MC714)

Este documento explica como utilizar a infraestrutura base (`base.py`) para criar novos algoritmos distribuídos e como conectá-los ao painel de monitoramento centralizado (`dash.py`).

## 1. Como usar o `base.py` (Camada P2P)

O arquivo `base.py` foi criado para abstrair a complexidade de Sockets TCP e Threads. Ele oferece apenas duas funções para que os nós conversem entre si de forma descentralizada. Para implementar um algoritmo novo, você só precisa usar estas duas funções.

### A. Inicializando o Nó (Modo Servidor)

Para que o seu algoritmo consiga escutar mensagens da rede em segundo plano, importe o `base.py` e chame a função `init()`.

Você deve passar o IP, a porta e a **função de callback** (a função do seu algoritmo que vai processar o JSON quando ele chegar).

```python
import base

# Função que será chamada automaticamente quando chegar uma mensagem
def receber_mensagem(m):
    print(f"Mensagem recebida: {m}")

# Inicia a thread do servidor (ex: na porta 8000)
base.init("127.0.0.1", 8000, receber_mensagem)
```

### B. Enviando Mensagens (Modo Cliente)

Quando o seu algoritmo precisar avisar os outros nós sobre algo (ex: iniciar eleição, pedir acesso à região crítica), use a função `snd()`. Não é necessário abrir conexão manualmente.

```python
# O payload deve ser sempre um dicionário (JSON)
mensagem = {"id": "1", "tipo": "ELECTION"}

# Envia para o IP e porta de destino
base.snd("127.0.0.1", 8001, mensagem)
```

## 2. Funcionamento do Dashboard (`dash.py`) e Acoplamento

O `dash.py` é um servidor à parte que roda em apenas **uma** máquina. O papel dele não é participar dos algoritmos, mas sim atuar como um "painel de controle" para visualização (ideal para gravar os vídeos do trabalho).

- **Como ele funciona:** Ele abre um servidor Web na porta `9367` (para você abrir no navegador) e um servidor TCP puro na porta `9368` (para receber os dados dos nós).
- **A tabela de estado:** O dashboard guarda um estado para cada nó, contendo: Relógio (`c`), Últimas Mensagens (`msg`), Líder atual (`ldr`) e Status de Exclusão Mútua (`mtx`).

### Como acoplar um novo algoritmo ao Dashboard

Os nós não param a execução para atualizar o dashboard. Eles mandam um pacote JSON "por fora" avisando que algo mudou. Para plugar o seu algoritmo novo no `dash.py`, basta colar a função auxiliar `s_dsh` no seu código:

```python
import socket
import json

# IP da máquina onde o dash.py está rodando (atualize na nuvem)
DASH_IP = "127.0.0.1"
DASH_PORT = 9368

def s_dsh(n_id, c=None, msg=None, ldr=None, mtx=None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((DASH_IP, DASH_PORT))

        # Monta o pacote apenas com as variáveis que foram passadas
        d = {"id": n_id}
        if c is not None: d["c"] = c
        if msg: d["msg"] = msg
        if ldr: d["ldr"] = ldr
        if mtx: d["mtx"] = mtx

        s.send(json.dumps(d).encode())
        s.close()
    except:
        pass # Se o dash estiver offline, o algoritmo não trava
```

### Exemplos de uso prático (Disparando atualizações)

O dashboard é inteligente: se você mandar atualizar apenas o líder, ele mantém o relógio e as mensagens antigas intactas na tela. Chame a função `s_dsh` nos momentos críticos do seu algoritmo:

**1. No Algoritmo de Lamport (Atualizou o relógio local):**

```python
s_dsh(n_id="1", c=15, msg="REC <- [2] | CLK: 14")
```

**2. No Algoritmo de Eleição (Novo coordenador assumiu):**

```python
s_dsh(n_id="3", ldr="Nó 4")
```

**3. No Algoritmo de Exclusão Mútua (Entrou na Região Crítica):**

```python
s_dsh(n_id="2", mtx="USANDO_RECURSO")
```
