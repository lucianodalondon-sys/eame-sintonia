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
alteração (`MISSAO`, `SOURCE_ID`, `CAMPO`, `ANTES`, `DEPOIS`, `ORIGEM`, `PROVA`, `DECISAO`, `AT`).

### Bloco 2 — catálogo (D9, 23/09, bot Luciano por delegação do dono)

As linhas `MUDAR_PARA_Tx` e `RETIRAR_DO_UNIVERSO` da `PROPOSTA-CATALOGO-V1`
(`origin/catalogo-proposta-v1` @ **`0644a916`**, o head conferido pelo coordenador:
87 acções com prova — MANTER 34 · MUDAR 6 · RETIRAR 47; a Agrofarma rebaixada a
UNKNOWN), **só com prova íntegra** (cada ficheiro de prova
existe em disco e o sha256 bate). `UNKNOWN` e `MANTER`: intocados.

* **MUDAR** muda `TERRITORY` e guarda `CATALOGO_D9.UNIVERSO_ANTERIOR`. O
  `SOURCE_ID` não muda (é identidade). É a **única** excepção ao «nunca muda grupo T»,
  e o invariante só a aceita para as fontes que a D9 autorizou e cuja prova bateu.
* **RETIRAR** marca `ESTADO_CATALOGO = RETIRADA_POR_DECISAO`, reversível, com
  proveniência. **Nunca apaga.** Se a prova tiver notícia `SINTONIA_RELEVANT = YES`,
  vale a D2 (REROUTE) e a linha SALTA.
* Uma fonte retirada **nunca entra** na tabela do coletor (nem na 1.ª nem na 2.ª passagem).
* Ledger com `DECISAO = D9`.

O pacote imprime o commit de onde leu o catálogo e **avisa** se a branch tiver
andado desde `0644a916`.

⚠️ **Contagem da proposta ≠ contagem da D9.** O ficheiro tem **6** MUDAR e **102**
UNKNOWN; o texto da D9 diz 7 e 101. Usei o ficheiro (último commit da branch:
`0644a916`, «regenerado após a conferência das provas»). As **53** linhas
MUDAR/RETIRAR têm prova íntegra em disco.

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
1.ª passagem (--escrever):  livro APLICA 68 (17 receitas + 51 catálogo D9) · livro SALTA 2
                            tabela APLICA 5 · tabela SALTA 11                 → 73 alterações no ledger (52 D9)
2.ª passagem (--escrever):  livro JA_APLICADA 68 · tabela JA_APLICADA 4 · 0 alterações
                            sha256 dos dois livros e do ledger IGUAIS antes e depois da 2.ª
IDEMPOTENTE = YES
```

⚠️ **A primeira versão do bloco D9 não era idempotente, e o ensaio apanhou-o.**
A IT-T12-041 (BURA) era posta na tabela pelo bloco 1 (rota da M3) e retirada
pelo bloco 2; na 2.ª passagem o livro já dizia «retirada», o bloco 2 respondia
`JA_APLICADA`, e o bloco 1 punha-a outra vez na tabela — **1 alteração na 2.ª
passagem**. Cura na raiz: fonte retirada nunca entra na tabela. Prova nova
cobre as duas passagens.

**O catálogo D9 no ensaio:** 51 aplicadas no livro (6 MUDAR + 45 RETIRAR), 1 na
tabela (IT-T2-030 Nomisma → T10, que já lá estava). SALTAM 2: **IT-T12-076**
(D2: a prova tem notícia relevante — REROUTE, não retirar) e **IT-T2-017**
(não está no livro vivo).

**As 17 do livro:** 15 `LINK_PATTERN` (14 da V1 + IT-T10-026 da V2) e 2
`INDEX_URL` (IT-T2-039, IT-T12-044). Todas com a prova a bater.

**As 5 da tabela:** IT-T10-022 (aquisição nova, canário G1), IT-T2-051, IT-T2-034,
IT-T9-021 (rotas da M3), IT-T2-030 (universo T10 pela D9). A IT-T12-041 tinha
rota provada, mas a D9 retira-a: não entra.

**As que a tabela salta, com motivo (11):**

* IT-T7-100 e IT-T2-056 — **DUPLICADAS** (mesmo documento que IT-T7-043 e IT-T2-051);
* IT-T12-057, IT-T12-074 — o canário da M3 provou a aquisição **antiga**, e a
  receita mudou: sem canário novo, não entram;
* IT-T10-018, IT-T7-017, IT-T7-033, IT-T7-042, IT-T7-043 — já na tabela; o
  canário da M3 é de outra aquisição; ficam como estão;
* IT-T10-018 (2.º motivo) — a receita mudou no livro sem canário da aquisição
  nova: a **tabela fica com a receita velha**, que já reconhece a notícia.
* IT-T12-041 — rota provada, mas RETIRADA_POR_DECISAO (D9) neste mesmo pacote.

⚠️ IT-T9-021 entra na tabela porque a rota está provada — é desbloqueio
**técnico**; não passa no funil (a feira escolar não é relevante). O pacote não
decide relevância.

⚠️ **O coletor não lê a marca `RETIRADA_POR_DECISAO`.** Neste ensaio nenhuma
fonte retirada estava na tabela do coletor, por isso não há efeito; mas se uma
estivesse, o coletor continuaria a colhê-la. Fazer o coletor/portão respeitar a
marca é da M5, não deste pacote.

### O funil G0 sobre as cópias alteradas

```
                      A    B    C    D    E    PASSAM_TUDO
