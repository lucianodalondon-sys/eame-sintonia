# PLANO DE INSTALAÇÃO — BC4b (armazém da Sala + país da corrida) na produção

> Missão BC4b, 24/09/2026. **Não instalado**: quem instala é o coordenador. Modelo:
> `PLANO-INSTALACAO-M5G.md`. FINAL = `origin/bc4-correcoes-v1` (medir o SHA na hora).

## O que vai para a produção, e porquê

A micro real da BC4 (24/09, 00:53–01:00, bot `8eec2e2a`, Sala real `54330/sala_italia`) pousou
+3 na Sala, mas:

1. **os bytes** das 4 matérias e dos 4 derivados ficaram na árvore do bot (`XX/…`,
   `NAO_SEI/derivados/…`), resíduo de medição que o Git ignora e a suíte já apagou uma vez
   (BC2, 20/09). O conserto de 20/09 (GARGALOS-BC2 `8e58f69c`/`356b1b3c`) **nunca chegou a esta
   linha** — foi trazido agora, sem mudar a regra dele;
2. **o país**: as corridas nasceram `XX-T..`, `source_country = NAO_SEI`. O instrumento da micro
   passa a pôr no pedido `--filtro pais=<prefixo do SOURCE_ID>` (regra do Atlas
   `IT-T<n>-<seq>`, a mesma do QUALIFY). **Nunca** o país da VPN: o egresso continua registado
   ao lado pelo coletor (`VPN_COUNTRY`, `EGRESS_IP` no livro de corridas).

| peça | muda | quem é o dono |
|---|---|---|
| `guarda/preservar_coleta.py` | `raiz_do_armazem_local` (OPERACIONAL exige `SINTONIA_ARMAZEM_RAIZ`, fora da árvore, com marcador; outros modos = árvore), `apagar_armazem_de_medicao` | dono dos bytes (`ArmazemLocal`) |
| `orquestrador/persistencia.py` | a raiz resolve-se com o modo, **antes** de a memória nascer; vai no recibo (`ARMAZEM_RAIZ`) | composição do runtime |
| `orquestrador/orquestrador.py` | `correr(..., raiz_do_armazem=)`; `main()` recusa (sai 2) sem raiz | a RUN |
| `scripts/micro_coleta/micro_coleta.py` | 5.ª variável obrigatória; `pais_de()`; comando com `pais=` | instrumento da micro |
| `ensaio_offline.py`, `micro_rede_real.py` | armazém do ensaio fora da árvore (a regra nova recusaria a árvore) | ensaios |
| `ferramentas/big_collection/reconciliar_bytes_bc4.py` | **nova**, só plano por omissão | reconciliação (abaixo) |

**O que NÃO muda:** o bot de fontes (supervisor/worker/canário) não declara
`SINTONIA_COLLECTION_DSN` → modo AUSENTE → raiz = árvore, como hoje. O workflow do GitHub usa
`BANCO_DESCARTAVEL_URL` → DESCARTÁVEL → como hoje. Só a corrida **operacional** (Sala real) muda,
e passa a exigir a 5.ª variável: `SINTONIA_ARMAZEM_RAIZ=%USERPROFILE%\sintonia-sala-italia\armazem`
(já tem o marcador `ARMAZEM_OPERACIONAL.json` desde 20/09).

## Provas (feitas)

```
TESTES ANTES/DEPOIS  22a2810e (vermelho) -> 7603a22b (verde): tests/test_bc4_armazem_e_pais (10)
                     + tests/test_armazem_operacional_protegido (12, o de 20/09): 22 vermelhos -> 0
MEDICAO POR NOME     46 modulos ligados (persistencia/orquestrador/preservar/micro), base 98ec8fbf
                     vs FINAL: SAIRAM 25 vermelhos (22 acima + audio 04/05/12, que NAO toquei — variou);
                     ENTRARAM 2, ambos resolvidos: test_sem_as_variaveis_da_sala_nao_lanca (4 -> 5
                     variaveis, atualizado) e test_M5_o_ponto_fixo (so passa depois da cadeia do mapa: OK)
MUTACAO              8 mutantes, 8 mortos, 0 sobreviventes (orquestrador volta a RAIZ; persistencia nao
                     resolve; dono aceita operacional sem raiz; main nao passa/nao apanha; comando sem
                     pais; pais fixo IT; micro sem a 5.a variavel)
RED TEAM             provas/red_team_persistencia_operacional.py: BLOCKERS 0 (+2 ataques novos)
PLANO DAS 18         orquestrador --so-plano com pais=IT: 18/18 com caminho (nada correu)
MAPA                 SYSTEM_MAP_CHECK = PASS; carimbo IGUAL; peca C-RECONCILIAR-BYTES-BC4 declarada
```

