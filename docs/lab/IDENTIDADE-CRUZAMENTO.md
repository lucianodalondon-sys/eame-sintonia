# IDENTIDADE-CRUZAMENTO — o mesmo cruzamento entre corridas: como a prova nova se junta e como o casco sabe que mudou

**SINTONIA LAB · MISSÃO-05 · 27/09/2026 · esforço XHIGH (D113)** · pesquisa + desenho + prova de conceito offline.
**Nada foi implementado no motor, no pote, no casco, na Sala ou na coleta.** HARD STOP no fim.

> **A fala do dono (verbatim):** «e como funciona por exemplo, a informacao, cruzamento ja esta no pote, porem chega
> mais uma informacao da inteligencia que faz parte daquele cruzamento especifico, como ele se junta a ele e atualiza o
> casco?» · «isso e prioridade arrumar agora, senao tudo vai virar uma bagunca de duplicacao».

## Como ler

| marca | quer dizer |
|---|---|
| **[M]** | medido, com `ficheiro:linha@commit` ou comando |
| **[M-LAB]** | medido pelo LAB local (PACOTE/POC de 27/09 ~18:45) e **não** re-medido aqui (falta o insumo nesta máquina) |
| **[RE-M]** | re-medido nesta sessão na nuvem |
| **[INF]** | inferência a partir do medido |
| **[HIP]** | hipótese / proposta — precisa de decisão do dono |
| **NÃO SEI** | não há prova; não é negativo |

**Proveniência desta entrega.** O LAB local fez a investigação e ficou sem motor Opus antes de escrever. Esta síntese
parte de `docs/lab-insumos/missao05/` (PACOTE, POC, triangulação) e de `docs/lab-insumos/PESQUISA-CRUZAMENTOS.md`
(MISSÃO-04). **TRIANGULAÇÃO 2/3**: GPT-6 Sol e DeepSeek v4.1-flash responderam às cegas; a do Opus deu **TIMEOUT**
(`triangulacao/MANIFEST.json`: `EXIT_CODE=TIMEOUT`, `resposta-opus.md` com 0 bytes, `RESULT_SHA256=e3b0c442…` =
SHA de arquivo vazio). Esta síntese **não** conta como terceiro voto: é o confronto dos dois votos com o medido.

**HEADs lidos [RE-M]:** esta branch `c15e818` (lote6 `21cc06c0` + insumos) · `origin/claude/cruzamentos-max-sguy1x`
`399e79f8` · `origin/claude/pote-v2-unico-contract-y8o1pi` `8982ce40` · `origin/claude/casco-r7-publication-yb7nsg`
`60ee56b2` · piloto `2b4e095f`.

---

## 0 · Painel

| | medido | fonte |
|---|---|---|
| IDs iguais entre R6 e R7 no pote | **0/47**; 43 objetos com o mesmo conteúdo e ID diferente | [M-LAB] POC `ROTACAO` |
| Sinais com ID igual R6→R7 | **0/10** hoje · **10/10** com o ID proposto `SG2` | [M-LAB] POC `ROTACAO` |
| F1 rótulo × substância citada (R7) | 86 links → **85 perguntas**; só **4** com chave completa (5 links) | [RE-M] |
| F2 portfolio_match | 14 objetos → **2 perguntas** (13 → 1 em OLIVO × mosca da oliveira) | [RE-M] |
| F3 competitive_set | 125 → 125 perguntas hoje; **+60** objetos repetidos a cada novo gatilho de folpet no esquema atual | [RE-M] |
| F4 janela olivo × mosca | 13 itens → 12 perguntas (com a Sala) / 13 (sem a Sala); só **1** com chave completa | [M-LAB] / [RE-M] |
| Fusão ingênua pela lista de culturas do documento | 1388 grupos, **1190** com 2+ links → convergência falsa | [RE-M] contraprova |
| POTE-R7 publicado (`docs/casco/r7`) | 2 cruzamentos, **os dois são tau-fluvalinato do mesmo ARIF** (n.37 e n.38), cultura NÃO SEI | [RE-M] **novo** |
| Red team executável | **17/17** casos · **9/9** mutantes mortos | [RE-M] `identidade-cruzamento/redteam_identidade.py` |

---

## Resposta curta ao dono

[HIP] **O cruzamento passa a ter o nome da PERGUNTA, não do boletim que a trouxe.** A informação nova da mesma pergunta
entra como **mais uma prova** do mesmo nome. A Intelligence recalcula o estado (a partir de todas as provas válidas, da
edição da bula e do relógio) e escreve no pote **o que mudou desde a corrida anterior**: `NOVO`, `FORTALECEU`,
`MUDOU_ESTADO`, `SEM_REVISAO` ou `SAIU` (este último só com causa). O casco apenas lê esse carimbo e mostra «atualizado»
— não compara nem calcula nada.

Duas guardas impedem a solução de virar o erro contrário (juntar o que é diferente):
1. **Chave com NÃO SEI não junta com nada.** O NÃO SEI vira `NAO_SEI@<documento>`, e isso é diferente para cada documento.
2. **A edição da bula não entra no nome.** Ela entra na **avaliação**: edição nova = nova avaliação da mesma pergunta,
   com histórico de→para. Sem isso, cada coleta oficial (D116) duplicaria todas as perguntas de novo.

---

## 1 · CHAVE DE IDENTIDADE (P1)

### 1.1 O defeito, na fórmula [M]

| objeto | fórmula de hoje | o que prende o ID | local |
|---|---|---|---|
| SIGNAL | `"SG-"+sha256(run_id|ITEM_ID|RAW_OBSERVATION_ID|len(SIGNALS))[:16]` | **corrida + posição** | `motor/corrida_da_inteligencia.py:641-644` @c15e818 [RE-M] |
| CROSSING piloto | `"XC-%s-%s-%s" % (source_id, ordem, substancia[:12])` | **origem + ordem** | `provas/o_piloto_da_sala.py:350-351` @2b4e095f [RE-M] |
| CROSSING R7 | `x["CROSSING_ID"] + "@" + si["RUN_ID"]` | **+ corrida da coleta** | `docs/lab-insumos/analise_r7.py:171` [RE-M] |
| CROSSING max | `"XMAX-"+sha256("|".join(partes))[:16]` | OBJETO_ID do piloto, ou `("PM", SALA_CHAVE, …)`, ou `("CS", origem, reg)` | `motor/cruzamentos_max.py:964-965, 985, 998, 1014, 1042` @399e79f8 [RE-M] |
| FUTURO | `"FUT-"+sha256(RUN+ITEM_ID+CORRIDA_UPSTREAM)[:16]` | **corrida** | `montar_entrada_r7.py:99` (fora do Git) [M-LAB] |
| pote | recusa OBJETO_ID repetido **no mesmo compartimento da mesma corrida**; entre corridas, nada | `pacote/pote_intelligence_casco.py:466-467` @8982ce40 [RE-M] |

[INF] Nenhuma dessas fórmulas sobrevive a uma segunda corrida, e a de max junta a pergunta com a origem. Por isso a
«mesma informação que chega de novo» vira cartão novo. **A duplicação não é um defeito de tela: nasce no ID.**

