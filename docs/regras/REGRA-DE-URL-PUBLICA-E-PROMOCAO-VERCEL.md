# REGRA DE URL PÚBLICA E PROMOÇÃO NA VERCEL

Um endereço só para o Luciano, e o que tem de acontecer para ele estar certo.
**Data:** 2026-09-05

| | |
|---|---|
| **PROJETO VERCEL** | `sintonia-eame-preview` · `prj_rKjzMNHiB2ulP8ev5bmYYeUFUTwe` |
| **TEAM** | London Creative · `team_jyZYzZOZwYWn06jOCXsrnU9X` |
| **REPOSITÓRIO** | `lucianodalondon-sys/eame-sintonia` |

---

## 1 · O ENDEREÇO É UM SÓ

```
https://sintonia-eame-preview.vercel.app
```

É o **alias de produção** do projeto. É o único endereço que se entrega ao Luciano,
em qualquer mensagem, relatório ou reunião.

Os endereços `sintonia-eame-preview-<hash>-london-creative.vercel.app` são **efémeros**:
existem um por build, não têm dono, e o próximo build deixa o anterior a servir uma versão
que ninguém mais está a olhar. Servem para **testar**, nunca para **entregar**.

> **UM ENDEREÇO QUE MUDA A CADA BUILD NÃO É UM ENDEREÇO: É UM RECIBO.**
> **QUEM O ENTREGA ESTÁ A PEDIR AO OUTRO QUE GUARDE A VERSÃO EM VEZ DE OLHAR PARA ELA.**

O Preview **continua a existir** e continua a ser onde se testa. O que muda é o fim da
linha: nada é dado como validável enquanto não estiver no endereço curto.

---

## 2 · A REGRA

Quando uma versão da **Linha B** é declarada **aprovada / para validação principal**:

1. **esperar** o deployment ficar `READY`;
2. **promover EXATAMENTE esse deployment** para Production — o que foi testado, não um
   irmão dele;
3. **não rebuildar** se não for necessário — a promoção nativa reaproveita o build que já
   passou;
4. **confirmar** que `sintonia-eame-preview.vercel.app` aponta para esse deployment e para
   esse commit;
5. **entregar o endereço curto** como URL principal, e mais nenhum.

```
Linha B aprovada → Preview READY → promote → https://sintonia-eame-preview.vercel.app
```

---

## 3 · O QUE "PROMOVER" SIGNIFICA AQUI

Há um detalhe medido neste projeto que tem de estar escrito, senão a próxima pessoa
conclui que a promoção falhou:

**A promoção nativa cria um DEPLOYMENT ID NOVO.** Ela não muda o `target` do deployment de
Preview — cria um deployment de produção que herda o output daquele. O que **não** muda é
o commit.

Medido na promoção anterior deste mesmo projeto (`dpl_75E1qUzitEuRXfJCoiSwW41wyUyw`):

| campo | valor | o que prova |
|---|---|---|
| `target` | `production` | é o deployment que o alias serve |
| `meta.action` | `promote` | veio de promoção, não de build novo |
| `meta.originalDeploymentId` | `dpl_5wLcU7hLvK1TMq72LzLmqm16BBwx` | **qual** Preview foi promovido |
| `source` | `redeploy` | reaproveitou o output, não recompilou da origem |
| `meta.githubCommitSha` | igual ao do Preview | **o commit atravessou intacto** |

> **O ID MUDA. O COMMIT NÃO.**
> **A PROVA DE QUE SE PROMOVEU O QUE SE TESTOU É `originalDeploymentId` + O SHA,
> NUNCA O ID DO DEPLOYMENT.**

---

## 4 · COMO SE PROMOVE — três caminhos, todos nativos

Qualquer um serve. O que **não** serve está no ponto 5.

**Dashboard** — `vercel.com/london-creative/sintonia-eame-preview` → o deployment →
`⋯` → **Promote to Production**.

**CLI**

```bash
vercel promote sintonia-eame-preview-<hash>-london-creative.vercel.app \
  --scope london-creative --token "$VERCEL_TOKEN"
```

**REST API**

