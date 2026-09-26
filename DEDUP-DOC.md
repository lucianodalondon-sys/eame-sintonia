# DEDUP-DOC — a Sala deixa de repetir o mesmo documento

Missão DEDUP-DOC (coleta) · 26/09/2026 · ramo `dedup-doc-v1` a partir de `ce28040c` (o vivo).
**NÃO instalado.** Vivo não tocado. Sala real só lida (`default_transaction_read_only = on`, conferido na
saída). Sem rede e sem coleta. O bruto (RAW) não foi alterado; na Sala nada foi apagado.

## 0 · Em uma linha

A Sala tinha **94 linhas**, e **14 delas repetem um documento que já estava lá**. A regra nova impede
novas repetições perguntando pelo **documento do bruto** (`source_id` + `document_key`), e **só** quando
a identidade é provada (`FORWARD_IDENTIFIED`). As 14 antigas ficam na Sala, marcadas neste relatório (§3).

## 1 · O defeito, medido

Onde a Sala decide «já está?»: `admissao/sala_de_espera.py:780` (em `ce28040c`) — compara
`(item_id, universo)`. O `item_id` é `derived:<n>`, o número do **derivado**, não do documento. Se o
bruto muda uns bytes (sha novo), nasce derivado novo, `item_id` novo, e o mesmo documento entra outra vez.

Três formas, todas vistas na Sala real:

| tipo | o que é | exemplo | a regra antiga barrava? |
|---|---|---|---|
| A | mesmo documento, mesmo bruto (sha igual), mesmo `item_id` | IT-T5-015 | sim, desde `f2d5217b` (23/09); estas linhas são de antes |
| B | mesmo documento, bytes novos → `item_id` novo | IT-T5-030, IT-T9-011 | **não** |
| C | o mesmo endereço registado em várias fontes | `georgofili.it/elenco-atti-georgofili` = IT-T5-034/035/036 | não |

Prova de que o tipo B ainda acontece: a IT-T9-011 ganhou a **3.ª linha em 25/09 22:57** (`derived:1060`).
O texto só difere porque o extrator mudou de versão (v5 → v9) e passou a ler o menu do site
(lista de países, `Contatti`). É a mesma matéria. **Comparar o texto não serve para achar repetidos.**

## 2 · A regra nova

Em `pousar` (backend POSTGRES), uma unidade **não** ganha linha se:

1. (já existia) outra corrida já pousou o mesmo `(item_id, universo)`; **ou**
2. (nova) o bruto dela é `FORWARD_IDENTIFIED` e já há na Sala, noutra corrida e **no mesmo universo**,
   uma linha cujo bruto é `FORWARD_IDENTIFIED` com **o mesmo `source_id` e o mesmo `document_key`**; **ou**
3. (nova) na **mesma corrida**, uma unidade anterior (ordem menor) tem esse mesmo documento.

O que a regra **não** faz, de propósito:
- **Identidade não provada nunca funde.** `FORWARD_IDENTITY_UNPROVEN` (chave nula, por lei da 026),
  `LEGACY_PRE_IDEMPOTENCY` (mesmo que traga chave) e unidade sem bruto (`NAO SEI`) passam como antes.
- **Não funde fontes diferentes.** O `source_id` entra na comparação: `CAMPANIA:SA:16-09-2026` não tem
  prefixo de fonte, e duas fontes não podem virar uma por coincidência de chave. Por isso o tipo C
  **entre fontes** continua: a página dos Georgofili fica com 3 linhas (uma por fonte). É defeito de
  **catálogo** (3 SOURCE_IDs para 1 endereço), não da Sala → vai para o Source Curator.
- **Outro universo continua a ser outra entrada** (REROUTE, D2).
- **Não apaga nem altera nada.** A observação nova continua em `raw_asset` e no derivado; só não volta
  à fila da Intelligence. A trava global `sala_de_espera:identidade` já serializa a pergunta.

