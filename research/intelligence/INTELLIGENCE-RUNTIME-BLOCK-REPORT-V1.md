# POR QUE O RUNTIME DA INTELLIGENCE NÃO COMEÇOU — C-CTRL-INT-NIGHT-02

```text
MISSAO        C-CTRL-INT-NIGHT-02
BRANCH        claude/control-plane-intelligence-night-v2
DATA          2026-09-14
GATE_A        PASS    PORTAO_DO_CONTROLE=PASS · 23 provas
GATE_B        PASS    BIBLE_PROMOTED=YES · 9/9 gates
GATE_C        BLOCKED
```

> **A Bíblia é canônica desde hoje. Isso mudou quem é a lei — não mudou o que a
> máquina consegue fazer.**
>
> `PROMOVER A LEI ≠ AUTORIZAR A OBRA.`

Esta missão passou o Gate A e o Gate B e parou no C. Não parou por falta de
tempo, nem de máquina, nem de desenho: parou porque **dois contratos canônicos,
ambos nesta árvore, proíbem-no hoje** — e nenhum dos dois é meu para abrir.

---

# 1 · O PRIMEIRO BLOQUEIO — A TRAVA DA INTELIGÊNCIA

`docs/operacao/TRAVA-DA-INTELIGENCIA.json` · `SCHEMA: TRAVA_DA_INTELIGENCIA/2`

```text
REGRA    COLLECTION_FOUNDATION_CLOSED != SIM  →  INTELLIGENCE_IMPLEMENTATION_BLOCKED
```

E o que ela bloqueia está escrito, à letra, no próprio contrato:

```text
O_QUE_A_TRAVA_IMPEDE
  · desenvolvimento NOVO de inteligencia
  · ligar sinais
  · pontuacao e recomendacao
  · alimentar o portal com dado de inteligencia
  · ativar Field Voices ou Opportunity Radar
```

As duas primeiras linhas são, palavra por palavra, a Parte VI desta missão.

## 1.1 · Medido hoje, não herdado do contrato

O contrato declara `COLLECTION_FOUNDATION_CLOSED: "NAO"` com `MEDIDO_EM:
2026-09-08`. Acreditar nesse campo seria herdar uma fotografia — o erro que esta
casa já cometeu quatro missões seguidas. Ele aponta onde se mede, e foi lá que se
mediu: `system-map/data/estradas-it.generated.json`, nesta árvore, hoje.

| | medido hoje |
|---|---|
| `ROUTE_CLASSES_MODELED` | 12 |
| `ROUTE_CLASSES_ARCHITECTURE_CLOSED` | **0** |
| `ROUTE_CLASSES_OBSERVED` | 2 — `RC-1`, `RC-2` |
| `ROUTE_CLASSES_DB_TESTED` | 1 — `RC-5` |
| `ROUTE_CLASSES_BLOCKED` | 3 — `RC-6`, `RC-7`, `RC-8` |
| `ROUTE_CLASSES_REQUIRED_TOTAL` | **UNKNOWN** |

E a razão do `UNKNOWN`, escrita pelo próprio censo:

> *23 fonte(s) sem rota conhecida. Até a M1 provar, nenhuma delas garante caber
> nas 12 classes modeladas.*

A condição de destrave exige **as cinco ao mesmo tempo**, e falham três:

| condição | hoje |
|---|---|
| os 14 critérios A..N cumpridos | **9 em falta** — A, B, E, G, H, I, J, M, N |
| nenhuma classe NECESSÁRIA em `UNKNOWN` | **falha** |
| nenhuma classe NECESSÁRIA em `OPEN` | **falha** — 0 de 12 fechadas |
| nenhuma `BLOCKED` sem decisão escrita | as 3 têm razão escrita ✔ |
| `ROUTE_CLASSES_REQUIRED_TOTAL` deixou de ser NÃO SEI | **falha** |

O próprio contrato explica por que a última é a que manda:

> *enquanto não se souber quantas estradas são precisas, «todas as necessárias
> estão fechadas» é uma frase sobre um conjunto que ninguém conhece.*

## 1.2 · O que a trava **não** impede, e foi usado

```text
· ler o codigo de inteligencia que ja exista
· preservar historico e documentos
· corrigir um defeito que ameace dados
· medir o que a inteligencia futura vai esperar da coleta
```

A quarta linha é a licença desta missão para medir a Sala de Espera, re-medir a
fronteira READY e provar os dois bloqueios. Foi só isso que se fez do lado da
Intelligence — nenhuma linha de runtime.

---

# 2 · O SEGUNDO BLOQUEIO — A PRÓPRIA BÍBLIA QUE ACABOU DE SER PROMOVIDA

A secção 32, `PRIMEIRA MISSÃO APÓS PROMOÇÃO`, fixa o gate da primeira execução:

```text
ONE REAL WAITING_ROOM ITEM
→ UPSTREAM CLAIM/FACT IDENTITY PRESERVED
→ ONE IDENTIFIED INTELLIGENCE_RUN
→ PROVEN INPUT LINEAGE
```

Medido hoje, pelo dono canônico da Sala (`admissao/sala_de_espera.py`):

```text
MORADA   data/samples/PRONTO-PARA-INTELIGENCIA/
EXISTE   NAO — a pasta nem chegou a ser criada
CORRIDAS 0
ITENS    0
```

