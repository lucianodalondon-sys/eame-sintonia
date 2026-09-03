# Revisão final da Commercial Priority V1.1 — antes de integrar

> Revisão sobre `claude/opportunity-commercial-priority-v1` · base `fa41cc5`.
> **Não integrado ao portal. Casco não alterado. Interface não redesenhada.**
>
> As três hipóteses de trabalho foram aceitas e mantidas: caso **por região**,
> `OPPORTUNITY_STATE` e `COMMERCIAL_PRIORITY` **independentes**, catálogo e
> autorização como **universos separados** (junção por número de registro).

    VEREDITO: NOT_READY — dois defeitos medidos, ambos no vínculo da JANELA
    e na leitura de UMA oração corrida. Nenhum deles inventa oportunidade;
    os dois destroem oportunidade verdadeira.

---

## 1 · Os 4 SALES_READY, ficha a ficha

Todos os quatro têm **produto do catálogo comercial com rótulo ministerial no
par exato** — verificado registro a registro, não por nome.

### `OPP_75C37DED9160` · maçã × carpocapsa · **Veneto**

| | |
|---|---|
| `NEED_DIRECTION` | `POSITIVE_PRESSURE` |
| `NEED_EXCERPT` | «O boletim frutticolo do Veneto declara terminada a colheita das variedades do grupo Gala e reporta terceiro voo de *Cydia pomonella* terminado com **danos em aumento também em pomares de manejo integrado**.» |
| apoio · método | `IT-CAN-D9582B1FD6` · `CROP_FROM_SINGLE_CROP_DOCUMENT` · campo `WHAT_IT_IS` |
| produtos ADAMA no par | KLARTAN 20 EW · TAU AL 240 EW · **LAMDEX EXTRA** · **MAVRIK SMART** · KLARTAN SMART · FORZA |
| no catálogo comercial? | **SIM** — Lamdex® Extra (008259) e MAVRIK SMART (009800) |
| rótulo cobre o par exato? | **SIM** — `MELO × CARPOCAPSA`, «Cydia pomonella» / «carpocapsa» |
| geografia do fato | `['REGION_VENETO']` |
| geografia da autorização | `['GEO_ITALY']` |
| janela usada · `WINDOW_KIND` | `SIGNAL_DATE` (2026-08-26, 7 dias) · **nenhuma** (`None`) |
| `COMMERCIAL_PRIORITY` | `SALES_READY` |
| `OPPORTUNITY_STATE` | `OPPORTUNITY_CONFIRMED` |
| `BLOCKING_GATES` | **vazio** |
| famílias externas | 1 · `FIELD_SIGNAL` |

**1 manda agir?** Sim — «danni in aumento **anche in frutteti a gestione
integrata**»: o serviço declara que a solução em uso está falhando.
**2 problema atual?** Sim, terceiro voo com dano crescente.
**3 produto existe comercialmente?** Sim, dois.
**4 rótulo cobre o par?** Sim, literal.
**5 região se sustenta?** Sim — boletim regional que fala pela região.
**6 tempo real?** Sim — documento de 7 dias; **nenhuma data administrativa é
apresentada como janela**.
**7 apresentável internamente?** **SIM.**
**8 enviável a revendedor/RTV hoje?** **SIM** — `EXTERNAL_MATERIAL_READY = YES`.
Para material externo, citar **MAVRIK SMART**: a página de catálogo dele declara
`POMACEE`; a de Lamdex® Extra declara apenas `MAIS, POMODORO, VITE`.

### `OPP_9C600748BB1B` · milho × piralide · **Friuli-Venezia Giulia**

