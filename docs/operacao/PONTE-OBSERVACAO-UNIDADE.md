# A PONTE OBSERVAÇÃO → UNIDADE — primeiro slice, `SOURCE_DOCUMENT`

**C-PLAN-A5.5 · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero migration, zero tabela, zero
> `preservar_documento.py`, zero registo, zero T-32, zero Admission, zero READY, zero
> contrato de fonte, zero System Map, zero Bíblia.

```
LOCAL_HEAD = REMOTE_HEAD = c5f75667d693df0ad81f54c9f50b1c754eb16e92
WORKTREE   = limpa   ·   DIVERGENCE = 0
```

---

## 1 · OS DOIS LADOS, MEDIDOS

### O que sai do coletor

```
OBSERVATION_PRODUCER    coleta/italy_pilot_collect.mjs
OBSERVATION_OUTPUT_SHAPE  uma linha NDJSON por observação, 26 chaves,
                          em data/collection-ledger/italy/observations.ndjson

BYTES · CADENCE_STATE · CAPTURED_AT · COLLECTION_RUN_STARTED_AT · DECLARED_FREQUENCY
DISCOVERY_DEGRADED · DOCUMENT_ID · DOCUMENT_VERSION_ID · EXPECTED_NEXT_UPDATE · FACT_TIME
HEALTH_STATE · MIME_ASSINATURA · OBSERVATION_RESULT · OBSERVED_FREQUENCY · PARSE_ERROR
PONTOS · RAW_OBJECT_CREATED · RAW_PATH · RAW_PRESERVED_BEFORE_PARSE · RAW_SHA256
RUN_ID · SOURCE_DATE · SOURCE_DATE_ISO · SOURCE_ID · SOURCE_URL · parse
```

### O que o T-32 exige

```
T32_REQUIRED_INPUT_SHAPE   dict de 10 chaves
  obrigatórias à entrada   RAW_ASSET_ID · PDF
  opcionais                SOURCE_ID · ROUTE_CLASS_ID · CAPTURED_AT · URL · TIPO · RULE_VERSION
  postas pelo próprio T-32 TEXTO · CONTENT_ID · DERIVED_STORAGE_PATH
```

### O confronto

```
FIELDS_ALREADY_COMMON      SOURCE_ID · CAPTURED_AT · URL/SOURCE_URL
FIELDS_MISSING             RAW_OBSERVATION_ID · RESOLVED_STRUCTURED_TARGET
                           DOCUMENT_ID e DOCUMENT_VERSION_ID (o T-32 não os pede — e devia)
FIELDS_OBSOLETE_IN_T32     PDF · TEXTO · CONTENT_ID · TIPO
                           existem porque o T-32 nasceu específico de PDF+canal (A2/A3)
```

---

## 2 · O BLOQUEIO DURO — e ele já tinha nome nesta casa

> ## `RAW_OBSERVATION_ID` NÃO EXISTE PARA A COLETA ITALIANA.
> ## E NÃO É POR ESQUECIMENTO: **ELA NUNCA PASSA PELA PORTA CANÓNICA.**

A cadeia, medida elo a elo:

```
coleta/italy_pilot_collect.mjs  não menciona raw_asset, preservar nem collection_run
                                (0 ocorrências)
pedido/receitas.py::EXECUTORES  NÃO contém o coletor italiano  (0 ocorrências)
orquestrador.py:117             é o ÚNICO chamador de ing.receber em runtime
guarda/preservar_coleta.py:410  é quem escreve `insert into public.raw_asset`
```

O orquestrador só corre o que o registo de executores conhece. O coletor italiano não está
lá. Logo `ing.receber` nunca vê aquela colheita, logo `preservar_coleta` nunca escreve a
linha, logo **não há `raw_asset_id` para nenhuma das 144 observações.**

E isto **não é achado novo** — a casa mediu-o e deu-lhe título próprio:

> *«OS BYTES ITALIANOS ESTÃO NO ARMAZÉM. 195 objetos · 80,7 MB.*
> *A MEMÓRIA OPERACIONAL DELES NÃO EXISTE. **`raw_asset` IT = 0 · `collection_run` IT = 0**.*
> *Um armazém cheio, com o livro de entrada em branco.»*
> — [`ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md`](ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md)

```
BRIDGE_INPUT_NOT_AVAILABLE_YET = RAW_OBSERVATION_ID
```

**E não se inventa o ID.** Ele nasce de uma linha escrita pelo dono do RAW, e essa linha
ainda não foi escrita.

### Mas ele é obtível — e o caminho já existe

O recibo de `preservar()` devolve caminhos e contagens (`CONFERIDOS`, `REUSED_METADATA`,
`LINHAS_OBSERVADAS_NO_BANCO`) e **não** os ids por objecto. A porta de leitura, essa, já
existe e devolve a linha inteira:

```python
# guarda/memoria_descartavel.py:196
def objeto_em(self, storage_path):
    cur = self.con.execute("select * from raw_asset where storage_path = ?", …)
```

`select *` inclui o `id`. Ou seja: **o `RAW_OBSERVATION_ID` obtém-se por leitura de volta**,
que é exactamente a lei que o dono do RAW já impõe — *«`LINHAS_OBSERVADAS` VEM DE UMA
LEITURA. SEMPRE.»* A ponte lê; não deduz.

---

## 3 · QUEM MATERIALIZA A UNIDADE

A pergunta parte-se em duas, e a medição responde a ambas:

```
quem sabe a IDENTIDADE DOCUMENTAL?   só o coletor — foi ele que correu documentIdDe()
quem sabe o RAW_OBSERVATION_ID?      só quem preservou — a linha nasce lá
```

**Nenhum dos dois tem as duas coisas.** Por isso a ponte não é «o executor a acrescentar um
campo»: é o sítio onde as duas metades se encontram — e esse sítio já existe.

```
SOURCE_DOCUMENT_UNIT_MATERIALIZER_OWNER = coleta/ingresso.py — a porta de entrada
BRIDGE_LOCATION_TARGET = coleta/ingresso.py :: para_o_dono_do_estruturado()
                         função nova num dono existente · NÃO módulo novo
```

**Porque é ali, e é medido:** `ingresso.py` já é o único ponto que, num só momento, tem a
observação original **e** o resultado da preservação. E já faz uma tradução exactamente
desta forma — o próprio ficheiro explica porquê:

> *«A casa tem DUAS linguas de artefato, e as duas estao certas … `preservar()` nunca aceitou
> um `Artefato`: ele pede `COUNTRY`, `SOURCE_SLUG`, `ARTIFACT_KIND` … Nada no repositorio
> ligava as duas.* ***DOIS CONTRATOS CERTOS E NENHUMA PONTE SAO DOIS CONTRATOS QUE NAO SE
> USAM.»***
> — `coleta/ingresso.py:170-186`, sobre `para_o_dono_do_raw`

`para_o_dono_do_raw` traduz para a língua do RAW. `para_o_dono_do_estruturado` traduz para a
língua do STRUCTURED. **Mesma forma, mesmo dono, segunda saída.**

### E isto não faz da porta um juiz

A guarda que protege este ficheiro continua verde, e é literal:

```python
# provas/o_encanamento_tem_uma_porta.py — P4 · A PORTA NAO JULGA
caso("P4_a_porta_nao_decide_admissao",
     not re.search(r"\bdecidir\s*\(", c_ing) and "pronto_para_inteligencia" not in c_ing)
```

A ponte **transporta** um alvo que a observação já traz. Não chama `decidir()`, não constrói
READY, não escolhe conceito, não persiste `source_document`, não escolhe dono, não recoleta
e não inventa identidade.

---

## 4 · ONDE NASCE O `RESOLVED_STRUCTURED_TARGET`

