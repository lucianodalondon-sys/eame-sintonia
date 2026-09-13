# C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1 — RELATÓRIO

**Data:** 2026-09-13 · **Veredito:** `CANARY = BLOCKED`
**Porquê:** `WAITING_ROOM_PERSISTENCE_NOT_PROVEN` (§7 da missão)

> **NENHUMA AQUISIÇÃO REAL FOI EXECUTADA.**
> Zero rede de aquisição · zero escrita em LIVE · zero dólar · zero linha de
> código funcional alterada.

---

## 1 · EM PORTUGUÊS FÁCIL

**1. A máquina estava pronta para rodar de verdade?**
Não. Falhou o portão bloqueante da missão — o §7, o da Sala de Espera — e ele
vem **antes** de qualquer aquisição. Por isso nada foi coletado.

**2. A VPN do runner estava realmente saindo pela Itália?**
Não foi medido, e não podia ser. O egresso italiano não vive nesta sessão: vive
na máquina Windows self-hosted (`eame-sintonia-local` / `-local-2`). E não
existe, no HEAD funcional, nenhuma fase canónica que meça `EGRESS_COUNTRY_CODE`
sozinha — o único medidor de egresso está **dentro** de uma rota de aquisição
(`coleta/instagram_janela.py`, via `ipinfo.io`). Medir o egresso exigiria ou
coletar, ou escrever código novo. As duas coisas estão proibidas antes do §7.

**3. O que coletamos de verdade?** Nada.
**4. Quantos itens?** 0.
**5. Quantos viraram RAW?** 0.
**6. Quantos chegaram a READY/Sala?** 0.
**7. Quantos foram recusados/UNKNOWN/NOT_APPLICABLE/ERRO?** 0 — não houve item.
**8. Cada READY consegue voltar ao arquivo bruto correto?** Não se aplica: não
houve READY. A cadeia inversa não foi exercida contra material real novo.
**9. Houve custo?** Não. `REAL_PAID_USD = 0`.

**10. A Sala permaneceu depois que o runner terminou?**
**Não — e é exatamente este o bloqueio.** A Sala de Espera escreve em
`data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`, no disco do runner. Esse
caminho **nunca** é devolvido ao repositório, **nunca** sobe como artefato, e
**não tem dono em banco**. O próximo `actions/checkout` limpa o que não está
versionado. Coletar material real agora seria coletá-lo para uma sala que
desaparece.

**11. Podemos aumentar para um lote de 20–50?**
Não. `READY_FOR_SMALL_BATCH = NO`.

---

## 2 · A MEDIÇÃO QUE BLOQUEOU — §7

A pergunta da missão é literal:

> quando o runner terminar, onde o READY real permanece de forma canónica e
> auditável?

### 2.1 · Onde a Sala escreve

```
admissao/sala_de_espera.py:63
    MORADA = <RAIZ>/data/samples/PRONTO-PARA-INTELIGENCIA

orquestrador/orquestrador.py:573        recibo = espera.pousar(run_id, aceites)
coleta/rota_forward_documento.py:381    recibo = espera.pousar(run_id, [pronta])
```

Os dois caminhos canónicos — control plane e rota forward — pousam no **mesmo
ficheiro local**. Não há segunda escrita, e isso está certo: o dono é um só.

### 2.2 · Quem devolve esse caminho ao mundo — ninguém

| mecanismo | cobre a Sala? | prova |
|---|---|---|
| commit do `sintonia-scrap.yml` | **NÃO** | `.github/workflows/sintonia-scrap.yml:499-502` só faz `git add` de `INSTAGRAM-*`, `YOUTUBE-*`, `SCRAP-YOUTUBE` |
| guarda de namespace do mesmo passo | **RECUSA** o resto | `:507-508` — `grep -qvE '^data/samples/(INSTAGRAM\|YOUTUBE\|SCRAP)-'` → `NAMESPACE_VIOLADO=YES`, `exit 1` |
| commit do `scrap-social.yml` | **NÃO** | `:452-455` — três ficheiros nomeados em `data/samples/SOCIAL-IT/` |
| `upload-artifact` | **NÃO** | só `scrap-social.yml:376` (RAW do piloto YouTube) e `scrap-evidencia.yml:93` |
| dono em PostgreSQL | **NÃO EXISTE** | `ADR-SALA-DE-ESPERA-V1.md` §1: «**Não** se cria tabela para READY (…) **Não** se persiste a decisão de admissão em PostgreSQL» |
| `.gitignore` | não ignora | `git check-ignore` do caminho devolve vazio — o caminho *poderia* ser commitado; ninguém o commita |

