# RELATÓRIO — MISSÃO G1 · PACOTE DE DESBLOQUEIO TÉCNICO DA COORTE

Branch `desbloqueio-coorte-v1`, a partir de `1a6d5bfa`. Motor: `claude-opus-5-5`.

```
SERVIÇO VIVO NÃO TOCADO (só cópias) · NADA NA SALA · COLLECTION NÃO CORREU
livro do Curator e tabela do coletor da árvore: NÃO ESCRITOS — o ensaio foi em cópias
```

---

## 0 — O QUE O PACOTE É

`scripts/desbloqueio/aplicar_desbloqueio.py` — aplica-se **uma vez, no cutover**,
por um só comando, sobre o livro corrente.

**Dois livros, porque o coletor tem a sua própria cópia da receita:**

| livro | o que o pacote muda | com que prova |
|---|---|---|
| contratos do Curator (`--livro`) | só `ACQUISITION.LINK_PATTERN` e `ACQUISITION.INDEX_URL`, pelas PROPOSTA-RECEITAS-V1 (6-PREP-d) e V2 (G0) | valor actual = `ANTES` da proposta · sha256 da página guardada = manifesto · o padrão casa **todas** as matérias confirmadas e **nenhuma** das 109 capas do GABARITO-CAPA-V1 · guarda contra padrão genérico · INDEX_URL: página buscada, sha conferido, ≥ 10 links com forma de matéria |
| tabela do coletor (`--tabela`) | acrescenta linha, ou muda `ACQUISITION` | canário `ROUTE_PROVEN` com **exactamente** a aquisição que fica (M3 ou G1), e um documento = uma fonte (duplicadas ficam de fora). A linha é construída pela `linha_da_tabela` da **peça da M3** (`curadoria/onboardar_rotas_provadas.py`, lida da árvore ou de `origin/rotas-elegiveis-v1`) |

**Invariantes** (se falhar um, nada é escrito, exit 4): nunca muda `TERRITORY`
(grupo T) nem `SOURCE_ID`; nunca retira fonte (D5 é do dono); no livro só
mudam os dois campos; na tabela só se acrescenta ou se muda a aquisição.

Com `--escrever`: grava os dois livros e acrescenta ao ledger uma linha por
alteração (`MISSAO`, `SOURCE_ID`, `CAMPO`, `ANTES`, `DEPOIS`, `ORIGEM`, `PROVA`, `AT`).

---

## 1 — O DESBLOQUEIO 1: AS 2 FONTES «SEM CONTRATO»

Medido: **as duas já têm contrato no livro do Curator**. O que lhes falta é a
linha na **tabela do coletor** — a mesma ponte das rotas da M3. A peça do bot
(`worker.etapa_build_contract`) escreve contratos no livro do Curator para
fontes que **não** têm nenhum; não era a peça certa aqui. A certa é a da M3:
canário real + `linha_da_tabela`.

**Canário** (`scripts/desbloqueio/canario_desbloqueio.py`): a peça da M3
(`medidas/canario_rotas_elegiveis.provar`) executada em memória, sem cópia,
com `MAX_ALVOS = 1` → robots + índice + 1 alvo = **3 pedidos por site**; o
contrato provado é o que o pacote vai deixar (V1/V2 aplicada em memória).

```
CANARIO_CONTRATOS_NOVOS
  IT-T7-100  Agrofarma    ROUTE_PROVEN  3 pedidos — mas DUPLICADA: o documento provado já é
                                        da IT-T7-043 (mesmo site) → o pacote NÃO a põe na tabela
  IT-T10-026 Granaria     UNKNOWN       robots ilegível deste egresso (2 tentativas, URLError);
                                        não insisti, para não passar de 3 pedidos → SALTA
  IT-T10-022 Zootecnica   ROUTE_PROVEN  3 pedidos, com a receita V1 → a tabela muda a aquisição
EGRESS = IT (149.22.91.171 Palermo), medido antes de cada site
```

**Resultado honesto do desbloqueio 1: zero sites novos.** A Granaria fica por
provar (repetir o canário no cutover) e a Agrofarma é a mesma fonte com dois
códigos — decisão de identidade no Atlas, não de rota.

---

## 2 — ENSAIO NUMA CÓPIA DO LIVRO VIVO

