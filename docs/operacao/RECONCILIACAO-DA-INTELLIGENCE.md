# RECONCILIAÇÃO DA INTELLIGENCE — a máquina que existe × a Bíblia que a governa

> ## ⚠️ CORRIGIDO EM 13/09/2026 — TRÊS ACHADOS DESTE DOCUMENTO ESTÃO ERRADOS
>
> Este documento foi medido em `main`/`claude/funny-hypatia-y7ho5s`, que está
> **268 commits atrás** da linha funcional da Collection. A missão `C-ADM-I01`
> remediu na linha funcional (`claude/raw-observation-identity-3jbwco` @
> `247fbf25`, onde `admissao/admissao.py` tem **356 linhas a mais**) e provou
> que o seguinte é **FALSO ali**:
>
> | o que este documento diz | o que a linha funcional mede |
> |---|---|
> | «INTERSECÇÃO DE CHAVES = VAZIA» | **falso** — `IDENTIDADE_DA_FONTE` lê `SOURCE_ID`; a pergunta «origem» responde **SIM** |
> | «ADMISSÕES CONCEDIDAS = 0» | **falso** — o livro tem **36 SIM**, e o recall da porta dá **42/49 (85,7%)** |
> | «`RAW_OBSERVATION_ID` não existe» | **falso** — `RAW_OBSERVATION_ID = raw_asset.id`, migration `027`, produzido por `guarda/preservar_coleta.observacoes_confirmadas()` |
>
> As 506 decisões com `item = "?"` são resíduo da **regra versão 1** (corridas
> `XX-*`). Nas versões 2 e 3 há 307 decisões, e **as 36 SIM têm identidade real**.
>
> A porta fala minúsculas **por desenho**: quem traduz é
> `coleta/ingresso.py::para_a_porta()`, o dono único do vocabulário. Medir o
> ledger contra a porta *sem* passar pelo tradutor — que foi o que este
> documento fez — não mede a estrada, mede um atalho que não existe.
>
> **O que continua verdadeiro:** a Intelligence não consome nada, e o contrato
> `PRONTO_PARA_INTELIGENCIA` não carrega as referências de identidade. Mas isso
> **não é um defeito**: é `G-READY-02`, uma decisão em aberto e deliberadamente
> não tomada — ver `provas/a_sala_de_espera_nao_tem_morada.py` na linha funcional.


> Medido em 13/09/2026, em `claude/funny-hypatia-y7ho5s` @ `dc0adf04`
> (`main` @ `f437ff11`). Continuação de
> [`CENSO-DA-INTELLIGENCE.md`](CENSO-DA-INTELLIGENCE.md).
>
> **Este documento não implementa nada e não é autoridade.** Ele reconcilia
> autoridades que já existem, arbitra com prova o que estava indeterminado, e
> desenha um contrato de entrada. Quem manda continua a ser a Bíblia; quem
> mede continua a ser o Git.

---

## A · A RESPOSTA EM UMA FRASE

**Reaproveitar quase tudo e ligar quase nada: a lógica analítica do SINTONIA é
património e fica; o que está errado é a fronteira — e a fronteira está errada
num ponto muito mais raso do que se pensava, porque a porta de admissão e a Sala
de Espera não falam a mesma língua.**

---

## B · O ACHADO QUE MUDA O PLANO

O censo disse: *«`PRONTO_PARA_INTELIGENCIA` é emitido e ninguém o lê.»* Ao
medir por baixo disso, o defeito é anterior e pior:

```text
ADMISSOES CONCEDIDAS ATE HOJE = 0
```

`data/samples/LIVRO-DE-DECISOES.json` tem **506 decisões**. Nenhuma é `SIM`:

```text
NAO_SEI        364
NAO_SE_APLICA  142
SIM              0
```

E em **506 de 506**, o item julgado é literalmente `"?"`.

### Porquê — provado executando o código real contra o dado real

```text
$ python3  ·  adm.decidir(<observação real da Sala de Espera>, "T3")
  resultado = NAO_SEI     regra = legivel     item = '?'

chaves que a porta procura : id · url · texto · source_id · fonte ·
                             fact_time · data · captured_at ·
                             source_location · fact_location
chaves que o ledger oferece: SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID ·
                             RAW_SHA256 · RAW_PATH · FACT_TIME · CAPTURED_AT ·
                             SOURCE_URL · RUN_ID · …

INTERSECCAO = VAZIA
```

