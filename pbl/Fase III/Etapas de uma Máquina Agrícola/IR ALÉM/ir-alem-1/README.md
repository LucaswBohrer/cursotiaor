# Ir Além 1 — ESP32 eficiente: tipos de variáveis e otimização de memória

## Objetivo

Revisar o firmware da Fase 2 com o olhar de quem conhece a representação
dos dados no microcontrolador: usar o tipo mais enxuto que representa
cada dado com segurança, sem alterar o comportamento do sistema.

## O que foi feito (nesta pasta, só na Fase 3)

Arquivo `main_otimizado.cpp`, gerado a partir do `main.cpp` da Fase 2
(a pasta da Fase 2 permanece intacta) com exatamente estas mudanças,
todas comentadas no código:

| # | Antes | Depois | Justificativa |
|---|---|---|---|
| 1 | Níveis N/P/K: `float` (4 bytes cada) | `uint8_t` (1 byte cada) | Valores inteiros 0–100, incrementos inteiros, meta 70. A função de exibição continua recebendo `float` e imprimindo "70.0" por conversão implícita. Economia: 9 bytes de RAM estática. |
| 2 | Pontuação: `int` (4 bytes) | `uint8_t` (1 byte) | Máximo teórico 4 (umidade) + 3 (pH) + 3 (nutrientes) = 10. Economia: 3 bytes + 3 bytes na variável local. |
| 3 | LDR: `int` (4 bytes) | `uint16_t` (2 bytes) | ADC do ESP32: 0–4095, cabe em 16 bits. Economia: 2 bytes. |
| 4 | Status meteorológico: `String` | `char[32]` fixo | Elimina alocação heap e fragmentação; status do Python têm < 32 caracteres, com truncamento garantido. |
| 5 | Parser meteorológico: `String` + `indexOf`/`substring`/`toFloat` | Buffer `char[160]` + `strstr`/`strtof` | Elimina todas as alocações heap no caminho serial. Mensagem do Python tem < 90 caracteres. Mesmo formato, mesma validação, mesmos valores impressos. |

## O que foi avaliado e NÃO aplicado (com motivo)

- **Umidade, pH, temperatura e chuvas:** mantidos em `float`. Os valores
  têm parte fracionária (sensor, 2 casas), e `float` já é o menor tipo
  de ponto flutuante no ESP32 (`double` seria pior).
- **Flags `bool` em bitfield:** economizaria só 4 bytes no total e
  pioraria a leitura; `bool` já ocupa 1 byte cada.

## O que NÃO mudou

- **Lógica de decisão:** idêntica à Fase 2, incluindo o comportamento
  de inicializar o ambiente simulado só na primeira leitura. A
  correção para leituras ao vivo do DHT22/LDR é uma proposta separada
  (`docs/correcao_leitura_ao_vivo.md`) e **não** está neste arquivo —
  de propósito, para a medição de memória comparar exatamente a mesma
  lógica antes e depois.

## Como medir (na máquina do grupo — sem PlatformIO neste ambiente)

```bash
# Antes (Fase 2, pasta original):
pio run
# Depois (copiar este arquivo para src/main.cpp de uma cópia do projeto):
pio run
```

Copiar as duas saídas de `RAM` e `Flash` para `TABELA_MEMORIA.md`
nesta pasta, junto com os prints. Depois, rodar os 7 testes da Fase 2
e confirmar que as decisões são as mesmas.

## Integrantes

Gabriel Kuwamoto (RM567125), Guilherme Rodrigues (RM574372),
João Rolnik Souza (RM576079), Lucas Welter Bohrer (RM576902).
