# SM-P2 · URL CANÓNICA FIXA

## O ENDEREÇO

```
https://sintonia-eame-preview.vercel.app/system-map/
```

É este. Não muda com commit novo, build nova, ou mudança de nome da linha
geradora. É o primeiro facto deste documento de propósito: um handoff que abre
com o URL de um deployment ensina o dono do produto a seguir deployments.

    O ENDEREÇO É DO PRODUTO. O DEPLOYMENT É DA ENGENHARIA.

**Estado: falta um clique.** Tudo o que autoriza a promoção está medido e
passa. A promoção em si não pôde ser executada — ver *O QUE FALTA*, no fim.

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

## O PROCESSO, DAQUI PARA A FRENTE

```
commit → preview da branch → SYSTEM MAP CHECK → PORTAL REGRESSION CHECK
       → READY → promoção explícita → o mesmo endereço de sempre
```

Os previews continuam a existir e são úteis: são a bancada da engenharia.
**Não se entregam ao dono do produto como endereço.**

    PREVIEW URL       ≠  USER URL
    PREVIEW READY     ≠  CANONICAL PUBLISHED
    LATEST DEPLOYMENT ≠  APPROVED DEPLOYMENT

`AUTO_PROMOTION_CANDIDATE = NO`, por agora. O que falta para o ser está listado
no contrato — e um dos três itens é um segredo de promoção no CI, que é matéria
da Security Foundation e não desta missão.

---

## QUANDO O GITHUB FICAR PRIVADO

`FUTURE_PRIVATE_REPO_COMPATIBLE = YES`. O endereço não depende de o repositório
ser público. O que depende é a leitura da cabeça remota que a tela faz do
browser para calcular frescura — e essa já falha para UNKNOWN, nunca para verde
falso. Muda o backend da frescura; o host e a rota ficam iguais.

    CLIENT NEEDS HEAD VALUE  ≠  CLIENT NEEDS GITHUB CREDENTIAL.

`LIVE_HEAD_LOOKUP_SECURITY_ARCHITECTURE = TEMPORARY`.

---

## O QUE FALTA — E É UM CLIQUE

A promoção não foi executada. Não por falta de prova: **por falta de
credencial**. Este ambiente não tem token da Vercel, não tem a CLI, e o servidor
MCP da Vercel não expõe operação de promote nem de alias. Ler deployments, sim;
mudar o alias, não.

Não se improvisou à volta disso. Havia um caminho — publicar ficheiros
directamente com `target: production` — e foi recusado: criaria um segundo dono
do mesmo endereço, sem metadata de Git, contra a lei que este repositório já
tinha escrita («UMA AUTORIDADE DE DEPLOY»).

**O passo mínimo**, no painel da Vercel, projecto `sintonia-eame-preview`:

```
promover   dpl_A7LS4FUDJnLweSoqVaSi9UifaBeB
           commit 22373dd43f403bc31a687f71d5a84a47d42d2cc4
           branch claude/system-map-canonical-url-v1
           state  READY

rollback   dpl_3MQEgpUsrc7d8VvSL47gQRU74HKA
           commit a4fb6d81681094925ccfd1638bc7386cbec6f4d4
```

Correr o portão outra vez imediatamente antes, e depois de promover confirmar
que `/` e `/system-map/` respondem 200 no host canónico.

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
