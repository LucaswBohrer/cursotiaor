# Guia Windows + roteiro para explicar a Fase 3

> Este guia é o passo a passo para rodar na máquina do grupo o que
> foi construído até aqui, e o roteiro para explicar o projeto sem
> decorar — entender o fluxo basta para responder às perguntas.

## 0. Antes de começar: o que está (e o que NÃO está) pronto

**Pronto, neste repositório:**
- CSV bruto (2.192 linhas) e tratado (2.178 linhas), indicadores,
  4 gráficos, 6 consultas, schema Oracle, carga Oracle (MERGE),
  carga MongoDB, firmware otimizado do Ir Além 1.
- Tudo reproduzível em Python: `src/tratamento.py` refaz tratados,
  indicadores e gráficos a partir do CSV bruto.

**NÃO feito ainda (e não pode ser apresentado como feito):**
- Carga real no Oracle e no MongoDB, prints em `evidencias/`,
  compilação dos firmwares no PlatformIO e tabela de memória.
  Isso só roda na máquina do grupo: aqui não há Docker nem
  PlatformIO. O passo a passo abaixo é exatamente para fechar isso.

**Atenção para a entrega:** o enunciado pede repositório **privado**,
compartilhado só com `fiap-tutoria`. Este repositório está público
por decisão temporária do grupo — virar para privado (ou criar o
privado) é um passo obrigatório **antes** da entrega final, e o
arquivo `.txt` do Portal só deve apontar para o link privado.

## 1. Preparar a máquina (Windows)

1. Instalar: **Docker Desktop** (com WSL 2), **Python 3.12+**,
   **Git** e **VS Code** (com a extensão PlatformIO, só para o
   Ir Além 1).
2. Clonar o repositório e entrar na pasta da Fase 3:

```powershell
git clone https://github.com/LucaswBohrer/cursotiaor.git
cd cursotiaor\"pbl\Fase III\Etapas de uma Máquina Agrícola"
```

3. Instalar as dependências Python:

```powershell
pip install -r requirements.txt
pip install pymongo   # só para o Ir Além 2
```

4. (Opcional, para conferir que tudo reproduz) Regerar os
   resultados a partir do CSV bruto:

```powershell
python src\tratamento.py
```

## 2. Oracle no Docker (Parte 2)

1. Trocar a senha placeholder em `docker-compose.yml`
   (`trocar-esta-senha`) por uma senha sua, e subir só o Oracle:

```powershell
docker compose up -d oracle
docker compose ps   # esperar o status ficar healthy (leva minutos na 1ª vez)
```

2. Criar o usuário da aplicação. Conecte como SYSTEM no
   `localhost:1521/FREEPDB1` (SQL Developer, VS Code ou `sqlplus`
   dentro do container) e rode:

```sql
CREATE USER farmtech IDENTIFIED BY "<sua-senha>";
GRANT CONNECT, RESOURCE TO farmtech;
ALTER USER farmtech QUOTA UNLIMITED ON USERS;
```

3. Criar as tabelas rodando `sql/schema.sql` como o usuário
   `farmtech`. Conferir:

```sql
SELECT table_name FROM user_tables;
-- esperado: TB_CULTURA, TB_MANEJO, TB_LEITURA_SENSOR, TB_BOMBA_HISTORICO
```

4. Rodar a carga (PowerShell — senha por variável de ambiente,
   nunca no código):

```powershell
$env:ORACLE_USER="farmtech"
$env:ORACLE_PASSWORD="<sua-senha>"
$env:ORACLE_DSN="localhost:1521/FREEPDB1"
python src\carga_oracle.py
```

   Referência do que deve aparecer: 10.890 linhas de leitura
   (2.178 ciclos × 5 sensores) + 2.178 de bomba.

5. **Prova de que não duplica:** rodar o comando de novo e contar
   por tabela antes e depois — os totais têm de ficar iguais
   (MERGE pela chave primária DATA_HORA + ID_SENSOR).

```sql
SELECT COUNT(*) FROM TB_LEITURA_SENSOR;   -- 10890
SELECT COUNT(*) FROM TB_BOMBA_HISTORICO;  -- 2178
```

6. Rodar `sql/consultas.sql` (uma consulta por informação de
   gestão) e salvar **print de cada resultado** em `evidencias/`.
   Os números de referência estão em
   `resultados/resultados_consultas_preview.csv` — preview em
   Pandas, não evidência do Oracle; se algum número divergir do
   print, o print do banco é que vale, e a divergência deve ser
   investigada, não escondida.

## 3. MongoDB — Ir Além 2

```powershell
docker compose up -d mongo
python "IR ALÉM\ir-alem-2\carga_mongo.py"
python "IR ALÉM\ir-alem-2\consultas_mongodb.py"
```

