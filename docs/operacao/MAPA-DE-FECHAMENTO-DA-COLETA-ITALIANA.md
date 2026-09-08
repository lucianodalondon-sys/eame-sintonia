# MAPA DE FECHAMENTO DA COLETA ITALIANA

> **DERIVADO.** Todo estado sai de `system-map/data/estradas-it.generated.json`,
> produzido por `python3 system-map/scripts/censo_das_estradas_it.py`.
> `tests/test_estradas_it.py` falha se um número aqui divergir de lá.

---

## A — O ÚLTIMO EXCESSO DO INSTRUMENTO, REMOVIDO

O censo afirmava: «quem não menciona não pode estar ligado». Falso, e
reproduzido em `tests/fixtures/ARESTAS/`:

```
owner_indireto.py    from ajudante import persistir → persistir(x)
ajudante.py          select ... from derived_artifact
```

`owner_indireto.py` **não contém** a string, e há caminho executável.

    AUSÊNCIA DE REFERÊNCIA DIRETA NÃO É AUSÊNCIA DE CONEXÃO.

O negativo mudou de nome, porque **o nome era o erro**:

| degrau | o que prova |
|---|---|
| `NO_DIRECT_REFERENCE` | não há referência **neste ficheiro**. Um facto sobre o ficheiro lido, não um veredito sobre a ligação. |
| `CANDIDATE_CONNECTION` | menciona só fora do código executável |
| `TRANSITIVE_CODE_PATH` | um módulo importado referencia o artefato em código |
| `DIRECT_CODE_REFERENCE` | o código executável deste ficheiro referencia |
| `TESTED_CONNECTION` | um teste faz o objeto atravessar |
| `OBSERVED_CONNECTION` | execução real, com recibo |

Fecham **transitiva e acima**. O resolvedor segue **2 saltos** de import — não é
um call graph universal, e o fundo está escrito.

### Quando a ausência *é* conclusiva

Só onde o contrato da etapa exige toque direto, e isso é **declarado por
aresta** (`DIRECT_REQUIRED`). Hoje são 4: `RC-1 STRUCTURED`, `RC-1 ADMISSION`,
`RC-2 RUN`, `RC-2 ADMISSION` — marcadas com `!` na matriz. Nelas o resolvedor
transitivo procurou ajudante em 2 saltos e não achou.

> **22 arestas mudaram de estado — e nenhuma mudou de veredito.** As positivas
> eram todas diretas; as 4 negativas continuam negativas mesmo com transitividade.
> O conserto era necessário para a coerência do instrumento e não resgatou nada.

---

## B — A MATRIZ

Célula: `ESTADO·ligação`. `!` = ausência conclusiva por contrato.

| ROUTE_CLASS | DISCOVER | FETCH | RAW | RUN | CHECKPOINT | DERIVED | STRUCTURED | ADMISSION | FECHADA | FALTA |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| **RC-1 · OFFICIAL_HTTP_DOCUMENT** | Declared·— | Observed·direta | Observed·direta | Observed·direta | N/A | Observed·direta | Code·semref! | Code·semref! | **NÃO** | STRUCTURED, ADMISSION |
| **RC-2 · YOUTUBE_OFFICIAL_API** | Observed·direta | Observed·direta | Localtes·direta | Code·semref! | Dbtested·direta | N/A | Dbtested·direta | Code·semref! | **NÃO** | RUN, ADMISSION |
| **RC-3 · PUBLIC_NATIVE_API** | Localtes·direta | Localtes·direta | Localtes·direta | — | — | N/A | — | — | **NÃO** | RUN, CHECKPOINT, STRUCTURED, ADMISSION |
| **RC-4 · SCIENCE_METADATA_API** | Localtes·direta | Localtes·direta | — | — | — | — | — | — | **NÃO** | RAW, RUN, CHECKPOINT, DERIVED, STRUCTURED, ADMISSION |
| **RC-5 · REGULATORY_BULK_IMPORT** | — | — | — | Livesche·direta | N/A | N/A | Livesche·direta | — | **NÃO** | DISCOVER, FETCH, RAW, ADMISSION |
| **RC-10 · OFFICIAL_HTTP_DATASET** | — | — | Code·direta | Code·direta | — | N/A | — | — | **NÃO** | DISCOVER, FETCH, CHECKPOINT, STRUCTURED, ADMISSION |
| **RC-11 · OFFICIAL_STATISTICAL_API** | — | — | — | — | — | N/A | — | — | **NÃO** | DISCOVER, FETCH, RAW, RUN, CHECKPOINT, STRUCTURED, ADMISSION |
| **RC-12 · SYNDICATED_FEED** | — | — | Code·direta | Code·direta | — | — | — | — | **NÃO** | DISCOVER, FETCH, CHECKPOINT, DERIVED, STRUCTURED, ADMISSION |

