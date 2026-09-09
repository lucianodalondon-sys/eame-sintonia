# HANDOFF · SM-P1R · O DELTA ABSORVIDO, E O ÚLTIMO FACTO QUE FALTA MEDIR

**`SYSTEM_MAP_PROMOTION_READY = NO`**
**`BLOCKER = ANONYMOUS_GITHUB_HEAD_LOOKUP_NOT_PROVED`**

E é o **único** bloqueio. Tudo o resto fechou.

---

## OS CAMPOS

| | |
|---|---|
| `SYSTEM_MAP_INITIAL_HEAD` | `44532540` |
| `SYSTEM_MAP_FINAL_HEAD` | *(ver `git rev-parse origin/claude/system-map-freshness-v1`)* |
| `COLLECTION_HEAD_INITIAL` | `c268f3ba` (o já integrado) |
| `COLLECTION_HEAD_FINAL_SEEN` | `1c99a48b` |
| `MERGE_BASE` inicial | `c268f3ba` |
| `SYSTEM_MAP_CURRENT_THROUGH` | `1c99a48b` |
| `PRODUÇÃO PROMOVIDA` | **NÃO** |

---

## 1 · O DELTA, MEDIDO E NÃO HERDADO

Um commit: `1c99a48b`, «a prova de identidade deixa de depender de quem correu
antes». Cinco conflitos na fusão, **os cinco em `*.generated.json`**. Nenhum
ficheiro de código conflita.

> **DERIVADO EM CONFLITO NÃO SE RESOLVE À MÃO. REGENERA-SE.**

Depois da fusão, a divergência da Collection em **todas** as gavetas de runtime
— `coleta/ guarda/ leis/ medidas/ admissao/ regras/ orquestrador/ ferramentas/
fontes/ pedido/ pacote/` — é **zero ficheiros**. O único ficheiro fora disso é
`provas/o_forward_conta_se.py`, e a diferença é a de SM-P1: um tuplo `GAPS`
declarado e um `print` que passou a citá-lo. **Nenhuma asserção mudou.**

## 2 · AS CINCO FALTAS SÃO DERIVADAS, NÃO COPIADAS

`MISSING_AUTHORITY` passou de três itens para cinco. As duas novas são o
desempate `IT-OWN-003` vs `IT-OWN-ARPAV` (AU9a/AU9b) e a ausência de qualquer
escritor de identidade em runtime (AU10).

O censo passou a vê-las **onde elas já vivem**, pela forma do valor — um
dicionário que diz o que FALTA.

> **GAP RENDERED ≠ GAP DUPLICATED.**

E entram **aninhadas** debaixo do buraco que explicam, nunca ao lado dele:

> **A razão de um buraco estar aberto não é outro buraco.**

Achatá-las faria a tela dizer treze onde há nove. A contagem diz as duas coisas
separadas: **9 buracos, 5 faltas medidas dentro deles**.
`CHANNEL_IDENTITY_NOT_RESOLVED` continua **OPEN**, e nenhum dono de identidade
foi desenhado porque nenhum existe.

## 3 · A IMPRESSÃO, E A MUTAÇÃO OBRIGATÓRIA

```
IMPRESSAO_DO_CARIMBO = IGUAL           árvore integrada, 1504 ficheiros-fonte
mutação numa fonte, COMMITADA          42abff84 -> f2afee04, GATE_EXIT=1
mutação numa fonte, por commitar       disco != índice, exit 1
```

**Reprova antes do deploy**, no passo `2b` do portão do mapa. E o paradoxo
`HEAD~1` continua dissolvido, medido nesta árvore:

```
PROVENANCE.HEAD  = 070d9449   (informativo, e nomeia o commit ANTERIOR)
HEAD real        = 8b5e1a40
IGUAIS           = False      <- e NÃO precisa de ser
FINGERPRINT      = igual dos dois lados
```

`.vercelignore` **inalterado**. Ficheiros adicionais enviados ao contentor:
**0**. Na build real, **1130 de 1516** continuam fora do disco — e
`MAP_BELONGS_TO_DEPLOYED_TREE` deu **`true`** na mesma.

## 4 · OS TRÊS PORTÕES, NO CI REAL

```
SYSTEM MAP CHECK   success    3/3 passos corridos
MAP RULES CHECK    failure    8/8 passos corridos · falhou só o 4
COLETA CHECK       failure    10/10 passos corridos · falhou só o 3
```

Os dois vermelhos são **um passo cada**, e os mesmos de antes de SM-P1.
`NEW_FAILURES = 0`.

## 5 · O BROWSER, SOBRE OS BYTES PUBLICADOS, SEM INTERCEPTAÇÃO

Zero `page.route`, zero mock, zero fixture. A página fez as **suas** chamadas e
recebeu as respostas **verdadeiras** do GitHub.

| verificação | resultado |
|---|---|
| o mapa abre | ✅ 145 peças |
| erros JS | ✅ só `/favicon.ico` 404, que o preview real também não serve |
| source branch | ✅ `claude/system-map-freshness-v1` |
| deployed commit | ✅ `8b5e1a40` |
| latest head | ✅ `8b5e1a40`, de uma resposta real do GitHub |
| source fingerprint | ✅ igual dos dois lados |
| system map check | ✅ `PASS`, lido do portão do CI |
| map rules gate | ✅ `FAIL`, **visível** |
| collection gate | ✅ `FAIL`, **visível** |
| gaps | ✅ 9 |
| as 5 faltas da M2I | ✅ visíveis e derivadas |
| CURRENT só se provado | ✅ 🟢 `CURRENT` |

O portão da coleta **não estava na tela** e este browser apanhou-o. Está agora,
fora da decisão de frescura e à vista.

> **MAPA ACTUAL ≠ SISTEMA SAUDÁVEL. FRESCURA VERDE ≠ TUDO VERDE.**

## 6 · ⚠️ O BLOQUEIO, MEDIDO

A chamada tem de partir do browser **sem credencial**. Medido no browser real:

```
x-ratelimit-limit: 5000
```

**5000 é o limite de quem se identifica. Anónimo são 60.** Todo o HTTPS deste
contentor atravessa um proxy que injecta autenticação — o Chromium até recusa os
certificados dele por não os conhecer, o que prova a interceptação. Portanto a
chamada foi **real** e **não interceptada por mim**, mas **não foi anónima**.

> **REPO PÚBLICO E CORS ABERTO NÃO SÃO O MESMO QUE PEDIDO ANÓNIMO ACEITE.**

Isto **não** é uma falha de arquitetura: falhando a chamada, a frescura cai para
`UNKNOWN` e a tela fica **branca** com o motivo. Fica declarado como buraco,
`LIVE_HEAD_LOOKUP_NEEDS_SERVER_SIDE_READONLY_PROXY`, em
`system-map/scripts/verificar_deploy.py`, e o mapa desenha-o.

**Nenhum proxy foi implementado, e nenhuma credencial foi para o browser.**

## 7 · 37 / 42 / 23

Continuam separados e medidos nesta árvore. **MENCIONADO ≠ TEM FICHA.**

---

## O MENOR PRÓXIMO PASSO

Abrir
`https://sintonia-eame-preview-git-claude-system-726648-london-creative.vercel.app/system-map/`
**num browser numa rede normal**, sem proxy de agente, e ler o painel:

- `Latest canonical head` preenchido → a chamada anónima funciona, e
  `SYSTEM_MAP_PROMOTION_READY` passa a `YES`;
- `Latest canonical head` em `UNKNOWN` → é preciso a ponte server-side
  read-only, e só então.

É uma leitura de trinta segundos, e é a única coisa que falta.
