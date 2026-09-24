# TRAVA-MEDIDORES-V1 — os dois medidores cegos da trava, consertados no dono

> A trava (`docs/operacao/TRAVA-DA-INTELIGENCIA.json`) **não foi editada**. Nenhuma Sala lida,
> nenhum banco, nenhuma rede, nenhuma execução da Intelligence.

| campo | valor |
|---|---|
| pedido | coordenação, 24/09 — consertar os 2 medidores cegos, testes antes/depois, mutação, re-medir A..N |
| branch | `trava-medidores-v1`, a partir de `origin/egresso-consenso-v1` @ `a310487f` (produção) |
| donos tocados | `system-map/scripts/censo_das_estradas_it.py` · `system-map/scripts/censo_do_congelamento.py` · a declaração de entradas deles em `system-map/scripts/CADEIA-DO-MAPA.json` |
| testes novos | `tests/test_os_medidores_da_trava_veem.py` (9) |
| provas | `data/derivados/TRAVA-MEDIDORES-V1/` |

## 1 · O que estava cego, e o que mudou

### 1.1 · O vigia do congelamento comparava a árvore consigo mesma

`censo_do_congelamento.py` gravava `FROZEN_AT_HEAD = HEAD desta corrida` e os blobs de agora.
Resultado: **0 diferenças sempre**, qualquer que fosse a mudança.

Agora ele lê a fotografia da trava (`FREEZE_MANIFEST`, `FROZEN_AT_HEAD = 82ef1deb`, 73
artefactos) **só para ler**, e publica `CONTRA_A_FOTOGRAFIA`: `MUDARAM`, `SUMIRAM`, `NOVOS` e
`CONGELAMENTO_RESPEITADO`. `FROZEN_AT_HEAD` passa a ser o da trava; o HEAD da corrida vai para
`MEDIDO_NO_HEAD`.

### 1.2 · O medidor das estradas só conhecia o catálogo antigo

`censo_das_estradas_it.py` lia **um** catálogo, `candidatas/ITALY-SOURCE-MASTER-V1.json` (54
fontes). O coletor da produção lê `regras/italy_contracts_onboarded.json` (193). **As duas
listas têm 2 fontes em comum.** A IT-T10-018 (3 SIM na Sala real na 1.ª onda) não aparecia.

Agora ele publica também `UNIVERSO_DO_COLETOR` (as 193, com lote, estratégia, se há evidência
no Git e o último estado no livro do curador) e `UNIVERSO_DO_VEREDITO`, que **declara** que o
veredito e o critério A continuam medidos sobre o catálogo, com `DECISAO = PENDENTE_DO_DONO`.

**O que ele não faz, de propósito:**
- **não muda a regra da trava** nem o universo do veredito — isso é decisão do dono;
- **não inventa classe de estrada**: o modelo (`estradas-it.model.json`) não diz a que classe
  pertence cada estratégia (`HTML_LINK_DISCOVERY`, `STATIC_ENDPOINT`, `CUSTOM_ADAPTER`). As 193
  ficam com `ROUTE_CLASS_ID = NAO_SEI` e `CRITERIO_A_NESTE_UNIVERSO = SEM_REGRA_DE_CORRESPONDENCIA`;
- **não usa o veredito do portão no instante**: esse depende do relógio (canário ≤ 7 dias) e
  dos livros vivos do bot, fora do Git — o mapa deixaria de ser reprodutível. Usa o último
  `NEW_STATE` do livro do curador **como está no Git**, e diz isso no campo.

## 2 · Testes que falham ANTES e passam DEPOIS

| ficheiro | antes do conserto | depois |
|---|---|---|
| `tests/test_os_medidores_da_trava_veem.py` | **FAILED** — 1 falha, 3 erros (`testes-ANTES.txt`) | **OK — 9 de 9** (`testes-DEPOIS.txt`) |

A falha de antes é o defeito em pessoa:

```text
AssertionError: 'a310487f95479ace484e8bd5a09ef9940d911b7a' != '82ef1deb1f85975b3ce7ccffdc439f8ee2b3e4f7'
                 (o HEAD da corrida)                           (a fotografia da trava)
```

## 3 · Mutação a morder

`data/derivados/TRAVA-MEDIDORES-V1/mutacao.py.txt` estraga o conserto de 6 maneiras, uma de
cada vez, corre só a classe de teste que devia apanhar, e repõe os bytes conferindo o sha256.

```text
M1 o vigia compara o blob consigo          MORTO · reposto=SIM
M2 FROZEN_AT_HEAD volta a ser o HEAD       MORTO · reposto=SIM
M3 o vigia ignora os novos                 MORTO · reposto=SIM
M4 o censo volta a ler so o catalogo       MORTO · reposto=SIM
M5 o censo inventa classe de estrada       MORTO · reposto=SIM
M6 a sobreposicao conta tudo               MORTO · reposto=SIM
MUTANTES 6 · MORTOS 6
```

## 4 · Os testes vizinhos: nada novo partido

| conjunto | antes (base `a310487f`) | depois |
|---|---|---|
| `test_estradas_it` + `test_trava_da_inteligencia` (35) | 2 falhas | **as mesmas 2** |
| `test_atomicidade_da_intelligence` + `test_o_controle_separa_lei_de_mencao` (99) | 102 falhas | **as mesmas 102** (`comm` vazio nos dois sentidos) |

