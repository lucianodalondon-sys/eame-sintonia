# CUTOVER — folha de uma página

Comandos completos em `CUTOVER-RUNBOOK.md` (mesmos números de passo). Ensaio final X2:
353 s de comandos, 429 s no relógio. Se um número não bater, **pare no 🛑 seguinte**.

**Antes (bot a correr)**
- [ ] 0 · `FINAL` medido na hora (ensaio: `516132fe`, e recomenda-se que já inclua
      `cutover-ensaio-v1`) · `$CASA` criada em `FINAL` · `LANE=SIM`?
- [ ] 0 · PIDs anotados: supervisor + lançador, observador + lançador (hoje 98512/80772 e
      14960/98996). HEAD vivo e ramo anotados (hoje `075501a0`, `source-curator-service-v1`).
- [ ] 0 · `medir_cutover pre` → rc 0 · A1 OK · A2 `LEVAR_NO_5B` (hoje 430/302) · A3 OK
      🛑 ABORTAR-0

**Parado ⏱️**
- [ ] 1 · `PARAR.flag`; supervisor sai (≤ 60 s); `taskkill /T` no lançador do observador;
      nenhum processo sobra 🛑 ABORTAR-1
- [ ] 2 · 3 fotografias com `CORTE.json` (≈ 96 s); nenhuma `NAO CONGELOU` 🛑 ABORTAR-2
- [ ] 3 · o corte vira o ramo `cutover-corte-$D`
- [ ] 4 · reconciliar: rc 0; a 2.ª corrida acrescenta 0 (≈ 145 s) 🛑 ABORTAR-4
- [ ] 5 · unir → 5b (rc 0) → D13 · D15 · PAÍS → commit → G1 ×2 (2.ª: `ESCRITO: 0`,
      livro do bot numa **cópia fora do corte**) → 5c (6) → D13 (0) → interface
- [ ] 6 · `medir_cutover livros --pasta $CASA` → rc 2 **só** por B4 · portão ≈ 29 ·
      retiradas todas recusadas → commit, anotar `CUT` 🛑 ABORTAR-6
- [ ] 7 · na viva: `checkout -- .` · `switch -c servico-$D $CUT` · 0 sujos
- [ ] 7b · `passos_do_cutover 7b --escrever` → **7** na fila (não 6) · `medir livros`
      na viva → rc 0 🛑 ABORTAR-7
- [ ] 8 · apagar `PARAR.flag` · relançar o supervisor (como hoje) ⏱️ **fim do tempo parado**

**Depois (bot a correr)**
- [ ] 9 · 2 min depois: `medir_cutover pos` → rc 0 (um só worker; RUNNING/IDLE;
      NAO SEI vazio) 🛑 ABORTAR-9
- [ ] 10 · na `$CASA`: cadeia do mapa (≈ 8 min) · push para `cutover-$D` · LOCAL == REMOTO
- [ ] 10 · observador **da `$CASA`**: `--servir --intervalo 20 --lane $VIVA` (sem
      `--lane` se `LANE=NAO`) · `--saude` → a trabalhar · 1.ª travessia com o portão estável
- [ ] 10 · avisar a M5: `unificacao-v1` pode avançar para `cutover-$D`; **a `$CASA` é a
      casa viva da ponte**, e ninguém trabalha lá

**Desfazer** (qualquer 🛑 depois do passo 1): parar o que foi relançado → viva de volta
ao ramo anotado → repor os livros das 3 fotografias (conferir o sha256 com o `CORTE.json`) →
apagar a `$CASA` → relançar como estava (supervisor na viva; observador em
`ponte-curador-v1`).

**Só se vê no vivo:** as 7 da D10 com internet (o ensaio foi sem rede) · PASS_PARCIAL
numa volta real.