A porta procura minúsculas, o armazém escreve MAIÚSCULAS. A porta pergunta
`id`; o armazém tem `DOCUMENT_ID`. A porta pergunta `url`; o armazém tem
`SOURCE_URL`.

> **NENHUMA CHAVE EM COMUM. A PORTA NUNCA VIU UM ITEM QUE CONSEGUISSE LER.**

Falha na **primeira** régua (`legivel`), antes de qualquer julgamento de
universo. Por isso `item = '?'`: a porta faz `item.get("id") or
item.get("url") or "?"`, e nenhuma das duas existe.

Isto é uma reparação de **uma dúzia de linhas na Collection** — não uma
arquitetura nova. E é o bloqueio real.

---

## C · MATRIZ BÍBLIA × IMPLEMENTAÇÃO

| Lei da Bíblia | Existe hoje? | Implementação | Prova | Compatível? | Ação |
|---|---|---|---|---|---|
| `INT-LAW-010` Intelligence começa na Sala de Espera | **NÃO** | motores leem `build/…/DESIGN-INGEST` | medido | **NÃO** | `ADAPT` |
| `INT-LAW-031` claim precisa de identidade global | PARCIAL | ledger tem `SOURCE_ID`+`DOCUMENT_ID`+`DOCUMENT_VERSION_ID`+`RAW_SHA256`; o contrato de saída perde-os | medido | parcial | `ADAPT` |
| `INT-LAW-036` SIGNAL ≠ FINDING ≠ OPPORTUNITY | NÃO | só OPPORTUNITY existe; os outros são nomes de campo | censo | — | `UNKNOWN` (não criar agora) |
| `INT-LAW-037` CROSSING é relação provada | **SIM** | `motor/v21_crossings.py`, 8 invariantes antes de emitir | código | **SIM** | `KEEP_LOGIC_ONLY` |
| `INT-LAW-050..054` INTELLIGENCE_RUN | **NÃO** | `RUN_ID` existe e é da Collection | medido | — | `RECOVER` (desenhar) |
| `INT-LAW-070..077` dependência antes da convergência | SIM | `v21_oportunidades` + Motor V2 §4 | código | SIM | `KEEP_AS_IS` |
| `INT-LAW-092` métricas de convergência separadas | SIM | 4 contadores separados | Motor V2 §4 | SIM | `KEEP_AS_IS` |
| `INT-LAW-101/102` escopo da página ≠ local do fato | SIM | `SOURCE_LOCATION`/`FACT_LOCATION` em 7 ficheiros | medido | SIM | `KEEP_AS_IS` |
| `INT-LAW-103..105` tempo participa da acionabilidade | PARCIAL | `SIGNAL_AGE_DAYS`, `REFERENCE_DATE`, `DATE_PARSE_STATE` — vocabulário próprio, ≠ do ledger | medido | parcial | `ADAPT` |
| `INT-LAW-130..136` Radar Futuro | SIM | Motor V2 §5, 4 estados | contrato | SIM | `KEEP_AS_IS` |
| `INT-LAW-150..153` Collection Gap first-class | **NÃO** | 0 ocorrências em código | censo | — | `RECOVER` (só contrato) |
| `INT-LAW-160..167` IA/LLM | N/A | **nenhum motor chama modelo** | medido | SIM | `KEEP_AS_IS` |
| `INT-LAW-183/184` READ ≠ DERIVE ≠ WRITE ≠ ACT | SIM | 0 chamadas de rede, 0 segredos | medido | SIM | `KEEP_AS_IS` |
| `INT-LAW-232` DECLARED ≠ OBSERVED | SIM | já é lei do System Map | portão | SIM | `KEEP_AS_IS` |

---

## D · ARBITRAGEM DAS LINHAGENS

O censo deixou o gerador canónico **indeterminado**. Está resolvido, e não era
um conflito de linhagens — era **um ponteiro velho**.