**`REAL_ITALY_READY_ITEMS = 0`.** Existem 17 pastas de amostra `IT-*`, e nenhuma
atravessou a admissão. Um `INTELLIGENCE_RUN` construído hoje correria sobre zero
itens reais — e um runtime provado só com fixtures, num projeto que separa
`DECLARED ≠ OBSERVED`, é um runtime `DEFINED`, nunca `OBSERVED`.

> A Bíblia promovida pede **um item real**. A Sala tem zero. O gate é dela, não
> meu, e não se satisfaz com uma fixture.

---

# 3 · O QUE **NÃO** FOI FEITO, E PORQUÊ NÃO FOI

Nada disto aconteceu, e nenhuma das ausências é esquecimento:

| | |
|---|---|
| `inteligencia/` ou qualquer módulo de runtime | a trava impede desenvolvimento NOVO |
| `INTELLIGENCE_RUN` produtivo | idem, e a §32 não tem item real para consumir |
| ligar sinais, crossing, hipótese, finding | «ligar sinais» está na lista do que a trava impede |
| migração, tabela, persistência de run | não há runtime para persistir |
| casos A–H da Itália | dependem do runtime |
| RT01–RT30 do runtime | dependem do runtime |
| mutação / concorrência / crash do runtime | dependem do runtime |

E — importante — **nada foi contornado**:

```text
--fixar usado para calar o portao         NAO   (usado uma vez, para BAIXAR o teto)
teto de divida levantado                  NAO   (2->0 e 6->5->4; nenhum subiu)
teste afrouxado                           NAO   (5 mutacoes provam que mordem)
ponteiro quebrado marcado como ignorado   NAO   (foi separado em tres erros reais)
documento registado so para zerar contador NAO  (zero dos dez era autoridade)
owner inventado                           NAO
trava contornada                          NAO
```

---

# 4 · A DECISÃO QUE FALTA, E DE QUEM ELA É

```text
DECISION_REQUIRED  = SIM
DE_QUEM            = frente COLLECTION (não Intelligence, não Control Plane)
BLOQUEIA           = GATE C e tudo a jusante
NAO_BLOQUEIA       = Gate A, Gate B, System Map, regressão, know-how
```

## Opção 1 — fechar a fundação da coleta *(recomendada)*

Pagar os 9 critérios em falta e responder à pergunta que trava tudo:
`ROUTE_CLASSES_REQUIRED_TOTAL`. O gargalo medido é único e nomeado: **23 fontes
sem rota conhecida**.

- **consequência** — a trava abre sozinha, por regra objetiva, sem ninguém a
  decidir abri-la. É a única porta que não deixa dívida atrás.
- **custo** — `UNKNOWN`. Não foi medido nesta missão, e escrever «pequeno» por
  ausência de medição seria inventar.

## Opção 2 — decidir que `RC-1` sozinha basta para a Itália

Declarar que a Itália V1 precisa apenas de `OFFICIAL_HTTP_DOCUMENT`, fechar
`RC-1` (faltam-lhe `STRUCTURED` e `ADMISSION`), e fixar
`ROUTE_CLASSES_REQUIRED_TOTAL = 1`.

- **consequência** — destrava muito mais cedo, **e** é exatamente o atalho que a
  versão 1 da trava permitia e a versão 2 fechou por escrito: *«uma estrada
  fechada de sete destrancaria as sete. Isso não é fechar a fundação: é fechar um
  caminho e chamar-lhe fundação.»* Só é legítimo com decisão humana escrita que
  assuma que as outras 11 classes não são necessárias para a Itália.

## Opção 3 — manter a trava fechada e não construir runtime

- **consequência** — o estado de hoje. A Bíblia canônica fica a governar código
  que ainda não existe, o que é o estado correto de uma constituição recém
  promovida — e não custa nada.

**Recomendação: 1.** A 2 só depois de alguém responder, por escrito, «quantas
estradas a Itália precisa», que é precisamente a pergunta que hoje é `NÃO SEI`.

---

# 5 · O QUE ESTA MISSÃO DEIXA PRONTO PARA O DIA DO DESTRAVE

| | |
|---|---|
| a lei | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` — **CANONICAL**, 9/9 |
| a espinha executável | `provas/espinha_da_intelligence.py` + 39 provas |
| os donos dos conceitos | `INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json` — 32, 0 conflitos |
| a fronteira de entrada | `admissao.pronto_para_inteligencia()` — 12 campos, medida |
| o dono da Sala | `admissao/sala_de_espera.py` — morada, escrita atómica, idempotência |
| o Control Plane | `PORTAO_DO_CONTROLE=PASS` · 23 provas · chão nesta linhagem |

O que falta para o runtime nascer não é desenho. É **um item real na Sala** e uma
**fundação fechada**.

---

# 6 · PROVAS

```bash
python3 -m unittest tests.test_o_controle_separa_lei_de_mencao   # 47, classe R_
python3 -m unittest tests.test_trava_da_inteligencia             # a trava, 21
python3 controle/portao_do_controle.py                           # PASS · 23
python3 system-map/scripts/validate_system_map.py                # PASS
```

`tests/test_o_controle_separa_lei_de_mencao.py::R_` mede os dois bloqueios
**hoje**, nunca lendo o campo que a própria trava declara sobre si. No dia em que
a fundação fechar ou um item real pousar na Sala, essas provas mudam de resposta —
e é aí, e só aí, que o Gate C abre.
