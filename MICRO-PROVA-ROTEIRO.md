# MICRO-PROVA-ROTEIRO · LOTE 1 + SONDA Coldiretti numa só sessão de rede (e o LOTE 2 pronto)

Ramo **`micro-prova-lote2-v1`**, a partir do vivo `origin/servico-20260923-0923` @ **`69b0e23f`** (INTEGRA-NOITE lote 1).
Medido a 26/09 entre 05:50 e 07:30 local, **sem rede**. Nada instalado; vivo e Sala não tocados.

## 0 · O que tem de estar certo antes (medido)

- **As ferramentas NÃO estão no vivo.** O «LOTE 1 instalado» (69b0e23f) é o da INTEGRA-NOITE; o `destravar-v1`
  (leitor de prova, sonda, ensaio) ficou fora. Este ramo junta-o por cima de `69b0e23f` (só o mapa declarado em
  conflito, resolvido pela união: as peças da produção + as 2 da micro-prova, 0 ficheiros com dois donos).
  Instalar = `git merge --ff-only` (o ramo desce de `69b0e23f`); **só acrescenta ferramentas** — o robô não as chama.
- **Colisão com a 4.ª onda** (`curadoria/micro_prova_colisao.py`): a rodada 1 da 4.ª onda (`auditoria-madrugada/
  C2-ONDA4/rodadas.txt`: 38 domínios, 174 pedidos) e o que o coletor colheu nas últimas 24 h (33 domínios, lidos nas
  OBSERVAÇÕES — `runs.ndjson` não tem `PEDIDOS_POR_HOST` em nenhuma das 155 corridas, e contar por lá dava 0 às cegas).
  **Colidem 3**, pelas DUAS razões:
  - **ENEA** (lote 1) — `enea.it` na rodada 1 (5 pedidos) e 6 documentos colhidos em 24 h;
  - **Fitogest** (lote 1) — `imagelinenetwork.com` na rodada 1 (4) e 5 em 24 h;
  - **CNR IT-T5-006** (sonda) — `cnr.it` na rodada 1 (5) e 3 em 24 h.
  **Ficam fora desta sessão** e voltam depois da rodada 1 da 4.ª onda + 24 h. A sessão é
  `curadoria/MICRO-PROVA-LOTE1-SESSAO.json`: **18 candidatas + sonda de 6** → `PODE_CORRER: true` (24 alvos, 0 colisões).
- A 4.ª onda está proibida antes de **26/09 19:34** (janela de 24 h, D79). Como os domínios são DISJUNTOS da rodada 1,
  a sessão não colide com ela em nenhum horário — mas repetir a verificação no instante de correr (o coletor anda).

## 1 · A sessão (numerada) — coordenador, com a VPN IT

`V=$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1`. Rede só pela VPN IT; o robô **pode continuar a
correr** nesta parte (nada disto escreve livro, fila ou Sala).

1. **Instalar as ferramentas:** robô parado só o tempo do ff (`CUTOVER-RUNBOOK.md` passo 1), `git -C $V fetch origin
   micro-prova-lote2-v1 && git -C $V merge --ff-only <SHA entregue>`, religar. (Ou correr tudo a partir de uma cópia do
   vivo com o ramo — os comandos abaixo são os mesmos, com a cópia no lugar de `$V`.)
2. **Portão ANTES:** `py superficie/rede.py --portao-de-egresso IT` → `EGRESS_GATE=PASS`. Outro → PARAR (0 pedidos).
3. **Colisão AGORA:** `py curadoria/micro_prova_colisao.py --rodadas=C:/Users/London1/auditoria-madrugada/C2-ONDA4/rodadas.txt
   --lote=curadoria/MICRO-PROVA-LOTE1-SESSAO.json --sonda=IT-T7-045,IT-T7-050,IT-T7-051,IT-T7-052,IT-T7-053,IT-T7-058`
   → código 0 e `PODE_CORRER: true`. Código 1 → PARAR e tirar da sessão o que ele listar.