```
RESOLVED_TARGET_WRITE_POINT = no COLETOR, no mesmo acto em que ele constrói
                              DOCUMENT_ID e DOCUMENT_VERSION_ID
                              coleta/italy_pilot_collect.mjs:308-334
                              gravado como campo da OBSERVAÇÃO
```

É o que a A5.3 fechou — *o executor carimba ao materializar, antes de entregar* — e a
medição diz que aquele é o único instante em que o coletor sabe que produziu um documento
identificado. **A ponte transporta; nunca carimba.**

```
observações com RESOLVED_STRUCTURED_TARGET hoje:  0 / 144
```

O campo não existe no livro. É trabalho, e está na lista de bloqueios.

---

## 5 · O CONTRATO DA PONTE

```
BRIDGE_INPUT_MINIMUM_CONTRACT

  da OBSERVAÇÃO     SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID · RUN_ID
                    RESOLVED_STRUCTURED_TARGET
  da PRESERVAÇÃO    a linha de raw_asset, lida de volta  →  o seu `id`
```

```
BRIDGE_OUTPUT_MINIMUM_CONTRACT   a unidade que o T-32 recebe

  SOURCE_ID                    da observação
  DOCUMENT_ID                  da observação
  DOCUMENT_VERSION_ID          da observação
  RAW_OBSERVATION_ID           da linha preservada        ← a testemunha (A5.1)
  RUN_ID                       da observação
  RESOLVED_STRUCTURED_TARGET   transportado               ← SOURCE_DOCUMENT
  LAST_REAL_STAGE              'RAW'                      ← A4
  LAST_REAL_ARTIFACT_ID        = RAW_OBSERVATION_ID
```

**Oito campos. E o que ficou de fora tem razão medida:**

| campo | fora, porquê |
|---|---|
| `PDF` | o T-32 indexa-o hoje, e é herança de ele ter nascido específico de PDF. **Não é semântica de `SOURCE_DOCUMENT`** |
| `TEXTO` | a A5.1 fechou `TEXT_STORAGE_STRATEGY = REFERENCE`. A ponte **não fabrica texto** |
| `MIME_ASSINATURA` | decide qual derivação corre depois; não define o conceito (§6) |
| `SOURCE_CONTRACT_VERSION` | **junta-se pelo `RUN_ID`** — medido: 6/6 corridas trazem-no no recibo, 0/144 observações o repetem. Copiá-lo para a unidade criaria segunda autoridade sobre a versão |
| `CONTENT_ID` · `TIPO` · `ROUTE_CLASS_ID` | do vocabulário social/PDF do T-32, não do documento |

---

## 6 · PDF NÃO É IDENTIDADE

```
SOURCE_DOCUMENT_UNIT_REQUIRES_PDF = NO
```

Medido nas 7 fontes que a A5.2 autorizou: **4 entregam PDF, 2 entregam HTML, 1 entrega
CSV** — e as sete produzem `DOCUMENT_ID` e `DOCUMENT_VERSION_ID` do mesmo jeito. A identidade
fechada pela A5.1 não tem MIME dentro dela.

> O tipo físico decide **qual transformação será chamada a seguir**. Nunca decide **o que a
> unidade é**. Exigir PDF faria um boletim em HTML deixar de ser um documento por causa do
> seu `content-type`.

```
SOURCE_DOCUMENT_UNIT_CAN_START_FROM_RAW     = YES  — e na ponte é sempre assim
SOURCE_DOCUMENT_UNIT_CAN_START_FROM_DERIVED = YES  — depois de a etapa DERIVED correr,
                                                     quando LAST_REAL_STAGE avança
```

**Nenhum estado novo é inventado para a derivação.** A unidade não carrega
`DERIVATION_REQUIRED`: ela carrega `LAST_REAL_STAGE`, e o estado da etapa DERIVED vive onde
já vive — em `etapa_da_corrida.estado`, dentro do vocabulário de sete valores de
`leis/telemetria.py`, incluindo `NOT_APPLICABLE`. A A2 e a A3 fecharam isso e **não são
reabertas**.

