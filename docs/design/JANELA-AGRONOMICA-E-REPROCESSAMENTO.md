# A janela agronômica, o acervo relido e o backfill preview

> Nada foi publicado. Portal, produção e Vercel não foram tocados.

```
BASE      caa6937 · BUILD_ID V21-473db7a54b90c382
AGORA     BUILD_ID V21-ea0d941dc39f6b49
CASOS     43 → 43
```

O motor tratava **janela** como **intervalo de calendário**. Medido no acervo:
das orações atribuídas a um par cultura × alvo, **nenhuma** declara datas — e
treze declaram a condição por fenologia, limiar, fase da praga, clima ou ato.

    O SERVIÇO FITOSSANITÁRIO NÃO ESCREVE «DE 3 A 18 DE JUNHO».
    ELE ESCREVE «EM PRÉ-COLHEITA», «AO ULTRAPASSAR 5%», «EM CONDIÇÕES
    PREDISPONENTES». ISSO É JANELA — SÓ NÃO É CALENDÁRIO.

Chamar de «sem janela» um boletim que diz quando agir é perder a informação que
a fonte deu. O contrato estava confundindo as duas coisas, e a rodada anterior
concluiu «0 de 17 combinações têm janela» **com esse contrato errado**.

---

## A · O que é uma janela agronômica

Sete tipos, todos **medidos antes de existirem** (`scripts/v21_janelas.py`):

| tipo | no acervo | agronômico? |
|---|---|---|
| `PHENOLOGY_WINDOW` | 3 | sim |
| `ADMINISTRATIVE_WINDOW` | 3 | **não** |
| `THRESHOLD_WINDOW` | 2 | sim |
| `WEATHER_TRIGGERED_WINDOW` | 2 | sim |
| `PEST_STAGE_WINDOW` | 2 | sim |
| `PREHARVEST_WINDOW` | 1 | sim |
| `CALENDAR_WINDOW` | 0 | sim |

**As duas perguntas, que nunca são a mesma:**

```
WINDOW_DEFINED   → sabemos QUAL condição define o momento certo?
WINDOW_OPEN_NOW  → há evidência de que a condição está satisfeita AGORA?
```

> **DEFINIDA NÃO É ABERTA. SABER O GATILHO NÃO É SABER QUE ELE DISPAROU.**

`WINDOW_OPEN_NOW = YES` exige, e só, que **o mesmo documento** que declara a
condição declare também o estádio da cultura (`CROP_STATE =
DECLARED_BY_SOURCE`), e que o documento seja corrente. Limiar, clima e fase da
praga **nunca** fecham: dependem de medição que ninguém nos deu, e ficam
`UNKNOWN` com o motivo `CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS`.

**Duas armadilhas, as duas medidas e fechadas:**

1. **O estádio sozinho não é janela.** «espigas em maturacao avancada» descreve
   a planta — numa oração que diz para **não** tratar. Lido como janela, virava
   janela aberta. Os padrões passaram a exigir a preposição que amarra a ação ao
   estádio: «a partir da invaiatura», «na fase de». `T40` fixa isso.
2. **A equivalência fenológica é LÉXICO, não dedução.** `PREHARVEST` é
   satisfeito por *maturazione, invaiatura, raccolta, vindima, BBCH 8x* — a
   tabela está escrita em `FENOLOGIA_QUE_SATISFAZ` e pode ser contestada lendo-a.

    A EQUIVALÊNCIA É NOSSA E ESTÁ ESCRITA. INFERÊNCIA É A QUE NÃO SE VÊ.

---

## B · O inventário do que o acervo já dizia

`python3 scripts/v21_janelas.py` → **13 candidatas** em 86 sinais client-safe,
onde o motor via **zero**. Gravadas em
`data/samples/AUDITORIA-SOMBRA/V113-INVENTARIO-DE-JANELAS.json`.

As cinco combinações obrigatórias:

| combinação | tipo | aberta agora | por quê |
|---|---|---|---|
| **botrite × videira · Emilia-Romagna** | `PREHARVEST_WINDOW` | **YES** | «intervir em pré-colheita» + o mesmo boletim declara «Vite: *maturazione*» |
| traça-da-uva × videira · Emilia-Romagna | `THRESHOLD_WINDOW` | UNKNOWN | «ao ultrapassar 5% de cachos infestados» — não medimos os 5% |
| piralide × milho · Friuli | `THRESHOLD_WINDOW` | UNKNOWN | «posturas superiores a 3 por 100 plantas» — idem |
| botrite × videira · Toscana | `PHENOLOGY_WINDOW` | UNKNOWN | «na fase de maior suscetibilidade»; o documento declara «invaiatura completa», que não nomeia a condição |
| carpocapsa × macieira · Veneto | `PEST_STAGE_WINDOW` | UNKNOWN | «terceiro voo terminado» — fase da praga, não medida por nós |

### A determinação 9818/2026 da Emilia-Romagna

Lida na fonte (`agricoltura.regione.emilia-romagna.it`, página atualizada em
28-05-2026). O texto declara:

> «La lotta obbligatoria dovrà essere attuata … **a partire dal 3 giugno 2026**
> e comunque **non prima della completa sfioritura della vite** … il **primo**
> dovrà essere realizzato **entro il 18 giugno 2026**, il secondo **entro e non
> oltre il 31 luglio 2026**.»

**O que essas datas são:**

| | |
|---|---|
| validade administrativa? | **sim** — são prazos de uma obrigação normativa |
| período autorizado? | **sim, por dentro** — delimitam quando o tratamento obrigatório deve ocorrer |
| janela agronômica? | **não sozinha** — o gatilho agronômico está numa cláusula *dentro* do ato: «non prima della completa sfioritura» |
| outra coisa? | é um ato **para o alvo que ele nomeia** — *Scaphoideus titanus* / cicaline — e **não** para a botrite da mesma videira |

E está **fechada**: 31/07/2026 é passado. `ADMINISTRATIVE_WINDOW` nunca vira
janela agronômica automaticamente — `T39` fixa isso no código.

---

## C · Os 43 reprocessados

| | antes | depois |
|---|---|---|
| `ACT_NOW` | 0 | **1** |
| `VALIDATE_NOW` | 5 | 4 |
| `WATCH` | 22 | 22 |
| `FUTURE_PREPARATION` | 7 | 7 |
| `TO_VALIDATE` | 9 | 9 |
| `SALES_READY` | 5 | 5 |
| `EXTERNAL_MATERIAL_READY = YES` | 5 | 5 |
| casos com `WINDOW_DEFINED = YES` | 0 | **6** |
| casos com `WINDOW_OPEN_NOW = YES` | 0 | **1** |

O único `ACT_NOW` é **botrite × videira × Emilia-Romagna** — o caso que a missão
apontou. E ele não voltou ao estado antigo: voltou com uma razão atrás.

```
ACTION_CHAIN_LINKS = {SINAL_ATUAL: true, JANELA_DEFINIDA: true,
                      JANELA_ABERTA_AGORA: true, VINCULO_COM_PORTFOLIO: true,
                      TEMPO_PARA_ACAO: true}
WHY_NOW_CODES = ['CADEIA_COMPLETA']
```

    O ESTADO NÃO VOLTOU. O QUE VOLTOU FOI COM UMA RAZÃO ATRÁS.

`ACT_NOW` exige agora **cinco** elos — a missão acrescentou dois:

```
SINAL ATUAL + JANELA DEFINIDA + JANELA ABERTA AGORA
            + VÍNCULO COM PORTFÓLIO + TEMPO PARA AÇÃO
```

`T30b` prova o elo novo: condição declarada com estado desconhecido **não** é
`ACT_NOW`.

---

## D, E, F, I, J · A inteligência que já estava no acervo

**Portfólio, produto a produto** (`PORTFOLIO_MATCHES`): `PRODUCT_ID`,
`ACTIVE_INGREDIENTS`, `MODE_OF_ACTION`, `CROP_FIT`, `TARGET_FIT`,
`REGIONAL_FIT`, `REGULATORY_FIT`, `WINDOW_FIT`, `VALIDATION_STATE`, `EVIDENCE`,
`RESTRICTIONS`, `MATCH_REASON`.