antes do pacote       45   14    8    6    6    6   (já com a D8 revista: Chianti conta)
depois do pacote      45   16   10    8    8    8   (receitas + rotas + catálogo D9)
```

```
PASSAM_TUDO (depois) = 8 fontes = 8 sites distintos
  IT-T10-018 myfruit · IT-T10-021 Plantgest · IT-T10-022 Zootecnica · IT-T2-051 Arpae ·
  IT-T7-017 Riunite · IT-T7-033 Chianti · IT-T7-041 Bonifica Romagna · IT-T7-043 Agrofarma
```

Esperado «até 9 sites»: a 9.ª seria a **Granaria**, parada no canário (robots
mudo). Nenhum degrau foi baixado; o que mudou foram receitas e linhas de
tabela com prova. O catálogo D9 **não muda o funil**: nenhuma das 8 é retirada ou
muda de gaveta. O funil passou a ler a gaveta do **contrato** (não do código da
fonte), a excluir as retiradas, e a deixar **T12 fora da micro-coleta** até haver
≥ 20 exemplos (D9.6).

---

## 3 — PROVAS

`tests/test_aplicar_desbloqueio.py` — **20 provas**, dados sintéticos, sem rede.
Bloco 1:
prova que bate aplica nos dois livros · página alterada / em falta / padrão
que casa capa / livro mudado → SALTA · canário de outra aquisição não entra ·
duas fontes no mesmo documento → só a primeira · idempotente (e a 2.ª passagem
diz `JA_APLICADA`) · nunca muda grupo T · nunca retira fonte nem muda outro campo.
Bloco D9: MUDAR muda o grupo e guarda o anterior (livro e tabela) · RETIRAR marca e
não apaga · retirada com notícia relevante SALTA pela D2 · prova adulterada ou em
falta SALTA · UNKNOWN e MANTER intocados · universo actual ≠ proposta SALTA ·
idempotente · retirada no mesmo pacote não entra na tabela (nas duas passagens) ·
fora das autorizadas o grupo T continua fechado.

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
| D9: prova não conferida | sim | morto | — |
| D9: retirada relevante aceite | sim | morto | — |
| D9: autorização para todas as fontes | sim | morto | — |
| D9: retirada entra na tabela | sim | morto | — |
| D9: retirar sem idempotência | sim | morto | — |

Os dois sobreviventes **não eram buracos**: a trava do grupo T era redundante
com a comparação do contrato inteiro, e sem o ramo `JA_APLICADA` a 2.ª passagem
ainda não mudava nada — mas dizia «o livro mudou» em vez de «já aplicada».
Os testes passaram a exigir o **motivo** (`grupo T`; `JA_APLICADA`), e os dois
morreram.

```
MUTATION = 11 mortos / 11 (2 depois de apertar os testes)
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
                         + 53 linhas de catálogo D9 (6 MUDAR + 47 RETIRAR)
