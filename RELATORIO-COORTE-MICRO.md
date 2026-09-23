# RELATÓRIO — MISSÃO G0 · A COORTE DA MICRO-COLETA NO UNIVERSO INTEIRO

Branch `coorte-micro-v1`, a partir de `9925bfaf`. Motor: `claude-opus-5-5`.

```
NÃO CORREU COLLECTION · NADA NA SALA · DB_WRITES = 0
catálogo · Admission · detector · micro_coleta.py = INTOCADOS
Nenhuma régua baixada: os desbloqueios só removem bloqueios com dono e decisão conhecidos
```

---

## 0 — DE ONDE VEM O UNIVERSO

Serviço vivo lido **por cópia**: `source-curator-service-v1` @ `9a82197c`, 03:36Z
(`%TEMP%\curator-snap-20260923T033656Z`; o `LIFECYCLE-LEDGER` tem o mesmo sha256
que às 02:51Z: `c3888c0b…`).

```
UNIVERSO = 134 fontes (dedup por SOURCE_ID) =
             42 READY no livro vivo
           ∪ 17 ELIGIBLE pelo gate desta linha (READY_CURRENT 21, 4 com revisão humana)
           ∪ 15 da M3 (rotas-elegiveis-v1 @ 88ce30a8)
           ∪ 121 do censo das receitas (6-PREP-d)
Fora: candidatas sem SOURCE_ID — não há contrato para medir.
```

Lista em `scripts/coorte_micro/UNIVERSO-G0.json`.

---

## 1 — O FUNIL A→E (`scripts/coorte_micro/funil.py` → `FUNIL-COORTE-MICRO-V1.json`)

| degrau | pergunta | regra | em cadeia | sozinho |
|---|---|---|---|---|
| **A** | está pronta? | READY no livro vivo (canário do worker) **ou** READY_CURRENT nesta linha (régua dos 4 passos). Só READY_LEGACY não passa. Não se decide qual dos dois manda (é da M5) | **45** | 45 |
| **B** | a rota é executável? | contrato na tabela do coletor + receita web para o universo + sem bloqueio vivo/M3 | **14** | 14 |
| **C** | a receita reconhece uma notícia **real**? | uma matéria **lida** da fonte casa o `LINK_PATTERN` que o coletor usa. Sem matéria lida = NÃO SEI, não passa | **7** | 13 |
| **D** | é relevante (D2)? | `SINTONIA_RELEVANT = YES` (decisão do dono > leitura minha > 3b). Idioma não exclui (D3) | **5** | 11 |
| **E** | não é propaganda de marca? | IT-T7-017, IT-T7-033, IT-T7-042 fora até decisão do dono | **3** | 131 |

```
PASSAM_TUDO = 3   IT-T10-018 myfruit (T10) · IT-T10-021 Plantgest (T10 → REROUTE T7) ·
                  IT-T7-043 Agrofarma/Federchimica (T7 → REROUTE T10/T9)
```

**Onde cada fonte pára** (primeiro degrau que falha): A 89 · B 31 · C 7 · D 2 · E 2 · passa 3.

### Porque param

* **A (89)** — `CONTRACTED_CANARY_FAILED` 78 (**69** com `EMPTY_LIST`: a receita
  não reconhece nada da entrada), `CAPABILITY_BLOCK` 6, `CONTRACT_READY_ROUTE_BLOCKED` 2,
  `RETRY_AFTER` 2, `AUTH_BLOCK` 1.
* **B (31 das prontas)** — `NEEDS_CONTRACT` 24 (fora da tabela do coletor; **7**
  com rota já provada pela M3, por aplicar), `CAPABILITY_BLOCK` 4, `MISSING_ROUTE` 3
  (sem receita web para T12/T8/T9).
* **C (7)** — 4 **sem matéria lida** (IT-T5-039, IT-T7-031, IT-T7-040, IT-T7-041 — a
  VPN caiu antes de lá chegar); IT-T10-022 (receita não casa `/featured/…`; a V1
  corrige); IT-T10-020 (não casa; relevância NÃO SEI); IT-T7-021 (a página lida é um
  projecto único; família < 2 → NÃO SEI).
* **D (2)** — IT-T2-030 (a rota da Nomisma trouxe imobiliário e BCE: NO);
  IT-T7-042 (NÃO SEI, e é marca).