⚠️ **Mudança de lei declarada.** O comentário em `sala_de_espera.py` dizia «VERSÃO NOVA = LINHA NOVA».
Com esta regra, uma versão nova **do mesmo documento** (conteúdo mudou de verdade) **também não** ganha
2.ª linha. Foi a decisão do bot Luciano (dedupe por `document_key`). Se o dono quiser versões na Sala, o
caminho é o caderno de revisões da 033, não uma linha nova. **Decisão do dono, não minha.**

**PERGUNTA AO DONO — VERSÕES** (um documento que muda de verdade, depois de já estar na Sala):
- **Opção A · guardar no caderno de revisões da 033:** a linha antiga fica, e a mudança entra como revisão (só acrescenta, com a data da mudança). Precisa de código novo; a Intelligence vê que o documento mudou.
- **Opção B · ignorar:** a Sala guarda só a 1.ª versão; a nova fica no bruto e no derivado, fora da fila. É o que a regra faz hoje, sem código novo.

O backend FICHEIRO **não mudou** (não tem `raw_asset`). Declarado.

## 3 · Os afetados na Sala real (só leitura, 26/09 ~00:10)

Consulta com a regra exata: 94 linhas; **13 documentos** com mais de uma linha; **14 linhas seriam
barradas** hoje; 13 ficam (a primeira de cada documento). Nada foi mudado na Sala.

| fica (1.ª) | seria barrada | fonte | universo | tipo | sha igual? |
|---|---|---|---|---|---|
| derived:6 (raw 7) | derived:6 (raw 26) | IT-T3-002 | T3 | A | sim |
| derived:56 (raw 164) | derived:56 (raw 289) | IT-T5-015 | T5 | A | sim |
| derived:57 (raw 165) | derived:57 (raw 298) | IT-T5-024 | T5 | A | sim |
| derived:58 (raw 166) | derived:128 (raw 299) | IT-T5-025 | T5 | B | não |
| derived:59 (raw 167) | derived:129 (raw 301) | IT-T5-027 | T5 | B | não |
| derived:60 (raw 168) | derived:60 (raw 302) | IT-T5-028 | T5 | A | sim |
| derived:61 (raw 169) | derived:130 (raw 304) | IT-T5-030 | T5 | B | não |
| derived:62 (raw 170) | derived:62 (raw 305) | IT-T5-033 | T5 | A | sim |
| derived:63 (raw 171) | derived:131 (raw 306) | IT-T5-034 | T5 | B + C | não |
| derived:87 (raw 200) | derived:132 (raw 307) | IT-T5-035 | T5 | B + C | não |
| derived:64 (raw 173) | derived:133 (raw 308) | IT-T5-036 | T5 | B + C | não |
| derived:65 (raw 174) | derived:134 (raw 309) | IT-T7-013 | T7 | B | não |
| derived:66 (raw 175) | derived:66 (raw 313) **e** derived:1060 (raw 1559, 25/09 22:57) | IT-T9-011 | T9 | A + B | 1.ª sim, 2.ª não |

As repetidas são de 18 a 20/09 (as duas corridas de 20/09, 13h e 19h), **mais a de 25/09 22:57**.
Os 94 brutos da Sala são todos `FORWARD_IDENTIFIED`: nenhum afetado depende de identidade não provada.
Tipo C entre fontes (fica): IT-T5-034/035/036 — 3 linhas, 1 por fonte, mesmo texto.

**Marcação das antigas:** este relatório é a marca. Marcar no banco (ex.: revisão da 033 com
`campo = 'repetido_de'`) é escrita na Sala → **só com ordem do dono**, fora desta missão.

## 4 · Testes

`tests/test_sala_dedup_por_document_key.py` — Postgres descartável, migrations pela cadeia canónica.

