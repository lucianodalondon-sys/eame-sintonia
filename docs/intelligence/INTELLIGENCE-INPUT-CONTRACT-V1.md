# CONTRATO — O QUE ENTRA NA INTELLIGENCE, E O QUE SAI

> **Nada aqui é novo.** Este documento não cria objeto, não cria identidade e
> não cria lei. Ele **nomeia o que já existe** e diz de quem é cada coisa,
> porque as duas matérias-primas passaram a viver na mesma árvore e a partir de
> agora dá para as confundir.

```
CASA        docs/intelligence/
MEDIDO EM   2026-09-15 · reconciliação da linha canónica da Intelligence
CONTRA      claude/it-trunk-v1 @ 43553a65
LEIS        COL-LAW-043 (fronteira) · INT-LAW-031 (identidade)
            INT-LAW-053 (estados) · INT-LAW-112 (NÃO SEI)
```

---

## AS DUAS ENTRADAS, E POR QUE NÃO SE MISTURAM

```
ENTRADA A   MATERIAL ADMITIDO      alguém observou            dono: COLLECTION
ENTRADA B   REFERÊNCIA FACTUAL     é oficialmente verdadeiro  dono: referencia/
```

A diferença não é de qualidade — é de **natureza**. O material admitido diz
*«a ARIF relatou peronospora em Verona a 12 de Maio»*. A referência diz *«o
produto X está autorizado para videira contra peronospora»*. Uma é um
acontecimento observado; a outra é um facto de catálogo e de registo.

```
QUEM MISTURA AS DUAS PASSA A PODER RESPONDER «HA PRESSAO DE DOENCA» COM UMA
TABELA DE PRODUTOS AUTORIZADOS — QUE NAO OBSERVOU NADA.
```

---

## ENTRADA A — MATERIAL ADMITIDO

| | |
|---|---|
| **o que é** | uma unidade `READY` pousada na Sala de Espera |
| **quem a produz** | `admissao/admissao.py::pronto_para_inteligencia()` |
| **onde pousa** | `admissao/sala_de_espera.py` |
| **o contrato** | `CAMPOS_READY` — **19 campos**, `COL-LAW-043` |
| **a cópia da Intelligence** | `provas/espinha_da_intelligence.py::CAMPOS_DO_READY` |
| **a Intelligence pode** | LER |
| **a Intelligence não pode** | escrever, completar, inventar, admitir |

### Os 19 campos

```
ESTADO · ITEM_ID · RAW_OBSERVATION_ID · UNIVERSO · ESTAGIO · TEXTO
SOURCE_ID · SOURCE_LOCATION · FACT_LOCATION · FACT_TIME
FACT_TIME_BASIS · FACT_LOCATION_BASIS · PUBLISHED_AT · OBSERVED_AT
SOURCE_DECLARED_EVIDENCE_CLASS · FATO
CAPTURED_AT · CORRIDA · ADMITIDO_POR
```

**Eram 12.** `C-COL-PRESERVE-FACTS-V1` acrescentou sete — `ESTAGIO`,
`PUBLISHED_AT`, `OBSERVED_AT`, `FACT_TIME_BASIS`, `FACT_LOCATION_BASIS`,
`SOURCE_DECLARED_EVIDENCE_CLASS`, `FATO`. **Nenhum dos doze antigos
desapareceu:** a fronteira cresceu, não se deslocou.

A cópia declarada da Intelligence é deliberada e continua a ser uma cópia:
importar a Collection tornaria a espinha dependente de um runtime que ela não
pode tocar. Quando a fronteira mudar outra vez,
`tests/test_atomicidade_da_intelligence.py` reprova — que é o trabalho dela.

### ⚠️ O quase-homónimo

`SOURCE_DECLARED_EVIDENCE_CLASS` **não é** `EVIDENCE_SPECIES`.

```
DECLARADO PELA FONTE != MEDIDO NO DOCUMENTO.
```

O primeiro é texto livre e é a expectativa de **quem publica** sobre o que
costuma publicar — pode trazer duas espécies de uma vez
(`OBSERVED_FIELD_SIGNAL + TECHNICAL_GUIDELINE`). O segundo seria a espécie
**deste item**, uma só, do vocabulário fechado `ESPECIES_DE_EVIDENCIA`.

Lê-los como o mesmo campo faria um boletim agroclimático da ARPAV valer por
relato de campo — a confusão exacta que `AGROCLIMATIC_NAO_PROVA` existe para
impedir. **O bloqueio G0 continua de pé, e por medida.**

### O que ainda NÃO atravessa

```
EVIDENCE_SPECIES · SUBJECT_ID · METHOD · UNIT · SCALE
DENOMINATOR · TARGET_POPULATION · PPP_USE
```

Oito campos, **zero atravessam**. É o que impede, hoje, ligar um item da Sala a
um produto da referência: sem `SUBJECT_ID` (EPPO, CAS, número de registo), a
ligação seria palpite.

---

## ENTRADA B — REFERÊNCIA FACTUAL (ADAMA)

| | |
|---|---|
| **casa** | `referencia/adama/` |
| **quem a constrói** | `fontes/adama_referencia.py` |
| **contrato do dono** | `referencia/adama/CONTRATO-ADAMA-REFERENCE.md` |
| **a prova de consumo** | `provas/consumo_da_referencia_adama.py` |
| **a Intelligence pode** | LER e CITAR |
| **a Intelligence não pode** | copiar, escrever, cunhar `ADAMA_PRODUCT_ID` |