| | |
|---|---|
| `NEED_DIRECTION` | `POSITIVE_PRESSURE` |
| `NEED_EXCERPT` | «Limiar declarado: **tratamento insecticida justificado** quando se observarem posturas superiores a 3 por cada 100 plantas e/ou presença de larvas superior a 30-40% em pelo menos 50-100 espigas observadas.» |
| apoio · método | `IT-PHEN-048` (ERSA FVG) · `PAIR_IN_DOCUMENT_TITLE` · «Bollettino… — **Piralide del mais**» |
| produtos ADAMA no par | **LAMDEX EXTRA** · FORZA · NINJA |
| no catálogo comercial? | **SIM** — Lamdex® Extra (008259), catálogo declara `MAIS` |
| rótulo cobre o par exato? | **SIM** — `MAIS × PIRALIDE` e `MAIS_DOLCE × PIRALIDE` |
| geografia do fato | `['REGION_FRIULI_VENEZIA_GIULIA']` |
| geografia da autorização | `['GEO_ITALY']` |
| janela usada · `WINDOW_KIND` | `SIGNAL_DATE` (2026-08-12, 21 dias) · **nenhuma** |
| `COMMERCIAL_PRIORITY` · `OPPORTUNITY_STATE` | `SALES_READY` · `OPPORTUNITY_CONFIRMED` |
| `BLOCKING_GATES` | **vazio** |
| famílias externas | 1 · `FIELD_SIGNAL` |

**1** Sim, com limiar numérico. **2** Sim, 3ª geração em voo. **3** Sim.
**4** Sim, literal. **5** Sim — ERSA fala pela região (`REGION_REPRESENTS=true`).
**6** Sim, 21 dias, sem data administrativa. **7 SIM.** **8 SIM**
(`EXTERNAL_MATERIAL_READY = YES`). **Ressalva a escrever no material:** o próprio
boletim restringe o dano às **semeaduras tardias** — as espigas em maturação
avançada não devem sofrer. O material externo tem de levar essa restrição.

### `OPP_1A9962A3A2BC` · videira × botrite · **Emilia-Romagna**

| | |
|---|---|
| `NEED_DIRECTION` | `POSITIVE_PRESSURE` |
| `NEED_EXCERPT` | «Vite/botrite: **intervir em pré-colheita** com Fenhexamid (max 2) ou alternativas biológicas.» |
| apoio · método | `IT-PHEN-001` · `PAIR_IN_SAME_CLAUSE` · `INTERVENTION_GUIDANCE` |
| produtos ADAMA no par | **BANJO** · EMBRACE · AGHARTA |
| no catálogo comercial? | **SIM** — BANJO (013905), catálogo declara `POMACEE, VITE` |
| rótulo cobre o par exato? | **SIM** — `VITE × BOTRITE`, «Botrytis cinerea» |
| geografia do fato | `['REGION_EMILIA_ROMAGNA', 'REGION_LOMBARDIA', 'REGION_PIEMONTE', 'REGION_VENETO']` ⚠️ |
| geografia da autorização | `['GEO_ITALY']` |
| janela usada · `WINDOW_KIND` | `PREPARATION_WINDOW` → 2027-05-31 · **`PREPARATION`** ⚠️ |
| `COMMERCIAL_PRIORITY` · `OPPORTUNITY_STATE` | `SALES_READY` · **`OPPORTUNITY_CANDIDATE`** |
| `BLOCKING_GATES` | `A_GEOGRAFIA` · `F_PROCEDENCIA (IT-WIN-001, IT-WIN-002)` |
| famílias externas | 2 · `FIELD_SIGNAL`, `CROP_WINDOW` ⚠️ |

**1** Sim. **2** Sim. **3** Sim. **4** Sim. **5** A região da **afirmação** se
sustenta (`CLAIM_GEOGRAPHY_HOLDS = true`), mas `FIELD_GEOGRAPHY` traz quatro
regiões — e **não é o sinal de campo que as traz**. **6 NÃO:** a janela exibida
é data de ato. **7 SIM**, internamente. **8 NÃO** —
`EXTERNAL_MATERIAL_READY = VALIDATION_REQUIRED`.

### `OPP_0C8669B0E849` · videira × tignoletta · **Emilia-Romagna**

