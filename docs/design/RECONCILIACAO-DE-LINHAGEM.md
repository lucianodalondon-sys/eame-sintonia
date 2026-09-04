# A reconciliação de linhagem — a catraca universal sobre a inteligência mais nova

```
LINEAGE_RECONCILIATION = PASS
CANONICAL_HEAD         = (o merge desta rodada — ver §1)

caa6937 ancestral?  YES        inteligência de janela preservada?  YES
209335e ancestral?  YES        red team semântico preservado?      YES
4b97cf5 ancestral?  YES        catraca universal preservada?       YES
e7c154c ancestral?  YES        backfill preservado?                YES
```

⚠️ **Antes do merge, os quatro respondiam NO.** Este documento existe porque a
resposta era NO, e porque descobrir isso **antes** de declarar canônico é a
diferença entre uma reconciliação e um acidente.

---

## 1 · A prova de ancestralidade, antes de qualquer conserto

```
$ git merge-base --is-ancestor caa6937 d83f6f3   →  NO
$ git merge-base --is-ancestor 209335e d83f6f3   →  NO
$ git merge-base --is-ancestor 4b97cf5 d83f6f3   →  NO
$ git merge-base --is-ancestor e7c154c d83f6f3   →  NO
$ git merge-base --is-ancestor d83f6f3 e7c154c   →  NO      (nem o inverso)
$ git merge-base d83f6f3 e7c154c                 →  0ddf52d
```

```
* e7c154c  o cartao acertava o estado e mentia a razao — agora as duas coisas batem
* 4b97cf5  cinco perguntas, cinco respostas — duas mudam o resultado e tres dizem nao
* 209335e  janela deixa de ser calendario, e o acervo relido devolve um ACT NOW com razao
* caa6937  o cartao para de dizer ACT NOW quando nao ha janela, e passa a dizer o que falta
| * d83f6f3  a catraca media a traducao antes de ela entrar, e o numero certo e 42
| * 83d26b6  a catraca existe, e a travessia de dez origens achou duas que desapareciam
|/
* 0ddf52d  a coleta nova atravessa a V11.2 sozinha
```

**Duas irmãs, nenhuma contém a outra.** A missão da trilha universal partiu de
`0ddf52d` às 21:56; a mesma branch avançou quatro commits até 23:47, enquanto a
outra rodava. `d83f6f3` **não era canônico**, e o relatório anterior o chamou de
canônico. Está corrigido.

A reconciliação é um **merge**, não um reset e não um cherry-pick: os dois pais
sobrevivem e nenhuma linha foi apagada da história.

---

## 2 · O conflito era semântico, não textual

Nenhum arquivo de código colidiu. Os únicos conflitos textuais foram nove
marcadores de contagem de teste, resolvidos com a ferramenta que o próprio
teste manda rodar.

O choque estava no **dono**:

| campo | `v21_oportunidades.py` @ e7c154c | `v21_briefing.py` (meu) |
|---|---|---|
| `STATUS` / por que agora | ✅ com cadeia de 4 elos + evidência | `WHY_NOW`, por fora |
| `WINDOW_TYPE` · `WINDOW_DEFINED` · `WINDOW_OPEN_NOW` | ✅ via `v21_janelas.py` | — (não conhecia) |
| `PEST_STAGE_STATE` · `ACTION_RECOMMENDATION_STATE` · `THRESHOLD_STATE` · `WINDOW_RULE_STATE` | ✅ | — |
| `PORTFOLIO_MATCHES` · `PRIMARY_MATCH` | ✅ com `LABEL_QUOTES` | duplicado |
| `ACTION_BY_DEPARTMENT` | ✅ com `WHY_CODE` por departamento | `ACTION_MAP[]`, duplicado |
| `EVIDENCE_ROLES` · `INTELLIGENCE_BRIEF` · `WHAT_IS_MISSING` | ✅ | duplicado |

