# MICRO-CAMINHO A1 — o que a micro-coleta real vai medir, onde, e o que falta antes

Missão A1 (23/09/2026). Branch `micro-caminho-v2`, sobre `origin/unificacao-v1` @ `8fe122cb`
(3.ª passagem, com a régua multilíngue L1). A v1 foi medida sobre `5a16d077`, antes da L1.
Nada foi colhido da rede, nada foi escrito na Sala real. A Sala real só foi **lida**
(SELECT com `default_transaction_read_only=on`).

## 1. Os campos do mandato (§22) e quem os produz

O §22 do mandato lista **15** campos. SALA_BEFORE e SALA_AFTER estão no bloco da Big
Collection e entram aqui porque o SALA_DELTA depende deles.

| campo | peça que produz | o instrumento lê? | estado |
|---|---|---|---|
| SOURCES_ATTEMPTED | `micro_coleta.correr` (uma corrida por fonte); `italy_pilot_collect.mjs` cont | sim (saída de `correr`) | COM DONO, LIDO |
| SOURCES_SUCCESS | saúde real: `italy_pilot_collect.mjs` cont.HEALTHY/DEGRADED/FAILED → `runs.ndjson` | **não**: só o código de saída do processo | COM DONO, NÃO LIDO |
| DETAIL_DOCUMENTS | `italy_pilot_collect.mjs` cont.DETAIL_NEW → `runs.ndjson` | não | COM DONO, NÃO LIDO |
| LISTINGS_REJECTED | nenhuma: `regras/motor_de_rota.mjs` `ligacoesDoIndice` descarta links sem contar | não | **MISSING_ROUTE** |
| RAW_CREATED | `guarda/preservar_coleta.py` (raw_asset) | sim (linhas de raw_asset) | COM DONO, LIDO (ver defeito D2) |
| DERIVED_CREATED | `guarda/preservar_derivado.py` (derived_artifact) | sim | COM DONO, LIDO |
| ADMISSION_SIM / NAO / NAO_SEI | `admissao/admissao.py` → `data/samples/LIVRO-DE-DECISOES.json` | sim (C7) | COM DONO, LIDO |
| SALA_DELTA | `admissao/sala_de_espera.py` pousar | sim (linhas da Sala por run_id) | COM DONO, LIDO |
| SALA_BEFORE / SALA_AFTER | `select count(*) from sala_de_espera` | não está ligado | ROTA POR LIGAR (trivial) |
| UNNECESSARY_REFETCHES | `italy_pilot_collect.mjs` + `regras/incrementalidade.mjs` → `runs.ndjson` | não | COM DONO, NÃO LIDO |
| FALSE_DOCUMENT_CHANGED | nenhum contador; derivável de `observations.ndjson` (`*CHANGED_IN_PLACE` com `MATERIAL_DIFF=false`) | não | **MISSING_ROUTE** |
| PROVENANCE_FAILURES | o próprio `micro_coleta.relatorio` (C4) | sim | COM DONO, LIDO (ver defeito D2) |
| NETWORK_REQUESTS | `italy_pilot_collect.mjs` REDE.total (INDEX_REQUESTS + DETAIL_REQUESTS) → `runs.ndjson` | não | COM DONO, NÃO LIDO |
| PAID_USD | `orquestrador.py` COST_USD = 0 porque a receita diz «gratuito»; `collection_run.cost_usd` fica NULL | não | DECLARADO, NÃO MEDIDO |

**CAMPOS_COM_DONO = 13/15.** MISSING_ROUTE: LISTINGS_REJECTED e FALSE_DOCUMENT_CHANGED.
O instrumento lê hoje **8 dos 15**. Os contadores do coletor Node (sucesso real,
detalhes, refetch e rede) existem, mas o `italy_executor` só guarda o código de saída e os
últimos 1500 caracteres do stderr, e o resumo vai só para `runs.ndjson`.

## 2. A Sala: onde está, como medir, como se desfaz

- **Onde:** Postgres `sala_italia` em `127.0.0.1:54330`. O cluster está em
  `%USERPROFILE%\sintonia-sala-italia\cluster`, a DSN em `SALA_DSN.txt` e o `psql` em
  `%USERPROFILE%\orca\pgtmp\pgsql\bin`. As tabelas `sala_de_espera`, `raw_asset`,
  `storage_object`, `derived_artifact` e `collection_run` estão na mesma base.
