# DEDUP-DOC — a Sala deixa de repetir o mesmo documento

Missão DEDUP-DOC (coleta) · 26/09/2026 · ramo `dedup-doc-v1`, nascido de `ce28040c` e refeito (rebase) sobre `69b0e23f` (o vivo às 05:45).
**NÃO instalado.** Vivo não tocado. Sala real só lida (`default_transaction_read_only = on`, conferido na
saída). Sem rede e sem coleta. O bruto (RAW) não foi alterado; na Sala nada foi apagado.

## 0 · Em uma linha

A Sala tinha **94 linhas**, e **14 delas repetem um documento que já estava lá**. A regra nova impede
novas repetições perguntando pelo **documento do bruto** (`source_id` + `document_key`), e **só** quando
a identidade é provada (`FORWARD_IDENTIFIED`). As 14 antigas ficam na Sala, marcadas neste relatório (§3).

## 1 · O defeito, medido

Onde a Sala decide «já está?»: `admissao/sala_de_espera.py:780` (em `ce28040c`; igual em `83de0ccd`) — compara
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

**VERSÕES — decidido (D79, bot Luciano, 26/09 03:45).** O `document_key` mantém **um** documento
lógico; uma mudança **real** de conteúdo acrescenta uma **versão** num caderno que só acrescenta; bytes
iguais não criam versão. Detalhe na §6.

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
| V1 | bytes do RAW iguais → nenhuma versão |
| V2 | texto diferente com o mesmo extrator → versão 2 (e 3); linha original intacta; retry não duplica |
| V3 | bytes novos, texto igual, mesmo extrator (tipo B) → nenhuma versão |
| V4 | extrator mudou e não há como re-extrair → `NAO_SEI` no recibo, nenhuma versão |
| V5 | extrator mudou, re-extraído do RAW: igual → nada; diferente → versão `REEXTRAIDO_DO_RAW` |
| V6 | identidade não provada → linha nova, nenhuma versão |
| V7 | `UPDATE`/`DELETE`/`TRUNCATE` no caderno de versões → recusados pelo banco |

`tests/test_versao_do_documento.py` (sem banco): 11 testes do decisor.

**Sem teste (declarado):** um bruto `LEGACY_PRE_IDEMPOTENCY` com chave. A 026 só aceita legado com
`id <= corte` (`legado_e_anterior_ao_corte`), por isso não se fabrica num banco novo. Consequência: o
mutante M3 (tirar a exigência `FORWARD_IDENTIFIED`) **deve sobreviver** aos testes — `UNPROVEN` tem chave
nula por lei, e nulo nunca é igual a nulo. A exigência continua no código, porque a Sala real pode ter
legado antigo com chave.

Mutantes do decisor (sem banco, corridos 26/09 ~05:45): **V-M5** comparar a receita só pela versão →
6 falhas; **V-M6** sem o atalho «bytes iguais» → 1 falha; **V-M7** não conferir o extrator da
re-extração → 1 falha. **3/3 mortos.** Decisor: **11/11 OK**.

Mutantes do pousar: M1 sem a pergunta pelo documento · M2 sem a pergunta dentro da mesma corrida · M3 sem a
exigência `FORWARD_IDENTIFIED` · M4 sem comparar a fonte.

### 4.1 · Resultados — PROVADO em Postgres descartável (26/09 10:14–10:50, sob LOCK-PESADO)

| o quê | resultado |
|---|---|
| `tests/test_sala_dedup_por_document_key.py` (dedup A/B/C/C2/U1/U3/L/R/Z + versões V1–V7) | **16/16 OK** |
| `tests/test_versao_do_documento.py` (decisor, sem banco) | **11/11 OK** |
| regressão `tests/test_sala_idempotente_por_documento.py` | **5/5 OK** |
| regressão `tests/test_migracao_033_sala.py` | **15/15 OK** |
| mutantes do pousar | **4/5 mortos**: M1 (4 falhas), M2 (1), M4 (1), M8 sem escrita de versões (3). **M3 sobrevive — previsto** (acima: nulo nunca é igual a nulo; legado com chave não se fabrica) |
| mutantes do decisor | **3/3 mortos** (V-M5, V-M6, V-M7) |

A 1.ª corrida desta vaga deu 14/16: **dois defeitos do teste, não da regra**, corrigidos em `61e91ff8`:
V1 criava um 2.º derivado do mesmo bruto com a mesma receita, e a 022 proíbe isso
(`derivacao_e_unica_por_regua`) — agora usa outra receita; Z contava brutos e derivados juntos.

Histórico: a 1.ª tentativa (25/09 00:12) começou depois do aviso de prioridade da C9 e foi parada;
os seus erros eram do teste (`preserved = true` sem cópia). **Mapa: não regerado** — fica para a
INTEGRA-NOITE (dica da coordenação, 03:21).

## 6 · Versões (D79) — migração 036

