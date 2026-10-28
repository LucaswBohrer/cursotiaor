# Correção proposta: leituras ao vivo do DHT22 e do LDR

> Documento de proposta, **somente na Fase 3**. Por decisão do grupo
> (28/10/2026), **nada foi alterado na pasta da Fase 2**, que permanece
> intacta como entrega encerrada. Este documento não altera nenhum
> arquivo da Fase 2.

## Problema confirmado na Fase 2

Em `src/main.cpp` da Fase 2, `umidadeSimulada` e `phSimulado` só são
inicializados na primeira leitura (`ambienteInicializado`). A função
`calcularPontuacao()` usa esses valores simulados, não a leitura
corrente. Consequência: mexer nos controles do DHT22/LDR no Wokwi
depois do início não muda a decisão — só o efeito da irrigação mexe
nesses valores.

## Correção proposta (para o próximo firmware, não aplicada aqui)

1. A cada ciclo, ler DHT22 e LDR normalmente (isso o loop já faz).
2. Quando a bomba está **desligada**, a pontuação passa a usar a
   leitura corrente: `umidadeSensor` e `calcularPH(valorLDR)`.
   Mexer no sensor muda a decisão na hora.
3. Quando a bomba está **ligada**, manter o efeito simulado da
   irrigação (umidade sobe, pH caminha para 6,25, nutrientes sobem),
   aplicado sobre a leitura corrente — para não perder o
   comportamento da simulação que a Fase 2 já validou.
4. Manter o travamento por nutrientes (bomba só com nutriente ativo
   e ≥ 3 pontos) e o bloqueio por chuva relevante prevista
   (OpenWeather via serial), inalterados.

## O que validar quando for aplicada

- Com a bomba desligada, variar o DHT22 no Wokwi e observar a
  pontuação/decisão mudar no ciclo seguinte.
- Repetir os 7 testes da Fase 2 e confirmar que a lógica de decisão
  continua a mesma quando os sensores não são mexidos.
- Registrar o novo `main.cpp` versionado na pasta da fase em que a
  correção for de fato aplicada — nunca retroativamente na Fase 2.
