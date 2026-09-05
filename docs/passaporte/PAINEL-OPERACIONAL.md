# PAINEL OPERACIONAL DO PASSAPORTE

**Data:** 2026-09-05 · **Dono:** `scripts/passaporte_painel.py` ·
**Saída de máquina:** `data/passaporte/PAINEL.json`

A pergunta que este painel existe para responder é uma só:

> ### "Onde estão as informações que entraram ontem?"

E a resposta tem de sair **sem auditoria manual** — sem abrir arquivo, sem contar linha,
sem perguntar a ninguém.

```bash
python3 scripts/passaporte_painel.py                    # o acervo inteiro
python3 scripts/passaporte_painel.py --em 2026-08-30    # o que entrou naquele dia
python3 scripts/passaporte_painel.py --colecao VOICE_ES
python3 scripts/passaporte_painel.py --json
```

Tudo é derivado do log de eventos no momento da execução. O painel não guarda estado
próprio: o que ele grava são **contagens**, e há teste que compara o gravado com o
derivado agora.

---

## AS TRÊS SEÇÕES

### COLETA — a primeira peneira

```
TOTAL      2.960
PASS       2.005      material tecnicamente utilizável
DEFER        930      não utilizável AINDA — nunca reprovação
REJECT        25      julgamento declarado, com evidência por item
ERROR          0
```

`TOTAL = PASS + DEFER + REJECT + ERROR`. Se não fechar, `GATE = FAIL`.

### INTELIGÊNCIA — onde o trabalho parou

```
CONTENT_AVAILABLE                 2.030
CONTENT_READ                         22
CONTENT_LEXICALLY_SCANNED_ONLY    1.966   ← linha PRÓPRIA, nunca somada a READ
CLAIMS_PENDING                    2.938
IDENTITY_PENDING                  2.294
GEOGRAPHY_PENDING                 2.427
ROUTING_PENDING                   2.944
```

**`CONTENT_LEXICALLY_SCANNED_ONLY` tem linha própria de propósito.** Somá-la a
`CONTENT_READ` seria repetir, em forma de painel, o erro que criou o incidente dos
1.005.157 caracteres.

### CONSUMO — a inteligência tem consumidor?

```
VALID_INTELLIGENCE                   22
CONSUMED_BY_1_PLUS_CAPABILITY        16
READY_NOT_CONSUMED                    0
ORPHAN_INTELLIGENCE                   6
```

`22 = 16 + 0 + 6`. Nenhuma inteligência válida com estado de consumo desconhecido — é
portão, não meta.

---

## AS SEIS FILAS DE DÍVIDA

Uma dívida é um par de estados que, junto, denuncia trabalho comprado e não usado. Não é
alerta nem exceção: é uma **fila, com nome**, e ela existe até alguém resolvê-la.

| fila | condição | hoje |
|---|---|---:|
| `TRANSCRIPT_AVAILABLE_NOT_READ` | transcrição disponível e não lida | **30** |
| `CONTENT_AVAILABLE_NOT_READ` | qualquer conteúdo disponível e não lido | 2.008 |
| `READ_WITHOUT_CLAIM` | lido e sem claim extraído | 0 |
| `CLAIMS_WITHOUT_ROUTING` | claim extraído e sem rota | 6 |
| `ROUTED_NOT_CONSUMED` | roteado e sem consumidor | 0 |
| `ORPHAN_INTELLIGENCE` | inteligência válida sem nenhuma rota relevante | 6 |

A primeira fila é a do incidente, separada da geral de propósito: era ela que não existia,
e é ela que precisa ser lida em voz alta toda vez.

---

## ONDE ESTÃO — estágio atual × motivo

A resposta direta à pergunta do topo. Todo item aparece exatamente uma vez.

```
INTELLIGENCE_READING · CONTENT_NOT_PROCESSED    1.983
CONTENT_ACQUISITION  · TRANSCRIPT_PENDING         863
CONTENT_ACQUISITION  · CONTENT_NOT_AVAILABLE       67
INTELLIGENCE_READING · FALSE_POSITIVE              25
CONSUMPTION          · —                           12
NORMALIZATION        · NORMALIZATION_PENDING        6
ROUTING              · NOT_ROUTED                   4
```

E filtrado pelo dia em que a informação entrou — `--em 2026-08-30`, o piloto de sensores:

```
INTELLIGENCE_READING · CONTENT_NOT_PROCESSED    1.033
CONTENT_ACQUISITION  · TRANSCRIPT_PENDING         391
CONTENT_ACQUISITION  · CONTENT_NOT_AVAILABLE       55
INTELLIGENCE_READING · FALSE_POSITIVE              25
```

Nenhum item aparece sem motivo. **Ausência de próximo selo nunca significa reprovação** —
significa que existe uma próxima ação, e ela tem nome.
