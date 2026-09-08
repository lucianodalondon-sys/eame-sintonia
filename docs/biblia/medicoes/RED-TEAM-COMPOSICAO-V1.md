# RED TEAM DO CONTRATO DE COMPOSIÇÃO — D0.4

```
DOCUMENT_TYPE   RED TEAM · casos sintéticos de contrato
DATE            2026-09-08
SCRIPT          testar_contrato_composicao.py   READ-ONLY · exit 1 se falhar
DADOS           RED-TEAM-COMPOSICAO-V1.json
RESULTADO       PASS · 8/8 casos · 3/3 testes de independência
```

> ⚠️ **`SYNTHETIC_CONTRACT_TEST ≠ OBSERVED CASE`.**
> Os oito casos abaixo **não existem no mundo**. Testam a arquitetura, nunca são
> evidência, **nunca somam aos 43** e nunca se publicam como dado.

## §1 · RECUPERABILIDADE DO ESTADO TEMPORAL

Reexecutada a lei do dono real (`fb96f49d::estado_de_acao`) sobre os campos que o
snapshot **já persiste**:

```
casos não sobrescritos que reproduzem exatamente ....... 34 / 34
os 9 TO_VALIDATE recuperam um estado temporal .......... 9 / 9
valor recuperado ....................................... WATCH em 9/9

TEMPORAL_STATE_AFTER_OVERRIDE = RECOVERABLE_BY_RE_EXECUTION
                                NOT_PERSISTED_AS_FIELD
```

**A informação não se perdeu nesta safra — mas não está no campo.**
E a recuperação exige **reexecutar a lei**, o que `L-32` proíbe ao casco.

## §2 · OS OITO CASOS

| id | cenário | contrato | regra que decidiu |
|---|---|---|---|
| `RT-01` | oportunidade acionável, publicação bloqueada | **ACEITE** | nenhuma violação — «é oportunidade» sobrevive sem publicar |
| `RT-02` | publicável internamente, brief externo negado | **ACEITE** | `C5` permite externo MAIS restritivo |
| `RT-03` | urgência tenta promover `RADAR` a `OPPORTUNITY` | **ACEITE, sem promoção** | `C1` — a elegibilidade **não muda**; a urgência convive |
| `RT-04` | prioridade alta tenta tornar futuro em agora | **ACEITE, sem promoção** | `C1`+`C6` — o rótulo continua `PREPARAR` |
| `RT-05` | sinal recente tenta virar janela aberta | **RECUSADO** | `C7` · `TIME SINCE ≠ TIME UNTIL` |
| `RT-06` | card existe com timing `UNKNOWN` | **ACEITE** | `C6` — pode existir sem inventar timing |
| `RT-07` | material para terceiro com `EXTERNAL = UNKNOWN` | **RECUSADO** | `C8` — **regra criada pelo red team** |
| `RT-08` | `EXTERNAL = YES` sobre publicação negada | **RECUSADO** | `C5` · `EXTERNAL ⊆ PUBLICATION` |

### O buraco que o red team encontrou no próprio contrato

**`RT-07` passou na primeira execução — e passou errado.** Nenhuma regra o cobria, e a
ausência de proibição foi lida como permissão.

> **UM CONTRATO QUE ACEITA POR OMISSÃO NÃO É UM CONTRATO. É UM SILÊNCIO.**

`C8 · só EXTERNAL=YES autoriza material para terceiro` nasceu daí, e fica registado que
nasceu do red team e não da primeira escrita. **`UNKNOWN NÃO É PERMISSÃO`.**

### Sobre `RT-03` e `RT-04` — por que «aceite» é a resposta certa

Ambos foram desenhados esperando **NÃO**. O contrato aceita-os — **e não promove**.
A distinção é o ponto: o contrato **não recusa a combinação**; recusa a **promoção**.
Um caso `RADAR` com janela aberta é um facto legítimo, e apagá-lo seria perder
informação. O que ele não pode é virar `OPPORTUNITY`.

> **RECUSAR A PROMOÇÃO NÃO É RECUSAR O ESTADO.**

## §3 · TESTE DE INDEPENDÊNCIA

Nos 43, `SALES_READY == PUBLISHABLE == EXTERNAL_YES`. Forçada a divergência sintética:

```
✅ ACEITA      SALES_READY=YES  +  PUBLICATION=VALIDATION_REQUIRED
               os três valores permanecem DISTINTOS — nenhum foi «corrigido»
✅ RECUSA      EXTERNAL=YES     +  PUBLICATION=VALIDATION_REQUIRED     (C5)
✅ NÃO CODIFICA  SALES_READY == PUBLISHABLE como regra
```

**O contrato não aprendeu a igualdade dos 43.** É `L-37 · OBSERVED SET EQUALITY ≠
SEMANTIC IDENTITY`, verificada por mutação em vez de prometida.

## §4 · LIMITAÇÕES DECLARADAS

1. As oito regras são **propostas desta missão**, não leis do runtime. Nenhuma corre em
   produção e nenhuma foi aplicada a nada.
2. `C3` está **violada hoje** pelo próprio sistema (`RR-01`). O teste passa porque o caso
   sintético não exercita o override — **o red team não pode reprovar o que não simula**.
3. Os oito casos não esgotam o espaço. Cobrem as combinações que a missão nomeou.
