# PLANO-INSTALACAO-SOCIAL — social-micro + social-qualificar + legacy-99-v5, numa ordem só (26/09)

⚠️ **Base = o vivo `83de0ccd`** (C9 instalada às 02:08, ff-only sobre `ce28040c`). O social foi refeito por cima
dele no ramo **`social-qualificar-v2`** (os mesmos 12 commits por cherry-pick, sem conflito; os commits de mapa
gerado não foram copiados — o mapa refaz-se pela cadeia). `social-qualificar-v1`/`social-micro-v1` ficam como
história: **não instalar esses**.

O coordenador instala; um escritor no vivo; nenhum passo daqui vai à rede. Este plano **não repete** os detalhes
de cada ramo — aponta para eles:

| ramo | SHA no GitHub (26/09 ~02:30) | o que traz | relatório do dono |
|---|---|---|---|
| `legacy-99-v5` | d8cc61c0 | A (importar só HTML), B antigo removido, **B = os 41 canais YouTube pela rota do Scrap** (`importar_do_coletor.py --pelo-scrap`), régua **D53** (VIDEO) | `ferramentas/legacy99v4/SEPARAR-A-B-V5.md` (SEPARAR-A-B-V5; falta-lhe a regressão por nome e o mapa, à espera da LOCK-PESADO) |
| **`social-qualificar-v2`** (contém a social-micro e a PROVA-TETO-SOCIAL) | ver o PRONTO desta entrega | PROVA-TETO-SOCIAL, precisão de data/lugar na Sala, `semear_qualify_social.py --candidatas`, medida do yt-dlp | `SOCIAL-MICRO-PLANO.md`, `SOCIAL-QUALIFICAR.md` |

## O que se mediu para esta ordem (sem juntar nada)

- **`social-qualificar-v2` parte de `83de0ccd`** → ff-only sobre o vivo de hoje = **SIM**.
- **`legacy-99-v5` (d8cc61c0) ainda parte de `ce28040c`** → sobre `83de0ccd` já **não** é ff. Duas saídas: a
  SEPARAR-A-B-V5 refaz-se sobre `83de0ccd` (ou sobre o social), ou entra por `--no-ff`.
- **Juntar a v5 por cima do social não dá conflito**: `git merge-tree --write-tree origin/legacy-99-v5
  social-qualificar-v2` escreveu a árvore 7ee0d306 sem ficheiro em conflito (com a C9 incluída, porque o v2 a
  contém). Refazer com os SHAs finais antes de instalar.
- **Canais:** os 41 da v5 e os 9 da SOCIAL-QUALIFICAR não têm canal nem SOURCE_ID em comum (medido pela
  SEPARAR-A-B-V5). A colisão está guardada nos dois lados (bloco 4 e worker recusam um 2.º dono do mesmo canal).
- **A D53 da v5 vale para a micro social.** A régua julga pela fase do CONTRATO (`canal-youtube`), e a micro colhe
  `audio-youtube` (D36). Conferido no código: o contrato dos 9 canais tem `ACQUISITION.CHANNEL_ID`, e o adaptador de
  áudio escreve as 4 provas (`SOURCE_URL` watch?v=, `NATIVE_ID`, `RAW.TITLE`, `PUBLISHED_AT` do info.json,
  `CHANNEL_ID`). Um vídeo sem data reprova — é o comportamento certo, não defeito. **Não corrido** sobre um recibo
  real (não há recibo de áudio novo no disco).
- **Nenhum dos dois ramos mexe nos 16 livros sujos do vivo** (medido para o social; a v5 idem no relatório dela).

## A ORDEM

**0 · Antes (bot parado)**
- `touch curadoria/PARAR.flag`; esperar a volta acabar.
- Confirmar `git rev-parse HEAD` = `83de0ccd`. Se andou: **parar** e pedir rebase.
- Corte com sha256 dos livros que os passos 2 e 4 escrevem: `curadoria/italy_contracts_curator.json`,
  `regras/italy_contracts_onboarded.json`, `curadoria/LIFECYCLE-*.json`, `curadoria/DESBLOQUEIO-LEDGER-V1.jsonl`,
  `curadoria/SOURCE-ID-ALLOCATION-V1.json`, `candidatas/FONTES-CANDIDATAS.json`.

