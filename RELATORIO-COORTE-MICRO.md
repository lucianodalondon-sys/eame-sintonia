# RELATÓRIO — MISSÃO G0 · A COORTE DA MICRO-COLETA NO UNIVERSO INTEIRO

Branch `coorte-micro-v1`, a partir de `9925bfaf`. Motor: `claude-opus-5-5`.

```
NÃO CORREU COLLECTION · NADA NA SALA · DB_WRITES = 0
catálogo · Admission · detector · micro_coleta.py = INTOCADOS (git diff desde 9925bfaf: vazio)
Nenhuma régua baixada: os desbloqueios só removem bloqueios com dono e decisão conhecidos
```

---

## 0 — DE ONDE VEM O UNIVERSO

Serviço vivo lido **por cópia**: `source-curator-service-v1` @ `9a82197c`, 03:36Z
(`%TEMP%\curator-snap-20260923T033656Z`; `LIFECYCLE-LEDGER` com o mesmo sha256 das
02:51Z: `c3888c0b…`).

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
| **A** | está pronta? | READY no livro vivo (canário do worker) **ou** READY_CURRENT nesta linha (régua dos 4 passos). Só READY_LEGACY não passa. Não se decide qual manda (é da M5) | **45** | 45 |
| **B** | a rota é executável? | contrato na tabela do coletor + receita web para o universo + sem bloqueio vivo/M3 | **14** | 14 |
| **C** | a receita reconhece uma notícia **real**? | uma matéria **lida** da fonte casa o `LINK_PATTERN` que o coletor usa. Sem matéria lida = NÃO SEI, não passa | **8** | 16 |
| **D** | é relevante (D2)? | `SINTONIA_RELEVANT = YES` (decisão do dono > leitura minha > 3b). Idioma não exclui (D3). **D8:** nas 3 de propaganda, só passa notícia com facto de mercado | **5** | 13 |
| **E** | não é propaganda de marca? | **Depois da D8 não corta**: as 3 ficam e são julgadas página a página em C/D | **5** | 134 |

```
PASSAM_TUDO = 5
  IT-T10-018  myfruit                         T10 · mercado hortofrutícola
  IT-T10-021  Plantgest                       T10 → REROUTE T7 · técnica (antigeada)
  IT-T7-017   Riunite (D8)                    T7  → REROUTE T10 · balanço, preço pago à uva
  IT-T7-041   Consorzio di Bonifica Romagna   T7  · água e rega
  IT-T7-043   Agrofarma (Federchimica)        T7  → REROUTE T10/T9 · indústria de agrofármacos
```

**Onde cada fonte pára** (primeiro degrau que falha): A 89 · B 31 · C 6 · D 3 · E 0 · passa 5.

### Porque param

* **A (89)** — `CONTRACTED_CANARY_FAILED` 78 (**69** com `EMPTY_LIST`: a receita não
  reconhece nada da entrada), `CAPABILITY_BLOCK` 6, `CONTRACT_READY_ROUTE_BLOCKED` 2,
  `RETRY_AFTER` 2, `AUTH_BLOCK` 1.
* **B (31 das 45 prontas)** — `NEEDS_CONTRACT` 24 (fora da tabela do coletor; **7**
  com rota já provada pela M3, por aplicar), `CAPABILITY_BLOCK` 4, `MISSING_ROUTE` 3
  (sem receita web para T12/T8/T9).
* **C (6)** — IT-T10-022 (receita não casa `/featured/…`; a V1 corrige); IT-T10-020
  (não casa; relevância NÃO SEI); IT-T7-021 (a página lida é um projecto único,
  família < 2); IT-T5-039 (não casa; e a notícia era aviso de matrícula);
  IT-T7-031 FederBio e IT-T7-040 Parmigiano (visitadas: a página-alvo era capa).
* **D (3)** — IT-T2-030 (a rota da Nomisma trouxe imobiliário e BCE: NO);
  IT-T7-042 (D8: emenda de lei sobre a denominação, sem facto de mercado);
  **IT-T7-033** Chianti — ⚠️ **conflito D1/D8 para o dono**: a notícia lida (campanha
  do azeite DOP 2025) foi mandada pelo dono para **produção (T1)** na D1, e a D8 só
  aceita, nestas 3, notícia de **mercado**. Fica NÃO SEI até o dono dizer.
