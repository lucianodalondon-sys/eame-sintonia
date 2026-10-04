# PLANO DE INSTALAÇÃO — M5G (7.ª passagem) na produção

> Missão M5G, 23-24/09/2026. **Não foi instalado.** O coordenador decide o momento e
> verifica o candidato num clone limpo antes. Este é o passo I do
> `BIG-COLLECTION-RUNBOOK.md`, com a mecânica de parar/relançar/desfazer do
> `CUTOVER-RUNBOOK.md` (passos 0, 1, 8, 9 e DESFAZER). Não é um SWITCH_PLAN novo.
>
> ⚠️ Corrige o `BIG-COLLECTION-RUNBOOK.md` §3.I: «instalar `origin/coorte-unica-v1` em vez
> de `origin/unificacao-v1` até a linha a absorver». **A linha absorveu-a** (G3 790fb10f, com
> BC2 83ca6c60, em `1527bfbc`). Instalar `origin/unificacao-v1`.

## O que vai para a produção

`FINAL` = `origin/unificacao-v1` @ `7ee87573` — o commit ensaiado. Os commits depois dele (até
o HEAD da entrega) só mudam `PLANO-INSTALACAO-M5G.md`, `RELATORIO-UNIFICACAO.md`, o mapa
gerado (`*.generated.json`) e o censo que a cadeia reescreve
(`docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`): conferir com `git diff --stat 7ee87573 origin/unificacao-v1`. Se aparecer outro
ficheiro, **repetir o ensaio**. Desde o vivo, esta passagem traz: A5 (robots,
pausa e teto dentro do coletor), G3+BC2 (coorte única, tabela do coletor 176 → 193), B4 (já
está no vivo, por cópia de ficheiros — conteúdo idêntico), e as passagens 5 e 6 que o vivo
ainda não tinha. **Nenhuma função nova da M5G**: só junções, duas correcções de teste
(declaração de `micro_rede_real.py` no portão; precedência da D9 em `test_collection_gate`) e,
por ordem da coordenação (C1), os testes/provas do Scrap desactualizados (RT01/RT02, RT20,
NS1/NS6, setUpClass do RC01) — só testes e provas.

## Ensaio (feito) — cópia fiel do vivo, 24/09 (em `e642c52a` ~00:55Z e de novo em `7ee87573`)

Cópias em `C:/ens-bot` e `C:/ens-ponte` (apagadas no fim): worktree no HEAD do vivo + os
ficheiros sujos do vivo copiados (só leitura no vivo; JSON conferido).

```
VIVO bot   servico-20260923-0923 @ 3d62e87d  sujos=10
VIVO ponte cutover-20260923-0923 @ 5c02bbe4  sujos=3
FINAL      7ee87573   (em e642c52a: os mesmos resultados, linha a linha)
BOT 1. merge --no-ff (com os livros sujos no sitio)   rc=0  conflitos=0
BOT 2. livros sujos: IGUAIS byte a byte (10)
BOT 3. arvore commitada vs FINAL: 0 ficheiros diferentes
BOT 4. testes na copia instalada: 54 corridos, 1 FAIL (test_5 de test_nivel_da_fila — ver abaixo)
       portao com os livros vivos: elegiveis = 37 de 143
BOT 5. DESFAZER: git reset --keep 3d62e87d   rc=0  HEAD=3d62e87d  0 codigo diferente
       livros sujos depois do desfazer: IGUAIS
PONTE 1. 5c02bbe4 esta na linha: avanco rapido (ff-only)   rc=0 HEAD=7ee87573
PONTE 2. livros sujos: IGUAIS (3)
PONTE 3. --lane presente (LANE=SIM)
PONTE 4. DESFAZER rc=0 HEAD=5c02bbe4 livros IGUAIS
VIVO depois: bot @ 3d62e87d, ponte @ 5c02bbe4   (o vivo nao foi tocado)
```

**O FAIL do BOT 4 não vem da instalação**: `test_nivel_da_fila.test_5` (B4) dá `4 != 0` também
numa cópia do vivo **sem instalar nada** (3d62e87d + os mesmos livros). É o teste da B4 a
discordar do livro vivo de hoje. Pertence à B4/R1; não bloqueia a instalação, mas fica
sabido antes.

**Rollback provado**: `git reset --keep <HEAD_antes>` repõe o código e **não toca** nos
livros sujos (sha256 igual antes/depois, bot e ponte).

## WRITESET — que ficheiros do vivo cada peça escreve

Serializar: **uma peça de cada vez, com o bot quieto; nos livros, um só escritor — o
processo do bot.** Nenhuma peça abaixo escreve livro na instalação.