---

## 7 · A UNIDADE É TRANSITÓRIA

```
UNIT_IS_PERSISTED = NO
UNIT_MATERIALIZATION_IDEMPOTENCY_RULE
    a ponte é uma FUNÇÃO DETERMINÍSTICA e SEM EFEITO:
    mesma observação + mesma linha de raw_asset  →  mesma unidade, sempre.
    Não escreve, não numera, não guarda estado. Chamá-la duas vezes não cria nada
    duas vezes porque não cria nada.
```

A idempotência que **importa** é a de quem persiste, e ela já está fechada: a chave natural
`UNIQUE (source_id, document_id, document_version_id)` do `source_document` (A5.1). **A ponte
não é dona dessa idempotência e não deve fingir que é** — nem se cria tabela de unidade.

---

## 8 · A FRONTEIRA, EM FORMA SIMPLES

```
ANTES DA PONTE     uma observação no livro  +  uma linha de raw_asset acabada de escrever
DEPOIS DA PONTE    uma unidade SOURCE_DOCUMENT, em memória, com 8 campos
COMPONENTE FUTURO  coleta/ingresso.py :: para_o_dono_do_estruturado()
QUEM CHAMA         coleta/ingresso.py :: receber(), logo após preservar() devolver
QUEM RECEBE        T-32
```

---

## 9 · A TESTEMUNHA REAL

```
OBSERVAÇÃO  (data/collection-ledger/italy/observations.ndjson)
  RUN_ID               PILOT_RUN_20260907153737_4c34b3
  SOURCE_ID            IT-T2-002
  DOCUMENT_ID          ARPAV:Z01:20260903160930
  DOCUMENT_VERSION_ID  v1_f88c89d73d6a
  RAW_SHA256           f88c89d73d6a132a1c1ec6e87aadd893dd1f1028425dcf0fc4ffb37ab29170af
  BYTES 463630 · MIME PDF · CAPTURED_AT 2026-09-07T15:37:42.531Z
  RAW_PATH             data/collection-store/italy/IT-T2-002/ARPAV_Z01_20260903160930/…

        ↓ campos usados pela ponte: SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID · RUN_ID
        ↓ mais o id lido de volta da linha preservada
        ↓ mais o alvo que o coletor carimbou

UNIDADE SOURCE_DOCUMENT  (em memória, nada persistido)
  SOURCE_ID                    IT-T2-002
  DOCUMENT_ID                  ARPAV:Z01:20260903160930
  DOCUMENT_VERSION_ID          v1_f88c89d73d6a
  RAW_OBSERVATION_ID           <id da linha de raw_asset>      ← HOJE NÃO EXISTE (§2)
  RUN_ID                       PILOT_RUN_20260907153737_4c34b3
  RESOLVED_STRUCTURED_TARGET   SOURCE_DOCUMENT                 ← HOJE NÃO EXISTE (§4)
  LAST_REAL_STAGE              RAW
  LAST_REAL_ARTIFACT_ID        = RAW_OBSERVATION_ID

        ↓

T-32   confere SOURCE_DOCUMENT ∈ ALLOWED_STRUCTURED_TARGETS de IT-T2-002
       pergunta ao T-06 quem recebe
       (não corre nesta missão)
```

**Dois dos oito campos ainda não existem, e estão ambos marcados.** O desenho não os esconde
para parecer completo.

---

## 10 · BLOQUEIOS