**Onde:** tabela nova `sala_de_espera_versao` (`supabase/migrations/036_a_sala_guarda_as_versoes_do_documento.sql`),
só `CREATE`, com gatilhos que recusam `UPDATE`/`DELETE`/`TRUNCATE` — o mesmo desenho do caderno da 033.
O caderno da 033 não serve: só aceita 8 campos (`revisao_so_de_campo_revisivel`). Número 036 porque a
D79 reservou 034 e 035 (no vivo `69b0e23f` a 034 já existe: `034_o_acervo_guarda_tempo_e_lugar_como_derivado`, não a lápide). Desfazer: `supabase/desfazer/036_desfazer.sql`.
**NÃO aplicada na Sala real.** Sem a 036, o `pousar` continua como antes e diz no recibo
«036 não aplicada».

**Quem decide:** `admissao/versao_do_documento.py::decidir`, antes da transação:

| caso | resposta |
|---|---|
| bytes do RAW iguais | IGUAL — nada |
| mesma receita de extrator (`producer` + `producer_version` + `parameters_hash`), texto igual | IGUAL — nada |
| mesma receita, texto diferente | **MUDOU → versão** (`MESMO_EXTRATOR`) |
| receita mudou | re-extrai o RAW anterior com o extrator novo: igual → nada; diferente → **versão** (`REEXTRAIDO_DO_RAW`) |
| receita mudou e não há RAW legível, extrator ou a receita não bate | **NAO_SEI** — não cria versão; fica em `recibo["VERSOES"]` |

**Quem escreve:** `sala_de_espera.py::pousar`, na mesma transação da corrida, debaixo da trava global;
`versao = última + 1`; a mesma versão (mesmo `item_id`) não entra duas vezes.

**A receita conta, não só a versão.** Medido na Sala real: os derivados 66 e 1060 da IT-T9-011 dizem os
dois `texto-de-html` **versão 1**, mas a receita mudou (parâmetros vazios → `TEXT_OWNER =
coleta/texto_fonte.py::limpar`). **O extrator mudou sem subir a versão** — isso é um achado para quem é
dono dos extratores.

**Os 14 repetidos da Sala real, pela regra D79 (só leitura, 26/09 ~05:30):**
6 IGUAL (bytes) · 7 IGUAL (mesmo extrator, texto igual) · **1 NAO_SEI** (IT-T9-011 `derived:1060`: a
receita mudou; sem armazém e extrator ligados, não se re-extrai). **0 versões novas.** Os 88 derivados
da Sala vêm todos de `texto-de-html` v1 ou `texto-de-pdf` v1.

⚠️ **Ligação por fazer (fora desta missão):** os dois chamadores do `pousar`
(`orquestrador/orquestrador.py:745`, `coleta/rota_forward_documento.py:503`) **não passam** `armazem`
nem `extratores`. Enquanto não passarem, todo «extrator mudou» dá `NAO_SEI` — seguro (não cria versão
falsa), mas sem re-extração. Ligar é passar o armazém que eles já têm e um registo
`{producer: extrair}` a partir de `coleta/executor_texto_de_html.py` / `_pdf.py`.

⚠️ **A Intelligence ainda não lê as versões.** `ler_atual` (ramo `sala-leitura-v1`, D10) traz o histórico
de revisões da 033, não as versões da 036. Juntar as duas coisas é o passo seguinte, depois de os dois
ramos entrarem.

## 5 · Plano de instalação (NÃO executado — só o coordenador instala)

1. LOCK-PESADO + ≥ 5 GB. Robô parado (`curadoria/PARAR.flag`), supervisor e observador parados.
2. Backup da Sala (`pg_dump`, como em D68/D74) e do código (`/c/inst/<data>-dedup-doc`).
3. No vivo `source-curator-service-v1` (em `69b0e23f`): `git merge --ff-only origin/dedup-doc-v1`.
   Código: `admissao/sala_de_espera.py` + `admissao/versao_do_documento.py` (novo); 2 testes; este relatório.
   **Migração 036** (tabela nova): aplicar pela cadeia canónica **com backup antes**; ensaiada só em
   descartável. Sem ela, o dedup funciona e as versões ficam desligadas (declarado no recibo).
4. Correr `tests/test_sala_dedup_por_document_key.py` e `tests/test_sala_idempotente_por_documento.py`
   no SHA instalado.
5. Conferir na Sala (só leitura): `select count(*) from sala_de_espera` igual ao de antes (a regra
   não apaga nada).
6. Religar robô, supervisor e observador. Na próxima corrida, o recibo mostra as barradas em
   `JA_NA_SALA_POR_OUTRA_CORRIDA`.
7. **Desfazer:** `git revert` dos commits; no banco, `supabase/desfazer/036_desfazer.sql` (apaga as
   versões — só com backup).

Pendências que não são desta missão: (a) decidir se versões novas do mesmo documento devem aparecer
(caderno de revisões); (b) Source Curator: 1 endereço em 3 fontes (Georgofili); (c) ordem do dono para
marcar as 14 antigas no banco.
