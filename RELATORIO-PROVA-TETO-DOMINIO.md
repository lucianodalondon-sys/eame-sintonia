# PROVA-TETO-DOMINIO · a verificação independente do teto D38 — 25/09/2026

Branch `prova-teto-v1`, a partir de `7cdb7ea4`. **NÃO instalado.** Não toca no código da ONDA2-G3.

## Em palavras simples

Depois de cada onda, esta prova abre o **livro de corridas** do coletor (onde o próprio transporte
escreve quantos pedidos fez a cada site), junta os sites pelo **domínio** (`www.cia.it`, `cia.it` e
`toscana.cia.it` contam juntos) e soma **a onda inteira**. Se algum domínio passar de 5, reprova.
Na 1.ª onda reprova, como devia: **cia.it = 16** (5 fontes: 3+3+3+3+4). Nenhum outro domínio passou de 5.

## Como se usa (depois do MICRO e da 2.ª onda)

```
py provas/prova_teto_dominio.py --livro data/collection-ledger/italy/runs.ndjson --onda <ficheiro da onda> [--teto 5] [--json saida.json]
```

- `--onda`: qualquer ficheiro que tenha os `RUN_ID` da onda (o relatório do disparador, um log, um JSON).
- Sai com **0 = PASS**, **1 = FAIL** (domínio acima do teto, com os hosts e as corridas que o somaram),
  **2 = NAO_SEI** (uma corrida da onda não está no livro ou não tem `PEDIDOS_POR_HOST` — nunca conta zero).

## Por que é independente

| o que a ONDA2-G3 usa | o que esta prova usa |
|---|---|
| o contador do disjuntor e o livro da onda `SINTONIA_TETO_ONDA` | o **livro de corridas** (`CORTESIA.PEDIDOS_POR_HOST`, escrito pelo transporte) |
| `dominioRegistavel()` em `.mjs` | `dominio_registavel()` próprio, em Python, com a lista de sufixos escrita aqui |
| — | não lê o resumo do condutor (`PEDIDOS_POR_SITE` do BC5) |

A mesma regra (D38: por domínio registável, pela onda inteira), dois medidores.

## Números da 1.ª onda (prova cffaad2d / e18ce992)

`ferramentas/big_collection/BC5-1A-ONDA-LIVRO-DE-CORRIDAS.ndjson` = as 18 linhas das 18 corridas, copiadas
do livro do serviço vivo (cópia lida, o vivo não foi tocado; sha256 do livro vivo no momento da cópia:
`7defc8b3cee56776f5db1df57246c6bc62bc62772c902a3bc2f764b8fec05717`).

```
PROVA_TETO_DOMINIO=FAIL · corridas=18 · pedidos=54 · teto=5 por dominio por onda
  ACIMA DO TETO  cia.it  16
```

## Testes e mutação

- `tests/test_prova_teto_dominio.py`: **11/11** (offline): a 1.ª onda reprova com `cia.it = 16`;
  5 passa e 6 reprova; www/subdomínio somam; `cia.it` ≠ `caf-cia.it`; `arpa.marche.it` ≠
  `regione.marche.it` (sufixo regional); corrida fora do livro ou sem contagem = NAO_SEI; onda vazia = NAO_SEI.
- **Mutação 7/7 mortos** (cópias isoladas): contar por host; host cru; 5 já reprova; corrida em falta
  conta zero; sem sufixo regional; **teto por corrida e não por onda** (o defeito da 1.ª onda); estado
  que ignora o teto.

## Ressalvas

1. **Sem Public Suffix List** (nenhuma na casa, e não se vai buscar à rede): a lista de sufixos de dois
   níveis é escrita à mão (Estado e regiões italianas + alguns estrangeiros). Um sufixo em falta junta
   **mais** do que devia — a prova fica mais exigente, nunca mais branda. As províncias italianas
   (ex.: `bz.it`) não estão na lista: hosts sob elas juntam-se no sufixo (mais exigente).
2. A prova confia na contagem que o **transporte** escreve por host. Se o transporte deixar de contar
   um pedido, a prova não o vê — por isso a pergunta que ela responde é «o livro diz que o teto se
   cumpriu?», não «houve pedidos fora do transporte?».
3. O livro de corridas da 1.ª onda não está no Git (vive na árvore do serviço); as 18 linhas foram
   copiadas para esta branch como prova fixa.
