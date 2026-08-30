# C–H · SNAPSHOT DE INTELIGÊNCIA — o que já conseguimos dizer

**Data:** 2026-08-30 · **Regra desta rodada:** nenhum estado é promovido. O que está
`PARCIAL` continua `PARCIAL`, mesmo quando conveniente.

> ## ⚠️ ESTADO DESTE DOCUMENTO — DUAS PASSAGENS
>
> **`SNAPSHOT_FROZEN_AT = 2026-08-30`.** Este documento foi escrito contra um snapshot
> congelado do acervo. Ele **não** persegue o HEAD das missões em paralelo.
>
> | seção | passagem | estado |
> |---|---|---|
> | **C · DATA / CAPABILITY INVENTORY** | 1 | **FECHADA** — estrutura do acervo |
> | **D · COUNTRY × CROP × ISSUE** | 1 | **FECHADA** |
> | **E · CONVERGÊNCIAS** | 2 | **PROVISÓRIA** — pode ganhar pernas novas |
> | **F · TOP ATTENTION ITEMS** | 2 | **PROVISÓRIA** — fila sujeita a reordenação |
> | **G · DAILY INTELLIGENCE** | 2 | **PROVISÓRIA** |
> | **H · ACTION MAP** | 2 | **PROVISÓRIA** |
>
> **As quatro missões em paralelo que abrem a PASSAGEM 2** — e que podem criar cruzamentos
> que este snapshot não tinha: `EARLY SIGNAL TERRITORIAL` · `CREATOR MAP · fechamento do
> piloto` · `META COMPETITOR INTELLIGENCE` · `COMPETITOR FORESIGHT (IP / regulatório /
> timeline de produto)`. A lista exata do que reler está em
> `docs/red-team/I-FERRAMENTAS-E-LACUNAS-EAME.md`, seção `REFRESH ÚNICO`.
>
> **Regra do refresh:** ler **uma vez** os handoffs finais; incorporar **somente** o que
> muda materialmente a inteligência; então fechar E, F, G e H.

**Onde os dados vivem.** O acervo está espalhado por seis branches vivas. Este documento leu
todas por `git show`, sem trazer nenhuma linha para cá:

| branch | HEAD | o que guarda |
|---|---|---|
| `origin/claude/sintonia-eame-repo-setup-xccfob` | `4724282` | tronco, EARLY SIGNAL (`SENSOR-PILOT/`), matriz de recortes, universo de pessoas |
| `origin/claude/sintonia-italy-pilot-b1l401` | `b929879` | fundação Itália: regulatório, campo, ciência, hero cases |
| `claude/adama-it-local-catalog` | `b5adc87` | catálogo ADAMA Itália · `ITALY_LOCAL_FOUNDATION_CAPTURE = COMPLETE` |
| `origin/claude/sintonia-france-foundation-n8k2p1` | `2b56904` | fundação de fontes França |
| `claude/adama-fr-local-catalog` | `ae13dea` | catálogo ADAMA França · `FRANCE_LOCAL_FOUNDATION_CAPTURE = COMPLETE` |
| `origin/claude/eame-agro-creators-map-77c4ld` | `08a637d` | CREATOR MAP rodada 2 |
| `origin/claude/adama-es-local-browser` (via `HEAD` detach `fa523a7`) | — | catálogo ADAMA Espanha |

⚠️ **Nenhuma delas foi mesclada na branch padrão.** O acervo do SINTONIA EAME hoje **não
existe inteiro em nenhum lugar**. Isso é um bloqueador de integração, não de inteligência,
e está em `Q · CASCO/PIPELINE GAPS`.

---

# C · DATA / CAPABILITY INVENTORY

Estado por camada, com o número que o sustenta. Nada aqui é estimativa.

## C.1 · REGULATÓRIO — a camada mais madura dos três países

| | ESPANHA (`ES-T4-005` ROPF) | ITÁLIA (`IT-T4-001`) | FRANÇA (`FR-T4-001` E-Phy) |
|---|---|---|---|
| registros no país | 3.084 · **1.993 em vigor** | 17.695 · **3.712 vigentes** | **15.140 produtos** · 177.111 linhas |
| ADAMA | **96 em vigor** | 602 registros · **163 vigentes** · 53 substâncias | 267 já existentes · **72 autorizados** |
| vencendo ≤6 meses | **486** (ADAMA **36**) | 71 (calendário) · 58 (180 d) | não medido nesta rodada |
| vencendo ≤12 meses | **1.004** (ADAMA **61**) | **104** | não medido |
| anomalia `vigente` × caducidade passada | **34** (ADAMA 3) | **8** | não medido |
| cultura × alvo | via consulta ao servidor | 622 relações, **`CROP_ISSUE = 0`** (tabela do PDF não reconstruída) | **367 linhas ancoradas · 161 pares distintos** |
| dose | de PDF | **`NOT_EXTRACTED`** | **562 linhas** |
| BBCH | — | — | **376 mín / 414 máx** |
| titulares distintos | — | 576 | — |
| **ESTADO** | **PROVADO** | **PROVADO no registro · PARCIAL no par cultura×alvo** | **PROVADO — e o mais rico dos três** |

