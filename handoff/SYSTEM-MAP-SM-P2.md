# SM-P2 · URL CANÓNICA FIXA

## O ENDEREÇO

```
https://sintonia-eame-preview.vercel.app/system-map/
```

É este. Não muda com commit novo, build nova, ou mudança de nome da linha
geradora. É o primeiro facto deste documento de propósito: um handoff que abre
com o URL de um deployment ensina o dono do produto a seguir deployments.

    O ENDEREÇO É DO PRODUTO. O DEPLOYMENT É DA ENGENHARIA.

**Estado: PROMOVIDO E PROVADO.** O alias serve o deployment integrado.

---

## O QUE ESTAVA ERRADO

O System Map vivia em `claude/system-map-freshness-v1`, uma linha que se tinha
separado do portal trinta commits antes. Promover o deployment dessa linha
punha o mapa no endereço certo **e levava o portal de volta para antes da Label
Intelligence**.

Medido, não suposto: esse deployment devolve HTTP 200 em `/portale` e ao mesmo
tempo deixa de servir `italy-label-intelligence.js` e `italy-label-lexicon.js`.

    A ROTA RESPONDER NÃO É A PÁGINA ESTAR INTEIRA.
    /system-map/ = 200  NÃO PROVA  / = correcto.

Por isso a promoção directa (opção A) foi recusada.

---

## O QUE SE FEZ EM VEZ DISSO

Uma árvore de release: a junção real, por Git, do commit que serve hoje o alias
(`a4fb6d81`, linha do portal) com a linha do mapa (`9624ad08`).

Oito conflitos, todos em ficheiros **gerados**. O único delta do lado do mapa
era o renomear de 149 scripts para gavetas (`scripts/x.py` → `leis/`, `coleta/`,
`superficie/`, `motor/`, `provas/`, `portoes/`). Resolvidos tomando o conteúdo
novo do portal e reaplicando esse mesmo mapa de renomeações mecanicamente, a
partir do próprio commit que o fez.

    CONFLITO EM DERIVADO NÃO SE ARBITRA. REGENERA-SE.

O mapa foi depois **regenerado** sobre a árvore integrada, pela cadeia que já
existia — não copiado de outra linha.

---

## O QUE FICOU PROVADO

| | |
|---|---|
| Portões do portal | **73/73** a passar (Label Intelligence 34/34, barras de busca 17/17) |
| `SYSTEM_MAP_CHECK` (árvore completa) | **PASS**, P1..P10, sem drift |
| Delta do portal, byte a byte | `/accesso` idêntico · `/` só a barra de preview da Vercel · `/portale` 4 strings de caminho em comentários |
| Regressões não intencionais | **0** |
| `.vercelignore` | **não mudou** (continua a não enviar 1137 de 1524 ficheiros) |
| Collection | **0** ficheiros funcionais tocados |
| Browser, no mapa servido | abre · **0 erros JS** · frescura, System Map Check, Map Rules e Collection em linhas separadas · 9 buracos com as 5 faltas da M2I dentro |

Os vermelhos herdados continuam vermelhos e continuam à vista.

    INHERITED RED  ≠  NEW DEPLOY REGRESSION.
    UNKNOWN        ≠  PASS.

---

## O CONTRATO E O PORTÃO

- [`system-map/CANONICAL-PUBLICATION.json`](../system-map/CANONICAL-PUBLICATION.json)
  — host, rota, dono da publicação, branches com autoridade, condições.
- [`system-map/scripts/portao_da_promocao.py`](../system-map/scripts/portao_da_promocao.py)
  — decide se um deployment pode ficar atrás do endereço.

`CANONICAL_DEPLOY_OWNER = explicit promotion only`. O alias não segue «o último
deploy de qualquer branch»: se seguisse, três linhas paralelas competiriam pelo
mesmo endereço e a última a construir ganhava. A Vercel continua a ser a única
autoridade que publica; a promoção escolhe qual dos deployments dela fica atrás
do alias.

O portão foi atacado antes de ser aceite. Contra o deployment do System Map
sozinho recusa por **duas vias independentes**: a branch não tem autoridade, e
os dois ficheiros que desapareceriam são nomeados. Recusa também commit errado,
deployment sem mapa, e ausência de alvo de rollback. E um socket que cai não é
um 404: o que fica por medir bloqueia a promoção em vez de a autorizar.

