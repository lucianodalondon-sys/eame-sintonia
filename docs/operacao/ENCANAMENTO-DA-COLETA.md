# ENCANAMENTO DA COLETA — uma porta, uma ordem, um dono por etapa

> Missão **C-PLUMB-1**. Branch `claude/collection-plumbing-canonical-v1`, sobre a
> árvore reconciliada `ded06c28`.
>
> Esta missão não é outro censo. As duas anteriores mediram os cartões e as
> ligações; esta conserta o **encanamento**.

---

## 1 · O QUE ESTAVA ERRADO, MEDIDO E NÃO OPINADO

`leis/artefato.py` — o contrato comum de artefato — abre com esta frase:

> «Hoje cada executor entrega o resultado à sua maneira. Ligar o orquestrador a
> isto obrigaria o cérebro da casa a **adivinhar** o que cada um produziu.»

O contrato foi escrito. **O orquestrador nunca o adotou, e continuou a
adivinhar** — literalmente, em `a_colheita()`:

```python
lista = d if isinstance(d, list) else next(
    (v for v in d.values() if isinstance(v, list) and v
     and isinstance(v[0], dict)), [])
```

«o primeiro campo do ficheiro que seja uma lista de fichas». Qualquer dicionário
encontrado na pasta declarada virava item da coleta e ia **direto à admissão**.

```
ISSO NÃO É UMA PORTA. É UM CHÃO POR ONDE AS COISAS ENTRAM.
```

E a etapa **RAW nunca corria**. Não é suposição: o próprio repositório guardava a
confissão por escrito, num teste que existe para isso —

```
tests/test_preservar_coleta_no_banco.py::test_esta_peca_ainda_nao_tem_caller_real
«Medido: nenhum ficheiro de produção chama preservar().»
```

### O caminho de produção, antes

```
PEDIDO → RECEITA → executor (subprocess) → larga JSON numa pasta
                                              ↓  a_colheita() adivinha
                                          ADMISSÃO
                                              ↓
                                           READY
```

`RAW`, `DERIVED` e `STRUCTURED` existiam, estavam provados contra Postgres, e
**nenhum tinha caller de produção**. A travessia
`DERIVED → STRUCTURED → ADMISSION` (`coleta/rota_forward_documento.atravessar`)
era importada por **ninguém** fora de `provas/` e `tests/`.

---

## 2 · POR QUE NINGUÉM CHAMAVA O DONO DO RAW

Duas razões, as duas estruturais — e nenhuma delas era desleixo.

**A casa tem DUAS línguas de artefato, e as duas estão certas:**

| | |
|---|---|
| `leis/artefato.Artefato` | como o **executor entrega** |
| `guarda/preservar_coleta` | como o **armazém endereça** o byte |

`preservar()` nunca aceitou um `Artefato`: pede `COUNTRY`, `SOURCE_SLUG`,
`ARTIFACT_KIND`, `SOURCE_NATIVE_ID`, `NAME`. **Nada no repositório ligava as
duas.**

```
DOIS CONTRATOS CERTOS E NENHUMA PONTE
SÃO DOIS CONTRATOS QUE NÃO SE USAM.
```

**E a porta do armazém só sabia escrever longe.** Tinha duas implementações: uma
*de mentira*, para provar, e a da Supabase. Preservar exigia **ou fingir, ou ir à
rede** — e por isso nenhum caminho local a chamava.

---

## 3 · O QUE ENTRA

`coleta/ingresso.py` — a porta única, que responde **uma** pergunta:

> posso preservar esta observação como RAW?

e **não** a da admissão, que é outra:

> este objeto pode entrar no universo utilizável?

```
O COLETOR OBSERVA. A PORTA PRESERVA. A ADMISSÃO JULGA.
```

Ela faz a ficha no contrato que já existia, confere com `art.conferir()`, traduz
para a língua do dono do RAW e entrega a `preservar()`. **Nada nela sabe como a
`raw_asset` é por dentro** — e há um portão que o garante.

Mais `guarda/preservar_coleta.ArmazemLocal`: a **terceira** implementação de uma
interface que sempre teve três métodos e só tinha duas casas.

### O que ela nunca inventa

```
FACT_TIME      NÃO SEI     ← não é a hora da colheita
FACT_LOCATION  NÃO SEI     ← não é o país da fonte
```

Enchê-los seria destruir exatamente o que `leis/artefato.py` existe para separar.