E não era só duplicação: era duplicação **pior**. Para botrite × videira ×
Emilia-Romagna, minha camada devolvia `VALIDATE_NOW` — porque não sabia ler
janela fenológica. O motor devolve `ACT_NOW`, com
`WINDOW_TYPE = PREHARVEST_WINDOW`, `WINDOW_OPEN_NOW = YES` por
`ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO` e os quatro elos fechados.

    DUAS RESPOSTAS PARA A MESMA PERGUNTA NÃO SÃO REDUNDÂNCIA:
    SÃO UM BUG ESPERANDO A HORA DE APARECER NA TELA.

**Resolução por dono:** `v21_briefing.py` e `v21_ler_briefing.py` apagados. A
cadeia volta a ter **um** passo novo — a catraca. `U10` impede a catraca de
escrever qualquer campo do cartão; `U10b` impede o briefing paralelo de voltar.

---

## 3 · Os 43 casos nas três árvores

`python3 scripts/v21_reconciliacao_de_linhagem.py <e7c154c> <d83f6f3>` → **EXIT 0**

| | e7c154c | d83f6f3 | reconciliado |
|---|---:|---:|---:|
| casos | 43 | 43 | **43** |

```
CASOS QUE SUMIRAM        0
DIVERGENCIA_SEM_DONO     0     ← nada foi decidido na fusão; tudo foi herdado

CAMPO_NOVO_DA_LINHAGEM  430    campos que nasceram em e7c154c
IGUAL_NOS_TRES          147
DA_CATRACA               86    PUBLICATION_STATE + TRAIL_STATE, 43 casos
DA_LINHAGEM_NOVA         25    onde as duas linhas discordaram
DA_MINHA_LINHA            0    ← minha linha não venceu em campo nenhum
```

As **25** divergências são todas no mesmo campo — `STATUS` — e todas na mesma
direção: a linhagem nova é **mais conservadora**.

| d83f6f3 | → reconciliado | n |
|---|---|---:|
| `ACT_NOW` | `WATCH` | 11 |
| `PREPARE_NOW` | `WATCH` | 11 |
| `ACT_NOW` | `VALIDATE_NOW` | 3 |

`STATUS` final: `WATCH` 22 · `TO_VALIDATE` 9 · `FUTURE_PREPARATION` 7 ·
`VALIDATE_NOW` 3 · **`ACT_NOW` 2**.

    QUATORZE CASOS DIZIAM «AGIR AGORA» PORQUE O BOLETIM ERA DE ONTEM.
    DOIS DIZEM «AGIR AGORA» PORQUE A JANELA ESTÁ ABERTA.

---

## 4 · As seis testemunhas, no estado reconciliado

| | testemunha | medido |
|---|---|---|
| **A** | botrite × videira × Emilia-Romagna | `ACT_NOW` · `WINDOW_TYPE=PREHARVEST_WINDOW` · `WINDOW_OPEN_NOW=YES` (`ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO`) · `PHENOLOGY_DECLARED="Vite: «maturazione»."` · produtos AGHARTA · BANJO · EMBRACE preservados · `PRIMARY_MATCH=CATPRD_BANJO` · **e `PUBLICATION_STATE=PUBLISHABLE` da catraca por cima** |
| **B** | Toscana · «maggior suscettibilità» | prova **só o elo que tem**: em `OPP_F8106D5E1767` ela sustenta `WINDOW_TYPE=PHENOLOGY_WINDOW`; sinal e portfólio vêm de outra evidência. Nos outros dois casos toscanos `WINDOW_DEFINED=NO` — a frase sozinha não abriu nada |
| **C** | Veneto × carpocapsa | `PEST_STAGE_STATE=STAGE_ENDED` **e** `ACTION_RECOMMENDATION_STATE=CONTINUE_RECOMMENDED`. `STATUS=VALIDATE_NOW`, **não** fechado: o fim do voo não virou janela fechada |
| **D** | Emilia-Romagna × limiar 5% | `THRESHOLD_STATE=NOT_DECLARED` · `WINDOW_OPEN_NOW=**UNKNOWN**` por `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE`. **Nunca `NO`** |
| **E** | Umbria | `OPP_169BD86DB324` tem `WINDOW_CONDITION` própria, citando a *soglia* do boletim da Umbria. Os 5% da Emilia-Romagna **não migraram**: são dois `THRESHOLD_WINDOW` distintos, cada um com sua evidência |
| **F** | `RULE_DELEGATED_TO_FARM` | `OPP_75C37DED9160` · `WINDOW_DEFINED=NO` · `STATUS=VALIDATE_NOW`. A decisão continua delegada ao pomar; **nenhuma janela regional foi inventada**. `U13` pina isso |