Anatomia idêntica à anterior. `NEED_EXCERPT`: «Vite/tignoletta: monitorar
vinhedos de colheita tardia e, **ao ultrapassar 5% de cachos infestados,
intervir** com Bacillus t., Emamectina (max 2) ou Spinosad (max 3).»
Produto de catálogo: **Lamdex® Extra** (`VITE × TIGNOLE`, catálogo declara
`VITE`). Mesmos dois portões abertos, mesma janela administrativa.
**7 SIM · 8 NÃO** (`VALIDATION_REQUIRED`).

---

## 2 · A regra de segurança para uso externo

Implementada em `v21_comercial.externo()` e gravada em cada oportunidade.

```
EXTERNAL_MATERIAL_READY ∈ { YES · VALIDATION_REQUIRED · NO }
```

    VENDER É UMA DECISÃO INTERNA. ENVIAR É UMA AFIRMAÇÃO PÚBLICA.
    A SEGUNDA PRECISA SOBREVIVER A QUEM A LER SEM NOS CONHECER.

`NO` se o caso não é `SALES_READY`. Sendo `SALES_READY`, **qualquer** um destes
o rebaixa a `VALIDATION_REQUIRED`:

| bloqueio | o que impede |
|---|---|
| `EVIDENCE_GATE_OPEN` | há portão sobre a mesma afirmação que o material levaria |
| `RED_TEAM_FINDING` | o red team registrou extrapolação no caso |
| `WINDOW_IS_ADMINISTRATIVE` | a janela exibida é data de ato, não de aplicação |
| `NO_SOURCE_SENTENCE` | não há frase da fonte sustentando a necessidade |
| `CATALOG_DOES_NOT_DECLARE_CROP` | o rótulo cobre o par, mas a **página de catálogo** do produto não declara a cultura |

O último saiu desta revisão: **Lamdex® Extra tem rótulo ministerial em
`MELO × CARPOCAPSA` e a página de catálogo dele declara apenas `MAIS, POMODORO,
VITE`.** O rótulo autoriza; o catálogo público não anuncia. Internamente as duas
coisas convivem — em material que sai de casa, a segunda é a que o leitor confere.

    O RÓTULO DIZ O QUE É PERMITIDO. O CATÁLOGO DIZ O QUE A EMPRESA OFERECE.
    MATERIAL EXTERNO NÃO PODE PROMETER MAIS DO QUE O CATÁLOGO ANUNCIA.

**A independência não foi escondida:** os dois casos de Emilia-Romagna
continuam `SALES_READY` na coluna interna e saem `VALIDATION_REQUIRED` na
externa. Seis provas novas (T13–T18) fixam isso, inclusive
`test_T14` que verifica que a coluna interna **não** é rebaixada pela externa.

**Resultado nas 43:** `YES` **2** · `VALIDATION_REQUIRED` **2** · `NO` **39**.

---

## 3 · Os dois SALES_READY com portão aberto — o diagnóstico

**Resposta: existe DEFEITO NO VÍNCULO DA JANELA.** Não é um portão irrelevante,
e o portão está certo em disparar.

Os sete registros de `CROP-WINDOWS` são triplas bem declaradas
(cultura × alvo × região):

| | cultura | alvo | região | procedência |
|---|---|---|---|---|
| `IT-WIN-001` | videira | `ISSUE_SCAPHOIDEUS` | Veneto | **UNRECOVERABLE** |
| `IT-WIN-002` | videira | `ISSUE_SCAPHOIDEUS` | Lombardia | **UNRECOVERABLE** |
| `IT-WIN-003` | videira | `ISSUE_SCAPHOIDEUS` | Piemonte | RECOVERED |
| `IT-WIN-005` | videira | `ISSUE_SCAPHOIDEUS` | **Emilia-Romagna** | UNRECOVERABLE |

Mas o motor as indexa **só por cultura**:

```python
win_crop = _ix(cs['CROP-WINDOWS'], 'CROP_IDS')      # linha 389
...
sin[:8] + win_crop.get(crop, [])[:3] + rot[:6]      # linha 609
```