---

## 4 · A TRAVESSIA, MEDIDA PELO CAMINHO DE PRODUÇÃO

As mesmas funções que uma corrida real chama — fixture só satisfaz a
precondição.

| caso | resultado |
|---|---|
| item válido | 2 preservados, 2 bytes no armazém |
| proveniência | `SOURCE_ID` · `OBSERVED_AT` · `COLLECTED_AT` · `RUN_ID` · `SHA256` |
| `FACT_TIME` / `FACT_LOCATION` | `NÃO SEI` — não inferidos |
| sem corrida | `INGRESS_SEM_CORRIDA` |
| item vazio | `INGRESS_SEM_CONTEUDO`, e os outros passam |
| **mesma entrada 2×** | mesmos `ARTIFACT_ID`, **2 ficheiros, não 4** |
| `RUN_STATE` | `PARTIAL` — porque o banco **não foi medido** |

`PARTIAL` aqui é a verdade: o dono do RAW recusa dizer `COMPLETE` sem um
`SELECT`.

```
RECUSA NA PORTA ≠ REJEITADO NA ADMISSÃO ≠ ERRO ≠ NÃO CORREU.
```

---

## 5 · O RED TEAM APANHOU DOIS PORTÕES MEUS A MENTIR

Sete ataques. Cinco morderam à primeira; **dois passaram**, e os dois eram
defeito das minhas próprias provas.

| # | ataque | o que aconteceu |
|---|---|---|
| A | coletor preserva por fora | mordeu |
| B | a porta começa a julgar | mordeu |
| **C** | o orquestrador salta a porta | **passou** — o caso procurava o **nome** `pela_entrada`; trocando a **chamada** por `pass`, o `def` continuava lá. **Definir não é chamar.** Passa a procurar a chamada, por AST |
| D | `FACT_TIME` inventado | mordeu |
| E | corrida inventada (`LEGACY-RUN`) | mordeu |
| F | segundo dono do RAW | mordeu |
| **G** | a porta escreve SQL na `raw_asset` | **passou** — o caso lia o código **sem prosa**, e o SQL vive **dentro de uma string**. Aqui a string *é* o risco |

O aperto de G trouxe o problema inverso: passando a ler o ficheiro cru, o caso
acusava o **próprio docstring** da porta, que diz que ela «não sabe como a
`raw_asset` é feita por dentro».

```
UMA FRASE SOBRE UMA TABELA NÃO É UMA ESCRITA NUMA TABELA.
```

O sinal é o **verbo** ao lado do nome. Depois dos dois apertos: **7 de 7 mordem**,
e a árvore limpa continua verde.

---

## 6 · UM IMPORT COM PONTO É UM IMPORT

Ao declarar a porta no mapa, a aresta mais importante desta missão **não
apareceu**. O resolvedor lia só o primeiro segmento de
`from guarda.preservar_coleta import ...`, procurava `guarda.py` — que não existe
— e desistia.

**Medido: 27 imports reais invisíveis.** E não quaisquer uns:

```
coleta/ingresso.py               -> guarda/preservar_coleta.py
coleta/executor_texto_de_pdf.py  -> guarda/preservar_derivado.py
guarda/preservar_derivado.py     -> guarda/preservar_coleta.py
provas/a_rota_m2_atravessa.py    -> guarda/preservar_coleta.py
```

O **dono do RAW** e o **dono do DERIVADO** — as duas peças que mais pareciam
soltas do encanamento — estavam desligadas **no desenho, não no código**. Uma
linha no resolvedor, e **13 arestas reais** voltam ao mapa.

---

## 7 · O TESTE QUE GUARDAVA O BURACO FOI CUMPRIDO, NÃO APAGADO

Ele dizia: «é este teste que segura a honestidade se alguém ligar a peça e
esquecer de atualizar o estado». Alguém ligou a peça — esta missão. Ele muda de
pergunta, e a nova é a que interessa:

> **há um caller, e é a porta canónica?**

```python
assertEqual(chamadores, ["coleta/ingresso.py"])
```

Um segundo chamador de produção seria uma segunda entrada, e é isso que a porta
existe para não haver.

---

## 8 · O QUE CONTINUA ABERTO, E DE QUEM É

