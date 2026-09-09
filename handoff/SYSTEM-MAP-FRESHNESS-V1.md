# HANDOFF · SM-FRESHNESS-V1

**O mapa continua a ser a foto de UMA árvore. Isso está certo. O defeito era que
ele podia mostrar uma foto velha sem avisar.**

Este trabalho está numa branch isolada, **não integrada**, porque a M2 estava a
correr na branch canónica durante toda a missão. Nada aqui tocou nela.

---

## O QUE ESTE HANDOFF DIZ EM UMA LINHA

O System Map passou a conseguir dizer, na própria tela, **qual branch, qual
commit está servido, qual é o commit mais novo, e se eles batem** — e, quando não
consegue conferir, diz `UNKNOWN` em vez de ficar verde.

---

## OS CAMPOS DE INTEGRAÇÃO

| | |
|---|---|
| `SYSTEM_MAP_FIX_BRANCH` | `claude/system-map-freshness-v1` |
| `SYSTEM_MAP_FIX_HEAD` | *(ver `git rev-parse origin/claude/system-map-freshness-v1`)* |
| `BASED_ON_CANONICAL_HEAD` | `8e1947d2d5dac39ba831ca6e637e14927a43101a` |
| `LATEST_CANONICAL_HEAD_SEEN` | `ef9803bbb98fcbb14cb9a31b16ef61fba23980e0` (M2 fechada) |
| `PREVIEW_URL` | `https://sintonia-eame-preview-git-claude-system-726648-london-creative.vercel.app/system-map/` |
| `OFFICIAL_PROMOTED` | **NÃO** |
| `M2_TOCADA` | **NÃO** |

A canónica andou **quatro vezes** durante a missão: `8e1947d2 → 700da777 →
ef9803bb`, mais o `c293be65` que já lá estava. **Não foi feito rebase** — perseguir
uma branch em movimento é como acertar num alvo que anda.

---

## FILES_CHANGED

Tudo em System Map ou metadata de build. **Zero ficheiros funcionais fora disso.**

```
.github/workflows/system-map.yml                 passos 4k, 7 e 8
.github/workflows/system-map-deploy-verify.yml   NOVO · o verificador pós-deploy
.gitignore                                       o artefato de deploy não se commita
AGENTS.md · system-map/README.md                 a lei escrita
package.json                                     o build corre o publicador
system-map/app/freshness.js                      NOVO · a lei da frescura
system-map/app/{index.html,map.js,map.css}       o bloco SYSTEM MAP STATUS
system-map/scripts/CADEIA-DO-MAPA.json           NOVO · a cadeia, num sítio só
system-map/scripts/publicar_no_deploy.mjs        NOVO · corre no BUILD
system-map/scripts/verificar_deploy.py           NOVO · corre DEPOIS do deploy
system-map/scripts/{generate,validate}_system_map.py   lêem a cadeia
system-map/tests/test_freshness.mjs              NOVO · 49 provas
system-map/tests/test_system_map.py              as provas SMF
system-map/data/*.generated.json                 derivados, regerados
italia-portale/client/system-map/*               a cópia publicada, regerada
```

---

## INTEGRATION_CONFLICT_RISK · **BAIXO, E MEDIDO**

`git merge-tree` contra `ef9803bb` dá conflito em **cinco ficheiros, e os cinco
são DERIVADOS**:

```
CONFLICT  system-map/data/state.generated.json
CONFLICT  system-map/data/architecture.generated.json
CONFLICT  system-map/data/casco.generated.json
CONFLICT  system-map/data/sources.generated.json
CONFLICT  italia-portale/client/system-map/state.generated.json
```

**`architecture.declared.json` funde-se limpo** — a canónica acrescentou
`C-ROTA-M2` e `C-PROVA-ROTA-M2-ATRAVESSA` noutro sítio do ficheiro. Nenhum
ficheiro de código conflita.

### EXACT_MERGE_PLAN

**Derivado não se resolve à mão. Regenera-se.**