### 1.2 Três coisas diferentes, três identidades (síntese GPT × DeepSeek)

- O **GPT** propôs três IDs (pergunta recorrente · episódio · avaliação).
- O **DeepSeek** propôs um ID (pergunta + edição do dossiê) e pôs documento, semana e produto como prova/resposta.
- **Síntese [HIP]:** duas identidades **persistentes** e uma **por corrida**:

| identidade | nasce de | muda quando | persiste entre corridas? |
|---|---|---|---|
| **CROSSING_ID** `XQ-…` = a pergunta (nas famílias situadas no tempo, a pergunta **já é o episódio**) | `FAMILIA/vN | SLOT=VALOR | …` em ordem fixa por família | nunca (mudar a chave = migração, INT-LAW-224) | **sim** |
| **EVIDENCE_LINK_ID** = pergunta × documento | `CROSSING_KEY | EVIDENCIA` | nunca (idempotente: o mesmo documento lido 2× é 1 link) | **sim** |
| **AVALIACAO_ID** = a resposta daquela corrida | `CROSSING_ID | INTELLIGENCE_RUN_ID` + edição da referência + versão da regra/vocabulário | a cada corrida | **não** — é aqui, e só aqui, que o run entra |

A **SÉRIE** (setembro, outubro, 2027…) não precisa de ID próprio. Ela é o prefixo da chave sem o slot de tempo, uma
**vista derivada**. Isso atende à preocupação do GPT sem criar uma terceira tabela.

**Compatibilidade com a INT-LAW-054** («"Parece a mesma pergunta" não é cache key», `BIBLIA…md:411-419` [RE-M]).
O ID pela pergunta **não reutiliza a resposta**. Ele só ancora a continuidade. Cada corrida **reavalia**, e a
AVALIACAO carrega `INPUTS + LOGIC + PARAMETERS` (provas, regra, edição). Identidade ≠ reuso.

### 1.3 A chave por família [HIP; testada na POC com dados R7]

| família | pergunta | slots da chave (ordem fixa) | **não** entra na chave (vai para PROVA ou AVALIAÇÃO) |
|---|---|---|---|
| **F1** rótulo × substância citada | «o rótulo ADAMA autoriza a substância S na cultura C, na Itália?» | `JURISDICAO · AI · CROP` (+ `TARGET` quando a pergunta nomeia o alvo) | boletim, semana, run, ordem, **edição da bula**, PRODUCT_ID/REGISTRATION_ID (são a **resposta**) |
| **F2** portfolio_match | «o rótulo ADAMA cobre o par cultura × praga?» | `JURISDICAO · CROP · TARGET` | boletim (prova), lugar (a pergunta é nacional: registro vale para IT), edição |
| **F3** competitive_set | «que registro concorrente tem a substância S?» | `JURISDICAO · AI · REGISTRO` (nº de registro **sem** a edição do cadastro) | o boletim-gatilho (hoje está no ID: `cruzamentos_max.py:1042`), a edição `MINSALUTE_FTS6_20260907` (hoje dentro do PRODUCT_ID em 125/125 [RE-M]) |
| **F4** janela cultura × praga (CAP-WIN) | «há janela para a praga P na cultura C, no lugar L, na campanha T?» | `CROP · TARGET · LUGAR · CAMPANHA` (+ `PHENOLOGY` quando o texto a der) | semana do boletim (prova; o estado muda **dentro** do episódio) |
| **F5** futuro (CAP-FUT) | «o evento E acontece em L no horizonte H?» | `ISSUE · GEO · HORIZON_WINDOW` (`BIBLIA…md:1786-1792` [RE-M]) | run (hoje está no hash) |
| sinal (SG) | «esta observação» | `DOCUMENTO · RAW_OBSERVATION_ID · FACT_TIME` | run, posição |
| REND- | métrica da execução | `SOURCE_ID · RUN_ID` — **mantém o run** (é da corrida, não do mundo; DeepSeek, concordo) | — |

[INF] A lugar e a janela entram **só onde a pergunta é situada** (F4/F5). A F1/F2 é uma pergunta de rótulo, e o
registro italiano não muda de Lecce para Siena. Pôr lugar na F2 recriaria os 13 cartões de OLIVO × mosca. Isso responde
à dúvida do GPT («os 13 podem ser aplicações territoriais distintas»): **na F2 não são; na F4, sim**, e lá ficam
separados (§5 da POC: 13 itens → 12/13 perguntas de janela).

### 1.4 Granularidade — as regras

| eixo | regra [HIP] | base |
|---|---|---|
| **lugar** | O código do **nível mais fino que o TEXTO sustentou**. Níveis diferentes nunca juntam (província LE ≠ região Puglia). A hierarquia serve para **vista** (somar LE e BR sob Puglia), nunca para chave. Zona da fonte («Comprensorio LE - Pianura Salentina Sud») é um lugar próprio. «zona costeira» não resolvida vira `NAO_SEI@doc`, **guardando o texto original**. | D112 · INT-LAW-100 (`BIBLIA…md:612`) · `leis/fato_local.py:174-200` (comune só pela lista ISTAT declarada; o ficheiro está ausente hoje ⇒ nenhum comune) [M-LAB] |
| **tempo** | F1/F2/F3 **sem tempo na chave**. F4 usa `CAMPANHA` = ano agrícola **do FACT_TIME**, nunca da publicação. Semana e validade do boletim são prova; o estado muda **dentro** da campanha com histórico. F5 usa `HORIZON_WINDOW` como intervalo. **Sobreposição de janelas NÃO é regra de junção** (ver RT-ARIF, §9). | INT-LAW-100 · CAP-WIN `BIBLIA…md:1846-1852` |
| **cultura** | Espécie e grupo são códigos **diferentes** (`CROP:PESCO` ≠ `CROP_GRUPO:DRUPACEE`). O grupo nunca vira o membro, e o membro nunca sobe para o grupo na chave. 2+ culturas ligadas à substância no texto ⇒ NÃO SEI (ambíguo). A cultura da **lista do documento** (ENTITY_SOURCE=DOCUMENT) **não entra na chave**. | INT-LAW-081/083 · D112 · contraprova: 1190 grupos falsos [RE-M] |
| **praga** | Um código canônico: EPPO onde o registro verificou (`PEST:EPPO:DACUOL`); senão `PEST:LOCAL:…` declarado. Sinônimos só por lista declarada (`leis/boletim_do_campo.py:90-111` MESMO_PROBLEMA). «mosca» sozinho = AMBÍGUO = NÃO SEI. | D104.3 · INT-LAW-082/084 |
| **substância** | `chave_substancia` (`motor/cruzamentos_max.py:260`): TAU-FLUVALINATE = TAUFLUVALINATE; METALAXYL ≠ METALAXYL-M. Quando existir o CAS de `motor/normalize_substance.py`, ele manda. | [RE-M] |
| **produto** | Produto + **edição** é a **resposta** da F1 e a chave da CAP-PORT (`PRODUCT_ID × … × REGISTRATION_VERSION`, `BIBLIA…md:1764-1770`). Nunca é chave da pergunta F1. | D116 |