* **E (0)** — depois da **D8** (23/09) a propaganda deixa de ser cortada aqui.

### As prontas sem notícia lida — o motivo real, não «falta rede»

```
PRECISA_REDE_IT = 0 das 45 prontas, depois de a VPN voltar. As 19 sem notícia lida:
  9  ROBOTS_NEGA — política do site; não se contorna
  4  visitadas: a página-alvo era capa, não matéria
  3  domínio já visitado por outra fonte: teto de 3 pedidos por site gasto
  2  sem contrato no livro vivo
  1  visitada, sem link com forma de matéria na entrada
```

### A relevância, com base declarada (`ROTULOS-RELEVANCIA-G0.json`)

26 fontes julgadas pelas duas perguntas separadas (D2). **BASE = DONO** em 4
(IT-T10-018, IT-T10-022, IT-T7-017, IT-T7-033); nas outras 22 é **leitura
minha**, quase sempre sobre **uma** notícia — humano-proposto, precisa de visto.

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
(`funil.desbloqueios`). Nenhum mexe em A nem em D:

| # | desbloqueio | dono | ganha (SOURCE_ID) | acumulado | **sites distintos** |
|---|---|---|---|---|---|
| 1 | contrato novo na tabela do coletor, com canário, + receita V2 | Curator + coordenador | IT-T10-026 Granaria · IT-T7-100 Agrofarma | 7 | **6** (IT-T7-100 é o mesmo site da IT-T7-043) |
| 2 | aplicar o onboarding das rotas provadas pela M3 | coordenador, depois da M5 | IT-T2-051 · IT-T2-056 Arpae | 9 | **7** (IT-T2-056 é duplicada da IT-T2-051) |
| 3 | aplicar a PROPOSTA-RECEITAS-V1 (6-PREP-d) | Curator/rotas, depois da M5 | IT-T10-022 Zootecnica | 10 | **8** |
| 4 | o dono resolve o conflito D1/D8 da IT-T7-033 (se a campanha do azeite contar como mercado) | **dono** | IT-T7-033 | 11 | **9** |
| 5 | canário novo nas 69 `EMPTY_LIST` depois da V1 (12 têm proposta) + régua T2/T12 (M3c) + receita web T12 | vários | **NÃO SEI** — não se conta sem medir | — | — |

```
DESBLOQUEIOS 1–3 → 10 SOURCE_ID = 8 sites · com o conflito D1/D8 resolvido a favor → 11 = 9 sites.
Chega a 10 SOURCE_ID, mas não a 10 sites.
```

⚠️ **Variedade.** Dos 9 sites: 2 de vinho/marca (Riunite pela D8; Chianti só se o dono resolver D1/D8), 3 de mercado (myfruit, Zootecnica, Granaria), 2 de água/rega (Arpae,
Bonifica Romagna), 1 técnico (Plantgest), 1 de indústria de agrofármacos
(Agrofarma). Nenhum de pragas/doenças (T3), nenhum científico (T5), nenhum
regulatório (T4).

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
EGRESS = IT em 22/22 idas com pedido (149.22.91.172 e, depois da volta, 149.22.91.171 — Palermo)
         0 pedidos pelo Brasil.
         A VPN caiu a meio: a 8.ª ida mediu BR (177.95.91.48 Londrina) e a recolha PAROU
         antes de qualquer pedido a esse site. Sem rede, marquei PRECISA_REDE_IT.
         Quando a coordenação avisou que voltou, a ida parada foi retirada do registo
         (0 pedidos feitos) e a recolha retomou os 15 sites em falta: 15/15 IT.
