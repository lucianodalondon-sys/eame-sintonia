# CONVERGÊNCIAS — SINTONIA EAME

**Data:** 2026-08-31 · derivado de `data/refresh/SIGNAL-DEPENDENCY-GRAPH.json`

> A pergunta **não** é *"quantos datasets batem?"*.
> A pergunta é *"existem sinais suficientemente independentes para este assunto merecer
> atenção?"*.

---

## 0 · PLACAR

```
MULTI_SIGNAL_CONVERGENCE ...... 0
PARTIAL_CONVERGENCE ........... 0
SINGLE_SIGNAL ................. 1     IT × Toscana × TRIGO DURO × FUSARIUM
NOT_ENOUGH_EVIDENCE ........... 5
```

**Sem threshold inventado.** Não há regra do tipo *"3 pernas = convergência"*. A
classificação sai de uma pergunta só: **quantas famílias INDEPENDENTES falam do mesmo par?**

---

## 1 · POR QUE ZERO NÃO É FRACASSO DE COLETA

O acervo tem seis famílias de sinal que podem contar. O que ele **não** tem é duas delas
falando do **mesmo país × cultura × problema × tempo**.

Antes do grafo, este documento teria anunciado convergências. Depois dele, elas caem — e
caem por motivos nomeáveis:

| convergência aparente | por que caiu |
|---|---|
| Foresight (marca + registro + anúncio) **+** Meta (anúncio) | o anúncio é **o mesmo**. `DERIVED_DEPENDENCY_ON_META` |
| Foresight **+** regulatório local **+** portfólio ADAMA | os três leem **a mesma base nacional**. `SHARED_REGISTRY_NOT_TWO_FAMILIES` |
| Creator Map **+** Deep Corpus | a mesma entidade, duas observações. `SAME_ENTITY_DIFFERENT_OBSERVATION` |
| Territorial listagem **+** territorial corpo | o mesmo documento, duas leituras. A própria missão declara `LISTING_ROLE = DISCOVERY_INDEX_ONLY` |
| Meta snapshot 1 **+** snapshot 2 | as mesmas páginas, **uma hora** de distância |
| Ciência **+** pesquisador | o mesmo OpenAlex |

**Seis pares que pareciam convergência e são a mesma evidência vista de outro ângulo.**

---

## 2 · A ÚNICA CONVERGÊNCIA QUE QUASE EXISTIU

`IT × DURUM_WHEAT × FUSARIUM` tem:

- **TERRITORIAL** — boletim IT-LAMMA de Grosseto, problema no corpo, 23/04/2026 ✅
- **SCIENCE_RESEARCHER** — duas identidades ORCID no recorte `IT-DURUM_WHEAT-FUSARIUM`…
  **mas expertise no problema `NOT_MEASURABLE`**: o corpus científico disponível é espanhol,
  e as duas pessoas têm zero obras nele. `NOT_MEASURABLE ≠ NOT_PROVED`, e nenhum dos dois
  autoriza contar como perna.
- **NATIONAL_REGISTRY** — a Itália tem 163 registros ADAMA vigentes, mas **`CROP_ISSUE = 0`**:
  a tabela cultura × alvo do rótulo nunca foi reconstruída. Não há como amarrar ao par.
- **CREATOR** — nenhum creator italiano com trigo duro provado, e o corpus não classifica
  fusarium.
- **META / FORESIGHT** — 10 tuplas italianas provadas, **sem cultura e sem problema**.

**Falta uma segunda perna por um motivo diferente em cada camada** — e nenhum deles é
"não coletamos o bastante". Três são estruturais: o corpus científico não cobre a Itália,
o registro italiano não publica cultura × alvo, e a camada de concorrente não carrega
cultura nem problema em país nenhum.

---

## 3 · O QUE FECHARIA UMA CONVERGÊNCIA DE VERDADE

Em ordem de custo, do mais barato ao mais caro:

1. **Reconstruir cultura × alvo do rótulo italiano.** O PDF existe, 163 rótulos oficiais
   já baixados. Fecharia a perna de registro para qualquer par italiano — e faria as 10
   tuplas italianas de concorrente entrarem na chave de caso.
2. **Corpus científico não-espanhol.** Sem ele, `EXPERT_CASE_EXPERTISE` de IT e FR fica
   `NOT_READY` para sempre — e `NOT_READY` não é `NOT_PROVED`.
3. **Segunda captura territorial com intervalo real.** Uma janela de um dia mediria o que
   uma janela de uma hora não mede.

**Nenhuma delas foi executada nesta rodada, e nenhuma é coleta nova de fonte nova** — as
duas primeiras são reprocessamento de material que já está preservado.

---

## 4 · CLASSIFICAÇÃO POR RECORTE

| recorte | famílias independentes | classe |
|---|---:|---|
| `IT_DURUM_WHEAT_FUSARIUM` | **1** | `SINGLE_SIGNAL` |
| `ES_OLIVE_REPILO` | 0 | `NOT_ENOUGH_EVIDENCE` |
| `ES_WHEAT_SEPTORIA` | 0 | `NOT_ENOUGH_EVIDENCE` |
| `IT_VINE_FLAVESCENCE` | 0 | `NOT_ENOUGH_EVIDENCE` |
| `FR_VINE_DOWNY_MILDEW` | 0 | `NOT_ENOUGH_EVIDENCE` |
| `FR_WHEAT_SEPTORIA` | 0 | `NOT_ENOUGH_EVIDENCE` |

**`ES_OLIVE_REPILO` merece uma nota.** É o par mais lastreado do acervo inteiro em número
de artefatos — e mesmo assim sai com zero famílias independentes **para o problema**. O
territorial não sustenta repilo no corpo; a expertise foi medida e derrubada; o creator é
rota de cultura, não de problema. Volume de artefato não é convergência.
