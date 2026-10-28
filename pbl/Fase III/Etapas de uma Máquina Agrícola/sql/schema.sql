-- ============================================================
-- FarmTech Solutions - Fase 3
-- Schema Oracle (testado como sintaxe Oracle; a execucao real
-- depende do ambiente documentado no README - Docker
-- gvenzl/oracle-free ou Oracle Cloud Free Tier).
-- Nenhuma senha esta neste arquivo. Use variaveis de ambiente
-- na carga (ver src/carga_oracle.py).
-- ============================================================

-- Limpeza idempotente (ordem inversa das dependencias)
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE TB_BOMBA_HISTORICO CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE TB_LEITURA_SENSOR CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE TB_MANEJO CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE TB_CULTURA CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

-- Cultura: a ancora da Fase 3 e o MILHO.
CREATE TABLE TB_CULTURA (
  ID_CULTURA      NUMBER(10)     PRIMARY KEY,
  NOME            VARCHAR2(100) NOT NULL,
  NOME_CIENTIFICO VARCHAR2(100),
  AREA_HA         NUMBER(10,2),
  PH_IDEAL_MIN    NUMBER(4,2),
  PH_IDEAL_MAX    NUMBER(4,2),
  OBSERVACAO      VARCHAR2(400)
);

-- Manejo e culturas trazidos das Fases 1 e 2 (tabela de trabalho
-- da Fase 3; ver data/dados_manejo_culturas.json e o aviso la).
CREATE TABLE TB_MANEJO (
  ID_MANEJO          NUMBER(10)     PRIMARY KEY,
  ID_CULTURA         NUMBER(10)     NOT NULL REFERENCES TB_CULTURA(ID_CULTURA),
  DATA_MANEJO        DATE           NOT NULL,
  ATIVIDADE          VARCHAR2(200)  NOT NULL,
  INSUMO             VARCHAR2(100),
  QUANTIDADE_INSUMO  NUMBER(12,2),
  UNIDADE_INSUMO     VARCHAR2(20)
);

-- Leituras dos sensores S1 (umidade), S2 (pH) e S3 (nutrientes).
-- DATA_HORA + ID_SENSOR formam a chave primaria: e isso que
-- torna a carga repetivel sem duplicar (MERGE na carga).
CREATE TABLE TB_LEITURA_SENSOR (
  DATA_HORA      TIMESTAMP       NOT NULL,
  ID_SENSOR      VARCHAR2(10)     NOT NULL,
  ID_CULTURA     NUMBER(10)       REFERENCES TB_CULTURA(ID_CULTURA),
  VALOR          NUMBER(10,2),
  UNIDADE        VARCHAR2(20),
  ORIGEM         VARCHAR2(20)     DEFAULT 'simulada',
  PRIMARY KEY (DATA_HORA, ID_SENSOR)
);

-- Historico de acionamento da bomba: 1 linha por ciclo/hora.
-- AGUA_L = horas * 120 L/h (vazao definida pelo grupo).
CREATE TABLE TB_BOMBA_HISTORICO (
  DATA_HORA      TIMESTAMP       PRIMARY KEY,
  ID_CULTURA     NUMBER(10)       REFERENCES TB_CULTURA(ID_CULTURA),
  BOMBA_LIGADA   NUMBER(1)        NOT NULL CHECK (BOMBA_LIGADA IN (0, 1)),
  AGUA_L         NUMBER(12,2)     NOT NULL,
  ORIGEM         VARCHAR2(20)     DEFAULT 'simulada'
);

COMMIT;
