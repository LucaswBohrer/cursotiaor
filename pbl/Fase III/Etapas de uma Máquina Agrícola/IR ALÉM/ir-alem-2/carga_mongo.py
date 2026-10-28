#!/usr/bin/env python3
"""
Ir Alem 2 - FarmTech Solutions: leituras brutas em MongoDB.

O que faz:
  - Le ../../data/leituras_brutas.csv (mesmo CSV da Parte 1)
  - Insere cada ciclo de leitura do ESP32 como UM documento JSON
    na colecao `leituras` do banco `farmtech`, preservando os
    campos originais (data_hora, umidade, ph, nitrogenio, fosforo,
    potassio, bomba_ligada, origem).
  - Carga repetivel: `update_one(..., upsert=True)` pela chave
    (data_hora, origem) -- rodar duas vezes nao duplica documentos.
    (MongoDB nao tem PK composta como o Oracle; por isso o filtro
    de upsert faz esse papel, e um indice unico e criado para
    garantir.)
  - Executa as consultas de exemplo e imprime os resultados.

Configuracao (variaveis de ambiente):
  MONGO_URI  (padrao: mongodb://localhost:27017, o servico `mongo`
              do docker-compose.yml da Fase 3)
  Sem senha embutida: o compose local usa Mongo sem autenticacao,
  apenas para a rede local do grupo. Para Atlas, passar a URI
  completa por variavel de ambiente.

Dependencia: pip install pymongo
  (neste ambiente o pymongo nao esta instalado e nao ha Mongo;
  a execucao real fica para a maquina do grupo, com Docker.)

Uso:
    python3 carga_mongo.py            # carga + consultas
    python3 carga_mongo.py --dry-run  # so conta, nao conecta
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(BASE / "data" / "leituras_brutas.csv", parse_dates=["data_hora"])
    print(f"Linhas no CSV bruto: {len(df)}")
    if args.dry_run:
        print("Dry-run: nenhuma conexao feita, nada foi gravado.")
        print("Exemplo de documento (primeira linha):")
        print(df.iloc[0].to_dict())
        return

    try:
        from pymongo import MongoClient
    except ImportError:
        print("ERRO: pacote 'pymongo' nao instalado. Rode: pip install pymongo")
        print("Nada foi carregado no MongoDB.")
        sys.exit(1)

    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as exc:  # noqa: BLE001 - mensagem amigavel ao grupo
        print(f"ERRO: nao foi possivel conectar no MongoDB ({uri}): {exc}")
        print("Suba o servico com: docker compose up -d mongo  (na pasta da Fase 3)")
        sys.exit(1)

    colecao = client["farmtech"]["leituras"]
    # Indice unico = garantia contra duplicata, alem do upsert.
    colecao.create_index([("data_hora", 1), ("origem", 1)], unique=True)
    inseridos = atualizados = 0
    for row in df.itertuples(index=False):
        doc = {
            "data_hora": row.data_hora.to_pydatetime(),
            "umidade": float(row.umidade) if pd.notna(row.umidade) else None,
            "ph": float(row.ph) if pd.notna(row.ph) else None,
            "nitrogenio": float(row.nitrogenio) if pd.notna(row.nitrogenio) else None,
            "fosforo": float(row.fosforo) if pd.notna(row.fosforo) else None,
            "potassio": float(row.potassio) if pd.notna(row.potassio) else None,
            "bomba_ligada": int(row.bomba_ligada),
            "origem": str(row.origem),
            "sensores": {"umidade": "S1", "ph": "S2", "nutrientes": "S3"},
            "cultura": "milho",
        }
        res = colecao.update_one(
            {"data_hora": doc["data_hora"], "origem": doc["origem"]},
            {"$set": doc},
            upsert=True,
        )
        if res.upserted_id is not None:
            inseridos += 1
        elif res.modified_count:
            atualizados += 1
    print(f"Documentos inseridos: {inseridos}, atualizados: {atualizados}")
    print(f"Total na colecao: {colecao.count_documents({})}")

    # --- Consultas de exemplo ---
    print("\n[1] Leituras com umidade abaixo de 40% (primeiras 5):")
    for doc in colecao.find({"umidade": {"$lt": 40}}).limit(5):
        print(" ", doc["data_hora"], doc["umidade"], "bomba:", doc["bomba_ligada"])
    print("\n[2] Ciclos com bomba ligada:")
    print(" ", colecao.count_documents({"bomba_ligada": 1}))
    print("\n[3] Leituras com pH fora da faixa do milho (5,5-6,5):")
    print(" ", colecao.count_documents(
        {"$or": [{"ph": {"$lt": 5.5}}, {"ph": {"$gt": 6.5}}]}))
    print("\n[4] Media de umidade (agregacao):")
    agg = list(colecao.aggregate([
        {"$group": {"_id": None, "umidade_media": {"$avg": "$umidade"}}}
    ]))
    print(" ", agg[0]["umidade_media"] if agg else None)
    client.close()


if __name__ == "__main__":
    main()
