# A V11.2 na entrada — a coleta nova chega sozinha até ela?

```
AUTOMÁTICO_NA_COLETA_NOVA = SIM
BACKFILL_DO_ACERVO        = SIM
```

Nenhuma das duas respostas veio de leitura de código. Vieram de pôr um registro
novo na porta real da coleta, rodar a cadeia real e olhar o que saiu do outro
lado — duas vezes, porque a primeira execução se acusou de um resíduo que era
dela mesma.

    UM REGISTRO QUE ENTRA POR UMA PORTA ESPECIAL PROVA A PORTA ESPECIAL.

---

## 1 · A porta real

| | |
|---|---|
| porta | `build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json`, família `CURRENT_FIELD_SIGNALS` |
| versionada? | **sim** — 110 arquivos de `build/ITALY-REALITY-HANDOFF-V2/` estão no git; só a **saída** `V2.1/` é ignorada |
| quem a lê | `scripts/v21_ingest_b.py`, passo **1** de `scripts/v21_cadeia.sh` |
| quem chama o motor | `scripts/v21_cadeia.sh`, passo **5e** — e **mais ninguém** |

Foi por essa porta que entraram os 49 sinais de last-mile que já estão no
acervo. A testemunha não abriu porta nova: usou essa.

`grep -rn v21_oportunidades.py` no repositório inteiro devolve **um** chamador
executável: a linha 93 da cadeia. Não há segundo motor, não há cópia da regra
rodando em paralelo. `T28` pina isso e quebra se alguém criar um segundo dono ou
mover o motor para antes da porta.

---

## 2 · A fixture, e o que ela foi desenhada para pegar

Um boletim fictício, no **Piemonte**, videira, com duas orações:

1. `Vite/botrite: intervir em pre-colheita com Fenhexamid.` — um alvo só.
2. `Suspensao de oidio, fim da defesa de tignoletta e de peronospora nas mesmas
   vinhas.` — **três alvos, uma direção**.

O Piemonte é escolha deliberada: o acervo tem `IT-WIN-003`, videira ×
*Scaphoideus*, **do Piemonte**. Cultura bate. Região bate. **Alvo não bate.**

No comportamento antigo os quatro casos herdariam `IT-WIN-001/002/003` — e os
três alvos da oração corrida receberiam `WINDOW_CONCLUDED`. Se qualquer uma
dessas duas coisas reaparecesse, a coleta nova teria caído no comportamento
antigo, e a testemunha falharia.

---

## 3 · O que a travessia mediu

`python3 scripts/v21_testemunha_de_ingestao.py` → **EXIT 0**

```
BASELINE            BUILD_ID V21-5c847ef25e17f680 · 43 casos
COM A FIXTURE       BUILD_ID V21-ef2ec05f2fc42327 · 47 casos · 4 novos
RESTAURADO          BUILD_ID V21-5c847ef25e17f680 · 43 casos
```

| alvo derivado | NEED_DIRECTION | ambiguidade | janelas herdadas | portões |
|---|---|---|---|---|
| botrite | `POSITIVE_PRESSURE` | — | **nenhuma** | nenhum |
| oídio | `UNKNOWN` | `MULTIPLE_TARGETS_IN_CLAUSE` | **nenhuma** | nenhum |
| tignoletta | `UNKNOWN` | `MULTIPLE_TARGETS_IN_CLAUSE` | **nenhuma** | nenhum |
| peronospora | `UNKNOWN` | `MULTIPLE_TARGETS_IN_CLAUSE` | **nenhuma** | nenhum |

As três provas que a missão pediu, uma a uma:

1. **O derivado recalculou sozinho.** Quatro casos novos apareceram no pacote
   sem que ninguém chamasse `v21_oportunidades.py` à mão. O `BUILD_ID` mudou,
   que é como o pacote diz que o conteúdo de entrada mudou.
