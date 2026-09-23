# RELATÓRIO — MISSÃO 6-PREP · A MICRO-COLETA PRONTA, SEM COLETAR

Branch `micro-prep-v1`, nascida de `44c873ff`. Motor: `claude-opus-5-5`.

```
NETWORK_REQUESTS = 0     (nenhum pedido de coleta; nenhum pedido a medidor de egresso)
DB_WRITES        = 0     (só SELECT, e com default_transaction_read_only=on na ligação)
ADMISSION / RÉGUA / DERIVADOR / CONTRATOS / FILA / LEDGER = intocados
```

Tudo o que se entrega está em `scripts/micro_coleta/` e
`tests/test_micro_coleta_instrumento.py`.

---

## 0 — AS DUAS MICRO-COLETAS ANTERIORES E O QUE ESTA PREPARAÇÃO TRAVA

| erro de 21/09 | onde | trava nesta preparação |
|---|---|---|
| RUN1/RUN2 com egresso **BR** | micro-collection-v1 | `correr` mede o egresso **antes e depois de cada fonte**; se não for IT, não lança essa fonte (prova `test_egresso_brasil_nao_lanca_nenhuma`) |
| 1 «CAPA» colhida em IT-T7-033 | micro-collection-v1 | **era falso alarme** — ver secção C2 abaixo; o critério passa a exigir visto humano em cada capa apontada |
| 3 robots «não lidos» | micro-collection-v1 | não é do instrumento: é do coletor (`italy_pilot_collect.mjs`), que já trata «não li» ≠ «proibido»; fica como risco R6 |
| 0 na Sala: **sem receita** para T5/T7/T10 | canonical-micro-v1 | **medido hoje: a receita existe** para T2, T5, T7 e T10 (`pedido/receitas.py::EXECUTORES`, todas com `roda = coleta/italy_executor.py`); o `plano` resolve a frase de cada fonte **em memória** e confere alvo e executor |
| a frase do pedido não resolvia o território | canonical-micro / duas-portas | o comando leva um apelido do dono (`preco`, `agronomo`, `ciencia`, `clima`) e o plano prova que resolve |
| `PONTE_EM_RUNTIME = NÃO EXISTE` | canonical-micro-v1 | o gate é perguntado **no instante** de cada corrida e o veredito fica no relatório (`GATE_NO_INSTANTE`) |
| FONTE 55/71 de marca | o meu diagnóstico | IT-T7-017, IT-T7-033, IT-T7-042 **excluídas** da coorte |

Confirmação pedida (facto 4): a receita existe para a coorte — **T10 e T7 sim**
(as 5 prontas); **T5 sim** (mas as duas fontes T5 estão bloqueadas por outro
motivo); **T2 sim**; **T12 não**; **T9 existe mas vai para o coletor social**,
não para o web.

---

## A — CRITÉRIOS DE PASSAGEM (7), CADA UM COM O SEU COMANDO

Todos saem de **um** comando, que só lê:

```
py scripts/micro_coleta/micro_coleta.py relatorio --run-id=<R1> --run-id=<R2> ... --saida=<pasta>
→ <pasta>/RELATORIO-PASSAGEM.json · RELATORIO-PASSAGEM.md · CLASSES.tsv · CAPAS-A-CONFIRMAR.tsv
```

`correr` chama-o sozinho no fim. Cada critério tem também a sua prova à mão:

