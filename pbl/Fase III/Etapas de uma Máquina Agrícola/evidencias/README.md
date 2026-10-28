# Evidências — Oracle (a capturar na máquina do grupo)

Esta pasta está vazia de propósito: neste ambiente não há Oracle
(sem Docker) e não há credencial de nuvem, então nenhum print aqui
foi forjado como saída do banco.

Depois de rodar `sql/schema.sql` e `src/carga_oracle.py` no ambiente
documentado no README, salvar aqui:

1. Print da criação das tabelas (ex.: `SELECT table_name FROM user_tables;`).
2. Print da carga — contagem por tabela, antes e depois de rodar a
   carga duas vezes (prova de que o MERGE não duplica).
3. Print de cada consulta de `sql/consultas.sql` com resultado.

Os números de referência, calculados em Pandas sobre o mesmo CSV
tratado, estão em `resultados/resultados_consultas_preview.csv` —
são um preview, não a evidência do Oracle, e devem ser substituídos
pelos prints reais nesta pasta.