```bash
git checkout claude/collection-foundation-integration-v1
git merge claude/system-map-freshness-v1        # 5 conflitos, todos derivados

# NÃO edite os cinco. Aceite qualquer lado e mande o gerador decidir:
git checkout --theirs system-map/data/*.generated.json \
                      italia-portale/client/system-map/state.generated.json

python3 system-map/scripts/scan_repo.py
python3 system-map/scripts/scan_sources.py
python3 system-map/scripts/scan_casco.py
python3 system-map/scripts/censo_da_coleta.py
python3 system-map/scripts/pente_fino_da_coleta.py
python3 system-map/scripts/generate_system_map.py
python3 system-map/scripts/validate_system_map.py     # tem de dar PASS
node system-map/tests/test_freshness.mjs              # 49 provas
git add -A && git commit
```

---

## ⚠️ O QUE FICOU POR FAZER, COM NOME

### 1 · O mapa fica `⚪ UNKNOWN` na Vercel, e isso está certo

**Medido no log de uma build real:**

```
Found .vercelignore
Removed 1125 ignored files defined in .vercelignore
SCAN=OK · arquivos=311          (em vez de 1338)
MAPA=OK · pecas=140 (🟢47 🟡57 🔴11 ⚪25) · cobertura=297/311
```

Python 3.12 e git **existem** no contentor. O commit implantado chega certo. O
problema é que **a árvore da build não é a árvore do repositório**: o
`.vercelignore` não envia `/build /data /docs /handoff /research /supabase /tests
/.github`, e regenerar ali dá o mapa **real de uma árvore mutilada**.

O publicador passou a **recusar-se** a fazer isso, e a tela diz `UNKNOWN` com o
número ao lado. **STALE continua a funcionar na mesma** — staleness prova-se
sozinha, sem o validador.

**Para o mapa poder ficar 🟢 na Vercel** é preciso que o contentor receba a
árvore inteira: afrouxar o `.vercelignore`. **Não foi feito aqui.** Aquele
ficheiro é uma tranca de segurança com o porquê escrito dentro dele — impedir que
o acervo, a investigação e os pacotes canónicos sejam sequer *enviados* para um
contentor cujo output é público. Trocar uma tranca por uma bolinha verde é
decisão do dono, não de quem passa.

> **Subir não é servir** — `outputDirectory` continua a ser `italia-portale/client`.
> Mas o `.vercelignore` é a segunda fechadura, e quem a abre tem de saber que a abriu.

### 2 · O job `check` está **vermelho na linha canónica**, e já estava

`check` dá `failure` em `8e1947d2`, `700da777` e `ef9803bb` — **antes desta
missão** — e o corte é no **passo 3**, `medidas/padrao_da_coleta.py`:

```
PADRAO_DA_COLETA=FAIL · alguma coisa piorou desde o chão
mudou: coleta/executor_texto_de_pdf.py, coleta/golden_path_pdf.py,
       coleta/social_envelope.py, coleta/social_rotas.py, coleta/youtube_oficial.py
```

Corrido no commit base `8e1947d2` e na minha branch, o relatório sai **byte a
byte idêntico**. Não é meu, e é da coleta — território da M2.

Como o passo 3 corta antes, **os passos novos nunca chegaram a correr no
GitHub**. Foram corridos localmente, exactamente como estão escritos:

```
4k · TESTES_FRESCURA=PASS · 49 provas
6  · SEM_SEGREDO=YES
7  · ARTEFATO_DE_DEPLOY_NASCE_NO_BUILD=YES
8  · BUILD_REGENERA=YES · DEPLOYED=b601b9ec · GENERATED_FROM=b601b9ec · MESMA_ARVORE=SIM
```

E o passo 4, `test_system_map.py`, reprova em duas provas que **também já
reprovavam** em `8e1947d2`, e também são da coleta:

```
regua_que_carimba_nao_e_regua_que_mede
E2_receita_continua_com_um_consumidor
```

**NEW_FAILURES desta missão = 0.**

O workflow novo, `system-map-deploy-verify`, **passa**: `verificar` deu
`success` em `b601b9ec` — o commit empurrado foi mesmo o commit publicado.

