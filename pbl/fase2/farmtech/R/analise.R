# FarmTech Solutions - Analise dos logs
# Fase 2


# ---------------------------------------------------------
# 1. Localizar os arquivos de log
# ---------------------------------------------------------

arquivos_log <- list.files(
  path = "logs",
  pattern = "\\.txt$",
  full.names = TRUE
)

cat("Logs encontrados:", length(arquivos_log), "\n\n")


# ---------------------------------------------------------
# 2. Funcao para extrair numeros
# ---------------------------------------------------------

extrair_numero <- function(linhas, padrao) {

  linha <- linhas[grepl(padrao, linhas)]

  if (length(linha) == 0) {
    return(NA)
  }

  valor <- sub(
    ".*: ([0-9.]+).*",
    "\\1",
    linha[1]
  )

  return(as.numeric(valor))
}


# ---------------------------------------------------------
# 3. Funcao para analisar um log
# ---------------------------------------------------------

analisar_log <- function(arquivo) {

  linhas <- readLines(
    arquivo,
    warn = FALSE
  )


  # -------------------------------------------------------
  # Data e hora
  # -------------------------------------------------------

  data_hora <- sub(
    "Data/hora da captura: ",
    "",
    linhas[
      grepl(
        "Data/hora da captura:",
        linhas
      )
    ][1]
  )


  # -------------------------------------------------------
  # Umidade
  # -------------------------------------------------------

  umidade <- extrair_numero(
    linhas,
    "Umidade simulada:"
  )


  # -------------------------------------------------------
  # pH
  # -------------------------------------------------------

  ph <- extrair_numero(
    linhas,
    "pH simulado:"
  )


  # -------------------------------------------------------
  # Pontuacao multicriterio
  # -------------------------------------------------------

  pontuacao <- extrair_numero(
    linhas,
    "^Pontuacao:"
  )

    # -------------------------------------------------------
  # Status da bomba
  # -------------------------------------------------------

  linha_bomba <- linhas[
    grepl(
      "^Bomba:",
      linhas
    )
  ]

  if (length(linha_bomba) > 0) {

    bomba <- sub(
      "^Bomba: ",
      "",
      linha_bomba[1]
    )

  } else {

    bomba <- NA

  }

  # -------------------------------------------------------
# Decisao de irrigacao
# -------------------------------------------------------

linha_decisao <- linhas[
  grepl(
    "^DECISAO:",
    linhas
  )
]

if (length(linha_decisao) > 0) {

  decisao <- sub(
    "^DECISAO: ",
    "",
    linha_decisao[1]
  )

} else {

  decisao <- NA

}

# -------------------------------------------------------
# Motivo da decisao
# -------------------------------------------------------

linha_motivo <- linhas[
  grepl(
    "^Motivo:",
    linhas
  )
]

if (length(linha_motivo) > 0) {

  motivo <- sub(
    "^Motivo: ",
    "",
    linha_motivo[1]
  )

} else {

  motivo <- NA

}


  # -------------------------------------------------------
  # Nitrogenio (N)
  # -------------------------------------------------------

  nivel_n <- extrair_numero(
    linhas,
    "Nitrogenio \\(N\\):"
  )

  linha_n <- linhas[
    grepl(
      "Nitrogenio \\(N\\):",
      linhas
    )
  ]

  status_n <- ifelse(
    grepl("ATIVO", linha_n),
    "ATIVO",
    "INATIVO"
  )


  # -------------------------------------------------------
  # Fosforo (P)
  # -------------------------------------------------------

  nivel_p <- extrair_numero(
    linhas,
    "Fosforo \\(P\\):"
  )

  linha_p <- linhas[
    grepl(
      "Fosforo \\(P\\):",
      linhas
    )
  ]

  status_p <- ifelse(
    grepl("ATIVO", linha_p),
    "ATIVO",
    "INATIVO"
  )


  # -------------------------------------------------------
  # Potassio (K)
  # -------------------------------------------------------

  nivel_k <- extrair_numero(
    linhas,
    "Potassio \\(K\\):"
  )

  linha_k <- linhas[
    grepl(
      "Potassio \\(K\\):",
      linhas
    )
  ]

  status_k <- ifelse(
    grepl("ATIVO", linha_k),
    "ATIVO",
    "INATIVO"
  )


  # -------------------------------------------------------
  # Retornar dados estruturados
  # -------------------------------------------------------

  return(
    data.frame(

      arquivo = basename(arquivo),

      bomba = bomba,

      data_hora = data_hora,

      umidade = umidade,

      ph = ph,

      pontuacao = pontuacao,

      decisao = decisao,

      motivo = motivo,

      nivel_n = nivel_n,
      status_n = status_n,

      nivel_p = nivel_p,
      status_p = status_p,

      nivel_k = nivel_k,
      status_k = status_k

    )
  )
}