4. **Sonda (6 pedidos, 4 rondas, ~1 h — corre sozinha, em segundo plano):**
   `py curadoria/sonda_um_pedido.py --fontes=IT-T7-045,IT-T7-050,IT-T7-051,IT-T7-052,IT-T7-053,IT-T7-058 --saida=<fora do Git>/SONDA-UM-PEDIDO.json`
   ronda 1: anga.it · www.coldiretti.it · unaprol.it; rondas 2–4: puglia · sicilia · veneto.coldiretti.it (20 min entre
   rondas: é o limite por organização que os recibos mostram). Portão pedido antes de cada ronda e no fim.
5. **Lote 1 (18 candidatas, ≤5 pedidos por site, ~90 pedidos, ~10 min — em paralelo com a sonda: domínios distintos):**
   `py curadoria/colher_prova_territorio.py --lote=curadoria/MICRO-PROVA-LOTE1-SESSAO.json --bytes=<fora do Git>/provas-lote1 --saida=<fora do Git>/PROPOSTAS-LOTE1.json`
   Portão pedido antes de cada candidata; robots lido e cumprido.
6. **Portão DEPOIS:** o mesmo comando do passo 2; guardar os dois resultados.
7. **O que ficou gravado** (tudo fora do Git, com sha256): bytes das provas `<pasta>/<CAND>/n_PAPEL.bin`,
   `PROPOSTAS-LOTE1.json` (TERRITORIO = A_DECIDIR), `SONDA-UM-PEDIDO.json`. **Nenhum RAW, nenhum livro, nenhuma Sala.**
   Pedidos totais ≈ 96 (90 + 6).

## 2 · Depois da sessão (sem rede, e a parte que PARA o robô)

8. **Decidir** (Opus/humano): nas propostas com `PROVA_COMPLETA=true`, preencher `TERRITORIO`, `PAIS` **da prova**,
   `DECIDIDO_POR`, `PORQUE` (tabela da gaveta em `MICRO-PROVA-LOTE1.md`). As incompletas não se decidem.
9. **Robô PARADO** (um só escritor): `py curadoria/colher_prova_territorio.py --aplicar=DECIDIDAS-LOTE1.json` (só entra o
   que o validador do canal aceita; o «NAO SEI» antigo fica em `ANTERIOR`) e reabrir as QUALIFY:
   `py -c "import sys; sys.path.insert(0,'curadoria'); import fila as F; print(len(F.recuperar_bloqueadas_por_defeito(['territorio indeterminado pelo nome'], {F.QUALIFY})))"`
   (as sem decisão voltam a BLOCK sozinhas, sem rede — medido 192/192).
10. **Portão IT outra vez** (o worker NÃO verifica o egresso por si) e **religar o robô**: QUALIFY → contrato → rota →
    canário → READY; depois `py medidas/canario_rotas_elegiveis.py --fontes=<IDs novos> --juntar` e o onboarding
    (o supervisor chama-o sozinho) → linha no coletor → coorte da onda seguinte.
11. **Sonda:** as que deram `OK` → re-enfileirar a tarefa CANARY/VALIDATE_ROUTE pelo caminho canónico, **uma
    organização por corrida**; `FECHO_DE_LIGACAO`/`TLS` outra vez → a saída IT é recusada: outra saída, não código.

## 3 · LOTE 2 (pronto para a sessão seguinte)