```text
CANDIDATO A   claude/acervo-to-package-intelligence-v1 @ 51010733  (2026-09-07)
              nomeado por italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json

CANDIDATO B   claude/opportunity-commercial-priority-v1 @ 55c2674  (2026-09-04)
              nomeado por motor/v21_cadeia.sh

HISTORY_EVIDENCE   git merge-base --is-ancestor 55c2674 51010733  ->  VERDADEIRO
                   git rev-list --left-right --count 55c2674...51010733
                       55c2674-only = 0      51010733-only = 17
                   B E ANTEPASSADO DIRETO DE A. Mesma linha, 17 commits atras.

CONTRACT_EVIDENCE  «medido em 5101073 pela cadeia canonica, corrida DUAS vezes
                   em worktrees limpos e independentes: 34/34 ficheiros byte a
                   byte identicos nas duas.»

ARTIFACT_EVIDENCE  EXPECTED_BUILD_ID = V21-06c6421d001ea52a
                   = o BUILD_ID do artefacto servido; `npm run build` PASSA.

CONTRA B           o proprio contrato lista a safra de 55c2674
                   (V21-69bf448ac934a6d9) como STALE_KNOWN_BUILD_ID.
```

```text
VEREDITO = A_WINS
```

Duas precisões que evitam o próximo erro:

- **O gerador é o COMMIT, não a branch.** `origin/claude/acervo-to-package-intelligence-v1`
  está **8 commits à frente** de `51010733`. Gerar a partir do topo da branch
  produziria uma safra que ninguém provou.
- **O comentário de `motor/v21_cadeia.sh` está errado** e é 3 dias mais velho
  que o contrato. Corrigi-lo é mudança de código — **não feita aqui**.

---

## E · BÍBLIA × MOTOR V2 — não há double-owner

```text
MOTOR_V2_ROLE = SUBORDINATE_CONTRACT
```

`docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`, 704 linhas, em
`claude/intelligence-backlog-canonical @ 4df24aa9` (2026-09-06). Nunca integrado.

| | Bíblia V0.2 | Motor V2 |
|---|---|---|
| o que se diz | constituição: fronteira, ownership, identidade dos objetos analíticos | «contrato de requisitos; fonte de verdade sobre **gates, estados e proibições**» |
| nível | lei | requisito verificável |
| reivindica conceitos da Collection? | **não** (`INT-LAW-002` exclui `SOURCE_ID`, `DOCUMENT_ID`, `RAW_OBSERVATION_ID`, Admission) | **não** — 0 ocorrências desses termos |

Sobreposições medidas, e todas **encaixam**:

| conceito | Bíblia | Motor V2 | veredito |
|---|---|---|---|
| identidade de claim | `INT-LAW-031` | §6 + gate `CLAIM_ID_COLLISIONS = 0` | Bíblia **cita e preserva** o Motor V2 e acrescenta o dono |
| convergência | `INT-LAW-076/092` | §4, 4 contadores separados | mesma regra, Motor V2 dá o contador |
| radar futuro | `INT-LAW-130..136` | §5, 4 estados | mesma regra, Motor V2 dá os estados |

A Bíblia diz *o que é proibido*; o Motor V2 diz *que número prova que não
aconteceu*. **Não há conceito com dois donos.**

---

## F · O CONTRATO DE ENTRADA

### F.1 · Não se cria conceito novo — o conceito já existe e está partido

Antes de inventar `INTELLIGENCE_INPUT`, `WAITING_ROOM_ITEM` ou
`EVIDENCE_PACKET`, a busca encontrou o objeto **já existente**:

```python
admissao/admissao.py :: pronto_para_inteligencia(item, decisao) -> dict
    ESTADO = "PRONTO_PARA_INTELIGENCIA"
```

Ele já tem dono (**Collection**), já tem nome, já tem 11 campos e já separa
`SOURCE_LOCATION` de `FACT_LOCATION`. Criar um segundo objeto de fronteira seria
exatamente o `RT` que o Control Plane existe para impedir.

```text
OWNER DO BOUNDARY OBJECT = COLLECTION
NOME                     = PRONTO_PARA_INTELIGENCIA  (já existe)
ACAO                     = REPARAR, NAO SUBSTITUIR
```

### F.2 · O que falta a esse contrato — medido campo a campo