- ⚠️ **Sem `SINTONIA_SALA_BACKEND=POSTGRES`, a Sala cai calada num FICHEIRO**
  (`admissao/sala_de_espera.py:810`). O `micro_coleta correr` recusa arrancar sem as quatro
  variáveis, e é essa a trava.
- **Medida real, só leitura, 23/09 ~08:30Z:**

  | tabela | linhas |
  |---|---|
  | `sala_de_espera` | 61 |
  | `raw_asset` | 1405 |
  | `storage_object` | 1097 |
  | `derived_artifact` | 908 |
  | `collection_run` | 389 |

  O 61 é o fim do lote-76 (56 → 61).
- **SALA_BEFORE / AFTER:** `select count(*) from sala_de_espera`, pelo `micro_coleta.sql`
  (só SELECT, ligação read-only), antes e depois da coorte. O ensaio já o faz; o
  `micro_coleta` ainda não (defeito D3).
- **Rollback (PROVADO no ensaio):** não existe apagar por `run_id`, e as chaves estrangeiras
  são RESTRICT. O método é o do lote-76:
  1. `backup_sala.cmd` (`pg_dump -Fc -Z 6 --no-owner --no-privileges`) **imediatamente antes**;
  2. para desfazer, com o serviço parado: `dropdb` → `createdb` → `pg_restore` desse dump.
  
  No ensaio, sobre uma base **cheia** (backup depois da 1.ª fonte, com 10 linhas na Sala e
  30 RAW), a 2.ª fonte acrescentou dados e o restauro devolveu **conteúdo md5 idêntico** nas
  5 tabelas.
  ⚠️ O `pg_restore` por cima da base existente, sem a apagar antes, «ignorou 499 erros» e
  deixou os dados da corrida: sai com código 1, mas **parece** ter corrido. Só a comparação
  de conteúdo o apanhou.
- **Não há backup do estado atual:** o mais recente é `POS-LOTE76-PARCIAL.dump` (22/09 16:33).
- **Quarentena (Q1):** não há mecanismo de quarentena nesta linha de código. NÃO SEI se já
  foi publicada noutra branch.

## 3. O ensaio offline (DRY-RUN)

`py scripts/micro_coleta/ensaio_offline.py [--fontes=...] [--provar-rollback] [--manter]`

- **Mesmo caminho e mesmo comando da corrida real:** orquestrador → italy_executor →
  coletor Node → ingresso → preservar → derivação → Admission → Sala, e depois o
  `micro_coleta.relatorio` sem cópia.
- **Rede:** um `_curlrc` em `CURL_HOME` com `connect-to` manda todo pedido do `curl` a
  127.0.0.1.
  - ⚠️ Os valores têm de ir **entre aspas**; sem elas o `curl` ignora a opção calado.
  - O servidor serve 304 páginas já guardadas: os gabaritos mais 97 matérias do lote-76,
    incluindo os 10 itens do GABARITO-MICRO.
  - O `ipinfo.io` recebe 404, e por isso o egresso fica NÃO SEI, nunca um «IT» fingido.
- **Base:** Postgres descartável chamado `sala_italia`, numa porta livre, com as 31
  migrations pela cadeia canónica. A Sala real não é tocada.
- **Árvore:** worktree temporária com o ledger do coletor **vazio**. Com o livro versionado,
  as matérias gravadas seriam puladas como «já conhecidas».

**Resultado com a coorte G1 (8 fontes), sobre `8fe122cb`.** Sobre `5a16d077` (sem a L1) duas
corridas deram os mesmos números entre si; a diferença entre as duas linhas é só a L1, e está
na coluna da direita.