* **E (2)** — IT-T7-017 e IT-T7-033: **o dono já as deu como relevantes**
  (gabarito itens 9 e 10, REROUTE), mas a exclusão por marca é decisão dele.

### A relevância, com base declarada (`ROTULOS-RELEVANCIA-G0.json`)

21 fontes prontas com notícia lida, julgadas pelas duas perguntas separadas (D2).
**BASE = DONO** em 4 (IT-T10-018, IT-T10-022, IT-T7-017, IT-T7-033); nas outras 17
é **leitura minha**, quase sempre sobre **uma** notícia — humano-proposto, precisa
de visto.

⚠️ **A 3b tinha tirado a Zootecnica por idioma.** A lei D3 proíbe-o e o dono já
validou duas notícias dela (itens 5 e 6). Aqui a decisão do dono vence a 3b.
Também **IT-T2-051** (Arpae): a 3b tirou-a por falta de régua T2, não por
assunto; a notícia (captações de água após eventos meteorológicos) é relevante.

---

## 2 — ABAIXO DE 10: O QUE CORTA MAIS, E O QUE DESBLOQUEIA

```
MAIOR_CORTE = A (89 de 134 não estão prontas; 69 por EMPTY_LIST = a receita)
              e, dentro das prontas, B (31 de 45: 24 sem contrato na tabela do coletor)
```

**Desbloqueios, por ordem de rendimento** — simulados em memória
(`funil.desbloqueios`); nenhum mexe em A nem em D por conta própria:

| # | desbloqueio | dono | fontes | acumulado |
|---|---|---|---|---|
| 1 | decidir a marca das 2 que o dono já deu como relevantes (REROUTE) | **dono** | +2 · IT-T7-017, IT-T7-033 | **5** |
| 2 | aplicar a PROPOSTA-RECEITAS-V1 (6-PREP-d) | Curator/rotas, depois da M5 | +1 · IT-T10-022 | **6** |
| 3 | aplicar o onboarding das rotas provadas pela M3 | coordenador, depois da M5 | +1 · IT-T2-051 | **7** |
| 4 | contrato na tabela do coletor + receita V2 (**2 passos**) | Curator + coordenador | +1 · IT-T10-026 Granaria | **8** |
| 5 | **ler** uma notícia das 4 prontas e executáveis sem página (precisa de VPN) | coordenação | **até** +4 · IT-T5-039, IT-T7-031, IT-T7-040, IT-T7-041 — sem garantia: C e D por medir | **até 12** |
| 6 | canário novo nas 69 `EMPTY_LIST` depois da V1 (12 delas têm proposta) + régua T2/T12 (M3c) + receita web T12 | vários | **NÃO SEI** — não se conta sem medir | — |

```
DESBLOQUEIOS: certos → 8 fontes (1–4) · com a VPN → até 12 (5) · o resto não se conta sem canário
```

⚠️ Com os desbloqueios 1–4 a coorte teria **8 fontes**, e **3 delas são de
vinho/marca ou de mercado muito próximo** (IT-T7-017 Riunite, IT-T7-033 Chianti,
IT-T10-018 myfruit). A variedade pedida pelo mandato não fica garantida.

---

## 3 — RECEITAS NOVAS (`curadoria/PROPOSTA-RECEITAS-V2.json`, NÃO APLICADA)

Pelo método da 6-PREP-d, sem alteração, só para fontes **relevantes** paradas em C:

```
RECEITAS_NOVAS = 1 com prova
  IT-T10-026 Granaria Milano   /comunicazione/<slug>   matéria lida 1/1 · capas 0/1
  (IT-T10-022 repete a proposta da V1)
NÃO SEI: IT-T12-019 ERSAF e IT-T7-021 Villoresi — a página lida é um projecto único,
         família < 2 na entrada; IT-T9-019 SCAM — sem contrato no livro vivo
```

---

## 4 — REDE

```
EGRESS = IT em 7 de 8 idas (149.22.91.172 Palermo) · a 8.ª mediu BR (177.95.91.48 Londrina)
         e a recolha PAROU antes de qualquer pedido a esse site → 0 pedidos pelo Brasil
         A VPN caiu durante a missão e continuava em BR no fim. Das 27 fontes prontas
         sem página: 22 buscáveis (uma por domínio, com contrato) · 7 visitadas ·
         15 por buscar por causa da VPN · 5 não buscáveis (sem contrato no livro vivo
         ou domínio repetido).
páginas  10 páginas de 7 sites em ~/coorte-paginas/ (fora do Git e da Sala), sha256 no MANIFESTO
```