| o ledger tem | o contrato de saída leva? | consequência |
|---|---|---|
| `SOURCE_ID` | sim (mas de `source_id`/`fonte`, minúsculas) | não casa |
| `DOCUMENT_ID` | **não** | perde a identidade do documento |
| `DOCUMENT_VERSION_ID` | **não** | perde a versão |
| `RAW_SHA256` | **não** | perde a identidade de conteúdo |
| `RAW_PATH` | **não** | perde o caminho para o bruto |
| `RUN_ID` (da Collection) | **não** | perde a corrida que o trouxe |
| `FACT_TIME` | sim (de `fact_time`) | não casa |
| `CAPTURED_AT` | sim (de `captured_at`) | não casa |
| `HEALTH_STATE`/`CADENCE_STATE` | **não** | perde frescura |

### F.3 · A menor interface possível

Três reparações, todas do lado da **Collection**, nenhuma nova camada:

```text
R1 · a porta passa a ler o vocabulario do ledger
     (SOURCE_ID, DOCUMENT_ID, ... — as chaves que a Sala de Espera ja escreve)
     -> deixa de devolver item='?'

R2 · o contrato de saida passa a carregar a IDENTIDADE que o ledger ja tem
     COLLECTION_RUN_ID · SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID ·
     RAW_SHA256 · RAW_PATH
     -> referencia, nunca copia: o dono continua a ser a Collection

R3 · a decisao passa a ser gravada COM essa identidade
     -> o LIVRO deixa de ter 506 linhas a dizer "?"
```

E do lado da **Intelligence**, nada ainda — só um leitor:

```text
R4 · um LEITOR que consome PRONTO_PARA_INTELIGENCIA e nao escreve nada
     na Collection. READ-ONLY sobre o dominio vizinho.
```

**O que fica explicitamente proibido**, por ser a ponte fácil que a missão veta:

```text
PROIBIDO  copiar JSON da Collection para build/ e mandar o motor ler
PROIBIDO  Intelligence ler collection-store/ledger diretamente
PROIBIDO  Intelligence inventar SOURCE_ID ou DOCUMENT_ID quando faltarem
          -> falta de identidade e COLLECTION GAP, nao valor por omissao
```

---

## G · IDENTIDADE E PROVENIÊNCIA ATRAVÉS DA FRONTEIRA

| exigido pela missão | existe na Sala de Espera? | atravessa hoje? |
|---|---|---|
| `RAW_OBSERVATION_ID` | **não com esse nome** — a identidade é `SOURCE_ID`+`DOCUMENT_ID`+`DOCUMENT_VERSION_ID` | não |
| `SOURCE_ID` | sim | mal |
| `DOCUMENT_ID` | sim | não |
| content identity | sim (`RAW_SHA256`) | não |
| `RUN` | sim (`RUN_ID`, `COLLECTION_RUN_STARTED_AT`) | não |
| admission decision | **não está no ledger** — vive noutro ficheiro, sem chave | não |
| `FACT_TIME` | sim, mas às vezes em **prosa** (*«por ponto — cada ponto traz a sua data»*) | mal |
| `PUBLICATION_TIME` | parcial (`SOURCE_DATE_ISO`) | não |
| `OBSERVED_TIME` / `COLLECTED_TIME` | `CAPTURED_AT` | mal |
| `SOURCE_LOCATION` / `FACT_LOCATION` | **não estão no ledger**; existem no contrato de saída | não |

> **`RAW_OBSERVATION_ID` não deve ser inventado.** A Collection já identifica uma
> observação por um trio. Se um `RAW_OBSERVATION_ID` único for mesmo necessário,
> quem o cria é a **Collection**, não a Intelligence — `INT-LAW-002` e
> `INT-LAW-083`.

---

## H · INTELLIGENCE_RUN

```text
EXISTE HOJE = NAO   (0 ocorrencias; RUN_ID e da Collection)
```

Requisitos mínimos, **desenhados e não implementados**, para responder às
perguntas de `INT-LAW-050..054`:

```text
INTELLIGENCE_RUN_ID        proprio, nunca reutilizar o RUN_ID da Collection
REQUESTED_BY               quem pediu
STARTED_AT / FINISHED_AT   quando
ENGINE_VERSION             que codigo correu
EFFECTIVE_CONFIG           configuracao efetiva (INT-LAW-052)
INPUTS_CONSUMED[]          referencias aos objetos de fronteira — nunca copias
RULES_EXECUTED[]           que reguas/motores
OUTPUTS_PRODUCED[]         que analiticos nasceram
RUN_STATE                  NOT_RUN | RUNNING | OK | ERROR | EMPTY_RESULT | NO_FINDING
                           (INT-LAW-053: sao cinco coisas diferentes)
REUSE_PROOF                se reaproveitou, porque (INT-LAW-054)
```

O schema completo **não se fecha aqui**: falta evidência sobre custo e modelo, e
fechá-lo agora seria inventar.

---

## I · MATRIZ DE REAPROVEITAMENTO

| Peça | Estado | Valor | Compat. V0.2 | Decisão | Motivo | Prova |
|---|---|---|---|---|---|---|
| `motor/v21_crossings.py` | wired, não corre | **alto** — 8 invariantes provadas antes de emitir | alta (`INT-LAW-037`) | `KEEP_LOGIC_ONLY` | a lógica é património; só o leitor `le()` está preso ao `DESIGN-INGEST` (21 refs) | código |
| `motor/v21_oportunidades.py` | wired, não corre | **alto** | alta | `KEEP_WITH_ADAPTER` | a versão de `main` é **1.374 linhas mais pobre** que a canónica — adotar a canónica | diff |
| `motor/v21_comercial.py` | wired | alto | alta | `KEEP_WITH_ADAPTER` | idem, −105/+92 | diff |
| `motor/v21_completude_oportunidade.py` | wired | alto | alta (`INT-LAW-110..114`) | `KEEP_AS_IS` | contrato de universo já é o que a Bíblia pede | teste verde |
| `leis/v21_*.py` (procedência, geografia, datas) | wired | alto | alta (`INT-LAW-101..105`) | `KEEP_AS_IS` | já separam `SOURCE_LOCATION`/`FACT_LOCATION` | 7 ficheiros |
| `leis/adama_relevance.py` | wired | alto | alta | `KEEP_AS_IS` | 19 testes verdes | teste |
| `motor/v21_ingest*.py` | wired | **médio** | baixa (`INT-LAW-010`) | `REWRITE_BOUNDARY` | é exatamente o leitor errado: lê `data/samples` e handoff anterior | medido |
| `portoes/site_v21_ingest.py` | wired | médio | n/a (é Delivery) | `KEEP_AS_IS` | do lado da Entrega, fora deste boundary | medido |
| `motor/v2_*.py` (7) | sem chamador | baixo | — | `RETIRE` (não apagar) | cadeia V2 legada, marcada legado no mapa | mapa |
| `pacote/lastmile_*.py` (4) | sem chamador | médio | — | `REFACTOR_LATER` | relatórios, não motor | medido |
| `pacote/v21_handoff_json.py` | não importa | nenhum | — | `RETIRE` | caminho `C:/eame-sintonia` fixo | ImportError |
| `motor/v21_reavaliar_35.py` | não importa | baixo | — | `RETIRE` | FileNotFoundError | ImportError |
| `italy-label-verdicts.js` | estático | médio | — | `KEEP_AS_IS` (histórico) | julgamento humano de 02/09, honesto no cabeçalho | ficheiro |
| 8 ficheiros do portal sem produtor | estático | ? | — | `UNKNOWN` | ver J | medido |
| `admissao/admissao.py` | corre, nunca admite | **crítico** | é o boundary | `REWRITE_BOUNDARY` | vocabulário incompatível — R1/R2/R3 | prova executável |

**Nada é apagado por esta missão.** `RETIRE` significa *marcado para aposentar
com prova*, não removido.

---

## J · O RESTO, EM UMA LINHA CADA

**CROSSINGS** — `KEEP_LOGIC_ONLY`. As 8 invariantes valem sob qualquer entrada;
o acoplamento é o leitor, não a regra. Pode operar sobre o futuro contrato.

**OPPORTUNITY** — a lógica é património e a versão canónica é a da linhagem A,
não a de `main`. O que depende de dados congelados são os **casos-testemunha**
(Motor V2 §3: VITE, EXELGROW, MAIS), que são fixtures — não regra.

