# FLUXOS DA INTELLIGENCE — o que é seta, o que é vizinhança

```
MISSAO     C-INT-CENSUS-01 · 2026-09-13
MEDIDO EM  claude/raw-observation-identity-3jbwco @ 84186dfa
```

> Nenhuma seta aqui é desenhada sem prova. E as que têm prova são separadas pelo
> **tipo** de prova, porque nem toda prova prova a mesma coisa.

---

## AS TRÊS CAMADAS, E POR QUE ELAS NÃO SE SOMAM

```
DECLARED           alguem escreveu no mapa que a seta existe
STATIC_OBSERVED    ha uma linha de codigo, e o mapa aponta-a
RUNTIME_OBSERVED   correu, e ha saida medida
```

Nas 12 peças de Intelligence:

```
DECLARED         82 arestas
STATIC_OBSERVED  82 arestas   (o mapa marca TODAS como `technical`/PROVEN)
RUNTIME_OBSERVED  2 fluxos    (os dois portoes de linhagem, corridos nesta missao)
```

O `82 = 82` não é boa notícia. Significa que **o mapa não tem nenhuma aresta em
`NÃO SEI`** dentro desta família — e um mapa em que tudo é verde está a esconder.

---

## ⚠️ O QUE O MAPA CHAMA DE «PROVA»

Classificadas as **135 linhas de evidência** que sustentam as 82 arestas:

| natureza da linha | quantas | exemplo |
|---|---|---|
| **co-acesso a ficheiro** | **56** | `CADEIA = os.path.join(RAIZ, "motor", "cadeia_canonica.sh")` |
| linha de workflow (`run:`) | 45 | `run: bash motor/cadeia_canonica.sh migrations ...` |
| `import` | 34 | `from v21_traducao_trava import conferir` |
| **chamada de função** | **0** | — |

```
A MAIORIA DAS SETAS DESTA FAMILIA E PROVADA POR
DUAS PECAS NOMEAREM O MESMO FICHEIRO.
```

Isso não é causalidade. É vizinhança. A lei da casa já o diz — *«não transformar
leitura do mesmo arquivo em causalidade»* — e é exatamente o que 56 das 135 linhas
fazem.

As 45 linhas de workflow **são** invocação real, e valem. Os 34 imports são
evidência estática legítima, mas `IMPORT ≠ FLUXO`.

### O caso que expõe o problema

`C-V2-LEGADO` — o motor V2 antigo — tem **3 arestas marcadas `PROVEN`** no mapa. E
tem **zero** referências em toda a árvore fora do próprio mapa: nenhum import,
nenhum workflow, nenhum teste, nenhum documento.

A prova das 3 arestas é esta:

```
motor/v2_cruzamentos.py:91      vozes = le('PUBLIC-VOICES.json')
motor/v21_vozes_reconciliar.py  qa = json.load(open(QA, ...))
```

Dois ficheiros que tocam artefactos do mesmo mundo. O mapa leu isso como
`C-V2-LEGADO → C-V21-FONTES`.

```
UMA PECA QUE NINGUEM CHAMA APARECE LIGADA
PORQUE PARTILHA UM NOME DE FICHEIRO COM QUEM E CHAMADO.
```

---

## OS DOIS FLUXOS COM PROVA RUNTIME

Estes correram nesta missão, nesta árvore, e a saída está medida.

### FLUXO 1 · O PORTÃO DA BUILD

```
CANONICAL-PACKAGE-CONTRACT.json
  → build-gate.mjs
  → italy-handoff-v21.js  [V21-06c6421d001ea52a]
```

```
node italia-portale/audit/build-gate.mjs   →  exit 0

  PASS  ARTEFACTO_SERVIDO_E_CANONICO   [V21-06c6421d001ea52a]
  PASS  PACOTE_LOCAL_NAO_E_SAFRA_VELHA [AUSENTE]
```

### FLUXO 2 · O PORTÃO DA SAFRA VELHA

```
node italia-portale/audit/stale-generator-gate.mjs   →  exit 0 · 9/9 PASS
```

E com **controlos negativos**, que é o que o torna prova e não impressão:

```
build com BUILD_ID de safra velha        exit 1   (tem de ser != 0)
build com estado revogado PREPARE_NOW    exit 1   (tem de ser != 0)
build com o artefacto reposto            exit 0   (tem de ser 0)
remover so a chamada torna o teste vermelho
```

---

## O FLUXO QUE SE RECUSA A CORRER — E É PROVA

```
bash motor/v21_cadeia.sh   →  exit 2

  CADEIA RECUSADA NESTA LINHAGEM.
  Esta branch e CONSUMIDORA da inteligencia, nao geradora.
```

A cadeia de 16 passos (`v21_ingest` → … → `v21_aceitacao`) **existe e está
completa**, e recusa-se a produzir porque sabe que produziria
`V21-5d312cb90a0de01d` — uma safra sem `MEETING_SURFACE_RULE` e com `PREPARE_NOW`
em 11 casos.

```
UM MOTOR QUE SE RECUSA A CORRER ESTA A FUNCIONAR.
O QUE ELE NAO ESTA A FAZER E PRODUZIR.
```

---

## O CAMINHO PARALELO ATÉ COLLECTION

```
motor/normalize_agro.py:29
  from eppo_gd import names as eppo_names
      ↓
coleta/eppo_gd.py:28
  urllib.request → https://gd.eppo.int/taxon/{code}
```

```
SEVERITY = ARCHITECTURAL
```

Viola `COLLECTION → SALA DE ESPERA → INTELLIGENCE`: a Intelligence chega a um
coletor sem voltar ao fluxo canónico.

**E é o único.** A primeira varredura acusou 18 ficheiros do motor de tocarem
Collection; medidas as **importações** em vez das menções, restou um. As outras 17
apenas escreviam a palavra `coleta` ou `guarda` num comentário ou numa string.

E ninguém o anda: `normalize_agro.py` é um CLI (`build` / `evaluate`) que nenhuma
cadeia e nenhum workflow invocam.

```
DIRECT_COLLECTION_PATHS   = 1   existe em codigo
EXERCIDOS POR UMA ROTA    = 0   CAN DO != DID DO
```

---

## O QUE NÃO TEM FLUXO NENHUM

```
C-V2-LEGADO         7 ficheiros · 0 referencias fora do mapa
lineage_consumer    0 ficheiros · o mapa apresenta-a como PROVEN
italy-v21.js        10 MB · BUILD_ID V21-843baf4229d93598 · 0 carregadores
```

O último merece nota. `italia-portale/client/italy-v21.js` é um pacote de
inteligência gerado a 2026-09-02, e o seu `BUILD_ID` **não é** o canónico nem
consta da lista de safras velhas do contrato — seria classificado `ESTRANEO`.

⚠️ **E aqui a medição corrigiu-me.** Julguei ter encontrado um portão contornado.
Não é: o portão verifica `italy-handoff-v21.js` — outro ficheiro, com o `BUILD_ID`
canónico — e só `portale.html` carrega um bundle, o canónico. O `italy-v21.js` está
lá, com 10 MB, sem ninguém a lê-lo.

```
DOIS FICHEIROS COM NOMES PARECIDOS NAO SAO O MESMO FICHEIRO,
E A PRESSA DE ACHAR UM DEFEITO E O QUE FAZ CONFUNDI-LOS.
```

Risco a registar, e não defeito hoje: ambos definem a **mesma global**
`window.ITALY_HANDOFF_V21`. Se alguém algum dia carregar os dois, o último a
carregar vence — e o portão, que confere por nome de ficheiro, não veria.