### 1.5 E quando a chave tem NÃO SEI

[HIP, testado] **Nunca juntar por NÃO SEI.** O slot vira `NAO_SEI@<identidade do documento>`
(`poc_identidade.py:103-113`). Consequências medidas na R7 [RE-M]:
- 81 das 85 perguntas F1 têm cultura NÃO SEI. Ficam **1 por documento** e não se juntam — é o custo honesto de
  ENTITY_SOURCE=DOCUMENT.
- As 2 do POTE-R7 publicado (tau-fluvalinato, ARIF n.37 e n.38, `CHAVES_NAO_SEI` = PRODUCT, CROP, TARGET,
  REGISTRATION_VERSION) continuam **2 identidades**. O que o casco precisa é de um **GRUPO de apresentação**
  (mesma substância, mesmo originador), calculado pela Intelligence e dito como grupo — **não** de uma fusão.
- Quando a chave se resolve depois (a Coleta passa a ligar a cultura), o objeto `NAO_SEI@doc` **não é renomeado**.
  Nasce o link na pergunta completa, e o antigo ganha `SUBSTITUIDO_POR` com causa (INT-LAW-224).

### 1.6 O que já existe para normalizar [M-LAB, conferido no PACOTE §4]

- `leis/boletim_do_campo.py:90-111` (lista MESMO_PROBLEMA, «não é EPPO»).
- `motor/cruzamentos_max.py:68-150` (CULTURAS_ROTULO/ALVOS_CANON por regex, com grupos).
- `motor/normalize_agro.py` (EPPO via dicionário ES + EPPO GD).
- `motor/normalize_substance.py` (CAS, morfologia).
- IAB canário Puglia do LAB: 26 entidades com código (PEST:DACUOL, CROP:OLVEU, PLACE:PROV-LE, ZONE definida pela fonte)
  e alias VERIFICADO/AMBÍGUO.

[INF] **O vocabulário é o gargalo.** A POC usa um v0 de ~12 entradas (`poc_identidade.py:54-67`). O dono do vocabulário
tem de ser **um** registro (D104.3). Cada chave leva `VOCABULARIO=<versão>`, e trocar de versão é migração explícita.

---

## 2 · JANELA DE TEMPO: episódio × série (P2)

[HIP] Setembro e outubro são o mesmo cruzamento ou outro?

- **F1/F2/F3** (perguntas de rótulo/cadastro): **o mesmo**. O boletim de outubro é mais uma prova. O que muda com o
  tempo é a **avaliação** (edição da bula, frescor D117). Teste: RT11.
- **F4** (janela): **mesmo episódio dentro da campanha**. «Não tratar» (n.38) → «soglia superata» (n.39 sintético) é
  uma **transição de estado com histórico** dentro do episódio, com `RELATION=TEMPORAL_CHANGE_IN_RECOMMENDATION`
  (INT-LAW-079). **Não** vira um cartão novo por semana. A campanha 2027 abre episódio novo da mesma série (RT12).
- **F5** (futuro): horizontes diferentes = episódios diferentes. Previsão nunca junta com fato (RT14).

**Por que a campanha e não a semana.** O dono pergunta «ainda importa agora?». A semana na chave faria cada boletim
semanal virar um cartão, que é exatamente a bagunça. A semana fica na prova, e o estado vigente é o da prova mais recente
**por FACT_TIME** do mesmo originador.

**Onde isso quebra [M-LAB].** No ARIF n.38 o cabeçalho diz «16 - 22 settembre 2026», mas o FACT_TIME gravado é
`2026-09-07/2026-09-13` com base `RELATIVA_A_PUBLICACAO`. Conferido no POTE-R7 publicado [RE-M]: a prova de derived:11
tem FACT_TIME `2026-09-07/2026-09-13`, e a de derived:7 (n.37) tem `09 - 15 settembre 2026`. As janelas **se sobrepõem**
sem serem a mesma semana. Qualquer regra «sobrepõe ⇒ mesmo» juntaria errado. Com a regra de CAMPANHA os dois caem na
campanha 2026, o que está certo, mas a **ordem** entre eles depende de um FACT_TIME que está errado.
⇒ Lacuna da Coleta (INT-LAW-031: a Intelligence não conserta o FACT_TIME de upstream). A POC não depende dela para a
identidade, só para a ordem do histórico.

---

## 3 · ACÚMULO DE PROVA (P3)

[HIP] O modelo é append-only de LINKS `(CROSSING_ID, EVIDENCIA, PAPEL, AVALIACAO_ID que o criou)`:

- **EVIDENCIA = o documento, não o item da Sala.** `raw_document_key`; na falta, `SHA:<raw_sha256>`. O mesmo boletim
  entrado 2× pela Coleta (Sala: 13 documentos com 2+ itens, ex. `CAMPANIA:SA:16-09-2026` em dois run_id com o mesmo
  raw_sha256 [M-LAB]) conta **1**. Teste RT15, que mata o mutante M5.
  Nota honesta: o `raw_document_key` falta em 38/242 [M-LAB], e aí cair para o SHA do conteúdo é derivar identidade de
  um campo **que a Coleta entregou**, não fabricá-la. A falta do campo é **gap de contrato da Coleta** (INT-LAW-031).
- **PAPEL** ∈ `APOIA | CONTRADIZ | NAO_CONFERIVEL | CONTEXTO`. O `NAO_CONFERIVEL` (DeepSeek) conserta um disfarce real:
  o FOLPET de Arezzo está UNRESOLVED porque «o cabeçalho … não está no troço guardado no repo» — isso não é «não
  autoriza». No objeto fica só NÃO SEI + motivo curto; o porquê técnico é know-how (D109).
- **Independência** (INT-LAW-071..078, 092): contar **ORIGINADORES** distintos, não SOURCE_ID. A mesma instituição em
  3 distritos = 3 aplicações (se a pergunta for situada) e **1** fonte independente (D111). Teste RT16, que mata o M6.
  **Lacuna:** o campo ORIGINADOR não existe hoje no item. A POC usa `N_SOURCE_ID` como **proxy declarado**
  (`poc_identidade.py:218`), e isso **superconta**: ex. `IT-T3-002` e `CAND-1213` podem ser o mesmo originador.
  NÃO SEI quanto.
- **Contagens separadas, nunca somadas:** `N_LINKS · N_EVIDENCIAS_DOCUMENTO · N_ORIGINADORES ·
  N_VALIDACOES_ESTRUTURAIS` (INT-LAW-092). Ex. [RE-M]: F2 OLIVO × mosca = 13 links · 13 documentos (12 com a Sala) ·
  10 SOURCE_ID.
- **Contradição fica aberta.** 4-5 % × 10-15 % entre originadores = `DIVERGENT_RECOMMENDATIONS`,
  `CONTRADICTION_STATUS=UNRESOLVED` (INT-LAW-079, D111). A mesma origem em períodos diferentes =
  `TEMPORAL_CHANGE_IN_RECOMMENDATION`, que não prova mudança no campo. Teste RT17, que mata o M7.

