# RECONCILIAÇÃO CONSTITUCIONAL — apêndice H da Bíblia

**Data:** 2026-09-08 · **Ramo:** `claude/italia-biblia-integracao-v1`
**Bíblia consumida:** `37020bc` (V1.2) · **Engenharia consumida:** `a32799c`
**Base comum:** `4fc8670`

> A Bíblia e a engenharia italiana viviam em dois ramos. Este documento é o que aconteceu
> quando as duas foram postas no mesmo HEAD e **a lei foi confrontada com a primeira estrada
> real da coleta** — PDF guardado → texto derivado → porta de admissão.
>
> **Nenhum número aqui foi copiado da documentação.** Tudo foi medido de novo, nesta árvore.

---

# A · O CENSO DA INTEGRAÇÃO

| | |
|---|---|
| ficheiros tocados pela **Bíblia** | 22 |
| ficheiros tocados pela **engenharia** | 88 |
| **sobreposição** | **8** |
| destes, **gerados** (não se resolvem à mão) | **7** |
| destes, **fonte real** | **1** — `system-map/data/architecture.declared.json` |

## O único ficheiro de fonte em conflito — resolvido por estrutura, não por linha

| | ENGENHARIA | BÍBLIA | interseção |
|---|---|---|---|
| territórios novos | `Z-ENTRADA` · `Z-ORQUESTRADOR` · `Z-EXECUCAO` | `Z-BIBLIA` | **nenhuma** |
| territórios alterados | 9 | 0 | **nenhuma** |
| peças novas | 7 (Golden Path) | `C-BIBLIA` · `C-PROVA-BIBLIA` | **nenhuma** |
| peças alteradas | `C-CI-COLETA` · `C-ORQUESTRADOR` · `C-PALAVRAS` · `C-PROVA-COLETA` · `C-SINTONIA-SCRAP` | `C-SUPABASE` · `C-CI-PERSIST` | **nenhuma** |

> ## CONFLITO TEXTUAL: 4 blocos. CONFLITO SEMÂNTICO: ZERO.
> **Nenhum id foi tocado pelos dois lados.** Os quatro blocos eram inserções no mesmo ponto
> do ficheiro — não discordâncias sobre a mesma coisa.

O ficheiro foi reconstruído **por estrutura**: união de territórios e peças por `id`, com um
`assert` que reprovaria se alguma peça da Bíblia tivesse sido alterada também pela
engenharia. Passou. Os sete gerados foram **regerados**, nunca editados.

| classificação do conflito | nº |
|---|---|
| `GENERATED` | 7 |
| `TEXTUAL` (aditivo, mesmo ponto) | 1 ficheiro · 4 blocos |
| `SEMANTIC` | **0** |
| `CONTRACT` · `TEST` · `MAP` (semânticos) | **0** |

---

# B · O GOLDEN PATH, REPRODUZIDO

**Não foram copiados números.** `py coleta/golden_path_pdf.py` foi corrido nesta árvore, e
as contagens foram refeitas por fora, com a mesma regra de seleção do repositório.

| medida | documentado | **medido agora** | ✓ |
|---|---:|---:|---|
| ocorrências (caminhos `.pdf` italianos) | 49 | **49** | ✅ |
| conteúdos `SHA256` únicos | 43 | **43** | ✅ |
| ocorrências de mesmo conteúdo | 6 | **6** | ✅ |
| textos derivados | 43 | **43** | ✅ |
| fichas no registo de artefatos | — | **43** | ✅ |
| derivados com **pai declarado** | — | **43 de 43** | ✅ |
| `NEEDS_OCR` | 0 | **0** | ✅ |
| `EXTRACTION_ERROR` | 0 | **0** | ✅ |
| `LOST` | 0 | **0** | ✅ |
| RAW imutável | sim | **49 conferidos · `IMUTAVEL`** | ✅ |
| caracteres derivados | 703.022 | **843.906** | ⚠️ **não bate** |

## ⚠️ A contagem de caracteres não se reproduz — e não se inventa um número

`703.022` **não aparece em lado nenhum desta árvore**. O que se mede:

| como se conta | caracteres |
|---|---:|
| lendo os 43 ficheiros do disco (quebra de linha = 1 caractere) | **843.906** |
| lendo os mesmos 43 como o Git os guarda, em `a32799c` | **859.142** |

