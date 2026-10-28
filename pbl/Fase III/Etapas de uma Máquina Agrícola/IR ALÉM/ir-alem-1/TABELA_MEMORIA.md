# Tabela comparativa de consumo de memória — Ir Além 1

> **A PREENCHER na máquina do grupo.** Não foi medida neste ambiente
> (sem PlatformIO), por isso nenhum número é apresentado aqui como
> medido. Preencher com os prints de `pio run` e colar os prints
> nesta pasta (ex.: `print_antes.png`, `print_depois.png`).

| Medida (`pio run`) | Antes (Fase 2) | Depois (otimizado) | Diferença |
|---|---|---|---|
| RAM usada | _a preencher_ | _a preencher_ | _a preencher_ |
| RAM total | _a preencher_ | _a preencher_ | _a preencher_ |
| Flash usada | _a preencher_ | _a preencher_ | _a preencher_ |
| Flash total | _a preencher_ | _a preencher_ | _a preencher_ |

## Verificação da lógica

- [ ] Os 7 testes da Fase 2 foram repetidos com o firmware otimizado.
- [ ] As decisões (IRRIGAR / NÃO IRRIGAR) foram as mesmas em todos.
- [ ] A mensagem meteorológica `WEATHER,...` via serial continua
      sendo interpretada com os mesmos valores.
- [ ] Mesma simulação no Wokwi nos dois firmwares, log comparado
      ciclo a ciclo: qualquer divergência invalida a otimização.

## Expectativa honesta

O ganho esperado é PEQUENO (dezenas de bytes, não kilobytes): o ESP32
tem RAM folgada para este firmware, e a maior parte das variáveis
precisa mesmo ser `float`. O valor do Ir Além 1 aqui é a revisão
documentada e a medição, não uma economia espetacular — e é isso que
deve ir para o README e para o vídeo, sem inflar números. Os números
só valem compilados no mesmo ambiente, com a mesma versão de framework
e de bibliotecas.