**Defeito encontrado na POC do LAB [RE-M].** A consolidação F4 da POC (`poc_identidade.py:208-211`) marca
`CONFLITANTE` quando há NO e YES, e o DELTA sintético imprime `NO -> CONFLITANTE` com a nota «TEMPORAL_CHANGE … não é
contradição». **O estado contradiz a própria relação.** Pela INT-LAW-079 o estado vigente deveria ser `YES (desde
n.39)`, com `NO (n.38)` no histórico. O `redteam_identidade.py` corrige isso na função `relacao()`.

**Segundo defeito da POC [INF].** A F1 consolida pelo «melhor estado provado» (`poc_identidade.py:204-207`):
FOLPET × VITE = CONFIRMED_YES com links {UNRESOLVED, CONFIRMED_YES}. Aqui dá certo por acaso: o UNRESOLVED é do lado do
**boletim** (texto não conferível) e a resposta do **rótulo** não depende do boletim. Como regra geral é o que o GPT
alerta: «escolher o cartão mais otimista». Regra proposta: **o estado da F1 é função da avaliação do RÓTULO**
(AI × CROP × edição da referência). A qualidade de cada link é um campo **do link**, e o casco mostra os dois.

---

## 4 · MÁQUINA DE ESTADOS (P4)

[HIP] Três eixos em vez de um SIM/NÃO. Estados de hoje → estados honestos:

| eixo | valores | de onde vem hoje [RE-M] |
|---|---|---|
| **RESPOSTA** (da pergunta) | `SIM_PROVADO` · `SIM_A_CONFIRMAR` · `NAO` · `NAO_SEI` · `NAO_TRATAR_AGORA` (F4) | CONFIRMED_YES 3 · YES_A_CONFIRMAR / POSSIBLE_ANSWER_YES · POSSIBLE_ANSWER_NO / NO 7 · UNRESOLVED 24 |
| **CHAVE** | `COMPLETA` · `GRAO_INCOMPATIVEL` (falta cultura ligada) · `NAO_POSSIVEL` (falta chave indispensável) | PARTIAL_GRAO_INCOMPATIVEL 48 · NOT_POSSIBLE 4 |
| **FRESCOR** (D117) | `EM_DIA` · `PODE_ESTAR_DESATUALIZADO` (>14 d sem checagem) · `A_CONFIRMAR_POR_FRESCOR` (>30 d; **nunca** vira NAO) | `REFERENCIA_USADA` proposto na MISSÃO-04 C.3 |

**Transições permitidas.** Toda transição grava `DE → PARA · QUANDO (transaction time) · CAUSA · PROVAS · versões`
(INT-LAW-125, `BIBLIA…md:729`):

| gatilho | transições possíveis | proibido |
|---|---|---|
| prova nova (link novo) | qualquer RESPOSTA; CHAVE não muda (a chave é a identidade) | apagar a avaliação anterior (INT-LAW-210/211) |
| edição nova da referência (D116) | SIM ↔ NAO ↔ A_CONFIRMAR; FRESCOR → EM_DIA | criar CROSSING_ID novo (RT10, que mata o M8) |
| relógio (D117) | FRESCOR `EM_DIA → PODE_ESTAR_DESATUALIZADO → A_CONFIRMAR_POR_FRESCOR` | RESPOSTA `SIM → NAO` por idade |
| correção na Sala (revisão append-only, `supabase/migrations/033…sql:194-243`) | o link pode ir a `REVOGADO`; a resposta é recalculada com a CAUSA=correção (INT-LAW-212) | reescrever o julgamento passado (INT-LAW-213) |
| chave resolvida (cultura ligada) | nasce o link na pergunta completa; o `NAO_SEI@doc` ganha `SUBSTITUIDO_POR` | renomear em silêncio (INT-LAW-224) |
| regra/vocabulário novos | reavaliação total com CAUSA=`NEW_LOGIC` (INT-LAW-220: new data ≠ new logic) | misturar com CAUSA=nova prova |

**Regra dura [HIP]:** `ESTADO = f(links válidos, edição da referência, relógio, versão da regra, versão do
vocabulário)`. É uma função pura, e a ordem das corridas não pode mudar o resultado. **Dois bitemporais:**
`FACT_TIME` = valid time; `ASSESSED_AT`/`INTELLIGENCE_RUN_ID` = transaction time. Isso casa com INT-LAW-100
(`FACT_TIME ≠ PUBLICATION_TIME ≠ OBSERVED ≠ COLLECTED`).

---

## 5 · COMPOSIÇÃO: Finding / Opportunity / Future (P5)

[HIP, coerente com a MISSÃO-04 C.3 `COMPOSTO_DE: [{OBJETO_ID, ESPECIE, PAPEL}]`]

- A referência passa a ser `{CROSSING_ID, AVALIACAO_ID, PAPEL}`. O CROSSING_ID diz **qual** pergunta; o AVALIACAO_ID diz
  **qual resposta** foi usada. A MISSÃO-04 resolveu isso **dentro** de uma corrida; a MISSÃO-05 dá o CROSSING_ID
  que sobrevive entre corridas.
- **Quando o cruzamento muda de estado:** a Intelligence acha os dependentes (INT-LAW-045, lineage para impact
  analysis) e os **reavalia na mesma corrida**. O Finding ganha nova avaliação com CAUSA=`PAI_MUDOU(<CROSSING_ID>)`.
  A antiga fica no histórico.
- **Ciclos:** as espécies sobem em uma direção só: SINAL → CROSSING → FINDING → OPPORTUNITY/FUTURE. O pote recusa a
  aresta que desce (checagem de DAG, `SEM_PAI`/`CICLO`).
- **Dupla contagem:** os números de um cartão são contados sobre o **fecho** das provas (união por EVIDENCIA,
  depois por ORIGINADOR), nunca pela soma dos filhos. A mesma prova em dois cruzamentos que alimentam a mesma
  Opportunity conta 1 (INT-LAW-092).

---

## 6 · POTE e CASCO: onde vive o «livro» e como o DELTA viaja (P6)

### 6.1 A pergunta de onde guardar — resposta com um fato que muda a conta

[INF, importante] **A Sala é append-only, e cada corrida relê a Sala inteira** (POTE-R7 `CORTE`:
`COPIA_DA_SALA_EM … READY 242`, `TRANSACTION_READ_ONLY on` [RE-M]). Então, **com IDs determinísticos**, a prova antiga
**reaparece sozinha** em toda corrida. O acúmulo de prova **não precisa de livro novo**: vem da Sala + da chave. Isso
refuta o argumento do DeepSeek («sem LIVRO, provas antigas que não reaparecem se perdem»), **desde que** a corrida continue
lendo tudo o que é READY.
NÃO SEI se alguma corrida futura vai fatiar a Sala por data. Se fatiar, o argumento do DeepSeek volta a valer.

O que **não** vem de graça é o **histórico de estado** (de→para, quando). Isso sai da **sequência de potes publicados**,
que já é uma foto auditável por corrida.

