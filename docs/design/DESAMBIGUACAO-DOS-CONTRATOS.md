# A desambiguação dos contratos — o manifesto parou de admitir duas leituras

```
CONTRACT               = PASS       (R4 · v21_contrato_da_superficie.py)
CANONICAL_BASE         = b3935bd
CASE_DATA_CHANGED      = NO
MANIFEST_CONTRADICTION_RESOLVED   = YES
PUBLICATION_WORDING_RESOLVED      = YES
RENDERABLE_SURFACE_RULE_DECLARED  = YES
```

⚠️ **Nenhum dos 43 casos mudou.** O que mudou foi o texto de três leis que
diziam uma coisa e valiam outra. Este documento é o **registro da decisão e da
prova**; o contrato em si vive num lugar só — `APP-MANIFEST.json`.

---

## 1 · O defeito: o contrato correto exigia desobedecer ao contrato

O `APP-MANIFEST` é o arquivo de entrada do portal. Ele carregava quatro campos e
não dizia qual deles decide o que aparece na tela:

| campo | o que parecia | o que é |
|---|---|---|
| `COMMERCIAL_PRIORITY` | uma classificação | **o dono da faixa da tela** |
| `CLIENT_SAFE` | um portão de visibilidade | uma pergunta sobre **fato × síntese** |
| `RENDERABLE_WITH_METHOD` | um portão de visibilidade | um **estado metodológico** |
| `PUBLICATION_STATE` | um portão de visibilidade | um portão de **distribuição externa** |

E a lei do `CLIENT_SAFE` dizia, literalmente:

> «CLIENT_SAFE=false vive no corpus e aparece como RESEARCH_LEADS»

Os 43 são `CLIENT_SAFE=false` **por construção** — o cruzamento é leitura nossa
sobre fatos de terceiros. Um portal que obedecesse ao manifesto mandava os 43
para research leads e chegava a uma **tela vazia**. Um portal que ignorasse o
manifesto chegava à tela certa **por sorte**.

    QUANDO A IMPLEMENTAÇÃO CORRETA EXIGE DESOBEDECER AO CONTRATO,
    QUEM ESTÁ QUEBRADO É O CONTRATO.

---

## 2 · As três correções, e o que cada uma NÃO fez

### CONFLICT 1 · `CLIENT_SAFE`

O mapeamento por `QA_STATUS` continua **byte a byte idêntico** — nenhum registro
mudou de valor. O que mudou foi a **consequência declarada**:

```
PERGUNTA  esta afirmação pode ser apresentada como FATO client-safe
          sem depender da leitura/síntese metodológica do Sintonia?

LEI       CLIENT_SAFE=false significa que a afirmação depende da nossa síntese
          — e por isso viaja COM O MÉTODO AO LADO, nunca sozinha.

          FATO CLIENT-SAFE ≠ LEITURA DE INTELIGÊNCIA MOSTRÁVEL
```

`RESEARCH_LEADS` continua existindo onde o contrato da coleção o determinar.
`CLIENT_SAFE=false` **sozinho** deixou de ser regra suficiente para mandar uma
`OPPORTUNITY` para lá.

### CONFLICT 2 · `RENDERABLE_WITH_METHOD`

Nasceu `MEETING_SURFACE_RULE`, que responde à pergunta que o manifesto nunca
respondia — *o que eu mostro?* — com uma única leitura possível:

```
SOURCE_COLLECTION                                OPPORTUNITIES
INCLUDE_ALL_CURRENT_CASES                        true
EXPECTED_TOTAL                                   recontado do pacote a cada build
LANE_OWNER                                       COMMERCIAL_PRIORITY
CLIENT_SAFE_IS_VISIBILITY_GATE                   false
RENDERABLE_WITH_METHOD_IS_VISIBILITY_GATE        false
PUBLICATION_STATE_IS_VISIBILITY_GATE             false
PUBLICATION_STATE_CONTROLS_EXTERNAL_DISTRIBUTION true
```

`true = 33` e `false = 10` continuam onde estavam. Os 10 não viraram coleção
nova, não foram para Segnali e não geraram classificação comercial. O campo
responde a uma pergunta epistemológica, não a «este caso existe na tela?».

`EXPECTED_TOTAL` **não é constante**: sai de `COLLECTIONS.opportunities.COUNT_TOTAL`
a cada build. Número escrito à mão em contrato envelhece em silêncio, e este
repositório já pagou por isso mais de uma vez (U32 segura).

### CONFLICT 3 · `PUBLICATION_STATE`

A frase ambígua era «portão de saída» — que, lido por quem implementa a tela,
vira «não renderize». Corrigida em **dois lugares, porque duas fontes diziam a
mesma coisa com palavras diferentes**:

- no manifesto, `FIELD_QUESTIONS.PUBLICATION_STATE.PAPEL`;
- na lei que viaja em cada cartão, `PUBLICATION_GATE_LAW`, que dizia
  «sustentar afirmação **publicável**» e hoje diz «sair como **material**».

```
VENDER É UMA DECISÃO INTERNA.  ENVIAR É UMA AFIRMAÇÃO PÚBLICA.

RENDER != EXPORT
```

`EXTERNAL_EXPORT_ALLOWED` declara o contrato de saída sem obrigar ninguém a
implementar botão de exportação agora: `PUBLISHABLE` permitido, sujeito aos
demais contratos; `VALIDATION_REQUIRED` bloqueado até validação; `UNKNOWN` e
`QUARANTINED` bloqueados por não terem estado decidido.

---

## 3 · A prova: o consumidor que não interpreta nada

