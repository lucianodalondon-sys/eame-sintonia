# CRUZAMENTOS-MAX — o máximo de cruzamentos que a prova do repo aguenta · EXPERIMENTAL / NAO_PARA_CLIENTE

```text
ORDEM     D114 do dono: portal com o MÁXIMO de cruzamentos possíveis — cada um com prova; nada inventado
RAMO      claude/cruzamentos-max-sguy1x   (base a09d383 = insumos da R7 sobre o vivo 18461b92)
INSUMOS   docs/intelligence/r7/ANALISE-R7.json (86 cruzamentos, IR-e09acab6365032523d6e)
          data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json   2030 pares, 102/163 rótulos com par lido
          data/collection-store/italy/IT-T4-001/.../PROD_FTS_6_20260907.csv   cadastro do Ministero, 17 695 linhas
REDE      nenhuma. Livros vivos: só lidos. Nada escrito na Sala, nada publicado, nada ao cliente.
```

## 0 · O achado que muda a leitura dos 48

A premissa da missão era que os 48 `PARTIAL_GRAO_INCOMPATIVEL` fossem culturas genéricas no boletim
(«fruttiferi», «drupacee»…). **Medido nos 48: não são.** Em todos, o boletim lista culturas no nível do
**DOCUMENTO** (até 50 culturas: «vite, ciliegio, albicocco, melo, actinidia…») e a substância **não está
ligada a nenhuma delas no texto**. O ANALISE-R7 guarda só os primeiros 300 caracteres de cada troço, e o
texto integral dos boletins **não está no repo** (o ARIF N37 nem tem o PDF guardado: só o N36). Um
nível de grão melhor não conserta isso: conserta o vocabulário, não a ligação.

> **GRÃO ≠ LIGAÇÃO.** A tabela de grão diz se o rótulo cobre a cultura; não diz de que cultura o boletim fala.

## 1 · Contagens antes / depois (os 86)

| estado | R7 (antes) | CRUZAMENTOS-MAX (depois) |
|---|---|---|
| `CONFIRMED_YES` | — | **3** |
| `POSSIBLE_ANSWER_YES_A_CONFIRMAR` | 5 | 0 |
| `PARTIAL_GRAO_INCOMPATIVEL` | 48 | **48** |
| `POSSIBLE_ANSWER_NO` | 29 | **7** |
| `UNRESOLVED` (NÃO SEI, com motivo) | — | **24** |
| `NOT_POSSIBLE` (sem cultura) | 4 | 4 |

| grupo | o que aconteceu |
|---|---|
| **os 48 PARTIAL** | **48 → 48.** 0 viraram YES, 0 viraram NO. Em 10 o grão ganhou cultura coberta pelo rótulo (melone, cocomero, cetriolo, pero, cavolfiore, fagiolo, fagiolino, aglio, oliveto, vigneto); em 1 perdeu (CAND-1227 × pirimicarb: «lattuga» — o rótulo escreve «Lattughe e insalate», grupo sem membros declarados). Em 20 a substância está no troço guardado, mas nenhuma cultura a ≤ 400 caracteres. |
| **os 5 YES a confirmar** | **3 CONFIRMED_YES** (CAND-1209, CAND-1228, CAND-1229) · **2 UNRESOLVED** (CAND-1221: o cabeçalho «vite» não está no troço guardado e a data é NÃO SEI; CAND-1223: data do boletim NÃO SEI). |
| **os 29 NO** (extensão declarada: a mesma régua) | **7 continuam NO** · **22 → UNRESOLVED**: 21 eram «NO» sobre rótulos que **nunca tiveram tabela lida** (`TABELA_NAO_LOCALIZADA`/`TABELA_SEM_PAR`), 1 tem cultura fora do vocabulário do leitor («anguria»). Ausência de leitura não é NO. |

## 2 · A tabela de GRÃO (`motor/cruzamentos_max.py:264`, regra em `:331`)

Só vale o que o **próprio rótulo** escreve. 28 declarações de grupo lidas nas citações:
`Pomacee (melo, pero, melo cotogno e nespolo)` ×8 · `Cereali (orzo, avena, frumento, segale, triticale)` ×7 ·
`Cavoli (cavolfiore, cavolo cappuccio, cavoletto di Bruxelles)` ×6 · `Fruttiferi minori (…lampone…)` ×5 ·
`DRUPACEE (albicocco, pesco, ciliegio, susino, nettarina)` ×1 · `Fruttiferi a guscio (nocciolo, mandorlo, noce)` ×1.