| opção | custo | verdade única? | veredito [HIP] |
|---|---|---|---|
| **A · Sequência de potes + DELTA** (a Intelligence compara com o pote **anterior publicado**, apontado por `RUN_ID + SHA256`) | ~zero: nenhum banco, nenhum esquema | sim: o pote é a foto, o delta é derivado e reconferível | **AGORA** |
| **B · Tabela append-only no MESMO Postgres** (`intelligence_cruzamento_avaliacao`, padrão `sala_de_espera_revisao`: trigger recusa UPDATE/DELETE, escrita **só** pela Intelligence, papel próprio) | uma migração | sim (D104.1), se o pote passar a ser **projeção** dela | **DEPOIS**, quando for preciso consultar a série sem abrir N potes |
| C · Arquivo versionado no repo como autoridade | baixo | **não**: concorre com o pote | rejeitar (só como export) |
| D · Banco/grafo separado | alto | não (D104.1) | rejeitar |

GPT e DeepSeek querem B já. Eu recomendo **A agora e B depois**: A resolve a fala do dono na próxima corrida, sem abrir um
segundo lugar de escrita no dia do portal.

### 6.2 Mudança mínima no contrato do pote (v2 → v2.1, DECLARADA) [HIP]

[RE-M] O schema v2 não declara `additionalProperties` no objeto. **Mas** o topo é montado por campos fixos
(`pote_intelligence_casco.py:563-570, 719-727`) e as chaves extras vão para `FORA_DO_CONTRATO`
(`pote_intelligence_casco.py:396-404`). Ou seja: «o JSON aceita» ≠ «o gerador emite» ≠ «o casco lê». Precisa de
mudança de contrato **declarada**, não de contrabando por campo extra (GPT, concordo).

```text
TOPO  (novo, opcional na v2.1; obrigatório a partir da primeira corrida com DELTA)
  ANTERIOR            { INTELLIGENCE_RUN_ID, POTE_SHA256 }  | "NENHUM" (primeira corrida)  | NAO SEI
  REGRA_DE_IDENTIDADE "IDENT-v1"      VOCABULARIO "VOCAB-vN"
  DELTA_CONTAGEM      { NOVO, FORTALECEU, MAIS_EVIDENCIA_MESMA_ORIGEM, MUDOU_ESTADO, ENFRAQUECEU, SEM_REVISAO, SAIU }
OBJETO (novos, opcionais)
  CROSSING_KEY        texto canônico legível (FAMILIA/vN|SLOT=VALOR|…)   — o OBJETO_ID passa a ser XQ-sha(CROSSING_KEY)
  ID_PROVISORIO       true enquanto a D119 vigorar
  ALIAS               [IDs legados: XC-…, XMAX-…, SG-…]  (nunca apagados)
  AVALIACAO_ID        XA-sha(CROSSING_ID|RUN_ID)
  DELTA               { MUDANCA, ESTADO_DE, ESTADO_PARA, EVIDENCIAS_NOVAS[], EVIDENCIAS_REVOGADAS[], CAUSA, RELACAO }
  GRUPO               (só apresentação: ex. AI:TAUFLUVALINATE|ORIGINADOR=ARIF) — nunca usado para contar
LISTA DE TOPO
  SAIRAM              [{CROSSING_ID, ESTADO_DE, CAUSA}]   — o objeto que saiu não está nos compartimentos; está aqui
```

**`SAIU` exige causa** (prova revogada na Sala, referência deixou de autorizar, migração de chave). **Ausência numa
corrida parcial ou falha não é saída**: vira `SEM_REVISAO` (GPT e DeepSeek concordam; sem isso o casco diria «sumiu» a
cada coleta incompleta).

### 6.3 O casco [HIP]

Ele só lê `DELTA.MUDANCA` e desenha um selo: **NOVO · ATUALIZADO (+n provas) · MUDOU DE ESTADO (de→para) · SEM
REVISÃO NESTA CORRIDA** e a lista `SAIRAM` com a causa. O histórico = link para os potes anteriores pela cadeia
`ANTERIOR`. **Não compara potes, não calcula delta, não agrupa por conta própria** (INT-LAW-023/280;
`sintonia-pote-casco.js:14-17` já declara «só FILTER, EXPLAIN e RENDER» [RE-M]).

---

## 7 · MIGRAÇÃO dos IDs atuais (P7)

[HIP; mapa medido: `MAPA-MIGRACAO` 221 linhas [M-LAB] / 211 sem os sinais [RE-M] em
`identidade-cruzamento/MAPA-MIGRACAO-NUVEM.json`]

| ID de hoje | o que ele **realmente** identifica | vira |
|---|---|---|
| `XC-<src>-<ordem>-<subst>@<run coleta>` (86) | um par (documento × substância) = **um LINK** | `ALIAS` do EVIDENCE_LINK na pergunta F1 |
| `XMAX-` refeito (`_oid(OBJETO_ID piloto, REG)`) | link × registro da resposta | `ALIAS` do link; o REG vai para a resposta |
| `XMAX-` PM (`_oid("PM", SALA_CHAVE, …)`, 14) | um link F2 | `ALIAS` do link; 13 → 1 pergunta |
| `XMAX-` CS (`_oid("CS", origem, reg)`, 125) | (gatilho × registro) | pergunta F3 `AI × REGISTRO` (sem gatilho, sem edição) |
| `SG-` (10 R6 / 19 R7) | uma observação **naquela corrida** | `SG2-sha(documento|RAW|FACT_TIME)`: 10/10 estáveis [M-LAB] |
| `FUT-` | um fato futuro naquela corrida | `sha(ISSUE|GEO|HORIZON)` quando houver ISSUE; senão `sha(documento|RAW|FACT_TIME)` como o SG2 |
| `REND-` | rendimento **da corrida** | **mantém** |

Regras: nunca recalcular nem reescrever o ID antigo. O mapa é `ID_LEGADO → (CROSSING_ID, EVIDENCE_LINK_ID) + motivo +
certeza`. **Fusão com estados divergentes = PARAR e perguntar ao dono** (DeepSeek). O caso real é FOLPET × VITE
{UNRESOLVED, CONFIRMED_YES}, e aqui a divergência se explica (lado do boletim × lado do rótulo, §3). O critério continua
de pé para os próximos casos.

---

## 8 · LITERATURA / BENCHMARKS (P8) — só o que decide

**NÃO visitei nenhum site nesta sessão** (regra da missão). As referências abaixo são padrões públicos conhecidos, e as
marcadas «(tri)» foram citadas pelas respostas da triangulação. Serve só para decidir, e nada disso é para adotar como
plataforma.

