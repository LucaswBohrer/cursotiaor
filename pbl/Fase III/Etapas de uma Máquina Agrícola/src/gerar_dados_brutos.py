#!/usr/bin/env python3
"""
Fase 3 - FarmTech Solutions: geracao do CSV bruto.

O que este script faz (e o que ele NAO faz):
  1. LE (nunca escreve) os 32 logs da Fase 2 em
     pbl/Fase II/Um mapa do tesouro/logs/*.txt e extrai as leituras
     reais do Monitor Serial (umidade simulada, pH simulado, N, P, K,
     estado da bomba). Essas linhas saem com origem = "real".
  2. Gera uma serie horaria simulada a partir do padrao dessas
     leituras reais, com a mesma logica de decisao da Fase 2
     (pontuacao multicriterio, bomba so com nutriente ativo e
     >= 3 pontos, bloqueio por chuva relevante prevista).
     Essas linhas saem com origem = "simulada", exatamente como o
     enunciado da Fase 3 permite quando o volume real nao basta.
  3. Injeta ~1% de leituras invalidas (fora da faixa fisica ou
     ausentes) na serie simulada, para que o tratamento da Fase 3
     tenha o que limpar. Elas sao marcadas, nao escondidas.

Premissas documentadas (ver README):
  - Cultura ancora da Fase 3: MILHO (decisao do grupo em 28/10/2026).
  - Cada ciclo simulado vale 1 hora (relogio simulado da Fase 2).
  - Serie simulada: 90 dias corridos, 2026-09-29 a 2026-12-27,
    comecando do ultimo estado real (28/09/2026).
  - Vazao da bomba definida pelo grupo: 120 L/h. Um ciclo com a
    bomba ligada = 1 h = 120 L aplicados. E um parametro de
    simulacao, nao uma medicao de campo.
  - Faixas fisicas para limpeza: umidade 0-100 %, pH 0-14,
    nutrientes 0-100 %. Valores fora disso sao invalidos.
  - Os niveis N/P/K sao a escala simulada (%) herdada da Fase 2,
    nao teores de laboratorio (mg/dm3 ou kg/ha).

Uso:
    python3 src/gerar_dados_brutos.py
Saida:
    data/leituras_brutas.csv
    data/leituras_reais_fase2.csv  (so as 32 linhas reais, para auditoria)
"""
from __future__ import annotations

import glob
import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
FASE2_LOGS = (
    Path.home()
    / "workspace/cursotiaor/pbl/Fase II/Um mapa do tesouro/logs"
)
# Caminho relativo ao repo, para rodar tambem no Windows do Lucas:
# se a pasta acima nao existir, tenta o caminho relativo do repo.
if not FASE2_LOGS.exists():
    FASE2_LOGS = BASE.parent / "Fase II" / "Um mapa do tesouro" / "logs"

VAZAO_L_H = 120.0
SEED = 42


def extrair_reais() -> pd.DataFrame:
    """Extrai as leituras reais dos logs da Fase 2 (somente leitura)."""
    padroes = {
        "umidade": re.compile(r"Umidade simulada: ([\d.]+)"),
        "ph": re.compile(r"pH simulado: ([\d.]+)"),
        "nitrogenio": re.compile(r"Nitrogenio \(N\): \w+ \| Nivel: ([\d.]+)"),
        "fosforo": re.compile(r"Fosforo \(P\): \w+ \| Nivel: ([\d.]+)"),
        "potassio": re.compile(r"Potassio \(K\): \w+ \| Nivel: ([\d.]+)"),
        "bomba": re.compile(r"Bomba: (\w+)"),
        "captura": re.compile(r"Data/hora da captura: (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})"),
    }
    linhas = []
    for arquivo in sorted(glob.glob(str(FASE2_LOGS / "*.txt"))):
        texto = Path(arquivo).read_text(errors="ignore")
        valores = {}
        for chave, padrao in padroes.items():
            m = padrao.search(texto)
            valores[chave] = m.group(1) if m else None
        if valores["captura"] is None:
            continue
        linhas.append(
            {
                "data_hora": datetime.strptime(valores["captura"], "%d/%m/%Y %H:%M:%S"),
                "umidade": float(valores["umidade"]),
                "ph": float(valores["ph"]),
                "nitrogenio": float(valores["nitrogenio"]),
                "fosforo": float(valores["fosforo"]),
                "potassio": float(valores["potassio"]),
                "bomba_ligada": 1 if valores["bomba"] == "ATIVA" else 0,
                "origem": "real",
            }
        )
    df = pd.DataFrame(linhas).sort_values("data_hora").reset_index(drop=True)
    return df