| como a cultura do boletim casa com um par do rótulo | vale? |
|---|---|
| `MESMA_CULTURA` — chave do leitor que é UMA cultura (VITE = vite/vigneto/uva) | sim |
| `NOMEADA_NO_ROTULO` — chave de GRUPO do leitor (CUCURBITACEE, MELO=pomacee, CIPOLLA=aglio…) e a cultura escrita na **zona da cultura** do par | sim |
| `MEMBRO_DECLARADO_NO_ROTULO` — o **mesmo** rótulo declara o grupo, o par cita o grupo na zona da cultura, e o par é desse grupo | sim |
| a chave do grupo bate, sem nome nem declaração (`GRAO_NAO_PROVADO`) | **não** — continua PARTIAL/NÃO SEI |
| declaração de grupo de **outro** rótulo («Cereali (orzo, frumento)» do MAVRIK JET ≠ o do KLARTAN) | **não** |
| cultura escrita fora da zona da cultura (depois do alvo, noutro bloco) | **não** |
| subtipo pelo genérico («cavolo» por «cavolo cappuccio», «melo» por «melo cotogno») | **não** |
| cultura de rotação («possono essere seminate fava, cece») | **não** — ver pedido P2 |

`GRUPOS_DO_LEITOR` (`:100`) é medido nas regex de `coleta/rotulos_ler.py:64`; vocabulários de cultura e
praga são **importados** de `coleta/rotulos_ler.py` e `leis/boletim_do_campo.py`, não copiados.

## 3 · Os 5 «sim a confirmar» contra o cadastro (`:575`)

Cheques por produto ADAMA: registo no cadastro em nome da ADAMA · substância na composição registada ·
**válido na data do boletim** (registado antes, scadenza depois, sem revoga antes — no cadastro de 07/09/2026) ·
cultura no rótulo lido · cabeçalho de uma cultura (X3h) visível no troço guardado. Dose/intervalo: transcritos
se o rótulo os escreve na linha (`DOSE_E_VOLUME_LITERAIS`: «l/ha» pode ser volume de calda — vai como está).

| boletim | substância × cultura | data | estado | produtos que confirmam (registo · scadenza) |
|---|---|---|---|---|
| CAND-1209 Cantina Negrar | azoxistrobina × vite | 30/06/2026 | **CONFIRMED_YES** | CUSTODIA ULTRA 015232 · 15/08/2026 ⚠️ · MIRADOR TURBO 017824 · 31/05/2027 |
| CAND-1228 Cantina Negrar | folpet × vite | 12/05/2026 | **CONFIRMED_YES** | FOLPAN GOLD 012878 · 2040 · SESTO GOLD 015317 · 2040 |
| CAND-1229 Parma | tau-fluvalinate × vite | 27/05/2026 | **CONFIRMED_YES** | EVURE PRO, KLARTAN 20 EW, KLARTAN SMART, MAVRIK EW, MAVRIK SMART, TAU AL 240 EW · 31/01/2027 (dose literal 30–300 ml/hl, máx. 0,3 l/ha) |
| CAND-1221 Arezzo | folpet × vite | NÃO SEI | **UNRESOLVED** | cabeçalho fora do troço guardado + data NÃO SEI |
| CAND-1223 Reggio E. | captano × melo | NÃO SEI | **UNRESOLVED** | 3 produtos com melo no rótulo (CAPTHENE, MAKE UP, MERPAN), mas a data do boletim não se prova |

- ⚠️ CUSTODIA ULTRA: scadenza 15/08/2026, **estado «Autorizzato» no cadastro de 07/09** — válido no dia do
  boletim; o cadastro não diz porque segue ativo depois da scadenza (escrito na `NOTA` do objeto).
- Dos 13 produtos de folpet, 11 têm o rótulo **sem tabela lida**: NÃO SEI para eles, não «não».
- O `CONFIRMED_YES` **herda a regra X3h da R7, que ainda não tem regressão**. Prova: o rótulo cobre a
  substância na cultura, com registo válido na data. **Não** prova uso, recomendação de produto ADAMA,
  lugar, momento nem eficácia.

## 4 · PORTFOLIO_MATCH e COMPETITIVE_SET (`:716`, `:773`)

**PORTFOLIO_MATCH** = o rótulo ADAMA lido tem aquela cultura × alvo **na mesma linha/bloco** + registo válido.
`DECLARACAO_DE_PRODUTO` fica à parte (`PORTFOLIO_MATCH_SO_ESPECTRO_DE_PRODUTO`) e não se soma. Separado de
«o boletim recomendou»: nenhum objeto diz isso.

| pares cultura × praga no repo | estado |
|---|---|
| 13 × olivo × mosca dell'olivo (corte vertical da R7, PAR = SECAO) | `SEM_PAR_LIDO` — nenhum par OLIVO × MOSCA_OLIVO nos rótulos lidos; **ausência NA NOSSA LEITURA**, nunca «a ADAMA não tem» |
| 1 × vite × «flavescenza dorata della vite» (CAND-1229, cabeçalho) | `NAO_SEI` — «flavescenza» não é alvo no vocabulário do leitor; o rótulo cita o vetor *Scaphoideus titanus* e ligar os dois seria inventar |

Os **1076 pares por secção** da R7 **não estão no repo** (só a contagem). O script do coordenador aceita o
livro (`--livro`, formato `PROBLEMA.SECOES` de `leis/boletim_do_campo.ler_boletim`) e corre a mesma régua
sobre eles.