2. **A chave de janela da V11.2 valeu para o registro novo.** `IT-WIN-003` bate
   em cultura e em região e mesmo assim não encostou em nenhum dos quatro: o
   alvo não é o dele.
3. **A direção não se repartiu.** A oração de três alvos deu `UNKNOWN` aos três,
   com o motivo gravado; a oração de um alvo só continuou decidindo.

E a quarta, que a missão não pediu mas o repositório exige: **a passagem não
deixou resíduo.** A porta foi restaurada com `git checkout --`, a cadeia rodou
outra vez e o `BUILD_ID` voltou a ser exatamente o de antes. Determinismo
verificado, não afirmado.

> ⚠️ A botrite do Piemonte saiu `SALES_READY`. É fixture — foi removida. Fica
> registrado porque mostra o tamanho do que a ingestão automática faz: um
> boletim novo pode criar um caso vendável no mesmo `bash scripts/v21_cadeia.sh`,
> sem intervenção humana entre a coleta e a régua comercial.

---

## 4 · BACKFILL — por construção, não por script separado

`v21_ingest.py` começa com `shutil.rmtree(OUT)`. A cadeia **apaga a saída e
reconstrói o acervo inteiro** a cada execução: os 43 casos são recalculados
todos, não só o que chegou. Não existe caminho incremental — e por isso não
existe acervo velho com regra velha.

    NÃO HÁ BACKFILL PORQUE NÃO HÁ INCREMENTAL.
    A CADEIA NÃO ATUALIZA O PACOTE: ELA O REFAZ.

A prova está no mesmo experimento: a rodada de restauração aplicou a V11.2 aos
43 casos e devolveu o `BUILD_ID` idêntico ao de antes da fixture. Reprocessar é
o caminho normal, e é o **mesmo** caminho — não um segundo.

---

## 5 · O que a testemunha achou de quebrado no meio do caminho

A primeira execução falhou, e a falha valeu a rodada.

A fixture original declarava `RESSALVA_PERMANENTE`. O registro entrou
perfeitamente — `CLIENT_SAFE: true`, `CROP_IDS: [CROP_GRAPEVINE]`,
`REGION_IDS: [REGION_PIEMONTE]` — e produziu **zero casos**. Motivo:

```python
# scripts/v21_dominio_da_alegacao.py · promover_research
if not r.get('CLIENT_SAFE') or any(r.get(c) for c in TELA):
    return 0            # ← tudo-ou-nada. PERMANENT_CAVEAT está em TELA.
```

Com a ressalva preenchida, **nenhuma** prosa sobe de `RESEARCH`. O boletim chega
ao motor com `WHAT_IT_IS = None` e `INTERVENTION_GUIDANCE = None`: o extrator de
pares não tem texto para ler, e o registro é ignorado — sem erro, sem aviso.

    UM REGISTRO IGNORADO EM SILÊNCIO É PIOR QUE UM RECUSADO EM VOZ ALTA.

**Isto não é hipótese. São 4 boletins REAIS, hoje, no acervo:**

| registro | cultura | região | campos de tela | prosa |
|---|---|---|---|---|
| `IT-CAN-71D68FCB7D` | videira | Veneto | só `PERMANENT_CAVEAT` | só em `RESEARCH.o_que` |
| `IT-CAN-6EFC8DC91A` | oliveira | Veneto | só `PERMANENT_CAVEAT` | idem |
| `IT-CAN-EB63AEC4AA` | oliveira | Campania | só `PERMANENT_CAVEAT` | idem |
| `IT-CAN-49BA29FF51` | oliveira | Lazio | só `PERMANENT_CAVEAT` | idem |

No pacote inteiro são **35 registros client-safe** com `RESEARCH.o_que` e sem
`WHAT_IT_IS` — 4 deles sinais de campo, que é onde o motor lê.

