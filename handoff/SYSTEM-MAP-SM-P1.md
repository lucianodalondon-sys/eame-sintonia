# HANDOFF · SM-P1 · O MAPA PASSA A PODER FICAR VERDE, E SÓ QUANDO PROVA

**O `.vercelignore` continua fechado. Zero ficheiros a mais foram enviados para o
contentor. E, ainda assim, a build passou a provar que árvore está a implantar.**

---

## EM UMA LINHA

A prova de pertença deixou de ser um SHA de commit — que era **impossível por
construção** — e passou a ser a **impressão das fontes**, lida do **índice do
git**, que o `.vercelignore` não apaga.

---

## OS CAMPOS

| | |
|---|---|
| `BRANCH` | `claude/system-map-freshness-v1` |
| `HEAD` | `34ac891f` |
| `BASE` | `96db9f1d` (system-map) + `c268f3ba` (canónica, M2I fechada) |
| `MERGE` | feito · 5 conflitos, os **cinco derivados**, resolvidos regenerando |
| `MERGEADO NA CANÓNICA` | **NÃO** |
| `PRODUÇÃO PROMOVIDA` | **NÃO** |
| `M2 / M2I / IDENTIDADE / LINHAGEM` | **NÃO TOCADAS** |

---

## O QUE ESTAVA A BLOQUEAR O VERDE, E O QUE O DESBLOQUEOU

Dois factos, e nenhum era resolúvel afrouxando o `.vercelignore`.

### 1 · «este mapa é o mapa desta árvore?» — era impossível, não difícil

```
commit 8e1947d2  ->  state.PROVENANCE.HEAD = c293be65
commit c293be65  ->  state.PROVENANCE.HEAD = 44e2de1b
```

Um ficheiro não pode conter o SHA do commit que só existe depois de ele entrar
lá. **Enquanto a prova for um SHA de commit, ela nunca fecha.**

> **A pergunta certa não é «que commit?». É «que fontes?».**

`system-map/scripts/impressao_da_arvore.py` sela as **fontes rastreadas** e
exclui as **saídas da própria cadeia**. Guardar o mapa regerado não mexe nas
fontes, logo **não move a impressão**.

**E lê-se do ÍNDICE.** O `.vercelignore` apaga **ficheiros do disco**; não apaga
o índice, e o índice carrega o SHA do blob de cada ficheiro rastreado.

> **ESTAR NO ÍNDICE ≠ ESTAR NO DISCO** — e desta vez isso joga a nosso favor.

```
7d52a9d3...   árvore inteira
7d52a9d3...   árvore mutilada, 999 ficheiros apagados do disco
```

Numa simulação real da Vercel (999 ficheiros fora do disco, índice intacto), o
publicador respondeu:

```
MESMA_ARVORE=NAO      (a comparação de SHAs — e sempre dirá NÃO)
PERTENCE=SIM          (a impressão — e está certa)
```

### 2 · o veredito do validador — o contentor nunca vai poder produzi-lo

Validar exige regenerar; regenerar exige a árvore inteira. **Isso não vai mudar,
e não deve.** O CI já produz esse veredito. Só que o job era **um só**, chamado
`check`, e misturava o mapa com a coleta — e o passo 3 (coleta) está vermelho na
canónica desde antes desta missão. Medido:

> **os passos `4k`, `6`, `7` e `8` NUNCA CHEGARAM A CORRER no GitHub.**

> **Um portão que nunca corre não é um portão.**
> **Um veredito sobre duas perguntas não responde a nenhuma.**

Agora são **`SYSTEM MAP CHECK`** e **`COLETA CHECK`**, em paralelo, os dois
obrigatórios. **Correm mais provas do que antes, não menos.** A tela vai buscar a
conclusão do portão **do mapa** para o commit servido, pelo nome que viaja no
artefato — o nome vive em `CADEIA-DO-MAPA.json`, nunca escrito no browser.

---

## A OPÇÃO A, MEDIDA E REJEITADA

Afrouxar o `.vercelignore` custaria **899 ficheiros / 151.1 MB**, dos quais
**127.3 MB são o acervo**, enviados para um contentor cujo output é público.

**Não é preciso, e por isso nem se discute o preço.**

---

## O PREÇO QUE ISTO TEM, DITO EM VOZ ALTA

A impressão cobre a árvore **inteira**. Cobrir «só o que alimenta o mapa»
exigiria adivinhar o que seis scanners leem, e **adivinhar de menos produz verde
falso** — o único erro que esta lei não pode cometer.

**Mexer em qualquer ficheiro rastreado obriga a correr a cadeia outra vez.**
`AGENTS.md` já mandava; o passo **`2b`** faz isso reprovar **à porta**, em vez de
virar um STALE depois do deploy.

> **Um alarme que só toca depois do deploy está mal colocado.**

---

## VERIFICADO NUM BROWSER A SÉRIO · 7/7

Sobre **os bytes que a build produziu** — contentor montado como o da Vercel,
publicador real, `deployment.generated.json` **não escrito à mão**. Só as
respostas do GitHub foram interceptadas, para cada cenário ser determinístico.

