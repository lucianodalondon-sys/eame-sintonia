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

### 2 · O `SYSTEM MAP CHECK` do CI está **vermelho na linha canónica**, e já estava

`check` dá `failure` em `8e1947d2`, `700da777` e `ef9803bb` — **antes desta
missão**. Duas provas reprovam, e são da coleta, não do mapa:

```
regua_que_carimba_nao_e_regua_que_mede
  O rastro da coleta está em Z-MEDIDAS, medido como Z-REGRAS
E2_receita_continua_com_um_consumidor
  consumidores da receita: C-ESTRADAS-IT, C-ORQUESTRADOR, C-PROVA-COLETA
```

**NEW_FAILURES desta missão = 0.**

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

**Nenhuma credencial no browser**, e não por disciplina: o repositório é público
(medido), e a API do GitHub responde à cabeça da branch sem autenticação e com
CORS aberto. Se deixar de ser público, a chamada falha e a tela cai para
`UNKNOWN`. A partir desse dia, medir ao vivo exige credencial — e credencial vive
**server-side**, numa função mínima e read-only. Nunca no browser.