---

## 5 · O que a catraca preserva, e o que ela não é

Preservado inteiro, porque não tem dono na outra linha:

- `UNIVERSAL_GATE` · `v21_catraca.py` · `PUBLICATION_STATE` só rebaixável
- aceitação que **interrompe** a cadeia (11 contadores)
- fim do `classificar || true` / `medir || true` no caminho de publicação
- testemunha universal de ingestão · `BACKFILL` pela mesma cadeia
- ordem tradução → catraca

Perdido de propósito, porque tinha dono melhor: `OPPORTUNITY-BRIEFINGS.json`, o
contrato comercial paralelo e os papéis de evidência da minha camada — **todos
existem no cartão**, em `EVIDENCE_ROLES`, `INTELLIGENCE_BRIEF`,
`ACTION_BY_DEPARTMENT`, `PORTFOLIO_MATCHES` e `WHAT_IS_MISSING`.

```
== A CATRACA (reconciliada) ==
porta          10 familias · COMMERCIAL_CATALOG 0/10 · HERBICIDE_CURRENT_CONTEXT 0/16
material       7.029 registros · PASSED 6.991 · INCOMPLETE 38 · QUARANTINED 0
oportunidades  PUBLISHABLE 5 · VALIDATION_REQUIRED 38
trilha         COMPLETE 43        VIOLACOES 0
```

`NO_TEXT_FOR_PAIR_EXTRACTION` caiu de 40 para **36**: a linhagem nova consertou
os quatro boletins que chegavam mudos ao motor. O teste `U6` **foi invertido** —
pinava o silêncio, agora pina o conserto.

    UM TESTE QUE PINA UM DEFEITO VIRA UM TESTE QUE PINA O CONSERTO.
    O QUE NÃO PODE É SUMIR NA HORA EM QUE O DEFEITO SUMIU.

---

## 6 · Os 26 sem coleção — e a correção de um erro meu

`python3 scripts/v21_censo_das_16_janelas.py` · **não ingere nada**

```
PAPEL_DE_TRABALHO = 10        JANELAS_CORRENTES = 16
```

A separação 10/16 **confirma-se** no estado reconciliado. O que **não** se
confirma é o que o relatório anterior disse sobre os 16.

Medido contra o dono do tipo de janela (`v21_janelas.tipos_da_oracao`):

| | |
|---|---:|
| com tipo **agronômico** reconhecido | **0** |
| `ADMINISTRATIVE_WINDOW` | 2 |
| sem alvo nomeado no texto | 6 |
| já modeladas pela linhagem nova | 0 |
| **realmente novas** (não duplicatas) | **16** |

O que elas são, pelo tipo que a própria fonte declara: `RESISTENCIA_x_EPOCA` 3 ·
`JANELA_CORRENTE` 2 · `DOCUMENTO_REGIONAL_DATADO` 2 · e um cada de
`SECAO_AUSENTE_NO_BOLETIM`, `DEROGA_COM_JANELA_DE_CALENDARIO`,
`LIMITE_DE_DISCIPLINAR_DE_PRODUCAO_INTEGRADA`,
`EVENTO_REGULATORIO_QUE_FECHA_JANELA`, `ORIENTACAO_TECNICA_NAO_REGULATORIA`,
`RESISTENCIA_CONFIRMADA`, `REGRA_TECNICA_DE_EPOCA`, `JANELA_FECHADA_AGORA`,
`LACUNA_DATADA`. Culturas: trigo genérico 7 · arroz 3 · beterraba 1 · tomate 1 ·
sem cultura 4. Todas `CURRENT`, todas Emilia-Romagna ou nacional.

**O erro do relatório anterior, em duas partes:**