```
BLOCKERS_TO_IMPLEMENT_BRIDGE

  B1  a coleta italiana nunca passa pela porta canónica: não está em EXECUTORES,
      o orquestrador nunca a corre, ing.receber nunca a vê, e por isso
      raw_asset IT = 0.  Já documentado em ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md
  B2  a observação não carrega RESOLVED_STRUCTURED_TARGET  (0/144)
  B3  dois armazéns com dois esquemas de caminho: o coletor guarda em
      data/collection-store/, o dono do RAW endereça o bucket por
      PAIS/FONTE/TIPO/sha16-nativo-nome
  B4  o recibo de preservar() não expõe os ids por objecto — a leitura de volta
      existe (objeto_em), mas a ponte tem de a fazer explicitamente

BLOCKERS_AFTER_BRIDGE

  C1  public.source_document não existe                       (A5.1)
  C2  guarda/preservar_documento.py não existe                (A5.1/A5.4)
  C3  o registo CONCEITO→DONO não existe                      (A5.4)
  C4  nenhum contrato declara ALLOWED_STRUCTURED_TARGETS      (A5.2)
  C5  o T-32 ainda indexa unidade['PDF'] e ['TEXTO'], fixa edge_from='DERIVED'
      e chama persistir_video sempre                          (A2/A3)

NOT_BLOCKING_FIRST_SLICE

  transcrição por máquina · censo da migration 021 · donos sociais ·
  as 1045 linhas do SIAS · candidatos AGROCLIMATIC_MEASUREMENT e FIELD_MONITORING_POINT
```

**O `B1` é o maior, e é o mais antigo.** Ele não nasceu desta série: estava medido e
publicado antes dela.

---

## 11 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `c5f75667d693df0ad81f54c9f50b1c754eb16e92` |
| **D** `WORKTREE` | limpa |
| **E** `OBSERVATION_PRODUCER` | `coleta/italy_pilot_collect.mjs` |
| **F** `OBSERVATION_OUTPUT_SHAPE` | linha NDJSON, 26 chaves, no livro |
| **G** `SOURCE_DOCUMENT_UNIT_MATERIALIZER_OWNER` | `coleta/ingresso.py` — a porta de entrada |
| **H** `BRIDGE_LOCATION_TARGET` | `ingresso.py::para_o_dono_do_estruturado()` — função nova, dono existente |
| **I** `BRIDGE_INPUT_MINIMUM_CONTRACT` | 5 campos da observação + o `id` lido da linha preservada |
| **J** `BRIDGE_OUTPUT_MINIMUM_CONTRACT` | 8 campos · sem `PDF`, sem `TEXTO`, sem `MIME` |
| **K** `RESOLVED_TARGET_WRITE_POINT` | no coletor, no acto do `DOCUMENT_ID` — a ponte transporta |
| **L** `SOURCE_DOCUMENT_UNIT_REQUIRES_PDF` | **NO** — 4 PDF · 2 HTML · 1 CSV entre as 7 autorizadas |
| **M** `CAN_START_FROM_RAW` | **YES** |
| **N** `CAN_START_FROM_DERIVED` | **YES**, depois da etapa DERIVED — não na ponte |
| **O** `RAW_OBSERVATION_ID_AVAILABLE_AT_BRIDGE` | **NO** — `raw_asset` IT = 0 |
| **P** `RUN_ID_AVAILABLE_AT_BRIDGE` | **YES** — 144/144 |
| **Q** `SOURCE_CONTRACT_VERSION_AVAILABLE_AT_BRIDGE` | **YES por junção via `RUN_ID`** — 6/6 corridas; 0/144 observações |
| **R** `UNIT_IS_PERSISTED` | **NO** — objecto transitório |
| **S** `UNIT_MATERIALIZATION_IDEMPOTENCY_RULE` | função determinística e sem efeito; a idempotência real é a chave natural do writer |
| **T** `REAL_EXAMPLE_SOURCE_ID` | `IT-T2-002` · `ARPAV:Z01:20260903160930` · `v1_f88c89d73d6a` |
| **U** `BLOCKERS_TO_IMPLEMENT_BRIDGE` | **4** — B1 a B4 |
| **V** `BLOCKERS_AFTER_BRIDGE` | **5** — C1 a C5 |
| **W** `RUNTIME_FILES_CHANGED` | **0** |
| **X** `DATABASE_MUTATIONS` | **0** |
| **Y** `SYSTEM_MAP_CHANGED` | **0** |
| **Z** `UNRESOLVED_CRITICAL_A5_5_QUESTIONS` | **0** |