# ---------------------------------------------------------
# 4. Analisar todos os logs
# ---------------------------------------------------------

dados <- do.call(
  rbind,
  lapply(
    arquivos_log,
    analisar_log
  )
)

dados$data_hora <- as.POSIXct(
  dados$data_hora,
  format = "%d/%m/%Y %H:%M:%S"
)

# ---------------------------------------------------------
# 5. Mostrar tabela completa
# ---------------------------------------------------------

cat(
  "========== DADOS EXTRAIDOS ==========\n\n"
)

print(dados)

# ---------------------------------------------------------
# 6. Resumo dos motivos das decisoes
# ---------------------------------------------------------

cat("\n========== RESUMO DOS MOTIVOS ==========\n\n")

print(
  table(
    dados$motivo,
    useNA = "ifany"
  )
)

# ---------------------------------------------------------
# 7. Estatisticas gerais
# ---------------------------------------------------------

cat("\n========== ESTATISTICAS GERAIS ==========\n\n")

cat(
  "Umidade media:",
  round(mean(dados$umidade, na.rm = TRUE), 2),
  "%\n"
)

cat(
  "pH medio:",
  round(mean(dados$ph, na.rm = TRUE), 2),
  "\n"
)

cat(
  "Pontuacao media:",
  round(mean(dados$pontuacao, na.rm = TRUE), 2),
  "\n"
)

cat(
  "Nivel medio de N:",
  round(mean(dados$nivel_n, na.rm = TRUE), 2),
  "\n"
)

cat(
  "Nivel medio de P:",
  round(mean(dados$nivel_p, na.rm = TRUE), 2),
  "\n"
)

cat(
  "Nivel medio de K:",
  round(mean(dados$nivel_k, na.rm = TRUE), 2),
  "\n"
)

# ---------------------------------------------------------
# 8. Analise das decisoes
# ---------------------------------------------------------

cat("\n========== ANALISE DAS DECISOES ==========\n\n")

cat(
  "Total de registros:",
  nrow(dados),
  "\n"
)

cat(
  "Registros com irrigacao:",
  sum(dados$decisao == "IRRIGAR", na.rm = TRUE),
  "\n"
)

cat(
  "Registros sem irrigacao:",
  sum(dados$decisao == "NAO IRRIGAR", na.rm = TRUE),
  "\n"
)

cat(
  "Percentual sem irrigacao:",
  round(
    mean(dados$decisao == "NAO IRRIGAR", na.rm = TRUE) * 100,
    2
  ),
  "%\n"
)

cat("\nDistribuicao das decisoes:\n\n")

print(
  table(
    dados$decisao,
    useNA = "ifany"
  )
)

# ---------------------------------------------------------
# 9. Grafico dos motivos das decisoes
# ---------------------------------------------------------

library(ggplot2)

motivos <- as.data.frame(
  table(
    dados$motivo,
    useNA = "ifany"
  ),
  stringsAsFactors = FALSE
)

colnames(motivos) <- c(
  "motivo",
  "quantidade"
)

motivos$motivo <- as.character(
  motivos$motivo
)

motivos$motivo[
  is.na(motivos$motivo)
] <- "Sem motivo registrado"


grafico_motivos <- ggplot(
  motivos,
  aes(
    x = reorder(motivo, quantidade),
    y = quantidade
  )
) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Motivos das decisões de irrigação",
    x = "Motivo",
    y = "Quantidade de registros"
  ) +
  theme_minimal()

print(grafico_motivos)

# ============================================================
# ANALISE TEMPORAL DA IRRIGACAO
# ============================================================