E a prova mais simples de todas, sobre **toda** a história do repositório:

```
$ git log --all --oneline -- 'data/samples/PRONTO-PARA-INTELIGENCIA'
(vazio)
```

Nunca, em nenhum ramo, um ficheiro da Sala de Espera foi versionado. A pasta
não existe na árvore — só no disco de quem correr o fluxo.

### 2.3 · O veredito

```
WAITING_ROOM_PERSISTENCE_MECHANISM = FILESYSTEM DO WORKSPACE DO RUNNER
                                     NÃO COMMITADO · NÃO ARTEFATO · SEM DONO EM BANCO
WAITING_ROOM_PERSISTENCE_PROVEN    = NO
VEREDITO                           = NOT_PERSISTENT
```

> **MODULE EXISTS ≠ FILE WRITTEN ON RUNNER ≠ PERSISTED AFTER RUN.**
>
> A `ADR-SALA-DE-ESPERA-V1` escolheu o **meio** (filesystem) e nunca respondeu
> à pergunta da **sobrevivência**. Não é contradição da ADR: é uma pergunta que
> ela não fez.

Conforme §7 da missão: `HARD STOP`. Nenhuma aquisição.
Conforme §20: **não se conserta em LIVE nesta missão.**

---

## 3 · O QUE FOI MEDIDO ANTES DO STOP

### 3.1 · Git (§0)

```
CURRENT_BRANCH            claude/great-ride-2n4gbh
CURRENT_HEAD              f437ff1140fa97484ca9695b341fbe9ca0a9f050
FUNCTIONAL_BRANCH         claude/raw-observation-identity-3jbwco
FUNCTIONAL_HEAD           f888776dffd789053fbaf39fc9fe630c74dde3ef
REMOTE_FUNCTIONAL_HEAD    f888776dffd789053fbaf39fc9fe630c74dde3ef
REFERENCE_HEAD (missão)   f888776dffd789053fbaf39fc9fe630c74dde3ef
FUNCTIONAL_HEAD_DRIFT_AT_START   NO
WORKTREE_STATUS           limpo
KNOW_HOW_BRANCH           claude/sintonia-eame-know-how-v1
KNOW_HOW_HEAD             7b5e50cf807f728524007f92660d73a3d2e0de1f
DEFAULT_BRANCH (main)     f437ff1140fa97484ca9695b341fbe9ca0a9f050
```

A leitura de autoridades foi feita numa **worktree destacada** em
`f888776d`, para que o que se leu fosse byte-equivalente ao HEAD funcional.

### 3.2 · Runner e egresso (§4)

```
RUNNERS SELF-HOSTED DECLARADOS   [self-hosted, Windows, X64, eame-sintonia-local]
                                 [self-hosted, Windows, X64, eame-sintonia-local-2]
RUNNER_NAME                      NOT_MEASURED
EGRESS_COUNTRY_CODE_BEFORE       NOT_MEASURED
EGRESS_COUNTRY_CODE_AFTER        NOT_MEASURED
```

Três factos que sustentam o `NOT_MEASURED`, e nenhum é suposição:

1. **O runner da nuvem não serve.** `docs/biblia/CENSO-DA-INFRAESTRUTURA.md:39`
   e `docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md:77` —
   «o runner sai por datacenter dos EUA/Europa, não pela VPN italiana».
2. **O estado dos runners não é legível daqui.**
   `GET /repos/.../actions/runners` → `HTTP 403` («Access to this GitHub Actions
   path is not permitted through this proxy»).
3. **Não há preflight canónico de egresso.** O único medidor vive dentro de uma
   rota de aquisição (`coleta/instagram_janela.py:442`, `ipinfo.io`). Criar um
   preflight separado seria `FUNCTIONAL_CODE_DIFF != 0`, proibido pelo §20.

> **ISTO É UM SEGUNDO ACHADO, E NÃO UM DETALHE DE EXECUÇÃO:**
> a missão exige `EGRESS_COUNTRY_CODE = IT` **antes** da primeira aquisição, e
> a máquina atual não sabe responder a isso sem já estar a adquirir.
> **UM PREFLIGHT QUE SÓ CORRE DEPOIS DE COMEÇAR NÃO É UM PREFLIGHT.**