`scripts/v21_contrato_da_superficie.py` é o **R4** da cadeia. Ele não sabe nada
sobre agronomia nem sobre a reunião da ADAMA. Abre o `APP-MANIFEST`, obedece
literalmente ao que estiver escrito, e conta o resultado no pacote. Se precisar
de **uma** decisão que o manifesto não declarou, o veredito é `CONTRACT = FAIL`
— e o defeito é do manifesto, nunca do portal.

Ele descobre até o nome do arquivo pela tabela `COLLECTIONS`: não pode chutar
que `OPPORTUNITIES` vira `OPPORTUNITIES.json`.

Os números da tela **não** saem do manifesto. São o critério, e estão escritos no
próprio script — se ele os lesse de lá, provaria apenas que o manifesto concorda
consigo mesmo.

```
                                   ANTES DA CORREÇÃO      DEPOIS
perguntas respondidas pelo manifesto      0/1              22/22
CONTRACT                                  FAIL             PASS
o portal teria de adivinhar               MEETING_SURFACE_RULE ausente    —

MEETING_SURFACE_TOTAL       43
POR_FAIXA                   AGIRE ORA 5 · PREPARARE ORA 8 ·
                            DA MONITORARE 13 · SEGNALI 17
EXTERNAL_EXPORT_LIBERADO    PUBLISHABLE 5
EXTERNAL_EXPORT_BLOQUEADO   VALIDATION_REQUIRED 38
```

O `FAIL` da coluna da esquerda é medido, não hipotético. O pacote é reconstruído
do zero a cada rodada e vive fora do Git, então esse `FAIL` desapareceria no
build seguinte — e ninguém poderia conferir que a correção consertou alguma
coisa. Ele ficou congelado como controle negativo em
`data/samples/AUDITORIA-SOMBRA/SURFACE-CONTRACT-ANTES-DA-CORRECAO.json`.

    UM PORTÃO QUE NUNCA REPROVOU NÃO É PORTÃO — É DECORAÇÃO.

---

## 4 · O que mudou no pacote, arquivo a arquivo

Duas builds completas do mesmo commit, comparadas ignorando `BUILD_ID`:

```
arquivos no DESIGN-INGEST                  32 antes · 32 depois · 0 só num lado
arquivos com conteúdo diferente            2   APP-MANIFEST.json · OPPORTUNITIES.json

APP-MANIFEST      chaves novas             MEETING_SURFACE_RULE · FIELD_QUESTIONS ·
                                           EXTERNAL_EXPORT_ALLOWED
                  chaves removidas         nenhuma
                  chaves alteradas         CLIENT_SAFE_RULE

OPPORTUNITIES     IDs                      43 → 43, conjunto idêntico
                  campos que mudaram       PUBLICATION_GATE_LAW  (texto de lei,
                                           1 valor distinto antes, 1 depois)
```

A build limpa em `b3935bd` reproduziu `V21-358954754db5ea2f` — o mesmo
`BUILD_ID` do checkpoint anterior. O determinismo é a razão de a comparação
valer alguma coisa.

---

## 5 · Os invariantes, medidos nas duas pontas

```
INVARIANTE                  AGORA                          == ANTES  == CRITÉRIO
CASES                       43                             SIM       SIM
BY_COMMERCIAL_PRIORITY      5 / 8 / 13 / 17                SIM       SIM
BY_PUBLICATION_STATE        PUBLISHABLE 5 · VALIDATION 38  SIM       SIM
CLIENT_SAFE                 false 43                       SIM       SIM
RENDERABLE_WITH_METHOD      true 33 · false 10             SIM       SIM
TRAIL_STATE                 COMPLETE 43                    SIM       SIM

CASE_IDS idênticos                                    : True
casos com QUALQUER campo diferente                    : 0
campos comparados por caso                            : COMMERCIAL_PRIORITY,
  PUBLICATION_STATE, CLIENT_SAFE, RENDERABLE_WITH_METHOD, TRAIL_STATE, STATUS,
  WINDOW_DEFINED, WINDOW_OPEN_NOW, WINDOW_TYPE, WINDOW_RULE_STATE
```

---

## 6 · Os portões, na mesma execução

```
ACEITAÇÃO           0 violações em 11 contadores obrigatórios
R1 GEOGRAFIA        0 violações · 6.472 registros · 19 cruzamentos
R2 PROCEDÊNCIA      0 violações · 7.169 registros
R4 SUPERFÍCIE       CONTRACT = PASS · 22/22
TESTEMUNHA          AUTOMATIC_NEW_INGEST YES · UNIVERSAL_GATE YES · BACKFILL YES
                    BUILD_ID volta ao original depois da restauração

SUÍTE               801 descobertos = 778 passam + 6 falhas + 1 erro + 16 pulados
```

As 6 falhas e o 1 erro **já existiam em `b3935bd`**, medidos numa build limpa
antes desta correção: o conjunto de testes que falha é idêntico antes e depois.
Estão classificados um a um em `RECONCILIACAO-DE-LINHAGEM.md`, §7 — proveniência
de amostras antigas, um artefato ausente do ambiente, uma migration, e um módulo
de teste que é script e aborta na descoberta. Nenhum toca o contrato do cartão,
a catraca ou a superfície.

    UMA SUÍTE QUE FICA VERDE PORQUE ALGUÉM CONSERTOU O TESTE
    MEDE O CONSERTO, NÃO O SISTEMA.

---

## 7 · O que este documento NÃO é

Ele **não é o contrato**. O contrato é o `APP-MANIFEST.json` — uma fonte só. Se
este texto e o manifesto divergirem um dia, o manifesto vence e a divergência é
um achado.

E a fronteira da missão continua onde estava:

```
INTELLIGENCE WRITES TRUTH.   PORTAL RENDERS TRUTH.
```

Nada aqui tocou portal, layout, menu, card, navegação, Vercel ou publicação.