Um caso de **videira × botrite** em **Emilia-Romagna** recebe as três primeiras
janelas de videira — que são de **Scaphoideus**, e de **Veneto, Lombardia e
Piemonte**. A janela da própria Emilia-Romagna (`IT-WIN-005`) fica de fora.

    É O MESMO DEFEITO DO PAR CARTESIANO, NOUTRO LUGAR:
    JUNTAR POR CULTURA E JOGAR FORA O ALVO E A REGIÃO QUE O REGISTRO DECLARA.

**Quatro consequências medidas, todas do mesmo vínculo:**

1. **`A_GEOGRAFIA`** — a janela injeta Veneto/Lombardia/Piemonte no
   `FIELD_GEOGRAPHY` de uma afirmação de Emilia-Romagna. Geografia promovida por
   um registro que não pertence ao caso.
2. **`F_PROCEDENCIA`** — `IT-WIN-001/002` têm `SOURCE_IDS: ['SRC_NAO_DECLARADA']`
   e `PROVENANCE_STATE: UNRECOVERABLE`.
3. **`WINDOW_KIND = PREPARATION`** — o `2027-05-31` desses dois casos vem do
   `PREPARATION_WINDOW` da janela errada («até 2027-05-31, quando historicamente
   sai o ato»).
4. **Família externa inflada** — `CROP_WINDOW` entra como segunda família em
   casos que têm uma só. Parte do salto «2 famílias: 7 → 16» é este artefato.
   Também infla `ACTIONABILITY` (`2 if win_crop.get(crop) else 1`).

**O portão aberto impede material externo? SIM** — e corretamente: o material
citaria uma janela que não é do caso, apoiada em registro sem origem
recuperável. **Não fechei o portão.** A correção é do vínculo, não do portão:
indexar as janelas por `(cultura, alvo)` e exigir que a região contenha a
afirmação — a mesma regra já aplicada ao par observado.

---

## 4 · NEED_DIRECTION — amostra das oito classes

| classe | pinos | trecho real e por que a classificação está certa |
|---|---:|---|
| `POSITIVE_PRESSURE` | 6 | «Vite/botrite: **intervir** em pré-colheita com Fenhexamid» · «para botrite, na fase de maior suscetibilidade, **possível intervir** com antibotríticos» — o texto manda agir |
| `MONITOR` | 2 | «Vite/flavescenza dorata: **inspecionar** os vinhedos e arrancar as plantas sintomáticas» — manda observar e erradicar, não tratar |
| `NEUTRAL_MENTION` | 28 | «Vite/botrite: **em castas normalmente atingidas ou havendo rachadura da baga**, Fenexamid…» — condicional sem gatilho corrente |
| `NO_ACTION_RECOMMENDED` | 2 | «Peronospora: «In generale **non necessari interventi**.»» |
| `ACTION_SUSPENDED` | 4 | «tratamentos de oidio **podem ser suspensos** nas variedades próximas da maturação» |
| `WINDOW_CONCLUDED` | 5 | «Vite/peronospora: **o cacho já não é suscetível**» · «esgotada a receptividade do cacho» |
| `TREATMENT_PROHIBITED` | 2 | «durante a floração **VIGORA A PROIBIÇÃO** de intervenção fitoiátrica com inseticidas, para tutela das abelhas» |
| `UNKNOWN` | 0 | nenhum pino — os 26 casos `UNKNOWN` são arquétipos **sem alvo** (O2/O4/O5/O6), que não formam par de campo |

**O falso positivo de «terzo volo terminato» não ocorre.** Prova `T6b`: os
padrões de conclusão exigem *defesa*, *tratamento* ou *armadilha* na mesma
expressão. «Terceiro voo de *Cydia pomonella* terminado, com danos em aumento»
sai `POSITIVE_PRESSURE`.

### ⚠️ Mas há OUTRO falso positivo, da mesma família — e este ocorre

`IT-PHEN-040` (Siena) e `IT-PHEN-041` (Firenze) publicam **o mesmo texto** — o
próprio registro de Firenze diz «Mesmo texto de seções que Siena nesta semana».
Siena usa **ponto e vírgula**; Firenze usa **vírgula**.

