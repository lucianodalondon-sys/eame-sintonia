# RED TEAM DO CONTRATO DE COMPOSIÇÃO — D0.4R

```
DOCUMENT_TYPE   RED TEAM · casos sintéticos de contrato
DATE            2026-09-08
REVISION        D0.4R · corrige o red team de D0.4 (não o substitui por outro documento)
SCRIPT          testar_contrato_composicao.py   READ-ONLY · exit 1 se falhar
DADOS           RED-TEAM-COMPOSICAO-V1.json
RESULTADO       PASS · 11/11 CENÁRIOS EXECUTADOS · 6/9 regras exercitadas por recusa
```

> ⚠️ **`SYNTHETIC_CONTRACT_TEST ≠ OBSERVED CASE`.**
> Os cenários abaixo **não existem no mundo**. Testam a arquitetura, nunca são
> evidência, **nunca somam aos 43** e nunca se publicam como dado.

> ⚠️ **`SCENARIO EXECUTED ≠ PROPERTY PROVED`.**
> D0.4 escreveu `PASS · 8/8` e deixou ler-se «o contrato está provado». Não estava.
> Um cenário que passa prova **que aquele cenário foi julgado como se esperava** —
> nada mais. As regras que nenhum cenário obrigou a recusar continuam **não
> exercitadas**, e estão nomeadas em §5 em vez de escondidas atrás de um `8/8`.

## §1 · O QUE D0.4R CORRIGE

| # | o que D0.4 dizia | o que a medição diz | onde |
|---|---|---|---|
| 1 | `PASS · 8/8` sem qualificar | 11 cenários executados · 6 de 9 regras exercitadas | §5 |
| 2 | `RT-03` e `RT-04` «testam a promoção» | testavam **coexistência**; a tentativa real faltava | §3 |
| 3 | `C3` violada, «o red team não pode reprovar o que não simula» | `C3` tem agora **testemunha executável sobre dado real** e cenário sintético (`RT-09`) | §2, §3 |
| 4 | — | contradição `EXECUTABLE RULE ≠ EMITTED EXPLANATION` medida e registada como **RR-06** | §4 |
| 5 | `SALES_READY` = «cinco condições» / «quatro pré-condições» | **7 condições atómicas → 6 dimensões semânticas** | §4 |

Nenhuma conclusão antiga foi protegida. Onde a prova derrubou o texto, o texto mudou.

## §2 · TESTEMUNHA EXECUTÁVEL DA VIOLAÇÃO DE `C3` (dado real)

`C3 · nenhuma autoridade que não é dona do tempo reescreve o tempo` é hoje **violada
pelo runtime** (`RR-01`). D0.4 declarou-o e não o provou. D0.4R prova-o, reexecutando a
lei do dono real (`fb96f49d::estado_de_acao`) sobre os campos que o snapshot já persiste:

```
casos onde o gate de validação sobrescreve o estado temporal ....  9
estado temporal pré-override persistido em algum campo .........  0 / 9
estado recuperado por REEXECUÇÃO ...............................  WATCH em 9/9
a lei reproduz os casos não sobrescritos .......................  34 / 34

C3_RUNTIME_STATE ......... KNOWN_VIOLATION
C3_VIOLATION_REPRODUCED .. YES
C3_TARGET_CONTRACT ....... PROPOSED   (não aplicado ao runtime)
```

Casos testemunha: `OPP_00C5B6E15185`, `OPP_4C39CCC05EEB`, `OPP_568684853264`,
`OPP_5D03565DB4C3`, `OPP_6BA350CA1538`, `OPP_8E210567B01F`, `OPP_9AB924CA36C8`,
`OPP_B362181E3A45`, `OPP_EE1E2A3869EE`.

**A informação não se perdeu nesta safra — mas não está no campo.** A recuperação exige
**reexecutar a lei**, o que `L-32` proíbe ao casco.

> **`C3` NÃO É UMA REGRA CUMPRIDA. É UMA REGRA PROPOSTA CONTRA UMA VIOLAÇÃO MEDIDA.**
> Escrevê-la sem esta linha seria declarar cumprido o que está aberto.

## §3 · OS ONZE CENÁRIOS