A diferença entre os dois é exatamente **15.236** — o número de linhas. É a quebra de linha
contada como um caractere ou dois.

**Nenhuma das duas é 703.022.** Este documento **não** adota o número documentado, e também
não afirma que ele estava errado: afirma que **não é reproduzível nesta árvore**. Registrado
como discrepância medida, não como falha do Golden Path — as onze outras medidas batem
exatamente.

## Os 6 repetidos, nomeados

Todos seguem o **mesmo padrão**: o documento na loja do coletor **e** o mesmo documento na
amostra versionada.

```
f88c89d73d6a  data/collection-store/italy/IT-T2-002/ARPAV_Z01_.../agro_01.pdf
              data/samples/IT-SOURCE-SAMPLES/IT-T2-002/agro_01.pdf
3d3c1bc0e963  … ARPAV_Z09 · agro_09.pdf                    (idem)
e612807928b5  … ARIF N36 · Notiziario_…_N36_02-09-2026.pdf  (idem)
59da05274359  … APOL N9 · Bollettino_Mosca_…_07_09_2026.pdf (idem)
0c2723e66201  … CAMPANIA · SA-02-09.pdf                     (idem)
420e08ef15be  data/samples/IT-BOLLETTINI-VPN-2026/pdf/CAMP_SA-26-08.pdf
              data/samples/IT-SOURCE-SAMPLES/IT-T3-002/SA-26-08.pdf
```

> **Não são perda. São duas ocorrências do mesmo conteúdo, com procedências diferentes** —
> uma veio da coleta, outra é a amostra guardada. Apagar uma perderia a prova de como
> chegou ali.

---

# C · AS SETE QUESTÕES CONSTITUCIONAIS

## Q1 · OCCURRENCE × CONTENT

| | |
|---|---|
| **ANTES** | 49 caminhos e 43 conteúdos, sem palavra que os separasse. Uma subtração ingénua lê «6 perdidos» |
| **LEI DA BÍBLIA** | COL-LAW-204 (dedupe não destrói) e COL-LAW-311 (o caminho é endereço, a identidade é o hash) chegam perto — **mas nenhuma diz como CONTAR** |
| **REALIDADE MEDIDA** | 49 ocorrências · 43 conteúdos · 6 repetições, todas do par loja/amostra |
| **RESOLUÇÃO** | ⚖️ **lei nova — `COL-LAW-501`.** Ocorrência e conteúdo são espécies diferentes e a contagem nunca subtrai uma da outra |
| **FICHEIROS** | `BIBLIA-CANONICA-DA-COLETA.md` · `system-map/data/golden-path-pdf.generated.json` |
| **TESTE** | `T6` `T7` `T8` em `tests/test_biblia.py` |

## Q2 · ARTIFACT × FACT

| | |
|---|---|
| **ANTES** | os 43 derivados chegam à porta com `FACT_TIME = "NAO SEI"` e saem `NAO_SEI` |
| **LEI DA BÍBLIA** | **`COL-LAW-201` já resolve, e por inteiro:** `FACT_TIME` é do **fato**, não do artefato, e *«NÃO DEVE ser exigido que todo RAW tenha `FACT_TIME`»* |
| **REALIDADE MEDIDA** | `admissao/admissao.py:169` pergunta *«tem tempo do fato?»* a um documento. 43 de 43 respondem `NAO SEI` — **nunca fabricado**, o que está certo |
| **RESOLUÇÃO** | ✅ **sem lei nova.** A resposta à pergunta M: **NÃO** — o documento não precisa de `FACT_TIME` para o estágio documental |
| **FICHEIROS** | nenhum alterado — é runtime da porta |
| **TESTE** | `T12` `T13` `T14` |

## Q3 · DOCUMENT READY × FACT READY

