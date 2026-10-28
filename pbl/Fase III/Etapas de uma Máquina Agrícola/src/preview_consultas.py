#!/usr/bin/env python3
"""
Preview das consultas de gestao, calculado em Pandas a partir do
CSV tratado -- NAO e saida do Oracle.

Por que existe: neste ambiente nao ha Oracle (sem Docker) e nao
ha credencial de nuvem, entao a carga real no Oracle e o passo
que fica para a maquina do Lucas, com os prints em evidencias/.
Este preview usa exatamente a mesma logica das consultas em
sql/consultas.sql, para o grupo conferir os numeros antes de
rodar no banco, sem fingir que o Oracle ja rodou.

Saida: resultados/resultados_consultas_preview.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
VAZAO_L_H = 120.0


def main() -> None:
    df = pd.read_csv(BASE / "data" / "leituras_tratadas.csv", parse_dates=["data_hora"])
    df["mes"] = df["data_hora"].dt.strftime("%Y-%m")
    df["dia"] = df["data_hora"].dt.date
    linhas = []

    agua_mes = df.groupby("mes")["bomba_ligada"].agg(["sum"]).reset_index()
    for r in agua_mes.itertuples():
        linhas.append({"consulta": "1_agua_por_mes", "periodo": r.mes,
                      "valor": r.sum * VAZAO_L_H, "unidade": "L"})
    ph_mes = df.groupby("mes")["ph"].mean().reset_index()
    for r in ph_mes.itertuples():
        linhas.append({"consulta": "2_ph_medio_mes", "periodo": r.mes,
                      "valor": round(r.ph, 2), "unidade": "pH"})
    top_dias = df.groupby("dia")["bomba_ligada"].sum().sort_values(ascending=False).head(10)
    for dia, horas in top_dias.items():
        linhas.append({"consulta": "3_top_dias_bomba", "periodo": str(dia),
                      "valor": int(horas), "unidade": "horas"})
    um_mes = df.groupby("mes")["umidade"].mean().reset_index()
    for r in um_mes.itertuples():
        linhas.append({"consulta": "5_umidade_media_mes", "periodo": r.mes,
                      "valor": round(r.umidade, 2), "unidade": "%"})
    fora = df[(df["ph"] < 5.5) | (df["ph"] > 6.5)].groupby("mes").size()
    for mes, qtd in fora.items():
        linhas.append({"consulta": "6_ph_fora_faixa_milho_mes", "periodo": mes,
                      "valor": int(qtd), "unidade": "leituras"})
    out = pd.DataFrame(linhas)
    out.to_csv(BASE / "resultados" / "resultados_consultas_preview.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