| padrão | o que decide aqui |
|---|---|
| **Entity resolution determinística com chave de bloqueio** (Fellegi–Sunter; Christen, *Data Matching*, 2012) | Juntar **só por chave canônica**, nunca por semelhança. Confirma INT-LAW-081 e o NÃO SEI ≠ NÃO SEI. |
| **Bitemporal** (Snodgrass, *Developing Time-Oriented Database Applications in SQL*; SQL:2011 PERIOD / system-versioned) | `FACT_TIME` = valid time, `RUN/ASSESSED_AT` = transaction time. Corrigir não apaga (INT-LAW-210..213). |
| **Kimball SCD tipo 2** — kimballgroup.com (tri) | A mesma chave com versões datadas = CROSSING_ID + AVALIACAO_ID. |
| **W3C PROV-O** — https://www.w3.org/TR/prov-o/ (tri) | `wasRevisionOf` / `wasDerivedFrom`: o ALIAS legado e o `SUBSTITUIDO_POR` são revisões, não ID novo. |
| **W3C Cool URIs** — https://www.w3.org/TR/cooluris/ (tri) | O identificador é da **coisa** (a pergunta), não do acesso (a corrida/boletim). |
| **Nanopublications** (Groth et al., 2010; nanopub.net) | Assertion ≠ provenance ≠ publication info: a pergunta ≠ o link de prova ≠ a avaliação. |
| **schema.org ClaimReview** | Claim com várias revisões datadas — o mesmo shape de pergunta × avaliação. |
| **Event/episode identity** (TDT / *event coreference*: mesmo evento = mesmo ator × lugar × tempo compatível) | O episódio F4 exige lugar e janela **resolvidos**; sobreposição temporal sozinha não basta (RT-ARIF). |
| **Delta Lake MERGE / upsert por chave determinística** (tri) | Foto + delta sobre chave estável = opção A do §6. |
| **OpenLineage** — arestas por saída (tri) | Participar do mesmo run não cria aresta (INT-LAW-042) → `COMPOSTO_DE` explícito. |
| **PostgreSQL `INSERT … ON CONFLICT`** — https://www.postgresql.org/docs/16/sql-insert.html (tri) | Idempotência do link (mesmo documento 2× = 1) quando a opção B chegar. |
| **Alertas fitossanitários EPPO** (EPPO Global Database, códigos EPPO; Reporting Service) | O código EPPO é a chave canônica de praga e cultura. Os alertas da EPPO também são **por organismo × país × data do relato** — episódio, não boletim. |

---

## 9 · RED TEAM — 17 casos, com o teste que pega cada um

**Executável:** `python3 docs/lab/identidade-cruzamento/redteam_identidade.py --mutar` → **17/17 passam**;
**9 mutantes plantados, 9 mortos** [RE-M]. Na primeira rodada o M5 (evidência por item em vez de documento) ficou
**VIVO**: o RT15 só contava originadores. O caso foi **fortalecido** (passou a contar evidências também) e o M5 morreu.
Declarado aqui porque é justamente o tipo de buraco que o red team existe para achar.

| # | risco | exemplo real (Puglia/R7) | regra que segura | mutante que o caso mata |
|---|---|---|---|---|
| RT01 | juntar **lugares diferentes** | janela mosca × olivo em Lecce × Brindisi | lugar mais fino do texto na chave F4 | M3 (sobe para região) |
| RT02 | juntar **níveis diferentes** | ARIF n.38 «Puglia ; Lecce» × um boletim só «Puglia» | nível diferente = chave diferente | M3 |
| RT03 | juntar **lugar não resolvido** | «zona costiera» | `NAO_SEI@doc` | M1 |
| RT04 | **NÃO SEI = NÃO SEI** | tau-fluvalinato ARIF n.37 × n.38 (POTE-R7, cultura NÃO SEI) | `NAO_SEI@doc` | M1 |
| RT05 | **cultura genérica** vira específica | drupacee × pesco | grupo ≠ espécie | M2 |
| RT06 | **praga de nome parecido** | mosca dell'olivo × mosca della frutta; «mosca» sozinho | lista declarada; «mosca» = NÃO SEI | — (guarda do vocabulário) |
| RT07 | **separar sinônimos** | bactrocera oleae / mosca delle olive / mosca dell'olivo | MESMO_PROBLEMA → EPPO:DACUOL | — |
| RT08 | **separar grafias** | TAU-FLUVALINATE × tau fluvalinate | `chave_substancia` | — |
| RT09 | juntar **substâncias diferentes** | METALAXYL × METALAXYL-M | `chave_substancia` não corta sufixo | M4 |
| RT10 | **edição nova da bula** duplica tudo | cadastro `MINSALUTE_FTS6_20260907` → próxima edição | edição na AVALIAÇÃO, não na chave | M8 |
| RT11 | **setembro × outubro** separa a F1 | FOLPET × VITE Arezzo × Cantina Negrar 12/05 | boletim é prova | — |
| RT12 | juntar **campanhas diferentes** | olivo × mosca LE 2026 × 2027 | CAMPANHA na chave F4 | — |
| RT13 | **publicação vira fact time** | item sem FACT_TIME, publicado em 20/09 | CAMPANHA só do FACT_TIME | M9 |
| RT14 | **previsão × fato** juntam | FUT (horizonte) × janela observada | família na chave | — |
| RT15 | **o mesmo boletim 2×** conta 2 | CAMPANIA:SA:16-09-2026 em 2 run_id, mesmo raw_sha256 | evidência = documento | M5 |
| RT16 | **3 distritos** = 3 fontes | mesma instituição, mesmo texto, 3 SOURCE_ID | independência por ORIGINADOR | M6 |
| RT17 | **tratar → não tratar** vira contradição | ARIF n.38 NO → n.39 YES (sintético) | TEMPORAL_CHANGE; DIVERGENT só entre originadores | M7 |
| RT-ARIF *(documental)* | **janela sobreposta** junta semanas diferentes | n.37 «09-15/09» × n.38 FACT_TIME «07-13/09» (cabeçalho 16-22/09) | sobreposição não é regra de junção | — (lacuna de FACT_TIME da Coleta, §2) |

---

## 10 · PROVA DE CONCEITO OFFLINE (P10)

**Insumos [RE-M]:** `ANALISE-R7.json` (`2ecdabd4…`, idêntico em `docs/lab-insumos/` e em `cruzamentos-max`),
`CRUZAMENTOS-MAX.json` (`1fc5fb1a…`), `CRUZAMENTOS-MAX-ITENS-DO-POTE.json` (`8c3071b0…`). **Os três SHA-256 batem
byte a byte com os de `POC-RESULTADO.json` do LAB.** Faltam aqui `SALA_ATUAL.json`, os LIVROs R6/R7 e o POTE-R6; o que
depende deles está marcado [M-LAB].

**Achado de proveniência [RE-M]:** o POTE-R7 lido pela POC local tem SHA `2610af4b…`, e o **publicado** em
`docs/casco/r7/POTE-R7.json` @60ee56b2 tem `01899678…`. A POC declara o publicado como `ANTERIOR` do DELTA. Os dois têm
47 objetos. **NÃO SEI** qual deles vai ao ar; a medição 0/47 foi feita no local.

### 10.1 Colapso: quantos IDs atuais viram quantas perguntas