**1 · Código social — ff-only** (é o que já parte do vivo de hoje)
```
git fetch origin && git merge --ff-only origin/social-qualificar-v2
```
O mapa vem pronto no ramo (carimbo IGUAL — ver o PRONTO).

**2 · Código da v5 — por cima.** Se a SEPARAR-A-B-V5 entregar um ramo refeito sobre `social-qualificar-v2`,
é `--ff-only` também (preferível: o mapa vem carimbado). Senão: `git merge --no-ff origin/legacy-99-v5` (sem
conflito, medido) e, **com a LOCK-PESADO**, a cadeia do mapa no vivo (`correr_a_cadeia.py REGERAR`, commit,
`VALIDAR`, `PORTOES_POS_COMMIT` → carimbo IGUAL). Reiniciar o supervisor.

**3 · Livros da v5 — os 41 canais (bot ainda parado)**: o passo 2 do SEPARAR-A-B-V5
(`importar_do_coletor.py` a mostrar → `--pelo-scrap --ids=<lote>` em lotes de 10). Primeiro este, **sozinho**.

**4 · Livros sociais — semear só o lote (bot ainda parado)**
```
py curadoria/semear_qualify_social.py --candidatas CAND-0118,CAND-0133,CAND-0112,CAND-0103,CAND-0094,CAND-0114,CAND-0119,CAND-0097,CAND-0105
py curadoria/semear_qualify_social.py --tipo YOUTUBE --candidatas CAND-0190,CAND-0219,CAND-0469,CAND-0335,CAND-0423,CAND-0289,CAND-0377,CAND-0873,CAND-0877
```
conferir 9 + 9 e nenhuma «NAO ELEGIVEIS»; repetir os dois com `--aplicar --vivo`.
Os passos 3 e 4 **nunca ao mesmo tempo**: o 3 escreve contratos/tabela/estados, o 4 escreve fila/alocação.

**5 · Tirar o `PARAR.flag`.** O bot faz QUALIFY → contrato → rota nos 18 sociais e **pára em `CANARY_PENDING`**,
como os 41 da v5 — sem rede para nenhum deles (a rota do Scrap não tem canário do Curator).

**6 · Ler os números que ficaram** (`SOURCE-ID-ALLOCATION-V1.json` por `CANDIDATE_ID`); os da SOCIAL-QUALIFICAR são
propostos e podem andar.

**7 · Rede — missões próprias, nesta ordem:** (a) a **micro social** (lote do `SOCIAL-QUALIFICAR.md` §4: YouTube 1
canal + 1 vídeo ≤ ~9 min por onda; LinkedIn 2 contas com `teto=1`); (b) depois os **canários dos 41 canais** da v5.
YouTube é UMA plataforma e UM orçamento (youtube.com + googlevideo.com, D41): **nunca na mesma onda**, e a
prova-teto a seguir a cada onda. Medido: cada vídeo = 3 + 1 por ~10 MiB de áudio (mínimo, sem erros).

**8 · Régua** depois de cada canário: `py curadoria/regua_social.py --corridas <resultados.json> --aplicar --vivo`,
com o bot parado (SOCIAL/v1 + D36 + D53).

## Desfazer
- Livros: repor do corte do passo 0 (o livro de estados só acrescenta: voltar por transição nova).
- Código: `git reset --keep 83de0ccd` e reiniciar o supervisor (desfaz os dois ramos juntos; a C9 fica).

## EM PALAVRAS SIMPLES
- São dois pacotes que chegam na mesma casa: o da **v5** (41 canais do YouTube antigos, que passam a ser buscados
  pelo "Scrap") e o **social** (as 9 contas do LinkedIn e 9 canais novos da micro).
- Testei juntar os dois sem juntar de verdade: **não briga nada**. O social vai primeiro (já está em cima do
  vivo novo, com a C9), a v5 entra por cima.
- Os cadernos do robô são escritos **um pacote de cada vez**, com o robô parado — como não deixar duas pessoas
  escreverem na mesma folha ao mesmo tempo.
- Depois de instalar, ninguém vai à internet sozinho. A internet só abre em missão própria: primeiro a micro social,
  depois os 41 canais, nunca juntos, porque os dois gastam o mesmo limite do YouTube (5 pedidos por rodada).
- A régua nova da v5 (D53) também vai julgar os vídeos da micro. Conferi no código que o nosso áudio traz o que
  ela pede. Mas **ainda não testei com um vídeo real** — isso só a micro mostra.
