# KNOW-HOW DELTA — O SOURCE_ID QUEIMADO NÃO VOLTA, E O ATLAS NÃO É A POPULAÇÃO

**Data:** 2026-09-18
**Missão:** SOURCE CURATOR — MISSÃO 001 (censo + expansão) e o landing das candidatas
**Branch:** `claude/it-sources-candidatas-v1`
**Base:** `b8e374a3` (cabeça de `claude/it-trunk-v1` no momento da medição)
**Estado:** delta interino — a integrar em `SINTONIA-EAME-KNOW-HOW.md` pelo dono da cadeia

---

## O QUE

Três coisas duráveis, medidas nesta missão. A primeira é a que custa caro.

### 1 · UM `SOURCE_ID` RETIRADO CONTINUA QUEIMADO, E O HEAD NÃO O MOSTRA

A convenção do Atlas já dizia que o ID *«uma vez atribuído, não é reciclado»*. O que
faltava dizer é **onde se pergunta isso** — porque um ID emitido numa versão antiga e
depois **retirado** desaparece do ficheiro vivo:

```
QUEM CALCULA max+1 NO HEAD RE-EMITE UM NÚMERO JÁ GASTO,
E NADA NO FICHEIRO ACUSA.
```

### 2 · A POPULAÇÃO DE IDs NÃO É O ATLAS, E TAMBÉM NÃO É O HEAD

`leis/fonte_do_atlas.py` já ensinava metade disto — a população em uso é maior do que as
fichas do Atlas, porque `candidatas/ITALY-SOURCE-MASTER-V1.json` cunhou identidades
presas a contratos e a pastas de evidência. A outra metade é o tempo:

```
POPULAÇÃO CORRETA = (ATLAS ∪ MASTER ∪ CANDIDATAS ∪ GENERATED) × (TODAS AS VERSÕES)
```

### 3 · DEDUPE DE FONTE TEM DOIS DEGRAUS, E O DEGRAU 1 TAMBÉM CONTA

Deduplicar uma fonte nova só contra o Atlas responde «esta fonte já é ficha?» — e deixa
passar a pergunta anterior: «esta fonte já está na fila à espera?». Medido: das 117
propostas validadas, **28 já estavam** em `candidatas/FONTES-CANDIDATAS.json`.

```
DEDUPE CONTRA O ATLAS  ≠  DEDUPE CONTRA A FILA
```

---

## POR QUÊ

O defeito dos três é o mesmo: **medir a população errada e chamar-lhe universo.**
O HEAD é uma fotografia do presente; o Atlas é um dos emissores; a fila é o degrau
anterior. Quem pergunta a um só obtém uma resposta verdadeira sobre a gaveta errada.

Um `SOURCE_ID` reciclado é pior do que um ID em falta, porque **faz duas fontes
parecerem uma** — e o erro não aparece no dia em que se comete: aparece quando alguém
cruzar evidência de duas fontes diferentes carimbadas com a mesma identidade.

---

## PROVA

```
VARREDURA          685 versões · 4 emissores · todas as refs (--all)
                   atlas 38 · master 5 · candidatas 2 · generated 640
UNIVERSO HISTÓRICO 203 IDs IT   (contra 162 no Atlas do HEAD)

IDs QUEIMADOS INVISÍVEIS NO HEAD:
  IT-T13-002 · IT-T13-003 · IT-T13-004 · IT-T13-005
  presentes no histórico, ausentes do ficheiro vivo.
  max+1 pelo HEAD daria IT-T13-002 → colisão com quatro identidades gastas.
  Alocado a partir do universo histórico: IT-T13-006, IT-T13-007.

COLISÃO NAS 117 PROPOSTAS:
  COLLISION_CURRENT = 0 · COLLISION_HISTORICAL = 0 · RECYCLED_IDS = 0

DEDUPE EM DOIS DEGRAUS:
  117 validadas − 28 já na fila = 89 realmente novas
  fila 241 → 330 (+89 · 0 perdidas · 0 preexistentes alteradas)

VALIDADOR CANÓNICO:
  tests/test_source_id.py → 6/6 OK antes e depois da escrita
```

O precedente já estava escrito no próprio Atlas, para **um** ID (`IT-T4-002`, retirado
por ser vocabulário e não fonte). O que esta missão mostra é que o caso não era único e
que a defesa não pode ser uma nota em prosa: tem de ser a varredura.

---

## CONSEQUÊNCIA

**Ao emitir `SOURCE_ID`:** perguntar ao universo histórico de todos os emissores, nunca
ao HEAD de um só. A varredura é barata (`git log --all --format=%H -- <ficheiro>` e
`git show <commit>:<ficheiro>`) e é a única que responde à pergunta certa.

**Ao propor fonte nova:** deduplicar contra a fila **e** contra o Atlas, nesta ordem.

**Ao classificar:** `BLOCKED` (403/503, WAF) e `UNREACHABLE` (DNS/reset do egresso) não
são `DEAD`. Fonte válida com aquisição impossível é `CAPABILITY_GAP`, e o dono é o SCRAP
ENGINEER — não é motivo para recusar a fonte.

**Dívida deixada em aberto, não corrigida aqui:** `tests/test_source_id.py` prova
colisão contra a população **em uso**, não contra a **histórica**. Ele teria passado
verde sobre `IT-T13-002` reciclado. Fechar isso é missão do dono dos testes de
identidade; está registado e não foi silenciosamente consertado fora de escopo.