### 3.3 · Banco LIVE (§5, §6)

```
LIVE_SCHEMA_COMPATIBLE      NOT_MEASURED
COLLECTION_RUNS_BEFORE      NOT_MEASURED
RAW_ASSETS_BEFORE           NOT_MEASURED
STORAGE_OBJECTS_BEFORE      NOT_MEASURED
DERIVED_ARTIFACTS_BEFORE    NOT_MEASURED
STRUCTURED_OBJECTS_BEFORE   NOT_MEASURED
WAITING_ROOM_ITEMS_BEFORE   0 (o caminho não existe em nenhum ramo)
```

`SUPABASE_DB_URL` é secret do GitHub e não está nesta sessão (verificado: nenhuma
variável `SUPABASE*`/`PG*`/`DATABASE_URL` no ambiente). O preflight de LIVE só
corre onde o secret existe — ou seja, dentro do mesmo runner que o §7 bloqueia.
**Não se mediu, e por isso não se declara `YES`.**

### 3.4 · Custo (§8, §17)

```
PAID_ROUTE_REQUIRED   NO
APIFY_REQUIRED        NO
PAID_USD_PLANNED      0
REAL_PAID_USD         0
TOTAL_NETWORK_ITEMS   0
```

### 3.5 · Contrato READY (§18)

```
READY_FIELDS = 12  ✅
```
`admissao/admissao.py:600-613` — `ESTADO`, `ITEM_ID`, `RAW_OBSERVATION_ID`,
`UNIVERSO`, `TEXTO`, `SOURCE_ID`, `SOURCE_LOCATION`, `FACT_LOCATION`,
`FACT_TIME`, `CAPTURED_AT`, `CORRIDA`, `ADMITIDO_POR`.

⚠️ **Deriva documental medida, não corrigida nesta missão:**
`docs/decisoes/ADR-SALA-DE-ESPERA-V1.md` §3 e o know-how `§76.1` ainda dizem
«os 11 campos da COL-LAW-043». O 12.º (`RAW_OBSERVATION_ID`) entrou em
`C-READY-LINEAGE-BEFORE-SCALE-V1` e a ADR não acompanhou. O código está certo;
os dois textos estão um passo atrás.

---

## 4 · OS CANÁRIOS QUE ESTAVAM PRONTOS, E QUE NÃO CORRERAM

Foram escolhidos **antes** do stop, e ficam registados para a missão que
desbloquear o §7 — nenhum deles foi executado.

### 4.1 · Social — o candidato mais maduro

```
SOCIAL_ROUTE      sintonia-scrap.yml · fase `canario-bluesky`
CAMINHO           workflow → orquestrador/orquestrador.py "colete concorrentes"
                          → --filtro fase/pais=IT/fonte/handle
RUNNER            self-hosted Windows (o do egresso italiano)
CUSTO             US$ 0,00 — sem credencial, sem navegador autenticado, sem provider
SOURCE_ID         vem do disparo (`--filtro fonte`), NUNCA do handle
                  (`sintonia-scrap.yml`: «HANDLE NÃO É SOURCE_ID»)
SOCIAL_CANARY     NOT_RUN
```

### 4.2 · Documental

```
DOCUMENT_ROUTE    coleta/rota_forward_documento.py
DOCUMENT_CANARY   NOT_RUN
```

`NOT_RUN` **não é** `PASS`. Nenhum dos dois foi tentado.

---

## 5 · ENTREGA FORMAL (§26)