1. Disse que estes 16 eram «janelas correntes de aplicação». **Não são.** Zero
   têm tipo agronômico; dois são administrativos.
2. Disse que a ausência deles era «a causa medida de `ACT_NOW = 0`».
   `ACT_NOW = 0` era defeito da **minha própria camada paralela**, que não sabia
   ler janela fenológica. O motor devolve `ACT_NOW = 2`.

    ATRIBUIR AO DADO QUE FALTA UM DEFEITO QUE ERA DO MEU CÓDIGO
    É A FORMA MAIS CONFORTÁVEL DE ERRAR.

Não foram ingeridos. A coleção canônica, se um dia forem, é
`CURRENT-FIELD-SIGNALS.json` — é de lá que `v21_janelas` lê a janela.
`CROP-WINDOWS.json` seria o lugar errado: guarda janela de **calendário**, e
estas não são de calendário.

---

## 7 · Regressões

| | e7c154c | reconciliado |
|---|---:|---:|
| testes descobertos | 758 | **778** (+20) |
| falhas | 7 | **6** |
| erros | 1 | **1** |
| pulados | 16 | 16 |

Nenhuma falha nova. As 6 e o erro são as de sempre: procedência de amostras
antigas (×5), o gate de import ES, e o módulo `test_comunicacao` que é script e
aborta na descoberta. A falha a menos é `test_branch_vivo_nao_e_alvo_congelado`,
que depende do estado git do checkout e falha só em worktree destacada.

O arquivo `tests/test_trilha_universal.py` **encolheu de 28 para 20 testes**, e
isso é o conserto: os 8 que sumiram provavam a camada paralela que foi apagada.
Em troca entraram `U10`, `U10b`, `U11`, `U12`, `U13`, `U14` — a fronteira da
reconciliação, que impede a catraca de ter apagado algo da linhagem nova.

---

## 8 · Confirmação

```
PORTAL          = NÃO TOCADO     (italia-portale/ não aparece no diff)
DESIGN          = NÃO TOCADO
VERCEL          = NÃO TOCADO
PRODUÇÃO        = NÃO TOCADA
THRESHOLDS      = NÃO ALTERADOS
NOVA COLETA     = NÃO
INGESTÃO DAS 16 = NÃO
MERGE PARA MAIN = NÃO            (o merge foi entre as duas linhas de trabalho)
PUBLICAÇÃO      = NÃO
SEGUNDO MOTOR   = NÃO — e o que existia foi APAGADO nesta rodada
```

---
---

# ADENDO · a rodada final — incorporar `85df96f`

```
FINAL_CANONICAL_RECONCILIATION = PASS

85df96f ancestral de 4628197 ANTES?   NO
85df96f ancestral do HEAD final?      YES
4628197 ancestral do HEAD final?      YES
```

## 1 · A prova, outra vez antes do conserto

```
$ git merge-base --is-ancestor 85df96f 4628197  →  NO
$ git merge-base 85df96f 4628197                →  e7c154c
$ git log --oneline e7c154c..85df96f            →  85df96f  (um commit só)
```

`4628197` **não era canônico**: parou em `e7c154c` e a branch canônica seguiu
mais um commit. Duas vezes seguidas a mesma lição:

    O NOME DA BRANCH NÃO É PROVA. A ANCESTRALIDADE É.

## 2 · A estratégia

Como a missão pediu: **partir da branch canônica em `85df96f` e fazer merge da
linhagem da catraca.** Sem reset, sem rebase, sem force-push, sem cherry-pick.
O commit final tem os dois pais.

Nove conflitos, **todos marcadores de contagem de teste**. Nenhum arquivo de
código colidiu — e cada metade ficou byte-idêntica ao seu dono:

| arquivo | idêntico a |
|---|---|
| `v21_janelas.py` · `v21_oportunidades.py` · `v21_necessidade.py` · `v21_fechamento_das_regras.py` | **85df96f** |
| `v21_catraca.py` · `v21_aceitacao.py` · `v21_cadeia.sh` · `test_trilha_universal.py` | **4628197** |

    CÉREBRO DE 85df96f + CATRACA DE 4628197.

