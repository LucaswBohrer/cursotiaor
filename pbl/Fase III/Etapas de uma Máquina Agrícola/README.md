# FarmTech Solutions — Fase 3: Etapas de uma Máquina Agrícola

## Objetivo

Na Fase 2 o grupo construiu a irrigação inteligente (ESP32 + Wokwi + Python + R):
as leituras existiam só no Monitor Serial e se perdiam a cada execução.
Nesta Fase 3 o sistema ganha **memória**: as leituras viram um histórico
organizado, tratado em Python científico e persistido num banco Oracle,
pronto para análise e para os modelos preditivos das próximas fases.

**Cultura âncora desta fase: MILHO** (*Zea mays*) — decisão do grupo em
28/10/2026, em resposta ao retorno da avaliação da Fase 2, que apontou
que os limites de umidade, pH e nutrientes apareciam como referências
da simulação, sem indicar para qual cultura foram pensados.

## Equipe

| Integrante | RM |
|---|---|
| Gabriel Kuwamoto | RM567125 |
| Guilherme Rodrigues | RM574372 |
| João Rolnik Souza | RM576079 |
| Lucas Welter Bohrer | RM576902 |

> A lista acima reproduz a equipe da Fase 2. Se a composição mudar nesta
> fase, atualizar esta tabela antes da entrega — o enunciado concede
> 1 ponto extra para equipes de 4 a 5 integrantes.

## O que o retorno da Fase 2 mudou aqui (e o que NÃO mudou)

- **Cultura definida:** milho, com faixa-alvo de pH 5,5–6,5 (ver abaixo).
- **Leituras ao vivo:** a correção do firmware da Fase 2 está documentada
  em `docs/correcao_leitura_ao_vivo.md` **como proposta para as próximas
  fases**. Por decisão do grupo, **nada foi alterado na pasta da Fase 2**,
  que permanece intacta como entrega encerrada. A leitura dos logs da
  Fase 2 feita por `src/gerar_dados_brutos.py` é somente leitura.
- **Próximo passo sugerido pelo avaliador** (o script em R decidir ligar
  ou não a bomba a partir das estatísticas) **não** faz parte do
  enunciado da Fase 3 e fica registrado como próximo passo, não como
  entregável desta fase.

## Cultura âncora: milho — de onde vêm os limites

| Parâmetro | Faixa adotada na Fase 3 | Origem / observação |
|---|---|---|
| pH ideal | **5,5–6,5** | Faixa ideal para milho em referências de cultivo (outras fontes citam 6,0–7,0; a faixa 5,5–6,5 é a adotada aqui e é a que o relatório usa para contar leituras fora da faixa). |
| Umidade operacional | 60–70 % (zona de trabalho) | **Faixa herdada da simulação da Fase 2**, mantida para comparabilidade do histórico. Não é apresentada como referência agronômica externa: abaixo de 60 % a lógica passa a pontuar irrigação; abaixo de 40 % pontua mais. |
| Nutrientes N, P, K | Escala simulada 0–100 %, meta 70 % | Escala herdada da Fase 2. Milho é exigente em N, com ordem de exportação N > K > P — o que justifica os três nutrientes como gatilho da bomba. Os % **não** são teores de laboratório (mg/dm³ ou kg/ha). |
| Vazão da bomba | 120 L/h | Parâmetro definido pelo grupo para estimar água aplicada (1 ciclo = 1 h = 120 L). Não é medição de campo. |

## Origem dos dados

- **Fases 1 e 2:** o circuito da Fase 2 (ESP32, DHT22, LDR, chaves N/P/K,
  relé) e seus 32 logs em `pbl/Fase II/Um mapa do tesouro/logs/`.
  `data/leituras_reais_fase2.csv` é a extração exata desses logs, para
  auditoria. O repositório da Fase 2 **não contém um arquivo de
  culturas/manejo**; por isso `data/dados_manejo_culturas.json` é um
  exemplo mínimo e explícito de tabela de trabalho (milho + soja de
  rotação), com aviso no próprio arquivo — não é apresentado como
  dado medido da Fase 1.
- **Volume:** 32 leituras reais não bastam para 3 meses. Como o
  enunciado permite, a série foi complementada em Python a partir do
  padrão das leituras reais, com a mesma lógica de decisão da Fase 2
  (cada ciclo = 1 h). Toda linha complementar está marcada com
  `origem = simulada` no CSV; as reais estão marcadas com `origem = real`.