## Ensaio — cópia fiel do vivo (24/09 ~02:10), `C:/ens-bc4`

```
VIVO bot   servico-20260923-0923 @ 8eec2e2a  sujos=14 + 4 pastas novas (18 ficheiros)
VIVO ponte cutover-20260923-0923 @ 98ec8fbf  sujos=3
FINAL      8afd504d
BOT 1. merge --no-ff (livros sujos no sitio)   rc=0  conflitos=0
BOT 2. livros sujos: IGUAIS byte a byte (18)
BOT 3. arvore commitada vs FINAL: 0 ficheiros diferentes
BOT 4. testes na copia: 95 focados, 1 ERROR ja existente na base
       (test_estagio...test_correr_julga_a_unidade_da_fronteira); portao 23/23; red team 0;
       plano com os livros vivos: PRONTAS 18 / BLOQUEADAS 19 (= coorte G3)
PONTE 1. ff-only  rc=0  HEAD=8afd504d;  livros IGUAIS (3)
```

(ensaio offline da micro e DESFAZER: ver o fim deste ficheiro)

## WRITESET

| peça | na INSTALAÇÃO escreve | em FUNCIONAMENTO passa a escrever | livros do vivo tocados |
|---|---|---|---|
| **BC4b** | bot: **31** ficheiros rastreados (8 código, 1 ferramenta nova, 3 testes + 1 novo + 1 do 20/09, 1 prova, 2 manuais, 13 do mapa gerado/declarado). Ponte: avanço rápido, os mesmos 31 | só a corrida **operacional**: bytes em `SINTONIA_ARMAZEM_RAIZ` (e o marcador, se faltar). Nada novo para o bot | **0 de 18** (bot) e **0 de 3** (ponte) |

## Os passos (coordenador, com o bot quieto) — ~5 min parado

```bash
VIVA=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
CASA=/c/Users/London1/orca/workspaces/eame-sintonia/ponte-viva
C=/c/inst/$(date +%Y%m%d-%H%M)-bc4b; mkdir -p $C/bot $C/ponte
FINAL=$(git -C $VIVA fetch -q origin && git -C $VIVA rev-parse origin/bc4-correcoes-v1); echo $FINAL
```

**0 · Medir** — bot `8eec2e2a` (`servico-20260923-0923`), ponte `98ec8fbf`; se mudou, repetir o
ensaio. `git -C $VIVA diff --name-only HEAD $FINAL -- $(git -C $VIVA status --short | awk '$1=="M"{print $2}')`
tem de sair vazio. Um só supervisor e um só observador; worker IDLE; memória livre.

**1 · Parar** — `PARAR.flag` com marca própria; esperar o supervisor sair; matar o observador.
⚠️ A Tarefa `SINTONIA-Arranque` (guarda) não toca flag alheio: fica ligada.

**2 · Foto dos livros** (inclui os não rastreados da micro BC4):
```bash
(cd $VIVA && git status --short | awk '{print $2}' | while read f; do find "$f" -type f; done) > $C/bot.lista
while read f; do mkdir -p $C/bot/$(dirname "$f"); cp "$VIVA/$f" "$C/bot/$f"; done < $C/bot.lista
for f in $(git -C $CASA status --short | awk '{print $2}'); do mkdir -p $C/ponte/$(dirname $f); cp $CASA/$f $C/ponte/$f; done
(cd $C && find bot ponte -type f | xargs sha256sum) > $C/foto.sha
```

**3 · Bot** — `git -C $VIVA merge --no-ff --no-commit $FINAL`; conflitos esperados: **nenhum**
(só `*.generated.json` → `--theirs`; outro → `merge --abort`, ABORTAR); commit
`instalar BC4b (bc4-correcoes-v1 @ ${FINAL:0:8}): livros = producao`; `git diff --name-only $FINAL HEAD` = 0.

**4 · Ponte** — `git -C $CASA merge --ff-only $FINAL`.

**5 · Conferir livros** — `cmp` de cada ficheiro da foto: nada «MUDOU». 🛑 algum → DESFAZER.

**6 · Relançar** — tirar o flag; `Stop-ScheduledTask SINTONIA-Arranque; Start-ScheduledTask SINTONIA-Arranque`
(liga observador e supervisor; provado na BC4: 57 s, um de cada).

**7 · Medir** — `py curadoria/supervisor.py --estado` (RUNNING/IDLE); `ponte_automatica.py --estado` SAUDAVEL;
`micro_coleta.py plano` → 18 PRONTAS.

**8 · Publicar** — push de `servico-20260923-0923` e `cutover-20260923-0923`.

### ↩️ DESFAZER