**SIGNAL / FINDING** — `SHOULD_EXIST = SIM` (`INT-LAW-036`), `OWNER =
Intelligence`, mas **não criar agora**. Lógica que poderia produzi-los já existe
dentro de `v21_oportunidades` (`RED_TEAM_FINDINGS`) e dos crossings. Extraí-los é
missão futura.

**COLLECTION GAP** — remedido: continua `ABSENT` (0 ocorrências). Contrato
conceitual, só desenho:
`Intelligence deteta ausência → COLLECTION_GAP_REQUEST → orquestrador canónico
da Collection`. **Nunca** `Intelligence → collector`. `INT-LAW-151`: pede prova,
não escolhe rota.

**LABEL INTELLIGENCE** — capacidade vertical futura. O julgamento humano de
02/09 sobre 163 rótulos é o **ground truth** de que um motor futuro precisaria;
preservá-lo é mais valioso que recalculá-lo já.

**FUTURE RADAR** — Motor V2 §5 já tem os 4 estados que `INT-LAW-130..136`
exigem. `KEEP_AS_IS`.

**SEGURANÇA** — `READ/DERIVE-FIRST` já é verdade hoje, por medição: **0 chamadas
de rede**, **0 segredos**, **0 chamadas a modelo** em `motor/`, `leis/`,
`pacote/`. As 9 menções a «claude» são comentários e caminhos.
`superficie/ask_sintonia.py` diz-se explicitamente *«Não há chatbot aqui»*.
Marcado, sem consertar: `leis/calendario_handoff.py` chama `psql`, e
`motor/v21_tm_colher.py` tem caminho pessoal de Windows.

**CONTEÚDO HOSTIL** — `SAFE BY DESIGN` **hoje**, por ausência: nenhum conteúdo
coletado chega a um modelo porque nenhum motor chama um modelo. É uma segurança
por acaso, não por desenho — no dia em que um motor chamar um LLM,
`INT-LAW-161` passa a ser obrigação ativa.

**TESTES** — as 17 suites são `UNIT` e `RULE`. Nenhuma é `INTEGRATION` ou
`E2E`: nenhum teste corre um motor por subprocesso. Reaproveitáveis quase todas
como rede de segurança da lógica; **nenhuma** prova a cadeia.

---

## K · A PRIMEIRA PROVA MÍNIMA (a desenhar, não a implementar)

```text
1 observacao REAL do ledger da Sala de Espera
        |
        v
admissao.decidir(...)   ->  resultado = SIM   (hoje: NAO_SEI)
        |
        v
PRONTO_PARA_INTELIGENCIA  com identidade completa
        |
        v
1 INTELLIGENCE_RUN que apenas REGISTA o consumo
        |
        v
nenhuma analise. nenhum crossing. nenhuma oportunidade.
```

O objetivo **não** é produzir inteligência. É provar `COLLECTION READY →
INTELLIGENCE ACCEPTED` sem perder identidade.

### PASS / FAIL

```text
PASS exige:
  INPUT veio de data/collection-ledger/**       (sem copia manual)
  ZERO leitura de build/                        (sem bypass)
  SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID · RAW_SHA256  preservados
  nenhum destes inventado quando ausente        (ausencia = UNKNOWN)
  decisao de admissao gravada COM identidade    (item != "?")
  INTELLIGENCE_RUN_ID != COLLECTION RUN_ID
  Intelligence nao escreveu nada em data/collection-*
  correr duas vezes nao duplica a execucao      (idempotencia)
  ERROR distinguivel de NOT_RUN, EMPTY_RESULT, NO_FINDING, REJECTED
```

---

## L · MAPA DE MIGRAÇÃO

```text
STEP 0   corrigir o ponteiro do gerador em motor/v21_cadeia.sh   [Collection/Delivery]
STEP 1   R1 · a porta passa a ler o vocabulario do ledger        [COLLECTION]
STEP 2   R2+R3 · identidade no contrato de saida e no LIVRO      [COLLECTION]
STEP 3   provar: 1 item real sai da Sala de Espera com SIM       [COLLECTION]
STEP 4   INTELLIGENCE_RUN minimo, so a registar consumo          [INTELLIGENCE]
STEP 5   adapter de leitura para UM motor (crossings)            [INTELLIGENCE]
STEP 6   1 crossing real sobre material admitido                 [INTELLIGENCE]
STEP 7   COLLECTION_GAP como pedido de volta ao orquestrador     [fronteira]
STEP 8   tools · portal                                          [DELIVERY]
```

