#!/usr/bin/env python3
"""
Ir Alem 2 - Consultas de gestao no MongoDB (Fase 3, FarmTech).

Rodar DEPOIS de carga_mongo.py, contra o mesmo banco `farmtech`,
colecao `leituras`. Consultas espelhando as perguntas de gestao
da Parte 2, incluindo medias por origem (real x simulada).

Uso:
    python3 consultas_mongodb.py [--uri mongodb://localhost:27017]

Sem MongoDB neste ambiente: execucao real fica para a maquina
do grupo, com `docker compose up -d mongo` na pasta da Fase 3.
"""
from __future__ import annotations

import argparse
import sys

from pymongo import MongoClient


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="mongodb://localhost:27017")
    args = parser.parse_args()

    colecao = MongoClient(args.uri)["farmtech"]["leituras"]

    print("== 1. Leituras com umidade < 40% (limite minimo da Fase 2) ==")
    print("Total:", colecao.count_documents({"umidade": {"$lt": 40}}))

    print("\n== 2. Ciclos com a bomba ligada ==")
    print("Total:", colecao.count_documents({"bomba_ligada": 1}))

    print("\n== 3. Medias por origem (real x simulada) ==")
    for grupo in colecao.aggregate([
        {"$group": {
            "_id": "$origem",
            "media_umidade": {"$avg": "$umidade"},
            "media_ph": {"$avg": "$ph"},
            "ciclos": {"$sum": 1},
        }}
    ]):
        print(grupo)

    print("\n== 4. Exemplo de documento (primeira leitura real) ==")
    print(colecao.find_one({"origem": "real"}, {"_id": 0}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
