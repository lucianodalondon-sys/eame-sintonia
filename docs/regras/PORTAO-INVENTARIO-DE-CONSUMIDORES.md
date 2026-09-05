# PORTÃO — INVENTÁRIO DE CONSUMIDORES ANTES DE MUDANÇA SEMÂNTICA

```
CONSUMER_INVENTORY_BEFORE_SEMANTIC_CHANGE = BLOCKING_GATE
```

**Estado:** LEI PERMANENTE · **Vale a partir de:** P0.2 passo 02 · **Origem:** correção do passo 01.

---

## Por que esta lei existe

No passo 01 eu lancei o inventário de consumidores **em paralelo** com o merge e selei antes
de ele terminar. Escrevi `CONSUMERS_REQUIRING_MIGRATION = nenhum bloqueante` como se fosse
medido. Não era — era inferido de os testes passarem.

A conclusão acabou por coincidir com a verdade. **Isso foi sorte, não método.** O inventário,
quando chegou, tinha encontrado 21 + 13 consumidores que exigem cultura única, um deles pondo
o campo dentro de um digest `sha256` e outro sendo o estrangulamento de um subsistema inteiro.

Se a coincidência não tivesse acontecido, o merge estaria selado sobre uma afirmação inventada.

## Quando o portão dispara

Qualquer enxerto que altere:

- **significado** de campo · **cardinalidade** · **enum** · **contrato**
- **formato consumido**
- **chave usada em gate, digest ou KPI**

## O que responder — obrigatoriamente, ANTES do commit de merge

```
DIRECT_CONSUMERS             =
INDIRECT_REACHABLE_CONSUMERS =
SINGLE_VALUE_CONSUMERS       =
BLOCKING_REACHABLE_CONSUMERS =
FUTURE_MIGRATION_RISKS       =
```

| resultado | ação |
|---|---|
| `BLOCKING_REACHABLE_CONSUMERS > 0` | **PARE**, ou migre esses consumidores **dentro do mesmo escopo** |
| `BLOCKING_REACHABLE_CONSUMERS = 0` | só então o merge pode ser selado |

## As duas proibições

> **1. Não rodar o inventário em paralelo com o selo.** Ele termina primeiro. Sempre.
>
> **2. "Nenhum bloqueante" NUNCA pode ser inferido de os testes passarem.** Teste verde prova
> que o que está coberto não quebrou; não prova que o consumidor não coberto não vai quebrar
> em silêncio. O consumidor mais perigoso é exatamente o que não tem teste.

Consumidor hoje inalcançável **não é consumidor seguro** — é `FUTURE_MIGRATION_RISK`, e fica
registado com endereço, para o dia em que passar a alcançar.

---

## REGISTO DE `FUTURE_MIGRATION_RISK` — semeado pelo passo 01 (CROP)

Nenhum destes recebe `MULTI:` hoje: os produtores gravam em `IT-VOZ-AUDIO-V2/` e `IT-VIDEO-V1/`,
e estes leem outras fontes. No dia em que um deles ler esses caminhos, quebra.

### Os que quebram em SILÊNCIO — os caros

| consumidor | como falha |
|---|---|
| `v21_normalizar.py:155` `crop_id()` | **o pior.** Não levanta exceção, não regista nada, devolve sempre UM id. Medido executando a função real: `crop_id('AMBIGUOUS:OLIVO_IT+VITE')` → `'CROP_OLIVE'`; `crop_id('VITE+OLIVO')` → `'CROP_OLIVE'`. `_n()` reduz `:` e `+` a espaços e `_casa()` elege o **apelido mais longo**. Duas culturas entram, uma sai, e quem sai é decidido por comprimento de string. É o estrangulamento de todo o v21. |
| `pacote_montar.py:115` | `crop[:4]` → `'MULT'` não casa nada; `rel_win`/`rel_news` ficam vazios sem erro |
| `it_rotulo_selar_v2.py:55` | CROP como chave de dict alimentando `LABELS_PER_CROP_OLD/NEW` e o gate `NO_CROP_REGRESSION` — um MULTI cria cultura fantasma e o gate acusa **perda falsa** |
| `territorial_medir.py:98` | já normaliza escalar-ou-lista, mas **não trata o prefixo** — leria `'MULTI:A+B'` como uma cultura chamada `MULTI:A+B` |

### Os que quebram com barulho

`it_rotulo_testemunha.py:27` (CROP dentro de um digest `sha256`) · `catalogo_importar.py:227`
e `it_pairset_propagar.py:83` (CROP em chave de tuplo — e esta última é a chave
`(CROP_ID, ISSUE_ID)` **das 43 oportunidades canónicas**) · `radar_v21.py:271`
(`== 'OLIVO'`, KPI impresso) · `adama_es_gate.py:689` · `pacote_relacoes_convergencia.py:195`
· `v2_cruzamentos.py:110` · `it_portfolio_v3.py:51` · `it_divida_fila.py:119` ·
`it_divida_consolidar.py:59` · `it_rotulo_parser.py:1111` · `it_rotulo_avaliar.py:44` ·
`linkedin_sensores.py:126`

### O que já convive com pluralidade — o precedente

E este é o argumento mais forte a favor da D1: **a casa já tinha CROP plural.**

- `data/samples/ES-T5-002-corpus-documentos.json` — `CROP` e `ISSUE` são **listas** em 1.771
  documentos; **119 já têm duas ou mais culturas**
- `tests/test_coleta_externa.py:470` — `assertIsInstance(d['CROP'], list)`: o contrato já é tipado como lista
- `comunicacao_classificar.py:171` · `sensor_territorial.py:333` · `territorial_documentos.py:175` — escrevem sempre lista
- `it_inventario.py:74` `marcas()` — devolve todas as ocorrências com evidência, escrito
  explicitamente como remendo porque `marcar_assunto` parava na primeira

A D1 não introduziu pluralidade no sistema. **Ela alinhou a regra canónica com o que quatro
camadas já faziam sozinhas.**