| peça | na INSTALAÇÃO escreve | em FUNCIONAMENTO passa a escrever | livros do vivo tocados na instalação |
|---|---|---|---|
| **M5G** (esta linha) | bot `$VIVA`: **181** ficheiros rastreados (89 novos, 92 alterados): código de `curadoria/` (7: canario, onboardar_rotas_provadas, ready_split, retrato_html + 3 testes), `coleta/` (11, incl. `italy_pilot_collect.mjs` da A5 e `retrato_html.mjs`), `admissao/` (2), `regras/` (5, incl. **`italy_contracts_onboarded.json` 176 → 193**), `scripts/`, `medidas/`, `ferramentas/`, `leis/social_matriz.py`, `pedido/receitas.py`, `orquestrador/orquestrador.py`, `.github/workflows/sintonia-scrap.yml`, provas, testes, docs e mapa. Ponte `$CASA`: avanço rápido, **187** ficheiros | **nada novo.** O bot escreve os mesmos livros de hoje (B4 já está no vivo). O coletor da A5 só escreve em `data/collection-ledger/italy/` quando corre uma Collection — e a instalação não corre nenhuma; não acrescenta destino de escrita novo (medido: nenhum `writeFileSync`/`appendFileSync` novo) | **0 de 10** (bot) e **0 de 3** (ponte) — os 13 são iguais na versão salva do vivo e em `FINAL` |
| **R1** reparo-fontes-v1 | pelo `scripts/reparo/R1-WRITESET.json` dela: 25 ficheiros por `git checkout 491cc9ea -- <ficheiros>`. **Medido contra `FINAL`:** 5 já são iguais e saem (`ready_split.py`, `retrato_html.py`, `test_retrato_html.py`, `test_zz_guarda_isolamento.py`, `propor_receitas_v4.py`); **20 diferem** da linha | `italy_contracts_curator.json` (REPAIR_CONTRACT reescreve ACQUISITION / acrescenta contrato), `LIFECYCLE-LEDGER`, `-QUEUE`, `-EVIDENCE` (append), `SOURCE-ID-ALLOCATION` (SOURCE_ID novos das QUALIFY YouTube), estado do supervisor | 0 (diz a R1) |
| **B5** b5-demotion-viva-v1 | **nada** (0 ficheiros; a B5 só tem relatório e provas em cópia) | quando houver uma falha real, a despromoção é feita **pelo bot** (gatilho REVALIDAR → VALIDATE_ROUTE → canário): `LIFECYCLE-LEDGER`, `-QUEUE`, `-EVIDENCE` — o mesmo escritor de hoje | 0 |

### ⚠️ R1 não pode ser instalada ficheiro a ficheiro por cima da M5G sem decisão

A R1 foi construída sobre uma base com a junção da SOC3 (`f07349e3`) **sem** a retirada
(`63169df3`). O `worker.py` dela importa `rota_do_scrap_youtube` (código da SOC2), e o
writeset dela inclui `rota_do_scrap_youtube.py`, `test_soc2_curator_youtube.py`,
`ensaiar_qualify_youtube.py`, `test_d21_heranca.py` — nenhum existe no vivo nem na linha.
Instalar a R1 por `git checkout` de ficheiros **reintroduz no vivo parte da SOC2 que a linha
tirou**, e o vivo deixa de ser uma versão da linha. Ordem proposta: **M5G primeiro; a R1
entra na linha por junção (como as outras) e só depois vai para o vivo, com novo ensaio.**
Se o coordenador quiser a R1 antes, é decisão dele, com esta diferença à vista.

## Os passos (para o coordenador, com o bot quieto) — ~10 min parado

```bash
VIVA=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
CASA=/c/Users/London1/orca/workspaces/eame-sintonia/ponte-viva
C=/c/inst/$(date +%Y%m%d-%H%M); mkdir -p $C/bot $C/ponte
FINAL=$(git -C $VIVA fetch -q origin && git -C $VIVA rev-parse origin/unificacao-v1); echo $FINAL
```

**0 · Antes de parar (medir; abortar se não bater)**
- `git -C $VIVA rev-parse --short HEAD` = `3d62e87d`, ramo `servico-20260923-0923`;
  `git -C $CASA rev-parse --short HEAD` = `5c02bbe4`. Se mudou: **repetir o ensaio**.
- `git -C $VIVA status --short` = só os 10 livros; `$CASA` = só os 3. Código sujo → ABORTAR.
- `git -C $VIVA diff --quiet 3d62e87d $FINAL -- <os 10 livros>` e o mesmo para os 3 da ponte:
  têm de ser iguais (é isto que deixa a instalação não tocar em livro nenhum).
- um só supervisor e um só observador (consulta do `CUTOVER-RUNBOOK.md` passo 0; medido às
  ~00:50Z: supervisor 23416 / lançador 45624, observador 22764 / lançador 18316);
  `py curadoria/supervisor.py --estado` → worker IDLE. A trabalhar: esperar.
- memória livre (o dono pode estar a editar vídeo): falta → esperar e repetir.

**1 · Parar** — `echo "instalar M5G $(date -Iseconds)" > $VIVA/curadoria/PARAR.flag`; esperar
o supervisor sair (3-6 s); parar o observador (não tem PARAR.flag: mata-se).
🛑 algum não sai em 60 s → `rm PARAR.flag`, ABORTAR.

