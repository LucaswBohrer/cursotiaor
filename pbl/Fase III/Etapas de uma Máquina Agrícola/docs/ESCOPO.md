# Escopo — Fase 3: Etapas de uma Máquina Agrícola (FarmTech Solutions)

> Documento de escopo em revisão. Nada aqui é entrega final até o grupo
> confirmar as decisões marcadas como PENDENTE. Este documento vive só
> na Fase 3; nada da Fase 2 foi alterado.

## Decisões já tomadas (atualizado 28/10, após definição de escopo)

- **Cultura âncora: MILHO** (pH alvo 5,5–6,5).
- **Fase 2 intacta:** ajustes do retorno da avaliação só na Fase 3.
- **Ir Além: OS DOIS** (Ir Além 1 — ESP32 eficiente; Ir Além 2 — MongoDB).
- **Vídeo:** como na Fase 2 — Muse faz a gravação/montagem da tela e
  o Lucas faz a narração (áudios gravados por ele, como no v10).
- **Repositório: PÚBLICO POR ENQUANTO.** O `cursotiaor` está público
  (confirmado). Isso NÃO atende o enunciado da Fase 3, que exige
  privado só com `fiap-tutoria` — a mudança para privado fica
  pendente para antes da entrega, por decisão do Lucas.
- **Oracle: A VERIFICAR NO PORTAL FIAP.** O Lucas acredita que a FIAP
  dá algum tipo de acesso ao Oracle; verificação no Portal do Aluno
  (somente leitura, sem submeter avaliações) está em andamento.
  Até confirmar, Docker local e Oracle Cloud Free Tier seguem como
  alternativas documentadas, não como decisão.
- **Repositório de trabalho local:** `pbl/Fase III/Etapas de uma Máquina Agrícola/`,
  sem push até decidir o repositório de entrega.

## Parte 1 — Coleta e processamento das leituras (obrigatória, 3,0 pts)

- [x] Pronto localmente: CSV bruto com 32 leituras reais da Fase 2 +
      2.160 simuladas (origem marcada), período 18/09–27/12/2026.
- [x] Pronto localmente: tratamento Pandas/NumPy (conversão de tipos,
      descarte fora da faixa física, média móvel 24 h em umidade e pH).
- [x] Pronto localmente: indicadores por dia (horas de bomba,
      acionamentos, água estimada a 120 L/h, médias e extremos).
- [x] Pronto localmente: 4 gráficos (umidade/pH no tempo, leituras vs.
      bomba, distribuição, mapa de calor de correlação).
- [ ] A revisar pelo grupo: números e interpretação dos gráficos no README.

## Parte 2 — Ambiente Oracle e primeira persistência (obrigatória, 2,0 pts + 2,0 pts de requisitos)

- [x] Pronto localmente: schema com 4 tabelas (cultura, manejo,
      leitura de sensor, histórico da bomba), 6 informações de gestão
      listadas e 6 consultas em SQL.
- [x] Pronto localmente: carga Python com MERGE (repetível, sem duplicar).
- [x] VERIFICADO NO PORTAL FIAP EM 28/10 (somente leitura, sem tocar
      em avaliações): **não há acesso ao Oracle fornecido pela FIAP
      nas aulas verificadas** — Fase 3 (Caps 1–13, incluindo Cap 8 de
      Banco de Dados e Cap 9 relacional/não-relacional) e Fase 2
      (Caps 1–11 + How To Google Colab). Oracle aparece só como
      exemplo teórico/histórico de SGBD relacional e em tipos de
      dados de exemplo; a busca interna do portal por "Oracle" não
      retornou resultados. Nenhum link, instalação ou credencial.
- [x] DECIDIDO EM 28/10: Docker local (opção 1). `docker-compose.yml`
      pronto (Oracle + Mongo). Sem Docker aqui, por isso a carga
      real e as evidências ainda dependem da máquina do grupo.
- [ ] PENDENTE — evidências: prints da criação das tabelas, da carga
      (2x, sem duplicar) e de cada consulta, em `evidencias/`.

## Documentação e entrega (obrigatórias, 1,0 + 1,0 + 1,0 pts)

- [x] Pronto localmente: README da Fase 3 com objetivo, cultura,
      origem dos dados, tabelas, execução, gráficos e equipe.
- [ ] PENDENTE — vídeo demonstrativo (até 4 min, YouTube não listado):
      mostrar tratamento, indicadores, gráficos, banco, carga e consultas.
      Formato como na Fase 2: Muse monta a gravação de tela, Lucas
      grava a narração (áudios por seção, como no v10 da Fase 2).
- [ ] PENDENTE — arquivo `.txt` do Portal do Aluno: só link do repo
      privado + link do vídeo.
- [ ] PENDENTE — repositório de entrega: o enunciado exige GitHub
      **privado**, compartilhado só com `fiap-tutoria`. O `cursotiaor`
      atual é público. Decidir: repo privado separado ou mudar a
      visibilidade do atual — antes de qualquer push da Fase 3.

## Ir Além (opcionais, fora da nota base de 10) — DECIDIDO: FAZER OS DOIS

- [x] Código pronto — Ir Além 1 (ESP32 eficiente): firmware otimizado
      em `IR ALÉM/ir-alem-1/`.
      Pendente: medição de memória (`pio run` antes/depois) + vídeo próprio.
- [x] Código pronto — Ir Além 2 (NoSQL/MongoDB): carga, consultas e
      comparação em `IR ALÉM/ir-alem-2/`.
      Pendente: execução no Mongo via Docker + vídeo próprio.
- Regra do enunciado: ambos ficam na pasta `IR ALÉM/` do mesmo repo,
  sem criar outro repositório e sem outro link no `.txt` (só o vídeo
  extra é acrescentado).

## Fora do escopo desta fase

- Não alterar nada na pasta da Fase 2.
- Não submeter nada no Portal do Aluno por aqui.
- O próximo passo sugerido pelo avaliador da Fase 2 (o R decidir a
  bomba pelas estatísticas) não entra nesta fase, salvo decisão
  explícita do grupo.