| teste | o que prova |
|---|---|
| A | mesmo bruto e mesmo item_id → 1 linha |
| B | bytes novos, item_id novo, mesmo documento → 1 linha (**o defeito**) |
| C | mesmo endereço noutra fonte entra; na mesma fonte outra vez, não |
| C2 | chave igual sem prefixo em fontes diferentes não funde |
| U1 | `FORWARD_IDENTITY_UNPROVEN` não funde |
| U3 | unidade sem bruto (`NAO SEI`) entra |
| L | o mesmo documento 2× na mesma corrida → 1 linha |
| R | mesmo documento noutro universo entra (REROUTE) |
| Z | o bruto só cresce |

**Sem teste (declarado):** um bruto `LEGACY_PRE_IDEMPOTENCY` com chave. A 026 só aceita legado com
`id <= corte` (`legado_e_anterior_ao_corte`), por isso não se fabrica num banco novo. Consequência: o
mutante M3 (tirar a exigência `FORWARD_IDENTIFIED`) **deve sobreviver** aos testes — `UNPROVEN` tem chave
nula por lei, e nulo nunca é igual a nulo. A exigência continua no código, porque a Sala real pode ter
legado antigo com chave.

Mutantes: M1 sem a pergunta pelo documento · M2 sem a pergunta dentro da mesma corrida · M3 sem a
exigência `FORWARD_IDENTIFIED` · M4 sem comparar a fonte.

### 4.1 · Resultados

**NÃO PROVADO ainda.** Estado honesto em 26/09 ~01:00:

- 1.ª corrida (00:12, sob LOCK-PESADO): **9 de 10 com erro**, 1 ok. A causa estava no **teste**, não
  na regra. O teste criava brutos com `preserved = true` sem cópia, e a 025 recusa isso
  (`preservado_aponta_para_a_copia`). Também não se pode criar legado num banco novo (corte da 026).
  O teste foi corrigido em `3b1ca724` (brutos `preserved = false` com motivo; sai o caso do legado).
- A mesma corrida passou a **regressão** `tests/test_sala_idempotente_por_documento.py`: **5/5 OK com
  a regra nova**.
- ⚠️ Essa corrida começou às 00:12, depois do aviso `LOCK-PRIORIDADE.txt` (00:08) a favor da C9. Eu
  não tinha conferido esse ficheiro. Parei, soltei a trava e desliguei o Postgres de teste.
- **Testes corrigidos e mutação M1–M4: NÃO corridos.** A prioridade da C9 continuava às 00:56.
  Comando para quando a trava estiver livre (sem prioridade, ≥ 5 GB):
  `PYTHONUTF8=1 py tests/test_sala_dedup_por_document_key.py`. Previsão: M1, M2 e M4 morrem; M3
  sobrevive (explicado acima).

## 5 · Plano de instalação (NÃO executado — só o coordenador instala)

1. LOCK-PESADO + ≥ 5 GB. Robô parado (`curadoria/PARAR.flag`), supervisor e observador parados.
2. Backup da Sala (`pg_dump`, como em D68/D74) e do código (`/c/inst/<data>-dedup-doc`).
3. No vivo `source-curator-service-v1` (em `ce28040c`): `git merge --ff-only origin/dedup-doc-v1`.
   Muda **um** ficheiro de código (`admissao/sala_de_espera.py`) e acrescenta 1 teste e este relatório.
   **Sem migration**: não há coluna nem tabela nova; a regra vive no `insert` do `pousar`.
4. Correr `tests/test_sala_dedup_por_document_key.py` e `tests/test_sala_idempotente_por_documento.py`
   no SHA instalado.
5. Conferir na Sala (só leitura): `select count(*) from sala_de_espera` igual ao de antes (a regra
   não apaga nada).
6. Religar robô, supervisor e observador. Na próxima corrida, o recibo mostra as barradas em
   `JA_NA_SALA_POR_OUTRA_CORRIDA`.
7. **Desfazer:** `git revert` do commit da regra; nada no banco para desfazer.

Pendências que não são desta missão: (a) decidir se versões novas do mesmo documento devem aparecer
(caderno de revisões); (b) Source Curator: 1 endereço em 3 fontes (Georgofili); (c) ordem do dono para
marcar as 14 antigas no banco.
