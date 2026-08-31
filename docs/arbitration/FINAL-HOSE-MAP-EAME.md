# MAPA FINAL DE MANGUEIRAS — SINTONIA EAME

**Data:** 2026-08-31 · artefato executável em `data/arbitration/FINAL-HOSE-MAP-EAME.json`

```
REAL_DATA_WIRED = NO      V8_IMPLEMENTATION_STARTED = NO      CASCO_V7_MODIFIED = NO
```

> **Nenhuma ligação foi executada.** Este é o mapa de onde cada cano começa, o que ele
> carrega, que guard o protege e o que ele faz quando falta dado.

---

## A CADEIA CANÔNICA

```
FROZEN SOURCE / HANDOFF
  → canonical adapter
    → canonical entity / observation
      → dependency guard
        → attention object builder
          → attention readiness
            → action map
              → surface
                → evidence drawer
```

> **Regra de ouro: toda mangueira lê COMMIT FIXO.** Uma branch se move; um join que aponta
> para a ponta responde diferente a cada hora sem que ninguém tenha mudado nada.

---

## AS NOVE MANGUEIRAS

| # | mangueira | commit fixo | objeto canônico | tipo |
|---|---|---|---|---|
| **H1** | TERRITORIAL | `11fd7b5` (handoff `4ea268d`) | `TERRITORIAL_OBSERVATION` | `PHENOMENON_CASE` |
| **H2** | REGULATORY DEADLINE | `origin/…italy-pilot` | `REGISTRATION_DEADLINE` | `REGULATORY_DEADLINE` |
| **H3** | COMPETITOR IDENTITY CHAIN | `dc32ce0` (freeze `25194e3`) | `COMPETITOR_PRODUCT_IDENTITY` | `COMPETITOR_IDENTITY_CHAIN` |
| **H4** | META | `acfd987` (handoff `a2fad2d`) | `OBSERVED_PAID_ACTIVITY` | **evidência** — não é tipo próprio |
| **H5** | LONGITUDINAL FIELD | em árvore `ad041d7` | `FIELD_PRESSURE_SERIES` | `LONGITUDINAL_FIELD_PRESSURE` |
| **H6** | CREATOR | `248bd27` + `a509c12` | `PERSON_CREATOR` / `FARM_BUSINESS_ENTITY` / `CREATOR_CONTENT_PROFILE` | capability contextual |
| **H7** | EXPERT | em árvore `ad041d7` | `SCIENTIFIC_PERSON` | capability contextual |
| **H8** | PUBLIC COMM | `c25e44b` | `COMPANY_LOCAL_ACCOUNT` | **não produz objeto hoje** |
| **H9** | MULTILINGUAL | `1443f643` | `CONTENT_ENTITY` + `ONTOLOGY_TERM` | **guardrail transversal** |

**Os commits foram verificados**: há prova de que cada um resolve.

---

## O QUE CADA MANGUEIRA FAZ QUANDO FALTA DADO

`FAIL_CLOSED_BEHAVIOR` é a parte do mapa que mais importa — é ela que impede o produto de
inventar quando a fonte cala.

| # | falha fechada |
|---|---|
| **H1** | sem par cultura × problema **na mesma passagem**, o objeto não é construído. Não há fallback para produto cartesiano |
| **H2** | sem data futura declarada pela fonte, não há objeto. Ação máxima é `REVIEW`; `ALERT` é proibido |
| **H3** | sem concordância de titular **e** país nas três pontas, o estado é `NOT_KNOWN`. Zero recusas sem portão exercido é portão sem dentes |
| **H4** | zero de leitura é `NO_CONTENT_COLLECTION_EXECUTED`, **nunca** `COMPANY_NOT_COMMUNICATING` |
| **H5** | `INDEPENDENCE_FROM_TERRITORIAL_RAIF = NOT_PROVED`: não conta como segunda perna sem linhagem |
| **H6** | sem `ENTRY_PATH` instrumentado, **não há promoção a ferramenta** |
| **H7** | sem `ISSUE_EXPERTISE_PROVED`, a pessoa **não aparece** como especialista do problema |
| **H8** | `CONTENT_COLLECTION_STAGE = NOT_STARTED`: a mangueira existe e **não corre** |
| **H9** | língua fora do vocabulário fechado **recusa a criação** da entidade |