Cada cenário é agora uma **tentativa de transição** explícita:
`(estado antes, autoridade que tenta, estado proposto depois)`. Um cenário sem autoridade
é declarado como **coexistência**, e não se apresenta como teste de promoção.

| id | cenário | autoridade que tenta | veredito | regra que decidiu |
|---|---|---|---|---|
| `RT-01` | oportunidade acionável que não pode ser publicada | — coexistência | **ACEITE** | nenhuma violação |
| `RT-02` | publicável internamente, brief externo negado | — coexistência | **ACEITE** | `C5` permite externo mais restritivo |
| `RT-03a` | `RADAR` com janela aberta | — coexistência | **ACEITE** | o estado convive |
| `RT-03b` | a urgência **tenta promover** `RADAR` → `OPPORTUNITY` | `TEMPORAL_STATE` | **RECUSADO** | `C1` |
| `RT-04a` | futuro com prioridade comercial alta | — coexistência | **ACEITE** | o estado convive |
| `RT-04b` | o comercial **tenta transformar** `FUTURE_PREPARATION` → `ACT_NOW` | `COMMERCIAL_PRIORITY` | **RECUSADO** | `C3b` |
| `RT-05` | sinal recente tenta virar janela de ação | `SIGNAL_RECENCY` | **RECUSADO** | `C7` · `TIME SINCE ≠ TIME UNTIL` |
| `RT-06` | card existe sem inventar timing | — coexistência | **ACEITE** | pode existir com `UNKNOWN` |
| `RT-07` | material para terceiro com `EXTERNAL = UNKNOWN` | `DELIVERY` | **RECUSADO** | `C8` · `UNKNOWN NÃO É PERMISSÃO` |
| `RT-08` | `EXTERNAL` permissivo sobre publicação negada | `EXTERNAL_MATERIAL_READY` | **RECUSADO** | `C5` |
| `RT-09` | o gate de validação **tenta reescrever o tempo** — `RR-01` em sintético | `VALIDATION_GATE_STATE` | **RECUSADO** | `C3` |

### O que mudou em `RT-03` e `RT-04`

D0.4 apresentou-os como «aceite, sem promoção» e concluiu que o contrato recusa a
promoção. **O cenário nunca tentou promover.** Um estado que ninguém tentou mudar não
prova que a mudança seria recusada.

D0.4R parte-os em dois. `RT-03a`/`RT-04a` mantêm a coexistência, que continua legítima e
continua aceite. `RT-03b`/`RT-04b` executam a **tentativa real** — e aí sim o contrato
recusa, por `C1` e por `C3b`.

> **NÃO TER TENTADO NÃO É TER SIDO RECUSADO.**

### `C3b`, a regra que o red team obrigou a escrever

`C3` proibia o gate de reescrever o tempo. Não proibia o **comercial** de o fazer.
`RT-04b` entrou por essa porta. `C3b · nenhuma autoridade não-dona reescreve o tempo,
seja qual for` nasceu daí — e fica registado que nasceu do red team, tal como `C8` em
D0.4 nasceu de `RT-07` ter passado por omissão.

> **UM CONTRATO QUE ACEITA POR OMISSÃO NÃO É UM CONTRATO. É UM SILÊNCIO.**

## §4 · DUAS MEDIÇÕES QUE DERRUBARAM TEXTO DE D0.4

### 4.1 · `EXECUTABLE RULE ≠ EMITTED EXPLANATION` → **RR-06**

```
dono ................ scripts/v21_oportunidades.py @ fb96f49d
regra executável .... ELOS = 5
                      SINAL_ATUAL · JANELA_DEFINIDA · JANELA_ABERTA_AGORA
                      VINCULO_COM_PORTFOLIO · TEMPO_PARA_ACAO
texto emitido ....... «quatro elos» · 3 ocorrências
                      WHY_NOW_LAW (l.1798) · STATUS_LAW (l.2218) · ESTADOS_DE_ACAO_LEI (l.2429)
o texto errado viaja para o snapshot?  NÃO — WHY_NOW_LAW e STATUS_LAW ausentes
o que viaja ......... ACTION_CHAIN_LINKS com 5 chaves em 43/43
```

