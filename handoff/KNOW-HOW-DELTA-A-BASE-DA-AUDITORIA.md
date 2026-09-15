# DELTA PARA O KNOW-HOW CANÓNICO — A BASE DA AUDITORIA, E O QUE A MISSÃO ANTERIOR APRENDEU SOBRE A ÁRVORE ERRADA

```
ORIGEM            C-SYSTEM-MAP-CURRENT-COLLECTION-TRUTH-V2
BRANCH            claude/system-map-current-collection-truth-v2
BASE FUNCIONAL    claude/sala-persistente-preflight-real-v1 @ 12c919af
KNOW_HOW_MEDIDO   claude/sintonia-eame-know-how-v1 @ d64d8124   (medido 2026-09-14)
ÚLTIMA SECÇÃO     §116.6   (medida agora, não herdada)
NÚMERO DESTA      **por atribuir** — quem integrar escolhe o primeiro livre
```

> **⚠️ ESTE DELTA REVÊ O ANTERIOR ANTES DE O DEIXAR ENTRAR.**
> `handoff/KNOW-HOW-DELTA-A-TRAVESSIA-OBSERVADA.md` **não aterrou** (medido em
> `d64d8124`: as frases-chave dele têm zero ocorrências). Isso foi **sorte**: ele
> traz sete leis duráveis **e** uma afirmação que hoje é falsa. Quem integrar
> aplica este ficheiro, e não aquele sozinho.

---

## PRIMEIRO: O QUE DO DELTA ANTERIOR AINDA É VERDADE

Cada lei foi **re-medida** contra a Collection atual (`12c919af`), que é outra
árvore — outro código, outros recibos, outro estado.

| lei do delta anterior | veredito | como se re-mediu |
|---|---|---|
| `ZERO POR OMISSÃO NÃO É PRUDÊNCIA` | **DURÁVEL — confirmada duas vezes** | o mesmo defeito reapareceu noutra forma: o mapa não lia `pedido*.observado.json`, e publicava a estrada canónica como se ninguém a tivesse percorrido |
| `O EXECUTOR QUE SE ESCOLHE POR TABELA NÃO APARECE A QUEM SÓ LÊ import` | **DURÁVEL — reforçada** | aqui o padrão é ainda mais forte: `scrap_registo.py` é um registo a sério, com seis adaptadores a auto-registarem-se. 36 capacidades que nenhum casador de `import` alcança |
| `UMA CORRIDA PROVA QUE ACONTECEU; NÃO PROVA QUE HÁ LINHA QUE A PERMITE` | **DURÁVEL** | as oito arestas `OBSERVED` desta árvore saem com `CODE = UNKNOWN`, e está certo |
| `UMA ENTRADA EXTERNA NÃO É UM BURACO` | **DURÁVEL** | seis cartões `EXTERNAL_ENTRY` nesta árvore, cada um com a prova do `on:` ao lado |
| `UM ATAQUE QUE APANHA O CASO BOM ENCONTROU UM ERRO SEU` | **DURÁVEL — e cobrou-se outra vez** | o ataque 25 desta missão sobreviveu por medir a árvore errada. A lei apanhou o seu próprio autor, de novo |
| `UM CENSO ESCRITO À MÃO É UMA FOTOGRAFIA` | **DURÁVEL — e pagou-se sozinha** | o censo derivado regenerou-se de 64 para **69** cartões sem ninguém lhe tocar. Se fosse um relatório, continuaria a dizer 64 |
| `UM MAPA PODE ESTAR CERTO E DESCREVER UM SISTEMA QUE JÁ NÃO EXISTE` | **DURÁVEL — e agora é uma guarda** | ver abaixo |

---

## E O QUE DELE **NÃO** PODE ENTRAR

O delta anterior é, em parte, uma **fotografia de uma árvore que já não existe**.
Estas frases estavam certas quando foram escritas e estão **erradas hoje**:

```
❌ «READY continua a NUNCA ter sido produzido»
❌ «a única rota forward provada é corrida só pela sua própria prova»
❌ «ENTRADA → PEDIDO e PEDIDO → ORQUESTRADOR estão CORTADOS»
❌ 64 cartões · 822 commits atrás · 5 arestas observadas
```

Medido na Collection atual:

```
✓ READY FOI produzido, e chegou à Sala:
  RUN IT-T4-2026-09-13-035053 · CANONICAL_E2E = PASS · 11/11 etapas
  REQUEST → ORCHESTRATOR → EXECUTOR → RUN → RAW → STORAGE → DERIVED →
  STRUCTURED → ADMISSION → READY → SALA
  e o ficheiro da Sala tem nome.

✓ PEDIDO → ORQUESTRADOR → EXECUTOR está OBSERVADO, sob um pedido real.
✓ 69 cartões.
```

**A LEI QUE ISTO ENSINA, e é a razão de este delta rever o outro:**

```
UM APRENDIZADO SOBRE UMA ÁRVORE TEM DUAS METADES:
A LEI, QUE DURA — E O NÚMERO, QUE ENVELHECE NA NOITE SEGUINTE.
Aterrar as duas juntas é plantar uma mentira com data marcada.
```

Um delta de know-how deve separar as duas **no próprio ficheiro**, e não deixar
essa separação para quem integra três dias depois.

---

## A LEI NOVA — `MAP CURRENT != SYSTEM CURRENT`