Cópias em `%TEMP%\ensaio-g1\`: o livro do Curator do serviço vivo (cópia
congelada de `9a82197c`, 03:36Z) e a tabela do coletor desta árvore.

```
1.ª passagem (--escrever):  livro APLICA 17 · tabela APLICA 5 · tabela SALTA 10  → 22 alterações no ledger
2.ª passagem (--escrever):  livro JA_APLICADA 17 · tabela JA_APLICADA 5 · 0 alterações
                            sha256 dos dois livros e do ledger IGUAIS antes e depois da 2.ª
IDEMPOTENTE = YES
```

**As 17 do livro:** 15 `LINK_PATTERN` (14 da V1 + IT-T10-026 da V2) e 2
`INDEX_URL` (IT-T2-039, IT-T12-044). Todas com a prova a bater.

**As 5 da tabela:** IT-T10-022 (aquisição nova, canário G1), IT-T2-051, IT-T2-034,
IT-T12-041, IT-T9-021 (rotas da M3).

**As 10 que a tabela salta, com motivo:**

* IT-T7-100 e IT-T2-056 — **DUPLICADAS** (mesmo documento que IT-T7-043 e IT-T2-051);
* IT-T12-057, IT-T12-074 — o canário da M3 provou a aquisição **antiga**, e a
  receita mudou: sem canário novo, não entram;
* IT-T10-018, IT-T7-017, IT-T7-033, IT-T7-042, IT-T7-043 — já na tabela; o
  canário da M3 é de outra aquisição; ficam como estão;
* IT-T10-018 (2.º motivo) — a receita mudou no livro sem canário da aquisição
  nova: a **tabela fica com a receita velha**, que já reconhece a notícia.

⚠️ IT-T12-041 e IT-T9-021 entram na tabela porque a rota está provada — é
desbloqueio **técnico**. Não passam no funil por outras razões (T12 sem receita
web; a feira escolar sem relevância). O pacote não decide relevância.

### O funil G0 sobre as cópias alteradas

```
                      A    B    C    D    E    PASSAM_TUDO
antes do pacote       45   14    8    6    6    6   (já com a D8 revista: Chianti conta)
depois do pacote      45   16   10    8    8    8
```

```
PASSAM_TUDO (depois) = 8 fontes = 8 sites distintos
  IT-T10-018 myfruit · IT-T10-021 Plantgest · IT-T10-022 Zootecnica · IT-T2-051 Arpae ·
  IT-T7-017 Riunite · IT-T7-033 Chianti · IT-T7-041 Bonifica Romagna · IT-T7-043 Agrofarma
```

Esperado «até 9 sites»: a 9.ª seria a **Granaria**, parada no canário (robots
mudo). Nenhum degrau foi baixado; o que mudou foram receitas e linhas de
tabela com prova.

---

## 3 — PROVAS

`tests/test_aplicar_desbloqueio.py` — **11 provas**, dados sintéticos, sem rede:
prova que bate aplica nos dois livros · página alterada / em falta / padrão
que casa capa / livro mudado → SALTA · canário de outra aquisição não entra ·
duas fontes no mesmo documento → só a primeira · idempotente (e a 2.ª passagem
diz `JA_APLICADA`) · nunca muda grupo T · nunca retira fonte nem muda outro campo.

**Lei de mutação Python**: cache apagada antes e depois,
`PYTHONDONTWRITEBYTECODE=1`, processo novo, mutação conferida, **execução
provada** por ficheiro-marca.

| mutante | executou | 1.ª bateria | depois |
|---|---|---|---|
| sha256 não conferido | sim | morto | — |
| capa do gabarito aceite | sim | morto | — |
| `ANTES` não conferido | sim | morto | — |
| grupo T livre | sim | **sobreviveu** | morto |
| duplicada aceite | sim | morto | — |
| sem idempotência | sim | **sobreviveu** | morto |

Os dois sobreviventes **não eram buracos**: a trava do grupo T era redundante
com a comparação do contrato inteiro, e sem o ramo `JA_APLICADA` a 2.ª passagem
ainda não mudava nada — mas dizia «o livro mudou» em vez de «já aplicada».
Os testes passaram a exigir o **motivo** (`grupo T`; `JA_APLICADA`), e os dois
morreram.

```
MUTATION = 6 mortos / 6 (2 depois de apertar os testes)
```

---

## 4 — O COMANDO DE CUTOVER

A correr **nesta máquina** (as provas são páginas guardadas em `~/detector-capa-gabarito`,
`~/receitas-paginas`, `~/coorte-paginas`; noutra máquina tudo SALTA com
«prova indisponível»), na raiz da árvore unificada, depois da M5:

```
# 1) opcional, com VPN IT: repetir o canário (a Granaria pode passar)
py scripts/desbloqueio/canario_desbloqueio.py --contratos=curadoria/italy_contracts_curator.json --escrever
# 2) ver o que muda
py scripts/desbloqueio/aplicar_desbloqueio.py --livro=curadoria/italy_contracts_curator.json --tabela=regras/italy_contracts_onboarded.json
# 3) aplicar (uma vez; uma 2.ª corrida dá 0)
py scripts/desbloqueio/aplicar_desbloqueio.py --livro=curadoria/italy_contracts_curator.json --tabela=regras/italy_contracts_onboarded.json --escrever
```

Provado nesta árvore (livro mais velho que o vivo), sem `--escrever`: o
comando corre e **salta 3 receitas** porque o valor actual não é o `ANTES` da
prova — a trava a funcionar sobre um livro diferente do medido.

⚠️ O livro do Curator é escrito pelo bot vivo. Aplicar com o bot a correr é
uma corrida entre dois escritores: parar o bot no cutover (é do coordenador).

---

## ENTREGA

```
ALTERACOES_PROPOSTAS   = 17 receitas (15 LINK_PATTERN + 2 INDEX_URL) + 3 contratos/rotas do desbloqueio 1
                         + 13 rotas provadas pela M3 (de 15 medidas) candidatas à tabela