| | |
|---|---|
| **ANTES** | uma noção só de «pronto», e ela cobrava do documento a régua do fato |
| **LEI DA BÍBLIA** | COL-LAW-043 define `READY`; COL-LAW-201 separa artefato de fato — **mas os dois estágios não tinham nome** |
| **REALIDADE MEDIDA** | **mistura real, confirmada.** E a porta **já sabe** responder `NAO_SE_APLICA` quando a pergunta não é da espécie — faz isso para ficha de conta e de catálogo |
| **RESOLUÇÃO** | ⚖️ **lei nova — `COL-LAW-502`.** `DOCUMENT READY` ≠ `FACT READY`. **Sem estado novo**: os cinco resultados da COL-LAW-038 bastam; o certo é `NAO_SE_APLICA` |
| **NÃO FEITO** | ❌ nenhum extrator de data, nenhuma heurística, nenhum LLM. Gap **G-22** |
| **TESTE** | `T12` |

## Q4 · RUN COMPLETE

| | |
|---|---|
| **LEI DA BÍBLIA** | `COL-LAW-210` — `COMPLETE` exige execução terminada + outputs registados + contas reconciliadas + erros registados + manifesto fechado |
| **REALIDADE MEDIDA** | o recibo `DERIV-PDF-20260908T033724Z` tem `STARTED_AT`/`FINISHED_AT` **medidos** (1 s de diferença), `EVIDENCE_PATH` para as contas, `ERROR`, `COST_USD`. A reconciliação **é feita e é provada** (`LOST = 0`). **Não tem** estado `COMPLETE` explícito, nem `STATE_BEFORE/AFTER`, nem as versões de engenharia |
| **VEREDITO** | 🟡 **`PARTIAL`** — cumpre a substância, falta o fecho atómico e o carimbo de versão |
| **RESOLUÇÃO** | ✅ sem lei nova. Gap **G-26** (fecho) e **G-02/G-307** (versões) |
| **CUIDADO** | `ITEM_COUNT_NORMALIZED = 0` **não é perda**: a corrida é idempotente e os 43 já existiam (`JA_EXISTIAM = 43`) |

## Q5 · EXECUTOR UNAVAILABLE × ARTIFACT ERROR

| | |
|---|---|
| **ANTES** | sem `pdftotext`, **todos** os PDFs voltam `EXTRACTION_ERROR` |
| **LEI DA BÍBLIA** | COL-LAW-037 e COL-LAW-215 dizem que o nosso defeito não vira defeito do mundo — **mas não nomeavam a capacidade ausente** |
| **REALIDADE MEDIDA** | `coleta/executor_texto_de_pdf.py:140-141`. O **motivo** é honesto (`FERRAMENTA_AUSENTE`); o **contador** que sobe é o do erro de extração. Nesta máquina a ferramenta existe, e por isso o defeito está adormecido |
| **RESOLUÇÃO** | ⚖️ **lei nova — `COL-LAW-503`.** A corrida falha no **pré-voo**, antes de tocar em documento |
| **NÃO FEITO** | ❌ nada instalado. Gap **G-34** |
| **TESTE** | `T20` |

## Q6 · SOURCE_HEAD × MAP_ARTIFACT_COMMIT

| | |
|---|---|
| **ANTES** | um campo só — `PROVENANCE.HEAD` — a responder duas perguntas |
| **LEI DA BÍBLIA** | COL-LAW-047 diz que o mapa é saída; **nada dizia qual árvore foi lida** |
| **REALIDADE MEDIDA** | o ramo da engenharia tem **três commits** chamados *«carimbo do HEAD nos ficheiros gerados»*. É a perseguição circular, registrada na história |
| **RESOLUÇÃO** | ⚖️ **lei nova — `COL-LAW-504`.** `SOURCE_TREE_FINGERPRINT` identifica a árvore de forma estável; `MAP_ARTIFACT_COMMIT` é opcional e só se sabe depois. **A igualdade `SOURCE_HEAD == FINAL_HEAD` não se persegue** |
| **NÃO FEITO** | ❌ o gerador não foi alterado. Gap **G-35** |
| **TESTE** | `T25` `T30` |

## Q7 · GITHUB × SUPABASE × REFERENCE PLANE

| | |
|---|---|
| **LEI DA BÍBLIA** | `COL-LAW-301`–`316` e `COL-LAW-401`–`406`, todas da V1.2 |
| **REALIDADE MEDIDA** | preservadas inteiras no merge. `C-SUPABASE` e `C-CI-PERSIST` chegaram ao HEAD integrado com o papel canônico, e **a engenharia não as tinha tocado** |
| **RESOLUÇÃO** | ✅ **sem lei nova.** Preservação verificada por `assert` no merge estrutural |
| **PRESERVADO SEM EXECUTAR** | `P-011` e `G-02/G-30` continuam abertos: **nada movido, nada migrado, Supabase intocado** |
| **TESTE** | `T16` `T17` `T18` |

