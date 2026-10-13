# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" width="40%">
  </a>
</p>

# FarmTech Solutions - Fase 2

## Sistema de Irrigação Inteligente com ESP32, Simulação Ambiental e Integração Meteorológica

## 👨‍🎓 Integrantes

- **Gabriel Kuwamoto** — RM567125
- **Guilherme Rodrigues** — RM574372
- **João Rolnik Souza** — RM576079
- **Lucas Welter Bohrer** — RM576902

## 👩‍🏫 Professor(a) / Tutor(a)

### Tutor(a)

- **Sabrina Otoni**

## 📜 Descrição

O projeto **FarmTech Solutions - Fase 2** apresenta uma solução acadêmica de irrigação inteligente desenvolvida para demonstrar a integração entre Internet das Coisas (IoT), sistemas embarcados, automação, integração de dados meteorológicos e análise de dados.

O controlador utilizado é um **ESP32 simulado no Wokwi**. O sistema lê variáveis ambientais, identifica necessidades simuladas de nutrientes e controla uma bomba de irrigação por meio de um relé. A solução utiliza um sensor DHT22 para temperatura e umidade, um LDR para representar o pH e chaves digitais para simular os níveis de Nitrogênio (N), Fósforo (P) e Potássio (K).

A decisão de irrigação é baseada em uma pontuação multicritério. Baixa umidade, pH fora da faixa de referência e necessidades de nutrientes contribuem para essa pontuação. A irrigação somente é autorizada quando há pelo menos um nutriente ativo, a pontuação atinge o limite definido e não existe previsão de chuva relevante.

Uma aplicação em Python consulta a previsão meteorológica e calcula a precipitação acumulada para os próximos 3, 6, 12 e 24 horas. Essas informações são enviadas ao ESP32 por comunicação serial. Quando a previsão atende aos critérios de chuva relevante, a irrigação é bloqueada mesmo que as condições locais indiquem necessidade.

Os dados gerados pelo ESP32 são capturados automaticamente em arquivos `.txt` pelo logger em Python. Em seguida, scripts em R processam os registros e utilizam o Quarto para gerar um relatório com indicadores, gráficos, decisões de irrigação, evolução dos nutrientes, comportamento meteorológico e análise dos ciclos de irrigação.

Os valores de nutrientes, pH, umidade utilizada na lógica e efeitos da irrigação são **simulados**. Portanto, os resultados têm finalidade acadêmica e demonstrativa e não representam uma validação agronômica para uso em uma propriedade rural real.

## 🎯 Objetivos

### Objetivo geral

Desenvolver uma solução simulada de irrigação inteligente capaz de combinar variáveis ambientais, necessidades de nutrientes e previsão meteorológica para apoiar automaticamente a decisão de acionamento de uma bomba de irrigação.

### Objetivos específicos

- Simular um sistema de sensores utilizando ESP32 e Wokwi.
- Monitorar temperatura e umidade por meio do DHT22.
- Utilizar um LDR para representar o pH do solo.
- Simular níveis de Nitrogênio, Fósforo e Potássio.
- Implementar uma lógica de decisão multicritério.
- Controlar uma bomba de irrigação simulada por relé.
- Integrar dados meteorológicos externos.
- Utilizar a previsão de chuva como camada adicional da decisão.
- Registrar automaticamente os dados produzidos pelo sistema.
- Processar os registros utilizando R.
- Gerar um relatório automatizado com Quarto.
- Analisar o comportamento dos ciclos de irrigação.
- Demonstrar a integração entre sistemas embarcados, Python e análise de dados.

## 🧠 Funcionamento do sistema

A arquitetura do projeto é composta por quatro camadas principais:

```text
                         ┌─────────────────────┐
                         │       Wokwi         │
                         │   ESP32 simulado    │
                         └──────────┬──────────┘
                                    │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
               Sensores       Nutrientes       Atuadores
              DHT22 / LDR       N / P / K       Relé / LED
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │ Decisão multicritério│
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ Integração climática│
                         │ Python + previsão   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Decisão final     │
                         │ IRRIGAR / NÃO       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              Logs `.txt`
                                    │
                       ┌────────────▼────────────┐
                       │          R + Quarto      │
                       │ Análise e relatório final│
                       └─────────────────────────┘
```

## 🖥️ Simulação no Wokwi

O circuito foi desenvolvido e validado no simulador **Wokwi** utilizando um ESP32 DevKitC V4. As imagens abaixo registram a montagem e diferentes estados observados durante os testes da simulação.

### Circuito e estados de operação

![Circuito completo](assets/wokwi/wokwi-01.png)

![Simulação - estado 1](assets/wokwi/wokwi-02.png)

![Simulação - estado 2](assets/wokwi/wokwi-03.png)

![Simulação - estado 3](assets/wokwi/wokwi-04.png)

As imagens complementam os testes descritos neste README e no relatório automatizado em R/Quarto.

## Variáveis monitoradas

#### Umidade

A umidade utilizada na lógica de decisão segue estes critérios:

| Faixa de umidade | Pontuação |
|---|---:|
| Abaixo de 40% | +4 |
| De 40% a 59,99% | +2 |
| A partir de 60% | +0 |

A faixa de referência utilizada na simulação é de **60% a 70%**.

#### pH

A faixa considerada adequada na simulação é **5,5 ≤ pH ≤ 7,0**. O valor do pH é obtido pela conversão da leitura do LDR para uma escala simulada de 0 a 14.

| Faixa de pH | Pontuação |
|---|---:|
| Abaixo de 4 ou acima de 8 | +3 |
| De 4 a 5,49 ou de 7,01 a 8 | +2 |
| De 5,5 a 7 | +0 |

#### Nutrientes

Os níveis iniciais utilizados pela simulação são:

| Nutriente | Nível inicial | Referência de atendimento |
|---|---:|---:|
| Nitrogênio (N) | 35% | 70% |
| Fósforo (P) | 50% | 70% |
| Potássio (K) | 40% | 70% |

Quando um nutriente atinge **70%**, ele é considerado **ATENDIDO** e deixa de contribuir para a necessidade de irrigação.

### Decisão multicritério

O limite de pontuação utilizado para permitir a irrigação é **3 pontos**. A decisão final respeita as seguintes regras:

1. **Nenhum nutriente ativo:** se N, P e K estiverem inativos, o sistema não irriga, mesmo que a pontuação ambiental seja elevada.
2. **Pontuação insuficiente:** se houver algum nutriente ativo, mas a pontuação for menor que 3, o sistema não irriga.
3. **Chuva relevante:** se houver previsão de chuva relevante, o sistema não irriga, mesmo com pontuação suficiente.
4. **Irrigação autorizada:** o sistema irriga somente quando existe nutriente ativo, a pontuação é maior ou igual a 3 e não há chuva relevante prevista.

### Integração meteorológica

A aplicação Python consulta a previsão meteorológica e calcula a precipitação acumulada nos seguintes horizontes:

- próximas 3 horas;
- próximas 6 horas;
- próximas 12 horas;
- próximas 24 horas.

Os critérios da simulação são:

| Condição | Critério |
|---|---|
| Chuva forte próxima | 3h ≥ 10 mm |
| Chuva significativa | 6h ≥ 15 mm |
| Chuva relevante | 12h ≥ 10 mm |
| Chuva leve | Chuva maior que 0 mm abaixo dos limites anteriores |
| Sem chuva relevante | Nenhuma das condições anteriores |

A chuva leve não bloqueia a irrigação. A chuva relevante ou forte bloqueia a irrigação.

Os dados são enviados ao ESP32 por uma mensagem serial no formato:

```text
WEATHER,RAIN_3H=...,RAIN_6H=...,RAIN_12H=...,RAIN_24H=...,STATUS=...
```