| # | critério | passa quando | comando independente |
|---|---|---|---|
| **PRÉ** | **egresso IT — PRÉ-REQUISITO DO DONO** | o dono liga a VPN italiana antes; já foi obtido em 21/09 (canonical-micro F3: `146.70.182.38` Milan AS9009 M247, 3 medidores). Sem VPN ligada, `correr` não lança nada | `curl -s https://ipinfo.io/json` → `"country": "IT"` |
| C1 | egresso IT **por corrida** | todas as fontes lançadas com `PAIS=IT` antes **e** depois | lido de `RELATORIO-PASSAGEM.json` → `C1.MEDIDO`; sem medição = FAIL |
| C2 | matéria individual, não capa, com controlo negativo | juiz canónico `CAPA_NAO_E_MATERIA/v1` sobre os **bytes brutos**; controlo negativo (listagem sintética de 120 ligações tem de dar CAPA, notícia sintética tem de dar MATÉRIA); 0 bytes em falta; cada capa apontada confirmada por pessoa | `CAPAS-A-CONFIRMAR.tsv` preenchido com 0 «SIM» |
| C3 | a decisão do bot atravessa a ponte **em runtime** | cada fonte lançada tinha `ELIGIBLE` no gate **no instante**, e só fontes lançadas aparecem nos `raw_asset` | `py curadoria/collection_gate.py --ids=<ID> --json` no momento; `select distinct source_id from raw_asset where run_id in (...)` |
| C4 | chegada à Sala com proveniência completa | toda linha da Sala junta `raw → storage → derived → collection_run` e `item_id = derived:<id>`; toda observação tem storage, derivado e decisão | `select count(*) from sala_de_espera s where run_id in (...) and not exists (select 1 from raw_asset r join storage_object so on so.id=r.storage_object_id join derived_artifact d on d.raw_asset_id=r.id join collection_run c on c.run_id=r.run_id where r.id::text=s.raw_observation_id::text and 'derived:'\|\|d.id=s.item_id)` → 0 |
| C5 | FACT_TIME / FACT_LOCATION: UNKNOWN honesto e contado | conta-se `NAO SEI` nos dois; **reprova** se algum `fact_time` for igual a `captured_at` (preenchido para parecer completo) | `select count(*) filter (where fact_time='NAO SEI'), count(*) filter (where fact_time=captured_at::text) from sala_de_espera where run_id in (...)` |
| C6 | zero bypass da Admission | nenhuma linha na Sala sem `SIM` no livro; nenhum `SIM` fora da Sala | cruzar `sala_de_espera.item_id` com `data/samples/LIVRO-DE-DECISOES.json` (`corrida` = RUN_ID) |
| C7 | SIM/NAO/NAO_SEI por fonte e por classe | tabela por fonte sem `SEM_DECISAO`/`SEM_DERIVADO`; `CLASSES.tsv` preenchida por pessoa com FONTE/ROTA/REGUA/TEMA/UNKNOWN para cada não-SIM | `CLASSES.tsv` sem coluna CLASSE vazia |

```
MICRO_CRITERIA = 7 (+ 1 pré-requisito do dono: VPN italiana ligada)
```

### Ensaio do relatório sobre dados reais, só lendo

Corri `relatorio` sobre a corrida real do lote-76
(`XX-T10-2026-09-22-193411-0a8a01dbc999da85`). Ele tem de repetir os números
que já se conhecem — e repete:

| critério | resultado | leitura |
|---|---|---|
| C1 | FAIL | correcto: corrida antiga, sem medição de egresso — **sem medição reprova** |
| C2 | PENDENTE_HUMANO | 76 julgados, 6 capas apontadas pelo juiz (ver abaixo) |
| C3 | FAIL | correcto: sem registo do gate no instante |
| C4 | PASS | 5 linhas na Sala, 5 com a cadeia inteira; 76/76 com storage, derivado e decisão |
| C5 | PASS | FACT_TIME e FACT_LOCATION `NAO SEI` em 5/5; 0 preenchidos à força |
| C6 | PASS | 0 na Sala sem SIM; 0 SIM fora da Sala |
| C7 | PASS | por fonte: T10-018 5 SIM/4 NAO_SEI · T10-022 10 NAO_SEI · T7-017 21 NAO/9 NAO_SEI · … (bate com o diagnóstico) |

### ⚠️ Dois achados que o ensaio trouxe

**1. O juiz de capa erra em notícias curtas.** Aponta 6 dos 76 como
`CAPA_PROVAVEL` (raw 1361, 1374, 1375, 1381, 1395, 1396). Li os 6: são **notícias
individuais com data**, curtas (522–786 caracteres em parágrafo) dentro de um
menu de 66–93 ligações. O raw **1381** é a página «E-learning: vuoi diventare un
esperto di Chianti Classico?» (7/11/2024) — **o mesmo documento** que a
micro-collection-v1 registou como «a única CAPA colhida» (os números batem: 88
ligações, 1.920 caracteres, 646 em parágrafos). **Essa capa de 21/09 era um
falso alarme.** Não mexi no juiz (trava). O critério C2 não reprova sozinho:
manda a pessoa ler.