**A França é o registro mais forte da região, e isso ainda não apareceu em lugar nenhum do
produto.** É o único país onde cultura × alvo, dose, BBCH e prazo saem do dado aberto, sem
parse de PDF e sem consulta produto a produto. Espanha exige PDF; Itália exige PDF e a
tabela não foi reconstruída — cruzar as listas produziria **9.746 pares que ninguém
autorizou**, e o artefato registra a recusa.

**Limite que viaja com todos:** `EXPIRY ≠ WITHDRAWAL` · `REGISTRATION ≠ SALES` ·
`REGISTRATION ≠ COMMERCIAL AVAILABILITY` · contagem de registros **não é** participação de
mercado.

## C.2 · PORTFÓLIO LOCAL ADAMA — três países, três estados diferentes

| | ESPANHA | ITÁLIA | FRANÇA |
|---|---|---|---|
| produtos no catálogo público | **56** (enumeração completa) | **0** — `ROUTE_BLOCKED_WAF` | **111** |
| documentos | **147** | 163 etiquetas oficiais (do registro) | **122** baixados, 0 falhas |
| relações com cultura | 711 (588 declaradas) | 622 (605 citadas) | — |
| relações com issue | 176 | 1.677 issues da fonte | 367 pares ancorados |
| usos com cultura **e** alvo | **5** | 0 | **161 distintos** |
| janelas de aplicação | **3** | `NOT_EXTRACTED` | 376/414 BBCH |
| crosswalk catálogo ↔ registro | **44 `LOCAL_REGISTERED`** · 12 presentes sem registro provado | **0 linhas** — só um lado chegou | 111 com alegação de AMM |
| RAW preservado | preservação verificada | — | **234/234 objetos · SHA verificado · 310.516.860 bytes** |
| **ESTADO** | **PROVADO** | **PARCIAL — regulatório completo, catálogo bloqueado** | **PROVADO** |

**A borda da ADAMA é a mesma nos três países.** `adama.com/spain`, `/italia`, `/france`:
403 de WAF para `curl` e para Chrome headless. Espanha e França foram resolvidas com
**Chrome com janela na máquina local**; a Itália ainda não. `EDGE_BOT_DENIED` descreve o IP
desta sessão, **não** o catálogo.

**A regra mais importante desta camada, e ela já está escrita:** *existir na França, na
Itália, no site global ou numa apresentação global **não** faz um produto ser resposta ADAMA
Espanha.*

## C.3 · CAMPO / SINAIS

| país | fonte | o que existe | estado |
|---|---|---|---|
| **ES** | RAIF Andaluzia `ES-T3-001` | **23 safras · 2003–2026 · 148.964 leituras**; campo 1702 visível ≠ 1703 incubado | **PROVADO — e só na Andaluzia** |
| **IT** | boletins regionais `IT-T3-002/003/006` (Vêneto, Lombardia, ERSA FVG) + decretos `lotta obbligatoria` | boletim semanal, último legível **13/08/2026**; 11 sub-áreas nomeadas com pressão 3–6 % em 26/08/2026 | **PROVADO regionalmente** |
| **FR** | BSV — Bulletins de Santé du Végétal | índice oficial responde 200 e lista **17 rotas regionais**; **todos os subdomínios `draaf.*` dão timeout** | **`READ_FAILURE`, não ZERO** |

⚠️ **A assimetria francesa é lei, não circunstância:** a França **não tem camada de campo
provada**. Nenhuma antecedência francesa pode ser construída contra campo — está congelado
em `PILOT-SCOPE-MATRIX-V1.json` desde antes da coleta.

**Cautelas que viajam com o campo espanhol:** as parcelas do RAIF **não são amostra
aleatória**; a média nunca viaja sem o `n`; a doença é **provincial, não regional** —
a média não descreve nenhuma província.

## C.4 · CIÊNCIA E PESSOAS

- **Corpus espanhol** `ES-T5-002`: **1.771 documentos**, 16 campos, **9.958 autores
  distintos**, 380 instituições, **152 pesquisadores** no quadro (eram 153 — um ID
  conflacionado foi removido).
- **`REGION_OF_STUDY` é 0 % em 1.771 de 1.771**, e está certo: afiliação de autor **não é**
  local do experimento.
- **Universo do piloto** (`SPEAKER-UNIVERSE-PILOT-V1.json`), congelado antes de qualquer
  execução paga:

| recorte | candidatos | elegíveis | tentados | **identidade PROVADA** |
|---|---:|---:|---:|---:|
| ES · olivo × repilo | 28 | 23 | 2 | **2** |
| ES · cereal × septória | 62 | 41 | 3 | **2** |
| IT · videira × flavescência | 216 | 103 | 2 | **2** |
| IT · trigo duro × fusarium | 135 | 80 | 2 | **2** |
| FR · videira × míldio | 278 | 104 | 2 | **2** |
| FR · cereal × septória | 326 | 125 | 2 | **2** |
| **TOTAL** | **1.045** | **476** | **13** | **12** |

Treze pessoas nomeadas, com ORCID resolvido em `pub.orcid.org`, instituição declarada e
obra em 2024 ou depois — Blanca B. Landa e Jesús Mercado-Blanco (IAS-CSIC),
Andrea Sánchez-Vallet, Lukas Meile e Cristian Carrasco-López (CBGP),
F. Quaglino (Milão), Nicola Mori (Verona), Massimo Blandino (Turim), Antonio Logrieco
(ISPA-CNR), François Delmotte, Isabelle D. Mazet, Frédéric Suffert e Thierry C. Marcel
(INRAE).

**Estado: `IDENTITY_PROVED` nos seis recortes.** E o artefato diz o que isso **não** é:
*"não é prova de que estas pessoas falam publicamente"*.

- **Canal público** (`SENSOR-PILOT/CANAL-IDENTIDADE.json`): 44 candidatos →
  **7 `PROVED` · 12 `PLAUSIBLE` · 25 `NOT_PROVED`**, cobrindo **5 pessoas com perfil
  provado**. Método: nome completo normalizado veta; cidade declarada no ORCID confirma.

## C.5 · EARLY SIGNAL / VOZ — o que a coleta territorial mediu

`SENSOR-PILOT/MEDICAO.json`, seis recortes congelados, **US$ 0,00 de execução nova**:

```
VÍDEOS ................ 431   (9 duplicatas interceptadas)
  NOISE ............... 220     TECHNICAL_INTERPRETATION ... 13
  NOT_ENOUGH_TEXT ..... 129     MARKETING .................. 11
  EVENT_PROMOTION ......48      RESEARCH_COMMUNICATION ...... 8
                                FIELD_OBSERVATION ........... 2
TRANSCRIÇÕES ........... 15   ·  300.008 caracteres
COM PAÍS DO FATO ...... 113 de 431
TECNICAMENTE RELEVANTES  23 de 431

COMENTÁRIOS ............ 991   (601 comentaristas únicos)
  OPINION ............. 571     QUESTION ................... 196
  NOISE ............... 203     TECHNICAL_REPLY ............. 13
                                FIRST_PERSON_FIELD_REPORT .... 6
                                MARKETING .................... 2
COM PAÍS DO FATO ....... 35 de 991
```

**Duas leituras, e elas são opostas:**