> A chave da API meteorológica deve ser configurada localmente e nunca deve ser publicada no repositório.

## 🐍 Aplicação Python

A pasta `python/` contém os componentes responsáveis pelo processamento externo ao ESP32.

### `logger.py`

Conecta-se à porta serial do Wokwi, captura os relatórios produzidos pelo ESP32 e salva os registros na pasta `logs/`. Cada arquivo recebe um nome baseado na data e no horário da coleta, por exemplo:

```text
logs/2026-09-21_11-16-36.txt
```

O intervalo configurado para a geração dos logs pelo ESP32 é de **15 segundos**.

### `weather.py`

Consulta a previsão meteorológica, calcula os acumulados de precipitação para os horizontes de 3, 6, 12 e 24 horas e envia os resultados ao ESP32 por comunicação serial.

### `test_weather.py`

Contém os testes relacionados ao processamento das informações meteorológicas.

## 📊 Análise de dados com R e Quarto

A pasta `R/` contém os arquivos responsáveis pelo processamento dos logs e pela geração do relatório:

```text
R/
├── analise.R
└── relatorio.qmd
```

A análise automatizada inclui:

- quantidade total de registros;
- umidade média;
- pH médio;
- pontuação média;
- níveis médios de N, P e K;
- quantidade de decisões de irrigação e de não irrigação;
- estado da bomba;
- distribuição dos motivos das decisões;
- evolução da umidade, do pH e da pontuação;
- evolução dos nutrientes;
- precipitação prevista;
- análise dos ciclos de irrigação;
- análise do ciclo mais recente;
- dados completos dos registros.

Novos arquivos `.txt` adicionados à pasta `logs/` são incorporados automaticamente na próxima geração do relatório.

## 📁 Estrutura de pastas

```text
FarmTech_Fase2/
│
├── .gitignore
├── .vscode/
│   ├── extensions.json
│   └── tasks.json
│
├── R/
│   ├── analise.R
│   └── relatorio.qmd
│
├── include/
│   └── README
├── lib/
│   └── README
├── logs/
│   └── arquivos de log gerados pelo sistema
│
├── python/
│   ├── logger.py
│   ├── test_weather.py
│   └── weather.py
│
├── src/
│   └── main.cpp
├── test/
│   └── README
│
├── assets/
│   ├── logo-fiap.png
│   └── wokwi/
│       ├── wokwi-01.png
│       ├── wokwi-02.png
│       ├── wokwi-03.png
│       └── wokwi-04.png
├── diagram.json
├── platformio.ini
├── wokwi.toml
└── README.md
```

## 🔧 Tecnologias utilizadas

### Hardware e simulação

- ESP32 DevKitC V4;
- Wokwi;
- DHT22;
- LDR;
- relé;
- LED;
- chaves digitais simulando N, P e K.

### Desenvolvimento

- Visual Studio Code;
- PlatformIO;
- Arduino Framework;
- C++.

### Integração

- Python;
- API de previsão meteorológica;
- comunicação serial.

### Análise de dados

- R;
- `ggplot2`;
- `dplyr`;
- `tidyr`;
- Quarto.

### Versionamento

- Git;
- GitHub.

## ▶️ Como executar

### 1. Pré-requisitos

Instale os seguintes componentes:

- Visual Studio Code;
- extensão PlatformIO;
- Python;
- R;
- Quarto;
- Wokwi, conforme a integração utilizada no ambiente local.

O projeto utiliza a placa **ESP32 DevKitC V4** e o ambiente PlatformIO **`esp32dev`**.

### 2. Abrir o projeto

Abra no Visual Studio Code a pasta raiz do projeto:

```text
FarmTech_Fase2/
```

### 3. Configurar a API meteorológica

Configure localmente a chave da API utilizada por `python/weather.py`. Não inclua a chave em arquivos versionados nem a publique no GitHub.