A missão anterior auditou 64 cartões com rigor total: validador verde, 22
guardas verdes, red team a zero sobreviventes, censo derivado, determinismo
provado. **E descrevia um sistema que já não existia.**

```
NADA FALHOU. E POR ISSO NINGUÉM DEU POR NADA.
```

O defeito não estava em nenhuma guarda. Estava na **pergunta que nenhuma
fazia**. Todas perguntavam:

> «o mapa corresponde a ESTA árvore?»

Nenhuma perguntava:

> «ESTA árvore é o sistema?»

A lei do espelho (`COL-LAW-046`) diz `SISTEMA REAL ⇄ SYSTEM MAP`. Ela **não diz
qual** sistema real — e com linhas paralelas de trabalho essa omissão deixa de
ser teórica e passa a custar noites.

### A guarda, e as cinco perguntas que ela faz

`system-map/tests/test_base_da_auditoria.py`, contra
`system-map/COLLECTION-AUDIT-BASE.json`:

```
a referência resolve?            senão CANNOT_MEASURE — e isso REPROVA
a árvore contém a linha?         senão FAIL HIGH, com os dois SHA ao lado
os marcos estão no disco?        ANCESTRY != CONTEÚDO
o observador mexeu no observado? diff contra a própria linha declarada
a base ainda é um ramo vivo?     um SHA cravado defende um ponto morto
```

**Três decisões de desenho que valem mais do que a guarda:**

1. **A base é uma REFERÊNCIA, não um SHA.** Um SHA obriga a editar o contrato a
   cada commit da Collection, e um ficheiro que se edita todos os dias deixa de
   ser lei em duas semanas.
   `REFERÊNCIA MEDIDA AGORA > SHA COPIADO ONTEM.`

2. **`CANNOT_MEASURE` reprova.** Uma guarda que passa por não conseguir medir dá
   sossego sem dar prova — e é assim que se perde a noite seguinte.

3. **`ANCESTRY != CONTEÚDO`.** Conter o commit não chega: um `revert` mantém a
   ancestralidade e tira o código. A guarda confere que os marcos nomeados estão
   no disco.

---

## O OBSERVADOR NÃO PODE ALTERAR O OBJECTO OBSERVADO — NEM FICAR PROIBIDO DE SE CORRIGIR

Trazer o System Map para a linha funcional é trazer **mecanismo**: `scripts/`,
`app/`, `tests/`, a cadeia. **Nunca** `system-map/data/`: as declarações de uma
árvore são dessa árvore, e a desta já declarava o SCRAP moderno inteiro (155
componentes contra 135 da linha do mapa).

E a guarda da preservação tem de **excluir explicitamente os workflows do
próprio observador**. Medi-los como código funcional proibiria o mapa de ganhar
uma guarda nova sem parecer que alterou a Collection.

```
O OBSERVADOR NÃO PODE ALTERAR O OBJECTO OBSERVADO.
MAS TAMBÉM NÃO PODE FICAR PROIBIDO DE SE CORRIGIR.
```

---

## A LEI DO RECIBO — E ONDE ELA PÁRA

Esta árvore guarda uma coisa que a anterior não tinha: o retrato de uma
**corrida inteira**, etapa a etapa, lido do banco depois de ela correr. O mapa
não lia nenhum dos dois.

```
UM MAPA QUE NÃO LÊ O RECIBO DA CORRIDA DESENHA SEMPRE O SISTEMA DE ONTEM.
```

Mas o recibo só autoriza o que ele próprio nomeia. `REQUEST`, `ORCHESTRATOR` e
`EXECUTOR` trazem `ACTOR=` e `COMANDO=` — um ficheiro, que resolve numa peça.
As outras oito etapas contam linhas e tabelas e **não dizem que peça as
escreveu**. Resolvê-las cruzando com o modelo das estradas seria juntar duas
fontes para inventar uma seta.

```
DUAS ETAPAS OBSERVADAS NÃO SÃO UMA ARESTA OBSERVADA.
A ARESTA SÓ NASCE QUANDO O MESMO RECIBO NOMEIA AS DUAS PONTAS.
```

**E o plano OBSERVED passa a ter um dono só.** Lia-se de um índice lateral, e as
arestas novas nasciam com a evidência certa e ficavam em `NÃO SEI` por não
estarem no índice.

```
A EVIDÊNCIA É O DONO DO PLANO QUE ELA SUSTENTA.
Um índice ao lado dela é uma segunda opinião à espera de divergir.
```

---

## O QUE ISTO **NÃO** PROVA

- **Não prova que a Collection colhe da rede.** O recibo que fecha a estrada diz
  `ORIGEM_DOS_BYTES = ARQUIVO_LOCAL` e `AQUISICAO_PELA_REDE = NOT_PROVEN`. A
  estrada fecha; a aquisição pela rede não está provada, e há um ataque que
  reprova quem disser o contrário.
- **Não prova que o SCRAP correu.** Ele está registado na receita e o
  orquestrador corre-o — em `CODE`. Nenhum recibo de corrida do SCRAP existe
  nesta árvore.
- **Não prova nada sobre LIVE.** A migration 031 está no Git. Se está aplicada,
  `LIVE_STATE = NOT_MEASURED` — e não se mediu de propósito.
- **Não prova que esta árvore está publicada.** `AUDIT TREE != DEPLOY TREE`.