**2. Os bytes do lote-76 não estão no armazém operacional.** Dos 76
`raw_asset.storage_path`, **2** existem em `sintonia-sala-italia/armazem/` e
**76** existem, com sha256 certo, na pasta de trabalho
`orca/workspaces/eame-sintonia/lote-76-v1/XX/`. A prova de origem de 74
documentos vive numa pasta de trabalho que pode ser apagada. Ver risco R1.

---

## B — COORTE CANDIDATA

Ficheiro: `scripts/micro_coleta/COORTE-PROPOSTA.json`. Medido pelo gate
canónico sobre o livro desta linha:

```
READY 102 · READY_CURRENT 21 · (4 com HUMAN_REVIEW → recusadas pelo gate) · ELIGIBLE 17
ELIGIBLE 17 − EXCLUÍDAS 3 = PROPOSTAS 14
```

| SOURCE_ID | universo | contrato | receita web | rota M3 | hoje |
|---|---|---|---|---|---|
| IT-T10-018 myfruit | T10 | sim | sim | ROUTE_PROVEN | **PRONTA** |
| IT-T10-022 Zootecnica (EN) | T10 | sim | sim | ROUTE_PROVEN | **PRONTA** |
| IT-T10-021 Plantgest | T10 | sim | sim | — | **PRONTA** |
| IT-T7-021 Est Ticino Villoresi | T7 | sim | sim | — | **PRONTA** |
| IT-T7-043 Agrofarma Federchimica | T7 | sim | sim | ROUTE_PROVEN | **PRONTA** |
| IT-T5-049 UNICT Di3A | T5 | sim | sim | **CAPABILITY_BLOCK** | bloqueada (M3) |
| IT-T2-034 ARPA Marche | T2 | **não** | sim | ROUTE_PROVEN | bloqueada (M3 por aplicar) |
| IT-T2-051 Arpae | T2 | **não** | sim | ROUTE_PROVEN | bloqueada (M3 por aplicar) |
| IT-T2-056 Arpae (duplicada de T2-051) | T2 | **não** | sim | ROUTE_PROVEN | bloqueada (M3 por aplicar) |
| IT-T5-041 CRPV | T5 | **não** | sim | **UNKNOWN** | bloqueada (M3) |
| IT-T12-041 BURA Abruzzo | T12 | **não** | **não** | ROUTE_PROVEN | bloqueada (M3 + receita T12) |
| IT-T12-057 Generazione Lombardia | T12 | **não** | **não** | ROUTE_PROVEN | bloqueada (M3 + receita T12) |
| IT-T12-074 Open Innovation | T12 | **não** | **não** | ROUTE_PROVEN | bloqueada (M3 + receita T12) |
| IT-T9-021 Fiera Didacta | T9 | **não** | **não** (T9 = coletor social) | ROUTE_PROVEN | bloqueada (M3 + receita T9 web) |

**Excluídas (3), com motivo:** IT-T7-017, IT-T7-033, IT-T7-042 — FONTE em 55 de
55 itens no RELATORIO-DIAGNOSTICO-SALA (comunicação de marca). A M3 confirmou
que as secções alternativas de Chianti e Balsamico são séries paradas em
2022/2020: **a exclusão mantém-se, não é ROTA**.

**Filtros de outras missões, já ligados.** O `plano` lê
`curadoria/ROTAS-ELEGIVEIS-V1.json` (M3) e
`curadoria/RELEVANCIA-POR-FONTE-V1.json` (M3b) **se existirem nesta linha**:
só bloqueiam, nunca promovem (prova `test_filtros_das_missoes_3_e_3b_so_bloqueiam`).
⚠️ O nome e a forma do ficheiro da 3b são **suposição minha** — confirmar com
quem a fizer.