### O que continua `NÃO SEI` — e nenhum bloqueia o desenho

1. Como a coleta italiana entra no registo de executores (é decisão de orquestração, T-06).
2. Se os dois armazéns se reconciliam ou se um deles passa a ser cache (B3).
3. Se o recibo de `preservar()` passa a expor ids ou se a leitura de volta fica na ponte (B4).

---

## 12 · VEREDITO

```
SOURCE_DOCUMENT_UNIT_MATERIALIZER_OWNER = CLOSED   coleta/ingresso.py
BRIDGE_INPUT_CONTRACT                   = CLOSED   5 + 1
BRIDGE_OUTPUT_CONTRACT                  = CLOSED   8 campos
PDF_DEPENDENCY_REMOVED_FROM_CONCEPT     = CLOSED   NO
RESOLVED_TARGET_WRITE_POINT             = CLOSED   no coletor; a ponte transporta
FIRST_REAL_OBSERVATION_EXAMPLE          = CLOSED   IT-T2-002 · ARPAV:Z01:20260903160930

C-PLAN-A5.5 = PASS
```

O desenho `OBSERVAÇÃO → UNIDADE → T-32` fecha sem adivinhação: sabe-se **quem cria** a
unidade, **que dados usa**, **que objecto entrega** e **onde nasce** o
`RESOLVED_STRUCTURED_TARGET`.

E fica dito, sem enfeite: **dois dos oito campos ainda não existem no dado**, e o maior deles
tem causa antiga e já publicada.

---

## 13 · EM PALAVRAS FÁCEIS

1. **O que é essa ponte?** A peça que pega numa observação já preservada e monta o objecto
   que o T-32 sabe receber. Oito campos, em memória.

2. **Por que não existe hoje?** Porque o coletor fala «observação» e o T-32 fala «unidade»,
   e ninguém traduz. A casa já viveu isto do outro lado e escreveu a frase: dois contratos
   certos e nenhuma ponte são dois contratos que não se usam.

3. **Quem cria a unidade?** A porta de entrada, `coleta/ingresso.py`. É o único sítio que
   tem, ao mesmo tempo, a observação original e a linha que a preservação acabou de escrever.

4. **O que entra nela?** Cinco campos da observação — fonte, documento, versão, corrida e o
   carimbo do tipo — mais o identificador da linha preservada, lido de volta.

5. **O que sai?** Oito campos. Nem PDF, nem texto, nem tipo de ficheiro.

6. **Precisa que seja PDF?** Não. Das sete fontes autorizadas, quatro dão PDF, duas dão HTML
   e uma dá CSV, e todas produzem documento identificado do mesmo jeito.

7. **Ela cria ou copia texto?** Nenhum dos dois. O texto vive onde já vive, e a unidade
   aponta.

8. **Salva alguma coisa no banco?** Nada. É objecto de passagem. Quem guarda é o dono do
   documento, e a repetição é travada pela chave natural dele.

9. **Depois dela o T-32 recebe algo real?** Ainda não. Faltam dois campos no dado: o
   identificador da linha preservada, que não existe porque a coleta italiana nunca passou
   pela porta canónica, e o carimbo do tipo, que o coletor ainda não escreve.

10. **Qual é o próximo passo?** Fazer a coleta italiana passar pela porta canónica, para que
    exista uma linha de `raw_asset` e, com ela, o identificador que falta. É o bloqueio mais
    antigo dos quatro, e é o primeiro.

> **HARD STOP.** Dono, entrada, saída, independência do PDF, ponto de carimbo e exemplo real
> estão fechados. Não se implementa a ponte, não se cria `preservar_documento`, não se altera
> o T-32.