```
IT-PHEN-040  «…; para botrite, na fase de maior suscetibilidade, possível
              intervir com antibotríticos…;»          → BOTRYTIS = POSITIVE_PRESSURE ✅

IT-PHEN-041  «suspensão da defesa antiperonosporica…, suspensão de oidio…,
              fim da defesa de black rot, janela de maior suscetibilidade a
              botrite, fim da defesa de Scaphoideus titanus.»
                                                       → uma oração só, três alvos,
                                                         todos ACTION_SUSPENDED ❌
```

O segmentador quebra em `.` e `;`, não em vírgula. A oração corrida de Firenze
casa `suspensão` primeiro e **aplica essa direção a `SCAPHOIDEUS`, `BOTRYTIS` e
`POWDERY_MILDEW` juntos** — quando sobre botrite ela diz o contrário: *janela de
maior suscetibilidade*.

**Efeito:** `videira × botrite · Toscana` fica `ACTION_SUSPENDED` → `TO_VALIDATE`.
A regra «a que manda parar vence» faz a leitura falsa **suprimir** a verdadeira
da região vizinha.

    UMA ORAÇÃO QUE NOMEIA TRÊS ALVOS E UM VERBO NÃO DIZ A QUAL DELES O VERBO SE
    APLICA. ATRIBUIR A TODOS É ADIVINHAR — E AQUI ADIVINHOU ERRADO.

O erro é **conservador na direção certa** (fecha uma porta, não abre uma falsa),
mas destrói uma oportunidade verdadeira. **Não corrigi**, porque a correção
promove um caso a `SALES_READY` e essa decisão é sua.

---

## 5 · Os 12 pares observados — nenhum cartesiano disfarçado

| cultura | alvo | método do pino que decide | pinos |
|---|---|---|---:|
| maçã | carpocapsa | `CROP_FROM_SINGLE_CROP_DOCUMENT` | 1 |
| videira | botrite | `CROP_FROM_SINGLE_CROP_DOCUMENT` | 11 |
| videira | peronospora | `PAIR_IN_SAME_CLAUSE` | 11 |
| videira | flavescenza | `PAIR_IN_SAME_CLAUSE` | 7 |
| videira | tignoletta | `PAIR_IN_SAME_CLAUSE` | 2 |
| videira | oídio | `CROP_FROM_SINGLE_CROP_DOCUMENT` | 5 |
| videira | *Scaphoideus* | `CROP_FROM_SINGLE_CROP_DOCUMENT` | 5 |
| milho | piralide | `PAIR_IN_DOCUMENT_TITLE` | 2 |
| milho | diabrótica | `PAIR_IN_DOCUMENT_TITLE` | 1 |
| oliveira | cercospora | `CROP_FROM_SINGLE_CROP_DOCUMENT` | 2 |
| oliveira | mosca | `PAIR_IN_SAME_CLAUSE` | 1 |
| tomate | peronospora | `PAIR_IN_SAME_CLAUSE` | 1 |

Sobre os **49 pinos**: `PAIR_IN_SAME_CLAUSE` 20 · `CROP_FROM_SINGLE_CROP_DOCUMENT`
20 · `CROP_FROM_PRECEDING_CLAUSE` 6 · `PAIR_IN_DOCUMENT_TITLE` 3.

**Duas leis atravessam os quatro métodos, e são o que impede o cartesiano:**
o **alvo tem de estar escrito no texto** (nunca vem do cabeçalho `ISSUE_IDS`), e
a **cultura tem de estar declarada em `CROP_IDS`** (nunca é adivinhada na prosa).
Provas `T10`, `T10b`, `T10c`.

**Falsos pares removidos** — dos 31 cartesianos do V1 sobraram 12; entre os 22
descartados: *beterraba × ticchiolatura*, *soja × ticchiolatura*, *trigo ×
ticchiolatura*, *arroz × ticchiolatura*, *milho × ticchiolatura*, *batata ×
ticchiolatura*, *kiwi × ticchiolatura*, *videira × mosca-da-oliveira*. A sarna é
doença de pomáceas; nenhuma frase de nenhum documento a atribuiu a essas
culturas.