A regra que decide está certa. **A explicação que o sistema emite sobre a sua própria
regra está errada.** O dano está contido a montante nesta safra, porque o texto não
viaja — mas a explicação é um produto, e um produto errado é um defeito.

> **RR-06 · `EXECUTABLE RULE ≠ EMITTED EXPLANATION`.**
> Impacto medido: contido no motor. Estado: **aberto**. Não corrigido aqui (`ZERO RUNTIME`).

### 4.2 · `SALES_READY` · contagem medida, não narrada

D0.4 escreveu «cinco condições» num parágrafo e «composição de quatro pré-condições»
noutro. **As duas erradas.** Medido sobre o dono real:

```
ATOMIC_CONDITIONS ..... 7      predicados que o motor avalia
SEMANTIC_DIMENSIONS ... 6      perguntas de negócio que esses predicados respondem
os 6 casos SALES_READY satisfazem todos os predicados verificáveis .... 6/6
```

| dimensão semântica | condições atómicas |
|---|---|
| `PROBLEMA` | `TARGET_DECLARADO` |
| `RESPOSTA_ADAMA` | `ROTULO_VERIFICADO` · `CATALOGO_COMERCIAL` |
| `NECESSIDADE` | `NECESSIDADE_POSITIVA` |
| `GEOGRAFIA` | `GEOGRAFIA_SUSTENTA` |
| `NATUREZA_DO_CASO` | `ARQUETIPO_NAO_REGULATORIO` |
| `TEMPO` | `JANELA_COMERCIAL` |

`JANELA_COMERCIAL` é declarada e **não verificável no snapshot** (`COMMERCIAL_WINDOW` não
viaja). Fica contada como condição atómica e marcada como não medida — não se apaga uma
condição por não a conseguirmos ver.

> **CONTAR AS CONDIÇÕES DE UMA REGRA É MEDIÇÃO, NÃO NARRAÇÃO.**
> As duas contagens de D0.4 eram narração. Nenhuma sobreviveu à medição.

## §5 · PLACAR EPISTEMOLÓGICO

```
SYNTHETIC_SCENARIOS .............. 11
SCENARIOS_PASS ................... 11
RULES_DECLARED ................... 9    C1 C2 C3 C3b C4 C5 C6 C7 C8
RULES_EXERCISED_BY_REJECTION ..... 6    C1 C3 C3b C5 C7 C8
RULES_NOT_EXERCISED .............. 3    C2 C4 C6
C3_RUNTIME_STATE ................. KNOWN_VIOLATION
```

`C2`, `C4` e `C6` **não foram provadas**. Nenhum cenário as obrigou a recusar coisa
alguma. Não são regras erradas — são regras **por testar**, e ficam assim declaradas até
que um cenário as exercite.

## §6 · TESTE DE INDEPENDÊNCIA

Nos 43, `SALES_READY == PUBLISHABLE == EXTERNAL_YES`. Forçada a divergência sintética:

```
✅ ACEITA        SALES_READY=YES + PUBLICATION=VALIDATION_REQUIRED
                 os três valores permanecem DISTINTOS — nenhum foi «corrigido»
✅ RECUSA        EXTERNAL=YES + PUBLICATION=VALIDATION_REQUIRED           (C5)
✅ NÃO CODIFICA  SALES_READY == PUBLISHABLE como regra
```

**O contrato não aprendeu a igualdade dos 43.** É `L-37 · OBSERVED SET EQUALITY ≠
SEMANTIC IDENTITY`, verificada por mutação em vez de prometida.

## §7 · LIMITAÇÕES DECLARADAS

1. As nove regras são **propostas desta missão**, não leis do runtime. Nenhuma corre em
   produção e nenhuma foi aplicada a nada.
2. `C3` está **violada hoje** pelo próprio sistema (`RR-01`), com testemunha em §2.
   `RT-09` mostra que o contrato **recusaria** o que o runtime **faz**. A distância entre
   os dois é a dívida, não a prova.
3. `C2`, `C4` e `C6` estão declaradas e **não exercitadas** (§5).
4. `JANELA_COMERCIAL` é contada e **não medida** — `COMMERCIAL_WINDOW` não viaja no
   snapshot.
5. Os onze cenários não esgotam o espaço. Cobrem as combinações que as missões nomearam.
