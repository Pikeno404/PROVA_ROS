# 1ª Avaliação Prática - Robô Explorador (ROS 2)

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20%7C%20Iron-22314E?logo=ros&logoColor=white)](https://ros.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C%2B%2B-Interfaces-00599C?logo=cplusplus&logoColor=white)](https://isocpp.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Disciplina:** Tópicos Especiais em Redes de Computadores  
**Equipe:**
- **Kleiton Josivan Lima de Oliveira**
- **Ciro Assuero Cabral da Silva Menezes**

---

## 📖 Descrição do Cenário

Um robô móvel autônomo opera em uma região inóspita caracterizada por escassez de oxigênio e temperaturas elevadas. O sistema embarcado conta com sensores de telemetria ambiental (oxigênio e temperatura), posicionamento geográfico via GPS (latitude e longitude) e um dispositivo atuador para perfuração e coleta de amostras geológicas para posterior análise na base central.

Este projeto implementa os três pilares fundamentais da comunicação entre nós no ecossistema **ROS 2**:
1. **Tópicos (`Publish` / `Subscribe`):** Telemetria contínua dos sensores e classificação de segurança.
2. **Serviços (`Client` / `Server`):** Requisito pontual de coleta e perfuração com resposta de confirmação.
3. **Ações (`Action Client` / `Action Server`):** Controle contínuo de deslocamento com telemetria de feedback e suporte a cancelamento sob demanda.

---

## 📁 Estrutura do Workspace

```text
PROVA_ROS/
└── src/
    ├── robo_interfaces/             # Pacote ament_cmake com as mensagens, serviços e ações
    │   ├── msg/
    │   │   └── Monitoramento.msg    # float64 oxigenio, float64 temperatura
    │   ├── srv/
    │   │   └── ColetaAmostra.srv    # float64 profundidade -> bool sucesso
    │   ├── action/
    │   │   └── Deslocamento.action  # Meta, resultado e feedback de deslocamento
    │   ├── CMakeLists.txt
    │   └── package.xml
    │
    └── robo_explorador/             # Pacote ament_python com os nós executáveis
        ├── robo_explorador/
        │   ├── __init__.py
        │   ├── robo_topico_publish.py          # Publicador de telemetria (1Hz)
        │   ├── robo_topico_subscriber.py       # Assinante e classificador (Safe / Not Safe)
        │   ├── robo_coleta_servidor.py         # Servidor de coleta de solo (70% de sucesso)
        │   ├── robo_coleta_cliente.py          # Cliente de requisição de coleta
        │   ├── robo_deslocamento_servidor.py   # Servidor de ação de navegação
        │   ├── robo_deslocamento_cliente.py    # Cliente padrão de ação
        │   └── robo_deslocamento_cancela.py    # Cliente com cancelamento aos 5s
        ├── resource/
        ├── test/
        ├── package.xml
        ├── setup.cfg
        └── setup.py
```

---

## ⚙️ Compilação e Preparação do Ambiente

Dentro do diretório raiz do workspace ROS 2:

```bash
# 1. Carregar variáveis do ROS 2
source /opt/ros/$ROS_DISTRO/setup.bash

# 2. Instalar dependências se necessário
rosdep install --from-paths src --ignore-src -r -y

# 3. Compilar os pacotes
colcon build --symlink-install

# 4. Carregar o overlay local
source install/setup.bash
```

---

## 🚀 Como Executar os Nós

### 1. Monitoramento Ambiental (Tópicos)
O publicador gera dados aleatórios a cada segundo no tópico `/monitoramento`. O assinante avalia se as condições são seguras:
- **`Safe`**: se $10 \le \text{temperatura} \le 40$ °C e $\text{oxigênio} > 80\%$.
- **`Not Safe`**: caso contrário.

**Terminal 1 (Publicador):**
```bash
ros2 run robo_explorador robo_topico_publish
```

**Terminal 2 (Assinante):**
```bash
ros2 run robo_explorador robo_topico_subscriber
```

---

### 2. Coleta de Material do Solo (Serviços)
O cliente solicita uma perfuração em profundidade entre $0.1$ m e $0.5$ m. O servidor simula a taxa mecânica de sucesso de 70%.

**Terminal 1 (Servidor):**
```bash
ros2 run robo_explorador robo_coleta_servidor
```

**Terminal 2 (Cliente):**
```bash
ros2 run robo_explorador robo_coleta_cliente
```

---

### 3. Navegação e Deslocamento (Ações)
O servidor recebe coordenadas de latitude, longitude e velocidades para calcular o trajeto incremental com envio de feedback a cada segundo.

**Terminal 1 (Servidor de Ação):**
```bash
ros2 run robo_explorador robo_deslocamento_servidor
```

**Terminal 2 — Opção A: Execução Completa até a Meta:**
```bash
ros2 run robo_explorador robo_deslocamento_cliente
# Ou passando argumentos customizados: ros2 run robo_explorador robo_deslocamento_cliente 8.0 10.0 1.5 1.5
```

**Terminal 2 — Opção B: Cancelamento Programado (após 5 segundos):**
```bash
ros2 run robo_explorador robo_deslocamento_cancela
```

---

## 🛡️ Licença
Distribuído sob a licença **Apache-2.0**.