---

# D · O PLACAR DA RECONCILIAÇÃO

| | nº |
|---|---|
| questões constitucionais confrontadas | **7** |
| já resolvidas por lei existente | **3** (Q2 · Q4 · Q7) |
| exigiram lei nova | **4** (Q1 · Q3 · Q5 · Q6) |
| leis novas criadas | **4** — `COL-LAW-501` a `504` |
| leis renumeradas ou apagadas | **0** |
| conflitos escondidos para obter `PASS` | **0** |
| runtime alterado | **0** |

**Três das sete não viraram lei nova**, e isso é o resultado que se queria: a Bíblia já
respondia. Criar lei onde já havia lei seria a segunda verdade que ela própria proíbe.

---

# F · UM VERMELHO HERDADO — MEDIDO, NÃO CAUSADO PELA INTEGRAÇÃO

`py medidas/padrao_da_coleta.py` devolve **`FAIL`** na árvore integrada:

```
COLETOR_CARIMBA_A_DATA          faltam hoje 28   chao 26   PIOROU
COLETOR_SEPARA_A_FONTE_DO_FATO  faltam hoje 21   chao 20   PIOROU
COLETOR_REGISTA_O_QUE_DESCARTOU faltam hoje 32   chao 30   PIOROU
     mudou: coleta/executor_texto_de_pdf.py, coleta/golden_path_pdf.py
```

## Não foi a integração. Foi medido no ramo da engenharia sozinho

Um *worktree* destacado em `a32799c`, **sem nada desta missão**, devolve
**exatamente os mesmos três números**. O chão (`26 · 20 · 30`) é idêntico nos dois ramos e
foi fixado **antes** de os dois ficheiros novos existirem — ninguém o subiu depois de os
criar.

> **A engenharia entregou `a32799c` com `PADRAO_DA_COLETA=FAIL`.** A integração herdou o
> vermelho; não o produziu.

## E o vermelho é verdadeiro — por isso o chão NÃO foi subido

A tentação era correr `--fixar`: o próprio portão o sugere, e a casa autoriza *«se a mudança
for deliberada e justificada»*. **Não foi feito**, e o motivo é medido.

A régua procura o carimbo pelo **texto do ficheiro**, e os dois novos delegam ao contrato
(`import artefato as art`) — o que parecia falso positivo. Mas ao abrir as 43 fichas:

| campo | nas 43 fichas derivadas |
|---|---|
| `DERIVED_AT` | ✅ hora real, medida |
| `ERROR` | ✅ vazio nas 43 |
| `COLLECTED_AT` | ⚠️ **`NAO SEI` nas 43** |
| `SOURCE_LOCATION` | ⚠️ **`NAO SEI` nas 43** |

**A dívida existe de verdade.** O artefato bruto não recebe `SOURCE_LOCATION` do registo da
fonte, e o derivado herda o `NAO SEI` do pai. Subir o chão congelaria essa dívida como
normal — e o portão existe exatamente para impedir isso.

> **Um portão que reprova por um motivo verdadeiro não se desliga; paga-se o que ele cobra.**

**Registrado como gap `G-36`. Não corrigido:** é runtime de coleta, fora do escopo desta
missão. E `COLLECTED_AT` num derivado provavelmente quer `NAO_SE_APLICA` e não `NAO SEI`
(COL-LAW-035) — o que reforça que a correção é de contrato, não de número.

---

# E · O QUE ESTA MISSÃO NÃO FEZ

Nenhum dado movido · nenhum byte migrado · nenhuma tabela criada · Supabase intocado ·
bucket não usado · `italy_recurrent_collect.mjs` não alterado · histórico do Git não
reescrito · nenhum extrator de data · nenhum `claim` extraído · nenhuma ferramenta instalada
· orquestrador não ligado · nenhum store novo · nenhum deploy.

**Gaps preservados e não executados:** `P-011` · `G-02` · `G-22` · `G-26` · `G-30` ·
`G-34` · `G-35`.
