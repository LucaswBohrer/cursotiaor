#!/usr/bin/env python3
"""
Fase 3 - FarmTech Solutions: tratamento, indicadores e graficos.

Entrada : data/leituras_brutas.csv (gerado por gerar_dados_brutos.py)
Saidas  : data/leituras_tratadas.csv
          resultados/indicadores_diarios.csv
          resultados/correlacao.csv
          resultados/resumo_tratamento.txt
          graficos/*.png

Tratamento (Pandas + NumPy), na ordem:
  1. Conversao de tipos (data_hora, numeros).
  2. Remocao de leituras fora da faixa fisica dos sensores
     (umidade 0-100 %, pH 0-14, nutrientes 0-100 %) e de valores
     ausentes em umidade/pH, com contagem do que foi descartado.
     Linhas com nutriente ausente tem o nutriente interpolado
     (o sensor de nutrientes e o menos critico para a decisao
     horaria; umidade e pH ausentes descartam a linha).
  3. Reducao de ruido por media movel de 24 h (1 dia) sobre
     umidade e pH -- janela centrada nao usada, para nao vazar
     o futuro para o passado; e media movel simples para tras.
  4. Indicadores de manejo por dia:
     - horas de bomba ligada, numero de acionamentos
       (transicoes 0 -> 1), agua estimada (vazao 120 L/h),
       medias e extremos de umidade e pH.
  5. Faixa-alvo do MILHO (cultura ancora, decisao do grupo):
     pH ideal 5,5-6,5. A serie historica foi gerada com a logica
     da Fase 2 (pH 5,5-7,0); por isso o tratamento NAO reescreve
     o passado: ele apenas conta quantas leituras tratadas ficam
     fora da faixa do milho, para orientar o manejo daqui em
     diante. A faixa de umidade operacional herdada da Fase 2
     (60-70 %) e mantida para comparabilidade, e documentada
     no README como faixa de simulacao, nao como referencia
     agronomica externa.
  6. Correlacao de Pearson entre umidade, pH, nutrientes e
     acionamento da bomba, com mapa de calor (Seaborn).

Graficos (Matplotlib + Seaborn):
  1. umidade_ph_tempo.png      - evolucao de umidade e pH no tempo
  2. leituras_vs_bomba.png     - leituras e acionamentos da bomba
  3. distribuicao_sensores.png - distribuicao de cada sensor
  4. correlacao_heatmap.png    - matriz de correlacao

Uso:
    python3 src/tratamento.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

BASE = Path(__file__).resolve().parents[1]
VAZAO_L_H = 120.0
PH_MILHO_MIN, PH_MILHO_MAX = 5.5, 6.5


def main() -> None:
    brutas = pd.read_csv(BASE / "data" / "leituras_brutas.csv", parse_dates=["data_hora"])
    n_brutas = len(brutas)

    df = brutas.copy()
    for col in ["umidade", "ph", "nitrogenio", "fosforo", "potassio", "bomba_ligada"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Limpeza: fora da faixa fisica ou ausente em umidade/pH ---
    validas = (
        df["umidade"].between(0, 100)
        & df["ph"].between(0, 14)
        & df["umidade"].notna()
        & df["ph"].notna()
    )
    descartadas = int((~validas).sum())
    df = df[validas].copy()
    # Nutriente ausente: interpola no tempo (nao descarta a linha).
    df[["nitrogenio", "fosforo", "potassio"]] = df[
        ["nitrogenio", "fosforo", "potassio"]
    ].interpolate(limit_direction="both")
    df = df.dropna(subset=["nitrogenio", "fosforo", "potassio"])
    df = df.sort_values("data_hora").reset_index(drop=True)

    # --- Media movel 24 h (reducao de ruido) ---
    df["umidade_mm24"] = df["umidade"].rolling(window=24, min_periods=1).mean()
    df["ph_mm24"] = df["ph"].rolling(window=24, min_periods=1).mean()

    # --- Faixa-alvo do milho (apenas diagnostico, nao reescreve dados) ---
    df["ph_fora_faixa_milho"] = ~df["ph"].between(PH_MILHO_MIN, PH_MILHO_MAX)

    (BASE / "data").mkdir(exist_ok=True)
    (BASE / "resultados").mkdir(exist_ok=True)
    (BASE / "graficos").mkdir(exist_ok=True)
    df.to_csv(BASE / "data" / "leituras_tratadas.csv", index=False)

    # --- Indicadores diarios ---
    df["data"] = df["data_hora"].dt.date
    df["acionamento"] = (df["bomba_ligada"].diff() == 1).astype(int)
    diarios = (
        df.groupby("data")
        .agg(
            horas_bomba=("bomba_ligada", "sum"),
            acionamentos=("acionamento", "sum"),
            umidade_media=("umidade", "mean"),
            umidade_min=("umidade", "min"),
            umidade_max=("umidade", "max"),
            ph_medio=("ph", "mean"),
            ph_min=("ph", "min"),
            ph_max=("ph", "max"),
            leituras=("umidade", "count"),
        )
        .reset_index()
    )
    diarios["agua_estimada_l"] = diarios["horas_bomba"] * VAZAO_L_H
    diarios.to_csv(BASE / "resultados" / "indicadores_diarios.csv", index=False)

    # --- Correlacao ---
    corr = df[["umidade", "ph", "nitrogenio", "fosforo", "potassio", "bomba_ligada"]].corr(
        method="pearson"
    )
    corr.to_csv(BASE / "resultados" / "correlacao.csv")

    resumo = (
        f"Linhas brutas: {n_brutas}\n"
        f"Linhas descartadas na limpeza: {descartadas}\n"
        f"Linhas tratadas: {len(df)}\n"
        f"Dias cobertos: {diarios.shape[0]}\n"
        f"Horas de bomba ligada: {int(df['bomba_ligada'].sum())}\n"
        f"Acionamentos: {int(df['acionamento'].sum())}\n"
        f"Agua estimada total (L): {diarios['agua_estimada_l'].sum():.0f}\n"
        f"Umidade media: {df['umidade'].mean():.2f} %\n"
        f"pH medio: {df['ph'].mean():.2f}\n"
        f"Leituras fora da faixa de pH do milho (5,5-6,5): "
        f"{int(df['ph_fora_faixa_milho'].sum())} "
        f"({100 * df['ph_fora_faixa_milho'].mean():.1f}%)\n"
        f"Correlacao com bomba ligada:\n{corr['bomba_ligada'].sort_values().to_string()}\n"
    )
    (BASE / "resultados" / "resumo_tratamento.txt").write_text(resumo, encoding="utf-8")
    print(resumo)

    # --- Graficos ---
    sns.set_theme(style="whitegrid")
    amostra = df.iloc[::6]  # 1 ponto a cada 6 h, para o grafico ficar legivel
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(amostra["data_hora"], amostra["umidade_mm24"], label="Umidade (media movel 24 h)")
    ax.plot(amostra["data_hora"], amostra["ph_mm24"] * 10, label="pH x10 (media movel 24 h)")
    ax.set_title("Evolucao da umidade e do pH no tempo (Fase 3 - milho)")
    ax.set_xlabel("Data"); ax.set_ylabel("Umidade (%) / pH x10")
    ax.legend(); fig.tight_layout()
    fig.savefig(BASE / "graficos" / "umidade_ph_tempo.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(amostra["data_hora"], amostra["umidade"], alpha=0.5, label="Umidade")
    ax2 = ax.twinx()
    ax2.step(amostra["data_hora"], amostra["bomba_ligada"], color="tab:red", label="Bomba ligada")
    ax.set_title("Leituras de umidade e acionamentos da bomba")
    ax.set_xlabel("Data"); ax.set_ylabel("Umidade (%)"); ax2.set_ylabel("Bomba (0/1)")
    ax.legend(loc="upper left"); fig.tight_layout()
    fig.savefig(BASE / "graficos" / "leituras_vs_bomba.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for ax_, col in zip(
        axes.flat, ["umidade", "ph", "nitrogenio", "fosforo", "potassio", "bomba_ligada"]
    ):
        sns.histplot(df[col], kde=True, ax=ax_)
        ax_.set_title(col)
    fig.suptitle("Distribuicao das leituras de cada sensor")
    fig.tight_layout()
    fig.savefig(BASE / "graficos" / "distribuicao_sensores.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    ax.set_title("Mapa de calor: correlacao entre variaveis e acionamento da bomba")
    fig.tight_layout()
    fig.savefig(BASE / "graficos" / "correlacao_heatmap.png", dpi=150); plt.close(fig)
    print("Graficos salvos em graficos/")


if __name__ == "__main__":
    main()