### 4. Compilar o firmware

Utilize o PlatformIO para realizar o build do projeto. A configuração principal está em:

```text
platformio.ini
```

### 5. Executar a simulação

O circuito simulado está descrito em:

```text
diagram.json
```

O arquivo que define o firmware utilizado pelo Wokwi é:

```text
wokwi.toml
```

### 6. Executar o ambiente integrado

O projeto possui uma task configurada no VS Code para iniciar o ambiente integrado. Utilize o atalho:

```text
Ctrl + Alt + W
```

A task executa as seguintes etapas:

1. build do projeto PlatformIO;
2. inicialização do logger;
3. inicialização do serviço meteorológico;
4. inicialização da simulação Wokwi.

## 🧪 Testes realizados

O funcionamento foi validado por diferentes cenários na simulação Wokwi.

| Teste | Cenário | Resultado principal |
|---|---|---|
| 1 | Nenhum nutriente ativo | Bomba inativa e decisão `NÃO IRRIGAR`. |
| 2 | Nutriente já atendido | Nutriente deixa de contribuir para a necessidade; pontuação igual a 0 e bomba inativa. |
| 3 | Necessidade insuficiente | Com Fósforo ativo e condições ambientais adequadas, pontuação igual a 1; bomba inativa. |
| 4 | Necessidade multicritério | Umidade aproximada de 45,8%, pH de 3,42 e Fósforo ativo produziram 6 pontos e acionaram a bomba. Ao final, pontuação igual a 2 e bomba inativa. |
| 5 | N, P e K ativos | Os nutrientes evoluíram até os níveis de atendimento; com pontuação igual a 2, a bomba permaneceu inativa. |
| 6 | Chuva relevante | Mesmo com pontuação suficiente, a previsão de chuva bloqueou a irrigação. |
| 7 | Sem chuva relevante | Com N e P ativos e precipitação igual a 0 mm, a bomba foi acionada até a pontuação deixar de justificar a irrigação. |

No teste 7, foram observadas as seguintes evoluções durante o ciclo:

- N: 43% → 70%;
- P: 54% → 68%;
- umidade: 53,8% → 81,8%;
- pH: 3,92 → 5,67.

## 📈 Resultados da análise dos logs

Na execução local mais recente utilizada para a análise, o relatório em R/Quarto processou **32 registros**.

| Indicador | Resultado |
|---|---:|
| Registros analisados | 32 |
| Umidade média | 66,6% |
| pH médio | 4,70 |
| Pontuação média | 3,94 |
| Média combinada N/P/K | 51,9% |
| Decisões `IRRIGAR` | 7 |
| Decisões `NÃO IRRIGAR` | 25 |
| Registros sem irrigação | 78,1% |
| Registros com bomba ativa | 7 |

> Os valores acima correspondem à execução local mais recente do relatório. Os arquivos de log versionados no repositório representam a evolução do projeto até o commit publicado e podem não coincidir com esse conjunto local mais recente.

Os motivos registrados para as decisões incluem ausência de nutrientes ativos, pontuação abaixo do limite, necessidade multicritério sem chuva relevante e bloqueio por chuva relevante prevista, conforme os cenários de teste realizados.

### Análise dos ciclos de irrigação

Na execução local mais recente foram identificados **4 ciclos completos** pela transição `INATIVA → ATIVA → INATIVA`.

As janelas observadas foram de aproximadamente **32 s, 56 s, 16 s e 31 s**. Esses valores representam intervalos entre registros discretos e não devem ser interpretados como o tempo físico exato de acionamento do relé.

### Ciclo mais recente

O ciclo mais recente ocorreu entre **28/09/2026 08:34:52** e **28/09/2026 08:35:23**, correspondendo a uma janela observada de **31 segundos**.

