#!/usr/bin/env python3
"""
Fase 3 - FarmTech Solutions: carga dos dados tratados no Oracle.

O que faz:
  - Le data/leituras_tratadas.csv e data/dados_manejo_culturas.json
  - Insere culturas e manejo (por chave primaria, sem duplicar)
  - Desnormaliza cada leitura em 3 linhas de TB_LEITURA_SENSOR:
    S1 = umidade, S2 = pH, S3 = nutrientes (P e K; N vai como
    observacao da linha S3? Nao: para nao perder o N da Fase 2,
    S3 grava P, e o N e gravado como sensor S3N em linha propria.
    Ver README: a Fase 3 lista P e K no S3, a Fase 2 tem N, P, K.)
  - Insere 1 linha por ciclo em TB_BOMBA_HISTORICO
  - Carga repetivel: MERGE (Oracle) pela chave primaria, ou
    seja, rodar duas vezes nao duplica nenhum registro.

Configuracao (variaveis de ambiente, nunca neste arquivo):
  ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN
  Exemplo de DSN: localhost:1521/FREEPDB1 (Docker oracle-free)
  ou o DSN do Oracle Cloud Free Tier.

Dependencia: pip install oracledb (modo thin, sem Instant Client)
Se oracledb nao estiver instalado, o script avisa e sai sem
fingir que carregou nada.

Uso:
    ORACLE_USER=farmtech ORACLE_PASSWORD=... ORACLE_DSN=... \
        python3 src/carga_oracle.py
    python3 src/carga_oracle.py --dry-run   # so conta, nao conecta
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
VAZAO_L_H = 120.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta os registros sem conectar no Oracle")
    args = parser.parse_args()

    tratadas = pd.read_csv(BASE / "data" / "leituras_tratadas.csv",
                           parse_dates=["data_hora"])
    manejo = json.loads((BASE / "data" / "dados_manejo_culturas.json").read_text())

    n_leituras = len(tratadas) * 5  # S1, S2, S3(P), S3K(K), S3N(N)
    n_bomba = len(tratadas)
    print(f"Culturas: {len(manejo['culturas'])}")
    print(f"Manejo: {len(manejo['manejo'])}")
    print(f"Linhas de leitura a carregar: {n_leituras}")
    print(f"Linhas de bomba a carregar: {n_bomba}")
    if args.dry_run:
        print("Dry-run: nenhuma conexao feita, nada foi gravado.")
        return

    try:
        import oracledb
    except ImportError:
        print("ERRO: pacote 'oracledb' nao instalado. Rode:")
        print("  pip install -r requirements.txt")
        print("Nada foi carregado no Oracle.")
        sys.exit(1)

    user = os.environ.get("ORACLE_USER")
    password = os.environ.get("ORACLE_PASSWORD")
    dsn = os.environ.get("ORACLE_DSN")
    if not all([user, password, dsn]):
        print("ERRO: defina ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN.")
        print("Nada foi carregado no Oracle.")
        sys.exit(1)

    conn = oracledb.connect(user=user, password=password, dsn=dsn)
    cur = conn.cursor()
    try:
        for c in manejo["culturas"]:
            cur.execute(
                """MERGE INTO TB_CULTURA t USING (SELECT :1 id, :2 nome FROM DUAL) s
                   ON (t.ID_CULTURA = s.id)
                   WHEN NOT MATCHED THEN INSERT
                   (ID_CULTURA, NOME, NOME_CIENTIFICO, AREA_HA, PH_IDEAL_MIN,
                    PH_IDEAL_MAX, OBSERVACAO)
                   VALUES (:1, :2, :3, :4, :5, :6, :7)""",
                [c["id_cultura"], c["nome"], c.get("nome_cientifico"),
                 c.get("area_ha"), c.get("ph_ideal_min"), c.get("ph_ideal_max"),
                 c.get("observacao")],
            )
        for m in manejo["manejo"]:
            cur.execute(
                """MERGE INTO TB_MANEJO t USING (SELECT :1 id FROM DUAL) s
                   ON (t.ID_MANEJO = s.id)
                   WHEN NOT MATCHED THEN INSERT
                   (ID_MANEJO, ID_CULTURA, DATA_MANEJO, ATIVIDADE, INSUMO,
                    QUANTIDADE_INSUMO, UNIDADE_INSUMO)
                   VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5, :6, :7)""",
                [m["id_manejo"], m["id_cultura"], m["data_manejo"],
                 m["atividade"], m["insumo"], m["quantidade_insumo"],
                 m["unidade_insumo"]],
            )
        # Sensores: S1 umidade, S2 pH, S3 fosforo, S3N nitrogenio.
        # Potassio: gravado como S3K para nao perder dado da Fase 2.
        # (A Fase 3 lista P e K no S3; a separacao S3/S3K/S3N preserva
        # todos os valores originais sem inventar uma media.)
        registros = []
        for row in tratadas.itertuples(index=False):
            ts = row.data_hora.to_pydatetime()
            origem = str(row.origem)
            for sensor, valor, unidade in [
                ("S1", row.umidade, "%"),
                ("S2", row.ph, "pH"),
                ("S3", row.fosforo, "%"),
                ("S3K", row.potassio, "%"),
                ("S3N", row.nitrogenio, "%"),
            ]:
                registros.append((ts, sensor, 1, float(valor), unidade, origem))
        cur.executemany(
            """MERGE INTO TB_LEITURA_SENSOR t
               USING (SELECT :1 dh, :2 s FROM DUAL) s
               ON (t.DATA_HORA = s.dh AND t.ID_SENSOR = s.s)
               WHEN NOT MATCHED THEN INSERT
               (DATA_HORA, ID_SENSOR, ID_CULTURA, VALOR, UNIDADE, ORIGEM)
               VALUES (:1, :2, :3, :4, :5, :6)""",
            registros,
        )
        bomba = [
            (row.data_hora.to_pydatetime(), 1, int(row.bomba_ligada),
             int(row.bomba_ligada) * VAZAO_L_H, str(row.origem))
            for row in tratadas.itertuples(index=False)
        ]
        cur.executemany(
            """MERGE INTO TB_BOMBA_HISTORICO t
               USING (SELECT :1 dh FROM DUAL) s ON (t.DATA_HORA = s.dh)
               WHEN NOT MATCHED THEN INSERT
               (DATA_HORA, ID_CULTURA, BOMBA_LIGADA, AGUA_L, ORIGEM)
               VALUES (:1, :2, :3, :4, :5)""",
            bomba,
        )
        conn.commit()
        print(f"Carga concluida: {len(registros)} leituras, {len(bomba)} ciclos.")
        print("Rode novamente para confirmar: MERGE nao duplica registros.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