`curadoria/MICRO-PROVA-LOTE2.json`: **24 candidatas em 24 domínios, 0 colisões** com a rodada 1 e com as 24 h.
- Pesquisa: IJ Food Safety (PAGEPress) · TESAF (2.ª página) · Enteca (ISPRA)
- Bases oficiais agrícolas: SIAN · Agriligurianet · consultazioni MASAF · Dati Ambientali Liguria
- Imprensa agrícola (T8): Agricultura.it · Il Nuovo Agricoltore · Agrifoodtoday · Il Fatto Alimentare · Mangimi & Alimenti
- Rede técnica (T7): Agrinsieme · CIA Abruzzo · CIA Veneto · CIA Marche · Unione Italiana Vini · Periti Agrari · PescAgri · Italia Cooperativa
- Mercado (T10, só 8 READY): Agrifood Monitor · Wine Monitor — Feiras (T11, só 3 READY): Interpoma · Fieravicola
- **Fora:** as ordens (D52), 11 de país NÃO SEI/EU/OUTRO (esperam a decisão EU/INT), 10 páginas soltas (leis, decretos, «via
  Stalingrado»… — são recusas, não provas), Rete Rurale (janela 01–03 UTC, sessão própria) e **Terremerse** (ver abaixo).

**Ensaio a seco** (cópia fiel do vivo `69b0e23f` + 16 livros sujos conferidos 16/16; servidor local; 0 rede real;
`curadoria/ENSAIO-MICRO-PROVA-LOTE2.json`), com as 25 de antes da troca:
- **21 PRONTA** (prova → decisão no canal → SOURCE_ID → contrato → rota → canário → READY → portão ELIGIBLE → ROUTE_PROVEN → coletor);
- **3 NÃO desenhadas a partir do que já se sabe:** SIAN (portal: 403 na entrada), Agrifood Monitor e Wine Monitor
  (a 23/09 deram os MESMOS bytes — casca JS) → prova incompleta, sem decisão;
- **1 NÃO que NÃO desenhei — e é real:** **Terremerse** (CAND-0151) passou a prova e a decisão (IT-T1-026), mas o
  BUILD_CONTRACT recusou: a `SOURCE-CHARACTERIZATION-V1` do vivo diz «SIM — ramo de índice» (o molde genérico daria lista
  vazia; dono: SCRAP ENGINEER). Aconteceria igual com a rede. **Saiu do lote 2** (5 pedidos para nada); é a única das 42 dos
  dois lotes com essa marca.
Contas: 24 × 18,9 % ≈ **4,5** fontes novas no rendimento medido; **24** no melhor caso.

## 4 · Código e provas neste ramo

`micro_prova_colisao.py` + testes 5/5 · `MICRO-PROVA-LOTE1-SESSAO.json` · `MICRO-PROVA-LOTE2.json` · o ensaio passa a
ler qualquer lote (`--lote=`, desenho em `ENSAIO.CLASSE/FALHA`, falha nova `HTTP_403`) · `ENSAIO-MICRO-PROVA-LOTE2.json`.
Testes das ferramentas no ramo: `test_colher_prova_territorio` 8/8 · `test_sonda_um_pedido` 5/5 · `test_micro_prova_colisao` 5/5.
**Erro meu corrigido:** na primeira edição do ensaio, o `\n` do robots do site HTTP_403 virou quebra de linha real e o
Python recusou o ficheiro — nada correu; corrigido antes do ensaio (commit próprio).

## EM PALAVRAS SIMPLES

- **Uma saída à internet, duas tarefas:** o coordenador liga a VPN italiana, confere o porteiro, e corre ao mesmo tempo
  (1) o teste da Coldiretti — 6 visitas, uma de cada vez, com pausa — e (2) a leitura de prova de 18 fontes. Nada disso
  mexe no robô; o robô pode ficar ligado.
- **Três ficam para depois:** ENEA, Fitogest e CNR vão ser visitados pela 4.ª onda logo na primeira rodada e já foram
  visitados ontem. Mandar mais visitas agora é o jeito de sermos bloqueados. Voltam depois.
- **As ferramentas ainda não estão no robô** — o primeiro passo é instalá-las (só acrescentam, não mudam nada).
- **Lote 2 pronto:** 24 fontes (imprensa agrícola, associações técnicas, mercado, feiras, pesquisa). No teste sem
  internet, 21 de 25 chegaram a «pronta». Uma delas (Terremerse) parou por um motivo real — o robô ainda não sabe ler
  aquele tipo de site — e tirei-a do lote.