- **Período coberto:** 18/09/2026 a 27/12/2026 (32 reais + 2.160
  simuladas = 2.192 linhas brutas; 2.178 após limpeza).

## Lista de informações relevantes e dados necessários

| # | Informação de gestão | Dados necessários | Consulta |
|---|---|---|---|
| 1 | Quantidade total de água aplicada em cada mês | Data/hora de cada acionamento + água por ciclo | `sql/consultas.sql` nº 1 |
| 2 | Variação do pH do solo ao longo do tempo | Data/hora + valor do sensor S2 (pH) | nº 2 |
| 3 | Dias com maior tempo de bomba ligada | Data/hora + estado da bomba | nº 3 |
| 4 | Culturas com maior consumo de insumos | Manejo: cultura, insumo, quantidade | nº 4 |
| 5 | Umidade média por mês e leituras abaixo de 60 % | Data/hora + valor do sensor S1 (umidade) | nº 5 |
| 6 | Leituras de pH fora da faixa ideal do milho (5,5–6,5) | Data/hora + valor do sensor S2 | nº 6 |

## Estrutura das tabelas (Oracle)

- `TB_CULTURA` — culturas (milho = 1, soja de rotação = 2).
- `TB_MANEJO` — atividades de manejo e insumos, com FK para cultura.
- `TB_LEITURA_SENSOR` — leituras S1 (umidade), S2 (pH), S3 (P),
  S3K (K) e S3N (N). A separação S3/S3K/S3N preserva todos os valores
  da Fase 2: a Fase 3 lista P e K no S3, mas a Fase 2 tem N, P e K —
  esconder o N seria perder dado real. Chave primária
  (DATA_HORA, ID_SENSOR).
- `TB_BOMBA_HISTORICO` — 1 linha por ciclo/hora, com água estimada.
  Chave primária DATA_HORA.

A chave primária composta é o que torna a carga repetível: o
`MERGE` em `src/carga_oracle.py` não duplica registros ao rodar
duas vezes.

## Como executar

```bash
pip install -r requirements.txt
python3 src/gerar_dados_brutos.py   # data/leituras_brutas.csv
python3 src/tratamento.py           # tratados, indicadores, graficos
python3 src/preview_consultas.py    # preview em Pandas (nao e Oracle)
```

### Oracle via Docker local (decisão do grupo, 28/10/2026)

O Portal FIAP foi verificado (somente leitura) e **não fornece
acesso ao Oracle** nas aulas da Fase 3 nem da Fase 2 — por isso o
grupo decidiu pelo Docker local (opção 1), em vez de Oracle Cloud.

Neste ambiente não há Docker, então a carga real no Oracle **não
foi executada aqui** — e nenhum print é apresentado como se tivesse
sido. Passos, na máquina do grupo (Docker Desktop instalado):

1. Trocar a senha em `docker-compose.yml` e subir:
   `docker compose up -d oracle`
2. Criar o usuário/schema e rodar `sql/schema.sql` (SQL*Plus / SQLcl).
3. Rodar a carga com variáveis de ambiente (nunca no código):
   `ORACLE_USER=... ORACLE_PASSWORD=... ORACLE_DSN=localhost:1521/FREEPDB1
   python3 src/carga_oracle.py`
4. Rodar `sql/consultas.sql` e salvar os prints em `evidencias/`
   (ver `evidencias/README.md`). Para o Mongo do Ir Além 2:
   `docker compose up -d mongo`.

## Tratamento dos dados

1. Conversão de tipos; descarte de umidade fora de 0–100 % e pH fora
   de 0–14 ou ausentes (14 linhas descartadas de 2.192); nutriente
   ausente interpolado no tempo.
2. Média móvel de 24 h sobre umidade e pH (redução de ruído).
3. Indicadores por dia: horas de bomba, acionamentos (transições
   0→1), água estimada, médias e extremos de umidade e pH — em
   `resultados/indicadores_diarios.csv`.
4. Correlação de Pearson + mapa de calor em
   `resultados/correlacao.csv` e `graficos/correlacao_heatmap.png`.

## Resultados (série tratada, 2.178 linhas)

- Bomba ligada: 373 horas, 343 acionamentos, **44.760 L estimados**.
- Umidade média: 30,76 % — baixa porque, na lógica herdada, a bomba
  só liga quando há nutriente ativo; com nutrientes atendidos
  (≥70 %) o solo seca até a necessidade voltar. É um comportamento
  da simulação, não uma recomendação de manejo.