| ROUTE_CLASS | OBSERVAÇÃO | razão |
|---|---|---|
| **RC-6 · PUBLIC_BROWSER** | BLOCKED | robots/termos: zero capabilities permitidas na matriz |
| **RC-7 · LOCAL_SESSION** | BLOCKED | AUTOMATION_NOT_ALLOWED: sessao humana nao autoriza automacao |
| **RC-8 · PAID_FALLBACK** | BLOCKED | APIFY-LAST: zero rotas permitidas hoje na matriz |
| **RC-9 · GIT_LEDGER** | DEBT | estado operacional em Git, contra P-011. Nao e estrada a fechar: e divida a mover. |

| medida | valor |
|---|---:|
| `ROUTE_CLASSES_MODELED` | **12** |
| `ROUTE_CLASSES_WITH_PROVEN_MEMBERSHIP` | **2** (RC-1, RC-9) |
| `ARCHITECTURE_CLOSED` | **0** |
| `OBSERVED` | **2** |
| `DB_TESTED` | **1** |
| `BLOCKED` | **3** |
| `DEBT` | **1** |
| `ROUTE_CLASSES_REQUIRED_TOTAL` | **UNKNOWN** |

---

## C — AS FONTES, DEPOIS DA M1B

| medida | valor |
|---|---:|
| total | 54 |
| `SOURCES_WITH_PROVEN_ROUTE` | **7** |
| `SOURCES_WITH_ONLY_CANDIDATE_ROUTE` | **24** |
| `SOURCES_ROUTE_UNKNOWN` | **23** |
| `SOURCES_BLOCKED` | **0** |

| medida | valor |
|---|---:|
| `TOTAL_PROVEN_MEMBERSHIPS` | **8** |
| `TOTAL_CANDIDATE_MEMBERSHIPS` | **38** |
| `TOTAL_BLOCKED_MEMBERSHIPS` | **0** |

| ROUTE_CLASS | provadas | candidatas | níveis de evidência |
|---|---:|---:|---|
| RC-1 · OFFICIAL_HTTP_DOCUMENT | 1 | 26 | DECLARED, EXPECTED, HISTORICALLY_OBSERVED, LIVE_FETCH_PROVEN, LIVE_METADATA_PROVEN |
| RC-9 · GIT_LEDGER | 7 | 0 | HISTORICALLY_OBSERVED |
| RC-10 · OFFICIAL_HTTP_DATASET | 0 | 3 | EXPECTED, HISTORICALLY_OBSERVED, LIVE_METADATA_PROVEN |
| RC-11 · OFFICIAL_STATISTICAL_API | 0 | 1 | DECLARED |
| RC-12 · SYNDICATED_FEED | 0 | 8 | LIVE_METADATA_PROVEN |

**A M1B levou `ROUTE_UNKNOWN` de 35 para 23, com zero chamadas de rede.**

---

## D — O QUE RESOLVEU, E O QUE NÃO CONTA

O probe de Milão **não preservou amostra** — ele mesmo avisa: «este probe NÃO
preserva amostra, ele só mede a porta». Mas registrou **pistas**, e elas não
valem o mesmo:

| pista | vale | por quê |
|---|:-:|---|
| `link .pdf na pagina` | ✅ | é um `<a href>` observado — um **endereço** |
| `link de planilha` / `.csv` | ✅ | idem |
| `RSS declarado no <head>` | ✅ | `<link rel=alternate>` — endpoint declarado por máquina |
| `a palavra 'bollettin' aparece` | ❌ | é uma palavra |
| `WordPress` | ❌ | é a plataforma |
| `area reservada / login citado` | ❌ | existe login em *algum* lugar do site; não diz que o boletim exige |

    UMA PÁGINA MENCIONAR PDF NÃO PROVA QUE AQUELE PDF É O PRODUTO DA FONTE.
    UM LINK PARA .PDF É OUTRA COISA: É UM ENDEREÇO.