```
COHORT_PROPOSED   = 14
PRONTAS_HOJE      = 6 com o livro desta linha · 5 com a M3 @ 88ce30a8 como filtro
EXCLUDED          = 3 (FONTE de marca, diagnóstico 55/55)
DEPENDS_ON_M2_M3  = 8 dependem da M3 (7 com rota provada mas fora da tabela do coletor + IT-T5-041)
                    + IT-T5-049 bloqueada pela M3 = 9 tocadas pela M3
                    · M2 afecta as 14 (o livro muda sozinho: supervisor PID 117276 desde 21:23)
                    · 4 dependem ainda de uma receita que é decisão do dono (3 × T12, 1 × T9 web)
```

---

## C — INSTRUMENTO

```
py scripts/micro_coleta/micro_coleta.py plano                               # sem rede, sem banco
py scripts/micro_coleta/micro_coleta.py correr --autorizado-pelo-dono       # a ÚNICA porta para a rede
py scripts/micro_coleta/micro_coleta.py relatorio --run-id=<R> [...]        # só SELECT
```

`correr` lança, por fonte pronta, **a porta canónica e mais nada**:

```
py orquestrador/orquestrador.py <apelido> --filtro fonte=<ID> --filtro universo=<Tn>
   → coleta/italy_executor.py (pergunta ao gate outra vez, por dentro)
   → coleta/ingresso.py → guarda/preservar_coleta
```

Recusa, antes de ir à rede: sem `--autorizado-pelo-dono`; sem as quatro
variáveis da Sala operacional (`SINTONIA_COLLECTION_DSN`, `SINTONIA_SALA_DSN`,
`SINTONIA_SALA_BACKEND=POSTGRES`, `SINTONIA_PSQL_EXE`); com
`BANCO_DESCARTAVEL_URL` presente; com egresso ≠ IT.

**Ensaio sem rede — 14 provas, 14 verdes.** `subprocess.run` do instrumento
é trocado por um que rebenta: nenhuma prova consegue alcançar curl, node,
psql ou o orquestrador. Cinco ataques (tirar a trava de egresso, tirar a
autorização, tirar a trava de escrita, deixar a capa aprovar calada, ignorar o
veredito da M3): **os cinco apanhados** por uma prova vermelha.

```
INSTRUMENT_DRY_RUN = PASS   (14/14 · 5 mutantes mortos · relatorio ensaiado só a ler sobre o lote-76)
```

⚠️ O que o ensaio **não** prova: que o orquestrador real, com rede e VPN,
imprime `CORRIDA <STATUS> · <RUN_ID>` na forma que `correr` lê. A forma foi
lida no código (`orquestrador.py::main`), não observada numa corrida desta
missão. Se não casar, `correr` regista `RUN_ID = NAO SEI` e o relatório não
nasce — falha à vista, não calada.

---

## D — GABARITO

`scripts/micro_coleta/GABARITO-MICRO-V1.json` — 10 itens do lote-76, o
veredito esperado e o porquê de cada um, casados por **URL** (um item
recolhido nasce com outro `derived`).

```
GOLD_ITEMS = 10    ESPERADO: 4 SIM · 6 NAO
AUTOR      = Claude, lendo o texto — NÃO é uma pessoa. Precisa de visto humano.
```

Contra ele, a Admission do lote-76 acerta **3 de 10** com a pergunta certa
(834, 841, 842) — **nenhum SIM errado**. Os erros são todos por prudência:
2 matérias de mercado em inglês viram NAO_SEI (régua sem inglês), 5 NAO viram
NAO_SEI.

---

## E — RISCOS ABERTOS

