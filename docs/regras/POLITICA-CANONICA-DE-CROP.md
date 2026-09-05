# POLÍTICA CANÔNICA DE CROP — SINTONIA EAME

Regra única sobre **como o sistema decide de que cultura um conteúdo fala**. Fecha a decisão D1,
que bloqueou o passo 01 da integração progressiva.

| | |
|---|---|
| `POLICY_OWNER` | dono da regra de coleta EAME, em conjunto com o dono da linhagem italiana |
| `RULE_VERSION` | `CROP-D1-2026-09-05` |
| `QUESTION_RESPONDED` | *"De que cultura(s) este conteúdo fala, e há uma principal?"* — **uma pergunta, um dono** |
| `STATE` | CANÔNICA |

---

## As quatro leis

```
MULTI_CROP              !=  AMBIGUOUS
DICTIONARY_ORDER        !=  EVIDENCE
FIRST_MATCH             !=  CANONICAL_RESOLUTION
CROP_ALL = conjunto evidenciado   ·   CROP_PRIMARY = somente se provado
```

### Por que esta regra existe

Duas linhagens tinham razão sobre metade do problema, e por isso colidiram.

Uma tinha razão em que **`for … break` não é critério**: elege a cultura pela ordem de inserção
do dicionário, sem prova, sem teste, em silêncio. Com um vocabulário de uma chave o defeito é
invisível — empate é impossível com um item.

A outra tinha razão em que **colapsar tudo em `AMBIGUOUS:A+B+C` destrói informação**: medido
sobre `data/samples/IT-CONVEGNO-V1/falas/*.json`, a regra `AMBIGUOUS` aplicada ao vocabulário
italiano marcava **17 de 17 falas** como ambíguas. Mas uma palestra que fala de videira, pêssego
e pereira **não é ambígua** — ela é plural, e sabemos exatamente do que fala.

O erro comum às duas era o mesmo: **tratar pluralidade e incerteza como a mesma coisa.**
São perguntas diferentes e agora têm campos diferentes.

---

## O modelo

| campo | o que é |
|---|---|
| `CROP_ALL` | lista **ordenada deterministicamente** de todas as culturas distintas com evidência no conteúdo |
| `CROP_PRIMARY` | a cultura principal — **só quando provada**; caso contrário `UNKNOWN` |
| `CROP_CARDINALITY` | `NONE` · `SINGLE` · `MULTI` |
| `CROP_RESOLUTION_STATE` | `RESOLVED` · `AMBIGUOUS` · `UNKNOWN` · `NO_CROP` · `ERROR` |
| `CROP_EVIDENCE` | por cultura: `MATCHED_TERM`, `EVIDENCE_SPAN`, `EVIDENCE_SOURCE`, `RULE_VERSION` |

### Cardinalidade e resolução são eixos independentes

```
CROP_CARDINALITY = MULTI  +  CROP_RESOLUTION_STATE = RESOLVED
```
é o estado **normal** de uma palestra que cobre várias culturas. Sabemos exatamente do que ela
fala; só não há uma principal provada.

`AMBIGUOUS` fica reservado para **ambiguidade real de mapeamento**: quando o mesmo trecho de
texto é reivindicado por mais de uma cultura e a evidência não decide qual entidade ele
representa. Não é o caso de um documento que menciona três culturas em três trechos diferentes.

### `CROP_PRIMARY` — o que NÃO prova principalidade

- a primeira chave do dicionário
- o primeiro casamento lexical
- a ordem de configuração
- a ordem de aparição, sozinha
- o país ou o vocabulário usado

`SINGLE` → `CROP_PRIMARY` é essa cultura. `MULTI` sem regra de principalidade provada →
**`CROP_PRIMARY = UNKNOWN`, e isso é um estado válido.** Não se escolhe uma para facilitar a
vida de quem consome.

### Uma regra, vários vocabulários

Não existem `REGRA_CROP_ES`, `REGRA_CROP_IT`, `REGRA_CROP_FR`. A **semântica é única** —
detectar todas → preservar evidência → medir cardinalidade → provar ou não uma primária. O que
varia é o **vocabulário** (`VOCAB_CROP`, `VOCAB_CROP_IT`, …), declarado por quem chama. Duas
réguas para a mesma pergunta criam dois donos da mesma pergunta.

### First-match legado

O comportamento antigo **não é apagado**, porque reproduzir o passado tem valor. Fica em
`CROP_LEGACY_FIRST`, com `CROP_LEGACY_STATE = LEGACY_HEURISTIC`.

> **Nunca `CANONICAL_FACT`. Nenhum consumidor canônico novo pode depender desse campo.**

---

## Consumidores

Consumidor que exige uma cultura única **não pode escolher a primeira em silêncio**. Diante de
`CROP_CARDINALITY = MULTI` com `CROP_PRIMARY = UNKNOWN`, as saídas legítimas são:

```
BLOCK   ·   DEFER   ·   UNKNOWN
```

E `CROP_PRIMARY = UNKNOWN` **nunca significa ausência de cultura** — `CROP_ALL` está preenchido e
`CROP_CARDINALITY` diz quantas. Ausência de cultura é `NO_CROP`, que é outra coisa.

`CONSUMERS` e `TESTS`: registados em `docs/organizacao/INTEGRACAO-PROGRESSIVA-01.md`, na secção D1.

---

## O que esta política NÃO decide

**`ISSUE` continua como está**, com `AMBIGUOUS:A+B` para múltiplos achados. A D1 foi pedida para
`CROP` e é sobre `CROP` que decide. O mesmo raciocínio provavelmente se aplica a `ISSUE` — um
texto pode tratar de várias doenças sem que isso seja incerteza — mas estender esta política a
outro campo sem pedido seria criar política escondida, que é exatamente o que a lei do canário
proíbe. Fica registado como pergunta aberta, não como decisão tomada.