### 3 · Nada foi recarimbado

Quatro peças do mapa que eu reescrevi ficam em 🟡 «precisa de releitura humana».
`--stamp` carimba **todos** os ficheiros, e seis dos que estão por reler são da
M2 — eu não os li. **Recarimbar sem reler é o único jeito de mentir neste
sistema.** Depois da integração, quem reler que carimbe.

---

## O QUE MUDA NA PRÁTICA, PARA QUEM ABRE O MAPA

No topo aparece um botão. Ele diz uma de quatro coisas:

| | | |
|---|---|---|
| 🟢 | `CURRENT` | o commit servido é a cabeça atual desta linha, e o validador passou |
| 🔴 | `STALE` | barra vermelha, largura toda, sem botão de fechar |
| ⚪ | `FRESHNESS UNKNOWN` | não deu para conferir — **e isso nunca é verde** |
| 🔴 | `SYSTEM MAP INVALID` | a proveniência contradiz-se, ou o validador reprovou |

E um painel com os factos separados: `REPOSITORY`, `SCOPE: THIS BRANCH / THIS
TREE ONLY`, `SOURCE BRANCH`, `GENERATED FROM`, `DEPLOYED COMMIT`, `LATEST
CANONICAL HEAD`, `SYSTEM MAP CHECK`, `MAP COVERAGE`.

**`624/1321` era COBERTURA**, e passou a chamar-se `MAP COVERAGE`: quantos
ficheiros rastreados desta árvore o mapa classifica. Nunca foi um indicador de
atualização, e `decidir()` **não recebe cobertura** — o teste prova isso pela
assinatura da função, não pela confiança.

---

## PREVIEW · o que foi verificado, e como

O preview foi aberto num browser real sobre **os bytes que estão publicados**
(descarregados do URL e servidos localmente, com a chamada ao GitHub
interceptada para tornar cada cenário determinístico).

| verificação | resultado |
|---|---|
| o mapa abre | ✅ 140 peças desenhadas, zero erros de JS |
| branch correta | ✅ `claude/system-map-freshness-v1` |
| deployed commit correto | ✅ `b601b9ec`, de `VERCEL_GIT_COMMIT_SHA` |
| generated source correto | ✅ `33468386`, o mapa commitado, intacto |
| coverage correto | ✅ `641 / 1339 tracked files`, rotulado `MAP COVERAGE` |
| sync status correto | ✅ `⚪ FRESHNESS UNKNOWN`, com o motivo na tela |
| STALE simulado fica vermelho | ✅ `🔴 STALE · MAP IS 7 COMMITS BEHIND`, barra que não fecha |
| UNKNOWN não vira verde | ✅ |
| nada fora de `/system-map/` mudou | ✅ zero ficheiros funcionais fora do escopo |

O guarda de completude foi provado **duas vezes**: numa simulação local (clone
com as pastas do `.vercelignore` apagadas do disco e o índice intacto) e na
build real da Vercel, que respondeu `1126 dos 1504 ficheiros rastreados não
chegaram ao disco` e **recusou-se a regenerar**. O mapa servido continua o
correcto: 1339 ficheiros rastreados, 0 peças partidas.

**PRODUÇÃO NÃO FOI PROMOVIDA.** E há um facto a registar sobre o alias oficial:
`sintonia-eame-preview.vercel.app/system-map/` responde **404**. Todos os
deployments recentes têm `target: null` — são preview — e o projecto diz
`live: false`. O alias de produção serve um deployment **anterior ao System Map
existir**. Quem promover tem de saber que está a promover a primeira versão do
mapa para aquele endereço, e não a substituir uma.

---

**Nenhuma credencial no browser**, e não por disciplina: o repositório é público
(medido), e a API do GitHub responde à cabeça da branch sem autenticação e com
CORS aberto. Se deixar de ser público, a chamada falha e a tela cai para
`UNKNOWN`. A partir desse dia, medir ao vivo exige credencial — e credencial vive
**server-side**, numa função mínima e read-only. Nunca no browser.