```
FUNCTIONAL_HEAD                  f888776dffd789053fbaf39fc9fe630c74dde3ef
RUNNER_NAME                      NOT_MEASURED
EGRESS_COUNTRY_CODE_BEFORE       NOT_MEASURED
EGRESS_COUNTRY_CODE_AFTER        NOT_MEASURED

LIVE_SCHEMA_COMPATIBLE           NOT_MEASURED

WAITING_ROOM_PERSISTENCE_PROVEN  NO
WAITING_ROOM_PERSISTENCE_MECHANISM
    FILESYSTEM DO WORKSPACE DO RUNNER · NÃO COMMITADO · NÃO ARTEFATO ·
    SEM DONO EM BANCO → NOT_PERSISTENT

DOCUMENT_SOURCE_ID               NOT_SELECTED (bloqueado antes da escolha final)
DOCUMENT_RUN_ID                  NONE
DOCUMENT_CANARY                  NOT_RUN
DOCUMENT_RAW                     0
DOCUMENT_READY                   0

SOCIAL_SOURCE_ID                 NOT_SELECTED
SOCIAL_ROUTE                     sintonia-scrap.yml · canario-bluesky (candidato)
SOCIAL_RUN_ID                    NONE
SOCIAL_CANARY                    NOT_RUN
SOCIAL_RAW                       0
SOCIAL_READY                     0

NEW_RUNS                         0
NEW_RAW                          0
NEW_STORAGE                      0
NEW_DERIVED                      0
NEW_STRUCTURED                   0
NEW_READY                        0

REUSED                           0
REJECTED                         0
UNKNOWN                          0
NOT_APPLICABLE                   0
ERRORS                           0

READY_TO_RAW                     NOT_RUN
RAW_TO_STORAGE                   NOT_RUN
READY_TO_STORAGE                 NOT_RUN

READY_WRONG_RAW_MATCHES          0 (não houve READY)
READY_AMBIGUOUS_RAW_MATCHES      0 (não houve READY)

SOURCE_ID_FABRICATION            0
DOCUMENT_ID_FABRICATION          0
RAW_OBSERVATION_ID_FABRICATION   0

REAL_PAID_USD                    0
TOTAL_NETWORK_ITEMS              0

FUNCTIONAL_CODE_DIFF             0

RETRY_REAL                       NOT_RUN
CANARY_SCOPE_BREACH              NO
SYSTEM_MAP_RUNTIME_DELTA         NAO (não houve runtime — nada a comparar)

ITALIA_FIRST_REAL_CANARY         BLOCKED
READY_FOR_SMALL_BATCH            NO

KNOW_HOW_DELTA                   SIM — ver §6
```

---

## 6 · KNOW-HOW — O DELTA DURÁVEL (§23)

Este delta **não foi escrito no know-how canónico** por esta sessão: o ramo
`claude/sintonia-eame-know-how-v1` não é o ramo designado desta aba, e esta
missão não cria um segundo know-how. Fica aqui, pronto a ser anexado **como
secção nova** ao ficheiro canónico, sem alterar nada do que já lá está.

### O QUE mudou
A escolha da morada da Sala de Espera (`§76`, `ADR-SALA-DE-ESPERA-V1`) foi
tomada, está certa no seu próprio termo — e **nunca respondeu à pergunta da
sobrevivência**. `WAITING_ROOM_V1_BACKEND = FILESYSTEM` diz **onde se escreve**;
não diz **quem o guarda depois de o processo morrer**.

### POR QUÊ
Porque toda a prova da Sala até hoje correu **dentro de um processo**:
`provas/a_unidade_pousa_na_espera.py`, `a_linhagem_do_ready*.py`,
`o_scrap_chega_ao_acervo.py`. Escrever e reler no mesmo processo prova a
**escrita atómica**; não prova **durabilidade**. A primeira pergunta operacional
real — «e amanhã, onde está?» — só apareceu quando se tentou coletar a sério.

> **PROVA DENTRO DO PROCESSO ≠ PERSISTÊNCIA DEPOIS DO PROCESSO.**
> É a mesma família de `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS`, aplicada
> ao tempo em vez de ao grafo: **FLOW EXISTS != FLOW SURVIVES.**

### PROVA
```
git log --all -- 'data/samples/PRONTO-PARA-INTELIGENCIA'        → vazio
.github/workflows/sintonia-scrap.yml:499-508                     → namespace INSTAGRAM|YOUTUBE|SCRAP, e RECUSA o resto
.github/workflows/scrap-social.yml:452-455                       → três ficheiros de SOCIAL-IT, nomeados
grep -rn upload-artifact .github/workflows/                      → nenhum cobre a Sala
ADR-SALA-DE-ESPERA-V1.md §1                                      → sem tabela, sem migration, sem PostgreSQL
```

### CONSEQUÊNCIA
```
WAITING_ROOM_DURABILITY_OWNER = NENHUM
```
A Collection pode **atravessar** a estrada inteira e ainda assim não **guardar**
a ponta dela. Enquanto isto não tiver dono, coletar material real em Actions
produz READY que ninguém consegue ir buscar no dia seguinte — e o custo do erro
cresce com o tamanho do lote. Por isso este canário parou **antes** de gastar
rede, e não depois.