| família | objetos hoje | perguntas | com chave completa | duplicata real hoje |
|---|---|---|---|---|
| F1 | 86 | **85** | 4 (5 links) | FOLPET × VITE: 2 cartões (Arezzo **UNRESOLVED**, Cantina Negrar **CONFIRMED_YES**) → 1 |
| F2 | 14 | **2** | 2 (14 links) | OLIVO × mosca da oliveira: **13 → 1**, 13 docs (12 com Sala), 10 SOURCE_ID, SEM_PAR_LIDO |
| F3 | 125 | 125 | 125 | nenhuma **dentro** da R7; **+60 por gatilho novo** de folpet no esquema atual |
| F4 | 13 | 12 [M-LAB] / 13 [RE-M] | **1** (LE 2026, ARIF n.38) | nenhuma: 12 com NÃO SEI ficam separadas (o certo) |

[INF] **A F1 quase não colapsa, e isso é bom sinal**: 81/85 têm cultura NÃO SEI, porque a cultura veio da lista do
documento. A fusão ingênua por essa lista daria 1190 grupos falsos. A regra **não inventa convergência**. O ganho está na
F2 (13→1), no fim da rotação entre corridas (0/47 → estável) e na F3 (para de duplicar por gatilho).

### 10.2 Corrida seguinte sintética (R8-SINT) e o DELTA

Três itens a mais, **marcados SINTÉTICO**: (a) boletim de vite que cita folpet; (b) ARIF n.39 «soglia superata» em
Lecce; (c) a 3ª cópia do boletim da Campania. `DELTA-R7-R8-SINTETICO-NUVEM.json` [RE-M]:

| mudança | pergunta | de → para | provas |
|---|---|---|---|
| **FORTALECEU** | F1 FOLPET × VITE | CONFIRMED_YES → CONFIRMED_YES | 2 → 3 documentos, 2 → 3 SOURCE_ID |
| **MAIS_EVIDENCIA_MESMA_ORIGEM** | F2 OLIVO × DACUOL | SEM_PAR_LIDO → igual | 13 → 14 docs, 10 → 10 SOURCE_ID (o ARIF já estava) |
| **MUDOU_ESTADO** | F4 OLIVO × DACUOL × LE × 2026 | NO → *(POC: CONFLITANTE — defeito, §3)* → **correto: YES, relação TEMPORAL_CHANGE** | 1 → 2 |
| (nada) | 3ª Campania | — | mesmo documento = mesma evidência: **0 cartões** |
| sem mudança | as outras 222 perguntas | — | — |

**O que o esquema atual faria com os mesmos itens** (`O_QUE_O_ESQUEMA_ATUAL_FARIA`): +1 cartão XC (o 3º FOLPET × VITE),
+1 cartão PM (o 14º OLIVO × mosca), **+60** objetos CS repetidos, a mudança de janela **invisível** (a sonda F4 só vive na
ANALISE), e **todos** os SG/FUT renomeados.

---

## 11 · RECOMENDAÇÃO (P11)

### 11.1 Confronto com a proposta preliminar do coordenador

| # | proposta | veredito | emenda |
|---|---|---|---|
| 1 | ID pela pergunta | **ACEITA com 3 emendas** | (a) a edição da bula **sai** da chave e vai para a avaliação; (b) NÃO SEI → `NAO_SEI@doc`; (c) lugar e janela só nas famílias situadas (F4/F5) |
| 2 | provas acumulam, fontes independentes | **ACEITA** | evidência = documento; independência = ORIGINADOR (campo que a Coleta ainda não entrega) |
| 3 | estado com histórico | **ACEITA** | estado = função pura; 3 eixos; F4 corrigida (TEMPORAL_CHANGE ≠ CONFLITANTE) |
| 4 | Opp/Future por ID | **ACEITA** | referência = `{CROSSING_ID, AVALIACAO_ID, PAPEL}` + reavaliação na mesma corrida |
| 5 | DELTA no pote, casco mostra | **ACEITA** | `SAIU` só com causa; ausência = `SEM_REVISAO`; livro = sequência de potes agora, tabela append-only depois |
| 6 | só a Intelligence escreve | **ACEITA** | o casco nem agrupa por conta própria; `GRUPO` vem do pote |

### 11.2 Texto proposto para a Bíblia da Intelligence (§9 e §20) — [HIP], decisão do dono

> **INT-LAW-096 — Identidade do crossing é a pergunta declarada.** O `CROSSING_ID` deriva de
> `FAMILIA/versão + chaves canônicas da pergunta` (INT-LAW-090), em ordem fixa por família. Origem, documento, run,
> posição e edição da referência **não** entram. A mesma pergunta em N corridas é um `CROSSING_ID`. Identidade não é
> reuso: cada corrida reavalia (INT-LAW-054).
>
> **INT-LAW-097 — NÃO SEI não junta.** Chave indispensável ausente ou ambígua vira `NAO_SEI@<documento>`. Dois NÃO SEI
> nunca produzem a mesma identidade. Resolver a chave depois cria link novo e registra `SUBSTITUIDO_POR`, nunca
> renomeia (INT-LAW-224).
>
> **INT-LAW-098 — Prova é link idempotente sobre o documento.** A evidência é o documento (`raw_document_key`; na falta,
> hash do conteúdo entregue pela Coleta). O mesmo documento lido N vezes é um link. A independência conta originadores
> (INT-LAW-071/092).
>
> **INT-LAW-099 — O estado é função, a avaliação é por corrida.** `ESTADO = f(links válidos, edição da referência,
> relógio, versão da regra, versão do vocabulário)`. A edição nova da referência (D116) é **nova avaliação** do mesmo
> crossing, não crossing novo. A mesma origem mudando no tempo = `TEMPORAL_CHANGE_IN_RECOMMENDATION` (INT-LAW-079).
>
> **INT-LAW-215 — Delta entre corridas é da Intelligence.** Todo pote aponta o pote anterior publicado
> (`RUN_ID + SHA256`) e declara por objeto `NOVO | FORTALECEU | MUDOU_ESTADO | ENFRAQUECEU | SEM_REVISAO`. `SAIU` exige
> causa. Ausência numa corrida parcial não é saída. O casco mostra, não calcula.
>
> **INT-LAW-216 — ID legado vira alias.** IDs de esquemas anteriores (XC-, XMAX-, SG-, FUT-) nunca são reescritos
> nem apagados. Viram `ALIAS` do link ou da pergunta, com mapa reconferível. Fusão com estados divergentes para e sobe
> ao dono.

### 11.3 Ordem de implementação (depois da decisão do dono; nada disto foi feito)

1. **Vocabulário único v1** (D104.3): praga/cultura/lugar com código, alias e versão. Sem ele, a chave não vale.
2. `SG2`/`FUT` sem run (mudança de uma linha cada: `corrida_da_inteligencia.py:641-644`, `montar_entrada_r7.py:99`).
   É o que mais estabiliza, e a POC mediu 10/10.