A lista de recursos exigidos não se escreve à mão — lê-se do canónico servido no
momento, por isso actualiza-se sozinha.

---

## O PROCESSO, DAQUI PARA A FRENTE — AUTOMATICO

A branch de produção do projecto Vercel é `release/canonical`. O que entra nela
vai ao ar sozinho, e nada mais vai.

```
commit  →  preview da branch de trabalho
        →  PR para release/canonical
        →  PROVENIENCIA · SYSTEM MAP CHECK · PORTAL REGRESSION CHECK
        →  merge
        →  o mesmo endereço de sempre, com a versão nova
```

**O dono do produto nunca promove.** Nunca promoveu por desenho; a primeira
promoção foi manual só porque a automação ainda não existia. Agora existe.

A conferência não desapareceu — mudou de sítio. Corria antes do clique; corre
antes do merge, que é o último momento em que reprovar ainda serve para alguma
coisa, porque depois do push já está no ar.

    LATEST DEPLOYMENT != APPROVED DEPLOYMENT — a não ser que alguém prove.

Os 73 portões do portal passam a correr em CI. Nunca tinham corrido. Enquanto a
publicação era um clique, um humano olhava; automatizar sem eles seria trocar um
humano atento por nada.

Os previews das branches de trabalho continuam a existir. São a bancada da
engenharia, e não se entregam ao dono do produto como endereço.

    PREVIEW URL  !=  USER URL.

### O 403 ERA PASSAGEIRO, E A FRESCURA FUNCIONA

Registado porque estava escrito o contrário neste ficheiro e no contrato: o
`403` do GitHub anónimo, visto no browser do dono do produto, **não era
permanente**. Era limite de pedidos. Voltou a responder sozinho.

Medido depois, na tela servida, e sem nada por medir:

```
LATEST CANONICAL HEAD   0affd2b2          ← lido ao vivo
SYSTEM MAP CHECK        PASS
MAP GATE (CI)           PASS
MAP RULES GATE (CI)     FAIL   ← vermelho herdado, à vista
COLLECTION GATE (CI)    FAIL   ← vermelho herdado, à vista
SYNC                    STALE · MAP IS 6 COMMITS BEHIND
```

O aparelho inteiro funciona. E o vermelho do SYNC não é defeito: é a tela a
dizer, sozinha, o que antes só se sabia perguntando a um engenheiro.

    A PERGUNTA «ESTÁ ACTUALIZADO?» DEIXA DE TER DONO HUMANO.

O STALE existia porque a versão do endereço só mudava quando alguém promovia,
e o trabalho continuava. Com a branch de produção a publicar sozinha, a branch
do endereço e o que está no ar deixam de se separar — e o verde passa a ser o
normal, com o vermelho a voltar a significar «há algo errado» em vez de
«ninguém clicou ainda».

`LIVE_HEAD_LOOKUP_SECURITY_ARCHITECTURE` continua `TEMPORARY`: quando o
repositório for privado, esta leitura deixa de funcionar e passa para o lado do
servidor. O endereço não muda.

### O QUE FALTA, E NÃO É CÓDIGO

Protecção de branch em `release/canonical`: exigir os três jobs, proibir push
directo. Sem isso o portão existe e pode ser contornado por quem tiver pressa.

    UM PORTAO QUE SE PODE CONTORNAR E UMA SUGESTAO.

Ao criar a regra, os três nomes foram guardados **numa linha só**, como se
fossem um check chamado `RELEASE · PROVENIENCIA RELEASE · SYSTEM MAP CHECK
RELEASE · PORTAL REGRESSION CHECK`. Esse check não existe e nunca vai existir:
o merge ficaria bloqueado para sempre.

    A MESMA ARMADILHA DO CÓDIGO, OUTRA VEZ, NA CONFIGURAÇÃO.

Os três têm de ser três linhas. Depois desta primeira passagem eles já correram,
e passam a aparecer prontos na busca do ruleset.

### E SE PRECISAR DE POUSAR UMA VERSÃO À MÃO

`portao_da_promocao.py` continua a existir para isso — um rollback, ou um
recurso. Não foi apagado por a automação ter chegado: o caminho automático é
para o dia normal, e um caminho manual provado é o que se tem no dia mau.