- pH médio: 6,18; leituras fora da faixa do milho (5,5–6,5): 114 (5,2 %).
- Correlação com a bomba ligada: umidade +0,15, fósforo +0,13,
  potássio +0,06, nitrogênio +0,04, pH −0,01. Correlações univariadas
  fracas são esperadas: a decisão é multicritério e travada por
  nutrientes, e o registro do ciclo é **pós-ação** (a umidade
  registrada já inclui o efeito da irrigação daquele ciclo), por
  isso correlação aqui não é causalidade.

## Interpretação dos gráficos

- `umidade_ph_tempo.png` — evolução suavizada (média móvel 24 h) de
  umidade e pH; mostra os ciclos de secagem e irrigação ao longo
  dos 3 meses.
- `leituras_vs_bomba.png` — umidade bruta contra os degraus da bomba;
  os acionamentos concentram-se nos períodos de umidade baixa com
  nutriente ativo.
- `distribuicao_sensores.png` — distribuição de cada sensor; a
  bomba é binária (a maioria dos ciclos desligada, coerente com o
  travamento por nutrientes).
- `correlacao_heatmap.png` — a maior correlação entre sensores é
  nitrogênio × potássio (+0,71), porque ambos sobem juntos na
  irrigação e caem juntos sem ela; nenhuma variável sozinha explica
  a bomba, o que confirma o caráter multicritério da decisão.

## Estrutura de pastas

```text
pbl/Fase III/Etapas de uma Máquina Agrícola/
├── README.md
├── requirements.txt
├── data/
│   ├── leituras_brutas.csv          # 32 reais + 2.160 simuladas
│   ├── leituras_reais_fase2.csv     # so as reais, para auditoria
│   ├── leituras_tratadas.csv
│   └── dados_manejo_culturas.json
├── src/
│   ├── gerar_dados_brutos.py
│   ├── tratamento.py
│   ├── carga_oracle.py              # MERGE, sem duplicar
│   └── preview_consultas.py         # preview em Pandas, nao e Oracle
├── sql/
│   ├── schema.sql
│   └── consultas.sql
├── graficos/
├── resultados/
├── evidencias/                      # prints do Oracle (a capturar)
├── docs/
│   └── correcao_leitura_ao_vivo.md  # proposta, Fase 2 intacta
└── IR ALÉM/                         # opcional, nao iniciado
    └── README.md
```

## Entrega

- **Vídeo demonstrativo (até 4 min, YouTube não listado):** pendente.
  Deve mostrar tratamento, indicadores, gráficos, banco, carga e
  consultas. O link entra aqui no README e no arquivo `.txt` do
  Portal do Aluno quando o vídeo existir.
- **Arquivo `.txt` do Portal:** pendente. Deve conter **apenas** o
  link do repositório GitHub **privado** do grupo (compartilhado
  somente com `fiap-tutoria`) e o link do vídeo.
- **Atenção — repositório:** o `cursotiaor` usado até aqui é
  **público**. O enunciado da Fase 3 exige repositório **privado**,
  compartilhado apenas com `fiap-tutoria`. Esta pasta foi construída
  localmente e **não recebeu push**: antes da entrega, o grupo
  precisa decidir se cria um repositório privado separado para a
  Fase 3 (seguindo o modelo da coordenação) ou se altera a
  visibilidade do atual — decisão que não foi tomada aqui.

## Ir Além (opcional — decidido: fazer os dois)

- **Ir Além 1 — ESP32 eficiente:** código otimizado em
  `IR ALÉM/ir-alem-1/` (tipos enxutos + parser sem
  `String`, lógica idêntica). Medição de memória antes/depois
  pendente: sem PlatformIO neste ambiente, preencher
  `TABELA_MEMORIA.md` com os prints do `pio run` na máquina do grupo.
- **Ir Além 2 — NoSQL (MongoDB):** código, exemplo de documento e
  comparação com o Oracle em `IR ALÉM/ir-alem-2/`.
  Execução pendente: sem Mongo neste ambiente; subir com
  `docker compose up -d mongo` na máquina do grupo.
- Vídeos próprios dos Ir Além (até 4 min, não listados): pendentes,
  mesmo formato do vídeo principal (Muse monta, Lucas narra).

## Licença / uso acadêmico

Projeto acadêmico FIAP. Valores de nutrientes, umidade e pH da série
simulada são parâmetros da simulação da Fase 2, não medições de
campo, e não constituem recomendação agronômica para uma lavoura real.