páginas  24 páginas de 22 sites em ~/coorte-paginas/ (fora do Git e da Sala), sha256 no MANIFESTO
```

---

## 5 — PROVAS

`tests/test_funil_coorte.py` — **14 provas**, dados sintéticos com resposta
conhecida à partida, sem rede nem git.

**Lei de mutação Python** (mandato): cache `__pycache__` apagada antes e depois,
`PYTHONDONTWRITEBYTECODE=1`, processo novo, mutação conferida por `git diff`, e
**prova de execução** (o código mutado escreve um ficheiro-marca):

| mutante | entrou | executou | resultado |
|---|---|---|---|
| A aceita READY_LEGACY | sim | sim | morto |
| C passa sem matéria lida | sim | sim | morto |
| a D8 ignorada (propaganda passa sem facto de mercado) | sim | sim | morto |

(O mutante «lista de marca esquecida», morto antes da D8, deixou de fazer sentido: a regra mudou.)
| um desbloqueio baixa A | sim | sim | morto |

⚠️ Na primeira tentativa o 4.º mutante tinha um erro meu de indentação e **não
executou**. Não o contei como sobrevivente: refi-lo e confirmei a execução.

---

## 6 — LIMITES

* A relevância de 22 fontes é leitura minha sobre **uma** notícia.
* O degrau C usa a receita da tabela do coletor desta linha (é a que corre); o
  livro vivo tem outra.
* «Qual canário manda» (worker vivo ou régua dos 4 passos) não foi decidido: as
  duas ficam escritas por fonte (`A_PORQUE`).
* Duplicados de fonte (IT-T2-051/056; IT-T7-043/100) são decisão de identidade
  no Atlas; contei-os à parte.

---

## ENTREGA

```
UNIVERSO        = 134 (dedup)
FUNIL           = A 45 · B 14 · C 8 · D 5 · E 5   (com a D8)
PASSAM_TUDO     = 5 — IT-T10-018, IT-T10-021, IT-T7-017, IT-T7-041, IT-T7-043
MAIOR_CORTE     = A (89: 69 EMPTY_LIST = receita); dentro das prontas, B (24 sem contrato no coletor)
DESBLOQUEIOS    = 1) contrato novo com canário + receita V2 → 7 · 2) rotas da M3 → 9 ·
                  3) receitas V1 → 10 SOURCE_ID = 8 sites · 4) dono resolve D1/D8 do Chianti → 11 = 9 sites ·
                  5) o resto: NÃO SEI sem canário novo
D8              = aplicada: E deixa de cortar a propaganda; só passa notícia com facto de mercado
                  (Riunite passa; Chianti em conflito D1/D8; Balsamico não)
RECEITAS_NOVAS  = 1 com prova (IT-T10-026)
EGRESS          = IT 22/22 idas com pedido · 0 BR · 1 ida parada por BR antes do pedido
PRECISA_REDE_IT = 0 (depois da volta da VPN)
```

---

## EM PALAVRAS SIMPLES

Queríamos 10 a 20 fontes prontas para o teste pequeno. Fui ver **134 fontes**
e passei cada uma por 5 peneiras, uma atrás da outra:

1. está pronta? → **45**
2. o coletor sabe lá ir? → **14**
3. a receita reconhece uma notícia de verdade? → **8**
4. o assunto serve ao Sintonia? → **6**
5. não é propaganda de marca? → **5** (pela sua decisão D8, a propaganda já não é
   cortada aqui: cada notícia é julgada sozinha, e só passa se tiver facto de mercado)

Sobram **5 fontes**: preços de fruta, técnica de pomares, rega na Romagna, a
associação dos fabricantes de agroquímicos, e as contas da cooperativa Riunite.

**A peneira que mais corta é a primeira.** 89 fontes nem estão prontas, e a
maioria por culpa da receita. A relevância quase nunca é o problema: quando uma
fonte chega a ser lida, costuma servir.

**Como chegar perto de 10**, sem baixar nenhuma exigência:

- dar contrato a duas fontes que já sabemos que servem;
- aplicar as rotas já provadas;
- aplicar as receitas corrigidas;
- você dizer se a notícia do azeite do Chianti conta como "mercado" (na D1 mandou-a
  para produção, e a D8 só deixa passar mercado nestas fontes).

Isso dá **11 códigos, mas 9 sites diferentes**: duas fontes são o mesmo site
com dois nomes. E faltam temas: nenhuma fonte de pragas, de ciência ou de leis.

A VPN caiu a meio. O programa viu, parou antes de pedir fosse o que fosse pelo
Brasil, e retomou quando ela voltou. Agora já não falta ler nada por causa da
rede. O que falta é por outros motivos: sites que não autorizam, ou páginas que
eram só capa.