As 2 falhas da trava são `test_nenhum_artefato_congelado_mudou` e
`test_nao_apareceu_inteligencia_nova` — **as violações reais** da secção 5, que já existiam na
produção. As 102 são dívida antiga da linha (a casa já sabe que o tronco chega vermelho); a
base foi medida com as minhas alterações guardadas numa cópia nomeada (`git stash`), e a
lista de falhas é igual linha a linha.

## 5 · A TRAVA, RE-MEDIDA COM OS MEDIDORES CONSERTADOS

```text
COLLECTION_FOUNDATION_CLOSED = NAO
A..N = 4 SIM · 8 NAO · 2 SEM MEDIDOR
CONDIÇÃO DE DESTRAVE = 0 de 5
```

| | critério | **hoje** | prova (produção `a310487f` + medidores consertados) |
|---|---|---|---|
| **A** | toda fonte IT tem route class conhecida ou BLOCKED explícito | **NAO** | no universo do veredito (catálogo, 54): 7 com rota provada, 24 só candidata, 23 desconhecida. No livro do coletor (193): **0 com classe conhecida** — não há regra de correspondência. Nos dois universos, NAO |
| **B** | nenhuma fonte depende de writer improvisado | **SEM MEDIDOR** | nenhum ficheiro gerado mede isto |
| **C** | RAW tem um dono | **NAO** | `donos`: `RAW_ASSET = DONO_DUPLICADO` (4 escrevem) |
| **D** | a corrida tem um contrato | **SIM** | `RUN_MANIFEST = UM_DONO` (`leis/data_clock.py`) |
| **E** | o checkpoint tem um dono | **NAO** | `CHECKPOINT = DONO_DUPLICADO` (2 escrevem) |
| **F** | o derivado tem um dono | **SIM** | `DERIVED_ARTIFACT = UM_DONO` (`guarda/preservar_derivado.py`) |
| **G** | persistência estruturada com dono por espécie | **NAO** | etapa `STRUCTURED` em `UNKNOWN` em RC-3/4/10/11/12 |
| **H** | a escolha de rota não vive espalhada | **NAO** | `ROUTE_MODEL` 6 escritores; `ORQUESTRADOR` 13 |
| **I** | Apify não é rota por omissão | **SIM** | `APIFY.DEFAULT = 0`, `FALLBACK = 5` |
| **J** | o Git não é estado operacional | **NAO** | 2 ledgers `ndjson` (521 + 59 linhas) |
| **K** | retry e queda não fabricam sucesso | **SEM MEDIDOR** | nenhum dono mede retry |
| **L** | UNKNOWN continua UNKNOWN | **SIM** | `REQUIRED_TOTAL = UNKNOWN` mantido; e agora também `ROUTE_CLASS_ID = NAO_SEI` nas 193 em vez de palpite |
| **M** | o System Map representa tudo | **NAO** | 202 de 241 componentes pendentes |
| **N** | a inteligência continua congelada | **NAO** | **agora pelo dono**: `congelamento.CONTRA_A_FOTOGRAFIA.CONGELAMENTO_RESPEITADO = false` — 16 mudaram, 0 sumiram, 5 novos |

Os 5 novos: `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json`,
`research/intelligence/DATA-DEMAND-MATRIX-ITALY.json`, `system-map/data/architecture.declared.json`,
`italia-portale/audit/superficie-visivel.mjs`, `italia-portale/client/italy-label-intelligence.js`.
A lista dos 16 está no próprio `congelamento.generated.json` (`MUDARAM`, com blob congelado e
blob de agora).

**O que mudou desde a medição anterior (`intelligence-bc1-v1` @ `c51ec96f`):** os números são
os mesmos; a diferença é **quem** os diz. A e N passaram a ser ditos pelos donos, e não por uma
comparação feita à mão ao lado.

## 6 · PARA O BOT LUCIANO / DONO — decisões que não tomei

1. **Que lista de fontes vale para o critério A?** O catálogo antigo (54), o livro do coletor
   (193) ou o livro do curador (716 IT)? Hoje o veredito continua no catálogo, declarado como
   `PENDENTE_DO_DONO`.
2. **A que classe de estrada pertence cada estratégia do coletor?** `HTML_LINK_DISCOVERY` (140
   fontes), `CUSTOM_ADAPTER` YouTube (50), `STATIC_ENDPOINT` (3). Sem isto, A fica sem regra
   no livro do coletor.
3. **Dono único de RAW** (4 escritores), **do checkpoint** (2) e **da escolha de rota** (6 +
   13) — ou decisão escrita de qual é o canónico e qual é legado.
4. **Os 21 do congelamento (16 + 5):** cada um é conserto permitido pela trava ou avanço
   proibido? Decidir por escrito; o vigia agora continua a tocar até lá.

Nota, não decisão: B e K não têm medidor. Construí-los é trabalho, não escolha.

## 7 · O que NÃO foi feito

- a trava não foi editada; nem a constante de `leis/fundacao_da_coleta.py`;
- não li o diff de cada um dos 16;
- não corri a suite inteira (RAM); só os 4 ficheiros vizinhos, antes e depois.