| Variável | Inicial | Final |
|---|---:|---:|
| Umidade | 47,8% | 71,8% |
| pH | 3,57 | 5,62 |
| Nitrogênio | 35% | 35% |
| Fósforo | 52% | 66% |
| Potássio | 40% | 55% |

A pontuação evoluiu de **6 para 2**, fazendo com que a condição deixasse de atingir o limite de irrigação. A decisão final registrada foi **`NÃO IRRIGAR`**.

## ⚠️ Limitações

Este projeto possui caráter acadêmico e utiliza simulações para representar determinadas condições ambientais. As principais limitações são:

- os níveis de N, P e K são simulados;
- o pH é simulado a partir da leitura do LDR;
- os efeitos da irrigação sobre a umidade e o pH são parâmetros da simulação;
- os valores utilizados para a evolução dos nutrientes são parâmetros acadêmicos;
- a umidade medida pelo DHT22 é distinta da variável de umidade utilizada pela lógica, que pode ser simulada;
- a previsão meteorológica depende da disponibilidade e da precisão da API utilizada;
- os dados meteorológicos não representam uma medição local do solo;
- os resultados não constituem validação agronômica para uso em uma propriedade rural real.

O objetivo principal é demonstrar a arquitetura tecnológica, a integração entre sistemas e o funcionamento da lógica de decisão.

## 🚀 Possíveis evoluções

Como evoluções futuras, o projeto pode incorporar:

- sensores reais de umidade do solo;
- sensores reais de pH;
- sensores físicos para N, P e K;
- armazenamento dos dados em banco de dados;
- dashboard em tempo real;
- histórico de irrigação;
- controle remoto do sistema;
- modelos preditivos;
- integração com outras fontes meteorológicas;
- calibração dos parâmetros com dados reais;
- implementação em hardware físico;
- alertas para eventos críticos;
- modelos agronômicos reais em substituição aos parâmetros simulados.

## 🗃 Histórico de lançamentos

- **0.2.0 — Fase 2**
  - implementação do sistema de irrigação inteligente;
  - simulação do ESP32 no Wokwi;
  - implementação da decisão multicritério;
  - simulação de N, P e K;
  - integração com DHT22 e LDR;
  - controle da bomba por relé;
  - logger automático em Python;
  - integração meteorológica e consulta de previsão de chuva;
  - análise dos logs com R;
  - geração de relatório com Quarto.
- **0.1.0 — Estrutura inicial**
  - criação do projeto;
  - configuração do PlatformIO e do ESP32;
  - estrutura inicial de diretórios;
  - configuração do Wokwi;
  - estrutura inicial dos scripts Python e R.

## 📋 Licença

Projeto desenvolvido para fins acadêmicos no contexto da FIAP. Os valores, as regras de decisão e os parâmetros ambientais utilizados na simulação possuem finalidade exclusivamente educacional e demonstrativa.

O modelo de README utilizado como referência é disponibilizado pela FIAP sob a licença **Creative Commons Attribution 4.0 International**: [modelo de README da FIAP](https://github.com/agodoi/templateFiapVfinal).

## 🔗 Referências

[1]: https://www.fiap.com.br/ "FIAP - Faculdade de Informática e Administração Paulista"
[2]: https://github.com/agodoi/templateFiapVfinal "Template FIAP utilizado como referência"
[3]: https://wokwi.com/ "Wokwi - Simulador de eletrônica online"
[4]: https://platformio.org/ "PlatformIO - Ecossistema de desenvolvimento para sistemas embarcados"
[5]: https://quarto.org/ "Quarto - Sistema de publicação científica e técnica"
[6]: https://www.r-project.org/ "R Project for Statistical Computing"

## 👥 Equipe

| Integrante | RM |
|---|---|
| Gabriel Kuwamoto | RM567125 |
| Guilherme Rodrigues | RM574372 |
| João Rolnik Souza | RM576079 |
| Lucas Welter Bohrer | RM576902 |
| **Tutor(a)** | **Sabrina Otoni** |