APLICAVEIS_COM_PROVA   = 22 no ensaio (17 livro + 5 tabela)
SALTADAS               = 10 na tabela (2 duplicadas · 2 canário de aquisição antiga · 5 já na tabela
                         com canário de outra aquisição · 1 receita mudada sem canário novo)
                         + Granaria (canário UNKNOWN: robots mudo)
IDEMPOTENTE            = YES (2.ª passagem: 0 alterações, sha256 iguais)
GRUPO_T_ALTERADO       = 0 (invariante + prova + mutante morto)
FUNIL_APOS (cópia)     = A 45 · B 16 · C 10 · D 8 · E 8
PASSAM_TUDO            = 8 fontes = 8 sites (myfruit, Plantgest, Zootecnica, Arpae, Riunite,
                         Chianti, Bonifica Romagna, Agrofarma)
CANARIO_CONTRATOS_NOVOS = IT-T7-100 ROUTE_PROVEN (duplicada) · IT-T10-026 UNKNOWN · IT-T10-022 ROUTE_PROVEN
EGRESS                 = IT 3/3 (149.22.91.171 Palermo)
MUTATION               = 6/6 mortos
COMANDO_DE_CUTOVER     = py scripts/desbloqueio/aplicar_desbloqueio.py --livro=curadoria/italy_contracts_curator.json --tabela=regras/italy_contracts_onboarded.json --escrever
```

---

## EM PALAVRAS SIMPLES

Preparei uma **caixa de correcções** para aplicar no dia da mudança, de uma
só vez.

Cada correcção só entra se a prova ainda estiver boa: a notícia que guardei
continua igual, a receita nova reconhece a notícia verdadeira, e não confunde
nenhuma das 109 páginas de índice que conhecemos. Se alguma coisa mudou entretanto,
a caixa não força: salta essa correcção e diz porquê.

Experimentei numa **cópia** — nada foi mexido no sistema de verdade. Na cópia,
a caixa aplicou 22 correcções. Correndo outra vez, aplicou **zero**: não faz
estragos se alguém a correr duas vezes. E ela nunca muda a "gaveta" de uma fonte
nem apaga nenhuma.

Com a caixa aplicada, as fontes prontas para o teste pequeno passam de **6 para 8**,
todas de sites diferentes. Ficou uma de fora: a Granaria (cereais), cujo site
não respondeu ao pedido de autorização. Pode tentar-se de novo no dia.

Descobri também que o sistema guarda **duas cópias** de cada receita — uma do
curador e outra do coletor. Corrigir só uma deixava o coletor a trabalhar com a
receita velha. A caixa corrige as duas, e só quando há prova para as duas.