**COMPETITIVE_SET** (grão = **SUBSTÂNCIA**; o cadastro FTS6 não tem cultura nem alvo, rótulos de concorrentes
não lidos → cultura × alvo do concorrente = `NAO SEI`):

| substância (data do boletim) | concorrentes válidos | só «Autorizzato*» | empresas |
|---|---|---|---|
| azoxistrobina (30/06/2026) | 65 | 56 | 22 |
| folpet (12/05/2026) | 60 | 39 | 14 |
| tau-fluvalinate (27/05/2026) | 0 | 0 | 0 (todos os de outras empresas estão revogados) |

## 5 · A saída para o portal — pote v2 (gerador `ce775ff5`, sem mudança nenhuma)

- `docs/intelligence/r7/CRUZAMENTOS-MAX.json` — a análise inteira (antes/depois por cruzamento, prova por cultura).
- `docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json` — `ITENS_POR_FERRAMENTA` no contrato de entrada do
  pote v2: **portfolio 103** e **competitors 125** objetos, todos `ESPECIE = CROSSING`, `EXPERIMENTAL_CANDIDATE`.
  O estado viaja como `CROSSING_STATE` (o portfolio não tem vaga → sai em `FORA_DO_CONTRATO`, com nome e valor).
- **O coordenador roda localmente** (`pacote/pote_cruzamentos_max.py`):

```bash
python3 pacote/pote_cruzamentos_max.py --entrada PARA-O-CASCO-R7/ENTRADA-DO-POTE-R7.json \
        --saida italia-portale/client/sintonia-pote.js [--livro saida/LIVRO-R7.json] [--so-cruzamentos]
```

  Monta **uma corrida nova** (`IR-XMAX-…`, `CORRIDA_BASE` = R7), LINEAGE da R7 verbatim, liga a prova à
  LINEAGE só por identidade exata e única, e entrega ao `pacote/pote_intelligence_casco.py`, que confere.
  ⚠️ **Esperado no pote real:** os objetos das 38 novas são **recusados à vista** até a Coleta pôr o
  `DOCUMENT_ID` (defeito C1 da R7), e só atravessa prova de item com G0 = PASSOU. Isso não é bug deste script.

## 6 · Testes, mutação, bateria, mapa

- `tests/test_cruzamentos_max.py`: **54 testes, OK** (sintéticos `SINT-`; `X_Real` prova que o JSON commitado
  é o que o código produz agora).
- Mutação `provas/_mutantes_cruzamentos_max.py`: **30/30 mortos** (grão de outro rótulo, chave de grupo como
  prova, rotação como uso, subtipo, zona inteira, PARTIAL→YES sem ligação, rótulo não lido como NO,
  validade sem scadenza/revoga/registo, declaração de produto como par forte, ADAMA no CS, METALAXYL =
  METALAXYL-M, DOCUMENT_ID fabricado, LINEAGE ambígua ligada, id da R7 reusado…). Na 1.ª passagem ficou
  **1 vivo** (G6: grupo declarado num par de outra cultura) → teste A10 novo; e o S2 morria por erro de
  sintaxe do próprio mutante → reescrito, agora morre pelo teste F2.
- Bateria por nome e mapa: ver §8.

## 7 · Pedidos (sem escolher coletor, URL ou rota)

| # | para | pedido |
|---|---|---|
| P1 | Coleta | texto integral (ou troço de ±400 car. à volta da substância) dos boletins dos 48: sem isso, os 48 continuam PARTIAL por construção |
| P2 | dono do leitor de rótulos | POSTSCRIPT 80 (XL): par LEGUMINOSE cuja «cultura» é a frase de rotação «possono essere seminate fava, cece» — o leitor tomou sucessão por uso |
| P3 | Coleta / leitura de rótulos | 61/163 rótulos sem par lido (11 dos 13 de folpet): são eles que fazem 21 dos 22 «NO → UNRESOLVED» |
| P4 | Coleta | data dos boletins CAND-1221 e CAND-1223 (confirmam no dia em que a data vier) |
| P5 | Intelligence | regressão de X3h/X3w antes de o CONFIRMED_YES subir para o motor |

Nenhum ficheiro de UI/casco foi tocado: a lei do ADAMA Design System não se aplica a esta entrega.

## 8 · Bateria inteira por nome e System Map

(preenchido depois da medição do ramo — ver abaixo)

## EM PALAVRAS SIMPLES

Perguntámos: «o rótulo da ADAMA deixa usar este produto na cultura de que o boletim fala?». Dos 5 «talvez
sim», 3 viraram **sim com papel passado** (registo válido no dia, cultura no rótulo). Os 48 «meio-termo»
continuam meio-termo: o boletim fala de muitas culturas de uma vez e o pedaço de texto que temos não diz de
qual fala o produto — ensinar ao sistema que «pero» faz parte de «Pomacee» não resolve isso. E 22 «não»
eram, na verdade, «nunca lemos esse rótulo»: agora dizem **não sei**. Para a concorrência só dá para dizer
quem tem a **mesma substância** registada — o cadastro não diz em que cultura.