def pontuacao_fase2(umidade: float, ph: float, ativos: list[bool]) -> int:
    """Pontuacao multicriterio exatamente como na Fase 2."""
    pontos = 0
    if umidade < 40:
        pontos += 4
    elif umidade < 60:
        pontos += 2
    if ph < 4 or ph > 8:
        pontos += 3
    elif ph < 5.5 or ph > 7.0:
        pontos += 2
    pontos += sum(1 for a in ativos if a)
    return pontos


def gerar_simuladas(inicio_estado: dict, dias: int = 90) -> pd.DataFrame:
    """Serie horaria simulada a partir do padrao das leituras reais."""
    rng = random.Random(SEED)
    umidade, ph = inicio_estado["umidade"], inicio_estado["ph"]
    n, p, k = (
        inicio_estado["nitrogenio"],
        inicio_estado["fosforo"],
        inicio_estado["potassio"],
    )
    linhas = []
    inicio = datetime(2026, 9, 29, 0, 0)
    # Dia de chuva prevista (bloqueia a bomba): ~8% dos dias, deterministico.
    dias_chuva = {d for d in range(dias) if rng.random() < 0.08}
    for hora in range(dias * 24):
        data_hora = inicio + timedelta(hours=hora)
        dia = hora // 24
        chuva_prevista = dia in dias_chuva
        ativos = [n < 70, p < 70, k < 70]
        pontos = pontuacao_fase2(umidade, ph, ativos)
        bomba = 1 if (any(ativos) and pontos >= 3 and not chuva_prevista) else 0
        if bomba:
            # Irrigacao: umidade sobe, pH caminha para 6,25, nutrientes sobem.
            umidade = min(95.0, umidade + rng.uniform(2.0, 5.0))
            ph += (6.25 - ph) * rng.uniform(0.05, 0.12)
            n = min(85.0, n + rng.uniform(1.5, 3.5))
            p = min(85.0, p + rng.uniform(1.5, 3.5))
            k = min(85.0, k + rng.uniform(1.5, 3.5))
        else:
            # Sem irrigacao: solo seca, pH deriva, nutrientes caem devagar.
            umidade = max(25.0, umidade - rng.uniform(0.5, 2.0))
            ph = min(8.5, max(3.0, ph + rng.uniform(-0.08, 0.08)))
            n = max(20.0, n - rng.uniform(0.2, 0.8))
            p = max(20.0, p - rng.uniform(0.2, 0.8))
            k = max(20.0, k - rng.uniform(0.2, 0.8))
        # Ruido de sensor em torno do estado verdadeiro.
        linhas.append(
            {
                "data_hora": data_hora,
                "umidade": round(umidade + rng.gauss(0, 1.5), 2),
                "ph": round(ph + rng.gauss(0, 0.08), 2),
                "nitrogenio": round(n + rng.gauss(0, 0.5), 1),
                "fosforo": round(p + rng.gauss(0, 0.5), 1),
                "potassio": round(k + rng.gauss(0, 0.5), 1),
                "bomba_ligada": bomba,
                "origem": "simulada",
            }
        )
    df = pd.DataFrame(linhas)
    # ~1% de leituras invalidas, para exercitar a limpeza (documentado).
    n_invalidas = max(1, len(df) // 100)
    idx = rng.sample(range(len(df)), n_invalidas)
    for i, pos in enumerate(idx):
        coluna = ["umidade", "ph", "fosforo"][i % 3]
        if coluna == "umidade":
            df.loc[pos, "umidade"] = 999.0
        elif coluna == "ph":
            df.loc[pos, "ph"] = 15.0
        else:
            df.loc[pos, "fosforo"] = None
    return df


def main() -> None:
    reais = extrair_reais()
    print(f"Leituras reais extraidas da Fase 2: {len(reais)}")
    ultimo = reais.iloc[-1].to_dict()
    simuladas = gerar_simuladas(ultimo)
    print(f"Linhas simuladas geradas: {len(simuladas)}")
    brutas = pd.concat([reais, simuladas], ignore_index=True).sort_values(
        "data_hora"
    )
    # Colunas do enunciado primeiro; nitrogenio e origem sao extras
    # explicitos (a Fase 2 tem N, P e K; o enunciado da Fase 3 lista
    # P e K nos sensores, mas esconder o N seria perder dado real).
    brutas = brutas[
        [
            "data_hora",
            "umidade",
            "ph",
            "nitrogenio",
            "fosforo",
            "potassio",
            "bomba_ligada",
            "origem",
        ]
    ]
    (BASE / "data").mkdir(exist_ok=True)
    reais.to_csv(BASE / "data" / "leituras_reais_fase2.csv", index=False)
    brutas.to_csv(BASE / "data" / "leituras_brutas.csv", index=False)
    print(f"Total no CSV bruto: {len(brutas)} linhas")
    print(f"Periodo: {brutas['data_hora'].min()} a {brutas['data_hora'].max()}")
    print(f"Bomba ligada: {int(brutas['bomba_ligada'].sum())} ciclos")


if __name__ == "__main__":
    main()