APLICAVEIS_COM_PROVA   = 73 no ensaio (livro 17 receitas + 51 catálogo · tabela 5)
SALTADAS               = 11 na tabela (2 duplicadas · 2 canário de aquisição antiga · 5 já na tabela
                         com canário de outra aquisição · 1 receita mudada sem canário novo ·
                         1 retirada pela D9) · 2 no catálogo (IT-T12-076 D2 · IT-T2-017 fora do livro)
                         + Granaria (canário UNKNOWN: robots mudo)
IDEMPOTENTE            = YES (2.ª passagem: 0 alterações, sha256 iguais)
GRUPO_T_ALTERADO       = 0 fora da D9 · 6 pela D9 (MUDAR, autorizadas, prova íntegra)
FUNIL_APOS (cópia)     = A 45 · B 16 · C 10 · D 8 · E 8
PASSAM_TUDO            = 8 fontes = 8 sites (myfruit, Plantgest, Zootecnica, Arpae, Riunite,
                         Chianti, Bonifica Romagna, Agrofarma)
CANARIO_CONTRATOS_NOVOS = IT-T7-100 ROUTE_PROVEN (duplicada) · IT-T10-026 UNKNOWN · IT-T10-022 ROUTE_PROVEN
EGRESS                 = IT 3/3 (149.22.91.171 Palermo)
MUTATION               = 11/11 mortos
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
a caixa aplicou 73 correcções. Correndo outra vez, aplicou **zero**: não faz
estragos se alguém a correr duas vezes. E ela nunca muda a "gaveta" de uma fonte
nem apaga nenhuma.

Com a caixa aplicada, as fontes prontas para o teste pequeno passam de **6 para 8**,
todas de sites diferentes. Ficou uma de fora: a Granaria (cereais), cujo site
não respondeu ao pedido de autorização. Pode tentar-se de novo no dia.

Juntei também à caixa a sua decisão D9 sobre o catálogo: **51 fontes** mudam
de gaveta ou ficam marcadas como retiradas. Nenhuma é apagada, e todas podem
voltar. Uma fonte que o catálogo mandava retirar ficou, porque tinha uma notícia
que serve ao Sintonia (a sua regra D2 passa à frente).

Descobri também que o sistema guarda **duas cópias** de cada receita — uma do
curador e outra do coletor. Corrigir só uma deixava o coletor a trabalhar com a
receita velha. A caixa corrige as duas, e só quando há prova para as duas.

---

## ADENDA — as 2 linhas que desapareciam na 2.ª passagem (pergunta do coordenador)

O coordenador mediu 16 linhas de tabela na 1.ª passagem (5 APLICA + 11 SALTA) e
14 na 2.ª (4 JA_APLICADA + 10 SALTA). As duas eram:

1. **IT-T2-030** (D9, MUDAR → T10). Com o livro já mudado, o bloco D9 dizia
   `JA_APLICADA` e **não olhava para a tabela**. Aqui o resultado estava certo
   (a tabela também já estava mudada), mas havia um **defeito de comportamento**
   por trás: se o livro chegasse aplicado e a tabela não, a tabela nunca seria
   corrigida. Agora o bloco D9 confere a tabela nas duas passagens: `APLICA` se
   lhe falta a marca, `JA_APLICADA` se já a tem.
2. **IT-T10-018** (aviso «a receita mudou no livro sem canário novo»). O pacote
   comparava o livro **antes/depois da passagem**, não o livro com a tabela; na
   2.ª passagem o livro já não muda e o aviso sumia — com a divergência ainda lá.
   Agora compara-se o livro com a tabela, só para as fontes a que o pacote muda a
   receita.

Depois da correcção, no mesmo ensaio: **1.ª passagem tabela 5 APLICA + 11 SALTA;
2.ª passagem 5 JA_APLICADA + 11 SALTA — as mesmas 16 linhas**, 0 alterações.
Provas novas: as duas passagens reportam as mesmas linhas; livro aplicado com
tabela por aplicar corrige a tabela; a divergência livro/tabela aparece nas duas
passagens. 23/23. Os dois comportamentos antigos, repostos como mutantes (com
execução provada), põem provas a vermelho.