E um link visto vira `CANDIDATE`, nunca `PROVEN`: o endereço foi observado, **o
byte não foi buscado**.

---

## E — POR QUE A REDE NÃO FOI CHAMADA

A regra de assimetria do próprio probe: `BLOCKED/WAF` de egresso errado é sinal
**FRACO e INCONCLUSIVO**.

| | |
|---|---|
| egresso do probe preservado | Milano · IT |
| egresso desta sessão | **US** |

Repetir daqui produziria evidência que teria de ser descontada — e evidência que
se desconta não é evidência. **Zero chamadas de rede nesta missão.**

### A próxima prova mínima, por fonte

| prova | fontes |
|---|---:|
| `CANONICAL_CHAIN_CAPTURE` | 24 |
| `BROWSER_PUBLIC_HEAD (egresso IT)` | 14 |
| `nada — ja provada` | 7 |
| `ALT_CANONICAL_URL` | 4 |
| `ITALIAN_BROWSER_RETEST` | 3 |
| `OFFICIAL_SITEMAP` | 2 |

Nenhuma delas exige login, sessão pessoal, download grande, quota ou Apify. Todas
exigem **egresso italiano**.

---

## F — RC-12, A CLASSE QUE O FEED EXIGIU

| classe | motivo material |
|---|---|
| **RC-12 · SYNDICATED_FEED** | Duas etapas divergem, **não o formato**. `DISCOVER`: a RC-1 descobre por catálogo escrito à mão; um feed enumera sozinho, e o endereço vem declarado por máquina no `<head>`. `INCREMENTALIDADE`: a RC-1 tem `CHECKPOINT` N/A por ser documento único sem janela; um feed tem cursor natural por entrada. 7 fontes com RSS declarado. |

---

## G — M1: FECHADA?

**Definição usada** (registrada em `docs/decisoes/DIARIO-DE-DECISOES.md`): M1
fecha quando toda fonte foi levada ao **máximo estado epistemicamente possível
com a política aprovada** e cada `UNKNOWN` residual carrega **próxima prova
nomeada**. Não exige zero `UNKNOWN`.

Isso vem do contrato, não da conveniência: `leis/fundacao_da_coleta.py` diz que
a fundação é sobre **classes de estrada**, e diz explicitamente que **não**
significa «coletamos todas as fontes». O critério 1 do mapa anterior pedia
«fontes IT em route class ou BLOCKED» — uma exigência **por fonte**. As duas não
podiam valer juntas; vale a do contrato.

    EXIGIR ZERO UNKNOWN POR FONTE CRIARIA O INCENTIVO
    DE CHAMAR DE BLOCKED O QUE É SÓ DESCONHECIDO.

**M1 = FECHADA.** A evidência preservada foi esgotada, e as 47 fontes sem rota
provada têm próxima prova nomeada — todas bloqueadas pela mesma coisa: egresso.

---

## H — TOP GAPS, RECALCULADOS

| # | gap | destrava |
|---:|---|---|
| **G-1** | **Observabilidade**: o sistema não sabe contar o próprio fluxo | toda missão seguinte. Três missões acharam estado publicado sem medição, sempre tarde |
| **G-2** | ligar `STRUCTURED` e `ADMISSION` da RC-1 ao `derived_artifact` | a classe mais populosa; ausência **conclusiva** por contrato |
| **G-3** | probe com egresso italiano para as 23 residuais | 23 fontes |
| **G-4** | tirar o Git do runtime (RC-9 → donos canônicos) | 7 pertenças provadas presas em Git |
| **G-5** | RC-2 ao vivo: `RUN` ligado + operacional | a única cadeia social |

**A ordem é `M1 → OBSERVABILIDADE → M2`.** Sem Observability, M2 seria G-2.

---

## I — O QUE ESTE MAPA NÃO PROVA

- **0** estradas com arquitetura fechada.
- `TRANSITIVE_CODE_PATH` prova caminho de import, não que o objeto **atravessa**
  — isso é `TESTED_CONNECTION`, e nenhuma aresta o tem hoje.
- Um link visto não é um byte buscado.
- Zero produção, zero rede, zero Apify, zero inteligência.

`COLLECTION_FOUNDATION_CLOSED` = **NÃO**.