---

## 5 — PROVAS

`tests/test_funil_coorte.py` — **13 provas**, dados sintéticos com resposta
conhecida à partida, sem rede nem git.

**Lei de mutação Python** (mandato): cache `__pycache__` apagada antes e depois,
`PYTHONDONTWRITEBYTECODE=1`, processo novo, mutação conferida por `git diff`, e
**prova de execução** (o código mutado escreve um ficheiro-marca):

| mutante | entrou | executou | resultado |
|---|---|---|---|
| A aceita READY_LEGACY | sim | sim | morto |
| C passa sem matéria lida | sim | sim | morto |
| a lista de marca esquecida | sim | sim | morto |
| um desbloqueio baixa A | sim | sim | morto |

⚠️ Na primeira tentativa o 4.º mutante tinha um erro meu de indentação e **não
executou**. Não o contei como sobrevivente: refi-lo e confirmei a execução.

---

## 6 — LIMITES

* A relevância de 17 fontes é leitura minha sobre **uma** notícia.
* O degrau C depende da tabela do coletor desta linha; o livro vivo tem outra
  (`italy_contracts_curator.json`). Usei a do coletor, que é a que corre.
* A decisão «qual canário manda» (worker vivo ou régua dos 4 passos) não foi
  tomada: as duas ficam escritas por fonte (`A_PORQUE`).

---

## ENTREGA

```
UNIVERSO       = 134 (dedup)
FUNIL          = A 45 · B 14 · C 7 · D 5 · E 3
PASSAM_TUDO    = 3 — IT-T10-018, IT-T10-021, IT-T7-043
MAIOR_CORTE    = A (89: 69 EMPTY_LIST = receita); dentro das prontas, B (24 sem contrato no coletor)
DESBLOQUEIOS   = 1) dono decide marca +2 → 5 · 2) aplicar receitas V1 +1 → 6 ·
                 3) aplicar rotas da M3 +1 → 7 · 4) contrato + receita V2 +1 → 8 ·
                 5) ler 4 prontas sem página (VPN) até +4 → até 12 · 6) o resto: NÃO SEI sem canário
RECEITAS_NOVAS = 1 com prova (IT-T10-026)
EGRESS         = IT 7/8 · 8.ª BR, parada antes do pedido · 0 pedidos BR · VPN em baixo no fim
PRECISA_REDE_IT = 24 das 45 prontas sem notícia lida (88 das 134 no universo) — marcadas no
                 FUNIL (C_PORQUE); nada foi buscado depois da queda, a pedido da coordenação
```

---

## EM PALAVRAS SIMPLES

Queríamos 10 a 20 fontes prontas para o teste pequeno. Fui ver **134 fontes**
e passei cada uma por 5 peneiras, uma atrás da outra:

1. está pronta? → **45**
2. o coletor sabe lá ir? → **14**
3. a receita reconhece uma notícia de verdade? → **7**
4. o assunto serve ao Sintonia? → **5**
5. não é propaganda de marca? → **3**

Sobram **3 fontes**: preços de fruta, técnica de pomares, e a associação
italiana dos fabricantes de agroquímicos.

**A peneira que mais corta é a primeira.** 89 fontes nem estão prontas, e a
maioria por culpa da receita (a mesma que medi na missão anterior). A relevância
quase nunca é o problema: quando uma fonte chega a ser lida, costuma servir.

**Como chegar a 8**, sem baixar nenhuma exigência:

- você decide sobre as 2 fontes de vinho que já disse que servem;
- aplicam-se as receitas corrigidas;
- aplicam-se as rotas já provadas;
- dá-se contrato a uma associação de cereais.

**Com a VPN italiana ligada, talvez 12.** Faltam ler 4 fontes que já estão
prontas.

⚠️ **A VPN caiu a meio desta missão.** O programa viu que a internet tinha
passado a sair pelo Brasil e parou antes de pedir fosse o que fosse. Ficaram 15
fontes por ler por causa disso.