## 3 · O fechamento das regras atravessou inteiro

`python3 scripts/v21_fechamento_das_regras.py` sobre a árvore mesclada →
**`WINDOW_RULE_CLOSURE = PASS`**

| | |
|---|---:|
| `CASES` | **43** |
| `WINDOW_DEFINED` | 6 → **16** |
| `WINDOW_RULE_MISSING` | 11 → **1** |

Dos onze gaps: **9** ganharam regra agronômica · **1** `RULE_ADMINISTRATIVE_ONLY`
· **1** continua `RULE_NOT_DECLARED`.

Estados presentes: `RULE_DECLARED` 15 · `RULE_NOT_DECLARED` 26 ·
`RULE_DELEGATED_TO_FARM` 1 · `RULE_ADMINISTRATIVE_ONLY` 1.
Tipos: `PHENOLOGY_WINDOW` 7 · `THRESHOLD_WINDOW` 5 · `PEST_STAGE_WINDOW` 1 ·
`PREHARVEST_WINDOW` 1 · `WEATHER_TRIGGERED_WINDOW` 1 ·
`RULE_DELEGATED_TO_FARM` 1.

`U19`–`U26` passam a segurar cada lei: a contagem, os quatro estados, norma que
não vira janela agronômica, regra delegada que **define e não abre**, arroz ×
giavone em `RULE_NOT_DECLARED` **por `GEO_ITALY` sem sinal e sem direção** (a
regra da Lombardia não foi aplicada à Itália inteira), disciplinare que não cria
`NEED_DIRECTION`, a evidência da janela dentro de `EVIDENCE_IDS`, e o limiar
região-específico.

### O teste que nasceu errado

`U26` procurava a substring «5%» no texto da Umbria para provar que ela não
herdara o limiar da Emilia-Romagna — e **reprovou**, porque «10-15%» contém
«5%». O dado estava certo; a medição é que era grosseira.

    PROCURAR PORCENTAGEM POR SUBSTRING ACHA O NÚMERO DENTRO DO NÚMERO.

Corrigido para comparar a **frase** de cada região, que é o que a fonte escreveu.

## 4 · As oito testemunhas

| | medido no HEAD final |
|---|---|
| **A** contagem | 43 · 16 · 1 — inalterados |
| **B** 11 gaps | 9 `RULE_DECLARED` + 1 `RULE_ADMINISTRATIVE_ONLY` + 1 `RULE_NOT_DECLARED`; nenhum voltou a `WINDOW_RULE_MISSING` |
| **C** arroz × giavone | `RULE_NOT_DECLARED` · `GEO_ITALY` · `DIRECTION_UNKNOWN` + `REGION_NOT_DECLARED` |
| **D** `STANDING_RULE` | 7 sinais; `v21_necessidade.CLASSES_QUE_NAO_DECLARAM_DIRECAO = ('STANDING_RULE',)`. Nenhum `NEED_EVIDENCE_ID` sai de disciplinare |
| **E** botrite × E-R | `ACT_NOW` · `PREHARVEST_WINDOW` · `WINDOW_OPEN_NOW=YES` · `RULE_DECLARED` · AGHARTA/BANJO/EMBRACE · `PUBLICATION_STATE=PUBLISHABLE` |
| **F** Toscana | `PHENOLOGY_WINDOW` sustentado pela frase de suscetibilidade — só o elo dela |
| **G** Veneto × carpocapsa | `STAGE_ENDED` + `CONTINUE_RECOMMENDED` · `WINDOW_DEFINED=YES` · `WINDOW_OPEN_NOW=UNKNOWN` · `VALIDATE_NOW` |
| **H** Umbria | `THRESHOLD_WINDOW` com a *soglia* 10–15% do próprio boletim · `WINDOW_OPEN_NOW=UNKNOWN` por `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE` |

## 5 · Os 43 nas três árvores

`v21_reconciliacao_de_linhagem.py <85df96f> <4628197>` → **EXIT 0**