**`PRIMARY_MATCH` só com regra defensável** — a fonte nomeia a substância, ou há
um produto só. Sem isso, `UNKNOWN`. Medido: 17 casos com primário
(`UNICO_PRODUTO_DO_CATALOGO_NO_PAR`), **26 com `PRIMARY_MATCH = UNKNOWN`**.

> ⚠️ Achado comercial que o cartão antigo não mostrava: no caso testemunha a
> fonte recomenda **fenhexamid**, e a ADAMA **não tem fenhexamid** no acervo. O
> produto ligado ao par é `BANJO` (**fluazinam, FRAC 29**), que o rótulo
> ministerial autoriza para *vite × muffa grigia*. É alternativa declarada, não
> a molécula que o boletim nomeou — e isso é informação de venda, não detalhe.

**Papel de cada evidência** (`EVIDENCE_ROLES`): `SUPPORTS_DIRECTION`,
`SUPPORTS_WINDOW`, `SUPPORTS_PRODUCT_MATCH`, `SUPPORTS_SIGNAL`,
`BACKGROUND_ONLY`… incluindo os papéis que esfriam.

    UM SISTEMA QUE SÓ CLASSIFICA EVIDÊNCIA A FAVOR APRENDE A VENDER.

**Briefing** (`INTELLIGENCE_BRIEF`): sai em **código + valores**, nunca em frase
pronta — frase com variável dentro é frase nova a cada build e nasce sem
tradução. Os textos fixos vivem em `OPPORTUNITY-RULES.json`. Renderizado, o
caso testemunha lê:

> Pressão recente de ISSUE_BOTRYTIS em CROP_GRAPEVINE na REGION_EMILIA_ROMAGNA,
> sustentada por 8 sinais de campo e 3 fontes independentes.
> A condição que define o momento está declarada e o mesmo documento declara o
> estádio da cultura: a janela está aberta agora.
> Há 1 produto(s) do catálogo comercial ADAMA com rótulo ministerial no par.
> Ação: MARKET_DEVELOPMENT deve CONFIRM_RECOMMENDATION_IN_FIELD antes de
> qualquer ativação comercial.

---

## H · Mapa de ações

Cada linha traz `DEPARTMENT`, `ACTION_STATE`, `ACTION`, `WHY_CODE`, `EVIDENCE`,
`DEPENDENCY` e `NEXT_TRIGGER` — o elo que falta e o evento que o destravaria.
`SUPPLY` continua só entrando com fato publicado (`T37`).

---

## K · A promoção tudo-ou-nada — auditada, e só depois corrigida

`python3 scripts/v21_auditoria_da_promocao.py`

| classe | n | regra |
|---|---|---|
| `DEVERIA_PROMOVER` | **35** | o destino está vazio e a origem tem texto |
| `NAO_DEVERIA_PROMOVER` | 52 | o destino já está cheio: nada mudaria |
| `UNKNOWN` | **0** | — |

**A regra que separa os casos:** a guarda larga recusa promover porque
*qualquer* campo de tela existe; a guarda estreita — «não sobrescrever o
destino» — já existia uma linha abaixo e continua valendo.

    RESSALVA NÃO É DESCRIÇÃO. UMA NÃO PODE BLOQUEAR A OUTRA.

**Zero `UNKNOWN`** — a separação é total: todos os 35 estavam bloqueados por
`PERMANENT_CAVEAT`, que ressalva e não descreve.

**Impacto medido antes de aplicar** (cadeia rodada com a guarda estreitada):

- 35 registros ganham texto de tela;
- 4 sinais de campo reais deixam de chegar mudos ao motor;
- 2 pares observados novos (*oliveira × mosca da azeitona*, Veneto e Lazio), os
  dois `NEUTRAL_MENTION`;
- **0 oportunidades mudam de estado. 43 → 43.**

Com a separação provada e o impacto medido em zero, **a correção de uma linha
foi aplicada** e o comportamento novo está pinado em `T26`; `T26b` prova que a
guarda estreita continua impedindo sobrescrita. Reverter é trocar uma linha.

---

## L e M · Backfill preview, caso a caso