**Os três primeiros passos são da Collection, não da Intelligence.** É a
consequência mais importante desta reconciliação: a Intelligence não está
bloqueada por falta de Intelligence.

---

## M · RED TEAM DA PRÓPRIA PROPOSTA

| # | ataque | resultado | prova / impacto |
|---|---|---|---|
| 1 | estamos a criar um segundo owner do boundary | **FALHA** | reutiliza `PRONTO_PARA_INTELIGENCIA`, que já existe e é da Collection |
| 2 | Intelligence passa a possuir algo da Collection | **FALHA** | R1–R3 são todos do lado da Collection; Intelligence só ganha um leitor |
| 3 | inventámos conceito desnecessário | **FALHA** | só `INTELLIGENCE_RUN` é novo, e `INT-LAW-050` exige-o |
| 4 | escolhemos motor pela aparência | **FALHA** | A_WINS por ancestralidade + reprodutibilidade + artefacto, não por nome |
| 5 | preservamos dívida por medo | **PARCIAL** | 26 módulos sem chamador ficam; justificado por serem CLI manuais, mas **não medido um a um** |
| 6 | aposentamos lógica válida sem prova | **FALHA** | os 4 `RETIRE` têm prova (ImportError, legado no mapa) |
| 7 | o contrato depende de `build/` | **FALHA** | proibido explicitamente em F.3 |
| 8 | o contrato perde provenance | **FALHA** | R2 existe só para isso |
| 9 | o contrato perde `RAW_OBSERVATION_ID` | **ACEITE** | esse campo **não existe**; usamos o trio real. Se for preciso, quem o cria é a Collection |
| 10 | retry duplica processamento | **ABERTO** | idempotência está no PASS, mas o mecanismo **não está desenhado** |
| 11 | dois inputs iguais de observações diferentes colapsam por SHA | **ABERTO** | o ledger tem `SEMANTIC_ID_CHANGED_SAME_BYTES` — sinal de que o caso é real e **não foi resolvido aqui** |
| 12 | `SOURCE_ID` inventado | **FALHA** | proibido; ausência vira gap |
| 13 | `DOCUMENT_ID` inventado | **FALHA** | idem |
| 14 | READY confundido com «Intelligence processou» | **FALHA** | `INTELLIGENCE_RUN` é o que prova processamento, e é outro objeto |
| 15 | o Portal está a puxar a arquitetura | **FALHA** | nenhum passo do mapa parte de necessidade de UI |
| 16 | a Bíblia conflita com código maduro | **FALHA** | a matriz C não achou conflito; achou desalinhamento de vocabulário |
| 17 | a linha escolhida não é reproduzível | **FALHA** | o contrato documenta duas corridas independentes, 34/34 byte a byte |

**Três ataques não morreram: 5, 10 e 11.** Ficam registados como dívida aberta,
não como resolvidos.

---

## N · DELTA PARA O SYSTEM MAP (não aplicado)

```text
1  a aresta COLETA -> INTELIGENCIA nao existe, e o mapa nao a mostra como
   ausente: mostra as duas familias lado a lado, como se houvesse continuidade
2  falta estado para «WIRED mas impedido de correr» (motor fenced)
3  admissao/admissao.py aparece PROVEN; ela corre, mas nunca admitiu nada
```

O ponto 3 é o mais perigoso: verde por «o teste passa», quando o resultado
medido em produção é `SIM = 0`.

---

## O · O QUE CONTINUA DESCONHECIDO

```text
NAO SEI  se as 506 decisoes sao de uma corrida real ou de um ensaio (corrida XX-*)
NAO SEI  como distinguir duas observacoes diferentes com o mesmo SHA
NAO SEI  o mecanismo de idempotencia do INTELLIGENCE_RUN
NAO SEI  se os 26 modulos sem chamador sao todos CLI legitimos — medi o conjunto,
         nao um a um
NAO SEI  se algum dos 8 artefactos sem produtor teve produtor noutra branch
NAO SEI  custo e modelo no INTELLIGENCE_RUN — sem evidencia para fechar o schema
```