| cenário | resultado |
|---|---|
| tudo alinhado | 🟢 `CURRENT` |
| a cabeça remota andou | 🔴 `STALE · MAP IS 7 COMMITS BEHIND` |
| o GitHub não responde | ⚪ `FRESHNESS UNKNOWN` |
| o portão reprovou este commit | 🔴 `SYSTEM MAP INVALID` |
| o portão ainda está a correr | ⚪ `FRESHNESS UNKNOWN` |
| o mapa é de OUTRA árvore | 🔴 `STALE · MAP OF ANOTHER TREE` |
| o portão correu com outro nome | ⚪ `FRESHNESS UNKNOWN` |

**Cinco dos sete exigem que a tela NÃO fique verde.** 145 peças desenhadas, zero
erros de JS. O harness está em `system-map/tests/verificar_a_tela.mjs`, com uma
etiqueta honesta: **ele não é um portão** (precisa de browser, e a cadeia do mapa
não carrega dependência de terceiro).

---

## OS BURACOS PASSARAM A VER-SE

Quatro buracos com nome viviam em **três formatos**, e um deles era **um
`print`**. Nenhum aparecia no mapa.

> **Um buraco que só existe num `print` não existe para ninguém.**

`censo_dos_buracos.py` **mede** onde eles já vivem — tuplos `GAPS` por AST e
chaves de `provas-de-execucao.json`. **Não é um registo novo**: copiá-los criaria
o quarto sítio, e a partir daí nenhum valeria. Fechar um buraco é apagar a
declaração dele. Os oito aparecem na tela, com o texto e o ficheiro:

```
ADMISSION_SEM_DONO_LIGADO      RAW_FORWARD_NAO_EMITE
CHANNEL_IDENTITY_NOT_RESOLVED  READY_NAO_TEM_DONO
GAP_DECLARADO                  STRUCTURED_SEM_DONO_LIGADO
LINEAGE_PROOF_GAP              TELEMETRY_FAILURE_SEM_POLITICA
```

`null` nunca se pinta como zero: «o censo não correu» e «não há buracos» são
frases opostas.

---

## 37 · 42 · 23 — TRÊS PERGUNTAS

A M2I escreveu «o atlas tem 42 fontes com ficha». Medido, não tem:

```
37   o que o CABEÇALHO do atlas declara
42   SOURCE_IDs MENCIONADOS no texto, tabelas incluídas
23   FICHAS completas, com SOURCE_ID válido
```

> **MENCIONADO NO ATLAS ≠ TEM FICHA NO ATLAS.**

**A conclusão da M2I não muda** — `IT-T2-002` aparece zero vezes nas duas contas
— e por isso **nada da M2I foi tocado**. O que mudou é que o scanner passou a
publicar os três, com os 19 mencionados-sem-ficha listados pelo nome.

---

## ⚠️ O QUE NÃO FOI MEDIDO, E ESTÁ ESCRITO NO CÓDIGO

A chamada ao GitHub tem de partir do browser **sem credencial**. Medido: o
repositório é público (`private: false`) e `api.github.com` devolve
`Access-Control-Allow-Origin: *`.

**A chamada ANÓNIMA não foi possível medir** do contentor desta missão: o proxy
de saída injecta autenticação, e a resposta veio com o limite de **15000/hora de
uma app instalada**, não com os **60** de quem não se identifica.

A suposição **não sustenta nenhum verde**: se a chamada falhar, o veredito cai
para `UNKNOWN` e a tela fica **branca**, com o motivo escrito.

> **Uma suposição que só pode empurrar para NÃO SEI não consegue mentir para
> verde.**

**Quem promover a produção deve confirmar isto no browser real**, e é a única
verificação que fica por fazer nesta linha.

---

## TESTES

```
SYSTEM_MAP_CHECK=PASS              validador, 145 peças, 0 partidas
TESTES_FRESCURA=PASS · 49 provas   a lei, sem browser
TESTES_IMPRESSAO=PASS · 19 provas  a impressão, e a lista que se confere sozinha
BROWSER=PASS · 7/7 cenários        a tela, com browser
IMPRESSAO_DO_CARIMBO=IGUAL         o mapa commitado é o mapa desta árvore
```

**`TESTES_SYSTEM_MAP` reprova em 2**, `regua_que_carimba_nao_e_regua_que_mede` e
`E2_receita_continua_com_um_consumidor` — **as mesmas que já reprovavam em
`8e1947d2`**, e são da coleta. `medidas/padrao_da_coleta.py` também, e também já
estava.

> **NEW_FAILURES desta missão = 0.**

`4h` (`test_preservar_coleta_no_banco.py`) não foi corrido aqui: precisa de
Postgres. **SKIP declarado, não PASS presumido.**

---

## O QUE FICA POR FAZER

1. **Confirmar a chamada anónima ao GitHub** num browser real, fora deste proxy.
2. **Promover a produção.** `sintonia-eame-preview.vercel.app/system-map/`
   respondia 404 na missão anterior: o alias serve um deployment **anterior ao
   System Map existir**. Quem promover está a publicar a **primeira** versão
   naquele endereço, não a substituir uma.
3. **Recarimbar o que foi relido.** Nada foi recarimbado aqui — `--stamp` carimba
   **todos** os ficheiros, e recarimbar sem reler é o único jeito de mentir neste
   sistema.
4. **O vermelho da coleta** (`padrao_da_coleta.py`) continua de pé, e agora está
   isolado no seu próprio portão: ele já não apaga as provas do mapa.
