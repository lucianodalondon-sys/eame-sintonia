# KNOW-HOW DELTA — O GARGALO DA BASE DE FONTES É O RAMO DA ROTA, NÃO A FONTE

**Data:** 2026-09-18
**Missão:** HOT SOURCE BASE ITALIA V1 (SOURCE CURATOR)
**Branch:** `claude/it-hot-source-base-v1` · **Base:** `d915f85a` (trunk no momento da medição)
**Estado:** delta interino — a integrar em `SINTONIA-EAME-KNOW-HOW.md` pelo dono da cadeia

---

## O QUE

### 1 · `HOT_READY` É UMA CONJUNÇÃO DE QUATRO PROVAS INDEPENDENTES

Medir uma só e chamar-lhe prontidão foi o erro da missão anterior. As quatro:

```
SOURCE_EVIDENCE_EXISTS   ha MANIFEST/amostra guardada       medido: 154/170
TERRITORY_HAS_EXECUTOR   o territorio tem executor           medido:  88/170
WIRED_TO_COLLECTION      executor + access_method conhecido  medido:  87/170
ROUTE_WORKS_NOW          corrida de hoje devolveu HEALTHY    medido:   5/170
```

**Ter MANIFEST não prova nada sobre a rota.** O MANIFEST é história: alguém, um dia,
guardou bytes. Não diz que existe executor, nem que a rota responde hoje.

```
SOURCE_EVIDENCE_EXISTS  !=  EXECUTOR_EXISTS  !=  WIRING_EXISTS  !=  ROUTE_WORKS_NOW
```

### 2 · O GARGALO MEDIDO É O RAMO `case` DA DESCOBERTA, E ISSO NÃO SE VÊ DE FORA

`coleta/italy_pilot_collect.mjs::alvosDe(sourceId)` é um `switch` com **um `case`
escrito à mão por fonte**. Sete fontes têm ramo. Qualquer outra — mesmo com contrato
completo em `regras/italy_contracts.mjs` — cai no `default` e devolve:

```
OBSERVATION_RESULT = DISCOVERY_FAILED
motivo = "fonte sem alvo definido no piloto"
```

Provado por canário real: `IT-T2-001`, `IT-T3-011` e `IT-T7-002` têm contrato com
`ROUTE_TYPE`, `RETRIEVAL_METHOD` e frequência observada — e falham na descoberta.

```
CONTRATO DE FONTE ESCRITO  !=  ROTA EXECUTÁVEL.
O CONTRATO DESCREVE O CAMINHO; O `case` É QUEM O PERCORRE.
```

**Consequência para a escala:** aumentar a base não é descobrir mais fontes — é
transformar o `switch` numa rota dirigida pelo contrato. Enquanto for `case` a `case`,
o custo de cada fonte nova é código, não cadastro.

### 3 · `SUCCESS` DA CORRIDA NÃO É COLHEITA — T6 MEDIDO

`corpus-pesquisador` (T6, 36 fontes ORCID) correu **`CORRIDA SUCCESS`** em 123 s e
declarou `colheita encontrada: 0 item(ns)`. O executor devolve `CATALOG` — a lista de
pessoas de quem se *poderia* colher obra —, não obra.

```
CORRIDA SUCCESS  !=  ITENS COLHIDOS.
CATALOG != COLHEITA (COL-LAW-013/014: só COLHEITA entra no ingresso).
```

Trinta e seis fontes que pareciam as mais prontas da base (executor existe, caminho
escrito, 36/36 com `access_method`) não entregam um item.

### 4 · O ENDEREÇO DA FICHA NÃO É O ENDEREÇO QUE A COLETA USA

Testar a `url` da ficha do Atlas produziu **4 falsos BLOCKED** em fontes que a
Collection já colhera. O endereço que importa é o `CANONICAL_ENTRY_URL` do contrato —
e às vezes nem esse: `IT-T3-002` dá 404 na entrada de 2026 e mesmo assim colhe, porque
a rota real é por ano/província.

```
URL DA FICHA != ENDPOINT DO CONTRATO != ROTA EXECUTADA   (COL-LAW-205)
UM PROBE HTTP DE FORA NÃO SUBSTITUI UMA CORRIDA.
```

Ordem de prova correta, da mais fraca para a mais forte: probe da ficha → probe do
endpoint do contrato → **canário pela porta oficial**. Quando divergem, manda o canário.

---

## POR QUÊ

Os quatro erros têm a mesma raiz: **confundir um artefacto guardado com uma capacidade
viva.** Um MANIFEST, um contrato escrito, um `SUCCESS` no recibo e um HTTP 200 são todos
verdadeiros — e nenhum deles responde «esta fonte entrega alguma coisa hoje?».

---

## PROVA

```
HEAD MEDIDO            d915f85a  (trunk; b8ebca8a ficou 3 commits atras no mesmo dia)
UNIVERSO               170 (IT 157 + EU 13) · ATLAS 210 == SYSTEM_MAP 210
DECISOES DE RELEVANCIA 6 -> 162 (156 registadas nesta missao, decisao humana)
PORTAO COLETA_TOTAL    AUTORIZA 162 · EXIGE_AVALIACAO 8

CANARIO PELA PORTA OFICIAL (VPN_COUNTRY=IT, egresso 205.147.30.6):
  6 fontes do piloto   -> HEALTHY 5 · FAILED 1 (IT-T3-010 IDENTITY_FAILED)
  3 fontes contratadas fora do piloto -> DISCOVERY_FAILED 3/3
  T6 (36 fontes)       -> CORRIDA SUCCESS, 0 itens (CATALOG)

CLASSES FINAIS  HOT_READY 5 · HOT_NEEDS_WIRING 70 · WARM 73 · BLOCKED 14 · PENDING 8
FILA DE WIRING  34 sem contrato · 36 com executor que devolve CATALOG
```

---

## CONSEQUÊNCIA

**Para o SOURCE CURATOR:** parar de reportar prontidão por evidência guardada. A
pergunta é sempre «correu hoje?», e a resposta vem de canário pela porta oficial.

**Para o SCRAP/COLLECTION (fila entregue, não executada):** o maior ganho por unidade de
esforço não é fonte nova — é (a) tornar `alvosDe` dirigido por contrato, o que converte
34 fontes já contratáveis, e (b) fazer o executor de T6 devolver obra em vez de catálogo,
o que converte 36. Duas mudanças, 70 fontes.

**Regra de prova que fica:** em base de fontes, `HOT_READY` exige as quatro provas
medidas na mesma janela. Qualquer subconjunto é `HOT_NEEDS_WIRING`, `WARM` ou `BLOCKED` —
nunca pronto.