| campo | valor (com L1) | sem L1 (5a16d077) |
|---|---|---|
| SOURCES_ATTEMPTED | 8 | 8 |
| SOURCES_SUCCESS | 6 (HEALTHY; IT-T2-051 sem contrato; IT-T7-041 recusada pelo portão: ESTADO_NAO_READY) | 6 |
| DETAIL_DOCUMENTS | 88 (88 pedidos de detalhe) | 88 |
| LISTINGS_REJECTED | NÃO SEI (MISSING_ROUTE); o juiz de capa apontou 5 depois, em C2 | idem |
| RAW_CREATED | 88 documentos, 0 registos de falha | 88 |
| DERIVED_CREATED | 88 | 88 |
| ADMISSION_SIM / NAO / NAO_SEI | **14 / 31 / 43** | 10 / 29 / 49 |
| SALA_BEFORE → SALA_AFTER | **0 → 14** (SALA_DELTA 14) | 0 → 10 |
| UNNECESSARY_REFETCHES | 0, por construção (1.ª passagem, ledger vazio) | 0 |
| FALSE_DOCUMENT_CHANGED | 0, por construção (MISSING_ROUTE no código) | 0 |
| PROVENANCE_FAILURES | 0 (só documentos; o instrumento também dá 0 nesta corrida) | 0 |
| NETWORK_REQUESTS | 100, todos ao servidor local (94 com 200; 6 com 404, que são o ipinfo); egresso Python 0 | 100 |
| PAID_USD | 0 (declarado) | 0 |

**Critérios C1–C9 (com L1):** C4, C5, C6, C7, C8 e **C9** PASS; C2 PENDENTE_HUMANO (5 capas);
C1 e C3 FAIL.
- C1 falha por não haver egresso medido no ensaio (por desenho; na corrida real mede-se).
- C3 falha porque a IT-T7-041 não estava ELIGIBLE no instante.
- Sem a L1, o C9 falhava com 10 itens em inglês em NÃO SEI sem sinal.

**C8, o gabarito validado pelo dono (com L1):** SIM_ERRADO = 0. Universo acertado: **10/10**
no binário (entra / não entra) e 6/10 no estrito. Relevante fora da Sala: **itens 9 e 10**,
os dois REROUTE que o dono pediu (T7 → T10 e T7 → T1). Sem a L1 eram 8/10 e 3/10, e os
itens 5 e 6 (Zootecnica, em inglês) também ficavam fora.

**O que cada fonte produziu no ensaio:**

| fonte | resultado |
|---|---|
| IT-T10-018 | 30 documentos: SIM 10, NAO 7, NAO_SEI 13 (igual nas duas linhas) |
| IT-T10-021 | 1: NAO |
| IT-T10-022 | 10: SIM 4, NAO 2, NAO_SEI 4 (com L1; sem ela, 10 NAO_SEI) |
| IT-T7-017 | 30: NAO 20, NAO_SEI 10 |
| IT-T7-033 | 15: NAO_SEI |
| IT-T7-043 | 2: NAO 1, NAO_SEI 1 |
| IT-T2-051 | sem contrato |
| IT-T7-041 | recusada pelo portão |

## 4. A coorte da micro (G1, após D8/D9/D10) e o comando exato

Fonte: `scripts/desbloqueio/FUNIL-APOS-ENSAIO-G1.json` (funil 45 → 16 → 10 → 8 → 8).

```
py orquestrador/orquestrador.py preco    --filtro fonte=IT-T10-018 --filtro universo=T10
py orquestrador/orquestrador.py preco    --filtro fonte=IT-T10-021 --filtro universo=T10
py orquestrador/orquestrador.py preco    --filtro fonte=IT-T10-022 --filtro universo=T10
py orquestrador/orquestrador.py clima    --filtro fonte=IT-T2-051  --filtro universo=T2
py orquestrador/orquestrador.py agronomo --filtro fonte=IT-T7-017  --filtro universo=T7
py orquestrador/orquestrador.py agronomo --filtro fonte=IT-T7-033  --filtro universo=T7
py orquestrador/orquestrador.py agronomo --filtro fonte=IT-T7-041  --filtro universo=T7
py orquestrador/orquestrador.py agronomo --filtro fonte=IT-T7-043  --filtro universo=T7
```

A porta prevista é `py scripts/micro_coleta/micro_coleta.py correr --autorizado-pelo-dono`,
que lança exatamente estes comandos. **Hoje ela só lançaria a IT-T10-018** (defeito D1).

## 5. Defeitos e propostas (medidos; NÃO aplicados)