| gap | estado |
|---|---|
| `RAW → DERIVED → STRUCTURED` em produção | **`ARCHITECTURE_DECISION_REQUIRED`** — a travessia existe (`rota_forward_documento.atravessar`) e está provada, mas exige **Postgres**. Ligá-la ao caminho por omissão faria toda corrida exigir banco, e isso é decisão de arquitetura, não de encanamento |
| `READY_SEM_CONSUMIDOR` | aberto — pertence à Intelligence futura |
| `SCRAP → INGRESS` | **`HANDOFF_TARGET_PROVED`** — o SCRAP não está nas receitas (`0 menções`), logo o orquestrador não o despacha. A porta está construída e é onde ele encaixa |
| `STRUCTURED_SEM_DONO_LIGADO` | aberto, herdado |
| 3 falhas herdadas da Security | não mascaradas, ver §9 |

---

## 9 · A ENTREGA

```
GIT
  A. BRANCH            claude/collection-plumbing-canonical-v1
  B. BASE_HEAD         ded06c28  (árvore reconciliada, remedida no arranque)
  C. FINAL_HEAD        (o desta entrega)
  D. WORKTREE          isolado
  E. COMMITS           3
  F. PUSHED            SIM · sem force push

OWNERS
  G. REQUEST_OWNER              pedido/pedido.py
  H. ROUTE_OWNER                pedido/receitas.py
  I. ACQUISITION_OWNER          os executores, via subprocess do orquestrador
  J. COLLECTION_INGRESS_OWNER   coleta/ingresso.py            ← NOVO
  K. RAW_OWNER                  guarda/preservar_coleta.py
  L. DERIVED_OWNER              coleta/derivacao_forward.py
  M. STRUCTURED_OWNER           coleta/rota_forward_documento.py
  N. ADMISSION_OWNER            admissao/admissao.py
  O. READY_OWNER                admissao.pronto_para_inteligencia
  P. PIPELINE_TRAVERSAL_OWNER   orquestrador/orquestrador.py (entrada→admissão)
                                rota_forward_documento.atravessar (derived→admissão,
                                exige Postgres — ver §8)

ENTRADAS
  Q. COLLECTOR_CLASSES_FOUND    17 ficheiros em coleta/ que falam com o mundo
  R. CANONICALLY_CONNECTED      4 despachados por receita, e passam pela porta
  S. DIRECTLY_CONNECTED         0
  T. UNWIRED                    13 sem receita (CLI/legado)
  U. LEGACY                     medido no censo anterior, não reaberto
  V. EXPERIMENTAL               Stories — NÃO integrado, de propósito

SCRAP
  W. LOGICAL_COMPONENTS   5, cada um com nome inequívoco:
                          C-SINTONIA-SCRAP (despachador aquisição)
                          C-SCRAP-ROTA (despachador rota/sessão)
                          C-SCRAP-SOCIAL (executor)
                          C-SCRAP-LEIS (taxonomia da falha)
                          C-SCRAP-GUARDA (credencial e sessão)
  X. SCRAP_OWNER          C-SINTONIA-SCRAP
  Y. OUTPUT_CONTRACT      coleta/social_envelope.py
  Z. TO_INGRESS_PROVED    NÃO — HANDOFF_TARGET_PROVED

ETAPAS                         DECLARADO  OBSERVADO  PROVADO
  AA. INGRESS_TO_RAW              SIM        SIM       SIM
  AB. RAW_TO_DERIVED              SIM        NÃO       SIM (prova M2)
  AC. DERIVED_TO_STRUCTURED       SIM        NÃO       SIM (prova M2)
  AD. STRUCTURED_TO_ADMISSION     SIM        NÃO       SIM (prova M2)
  AE. ADMISSION_TO_READY          SIM        SIM       SIM

READY
  AF. CONTRACT                 existe · 11 campos, COL-LAW-043
  AG. PRODUCTION_PRODUCERS     1  orquestrador/orquestrador.py:145
  AH. CLI_PRODUCERS            1  admissao/admissao.py (demo do módulo)
  AI. TEST_PRODUCERS           4  provas/ e tests/
  AJ. PRODUCTION_CONSUMERS     0
  AK. IS_CURRENT_TERMINAL      SIM — e está correto que seja

BYPASSES
  AL. INICIAIS                 1  (colheita → admissão, sem RAW)
  AM..AQ. COLETOR → DERIVED/STRUCTURED/ADMISSION/READY/INTELLIGENCE   0 · 0 · 0 · 0 · 0
  AR..AU. RAW→ADMISSION · RAW→READY · DERIVED→READY · STRUCTURED→INTELLIGENCE
                               0 · 0 · 0 · 0
  AV. REAIS NÃO AUTORIZADOS FINAIS                                    0

INTELLIGENCE
  AW. EDGES_INITIAL   6
  AX..BC. DATA 0 · CODE 1 · RULE 1 · PROOF 0 · CONTROL 1 · READ 3 · STALE 0
  BD. DATA_EDGES_FINAL                                                0

DUPLICAÇÃO
  BE. RAW_WRITERS          1  (coleta/ingresso.py)
  BF. DERIVED_WRITERS      1
  BG. STRUCTURED_WRITERS   1
  BH. ADMISSION_CALLERS    1 em produção (orquestrador)
  BI. READY_PRODUCERS      1 em produção
  BJ. DUPLICATE_CANONICAL_OWNERS                                      0

IDEMPOTÊNCIA (mesma entrada, duas corridas)
  BK/BL. RAW              2 aceites / 2 aceites · 2 ficheiros no armazém (não 4)
  BM/BN. DERIVED          não corre sem banco — NÃO MEDIDO, e não se escreve 0
  BO/BP. STRUCTURED       idem
  BQ/BR. ADMISSION        idem
  BS/BT. READY            idem
  BU. UNEXPECTED_DUPLICATES                                           0

PROVENIÊNCIA
  BV. SOURCE_PRESERVED           SIM
  BW. OBSERVED_TIME_PRESERVED    SIM
  BX. COLLECTED_TIME_PRESERVED   SIM
  BY. RUN_ID_PRESERVED           SIM
  BZ. FACT_TIME_INFERRED         NÃO
  CA. FACT_LOCATION_INFERRED     NÃO

MAPA
  CB. MAIN_OPERATIONAL_FLOW   BÍBLIA · ENTRADA · PEDIDO · ORQUESTRADOR · CANDIDATAS ·
                              FONTES · EXECUÇÃO · VEÍCULOS · FERRAMENTAS · AÇÕES ·
                              GUARDA · REGRAS · ADMISSÃO · READY
  CC..CG. arestas por categoria — DATA/CONTROL/CODE/RULE/PROOF todas tipadas
  CH. UNEXPLAINED_OPERATIONAL_EDGES     0   (UNKNOWN = 0 de 601)
  CI. UNEXPLAINED_OPERATIONAL_CARDS     0
  CJ. SYSTEM_MAP_CHECK                  PASS

SEGURANÇA
  CK. SECURITY_RATCHET          PASSA
  CL. INHERITED_FAILURES        3  (trava da inteligência ×2, contagem de testes)
  CM. NEW_SECURITY_FAILURES     0

TESTES
  CN/CO/CP. BASE   72 executados · 63 PASS · 9 FAIL   (ded06c28)
  CQ/CR/CS. FINAL  72 executados · 63 PASS · 9 FAIL
  CT. NEW_FAILURES                                     0

RED TEAM
  CU..DC.  7 ataques · 7 morderam · 2 exigiram apertar os meus próprios portões

FRONTEIRAS
  DD. STORIES_MERGED                NÃO
  DE. INTELLIGENCE_CHANGED          NÃO
  DF. PORTAL_CHANGED                NÃO
  DG. SECURITY_ARCHITECTURE_CHANGED NÃO
  DH. PRODUCTION_DB_MUTATED         NÃO
```

**VEREDITO: `C-PLUMB-1 = PASS`**

```
COLLECTION_INGRESS        = PROVED
INGRESS_TO_RAW            = PROVED
RAW_TO_DERIVED            = PROVED (prova M2)
DERIVED_TO_STRUCTURED     = PROVED (prova M2)
STRUCTURED_TO_ADMISSION   = PROVED (prova M2)
ADMISSION_TO_READY        = PROVED
REAL_UNAUTHORIZED_BYPASSES = 0
DUPLICATE_CANONICAL_OWNERS = 0
TEST_PATH = PRODUCTION_PATH   (a travessia chama pela_entrada/pela_porta reais)
NEW_FAILURES               = 0
```

Com uma ressalva dita em voz alta e **não escondida**: a travessia
`RAW → DERIVED → STRUCTURED` está **provada** e **não corre por omissão em
produção**, porque exige Postgres. Ligá-la ao caminho por omissão é
`ARCHITECTURE_DECISION_REQUIRED`, e não encanamento em falta.