**Nota de cobertura, não de defeito:** dos **483** termos de praga citados nos 86
boletins, **296 não têm `ISSUE_ID`** (*Colpo di fuoco*, *Maculatura bruna*,
*Glomerella*, *Psilla*, *Monilia*, *Mal dell'esca*…). É o teto medido de `O1`, e
é vocabulário — não modelagem.

---

## 6 · DURUM WHEAT — mantido `HONEST_UNKNOWN`

Nada foi mapeado. `frumento` **não** virou `frumento duro`.

**A próxima coleta, descrita objetivamente:** ler a **tabela de usos** («Colture
e avversità» / «Dosi e modalità d'impiego») das etiquetas ministeriais dos 14
registros abaixo, e extrair os pares `CROP_ON_LABEL × TARGET_ON_LABEL` como já
se faz para os outros 176. Cada URL já está no pacote, em
`PRODUCTS-REGULATORY.json`, campo `LABEL_URL`.

| registro | produto | catálogo | substâncias | etiqueta |
|---|---|---|---|---|
| 008929 | TOPIK 240 EC | — | clodinafop + cloquintocet | `EtichettaServlet?id=40823` |
| 010063 | TOPIK 80 EC | — | clodinafop + cloquintocet | `id=39822` |
| 013332 | VIP | — | clodinafop + cloquintocet | `id=40827` |
| 013736 | TRACE | — | clodinafop + cloquintocet | `id=39820` |
| 013807 | RAVENAS | — | clodinafop + cloquintocet | `id=40826` |
| 014693 | VIP 80 EC | — | clodinafop + cloquintocet | `id=39824` |
| 014694 | CELIO 80 EC | — | clodinafop + cloquintocet | `id=39823` |
| 014728 | CELIO | — | clodinafop + cloquintocet | `id=40824` |
| 015316 | HAWK | — | clodinafop + cloquintocet | `id=40825` |
| 015847 | MAKURI | — | clodinafop + cloquintocet | `id=39821` |
| 016152 | **SEEDRON** | **SIM** | fludioxonil + tebuconazol | `id=39273` |
| 016218 | DICURAN PLUS | — | clorotolurón + diflufenican | `id=36530` |
| 018176 | **EDAPTIS** | **SIM** | mefenpir + mesosulfurão | `id=45957` |
| 018644 | MEZAYO | — | mesosulfurão + pinoxaden | `id=45958` |

Base: `https://www.fitosanitari.salute.gov.it/fitosanitariws_new/`

**A pergunta que a coleta responde:** para cada um destes 14, a tabela de usos
escreve `frumento duro` / `grano duro`, ou escreve apenas `frumento`? Se
escrever apenas `frumento`, o `HONEST_UNKNOWN` **permanece** — e passa a ser um
`NÃO SEI` do documento, não nosso. **Dois deles estão no catálogo comercial**
(SEEDRON e EDAPTIS): são os que mais valem a leitura.

---

## 7 · As 9 ocorrências da suíte, classificadas

Suíte: **700 testes** · **6 falhas** · **2 erros** · 14 skips.
Base do commit de auditoria: 13 falhas · 2 erros.

| # | ocorrência | classe | toca a camada comercial? |
|---|---|---|---|
| 1 | `test_adama_es_import_rules` `setUpClass` | **ENVIRONMENT** — `git show origin/claude/adama-es-local-browser:…` sai 128: o branch não existe neste clone raso | não |
| 2 | `test_comunicacao` ImportError | **PRE_EXISTING** — auto-verificação do módulo falha («nenhuma casa nasce autorizada») | não |
| 3 | `test_a_unica_migration_nova_tem_incompatibilidade_provada` | **PRE_EXISTING** — migrations 019/020 do Supabase ES sem defeito medido declarado | não |
| 4–6 | `test_source_e_fact_location_quando_declarados` ×3 | **PRE_EXISTING** — `COMPETITOR-PUBLIC-COMM` ×2, `PIEMONTE-FD` ×1 | não |
| 7 | `test_toda_amostra_declara_origem` | **PRE_EXISTING** — 24 amostras antigas (IT-ARPAV, IT-LASTMILE, IT-V2, IT-ROTULOS…) | não |
| 8 | `test_toda_amostra_declara_data_de_captura` | **PRE_EXISTING** — mesmo conjunto | não |
| 9 | `test_a_contagem_de_testes_do_handoff_bate` | **CORRIGIDO nesta revisão** | era meu |

**Duas eram minhas, e foram corrigidas — não desculpadas:**

- `data/samples/AUDITORIA-SOMBRA/*.json` (os dois arquivos que eu mesmo gerei)
  não declaravam `SOURCE` nem `CAPTURED_AT`. O contrato de `data/samples/` vale
  para o que eu produzo, ou não é contrato. Os geradores passaram a emitir os
  dois campos.
- `PROMPT-PARA-NOVA-CONTA-CLAUDE.md` publicava «Esperado: 649 testes» e
  `TEST_COUNT_CURRENT = 649`. A suíte cresceu **por causa das minhas 42 provas**.
  Atualizado para 705, que é o que o ledger mede. E os dois arquivos de
  handoff deixaram de prometer «0 falhas, 0 erros»: publicam agora as 6
  falhas e os 2 erros reais, e apontam para esta classificação. Um handoff
  que promete verde e entrega vermelho ensina a nova conta a desconfiar do
  próprio contador.

**Nenhuma das 8 restantes toca** commercial priority, crop × target, geografia
do motor, catálogo, janela ou need direction.

**As provas próprias da camada: 42 de 42 verdes.**

---

## 8 · Veredito

```
VEREDITO = NOT_READY

SALES_READY                       = 4
SALES_READY INTERNAMENTE DEFENSÁVEIS = 4
EXTERNAL_MATERIAL_READY           = 2   (OPP_75C37DED9160 · OPP_9C600748BB1B)
VALIDATION_REQUIRED               = 2   (OPP_1A9962A3A2BC · OPP_0C8669B0E849)

CASOS REGIONAIS   = PASS
NEED_DIRECTION    = FAIL   (oração corrida atribui uma direção a vários alvos)
CROP_TARGET       = PASS
CATÁLOGO          = PASS
JANELA            = FAIL   (vínculo por cultura, ignorando alvo e região)

9 FALHAS/ERROS CLASSIFICADOS = YES
DURUM_WHEAT = COLLECTION_REQUIRED
```

**BLOQUEIOS**

1. **`JANELA` — vínculo indexado só por cultura.** `win_crop` descarta o alvo e
   a região que o próprio registro declara. Causa os dois portões abertos, a
   janela administrativa, a família externa inflada e o `ACTIONABILITY` inflado
   em todos os casos de videira. **Correção:** indexar por `(cultura, alvo)` com
   contenção de região — a mesma regra do par observado.
2. **`NEED_DIRECTION` — oração corrida.** Quando uma oração nomeia mais de um
   alvo e uma só palavra de direção, a direção é aplicada a todos. Reproduzido
   em `IT-PHEN-041`, que publica o mesmo texto de `IT-PHEN-040` com vírgulas em
   vez de ponto e vírgula. Suprime `videira × botrite · Toscana`.
   **Correção sugerida:** não atribuir direção a partir de oração que nomeie
   mais de um alvo — deixar `NEUTRAL_MENTION` e registrar a ambiguidade.

Os dois são do mesmo tipo: **juntar por um eixo e jogar fora os outros**. Nenhum
inventa oportunidade; os dois destroem oportunidade verdadeira. Por isso
`NOT_READY` — e por isso o número correto de `SALES_READY` depois de corrigidos
é provavelmente **maior** que 4, não menor.

**O que já está pronto e não precisa voltar:** a régua por região, a separação
das três geografias, a separação catálogo × registro, a leitura de direção do
texto, e a regra de saída externa com as duas colunas independentes.
