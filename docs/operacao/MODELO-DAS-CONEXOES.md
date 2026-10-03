# O MODELO DAS CONEXÕES DO MAPA

> Medido em 07/09/2026. Regenerável com
> `py system-map/scripts/generate_system_map.py`.

---

## A — COMO ERA ANTES DESTA ETAPA

### Os tipos que existiam

| tipo | quantas | como é detectado | direção guardada |
|---|---:|---|---|
| `READS` | 167 | `open(CONST)` sem modo de escrita, `ast` | **virada**: lido → leitor |
| `IMPORTS` | 76 | `import X` / `require()`, `ast` | **virada**: importado → importador |
| `RUNS` | 32 | workflow ou script que chama outro | não virada: quem manda → quem obedece |
| `VIAJA_POR` | 15 | canal citado no código da ação | canal → ação |
| `FEEDS` | 11 | contrato de bloco nomeia a camada | camada → tela |
| `WRITES` | 11 | `open(CONST,'w')`, `ast` | não virada: quem escreve → o ficheiro |
| `ABRE_O_CANAL` | 6 | ferramenta e canal no mesmo ficheiro | ferramenta → canal |
| `ENTREGA_A_LISTA` | 4 | contas por plataforma no atlas | AS FONTES → canal |

### A regra de direção que estava em vigor

Uma só, e coerente:

> **FROM = de onde PARTE o que atravessa a linha.**

- `READS`: o conteúdo do ficheiro parte dele e entra em quem leu → **lido → leitor**
- `IMPORTS`: o código do módulo importado entra no importador → **importado → importador**
- `RUNS`: a ordem parte de quem manda → **quem manda → quem obedece**
- `WRITES`: o conteúdo parte de quem escreve → **escritor → ficheiro**

### Como o cliente desenhava

Três naturezas, e **duas delas com o mesmo traço**:

```
FLUXO     linha cheia
MONTAGEM  tracejado 3 4, opacidade 30%   ← iguais
DISPARO   tracejado 3 4, opacidade 30%   ← iguais
```

**O que ficava visualmente igual:** `IMPORTS` e `RUNS`. Um é dependência de
código, o outro é uma ordem de execução — coisas completamente diferentes,
desenhadas com o mesmo tracejado. E `READS`, `WRITES`, `VIAJA_POR`, `FEEDS`,
`ENTREGA_A_LISTA` e `ABRE_O_CANAL` — seis relações distintas — todas com a
mesma linha cheia.

---

## B — O ERRO DE DIREÇÃO, REPRODUZIDO

O código, em `orquestrador/orquestrador.py:54`:

```python
import admissao as adm
```

A verdade: **o orquestrador importa a admissão.**

O que o mapa guardava:

```
FROM    C-ADMISSAO       (A porta de admissão)
TO      C-ORQUESTRADOR   (O orquestrador)
TYPE    IMPORTS
REASON  «A porta de admissão importa O orquestrador»   ← INVERTIDO
```

### Onde estava o defeito

A direção **não** estava errada: `IMPORTS` é virado de propósito, porque o
código do importado entra no importador — e isso é coerente com a regra única.

O errado era a **frase**. Ela é montada assim
(`generate_system_map.py`, ~linha 1794):

```python
verbo = {"IMPORTS": "importa", "READS": "alimenta", ...}
reason = f"{de} {verbo} {para}."
```

`READS` foi virado **e** ganhou o verbo da direção nova (*alimenta*). `IMPORTS`
foi virado depois e **ficou com o verbo da direção antiga** (*importa*).

Resultado: a seta dizia uma coisa e a frase dizia o contrário.

**Quantos casos: 76** — todas as arestas `IMPORTS`. Não é um caso isolado: é
sistemático, e passava despercebido porque cada frase, lida sozinha, parece
plausível.

### A lição

> Virar uma seta é meia mudança. A outra metade é a frase que a descreve — e
> ela não avisa quando fica para trás.