| # | risco | dono |
|---|---|---|
| R1 | 74 dos 76 bytes do lote-76 vivem só na pasta de trabalho `lote-76-v1/XX/`, não no armazém operacional | quem fez o lote-76 / dono do armazém (`guarda/preservar_coleta.py::ArmazemLocal`) |
| R2 | VPN italiana: sem ela nada corre. É **pré-requisito do dono** | Luciano |
| R3 | 7 rotas provadas pela M3 ainda fora da tabela do coletor (`onboardar_rotas_provadas.py --aplicar` não foi corrido) | M3 / coordenação |
| R4 | receita T12 e receita web T9 não existem — 4 fontes nunca chegam à Sala | dono (é política de coleta) |
| R5 | o juiz de capa marca notícias curtas como capa (6/76) | dono de `curadoria/retrato_html.py` |
| R6 | robots «não lido» em 3 sites em 21/09 | coletor (`italy_pilot_collect.mjs`) |
| R7 | régua T10 sem inglês: IT-T10-022 vai dar NAO_SEI mesmo com matéria boa | dono da Admission (RECOMENDAÇÃO 6 do diagnóstico) |
| R8 | o livro muda sozinho (M2 em produção): a coorte de hoje não é a de amanhã | coberto: o gate é perguntado no instante |
| R9 | IT-T12-057, IT-T12-074, IT-T9-021 têm cara de FONTE errada (juventude, inovação, feira de educação) | Source Curator / M3b |
| R10 | a forma do ficheiro de relevância da 3b é suposição | M3b |
| R11 | o controlo negativo de capa é sintético: não há capa real guardada no acervo | quem correr a micro-coleta: guardar uma `INDEX_URL` como controlo |

---

## SYSTEM MAP

Peça nova `C-MICRO-COLETA-INSTRUMENTO` (os testes ficam na gaveta `C-TESTES`).
Cadeia `REGERAR` = OK 20/20.

```
SYSTEM_MAP_CHECK = FAIL — só P9, herdado: provas/recollection_red_team_estrito.mjs
                   (o mesmo do RELATORIO-LOTE-76). As peças desta missão passam.
                   Um P8 meu (o teste declarado em duas peças) apareceu e foi corrigido.
```

---

## ENTREGA

```
MICRO_CRITERIA     = 7 (cada um com comando) + PRÉ-REQUISITO do dono: VPN IT
COHORT_PROPOSED    = 14 · PRONTAS HOJE 5 (com a M3) · EXCLUDED = 3 (FONTE de marca)
DEPENDS_ON_M2_M3   = 9 pela M3 · 14 pela M2 (livro vivo) · 4 ainda pedem receita do dono
INSTRUMENT_DRY_RUN = PASS
GOLD_ITEMS         = 10 (propostos; visto humano pendente)
NETWORK_REQUESTS   = 0 · DB_WRITES = 0
```

`FINAL_HEAD` / `REMOTE_HEAD`: na mensagem de entrega (o commit não contém o
próprio hash).

---

## EM PALAVRAS SIMPLES

Da outra vez, fomos ao mercado sem lista, com o carro no país errado, e
voltámos sem nada no cesto. Desta vez **não fui ao mercado** — deixei tudo
pronto para a ida.

- **A lista de compras.** De 17 fontes que hoje podem ser colhidas, tirei as 3
  de vinho e vinagre que só falam de festas e prémios. Ficam 14. Dessas, **5
  estão prontas hoje**; as outras 9 esperam papelada de outras equipas.
- **Um botão só.** Há um comando que faz a ida inteira. Ele recusa-se a sair
  de casa se a internet não estiver a passar pela Itália, se ninguém autorizou,
  ou se o banco não estiver bem ligado. No fim, ele próprio escreve a nota de
  7 pontos: passou ou não passou.
- **O teste.** Experimentei o botão com um "carro de brincar" — não sai à rua.
  Estraguei de propósito cada trava, uma de cada vez, e o teste apanhou as 5.
- **A folha de respostas.** Escrevi, para 10 notícias já colhidas, se cada uma
  devia entrar ou não e porquê. Serve para ver se a porta acerta. ⚠️ Fui eu que
  escrevi, não uma pessoa — alguém tem de conferir.

Duas surpresas:
- A "página de capa" que a missão de 21/09 disse ter apanhado **era uma
  notícia de verdade**, só que curta. O detector de capas engana-se com
  notícias curtas.
- As cópias originais de 74 notícias do lote-76 estão guardadas numa pasta de
  trabalho, não no cofre oficial. Se alguém apagar essa pasta, perde-se a prova
  de onde elas vieram.

**O que depende de você:** ligar a VPN italiana no dia, e dizer "pode ir".
