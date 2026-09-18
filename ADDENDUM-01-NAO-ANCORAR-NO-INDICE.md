# ADDENDUM 01 — OBRIGATÓRIO
# NÃO ANCORAR O CENSO NO ÍNDICE GERADO

Este addendum CORRIGE o ficheiro `MISSAO-SOURCE-COLLECTION-READINESS-V1.md`.
Onde houver conflito, ESTE documento vence.

NÃO reiniciar a missão. NÃO recriar a worktree. CONTINUAR de onde está.

==================================================
A CORREÇÃO
==================================================

O coordenador ancorou o baseline num ficheiro GERADO. Isso estava errado.

NÃO usar:

```
docs/fontes/INDICE-DE-FONTES.md
coluna "a máquina busca?" = sim  →  5
```

como baseline de `SOURCE_COLLECTION_READY` ou de "fontes coletáveis".

Esse número significa APENAS:

```
FONTES COM CONTRATO DE BUSCA ESCRITO NO ÍNDICE GERADO = 5
```

E já existe **contraposição de runtime**: a primeira Big Collection italiana
executou **6 fontes italianas com SUCCESS** (commit `d915f85a`, que é a BASE_HEAD
desta missão).

Portanto, cinco universos distintos, e nenhum se infere do outro:

```
DECLARED_CONTRACT
!= CAPABILITY EXISTS
!= COLLECTION WIRED
!= FLOW OBSERVED
!= SOURCE_COLLECTION_READY
```

A secção 0-BIS do ficheiro da missão listava `"A MÁQUINA BUSCA" = SIM → 5`.
Esse valor continua a ser um facto medido SOBRE O ÍNDICE, mas está agora
REBAIXADO: não é baseline de readiness, é apenas `CONTRATOS_DECLARADOS = 5`.

==================================================
REMEDIR O BASELINE CORRETO
==================================================

Para cada SOURCE_ID, medir pelas autoridades REAIS (código, runtime, evidência),
não pelo índice:

1.  SOURCE_ID existe no owner canônico?
2.  endereço/endpoint real existe?
3.  qual ACCESS_SHAPE?
4.  já existe collector/capability capaz desse shape?
5.  existe recipe/fase?
6.  está wired no orquestrador?
7.  houve execução observada anterior?
8.  existe RAW/evidence preservado?
9.  policy permite?
10. gasto é permitido?
11. canário já passou?

Derivar então, SEPARADAMENTE, sem inferir um do outro:

```
DECLARED_CONTRACT             = YES/NO
TECHNICALLY_COLLECTION_READY  = YES/NO
FLOW_OBSERVED                 = YES/NO
BIG_COLLECTION_EXECUTABLE     = YES/NO
```

`FLOW_OBSERVED = YES` com `DECLARED_CONTRACT = NO` é resultado VÁLIDO e esperado.
Não "corrigir" essa combinação: reportá-la.

==================================================
CONTRAPROVA OBRIGATÓRIA
==================================================

As 6 fontes executadas na Big Collection recente DEVEM aparecer no censo.

Medir especificamente:

```
IT-T2-002
IT-T2-004
IT-T3-002
IT-T3-008
IT-T3-010
IT-T4-001
```

Pergunta a responder com número:

> quantas delas o índice marca "máquina busca = sim"?

MEDIÇÃO JÁ FEITA PELO COORDENADOR (confirme, não confie):

```
SOURCE_ID    índice "máquina busca?"   estado no índice
IT-T2-002    **não**                   🟢 GREEN
IT-T2-004    **não**                   🟢 GREEN
IT-T3-002    **não**                   🟢 GREEN
IT-T3-008    **não**                   🟢 GREEN
IT-T3-010    **não**                   🟢 GREEN
IT-T4-001    sim                       🟢 GREEN
------------------------------------------------------
índice diz SIM:  1 / 6
runtime provou:  6 / 6  (afirmado; VERIFICAR em d915f85a)
```

Logo:

```
INDEX_COLLECTION_READINESS_STALE = YES
```

O índice **NÃO pode ser usado como owner do readiness**: 5 das 6 fontes que o
runtime executou estão marcadas "não" no índice. A divergência é 1 vs 6.

NOTA DE HONESTIDADE: o coordenador escreveu primeiro "0/6" neste ficheiro, por
suposição, e a medição devolveu "1/6". O valor correto é **1/6**. Registado aqui
porque o erro é exatamente o que esta missão proíbe — afirmar antes de medir.

OBRIGAÇÃO ADICIONAL — JÁ CUMPRIDA PELO COORDENADOR:

O "6/6 com SUCCESS" era uma afirmação recebida. Foi VERIFICADA contra o ledger,
medindo o **delta do commit** (não o total do ficheiro, que é cumulativo:
34 runs / 184 observações acumuladas — usar o total seria erro de denominador).

Evidência: `git show d915f85a -- data/collection-ledger/italy/runs.ndjson
data/collection-ledger/italy/observations.ndjson`

```
DELTA DO COMMIT      runs = 6      observações = 9

RUNS (6), todos:     SOURCES_ATTEMPTED 1 · HEALTHY 1 · DEGRADED 0
                     FAILED 0 · UNKNOWN 0 · VPN_COUNTRY IT
                     GIT_HEAD dos runs = 78f8fcdc  (executados ANTES do commit)

OBSERVAÇÕES por SOURCE_ID
  IT-T2-002  4
  IT-T2-004  1
  IT-T3-002  1
  IT-T3-008  1
  IT-T3-010  1
  IT-T4-001  1
  ----------------
  total      9   sobre exatamente as 6 fontes nomeadas

OBSERVATION_RESULT           NEW_DOCUMENT 9/9
RAW_PRESERVED_BEFORE_PARSE   True 9/9
RAW_OBJECT_CREATED           True 8 · False 1   ← NÃO é uniforme; medir porquê
```

VEREDITO: `FLOW_OBSERVED = YES` para as 6, sustentado por RUN + observação
preservada, não por mensagem de commit. A afirmação resistiu à verificação.

Fica de pé, e é trabalho seu: **1 das 9 observações tem
`RAW_OBJECT_CREATED = False`**. Apurar qual, e porquê, antes de tratar as 6 como
equivalentes. Observação registada não é objeto bruto guardado.

Nota de procedência: os runs carregam `GIT_HEAD = 78f8fcdc` porque correram antes
de o resultado ser commitado como `d915f85a`. Isto é coerente — e explica de onde
veio o HEAD obsoleto citado no prompt original. Não é contradição.

REGRAS SOBRE ISSO:

- NÃO editar `docs/fontes/INDICE-DE-FONTES.md` manualmente. É GERADO.
- Corrigir owner/gerador SOMENTE se isso pertencer ao escopo desta missão E
  houver prova. Caso contrário: reportar como achado, não consertar.
- Se a correção do gerador for fora de escopo, entregar como dívida registada
  com o owner nomeado — não como missão nova iniciada.

==================================================
CONTADORES — QUATRO, NÃO UM
==================================================

Manter SEPARADOS. Não fundir. Não "acertar" para fazer bater:

```
ATLAS_FICHAS          = 210   fichas com SOURCE_ID na tabela do índice
ATLAS_HEADER_STAMP    = 190   carimbo no cabeçalho do Atlas
ESCADA_REGISTADA      = 173   degrau "REGISTADA" da escada
CONTRATOS_DECLARADOS  =   5   coluna "a máquina busca?" = sim
```

Para cada um, descobrir e declarar:

```
O QUE MEDE (na verdade) =
QUEM É O OWNER =
COMO É PRODUZIDO (gerado? à mão? carimbo?) =
ESTÁ STALE? =
```

Se houver owner diferente: reportar.
Se houver métrica stale: reportar.
NÃO editar contador para fazê-lo bater com outro.

Estes quatro são DIFERENTES de `SOURCE_COLLECTION_READY`, que é o §16 da missão
e nasce de código/runtime/prova.

==================================================
O OBJETIVO NÃO MUDOU
==================================================

Continuar a procurar o maior ganho de cobertura:

```
muitas fontes
→ mesmo ACCESS_SHAPE
→ collector existente
→ configuração/wiring mínimo
→ canário
→ SOURCE_COLLECTION_READY
```

O resultado que importa continua a ser:

```
SOURCE_COLLECTION_READY_BEFORE =
SOURCE_COLLECTION_READY_AFTER  =
NEW_SOURCE_COLLECTION_READY    =
```

Esses três números devem nascer de **código / runtime / prova**,
NUNCA do campo "máquina busca?" do índice.

`SOURCE_COLLECTION_READY_BEFORE` deve ser REMEDIDO por este método. É provável
que não seja 5. Seja qual for, tem de vir com a evidência que o sustenta.

==================================================
HARD STOP (inalterado)
==================================================

Não iniciar Big Collection. Não iniciar Intelligence. Não iniciar Portal.
Não descobrir novas fontes. Não iniciar próxima missão.
Não fazer merge para o trunk sem autorização do coordenador.