```
casos                 43 · 43 · 43        sumiram 0
DIVERGENCIA_SEM_DONO   0
DA_MINHA_LINHA         0
IGUAL_NOS_TRES       564
DA_CATRACA            86      PUBLICATION_STATE + TRAIL_STATE
DA_LINHAGEM_NOVA      81      o cérebro venceu
```

Os **81** são exatamente os 10 gaps fechados, oito campos cada:
`WINDOW_DEFINED` NO→YES ×10 · `WINDOW_TYPE` null→tipo ×10 ·
`WINDOW_RULE_STATE` ×10 · `WHY_NOW_CODES` ×10 · `ACTION_CHAIN_LINKS` ×10 ·
`ACTION_BY_DEPARTMENT` ×10 · `WHAT_IS_MISSING` ×10 · `EVIDENCE_ROLES` ×11.

**`STATUS`, `COMMERCIAL_PRIORITY`, `EXTERNAL_MATERIAL_READY`, `NEED_DIRECTION`,
`PORTFOLIO_MATCHES`, `PRIMARY_MATCH` e `WINDOW_OPEN_NOW` ficaram IGUAIS nos
três.** A regra definiu janela e **não criou oportunidade** — a lei que
`85df96f` escreveu, provada por diferença medida.

## 6 · A catraca universal, de novo

```
AUTOMATIC_NEW_INGEST = YES   ·   UNIVERSAL_GATE = YES   ·   BACKFILL = YES

RAW → CANONICAL ENTRY → NORMALIZATION → WINDOW INTELLIGENCE →
COMMERCIAL PRIORITY → ACCEPTANCE → PUBLICATION_STATE

BUILD_ID  V21-1cac64ceb8067205  →  com fixtures muda  →  restaurado IGUAL
material  7.036 · PASSED 6.998 · INCOMPLETE 38 · QUARANTINED 0
gate      PUBLISHABLE 5 · VALIDATION_REQUIRED 38 · VIOLACOES 0
```

Segundo motor: **não** — e o que existia foi apagado na rodada anterior.

## 7 · Os 26, reavaliados depois do fechamento

```
10 papel de trabalho   ·   16 registros reais
com tipo AGRONÔMICO reconhecido                        0
ADMINISTRATIVE_WINDOW                                  2
sem alvo nomeado                                       6
com STANDING_RULE já ingerida no mesmo par             0
REDUNDANTES APÓS 85df96f                               0
realmente novas                                       16
```

`85df96f` ingeriu disciplinari para videira, milho e macieira; estes 16 são
contexto de herbicida para trigo, arroz, beterraba e tomate. **Não se cruzam.**
Continuam não sendo janela agronômica, e continuam não ingeridos.

## 8 · ISTAT

```
2024 QA = YES   ·   2025 QA = YES   ·   2026 QA = UNKNOWN
CARIMBO NÃO APLICADO
```

O bug `area[0]` continua em `scripts/v21_oportunidades.py:1288` e nomeado em
`docs/design/FECHAMENTO-DAS-REGRAS-DE-JANELA.md`. **Não corrigido por palpite** —
a integração não o apagou.

## 9 · Regressões

| | 85df96f | HEAD final |
|---|---:|---:|
| testes | 763 | **791** (+28) |
| falhas | 7 | **6** |
| erros | 1 | **1** |
| pulados | 16 | 16 |

Nenhuma falha nova. A que falta é `test_branch_vivo_nao_e_alvo_congelado`, que
só falha em worktree destacada.

## 10 · Branch

`claude/opportunity-commercial-priority-v1` volta a ser a **casa da
inteligência**. `claude/trilha-universal-inteligencia-a5rx9d` fica como branch
histórica de integração, apontando para o mesmo commit — **não há duas linhas
evoluindo em paralelo.**

```
PORTAL = NÃO TOCADO · DESIGN = NÃO TOCADO · VERCEL = NÃO TOCADO
PRODUÇÃO = NÃO TOCADA · THRESHOLDS = NÃO ALTERADOS
NOVA COLETA = NÃO · INGESTÃO DAS 16 = NÃO · PUBLICAÇÃO = NÃO
```