---

## QUANDO O GITHUB FICAR PRIVADO

`FUTURE_PRIVATE_REPO_COMPATIBLE = YES`. O endereço não depende de o repositório
ser público. O que depende é a leitura da cabeça remota que a tela faz do
browser para calcular frescura — e essa já falha para UNKNOWN, nunca para verde
falso. Muda o backend da frescura; o host e a rota ficam iguais.

    CLIENT NEEDS HEAD VALUE  ≠  CLIENT NEEDS GITHUB CREDENTIAL.

`LIVE_HEAD_LOOKUP_SECURITY_ARCHITECTURE = TEMPORARY`.

---

## A PROMOÇÃO — FEITA, E MEDIDA DEPOIS

O portão autorizou; a promoção foi executada no painel da Vercel (este ambiente
não tem credencial da Vercel, e o atalho de publicar ficheiros com
`target: production` foi recusado: criaria um segundo dono do mesmo endereço).

```
canónico    dpl_BP8bckP7YdG6ha5A3m2dpJiMdcJu
            commit a7a746b8af8183a4680e2d8593d9a3f40797305d
            branch claude/system-map-canonical-url-v1
            target production

rollback    dpl_3MQEgpUsrc7d8VvSL47gQRU74HKA
            commit a4fb6d81681094925ccfd1638bc7386cbec6f4d4
```

Medido **depois**, no host canónico, e não na API da Vercel:

| | |
|---|---|
| `/` · `/accesso` · `/portale` · `/system-map/` | 200 |
| `/` `/accesso` `/portale` | **byte a byte iguais** ao candidato provado |
| recursos referenciados pelo portal | 35/35 servidos |
| `italy-label-intelligence.js` · `italy-label-lexicon.js` | 200 — os dois que a promoção directa teria apagado |
| `MAP_BELONGS_TO_DEPLOYED_TREE` | PROVEN |
| regressões pós-promoção | **0** · rollback não foi preciso |

No browser, na tela servida pelo endereço canónico: o mapa abre, a frescura
fica branca com a frase «não é prova de que está actual», e os quatro estados
continuam em linhas separadas.

### O 403 DO GITHUB — MEDIDO NO BROWSER CERTO

`LATEST CANONICAL HEAD: UNKNOWN — GitHub respondeu 403`.

Ficou provado no browser do dono do produto, não só num contentor: a chamada
anónima ao GitHub é recusada. O SM-P1R suspeitava do proxy; agora sabe-se que
não era só isso.

Isto **não** derruba o endereço, e não derrubou a promoção, porque o modo de
falha é o certo: bolinha branca, frase a dizer que não é prova, e nenhum verde.

    UNKNOWN != PASS. FALHAR PARA BRANCO NAO E MENTIR DE VERDE.

O conserto é o que a Security Foundation já ia estudar — mover a leitura da
cabeça para o lado do servidor. Muda o backend da frescura; o endereço fica.
`LIVE_HEAD_LOOKUP_SECURITY_ARCHITECTURE = TEMPORARY`, e agora com uma medição
real por trás.

### O ALIAS É INDEPENDENTE DO DEPLOYMENT

Provado sem inventar mudança nenhuma: os commits deste handoff continuam a
gerar previews novos na branch, e o endereço canónico continua a servir
`a7a746b8`. O alias não segue o último build.

    MANY BUILDS. MANY PREVIEWS. ONE CANONICAL URL.

---

## SECÇÃO TÉCNICA — URLs DE ENGENHARIA

Não são o endereço. Estão aqui, em baixo, e não em cima, de propósito.

| | |
|---|---|
| candidato | `https://sintonia-eame-preview-2ctyz4llj-london-creative.vercel.app` |
| branch preview | `https://sintonia-eame-preview-git-claude-system-34de93-london-creative.vercel.app` |
| projecto | `prj_rKjzMNHiB2ulP8ev5bmYYeUFUTwe` · equipa `team_jyZYzZOZwYWn06jOCXsrnU9X` |

`sintonia-eame-preview.vercel.app` é o ambiente oficial de preview/demo da
Sintonia EAME. Dentro do ambiente actual é o endereço fixo do produto. Não é
afirmação de que será o domínio contratual final da ADAMA.