```bash
curl -X POST \
  "https://api.vercel.com/v10/projects/prj_rKjzMNHiB2ulP8ev5bmYYeUFUTwe/promote/<DEPLOYMENT_ID>?teamId=team_jyZYzZOZwYWn06jOCXsrnU9X" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

---

## 5 · O QUE NÃO SE FAZ

| proibido | porquê |
|---|---|
| criar **projeto novo** na Vercel | multiplica endereços — é exatamente a confusão que esta regra fecha |
| **copiar ficheiros** / `vercel deploy --prod` a partir do disco | entrega uma versão que **nunca passou pelo Preview aprovado**; o commit deixa de ser rastreável |
| **push vazio** ou re-push para forçar build de produção | é rebuild, e rebuild pode dar resultado diferente do que foi aprovado |
| mudar a **production branch** do projeto para promover | promove por acidente tudo o que entrar nessa branch a seguir |
| entregar `*-london-creative.vercel.app` ao Luciano | ponto 1 |

---

## 6 · COMO SE PROVA — bloco obrigatório

Toda promoção termina com este bloco preenchido. Sem ele, não está entregue.

```
PUBLIC_URL                       = https://sintonia-eame-preview.vercel.app
DEPLOYMENT_URL                   = <url efémera do deployment promovido>
DEPLOYMENT_ID                    = <dpl_...>
COMMIT                           = <sha completo>
BRANCH                           = <ref>
TARGET                           = production
ALIAS_POINTS_TO_SAME_DEPLOYMENT  = SIM/NÃO
```

A última linha **não se afirma, mede-se**. O endpoint de deployment da Vercel resolve
aliases, portanto a pergunta *"o que é que o endereço curto está a servir?"* tem resposta
direta:

```bash
curl -s "https://api.vercel.com/v13/deployments/sintonia-eame-preview.vercel.app?teamId=team_jyZYzZOZwYWn06jOCXsrnU9X" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["id"], d["target"], d["meta"]["githubCommitSha"], d["meta"].get("originalDeploymentId"))'
```

`ALIAS_POINTS_TO_SAME_DEPLOYMENT = SIM` só quando o `id` devolvido é o do deployment
promovido **e** o `githubCommitSha` é o commit aprovado.

---

## 7 · MEDIÇÃO DE 2026-09-05 — o estado encontrado

O que o endereço curto servia quando esta regra foi escrita, contra o que a Linha B
tinha aprovado:

| | endereço curto (produção) | Linha B aprovada |
|---|---|---|
| **DEPLOYMENT_ID** | `dpl_75E1qUzitEuRXfJCoiSwW41wyUyw` | `dpl_BqaTXKbJtTXoB4txA8FQAizPTooi` |
| **DEPLOYMENT_URL** | `sintonia-eame-preview-nfyf8d4o2-london-creative.vercel.app` | `sintonia-eame-preview-leskxxw1z-london-creative.vercel.app` |
| **COMMIT** | `98bd0f93a2eda55923aba17d7f108b2ccf76793d` | `cfbd8a460f3d548ba6542b4701f22fc674d7f81e` |
| **BRANCH** | `claude/meeting-portal-integration-build-dr7jqr` | `claude/meeting-portal-integration-build-dr7jqr` |
| **TARGET** | `production` | `null` (preview) |
| **READY** | 2026-09-04 13:44:27 UTC | 2026-09-05 06:45:58 UTC |

`98bd0f9` é ancestral de `cfbd8a4`: o endereço curto estava **22 commits atrasado**.
`ALIAS_POINTS_TO_SAME_DEPLOYMENT = NÃO`.

Foi exatamente este atraso que produziu a confusão de URLs — o endereço curto não estava
errado, estava **velho**, e por isso cada sessão acabava a mandar a sua própria URL efémera.

> **UM ALIAS DESATUALIZADO NÃO FALHA. ELE RESPONDE 200 COM A VERSÃO DE ONTEM,**
> **E QUEM O LÊ NÃO TEM COMO SABER.**

Proteção de acesso verificada no mesmo dia: `passwordProtection`, `ssoProtection` e
`trustedIps` todos desligados — o endereço curto abre sem login.

---

## 8 · ANEXO — o workflow que executa a regra

`.github/workflows/promover-linha-b.yml`

Dispara **só à mão** (`workflow_dispatch`) — nunca sozinho — porque quem aprova a Linha B
é uma pessoa, não um push. Pede dois campos:

| campo | |
|---|---|
| `deployment` | o `dpl_...` ou o hostname efémero do Preview **já READY** |
| `commit_esperado` | o SHA aprovado da Linha B |

E tem **três portões, todos fail-closed**:

1. **antes de promover** — o alvo tem de estar `READY` **e** o seu `githubCommitSha` tem de
   ser o commit aprovado. Se o Preview ainda constrói, ou se o ID que alguém colou é de
   outro commit, nada é promovido;
2. **a promoção** é a nativa: `POST /v10/projects/{id}/promote/{deploymentId}`. Não
   constrói, não copia ficheiros, não toca no repositório;
3. **depois de promover** — resolve `sintonia-eame-preview.vercel.app` contra a API e só dá
   verde quando o que o alias serve é `target=production`, `READY`, com o commit aprovado e
   com `originalDeploymentId` igual ao alvo. Espera até 5 minutos; se não bater, **falha** e
   imprime o que encontrou.

> **O SEGUNDO PORTÃO É O QUE FALTAVA.**
> **PROMOVER SEM VOLTAR A LER O ALIAS É ASSUMIR QUE CORREU BEM.**

O job termina imprimindo o bloco de prova do ponto 6, já preenchido — é esse texto que se
entrega, e é a única coisa que conta como promoção feita.

**Pré-requisito:** o secret `VERCEL_TOKEN`. Cria-se em `vercel.com/account/tokens`, com
âmbito sobre a team **London Creative**, e guarda-se em **Settings → Secrets and variables
→ Actions** do repositório, com esse nome exato. Sem ele o primeiro passo pára e diz porquê.

O workflow vive na branch onde esta regra foi escrita; o GitHub só o oferece no menu
**Actions** depois de ele chegar à branch por omissão do repositório.