---

## AS DEPENDÊNCIAS QUE O MAPA CARREGA

**H3 depende de H4.** A perna Meta da cadeia de três camadas **é** o anúncio da Meta.
`DERIVED_DEPENDENCY_ON_META`: as duas nunca contam como famílias independentes para o mesmo
produto e país.

**H5 depende de H1 pela fonte.** O RAIF é publicador dos dois lados. `SAME_PUBLISHER ≠
INDEPENDENT_OBSERVATION`.

**H6 tem dependência interna de entidade.** O corpus profundo lê o conteúdo das identidades
que o mapa resolveu — uma família com duas observações, não duas famílias.

**H9 atravessa todas.** Nenhum texto chega à tela sem passar pelo contrato multilíngue.

---

## LIMITES CONHECIDOS, DECLARADOS ANTES DE LIGAR

| # | limite |
|---|---|
| **H1** | o **corpo completo não está preservado** — só `DOCUMENT_EXCERPT` (3.000 caracteres) e as passagens de evidência |
| **H2** | **só a Itália** está neste artefato. ES e FR precisam do equivalente antes de generalizar |
| **H4** | `OPERATIONAL_TEMPORAL_SIGNAL_VALUE = NOT_PROVED`; janela medida de uma hora |
| **H5** | escopo: o artefato de série cobre o recorte moderno; o número canônico do ledger é **23 safras · 148.964 leituras** — ver 4.1 |
| **H6** | `REVALIDATION_RULE = NOT_YET_DEFINED`, de propósito |
| **H8** | zero conteúdo |

### 4.1 · Uma correção que o próprio repositório pegou

O refresh corrigido (`ad041d7`) tratou o número de safras do RAIF como **divergência
aberta**, dizendo *"não se escolhe a mais conveniente"*. **Estava errado — e não por
excesso de cautela, mas por falta de leitura.**

O repositório **já tinha resolvido** isso na MISSÃO 02: a leitura antiga usou apenas os
arquivos modernos e publicou o número menor; o pacote traz **também** os arquivos por
província de 2003–2016. O ledger é dono do número:

```
RAIF_SEASONS_AVAILABLE = 23        RAIF_READINGS_TOTAL = 148.964
```

E há **teste no repositório** que reprova documento corrente que volte a afirmar o número
antigo. **Foi ele que pegou este erro**, quando este documento entrou na suíte.

> **Quem manda no número é o ledger, nunca o documento** — e um artefato de recorte não é
> uma segunda opinião sobre o total.

---

## ORDEM SUGERIDA DE LIGAÇÃO

**Sugestão, não instrução de implementação.**

```
1  H2  REGULATORY DEADLINE    é o único objeto com decisão de negócio defensável hoje,
                              e a fonte é oficial e primária
2  H1  TERRITORIAL            produz o único PHENOMENON_CASE com chave completa
3  H9  MULTILINGUAL           guardrail transversal: entra ANTES de haver texto na tela
4  H3  IDENTITY CHAIN         36 tuplas prontas, ainda sem gatilho de atenção
5  H5  LONGITUDINAL FIELD     série longa, com backtest honesto sobre o limite
6  H7  EXPERT                 contextual dentro do caso, com portão de expertise
7  H6  CREATOR                contextual e instrumentado, sem navegação própria
8  H8  PUBLIC COMM            só quando houver conteúdo
```

**Por que o regulatório vem primeiro e não o caso:** é o único que hoje atravessa o portão
de atenção até a ação, com dono real. Começar por ele testa a cadeia inteira — objeto,
estado, ação, superfície, gaveta de evidência — com o material mais sólido que existe.

---

## MANGUEIRAS QUE NÃO EXISTEM E NÃO DEVEM SER CRIADAS

```
META → superfície própria .................... DO_NOT_BUILD = META_DASHBOARD
REGULATORY → dashboard ....................... vencimento autoriza REVIEW, não painel
UNKNOWN → audit dashboard .................... estado transversal, nunca ferramenta
CREATOR → navegação primária no V8 inicial ... TEST_AS_CAPABILITY até haver uso real
qualquer score agregado ...................... somar eixos esconde o eixo vazio
```