| ficheiro que manda | chave | linhas |
|---|---|---:|
| `PRODUCT-MASTER.json` | `ADAMA_PRODUCT_ID` | 51 |
| `PORTFOLIO.json` | `ADAMA_PRODUCT_ID` | 51 |
| `REGISTRATIONS.json` | `REGISTRATION_NUMBER` | 602 |
| `LABEL-DOCUMENTS.json` | `DOCUMENT_ID` | 141 |
| `AUTHORIZED-USES.json` | `USE_ID` | 2.030 |
| `ACTIVE-INGREDIENTS.json` | `ACTIVE_INGREDIENT_ID` | 122 |
| `PRODUCT-ACTIVE-INGREDIENTS.json` | `RELATION_ID` | 203 |
| `SNAPSHOTS.json` | `SNAPSHOT_ID` | 3 |
| `SOURCE-ID-MAP.json` | `LEGACY_SOURCE_ID` | 2 |

Contado, não citado: `COUNT` de cada ficheiro é conferido contra as linhas em
`tests/test_consumo_da_referencia_adama.py`.

### A identidade tem um dono, e não é esta casa

`ADAMA_PRODUCT_ID` é emitido em série e **append-only** pelo construtor da
referência. A Intelligence cita-o. A `INT-LAW-031` já dizia isto antes de
existir referência para citar:

```
A INTELLIGENCE NAO CUNHA IDENTIDADE UPSTREAM.
```

O teste que a impõe não lê comentários: percorre a árvore sintáctica dos
módulos declarados da Intelligence à procura de escrita real — `open(w)`,
`write_text`, `json.dump` — sobre `referencia/adama/`.

⚠️ **`provas/` não é só da Intelligence.** `red_team_adama_referencia.py` mora
lá e escreve na referência **por direito**: é o red team do DONO, que muta o
ficheiro para provar que a suite apanha a mutação. Por isso a lista de módulos
da Intelligence é declarada, e não varrida por pasta.

### O NÃO SEI deles continua NÃO SEI

```
UNKNOWN   ·  MULTIPLE  ·  NAO SEI
```

- **560** autorizações escrevem `ADAMA_PRODUCT_ID: UNKNOWN` — não têm produto
  de catálogo, e o palpite fica por fazer;
- o registo `017995` escreve `MULTIPLE` — uma autorização vendida sob dois
  nomes. **Fundi-los apagaria um produto;**
- `CURRENTLY_MARKETABLE` é `UNKNOWN` nas **602**. Derivá-lo de `ADMIN_ACTIVE`
  seria inventar.

A `INT-LAW-112` aplica-se a estes três exactamente como aos campos da Sala:
**não viram FALSO, e não viram AUSÊNCIA.**

---

## A SAÍDA — OS NOMES CANÓNICOS QUE JÁ EXISTEM

Nenhum nome novo foi criado. Estes são os que `provas/espinha_da_intelligence.py`
e `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json` já definem:

```
SINAL        SIGNAL_ID       nasce de UM item admitido, por G1
CRUZAMENTO   CROSSING_ID     junta sinais, por G2 — e conta origens
                             INDEPENDENTES, não só totais
HIPOTESE     HYPOTHESIS_ID   = CANDIDATE_FINDING = ANALYTIC_HYPOTHESIS
                             (três nomes, um objeto — e é deliberado)
ACHADO       FINDING_ID      só nasce de hipótese promovida por um portão
```

E os estados da corrida, da `INT-LAW-053`:

```
NOT_RUN · RUNNING · DONE · EMPTY_RESULT · NO_FINDING · ERROR · REUSED
```

```
NOT_RUN != ERROR != EMPTY_RESULT != NO_FINDING != REUSED.
COMPRIMI-LOS PERDE A UNICA INFORMACAO QUE DISTINGUE
«NAO CORRI» DE «CORRI E NAO ACHEI».
```

### ⚠️ *Evidence of capability* não tem objeto canónico

O enunciado da missão pede `finding / crossing / evidence of capability`. Os
dois primeiros existem, com este nome, há muito. **O terceiro não existe como
objeto** — «capability» aparece na Bíblia e no backlog como *conceito*
(`MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`, `BACKLOG-OBRIGATORIO.md`), nunca como
coisa emitida, com id, estado e história.

Fica escrito como **falta nomeada**, e não inventado aqui. Criar-lhe um id
nesta missão seria cunhar um objeto sem dono declarado — que é a mesma avaria
que este documento existe para impedir, virada para dentro.

---

## O QUE ESTE CONTRATO **NÃO** DIZ

- **não diz** que o cruzamento item × produto já é possível — não é, falta
  `SUBJECT_ID`, e está medido em `provas/consumo_da_referencia_adama.py`;
- **não diz** que a Intelligence já corre sobre a Sala real em produção — o que
  existe é `motor/corrida_da_inteligencia.py`, uma admissão analítica mínima;
- **não diz** que os sete campos novos da fronteira vêm preenchidos. Um campo
  que passou a existir não é um campo que passou a ter valor.
