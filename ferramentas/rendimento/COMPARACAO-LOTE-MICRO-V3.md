# MICRO-V3: previsão × resultado, fonte a fonte

- **Lote:** `LOTE-MICRO-V3.json`, sha256 `cd5d3b79…93f7`. Previsões escritas **antes** da corrida.
- **Corrida:** `MICRO-V3-20260925-0803`, das 08:03 às 08:08.
- **Como se mediu:** `ferramentas/rendimento/comparar_lote_micro.py`, só leitura, sobre cópias tiradas às
  08:17. Os sha256 das cópias estão em `COMPARACAO-LOTE-MICRO-V3-INSUMOS.txt`. Nenhum SELECT foi
  necessário: o livro de corridas e o livro de decisões chegam. O vivo e a Sala não foram tocados.

**Resultado D35: 2 SIM ÷ 6 fontes que correram = 33,3 % → PASSA** (> 16,7 % e ≥ 2 SIM).
**Os 2 SIM são da myfruit.** Clima T2 = **NÃO PROVADO** (D47).

| Fonte | Docs previstos → reais | SIM previstos → reais | NÃO / NÃO SEI | Pedidos (teto 5) |
|---|---|---|---|---|
| IT-T10-018 myfruit | 3 → **3** | 3 → **2** | 0 / 1 | 5 |
| IT-T2-034 ARPA Marche | 3 → **3** | NÃO SEI → 0 | **3** / 0 | 5 |
| IT-T2-051 ARPAE | 3 → **3** | NÃO SEI → 0 | 1 / **2** (quarentena capa/matéria) | 5 |
| IT-T10-021 Plantgest | 3 → **3** | NÃO SEI → 0 | 2 / 1 | 5 |
| IT-T7-017 Riunite | 3 → **3** | NÃO SEI → 0 | 2 / 1 | 5 |
| IT-T7-021 Villoresi | 3 → **1** | 0 → **0** | 0 / 1 | 5, e **2 alvos cortados por TETO_DOMINIO** |
| **Total** | **18 → 16** | **3 (só as fontes com histórico) → 2** | **8 / 6** | 30 |

## O que a previsão acertou

- **Documentos:** 5 de 6 exatos (3 = 3). A escolha D40 («1.º alvo não coletado + até 3 novos») trouxe
  o que a medição dizia.
- **O PASS e de onde ele vinha:** a previsão dizia que o ≥ 2 SIM assentava na myfruit, e foi isso.
- **As ARPA não dariam janela:** a nota QUATRO-CHAVES/D47 dizia «notícias gerais, não boletim». A
  Admissão julgou as 3 da ARPA Marche **NÃO** com prova de outro universo (revista, publicação,
  congresso, universidade, ministério).
- **Villoresi 0 SIM** (previsto 0,0).

## O que errou, e porquê

1. **myfruit: 2 SIM em vez de 3.** A previsão usou a taxa da 1.ª onda (3/3). A 3.ª matéria só tinha uma
   palavra de T10 («prezzi») e ficou NÃO SEI («indício, não sinal»). **A taxa de 100 % vinha de 3
   documentos só**: era uma amostra pequena.
2. **Villoresi: 1 documento em vez de 3.** A fonte gastou os 5 pedidos antes das matérias: robots,
   índice e o salto `www.etvilloresi.it` → `etvilloresi.it`, que já tinha custado pedidos na A5. Os
   outros 2 alvos foram cortados com `TETO_DOMINIO`, **o teto D38 a funcionar**. A previsão
   («min(alvos D40, 3)») não contou os pedidos gastos em saltos. **Correção para a próxima previsão:**
   contar os saltos da entrada, medidos na última corrida.
3. **Plantgest: 0 SIM, com 2 NÃO.** As 3 matérias são **técnicas agronómicas**: geada e antigeada,
   agrivoltaico em vinha, pessegueiro. A régua de **T10 (mercado)** julgou-as «de outro universo»
   (T5, T7, T9, T3). **A fonte está no universo errado para o que publica.** Isto não é culpa da régua:
   uma Plantgest julgada como T3/T5 (técnica) ou T1 (janela) teria outra resposta. É um achado de
   **catálogo** (o UNIVERSO da fonte), não de coleta.
4. **ARPAE: 2 NÃO SEI por quarentena (D11)**, porque o detector não soube se era matéria ou página de
   entrada. A previsão NÃO SEI não distinguia «julgado NÃO SEI» de «em quarentena».

## Para quem decide

- O PASS mede o **sistema instalado**: 16 documentos, 6 de 6 SUCCESS, teto a cortar certo. Mas o SIM
  continua a ser **da myfruit e só dela**.
- Três alavancas, **medidas e não suposições:**
  - contrato das ARPA para o **boletim** (clima/janela);
  - **universo da Plantgest** (técnica, não mercado);
  - os **saltos da Villoresi** a gastar o teto.