1. **`FIELD_VOICE_EXISTS = PROVADO. `FIELD_VOICE_DENSITY` = BAIXA.**
   **6 relatos de campo em primeira pessoa dentro de 991 comentários** — e distribuídos:
   ES·olivo 2 · IT·videira 2 · FR·cereal 1 · FR·videira 1. Existe. É raro.
   **6 em 991 não sustenta série temporal, tendência nem alerta.**

2. **A pergunta é o achado, não a resposta.** **196 perguntas em 991 comentários (19,8 %)**.
   Isso confirma, num segundo corpus e em três países, o que a rodada espanhola já havia
   medido: *comentário de YouTube mede **demanda por informação técnica**, não estado do
   campo.* Usá-lo como sensor de campo é ler a pergunta como se fosse resposta.

**Estados que o briefing desta missão declara e que o repositório NÃO contém.**
Procurei em todas as branches: as strings `TECHNICAL_PERSON_AS_EXPERT_DIRECTORY`,
`TECHNICAL_PERSON_AS_EXPLANATION_SOURCE`, `TECHNICAL_PERSON_SENSOR`,
`PERSONAL_YOUTUBE_AS_DAILY_SIGNAL_SOURCE`, `FIELD_VOICE_EXISTS`, `FIELD_VOICE_DENSITY` e
`AUDIENCE_TECHNICAL_QUESTION` **não existem em nenhum arquivo**. São vereditos da aba
árbitra, e esta rodada os respeita como vieram. **Mas eles não têm artefato.** As medições
acima os sustentam; o veredito escrito não está no acervo. Registrado em `O · INTELLIGENCE
GAPS`.

## C.6 · CREATOR MAP — rodada 2

`WHO-COULD-MARKETING-CALL.json`: **18 fichas** em `COUNTRY → REGION → CROP`.

```
ACTIVATION_READY ...  2      IT  7
PROMISING .........  4      FR  6
RESEARCH_NEEDED ... 12      ES  5
```

**Os dois `ACTIVATION_READY`:**

| país | região | cultura | creator | atividade |
|---|---|---|---|---|
| IT | Limena, Padova (Veneto) | milho, alfafa, soja, forragem | **Davide Gomiero** `@gomierofarm` | 6 posts/30 d · 12/90 d |
| ES | Níjar, Almería | pimento, tomate, hortícolas | **Bio Campojoyma** `@biocampojoyma` | 1/30 d · 7/90 d ⚠️ **conta de empresa** |

`ACTIVATION_READY` significa *"o Marketing já consegue avaliar esta pessoa"* — **não**
"contratar", **não** "campanha aprovada". Exige seis provas, e nem marca nem seguidores
estão entre elas.

**O achado mais reaproveitável da rodada não é a lista: são os erros.** Seis identidades
resolvidas em fonte primária falharam de **cinco maneiras diferentes** — handle errado na
seed (`@davide_gomiero` → o real é `@gomierofarm`, 457 mil seguidores); nome **e** handle
errados; pessoa ≠ persona (*Tomy Rohde* é alter ego de Fernando Giraldo); pessoa ≠ empresa
(`@biocampojoyma` é a conta da empresa); e um handle **parado desde 2012** cuja comunidade
real nasceu em 2020 — medir atividade ali teria produzido `DORMANT` para quem publica.

**Seis farmer creators com `ACTUAL_FARMER = PROVED`:** Gomiero (IT, ~400 ha, 1.200 bovinos)
· Leonardo Leggieri (IT, olivicultor pugliês) · Fernando Giraldo (ES, olivarero) ·
Francisco J. Montoya (ES) · David Forge (FR, 160 ha) · Gilles Van Kempen (FR).

**Concorrência observada com creators:** BASF (ES, `#YoSoyAgricultor`, 2020) · Seipasa (ES,
*Tomatito*, TOMATE, 2026) · Syngenta (ES, *Embajador del AOVE*, OLIVO, 2026) ·
Bayer (FR, Salon de l'Agriculture, 2023). **`PRODUCT_ACTIVATION_PROVED`: nenhum caso nos
três países.** E `ADAMA_CREATOR_COLLABORATION = NOT_OBSERVED` — busca feita, nada
encontrado, **o que não é "a ADAMA nunca fez"**.

**Limites duros:** 34 dos 43 hubs `NOT_TESTED` com `PEOPLE_EXTRACTED = 0`; audiência não
medida em ninguém fora de Gomiero; **só Instagram** foi usado.

## C.6 · ESCALA E MERCADO

- **Área por NUTS2** `EU-T1-001` e **preço de cereal** `EU-T10-001`: as **únicas duas
  dimensões comparáveis** entre os três países (X-008).
- **França 2024** (`apro_cpshr`, consulta própria): cereais **8.526,6 mil ha** — trigo mole
  4.214,6 · cevada 1.808,5 · oleaginosos 2.233,0 · milho grão 1.593,9. Espanha:
  **4.938,5 mil ha** de cereais liderados por cevada, mais o olivar.
- **Olivar andaluz** (MAPA 2024): **1.665.100 ha** — Jaén 589.047 · Córdoba 376.967 ·
  **Sevilla 253.293**.
- **`ha × incidência` é `RELATIVE EXPOSURE INDEX`.** Ordena. **Nunca dimensiona.** Não é
  hectare afetado, área tratada, demanda nem venda.
- **Rendimento por região não existe** (medido). `MARKET` não é um dataset.

## C.7 · CLIMA · COMPETIÇÃO · DISTRIBUIÇÃO

| camada | estado | por quê |
|---|---|---|
| **CLIMA** | **PROVADO como exposição · `NÃO COMPÕE` como explicação** | X-009 refuta clima → doença. E **a janela escolhida inverte o sinal** (CASE-006) |
| **COMPETIÇÃO · resposta registrada** | **PROVADO** (X-005) | trigo × septoriose FR: BASF 22 · Bayer 20 · ADAMA 6 |
| **COMPETIÇÃO · comunicação** | **BLOQUEADA** | 1 rota provada de 5 majors (sitemap Bayer ES, 265 URLs). Syngenta, ADAMA e BASF: 403. **403 não é ausência de comunicação** |
| **COMPETIÇÃO · ativação paga (Meta)** | **`NÃO TESTADO`** | `EU-T9-002` nomeada como fonte estratégica, nunca aberta. `NÃO TESTADO` ≠ `AUSENTE_MEDIDO` |
| **DISTRIBUIÇÃO** | **PARCIAL, só FR** | SIRENE: 4.646 atacadistas de grãos. Dá **a rede**, não o **fluxo** |

## C.8 · TEMPO — a camada mais fraca, e a que o casco mais quer

```
JANELA AGRONÔMICA POR CULTURA × REGIÃO ......... NÃO CONECTADA em ES, IT e FR
JANELA REGISTRADA (rótulo) ..................... FR sim (376/414 BBCH) · ES 3 · IT 0
JANELA REGULATÓRIA (vencimento) ................ PROVADA nos três — é a única forte
FENOLOGIA OBSERVADA ............................ IT sim, pontual · ES não · FR não
IDADE DA EVIDÊNCIA ............................. derivada, nunca persistida
JANELA DE DECISÃO ORGANIZACIONAL ............... NÃO DETERMINADA em lugar nenhum
```

**O vencimento de registro é a única antecipação temporal forte que este projeto tem** — e
ela é forte porque a data é **publicada**, não prevista. Tudo o mais que parecia antecipar
foi medido e reprovado: voz × campo deu `NO_RELIABLE_SIGNAL` (ρ máximo 0,442 contra crítico
≈0,648 com n=10, e os sinais **se invertem** entre defasagens); o backtest de lead time deu
**1 safra no melhor caso e 0 em duas de três**.

## C.9 · PLACAR DA CAMADA DE EVIDÊNCIA

`37 SOURCE_IDs · 26 fichas · 16 GREEN · 4 YELLOW · 0 RED · 16 NÃO SEI` ·
**649 provas automatizadas** · 16 amostras com proveniência obrigatória testada.
Cruzamentos: **4 COMPROVADOS · 4 PARCIAIS · 3 NÃO COMPÕEM · 2 POSSÍVEIS NÃO TESTADOS.**

---

# D · MATRIZ COUNTRY × CROP × ISSUE

Já existe, e foi construída antes desta rodada: **`PILOT-SCOPE-MATRIX-V1.json`** —
85 arquivos lidos, **124 pares** encontrados, congelado pela aba árbitra em 2026-08-30.

⚠️ **O que a matriz mede, escrito por ela mesma:** *"MENÇÃO do par no artefato de uma
camada"*. E o que **não** mede: não mede a força da camada — `MENTION ≠ EVIDENCE`; não mede
quantas leituras, papers ou vídeos; não afirma que o artefato **trate** do par, só que o
**cita**; e o país é o país **citado no artefato**, não o lugar do fato.

**Ler a matriz como cobertura é o erro mais fácil desta rodada.** `ES · OLIVE · SEPTORIA`
aparece com 6 camadas — septória é doença de cereal, não de olivo. É colisão de vocabulário,
não convergência. **A matriz é achadora de pistas; não é evidência.**

## D.1 · Distribuição

```
por país      ES 46 · IT 42 · FR 36
por lastro    1 camada  38 pares      5 camadas  4 pares
              2 camadas 34 pares      6 camadas  6 pares
              3 camadas 26 pares      7 camadas  1 par
              4 camadas 14 pares      8 camadas  1 par
```

**Só 11 pares em 124 (8,9 %) têm 5 ou mais camadas.** A cauda é longa e rasa.

## D.2 · Os pares com mais lastro

| país | cultura | issue | camadas | artefatos | quais camadas |
|---|---|---|---:|---:|---|
| ES | VINE | DOWNY_MILDEW | **8** | 9 | case, competitor, field, portfolio, radar, researcher, science, voice |
| ES | OLIVE | **REPILO** | **7** | **27** | case, field, portfolio, radar, researcher, science, voice |
| ES | CEREAL | SEPTORIA | 6 | 15 | case, field, portfolio, radar, researcher, science |
| ES | MAIZE | — | 6 | 10 | — |
| FR | VINE | DOWNY_MILDEW | 6 | 7 | case, competitor, portfolio, radar, **regulatory**, science |
| FR | CEREAL | SEPTORIA | 5 | 6 | case, portfolio, radar, researcher, science |
| IT | VINE | FLAVESCENCE | 1 | 1 | radar — **e é o caso corrente do país** |
| IT | DURUM_WHEAT | FUSARIUM | 3 | 3 | radar, researcher, science |

**A anomalia mais informativa da tabela:** `IT · VINE · FLAVESCENCE` tem **1 camada de
menção e é o caso italiano mais forte que existe** (`IT-HERO-001`, convergência 5/5). Prova,
sozinha, que **contagem de menção não mede caso** — e que a matriz precisa da leitura humana
que este documento faz.

## D.3 · Os seis recortes congelados do piloto

Escolhidos pela árbitra **antes** da coleta, com a regra escrita:
*não trocar recorte, não afrouxar limiar, não otimizar o desenho depois de ver o resultado.*

| recorte | por que foi escolhido |
|---|---|
| **ES-OLIVE-REPILO** | o par mais lastreado do acervo; **única série de campo longa** (23 safras, 148.964 leituras) — o único com baseline real |
| **ES-CEREAL-SEPTORIA** | segundo par espanhol; **VOICE ausente de propósito** — é o lado cerealista sem voz medida |
| **IT-VINE-FLAVESCENCE** | caso **corrente** do país, janela de monitoramento aberta |
| **IT-DURUM_WHEAT-FUSARIUM** | onde a voz humana **já** foi medida e deu `HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL`: 8 alvos, 4 com identidade resolvível, **3 posts num ano inteiro** |
| **FR-VINE-DOWNY_MILDEW** | par francês mais lastreado; **par regulatório nº 1 do país** — 168 usos em X-007 |
| **FR-CEREAL-SEPTORIA** | espelha ES·CEREAL·SEPTORIA — **o mesmo par nos dois países**, o eixo cross-market que X-006 já provou forte (82,1 % do uso) |

---

# E · CONVERGÊNCIAS

**Regra aplicada:** independência precisa ser provada. Mesmo instituto em dois canais **não**
vira duas fontes. Contagem de pernas com evidência **nunca** vira score.

| # | recorte | classe | pernas com evidência independente |
|---|---|---|---|
| **1** | **IT · videira × flavescência dourada** (Veneto + Lombardia) | **STRONG_CONVERGENCE** | **5/5** — norma regional (`lotta obbligatoria`, decreto) · sinal de campo corrente (boletim semanal, 13/08/2026) · ciência (2 pesquisadores ORCID, Milão e Verona) · resposta ADAMA registrada (dos 163 vigentes) · escala regional (ISTAT + Eurostat) |
| **2** | **IT · milho × piralide / *Diabrotica*** (FVG sinal, vale do Pó escala) | **STRONG_CONVERGENCE** | **5/5** — e o próprio boletim ancora a decisão de 2027 em 2026 |
| **3** | **ES · olivar × repilo** (Sevilla, Córdoba) | **CONVERGENCE_FORMING** | campo (coorte de 301 parcelas, 23 safras) · escala (253.293 ha) · ciência (IAS-CSIC, 2 ORCID) · portfólio (NEPTUNE ES-00211) — **falta tempo**: relógio agronômico não conectado |
| **4** | **IT · portfólio × calendário de vencimentos** (nacional) | **PARTIAL_CONVERGENCE** | 3/5 — regulatório forte, campo e ciência não entram |
| **5** | **FR · videira × míldio** | **PARTIAL_CONVERGENCE** | regulatório (168 usos, ADAMA 17) · ciência (INRAE, 2 ORCID) · concorrência registrada · **campo `READ_FAILURE`** e nenhuma ativação encontrada |
| **6** | **ES ↔ FR · cereal × septória** | **WAITING_FOR_CONFIRMATION** | o mesmo par nos dois países, com ciência e portfólio dos dois lados; **a ponte é a molécula (X-006, 82,1 % do uso)** e ela **não foi executada para este par** |

**Convergências que NÃO existem, e é importante dizer:**

- **Voz × campo:** `NO_RELIABLE_SIGNAL`, medido duas vezes. Não é convergência fraca —
  é **refutada**.
- **Ciência × voz pública por nome:** `NOT_REACHED`. Casamento estrito deu zero; o frouxo
  produziu falso positivo demonstrável (*"Universitat de Barcelona"* casou com uma unidade
  de pesquisa em **tuberculose**). **Falta identificador que atravesse camadas** (ORCID/ROR)
  — e o universo do piloto acabou de criar exatamente isso para 13 pessoas.
- **Clima → doença:** `NÃO COMPÕE` (X-009).
- **Concorrência × comunicação:** `NÃO COMPÕE` — 4 de 5 majors inacessíveis.

**Confundidor aberto, e ele não fechou:** a concordância geográfica entre voz e exposição
(ρ 0,96 no YouTube, 0,94 no LinkedIn) pode ser **densidade institucional**, não sinal
agronômico — Córdoba concentra IAS-CSIC, UCO e ETSIAM **e** lidera a voz.
**`CONCORDÂNCIA GEOGRÁFICA ≠ ANTECIPAÇÃO TEMPORAL`.**

---

# F · TOP ATTENTION ITEMS

**Quatro itens sobrevivem à régua.** Não cinco, não dez. Cada um responde: por que merece
atenção · o que é novo · o que sustenta · o que falta · tempo · quem olha.

---

### F.1 · ES · REGULATÓRIO · vencimentos em janela curta — `REGULATORY DEADLINE`

```
COUNTRY   ES     REGION nacional     CROP todas     ISSUE exposição de registro
```

- **Por que merece atenção:** **486 autorizações espanholas vencem em ≤6 meses e 1.004 em
  ≤12.** Da ADAMA: **36 e 61**. **Syngenta 37 e ADAMA 36 são os dois titulares mais expostos
  na janela de 6 meses.**
- **O que é novo:** nada — e isso é a força. A data é **publicada**, não prevista.
- **Sustenta:** ROPF `ES-T4-005`, snapshot `ropf_20260829.json.gz`, fonte oficial primária.
- **O que falta:** `BY_HOLDER`, `TOP_HOLDERS`, `BY_SUBSTANCE` **não existem na rota
  canônica** — saem do mesmo snapshot; `CROP_COVERAGE` custa 972 requisições.
- **TEMPO:** **`WINDOW_OPEN`** — a única janela de horizonte verificável do projeto.
- **Quem deve olhar:** **REGULATÓRIO** (dono) · PORTFÓLIO · MARKET DEVELOPMENT.
- **Decisão possível:** priorizar renovação e verificar quais dos 36 sustentam pares
  cultura × alvo relevantes.
- **NÃO diz:** que produto sairá do mercado. `EXPIRY ≠ WITHDRAWAL`.

---

### F.2 · IT · VIDEIRA × FLAVESCÊNCIA DOURADA · Vêneto + Lombardia — `GEOGRAPHIC PRIORITY`

```
COUNTRY IT   REGION Vêneto (principal) + Lombardia   CROP videira   ISSUE flavescência
```

- **Por que merece atenção:** **cinco camadas independentes falam do mesmo par ao mesmo
  tempo** — a única convergência 5/5 com sinal **corrente** de toda a região.
- **O que é novo:** boletim semanal, **último legível 13/08/2026**; adultos do vetor
  *Scaphoideus titanus* presentes, sintomas foliares expressos ago–set.
- **O que é recorrente:** `lotta obbligatoria` é **obrigação anual por decreto** — não é
  novidade, é calendário legal.
- **Sustenta:** decreto regional · boletim · 2 pesquisadores ORCID (Milão, Verona) ·
  resposta ADAMA registrada · escala ISTAT/Eurostat.
- **O que falta:** **disponibilidade comercial `NÃO SEI`** (exige dado interno, que não
  virá); janela 2027 a confirmar; ativação de concorrente `NÃO SEI`.
- **TEMPO:** **`WINDOW_OPEN` (monitorar) + `FUTURE SEASON` (preparar 2027)**. Evidência com
  **17 dias** na data desta leitura.
- **Quem deve olhar:** **TÉCNICO / AGRONOMIA** · MARKET DEVELOPMENT · PORTFÓLIO ·
  MARKETING (material técnico para 2027).
- **NÃO diz:** que há surto, nem que a aplicação é necessária. Janela aberta nunca confirma
  necessidade.

---

### F.3 · ES · OLIVAR × REPILO · Sevilla e Córdoba — `GEOGRAPHIC PRIORITY`

```
COUNTRY ES   REGION Sevilla · Córdoba (Andaluzia)   CROP olivar   ISSUE repilo
```

- **Por que merece atenção:** **Sevilla é a única província no top-3 das duas réguas** —
  sobe **e** tem escala. Coorte de repilo **1,10 → 2,74 em duas safras, sobre 301 parcelas**,
  em **253.293 ha** de olivar.
- **O que é recorrente:** 23 safras de série. Este é o único par do acervo com **baseline
  real**.
- **Limite obrigatório, e ele é grande:** **2,74 está abaixo do próprio máximo histórico
  (7,07 em 2009)**; a área é de **2024** e a incidência é de **2026**; as parcelas do RAIF
  **não são amostra aleatória**.
- **Portfólio ADAMA:** **NEPTUNE `ES-00211`** é resposta registrada para repilo em olivo —
  **com caducidade em 15/08/2026**, e `REGISTRATION ≠ COMMERCIAL AVAILABILITY`.
- **TEMPO:** **`NOT_KNOWN` para a janela agronômica** (relógios não conectados) ·
  **`FUTURE SEASON`** para preparação. Honestamente: **não sabemos se ainda dá tempo nesta
  safra**, e dizer que dá seria inventar.
- **Quem deve olhar:** **MARKET DEVELOPMENT** · TÉCNICO · **REGULATÓRIO** (a caducidade de
  15/08/2026 está em renovação?) · PORTFÓLIO.
- **NÃO diz:** hectares afetados, área tratada, demanda ou venda. `ha × incidência` **ordena**.

---

### F.4 · FR · VIDEIRA × MÍLDIO — `ACTIVATION QUESTION`

```
COUNTRY FR   REGION nacional   CROP vigne   ISSUE mildiou
```

- **Por que merece atenção:** **168 usos autorizados no par; a ADAMA é a empresa nomeada com
  mais usos (17)** — e **nenhuma campanha 2025–2026 foi encontrada nas fontes pesquisadas**.
- **Sustenta:** E-Phy `FR-T4-001` (registro e usos) · X-007 (par nº 1 do dicionário
  canônico francês) · INRAE (2 pesquisadores ORCID).
- **O que falta:** campo francês é **`READ_FAILURE`** (BSV bloqueado); comunicação de
  concorrente inacessível em 4 de 5 majors; Meta Ads Library **nunca testada**.
- **TEMPO:** **`NOT_KNOWN`.**
- **Quem deve olhar:** **MARKETING** (pode avaliar comunicação) · MARKET DEVELOPMENT ·
  PORTFÓLIO.
- **A saída é uma pergunta, não uma oportunidade:** *este nível de ativação pública é
  deliberado?* **Quem responde é a ADAMA.**
- **NÃO diz:** que a ADAMA está silenciosa. O correto é
  **`NO PUBLIC ACTIVITY FOUND IN SEARCHED SOURCES`**.

---

### Itens que **não** entraram, e por quê

| candidato | por que ficou fora |
|---|---|
| ES · 34 registros `Vigente` com caducidade passada (31 na mesma data) | é `INVESTIGATE` de qualidade de fonte, não item de decisão de negócio. Vai para `Análises`, não para a fila |
| IT · milho × piralide (5/5) | forte, mas duplica a lógica de F.2 sem trazer decisão nova nesta rodada |
| Creator `ACTIVATION_READY` (Gomiero, IT · milho) | **é oferta, não atenção.** Só vira item de fila quando amarrado a um caso — hoje nenhum caso italiano de milho está aberto |
| ES · milho × *Amaranthus palmeri* | tem caso escrito, **não tem camada de campo** |
| Qualquer item de "voz crescendo" | **não existe baseline.** Sem linha de base, o sistema emite observação, nunca alerta |

---

# G · DAILY INTELLIGENCE BY DEPARTMENT

*Por que cada área abriria o Sintonia amanhã?* Notícia nova **não** é requisito.

| área | motivo real hoje | com que dado | frequência honesta |
|---|---|---|---|
| **MARKET DEVELOPMENT** (usuário central) | a fila de quatro itens de `F`, e o que mudou de estado nela | ROPF · RAIF · boletins IT · E-Phy | **semanal** — a fila não muda todo dia, e fingir que muda é vender feed |
| **REGULATÓRIO** | 486 ES em ≤6 m (36 ADAMA) · 104 IT em ≤12 m · 34 + 8 anomalias `vigente`/vencido | registros nacionais | **semanal**, e **diária** perto de data-limite |
| **PORTFÓLIO** | assimetria de resposta registrada entre países; 12 produtos ES presentes no catálogo **sem registro provado**; crosswalk IT em **zero** | crosswalk catálogo↔registro | **por evento** de catálogo ou registro |
| **TÉCNICO / AGRONOMIA** | boletim italiano semanal com fenologia observada; coorte RAIF; **196 perguntas técnicas** de audiência com o que o campo não entende | `IT-T3-*` · `ES-T3-001` · `SENSOR-PILOT` | **semanal na safra** |
| **MARKETING** | a pergunta de ativação FR; **18 fichas de creator** com `MISSING_PROOFS`; 4 casos de concorrente com creator (BASF, Seipasa, Syngenta, Bayer) | `WHO-COULD-MARKETING-CALL` · `BRAND-COLLABORATIONS-EU` | **quinzenal** |
| **COMERCIAL** | **hoje: quase nada.** Sem dado interno, o Sintonia entrega contexto de território e janela, não pipeline | — | **por caso**, não por dia |
| **CIÊNCIA & P&D** | 13 pessoas com ORCID nos seis recortes; 1.771 documentos ES; o confundidor de Córdoba, que é uma pergunta de pesquisa real | `ES-T5-002` · `SPEAKER-UNIVERSE` | **mensal** |
| **SUPPLY** | **nada, e deve continuar nada** até existir evidência que torne a área relevante | — | — |

> **A resposta honesta à pergunta "por que abriria amanhã?" é: a maioria das áreas não
> abriria amanhã. Abriria toda semana.** Um produto que exige uso diário sem sinal diário
> acaba fabricando sinal. O casco já resolve isso melhor do que a pergunta: a home mostra
> **estado**, e estado pode ficar igual sem ficar velho.

---

# H · ACTION MAP

Derivado caso a caso, sem ordem fixa — como o briefing exige.

| item | quem age | o que pode fazer | o que **só** a ADAMA decide |
|---|---|---|---|
| **F.1 · vencimentos ES** | REGULATÓRIO → PORTFÓLIO → MD | listar os 36, cruzar com pares cultura×alvo, verificar renovação | se a renovação já está em curso; prioridade interna |
| **F.2 · flavescência IT** | TÉCNICO → MD → PORTFÓLIO → MARKETING | acompanhar o boletim semanal; confirmar resposta registrada; preparar material técnico para 2027 | se a região já é atendida; disponibilidade comercial |
| **F.3 · repilo ES** | MD → REGULATÓRIO → TÉCNICO | verificar renovação do NEPTUNE (15/08/2026); programar validação de campo em Sevilla/Córdoba | se a província já é atendida; se vale a assistência técnica |
| **F.4 · ativação FR** | MARKETING → MD | **avaliar** se o nível de comunicação pública é deliberado | a resposta — o sistema só faz a pergunta |
| **creators** | MARKETING | avaliar 2 `ACTIVATION_READY`; buscar os `MISSING_PROOFS` dos 4 `PROMISING` | contratar, orçar, aprovar campanha |

**Duas regras que a interface precisa carregar:**

1. **A área central é Market Development em toda a arquitetura** — no casco e no documento
   canônico. Ela **avalia e programa a investigação**; não executa.
2. **SUPPLY só aparece quando houver evidência que a torne relevante.** Hoje não há.
   Listá-la sempre, ainda que como `NÃO DETERMINADO`, convida ao preenchimento.