3. `CROSSING_KEY` + `XQ-` em `cruzamentos_max.py` (substitui `_oid`), com os IDs antigos em `ALIAS`.
4. Contrato pote **v2.1** (§6.2), gerador e validação; o casco lê `DELTA`/`GRUPO`/`SAIRAM`.
5. DELTA pela opção A (pote anterior publicado).
6. `redteam_identidade.py` promovido a teste do motor (`tests/`), com os 17 casos e os 9 mutantes.
7. Opção B (tabela append-only no Postgres da Sala) quando a série precisar de consulta.
8. Pedir à Coleta: campo `ORIGINADOR`, `raw_document_key` nos 38 que faltam, FACT_TIME do ARIF n.38.

### 11.4 ANTES de publicar o portal hoje — mínimo e reversível

**Fato que muda a urgência [RE-M]:** o casco só pede o pote com `?pote=local`; o arquivo é gerado fora do Git e fora de
qualquer deploy; o pote é `EXPERIMENTAL · NAO_PARA_CLIENTE` (`sintonia-pote-casco.js:1-9`, `POTE-R7.json` topo). A
MISSÃO-04 mediu que o portal **no ar** ainda é o legado de 14/09. **NÃO SEI** se a publicação de hoje leva o pote de 47
objetos (2 cruzamentos) ou a saída de max (228). O DeepSeek levantou a mesma dúvida.

1. **Não inventar esquema definitivo hoje** (D119). Todo ID novo sai com `ID_PROVISORIO: true`.
2. **Não mostrar estado consolidado por «melhor link»**. Se FOLPET × VITE aparecer, os dois estados aparecem **lado a
   lado**, com o motivo de cada um (boletim não conferível × rótulo confirmado).
3. **Se o pote de max for ao ar:** a Intelligence emite `GRUPO = CROSSING_KEY` (calculado no gerador, não no casco), e o
   casco agrupa por esse campo, mostrando «N provas, X não conferíveis». Efeito: OLIVO × mosca 13 → 1, FOLPET × VITE
   2 → 1. Isso se desfaz tirando o agrupamento.
4. **Se for o POTE-R7 publicado:** os 2 tau-fluvalinato **ficam 2** (NÃO SEI ≠ NÃO SEI), mas com a legenda «mesma
   substância, mesmo boletim ARIF, semanas n.37 e n.38, cultura NÃO SEI». A contagem é por objeto distinto: 25, não 47,
   porque o `archive` repete 22 objetos das outras gavetas (MISSÃO-04 F.1 item 4; 22 no archive [RE-M]).
5. **Guardar o pote publicado hoje com o SHA** como `ANTERIOR` da primeira corrida com DELTA. Se isso não for feito
   hoje, a primeira comparação de amanhã **não tem base**.

---

## ONDE POSSO ESTAR ERRADO

1. **Edição fora da chave** (contra DeepSeek e contra a proposta do coordenador). Se a edição mudar o **escopo** do
   registro (cultura retirada), eu trato como transição de estado da mesma pergunta; o outro lado trataria como pergunta
   nova. Escolhi o que não duplica. Isso depende do dono.
2. **CAMPANHA como grão da F4** pode ser grossa demais para «agir agora». Se o dono quiser episódio semanal, a
   duplicação volta, mas honesta, porque são janelas diferentes.
3. **Independência por SOURCE_ID** na POC superconta, e NÃO SEI quanto até existir `ORIGINADOR`.
4. **«A Sala inteira é relida a cada corrida»** é [INF] a partir do CORTE da R7. Se isso mudar, preciso da opção B mais
   cedo.
5. **O vocabulário v0 tem 12 entradas.** Os números de colapso da F2/F4 dependem dele. Com o vocabulário real, a F4 pode
   juntar mais ou menos.

## FATO MEDIDO / INFERÊNCIA / HIPÓTESE / NÃO SEI — resumo

- **FATO MEDIDO:**
  - As fórmulas de ID de hoje prendem corrida, posição ou origem (§1.1).
  - Rotação de 0/47 R6→R7 [M-LAB].
  - Colapso F1 86→85, F2 14→2, F3 125→125 (+60 por gatilho), F4 13→12/13 [RE-M/M-LAB].
  - POTE-R7 publicado: 2 tau-fluvalinato do mesmo ARIF [RE-M].
  - Red team 17/17, mutação 9/9 [RE-M].
  - Os insumos da POC batem por SHA [RE-M].
  - Os dois defeitos da POC (§3) [RE-M].
- **INFERÊNCIA:**
  - A duplicação nasce no ID.
  - O acúmulo vem de graça com a Sala append-only + chave determinística.
  - A F1 quase não colapsa por causa da cultura NÃO SEI, e isso é correto.
- **HIPÓTESE:** a regra IDENT-v1, as 6 INT-LAW, o contrato v2.1, a ordem de implementação.
- **NÃO SEI:**
  - Qual pote vai ao ar hoje.
  - Qual POTE-R7 (2610… × 0189…) é o canônico.
  - O número de originadores reais.
  - Se as corridas futuras vão fatiar a Sala.
  - O FACT_TIME correto do ARIF n.38.

## Anexos (em `docs/lab/identidade-cruzamento/`)

| arquivo | o que é |
|---|---|
| `redteam_identidade.py` | os 17 casos + 9 mutantes; `--mutar` |
| `poc_identidade_nuvem.py` | a POC do LAB com 4 cortes declarados (sem Sala/LIVROs/POTE-R6); instruções de insumo no cabeçalho |
| `POC-RESULTADO-NUVEM.json` · `DELTA-R7-R8-SINTETICO-NUVEM.json` · `MAPA-MIGRACAO-NUVEM.json` · `poc-nuvem.out.txt` | as saídas re-medidas |

Os originais do LAB continuam em `docs/lab-insumos/missao05/` (sem alteração).

---

## EM PALAVRAS SIMPLES

Hoje cada cartão ganha o nome **do papel de onde veio** e **da rodada em que foi feito**. Por isso, quando chega mais uma
informação sobre a mesma coisa, o sistema não reconhece que é a mesma e cria outro cartão: já são 13 cartões para
«a bula da ADAMA cobre a mosca da oliveira?», e 2 cartões, com respostas diferentes, para «cobre o folpet na videira?».
E a cada rodada **todos** os nomes mudam.

O conserto é dar ao cartão o nome **da pergunta** (cultura, praga, substância e, quando importa, lugar e safra). Informação
nova sobre a mesma pergunta entra como **mais uma prova no mesmo cartão**. O sistema recalcula a resposta e escreve no
pote «o que mudou desde a última vez». O portal só mostra o selo: *novo*, *atualizado*, *mudou*.

Duas travas evitam o erro contrário, que é juntar coisas diferentes:
- onde a gente **não sabe** (por exemplo, a cultura), o cartão **não se junta** com nenhum outro;
- uma **bula nova** atualiza a resposta, mas **não cria** outro cartão.

Testei em 17 situações reais da Puglia, e as 17 se comportaram certo. Quebrei a regra de propósito de 9 jeitos, e os
testes pegaram os 9.

Para **hoje**: não inventar nome definitivo (marcar «provisório»), não esconder quando dois cartões discordam e guardar o
pote de hoje com a impressão digital (SHA), para amanhã ter com o que comparar. **Nada foi mudado no motor, no pote nem no
portal.**