`PARAR.flag`; `git -C $VIVA reset -q --keep 8eec2e2a`; `git -C $CASA reset -q --keep 98ec8fbf`;
conferir a foto; relançar como no passo 6.

## Os 8 ficheiros da micro BC4 — proposta de reconciliação (NÃO aplicada)

As linhas da Sala estão certas; só os bytes estão fora do armazém. **Nada se muda na Sala.** Depois
da instalação, com o bot quieto:

```
set SINTONIA_ARMAZEM_RAIZ=%USERPROFILE%\sintonia-sala-italia\armazem
py ferramentas/big_collection/reconciliar_bytes_bc4.py --origem=<VIVA>            (plano)
py ferramentas/big_collection/reconciliar_bytes_bc4.py --origem=<VIVA> --aplicar  (copia)
```

Lê da Sala (só SELECT) `storage_path` + `sha256` de `raw_asset` 1406–1409 e `derived_artifact`
909–912, confere o sha256 dos bytes na origem, e escreve pelo `ArmazemLocal.enviar` no **mesmo
caminho relativo** na raiz operacional. Recusa fechado sha diferente, byte ausente ou destino já
existente com outro conteúdo. Plano medido a seco às 01:4x: **8/8 COPIAR, sha256 iguais, Sala
escrita 0**. Cópia de segurança dos 8: `C:/bc4/micro/bytes-copia`. Os caminhos continuam com
`XX`/`NAO_SEI` — é a verdade de como aquelas corridas nasceram; não se reescreve história.

## Ensaio offline da micro na cópia instalada (24/09 02:31–02:36)

`scripts/micro_coleta/ensaio_offline.py --fontes=IT-T10-018,IT-T10-022,IT-T7-033` (as 3 da BC1),
na cópia `C:/ens-bc4/bot` = vivo + FINAL + livros vivos commitados **só na cópia** (como a BC1:
a árvore do ensaio é uma worktree do HEAD, e sem isso lê o livro antigo e o coletor recusa
`ESTADO_NAO_READY` — medido na 1.ª tentativa). Servidor local, Postgres descartável, 0 internet.

```
                         SEM conserto (8eec2e2a)        COM conserto (FINAL)
corridas                 3 SUCCESS  XX-T10-.../XX-T7-   3 SUCCESS  IT-T10-.../IT-T7-
RUN-MANIFEST COUNTRY     NAO SEI                        IT
bytes                    <arvore>/XX, <arvore>/NAO_SEI  armazem FORA da arvore (19 ficheiros,
                                                        com ARMAZEM_OPERACIONAL.json); arvore 0
RAW / DERIVED            9 / 9                          9 / 9
Admission (9 itens)      NAO 4 · NAO_SEI 5 · SIM 0      IGUAL, item a item (md5 da folha igual)
Sala                     +0                             +0
```

**A Admission não mudou com o conserto** (as 9 decisões são as mesmas). O SIM 0 (e por isso a Sala
+0 e o C4 FAIL por `SALA_LINHAS = 0`) vem das páginas guardadas do ensaio com o teto de 5 pedidos
por site da A5 (3 matérias por fonte; a BC1, antes da A5, tinha 55). C1 FAIL é o esperado offline
(egresso NAO SEI; o ensaio nunca finge IT).

### ⚠️ O que o conserto do país NÃO muda (decisão do coordenador)

- `collection_run.source_country` continua `NAO_SEI`: o dono do RAW lê `SOURCE_COUNTRY` do recibo,
  e o orquestrador só escreve `COUNTRY` (a frente de trabalho do pedido).
- o `COUNTRY_SCOPE` de cada observação continua `NAO SEI` (vem do coletor), e é ele que dá o prefixo
  do caminho (`XX/…`, derivados em `NAO_SEI/…`).

Preencher um com o outro seria colapsar COUNTRY_SCOPE, SOURCE_LOCATION e FACT_LOCATION, que
`leis/artefato.py` manda manter separados. Caminhos possíveis, **não feitos**: (a) o contrato do
coletor declara `SOURCE_LOCATION` da fonte pelo Atlas → `source_country`; (b) `COUNTRY_SCOPE` das
observações = `COUNTRY` da corrida (é a frente de trabalho, e a lei diz que é decisão nossa) — mas
muda o prefixo dos caminhos para `IT/`, que o `.gitignore` e a limpeza de resíduo (só `XX/`) não
conhecem: a suíte deixaria `IT/` solto na árvore. Precisa de decisão e de missão própria.

## DESFAZER — provado na cópia

`git reset --keep 8eec2e2a` (bot) e `98ec8fbf` (ponte): rc 0; livros IGUAIS à foto (18 + 3).
