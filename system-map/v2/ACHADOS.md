# ACHADOS — o que a reconstrução encontrou, e não consertou

> Esta missão tinha uma proibição explícita: **mostrar o defeito, não corrigir o
> defeito.** O que está aqui foi **medido**, não suposto. Nada nesta lista foi
> arranjado — cada achado continua exatamente como estava quando o mapa o viu.

Medido em `HEAD` da reconstrução, sobre 1929 ficheiros rastreados e 105 leis.

---

## ACHADO-1 · o mapa **oficial** perdeu uma aresta verdadeira por colisão de nome

**O que aconteceu.** Ao regenerar o mapa oficial (lei do `CLAUDE.md`), a aresta

```
C-MAPA-APP --READS--> C-TESTES
prova: tests/test_observabilidade_estrada.py:382  ·  "'system-map', 'map.js'))"
```

**desapareceu**. O ficheiro de teste não mudou, a linha não mudou, o dono não
mudou (`C-TESTES`, nas duas revisões). A aresta deixou de existir na mesma.

**Porquê.** `system-map/scripts/scan_repo.py` resolve um literal de caminho por
**nome único no censo** (`por_nome_unico`). Antes desta missão havia **um**
`map.js` no censo — as cópias publicadas estão em `IGNORAR`:

| censo | antes | depois |
|---|---|---|
| `map.js` | 1 · `system-map/app/map.js` | 2 · `+ system-map/v2/app/map.js` |
| `map.css` | 1 | 2 |

Com dois, o nome deixou de ser único, e o scanner recusou-se a escolher.

**O scanner não está a mentir — está a recusar inventar.** O comentário dele diz
isso com todas as letras: *«Dois ficheiros com o mesmo nome não dão para
distinguir a partir do literal, e escolher um seria inventar.»* A recusa é
correta pela lei dele.

**O defeito real é outro, e é este:** a derivação de arestas do mapa oficial é
**frágil a colisões de nome em qualquer ponto do repositório**. Um ficheiro novo,
numa pasta sem relação nenhuma com a aresta, apaga silenciosamente uma ligação
verdadeira — e o mapa fica **mais pobre sem avisar ninguém**. Não há aviso, não
há contagem, não há teste que falhe. A aresta simplesmente não está lá.

**Não corrigido nesta missão.** Corrigir é mexer em `scan_repo.py`, que é
runtime do mapa oficial.

---

## ACHADO-2 · a cadeia canónica morre em `ADMISSION → READY`

`FIRST_LOST_EDGE: ADMISSION → READY`. A cadeia está **OBSERVED** até à admissão
e não passa dali.

| peça | estado | motivo medido |
|---|---|---|
| `M-READY` · A unidade pronta | `BLOQUEADO` | a medição diz que este passo não aconteceu |
| `M-SALA` · A sala de espera | `BLOQUEADO` | a medição diz que este passo não aconteceu |
| `M-TRAVA` · A trava da inteligência | `BLOQUEADO` | a medição diz que este passo não aconteceu |

**A sala de espera nunca recebeu nada.** Tem contrato, tem código, e nunca
correu. A inteligência está travada por contrato, a montante dela.

---

## ACHADO-3 · a Bíblia exige uma peça que não existe

`M-LACUNA` · *A falta de coleta* — `NAO_IMPLEMENTADO`.
Motivo medido: **a Bíblia exige, e não existe implementação aqui.**

A única saída canónica dela (`M-LACUNA → M-PEDIDO`, «a falta de material vira um
pedido, pela porta da frente») tem prova **DECLARED** e nada mais forte. É o
*Collection Gap*: hoje ninguém pede nova coleta pela porta da frente.

---

## ACHADO-4 · três ligações vivem só no papel

As três arestas mais fracas do mapa estão em `DECLARED` — contrato sim, código
não provado, execução nenhuma:

| ligação | onde está escrita |
|---|---|
| `D-ESPERA → D-INTELIGENCIA` | `docs/operacao/TRAVA-DA-INTELIGENCIA.json` |
| `D-INTELIGENCIA → D-ENTRADA` | `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` |
| `M-LACUNA → M-PEDIDO` | `BIBLIA-CANONICA-DA-COLETA.md` |

Nenhuma foi promovida. `UNKNOWN = 0` porque cada uma declara o que a sustenta.

---

## ACHADO-5 · dez peças em 27 nunca foram vistas a correr

`observado`: `SIM 14 · NAO 3 · NÃO SEI 10`.

**`NÃO SEI` não é `NÃO`.** Dez peças não têm artefato de execução que as prove —
nem para bem nem para mal. O mapa diz `NÃO SEI` e mostra porquê, em vez de
escolher um lado.

---

## ACHADO-6 · o publicado não é o mais recente, e isso é lei

`system-map/CANONICAL-PUBLICATION.json` declara `CANONICAL PUBLISHED != LATEST SOURCE`,
e explica que *a cópia commitada nasce sempre um commit atrás de si mesma*.

É por isso que `V01_SEM_DRIFT` compara **sem** `PROVENANCE`: o `HEAD` que o mapa
grava muda no próprio commit que o grava. Comparar byte a byte reprovaria toda a
gente, para sempre. Quem ler o `stamp` da página e o `HEAD` do repositório vai
ver um commit de diferença — **por desenho, não por avaria.**

---

## O que NÃO foi tocado para nenhum destes achados

`collection/` · `intelligence/` · `scripts/` · `migrations/` · `italia-portale/server/` ·
`.github/workflows/scrap-social.yml` · contratos canónicos · Bíblia · donos
arquiteturais · e os quatro ficheiros de código do mapa oficial
(`index.html`, `map.js`, `map.css`, `freshness.js`).
