# Ir Além 2 — Leituras brutas em banco NoSQL (MongoDB)

## Objetivo

Experimentar o armazenamento das leituras brutas do circuito em um
banco de documentos e comparar, com base no próprio projeto, com o
banco relacional (Oracle) da Parte 2.

## O que foi feito

- `carga_mongo.py`: lê o mesmo CSV bruto da Parte 1 e insere cada
  ciclo como um documento JSON na coleção `leituras` do banco
  `farmtech`, preservando todos os campos originais.
- Carga repetível: `upsert` por (data_hora, origem) + índice único —
  rodar duas vezes não duplica documentos (o equivalente, em
  documento, ao MERGE por chave primária do Oracle).
- `exemplo_documento.json`: um documento como fica armazenado.
- Consultas no próprio script e em `consultas_mongodb.py`: umidade
  < 40 %, ciclos com bomba ligada, pH fora da faixa do milho
  (5,5–6,5), média de umidade por agregação e médias por origem
  (real x simulada).

## Como executar (na máquina do grupo — sem Mongo neste ambiente)

```bash
# Na pasta da Fase 3, subir só o Mongo:
docker compose up -d mongo
pip install pymongo
python3 "IR ALÉM/ir-alem-2/carga_mongo.py"
# Para Atlas gratuito, em vez do compose:
# MONGO_URI="mongodb+srv://..." python3 carga_mongo.py
```

## Comparação: documento (MongoDB) vs. relacional (Oracle)

| Situação | Mais conveniente | Por quê, no projeto |
|---|---|---|
| Chega um sensor novo, ou uma leitura vem incompleta / com campo extra | **MongoDB** | O documento aceita campos diferentes por registro, sem migração de schema. No Oracle, seria preciso alterar tabela ou aceitar nulos. |
| Perguntas de gestão com agregação por mês, joins com manejo e culturas | **Oracle** | SQL com `GROUP BY`, joins e chaves primárias/estrangeiras expressa direto as 6 consultas da Parte 2; no Mongo, a mesma pergunta vira pipeline de agregação mais verboso. |
| Garantir que não há duplicata na carga | **Oracle, com ressalva** | A chave primária composta (DATA_HORA, ID_SENSOR) impõe isso no banco. No Mongo foi preciso criar índice único + upsert para obter a mesma garantia — funciona, mas é manual. |
| Evolução do formato ao longo das fases | **MongoDB** | As próximas fases podem acrescentar campos (ex.: novo sensor) sem quebrar as leituras antigas; no Oracle, cada campo novo é uma alteração de schema versionada. |
| Integridade entre leitura, bomba e manejo | **Oracle** | FKs garantem que uma leitura/bomba referencia uma cultura existente; no documento, essa checagem fica por conta da aplicação. |

Conclusão do grupo: **os dois se complementam** — Oracle como
histórico estruturado e auditável das decisões de gestão, MongoDB
como depósito flexível das leituras brutas, que mudam de formato
com o tempo. Nenhum substitui o outro nesta fase.

## Integrantes

Gabriel Kuwamoto (RM567125), Guilherme Rodrigues (RM574372),
João Rolnik Souza (RM576079), Lucas Welter Bohrer (RM576902).