- **D1 — a coorte e os filtros do instrumento estão atrás do G1.**
  - O `plano` lê `COORTE-PROPOSTA.json` (14 fontes) e o filtro M3b (relevância).
  - Resultado: PRONTAS 1 / BLOQUEADAS 13.
  - Dos 8 do G1, 3 nem estão na coorte (IT-T7-017, IT-T7-033, IT-T7-041).
  - Outros 4 são barrados pela 3b: IT-T10-022 e IT-T2-051 «fica fora», IT-T7-043 «não sei»,
    IT-T10-021 não medida. A IT-T2-051 também não tem contrato.
  - A decisão D8 do dono (G0/G1) passou por cima da 3b; o instrumento ainda não sabe.
- **D2 — RAW_CREATED e C4 misturam registos de falha com documentos.**
  - Cada matéria que falha (404, transporte) vira uma observação JSON guardada como
    `raw_asset`, e sem derivado.
  - Medido no 1.º ensaio: 30 linhas de raw_asset para 1 documento, e «29 falhas de
    proveniência» que não existem.
  - Critério certo: o conteúdo do registo (HEALTH_STATE=FAILED e SHA256 vazio). A pasta
    (`OBSERVATION`) não serve, porque é a mesma para todos.
- **D3 — SALA_BEFORE e SALA_AFTER não estão ligados.**
- **D4 — SUCCESS = código de saída 0:** uma fonte FAILED no coletor pode sair SUCCESS.
  Ler `runs.ndjson` pelo RUN_ID.
- **D5 — DETAIL_DOCUMENTS, UNNECESSARY_REFETCHES e NETWORK_REQUESTS existem em
  `runs.ndjson` e não são lidos.**
- **D6 — LISTINGS_REJECTED e FALSE_DOCUMENT_CHANGED não têm contador.**
  - O primeiro exige que `ligacoesDoIndice` conte o que descarta.
  - O segundo deriva-se de `observations.ndjson`.
- **D7 — RESOLVIDO na linha atual.** A régua multilíngue L1 (`admissao/idioma.py`) entrou na
  3.ª passagem da unificação. Medido: C9 passa (0 violações) e os itens 5 e 6 entram na Sala.
- **D8 — refetch e «falso mudou» só se medem numa 2.ª passagem** sobre o mesmo ledger. Na
  1.ª passagem dão 0 por construção.

## 6. PRE_MICRO_CHECKLIST — tem de estar verde antes de `correr`

1. [ ] Cutover feito: a produção nesta linha, `origin/unificacao-v1` ou o que a suceder.
2. [ ] Pacote G1 (desbloqueio D8/D9/D10) aplicado no livro e na tabela do serviço.
3. [ ] D1 resolvido: a coorte do instrumento = os 8 do G1, e o filtro 3b reconciliado com a
       D8, **por decisão do dono ou do coordenador**, não por mim.
4. [x] Régua multilíngue L1 na linha (`unificacao-v1` @ `8fe122cb`). Confirmar que é esta a
       linha instalada na produção antes de `correr`.
5. [ ] Contrato de coleta para a IT-T2-051, ou retirá-la da coorte. E a IT-T7-041 em
       READY_CURRENT, ou fora.
6. [ ] `backup_sala.cmd` corrido **imediatamente antes**, com o dump verificado
       (`pg_restore -l` lista `sala_de_espera`). Registar SALA_BEFORE.
7. [ ] Serviço do curator parado durante a micro, ou pelo menos sem colher. O rollback
       exige a base sem ligações.
8. [ ] As quatro variáveis da Sala definidas (`SINTONIA_SALA_BACKEND=POSTGRES`) e
       `BANCO_DESCARTAVEL_URL` ausente.
9. [ ] VPN IT medida (ipinfo = IT) antes e depois de cada fonte; o instrumento já o faz.
10. [ ] Orçamento de rede: no ensaio foram 100 pedidos para 8 fontes (MAX_TARGETS 30 por
        fonte). Robots respeitado pelo coletor.
11. [ ] PAID_USD = 0: nenhuma rota paga na coorte (todas `italia-recorrente`, «gratuito»).
12. [ ] D2–D5 ligados no relatório, ou medidos à parte pelo `ensaio_offline.campos` sobre a
        corrida real.
13. [ ] Plano de rollback escrito com o nome do dump do passo 6.