`python3 scripts/v21_backfill_preview.py` →
`data/samples/AUDITORIA-SOMBRA/V113-BACKFILL-PREVIEW.json`

O **antes** não é memória: é o pacote reconstruído num `git worktree --detach`
em `caa6937`, que reproduziu exatamente `BUILD_ID V21-473db7a54b90c382`.

| classe | n |
|---|---|
| `ENRIQUECIMENTO` | **37** |
| `CORRECAO` | **5** |
| `PROMOCAO` | **1** |
| `REBAIXAMENTO` | 0 |
| `SEM_MUDANCA` | 0 |

- **PROMOÇÃO (1)** — botrite × videira · Emilia-Romagna: `VALIDATE_NOW →
  ACT_NOW`, porque a evidência que já existia passou a ser lida.
- **CORREÇÃO (5)** — os casos onde o reprocessamento **encontrou no acervo** uma
  janela que o pacote anterior afirmava não existir.
- **ENRIQUECIMENTO (37)** — mesmo estado, com `WINDOW_DEFINED`,
  `PORTFOLIO_MATCHES`, `EVIDENCE_ROLES`, `INTELLIGENCE_BRIEF` e
  `WHAT_IS_MISSING` carregados.

Nenhum rebaixamento: nada do que o pacote anterior afirmava caiu.

---

## N · O que mudaria no portal hoje

A informação que alimentaria a tela, sem tocar a tela:

1. um cartão passa de `VALIDATE_NOW` a `ACT_NOW`, **com a cadeia visível**;
2. cinco cartões passam a mostrar **qual condição** define o momento e **se
   está aberta**, em vez de «no canonical window linked»;
3. 43 cartões passam a mostrar substância ativa, modo de ação, dose citada do
   rótulo, restrição regulatória com data, papel de cada evidência, briefing e
   **o que falta**;
4. 26 cartões passam a dizer `PRIMARY_MATCH = UNKNOWN` em vez de sugerir o
   primeiro produto da lista.

---

## O · O vão que sobrou, e só ele

`WHAT_IS_MISSING`, contado no acervo inteiro:

| falta | casos | classe |
|---|---|---|
| `OFFICIAL_AREA_NOT_CLIENT_SAFE` | 43 | **QA, não coleta** — a linha ISTAT existe |
| `REGION_NOT_DECLARED` | 26 | natureza do arquétipo (nacional/EU) |
| `NO_AGRONOMIC_TARGET` | 25 | idem |
| `INTENSITY_UNKNOWN` | 18 | **coleta** — boletim declara ocorrência, não incidência |
| `RECURRENCE_UNKNOWN` | 18 | **coleta** — o acervo é retrato, não série |
| `WINDOW_RULE_MISSING` | 12 | **coleta** — nenhuma fonte declara a condição |
| `WINDOW_STATE_UNKNOWN` | 5 | **coleta dirigida** — a condição existe, falta o estado |
| `COMMERCIAL_PRODUCT_MISSING` | 4 | catálogo |
| `DIRECTION_UNKNOWN` | 1 | leitura |
| `SIGNAL_NOT_RECENT` | 1 | recência |

**Próximo lote recomendado — pequeno e dirigido, 5 itens:** o estado da condição
para os quatro `WINDOW_STATE_UNKNOWN` que já são `SALES_READY` (a contagem de
armadilha da traça em Emilia-Romagna, as posturas da piralide no Friuli, a fase
de suscetibilidade da botrite em Toscana, o voo da carpocapsa no Veneto) e a
revisão de QA que libera a área ISTAT. **Nenhuma coleta grande foi aberta.**

---

## Suíte e contratos

**737 descobertos · 732 executados · 6 falhas · 2 erros** — as mesmas 8
anteriores a esta linha de missões. Provas da camada: **74/74**. Cadeia
`EXIT=0`, 0 violações de contrato, 0 campos só em português.

```
portal = NÃO TOCADO   produção = NÃO TOCADA   Vercel = NÃO TOCADO
publicação = NÃO      merge = NÃO             thresholds = NÃO ALTERADOS
segundo motor = NÃO   evidência bruta = INTACTA
```