**2 · Foto dos livros** (é o rollback dos dados):
```bash
for f in $(git -C $VIVA status --short | awk '{print $2}'); do mkdir -p $C/bot/$(dirname $f); cp $VIVA/$f $C/bot/$f; done
for f in $(git -C $CASA status --short | awk '{print $2}'); do mkdir -p $C/ponte/$(dirname $f); cp $CASA/$f $C/ponte/$f; done
(cd $C && find bot ponte -type f | xargs sha256sum) > $C/foto.sha
```

**3 · Bot**
```bash
git -C $VIVA merge --no-ff --no-commit $FINAL; git -C $VIVA diff --name-only --diff-filter=U
# esperado: nada. So *.generated.json / docs/operacao/CENSO...: --theirs + add. Outro: merge --abort, ABORTAR.
git -C $VIVA commit -q -m "instalar M5G (unificacao-v1 @ ${FINAL:0:8}): livros = producao"
git -C $VIVA diff --name-only $FINAL HEAD | wc -l        # 0
```

**4 · Ponte** — `git -C $CASA merge --ff-only $FINAL` (rc 0).

**5 · Conferir os livros**
```bash
for f in $(cd $C/bot && find . -type f); do cmp -s $VIVA/$f $C/bot/$f || echo "MUDOU bot $f"; done
for f in $(cd $C/ponte && find . -type f); do cmp -s $CASA/$f $C/ponte/$f || echo "MUDOU ponte $f"; done
```
Nada impresso = os 13 livros iguais. 🛑 algum «MUDOU» → DESFAZER.
Portão (só leitura): elegíveis com os livros vivos = **37** no ensaio.

**6 · Relançar** — `rm $VIVA/curadoria/PARAR.flag`; supervisor pelo meio de hoje
(`py curadoria/supervisor.py`, cwd `$VIVA`); observador da `$CASA`:
`py curadoria/ponte_automatica.py --servir --intervalo 20 --lane "$(cygpath -w $VIVA)"`.

**7 · Medir depois (2-5 min)** — `py ferramentas/cutover/medir_cutover.py pos --viva "$(cygpath -w $VIVA)"`:
C1 (um só worker, rc 0) e C2 (RUNNING/IDLE, `PID_CHECK_NAO_SEI` vazio). 🛑 PARAR → DESFAZER.

**8 · Publicar** — `git -C $VIVA push origin servico-20260923-0923` e
`git -C $CASA push origin cutover-20260923-0923` (só depois do passo 7 verde).

### ↩️ DESFAZER (provado no ensaio)

```bash
echo "desfazer" > $VIVA/curadoria/PARAR.flag      # esperar sair; parar o observador
git -C $VIVA reset -q --keep 3d62e87d              # o codigo volta; os livros sujos ficam como estao
git -C $CASA reset -q --keep 5c02bbe4
# conferir cada livro contra a foto do passo 2; se algum diferir, copiar de $C/bot ou $C/ponte
rm $VIVA/curadoria/PARAR.flag                      # relancar como no passo 6
```

Se já houve push (passo 8), o desfazer da pasta é o mesmo; o ramo no origin fica com o commit
de instalação e o coordenador decide se o reverte.

## O que o ensaio NÃO provou

- **Rede**: a instalação não usa rede e o ensaio não correu coleta nenhuma (NÃO RODAR
  COLLECTION). Que a cortesia da A5 se porta bem com os sites reais só se vê na BC.
- **Processos**: o ensaio não parou nem relançou o supervisor e o observador verdadeiros
  (isso está provado pelos ensaios X1/X2 do `CUTOVER-RUNBOOK.md`).
- **Livros em movimento**: se o bot escrever entre o passo 0 e o 1, a igualdade dos livros
  (passo 0, 3.º ponto) tem de ser medida outra vez depois do passo 1.

## Fora desta instalação (bloqueios nomeados)

| peça | porque fica fora | o que falta |
|---|---|---|
| P1b f5123e23 · P2 52a64e48 · YT3 ffb6e971 | as candidatas novas usam números CAND que a produção já deu a outras: **164/164, 29/29, 14/14** (YT3: 3 endereços já estão na fila) | cada lane re-regista as suas pela porta (`candidatas/fonte_nova.py registar`) sobre a fila de hoje; depois junta-se |
| SOC5 97728444 | está construída sobre SOC2/SOC3 **sem** a retirada da 6.ª passagem; `worker.py`, `rota_do_scrap_youtube.py` e a prova de roteamento só funcionam com esse código de volta | a SOC3 corrigida na própria lane (as 4 leis da casa), depois a SOC5 |
| R1 reparo-fontes-v1 | a missão manda juntar só depois de instalada no vivo, com o SHA dela; e a nota acima (SOC2) | decisão do coordenador sobre a ordem |
| P1 34 candidatas Vet/IZS (em f5123e23) | o dono tirou Vet/IZS do foco às ~18:50 (017a0601, trava que é função nova — fora) | `--fora-do-foco --aplicar` da P1, quando a coordenação pedir |