Rodar a carga duas vezes também não pode duplicar (upsert +
índice único por data_hora + origem). Salvar a saída em
`evidencias/` junto com as do Oracle.

## 4. Firmware otimizado — Ir Além 1

1. Fazer uma **cópia** do projeto da Fase 2 (nunca mexer no
   original) e substituir `src/main.cpp` por
   `IR ALÉM\ir-alem-1\main_otimizado.cpp`.
2. No VS Code com PlatformIO: `pio run` no original e no
   otimizado, e preencher `IR ALÉM\ir-alem-1\TABELA_MEMORIA.md`
   com RAM e Flash dos dois.
3. Repetir os testes da Fase 2 (e a simulação no Wokwi) nos dois:
   a decisão da bomba tem de ser idêntica ciclo a ciclo.

## 5. Roteiro para explicar (o fluxo, em 2 minutos)

> "A Fase 2 era o circuito: ESP32 lendo umidade, pH e nutrientes e
> decidindo irrigar. A Fase 3 muda o foco da coleta para o
> histórico: pegar essas leituras, tratar, guardar num banco
> relacional e responder perguntas de gestão."

1. **Origem dos dados:** 32 leituras reais dos logs da Fase 2
   (`data/leituras_reais_fase2.csv`) + 2.160 simuladas geradas em
   Python a partir do último estado real, com a mesma lógica
   multicritério da Fase 2 — e a coluna `origem` marca cada linha,
   então nada simulado se passa por real.
2. **Cultura âncora:** milho, porque o retorno da Fase 2 cobrou
   limites pensados para uma cultura — pH alvo 5,5–6,5. A umidade
   60–70 % e os N/P/K em % são faixas herdadas da simulação da
   Fase 2, não referência agronômica externa, e o README diz isso.
3. **Tratamento:** conversão de tipos, descarte de umidade fora de
   0–100 % e pH fora de 0–14 (14 linhas de 2.192), interpolação de
   nutriente ausente, média móvel de 24 h para reduzir ruído.
4. **Indicadores:** 93 dias, 373 h de bomba, 343 acionamentos,
   44.760 L estimados (vazão definida pelo grupo: 120 L/h, 1 ciclo
   = 1 h). pH médio 6,18; 114 leituras (5,2 %) fora da faixa do milho.
5. **Por que a umidade média é baixa (30,76 %)?** Porque, na lógica
   herdada, a bomba só liga com nutriente ativo — o solo seca até
   a necessidade voltar. É comportamento da simulação, documentado,
   não recomendação de manejo.
6. **Por que as correlações com a bomba são fracas (umidade +0,15,
   fósforo +0,13, resto menor)?** Porque a decisão é multicritério
   travada por nutrientes, e o registro do ciclo é pós-ação: a
   umidade da linha já inclui o efeito da irrigação daquele ciclo.
   Correlação aqui não é causalidade.
7. **Oracle:** 4 tabelas com chave primária; cada ciclo vira 5
   linhas de leitura (S1 umidade, S2 pH, S3 fósforo, S3K potássio,
   S3N nitrogênio — o N existe na Fase 2 e não podia ser perdido)
   + 1 linha de bomba. Carga por MERGE: repetível, sem duplicar.
   Docker local porque a FIAP não fornece Oracle nas aulas
   (verificado no portal, só leitura).
8. **MongoDB (Ir Além 2):** o mesmo ciclo vira um documento JSON.
   Bom para formato que muda (sensor novo, campo extra); pior para
   joins e agregações de gestão — por isso os dois se complementam,
   nenhum substitui o outro.
9. **ESP32 eficiente (Ir Além 1):** tipos enxutos onde o dado cabe
   (níveis em `uint8_t`, pontuação em `uint8_t`, LDR em `uint16_t`,
   status e parser sem `String`), lógica idêntica. Ganho esperado
   pequeno, dezenas de bytes — o valor é a revisão documentada e a
   medição, não um número espetacular.
10. **O que o avaliador da Fase 2 pediu e onde foi parar:** cultura
    definida (milho, nesta fase) e leituras ao vivo do DHT22/LDR —
    esta última ficou só como proposta em
    `docs/correcao_leitura_ao_vivo.md`, fora do Ir Além 1, para a
    comparação de memória ser da mesma lógica. A pasta da Fase 2
    não foi alterada em nada.

## 6. Checklist final antes de entregar

- [ ] Docker subiu, carga Oracle rodada 2× sem duplicar, prints
      em `evidencias/`
- [ ] Mongo rodado, saída salva
- [ ] Tabela de memória preenchida com os prints do `pio run`
- [ ] Repositório virado para privado, só com `fiap-tutoria`
- [ ] Vídeos (principal + 2 Ir Além, até 4 min, não listados)
      com links no README e no `.txt` do Portal
- [ ] `.txt` do Portal: link do repo privado + links dos vídeos