**NÃO foi consertado nesta rodada, de propósito.** A pergunta da missão era se a
V11.2 roda sozinha, e a resposta é sim; mexer no guarda da promoção move texto
para a tela em 35 registros, passa 35 textos novos pela trava de tradução e pode
criar oportunidade — é decisão de vocês, não efeito colateral de uma testemunha.
O comportamento atual está **pinado** em `T26`, que quebra na hora se alguém o
mudar sem querer.

A correção mínima, quando for a hora, é uma linha: trocar o `return 0`
tudo-ou-nada pela guarda que já existe campo a campo (`if res.get(origem) and
not r.get(destino)`).

---

## 6 · Onde o formato antigo ainda vive — e por que não mexi

`scripts/v21_crossings.py` (passo 2 da mesma cadeia) monta
`COMPETITOR_X_CROP_WINDOW_X_PORTFOLIO` com um índice de janelas **por cultura
só**. Medido no pacote de hoje:

```
XCR_COMPETITOR_X_CROP__GRAPEVINE
   WINDOW: ["IT-WIN-001", "IT-WIN-002", "IT-WIN-003", "IT-WIN-004"]
```

Quatro janelas de *Scaphoideus* — Veneto, Lombardia, Piemonte, Trentino — ao
lado de uma comunicação de concorrente sobre videira que não declara alvo nem
região.

**Isto NÃO é uma oportunidade e o próprio arquivo diz isso**, no corpo que ele
grava:

> `CROSSING NAO E OPPORTUNITY. E a constatacao de que duas camadas falam do
> mesmo CROP_ID.`
> `JOIN_METHOD: IDs normalizados exatos (CROP_ID).`

O cruzamento declara a chave que usa e a afirmação que faz. Aplicar
`janela_vale` ali — com alvo e região ausentes — apagaria os dois cruzamentos
inteiros, e apagaria uma frase que é verdadeira no nível da cultura: videira
**tem** janela declarada. Trocar uma regra honesta por outra e perder informação
verdadeira no caminho não é conserto.

Fica como **item aberto nomeado, não como conserto silencioso**: se a decisão for
que um cruzamento também não pode citar janela sem dizer de qual alvo e de qual
região ela é, isso é uma missão, com regressão própria.

---

## 7 · Testes que passam a segurar isto

| teste | o que fixa |
|---|---|
| `T25` | o registro novo chega ao extrator **com texto** |
| `T26` | pina o silêncio da ressalva permanente — quebra se alguém mudar sem medir |
| `T27` | a V11.2 (direção + chave de janela) vale para o registro novo, pelas funções reais da ingestão |
| `T28` | o motor tem **um** chamador, e ele roda **depois** da porta |
| `T29` | confere o que a travessia completa mediu (`FALHAS == []`, sem resíduo, sem janela herdada) |

`T25` a `T27` percorrem `do_lastmile` → `promover_research` → `pares_observados`
→ `janela_vale`: as funções reais, na ordem real. Não é uma cópia da regra.
A travessia com a cadeia inteira é o script; o teste rápido confere o medido.

Suíte: **720 descobertos · 715 executados · 6 falhas · 2 erros** — as mesmas 8
de sempre, todas anteriores a esta linha de missões. Provas da camada: **57/57**.

---

## Resposta

```
AUTOMÁTICO_NA_COLETA_NOVA = SIM
BACKFILL_DO_ACERVO        = SIM

porta       build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json (versionada)
motor       scripts/v21_cadeia.sh passo 5e — chamador único
backfill    a cadeia apaga a saída e refaz o acervo inteiro: não há incremental
testemunha  scripts/v21_testemunha_de_ingestao.py → EXIT 0

ABERTO 1  promover_research é tudo-ou-nada: 4 boletins reais chegam ao motor
          sem texto. Medido, pinado em T26, NÃO consertado.
ABERTO 2  v21_crossings.py ainda indexa janela por cultura só — declara a
          chave, não produz oportunidade. Nomeado, NÃO alterado.

motor comercial alterado = NÃO   thresholds = NÃO
portal/casco = NÃO               merge = NÃO      publicação = NÃO
```
