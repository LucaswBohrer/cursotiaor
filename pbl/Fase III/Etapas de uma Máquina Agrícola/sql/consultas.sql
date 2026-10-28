-- ============================================================
-- FarmTech Solutions - Fase 3: consultas de gestao
-- Uma consulta para cada informacao da lista do README.
-- Cultura ancora: MILHO (ID_CULTURA = 1).
-- ============================================================

-- 1. Quantidade total de agua aplicada em cada mes
SELECT TO_CHAR(DATA_HORA, 'YYYY-MM') AS MES,
       SUM(AGUA_L) AS AGUA_TOTAL_L,
       SUM(BOMBA_LIGADA) AS HORAS_BOMBA
FROM TB_BOMBA_HISTORICO
WHERE ID_CULTURA = 1
GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')
ORDER BY MES;

-- 2. Variacao do pH do solo ao longo do tempo (media mensal, sensor S2)
SELECT TO_CHAR(DATA_HORA, 'YYYY-MM') AS MES,
       ROUND(AVG(VALOR), 2) AS PH_MEDIO,
       ROUND(MIN(VALOR), 2) AS PH_MINIMO,
       ROUND(MAX(VALOR), 2) AS PH_MAXIMO
FROM TB_LEITURA_SENSOR
WHERE ID_SENSOR = 'S2' AND ID_CULTURA = 1
GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')
ORDER BY MES;

-- 3. Dias com maior tempo de bomba ligada (top 10)
SELECT TRUNC(DATA_HORA) AS DIA,
       SUM(BOMBA_LIGADA) AS HORAS_BOMBA,
       SUM(AGUA_L) AS AGUA_L
FROM TB_BOMBA_HISTORICO
WHERE ID_CULTURA = 1
GROUP BY TRUNC(DATA_HORA)
ORDER BY HORAS_BOMBA DESC
FETCH FIRST 10 ROWS ONLY;

-- 4. Culturas com maior consumo de insumos (tabela de manejo)
SELECT C.NOME AS CULTURA,
       M.INSUMO,
       SUM(M.QUANTIDADE_INSUMO) AS TOTAL_INSUMO,
       MAX(M.UNIDADE_INSUMO) AS UNIDADE
FROM TB_MANEJO M
JOIN TB_CULTURA C ON C.ID_CULTURA = M.ID_CULTURA
GROUP BY C.NOME, M.INSUMO
ORDER BY TOTAL_INSUMO DESC;

-- 5. Umidade media por mes e leituras fora da faixa operacional (sensor S1)
--    Faixa operacional herdada da Fase 2: 60-70 %. Abaixo de 60 %
--    o solo esta na zona em que a logica passa a pontuar irrigacao.
SELECT TO_CHAR(DATA_HORA, 'YYYY-MM') AS MES,
       ROUND(AVG(VALOR), 2) AS UMIDADE_MEDIA,
       SUM(CASE WHEN VALOR < 60 THEN 1 ELSE 0 END) AS LEITURAS_ABAIXO_60
FROM TB_LEITURA_SENSOR
WHERE ID_SENSOR = 'S1' AND ID_CULTURA = 1
GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')
ORDER BY MES;

-- 6. Leituras de pH fora da faixa ideal do milho (5,5-6,5), por mes
SELECT TO_CHAR(DATA_HORA, 'YYYY-MM') AS MES,
       COUNT(*) AS LEITURAS_FORA_FAIXA,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS PERCENTUAL_DO_TOTAL
FROM TB_LEITURA_SENSOR
WHERE ID_SENSOR = 'S2' AND ID_CULTURA = 1
  AND (VALOR < 5.5 OR VALOR > 6.5)
GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')
ORDER BY MES;