### SEGUNDO ACHADO — o preflight de egresso
```
EGRESS_PREFLIGHT_OWNER = NENHUM
```
O único medidor de egresso vive dentro de uma rota de aquisição. Exigir
`EGRESS_COUNTRY_CODE = IT` *antes* de adquirir é, hoje, impossível sem código
novo. **UM PREFLIGHT QUE SÓ CORRE DEPOIS DE COMEÇAR NÃO É UM PREFLIGHT.**

### TERCEIRO ACHADO — deriva de contrato na documentação
O código entrega `READY` com **12** campos; a ADR e o know-how `§76.1` ainda
dizem **11**. Medido, não corrigido nesta missão.

---

## 7 · O QUE ESTA MISSÃO NÃO FEZ, DE PROPÓSITO

```
DDL · migration · ALTER · CREATE · DROP · TRUNCATE · DELETE      NÃO
mudança de contrato · de Bíblia · de código funcional            NÃO
rota paga · Apify · comentários · dado pessoal                   NÃO
Big Collection · lote 20–50 · Intelligence                       NÃO
portal · legado IT/adama-website · reconciliação dos 195          NÃO
edição de JSON gerado do System Map                              NÃO
conserto em LIVE                                                 NÃO
```

---

## 7.1 · O VALIDADOR DO SYSTEM MAP — MEDIDO, E REPROVA POR DÍVIDA ANTERIOR

A lei do `AGENTS.md` exige correr o validador antes de fechar. Correu, no ramo
desta entrega (`claude/great-ride-2n4gbh`, que é a cabeça da `main`):

```
SYSTEM_MAP_CHECK=FAIL · 2 prova(s) reprovada(s)
  · P1_SEM_DRIFT        o mapa commitado nao corresponde ao repositorio de hoje
  · P9_CODIGO_DECLARADO .github/workflows/scrap-social.yml nao tem peca no mapa
```

**As duas reprovações são anteriores a esta missão e não foram causadas por
ela.** A causa é o commit `df165da9` — «registrar o workflow scrap-social no ramo
padrão (#3)» — que pôs o ficheiro na `main` sem lhe dar peça no mapa. Verificado
por medição: com o único ficheiro desta entrega (este relatório, um `.md` em
`docs/`) fora da árvore, o `P9` continua a reprovar na mesma.

Não se consertou aqui, e a razão está no §21 da missão: *«System Map observa. Não
editar JSON gerado.»* O gerador, ao correr, reescreveu oito ficheiros gerados na
árvore de trabalho — **todos revertidos**, e nenhum entra neste commit.

```
SYSTEM_MAP_FAIL_CAUSADO_POR_ESTA_MISSAO = NAO
SYSTEM_MAP_GENERATED_FILES_COMMITADOS   = 0
```

---

## 8 · RISCOS RESIDUAIS

1. **Nada foi provado sobre o LIVE.** `LIVE_SCHEMA_COMPATIBLE` continua
   `NOT_MEASURED`. Desbloquear o §7 **não** dispensa o §5.
2. **Nada foi provado sobre o egresso.** O `EGRESS_COUNTRY_CODE = IT` continua
   por medir, e hoje não há mecanismo que o meça sem adquirir.
3. **O runner pode estar offline.** Não foi possível confirmar (403 no proxy). O
   próprio `scrap-social.yml` avisa: `timeout-minutes` não limita a espera na
   fila — um job para um runner que não atende fica `queued` até 24h.
4. **`CANONICAL_E2E` continua por provar** (know-how `§76.3`): `REQUEST`,
   `ORCHESTRATOR`, `EXECUTOR` e `RUN` seguem sem corrida observada. Este canário
   era a tentativa de a produzir, e parou antes.
5. **Duas saídas possíveis para o §7, e a escolha é de gente, não desta aba:**
   (A) um passo canónico que devolva a Sala ao repositório — e aí colide com
   `P-011 · GIT NÃO É BANCO OPERACIONAL`; (B) a Sala ganha dono em banco — e aí
   é migration, proibida aqui. **As duas exigem decisão declarada; nenhuma é
   um conserto de execução.**

---

## HARD STOP

Missão encerrada no §7. Nada depois dele foi executado.