cat("\n========== ANALISE TEMPORAL DA IRRIGACAO ==========\n\n")

# Registros em que a bomba esteve ativa
registros_bomba <- dados[dados$bomba == "ATIVA", ]

cat("Registros com bomba ativa:", nrow(registros_bomba), "\n")

if (nrow(registros_bomba) > 0) {

  cat(
    "Primeiro registro com bomba ativa:",
    format(
      min(registros_bomba$data_hora, na.rm = TRUE),
      "%d/%m/%Y %H:%M:%S"
    ),
    "\n"
  )

  cat(
    "Ultimo registro com bomba ativa:",
    format(
      max(registros_bomba$data_hora, na.rm = TRUE),
      "%d/%m/%Y %H:%M:%S"
    ),
    "\n"
  )

  cat("\n")

  cat(
    "Umidade simulada inicial:",
    min(registros_bomba$umidade, na.rm = TRUE),
    "%\n"
  )

  cat(
    "Umidade simulada final:",
    max(registros_bomba$umidade, na.rm = TRUE),
    "%\n"
  )

  cat(
    "pH minimo:",
    min(registros_bomba$ph, na.rm = TRUE),
    "\n"
  )

  cat(
    "pH maximo:",
    max(registros_bomba$ph, na.rm = TRUE),
    "\n"
  )

} else {

  cat("Nenhum registro com bomba ativa foi encontrado.\n")

}

# ============================================================
# 10. CICLO OBSERVADO DE IRRIGACAO
# ============================================================

cat("\n========== CICLO OBSERVADO DE IRRIGACAO ==========\n\n")

# Ordenar cronologicamente
dados <- dados[
  order(dados$data_hora),
]

# Localizar o primeiro registro com bomba ativa
inicio_irrigacao <- which(
  dados$bomba == "ATIVA"
)[1]

if (!is.na(inicio_irrigacao)) {

  # Localizar o primeiro registro INATIVO depois do inicio
  fim_candidatos <- which(
    seq_len(nrow(dados)) > inicio_irrigacao &
    dados$bomba == "INATIVA"
  )

  if (length(fim_candidatos) > 0) {

    fim_irrigacao <- fim_candidatos[1]

    inicio <- dados[inicio_irrigacao, ]
    fim <- dados[fim_irrigacao, ]

    duracao_segundos <- as.numeric(
      difftime(
        fim$data_hora,
        inicio$data_hora,
        units = "secs"
      )
    )

    variacao_umidade <- fim$umidade - inicio$umidade
    variacao_ph <- fim$ph - inicio$ph

    cat(
      "Inicio observado:",
      format(
        inicio$data_hora,
        "%d/%m/%Y %H:%M:%S"
      ),
      "\n"
    )

    cat(
      "Fim observado:",
      format(
        fim$data_hora,
        "%d/%m/%Y %H:%M:%S"
      ),
      "\n"
    )

    cat(
      "Janela observada:",
      duracao_segundos,
      "segundos\n"
    )

    cat(
      "Umidade:",
      inicio$umidade,
      "% ->",
      fim$umidade,
      "% | Variacao:",
      round(variacao_umidade, 2),
      "p.p.\n"
    )

    cat(
      "pH:",
      inicio$ph,
      "->",
      fim$ph,
      "| Variacao:",
      round(variacao_ph, 2),
      "\n"
    )

    cat(
      "N:",
      inicio$nivel_n,
      "->",
      fim$nivel_n,
      "%\n"
    )

    cat(
      "P:",
      inicio$nivel_p,
      "->",
      fim$nivel_p,
      "%\n"
    )

    cat(
      "K:",
      inicio$nivel_k,
      "->",
      fim$nivel_k,
      "%\n"
    )

    cat(
      "Pontuacao:",
      inicio$pontuacao,
      "->",
      fim$pontuacao,
      "\n"
    )

    cat(
      "Decisao final:",
      fim$decisao,
      "\n"
    )

  } else {

    cat(
      "O ciclo de irrigacao ainda nao possui um registro posterior com bomba inativa.\n"
    )

  }

} else {

  cat(
    "Nenhum ciclo de irrigacao foi encontrado.\n"
  )

}