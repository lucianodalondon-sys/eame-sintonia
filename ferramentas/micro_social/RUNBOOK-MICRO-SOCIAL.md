# RUNBOOK — MICRO SOCIAL (LinkedIn + YouTube), por rodadas

Missão RUNBOOK-MICRO-SOCIAL, 26/09/2026. Ramo `runbook-micro-social-v1` (a partir do vivo `83de0ccd`).
O condutor é `ferramentas/micro_social/micro_social.py`. Quem corre no vivo é o **coordenador**,
**depois** da instalação do lote 1 do INTEGRA-NOITE.

> ## ⛔ HOJE A MICRO SOCIAL NÃO PODE CORRER
>
> Medido no ensaio a seco com os livros do vivo (`LIFECYCLE-LEDGER-V1.json` md5 `51b511f1cc06…`,
> copiados para uma pasta descartável):
>
> | # | bloqueio | medido | quem resolve |
> |---|---|---|---|
> | B1 | **lote 1 por instalar** (PROVA-TETO-SOCIAL `84a997a6`) | no `83de0ccd`, `prova_teto_dominio.py` não tem `googlevideo.com` (0 ocorrências) e o Scrap não conta pedidos | coordenador (INTEGRA-NOITE lote 1) |
> | B2 | **nenhuma fonte LinkedIn no vivo** | 0 contratos com `linkedin.com/company`; as 68 transições que falam de LinkedIn são candidatas `POLICY_BLOCK` («TOS», D15). Os números `IT-T7-171`/`IT-T5-160` da cópia `7b769819` são, **no vivo**, fontes WEB (Periti Agrari, CNR IBBA) | dono (D15 × D24/D41) + junção social + semear com o robô parado |
> | B3 | **nenhum canal YouTube elegível** | 50 canais: 41 `READY_LEGACY` (régua antiga) + 9 `ESTADO_NAO_READY`; `ELIGIBLE` = 0 | re-medir pela régua de hoje (`regua_social` / DETAIL) |
> | B4 | **o `py` do vivo não abre o `yt_dlp`** | `py -m yt_dlp` → `No module named yt_dlp`; a sonda do adaptador diz «pronto» porque acha um `yt-dlp.EXE` de OUTRO projeto (hermes). Resultado medido: `AUDIO_NAO_OBTIDO` com zero pedidos | `PYTHONPATH=<pasta só com o yt_dlp>` (passo 5) |
> | B5 | **a lista do canal pede a chave da API** | `youtube.channel.discovery` → `youtube_uploads` (Data API, `CREDENTIAL_MISSING` nesta máquina); a rota pela página pública (`youtube_canal_publico`, PROVED na matriz) existe e **não está registada** | por isso o vídeo vai escolhido à mão no lote (passo 4); ligar a rota pública = código novo |
> | B6 | ~~`integra-noite-v1` ainda não existe~~ **FEITO** | ensaio repetido na `integra-noite-v1 @ 2a2fa154` + este ramo (secção D, N0–N8): tudo recusa limpo, 34 + 22 testes OK | — |
>
> **Previsão do teto (D38), lida no código:** cada item corre num processo novo, e o
> `robots.txt` de cada host é relido por processo (`scrap_http._ROBOTS` vive só no processo).
> Uma conta LinkedIn com `teto=1` = `linkedin.com` **2** (robots + página) + `licdn.com` **3**
> (robots + MP4 + legenda). **Duas contas na mesma noite dão `licdn.com` = 6 > 5.** O condutor
> recusa-o ANTES da rodada (`PREVISAO_ACIMA_DO_TETO`). A missão pedia «LinkedIn 2 contas × 1
> vídeo»: são **duas noites**, uma conta por noite (ou uma noite, se a 1.ª conta medir
> `licdn.com` ≤ 2 — sem legenda). YouTube (`youtube.com` + `googlevideo.com`, D41): **NÃO SEI**
> — o `yt-dlp` nunca foi medido; só a 1.ª rodada de YouTube da noite pode correr.

---

## A. O que o condutor faz (e recusa)

```
py ferramentas/micro_social/micro_social.py plano     --lote=<LOTE.json>
py ferramentas/micro_social/micro_social.py rodada    --lote=<LOTE.json> --n=<K> --estado=<PASTA>\ESTADO.json --autorizado-pelo-dono
py ferramentas/micro_social/micro_social.py sala      --estado=<PASTA>\ESTADO.json
py ferramentas/micro_social/micro_social.py relatorio --estado=<PASTA>\ESTADO.json --saida=<PASTA>\relatorio
```

`rodada` recusa, **antes de qualquer pedido**, por esta ordem (código de saída **2**):

1. sem `--autorizado-pelo-dono`
2. lote 1 por instalar (`LOTE_1_NAO_INSTALADO`)
3. `PARAR-MICRO-SOCIAL.flag` ao lado do ESTADO (a parada automática de uma rodada anterior)
4. robô a correr (`ROBO_NAO_PARADO`: sem `curadoria/PARAR.flag`, ou processo `supervisor|worker|ponte_automatica` vivo)
5. Sala operacional por declarar (as 5 variáveis da micro web; `BANCO_DESCARTAVEL_URL` presente também recusa)
6. rodada que não está no lote
7. previsão acima do teto (`PREVISAO_ACIMA_DO_TETO`): gasto da noite (medido) + previsto > 5 por domínio
8. rodada com YouTube e `py -m yt_dlp` que não abre (`YT_DLP_NAO_ABRE`)
9. egresso ≠ IT pelo portão de consenso (`EGRESSO_NAO_IT`)

Por item, também no `plano`:
- **o contrato da fonte tem de ser a MESMA conta** — LinkedIn: o `linkedin.com/company/<slug>` do lote
  está no contrato (a conta inteira: `ispra` não é `ispra_2`); YouTube: o contrato é de um canal
  (`SOURCE_NATIVE_ID_KIND = YOUTUBE_CHANNEL_ID`). Medido no ensaio na `integra-noite-v1`: sem isto,
  `IT-T7-171` e `IT-T5-160` (fontes WEB no vivo, `ELIGIBLE` de WEB) passavam o plano como LinkedIn;
- o portão de coleta **no instante** (`collection_gate.avaliar`) — item não `ELIGIBLE` não corre.
Cada item vai pela porta canónica (orquestrador → `scrap-colheita`), com o Pedido montado em processo.

Depois da rodada: egresso outra vez + **PROVA-TETO sobre todas as corridas da noite** (D38 é por onda).
Se a prova não for `PASS` (FAIL **ou** NAO_SEI), ou o egresso cair, ou uma corrida sair sem RUN_ID:
escreve `PARAR-MICRO-SOCIAL.flag` e sai com **3**. A rodada seguinte recusa-se sozinha.

⚠️ **Nunca correr o Pedido à mão.** Medido no ensaio (E7): o orquestrador sozinho **não** pergunta ao
portão de coleta — aceitou `fase=video-linkedin` numa fonte que é WEB e respondeu `CORRIDA SUCCESS`
com zero itens. Quem pergunta ao portão é o condutor.

---

## B. A noite, passo a passo (no vivo, Git Bash)

```bash
VIVA=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
NOITE=C:/inst/$(date +%Y%m%d)-micro-social        # fora do Git; tudo desta noite fica aqui
mkdir -p $NOITE && cd $VIVA
git log -1 --format='%h %s'                          # tem de conter o lote 1 (INTEGRA-NOITE)
```

**0 · O lote 1 está lá.** Sem isto não se passa daqui:
```bash
py -c "import sys; sys.path.insert(0,'ferramentas/micro_social'); import micro_social as MS; print(MS.lote_1_instalado() or 'LOTE_1=OK')"
```

**1 · Egresso pelo portão de consenso** (3 verificadores; código 0 = PASS):
```bash
py superficie/rede.py --portao-de-egresso IT --sem-cache ; echo rc=$?
```
`rc=1` (`EGRESS_GATE: BLOCKED`, `EGRESS_VERDICT` BLOCKED/UNKNOWN) → ligar a VPN italiana e repetir. Não seguir sem `rc=0`.

**2 · Backup da Sala** (antes de parar o robô, como na BC2):
```bash
cmd //c "%USERPROFILE%\\sintonia-sala-italia\\backup_sala.cmd"      # tem de imprimir BACKUP=PASS
py -c "import sys; sys.path.insert(0,'scripts/micro_coleta'); import micro_coleta as M; print(M.sql('select count(*) from sala_de_espera'))" | tee $NOITE/SALA_ANTES.txt
```
A cópia fica em `%USERPROFILE%\sintonia-sala-italia\backups\sala_italia-AAAAMMDD-HHMMSS.dump`. Anotar o nome.

**3 · Parar o robô** (flag; a Tarefa `SINTONIA-Arranque` fica ligada):
```bash
py curadoria/supervisor.py --estado                   # antes: RUNNING / worker IDLE
echo "micro-social $(date -Iseconds)" > $VIVA/curadoria/PARAR.flag
# esperar o supervisor sair (ate 60 s); o observador da ponte nao tem flag:
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='py.exe'\" | Where-Object { \$_.CommandLine -match 'supervisor|worker|ponte_automatica' } | ForEach-Object { '{0} {1}' -f \$_.ProcessId,\$_.CommandLine }"
# se o observador continuar: taskkill //PID <PID_LANCADOR_OBSERVADOR> //T //F   (CUTOVER-RUNBOOK.md:84)
```
A lista de processos tem de sair **vazia**. O condutor confere o mesmo, sozinho.

**4 · O lote da noite** (escrito pelo coordenador; o condutor não escolhe fontes). Uma conta LinkedIn por noite; um vídeo YouTube ≤ 9 min, **escolhido antes da janela de coleta** (a lista do canal pede a chave — B5). A duração lê-se na página do vídeo e vai no lote:
```json
{"RODADAS": [
  {"N": 1, "ITENS": [{"SOURCE_ID": "<IT-Tn-nnn da conta LinkedIn ELIGIBLE>", "FASE": "video-linkedin",
                      "PAGINA": "https://www.linkedin.com/company/<slug>/", "TETO": 1}]},
  {"N": 2, "ITENS": [{"SOURCE_ID": "<IT-Tn-nnn do canal ELIGIBLE>", "FASE": "audio-youtube",
                      "VIDEO": "<id de 11>", "DURACAO_S": 480}]}]}
```
```bash
py ferramentas/micro_social/micro_social.py plano --lote=$NOITE/LOTE.json | tee $NOITE/PLANO.json ; echo rc=$?
```
Tem de dar `"PRONTAS" == "DE"` e `rc=0`. Qualquer `BLOQUEADA` para a noite aqui.

**5 · As variáveis da Sala operacional e o `yt_dlp`** (as mesmas da micro web, `MICRO-RUNBOOK.md:87-92`):
```bat
set SINTONIA_SALA_BACKEND=POSTGRES
set SINTONIA_SALA_DSN=<conteudo de %USERPROFILE%\sintonia-sala-italia\SALA_DSN.txt>
set SINTONIA_COLLECTION_DSN=<a mesma DSN>
set SINTONIA_PSQL_EXE=%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe
set SINTONIA_ARMAZEM_RAIZ=%USERPROFILE%\sintonia-sala-italia\armazem
set BANCO_DESCARTAVEL_URL=
set PYTHONPATH=<pasta que contem SO a copia de ~\.sintonia-libs\yt_dlp>
```
(`~\.sintonia-libs` inteiro não serve: o resto é cp311 e o `py` é 3.12.) Conferir: `py -m yt_dlp --version` → `2026.08.19`.

**6 · Rodada 1 — LinkedIn, 1 conta × 1 vídeo:**
```bash
py ferramentas/micro_social/micro_social.py rodada --lote=$NOITE/LOTE.json --n=1 --estado=$NOITE/ESTADO.json --autorizado-pelo-dono | tee $NOITE/RODADA-1.json ; echo rc=$?
```
`rc=0` segue · `rc=3` **parada automática** (ler `PARAR-MICRO-SOCIAL.flag` e `PROVA-TETO-DA-NOITE.json`; ir ao passo 9) · `rc=2` recusou antes da rede (ler `PORQUE`).

**7 · Rodada 2 — YouTube, 1 canal × 1 vídeo ≤ 9 min:** o mesmo comando com `--n=2`. É a primeira medição do `yt-dlp`: o que ela gastar em `youtube.com`+`googlevideo.com` fica no `PROVA-TETO-DA-NOITE.json`, e uma segunda rodada de YouTube na mesma noite é recusada.

**8 · Depois de CADA rodada** (o condutor já o fez; o coordenador lê):
```bash
cat $NOITE/PROVA-TETO-DA-NOITE.json | grep -E '"ESTADO"|"PEDIDOS_NA_ONDA"'
py superficie/rede.py --portao-de-egresso IT --sem-cache ; echo rc=$?
```

**9 · Relatório e Sala** (só leitura; `default_transaction_read_only` na ligação):
```bash
py ferramentas/micro_social/micro_social.py relatorio --estado=$NOITE/ESTADO.json --saida=$NOITE/relatorio
py ferramentas/micro_social/micro_social.py sala      --estado=$NOITE/ESTADO.json | tee $NOITE/SALA.json ; echo rc=$?
```

**10 · Religar o robô:**
```bash
rm $VIVA/curadoria/PARAR.flag
powershell -NoProfile -Command "Stop-ScheduledTask SINTONIA-Arranque; Start-ScheduledTask SINTONIA-Arranque"
py curadoria/supervisor.py --estado                   # RUNNING / IDLE
```

**↩️ Desfazer** (só por decisão do coordenador; nunca por cima da base existente — `MICRO-RUNBOOK.md:167-177`):
robô parado → `dropdb` → `createdb` → `pg_restore --no-owner --no-privileges -d <DSN> <o .dump do passo 2>`.
O livro de corridas e o RAW são só-acrescentar: não se desfazem, ficam com as linhas da noite.

---

## C. O que conferir na Sala (verbo `sala`)

Lê `sala_de_espera_atual` (a vista da migração 033: valor atual = última revisão, senão o original),
só as linhas das corridas desta noite. Por item:

| campo | base | precisão |
|---|---|---|
| `published_at` | `published_at_basis` | `tempo_lugar_evidencia->>'PUBLISHED_AT_PRECISION'` |
| `source_location` | `source_location_basis` | `…->>'SOURCE_LOCATION_PRECISION'` |
| `fact_time` | `fact_time_basis` | `…->>'FACT_TIME_PRECISION'` |
| `fact_location` | `fact_location_basis` | `…->>'FACT_LOCATION_PRECISION'` |

Reprova (`rc=1`): **valor sem base** (um valor preenchido com base `NAO SEI`) e **`fact_time` igual
a `captured_at`** (tempo do facto fabricado a partir da nossa visita). `NAO SEI` com base `NAO SEI`
é a resposta honesta e passa: **UNKNOWN continua UNKNOWN**. Sala vazia não passa.

O que se espera de cada plataforma (do código, por medir na noite):
- LinkedIn: `observed_at`; a data da publicação é a que a plataforma declara, com a sua base.
- YouTube áudio: `captured_at`; `PUBLISHED_AT` vem do `info.json` do `yt-dlp` (`--write-info-json`),
  com a base «PLATAFORMA».
- `fact_time` / `fact_location`: `NAO SEI` salvo o texto dizê-lo (`leis/fato_do_texto.py`).

---

## D. Ensaio a seco (26/09, sem rede, sem Sala)

Cópia descartável `C:/nuvem/ensaio-micro-social` = vivo `83de0ccd` + `origin/prova-teto-social-v1` +
este ramo (merge local, nunca publicado). Proxy numa porta morta (`127.0.0.1:9`), nenhuma variável
`SINTONIA_*`. Saídas guardadas em `ferramentas/micro_social/ensaio/` (sha256 em `SHA256SUMS.txt`).

| passo | o que se correu | resultado |
|---|---|---|
| E1 | `superficie/rede.py --portao-de-egresso IT --sem-cache` | `EGRESS_GATE BLOCKED`, `VERDICT UNKNOWN`, **rc=1** |
| E2 | `plano` (livros do Git desta cópia) | 0/3 prontas: LinkedIn `AUSENTE_DO_LIVRO`; YouTube `READY_LEGACY`, rc=1 |
| E2′ | portão com os livros do **vivo** copiados | YouTube 41 `READY_LEGACY` + 9 `ESTADO_NAO_READY`; LinkedIn 0 fontes (B2, B3) |
| E3 | `rodada` sem `--autorizado-pelo-dono` | recusa, rc=2 |
| E4 | `rodada` autorizada | `ROBO_NAO_PARADO` (sem `PARAR.flag`), rc=2 |
| E5 | robô dado por parado, sem variáveis da Sala | recusa: faltam as 5 variáveis |
| E6 | variáveis falsas (nunca usadas) | `EGRESSO_NAO_IT` (UNKNOWN) — **nenhum pedido saiu** |
| E7 | o Pedido LinkedIn **à mão**, rede fechada | `CORRIDA SUCCESS` com 0 itens; envelope PARTIAL («o atlas não conhece IT-T7-171»); linha no livro com `PEDIDOS_POR_HOST {"linkedin.com": 1}` (a tentativa do robots.txt, recusada pelo proxy) |
| E8 | o Pedido YouTube áudio à mão | `AUDIO_NAO_OBTIDO`, `SOURCE_UNAVAILABLE`, `PEDIDOS_POR_HOST {}` — o `py` não tem `yt_dlp` (B4) |
| E10/E14 | `tests/test_micro_social.py` na cópia com o lote 1 | **29/29**, incluindo a prova-teto REAL a reprovar `youtube.com` 3 + `googlevideo.com` 3 = 6 |
| E11 | `py -m yt_dlp --version` sem / com `PYTHONPATH` | `No module named yt_dlp` / `2026.08.19` |
| E12/E13 | `lote_1_instalado()` na cópia / `googlevideo` no `83de0ccd` | OK / 0 ocorrências |

Testes no ramo: 34 (1 deles à espera do lote 1, e corre na cópia). Mutação do condutor: **28/28**
(`ferramentas/micro_social/_mutantes_micro_social.py`).

### Repetido na `integra-noite-v1 @ 2a2fa154` (+ este ramo, merge local descartável)

Saída inteira em `ensaio/integra-noite/saida-noite.txt` (sha256 em `SHA256SUMS.txt`).

| passo | resultado |
|---|---|
| N1 lote 1 | `LOTE_1=OK` |
| N2 egresso, rede fechada | `BLOCKED` / `UNKNOWN`, rc=1 |
| N3 plano, livros do vivo (md5 `51b511f1cc06`) | 0/3: `IT-T7-171` e `IT-T5-160` «o contrato não é a conta LinkedIn» (são Periti Agrari e CNR IBBA); `IT-T8-006` `READY_LEGACY` |
| N4 sem autorização / autorizada | rc=2 / `ROBO_NAO_PARADO` rc=2 |
| N5 robô dado por parado | sem Sala → recusa; 2 contas LinkedIn → `licdn.com: 6 previstos (teto 5)`; YouTube → `YT_DLP_NAO_ABRE`; 1 conta → `EGRESSO_NAO_IT` — **zero pedidos** |
| N6 / N7 testes | condutor 34/34 · lote 1 (`test_prova_teto_social`) 22/22 |
| N8 `yt_dlp` com `PYTHONPATH` | `2026.08.19` |

---

## E. O que falta para correr

1. **B1** instalar o lote 1 (PROVA-TETO-SOCIAL) — já no pacote INTEGRA-NOITE.
2. **B2** decidir o LinkedIn no vivo: hoje todas as candidatas estão `POLICY_BLOCK` (D15). Sem uma fonte
   LinkedIn `ELIGIBLE`, a rodada 1 fica `BLOQUEADA` no plano.
3. **B3** pelo menos 1 canal YouTube `ELIGIBLE` (hoje 0 de 50): re-medir pela régua de hoje.
4. **B4** a pasta com a cópia do `yt_dlp` para o `PYTHONPATH` do vivo (ou instalar o `yt-dlp` no `py` 3.12 com `--target`).
5. **B5** o vídeo escolhido à mão, com a duração, no lote; ou ligar `youtube_canal_publico` como rota da lista (código novo, com teste).
6. ~~B6~~ feito (secção D).
7. Aceitar a previsão: **1 conta LinkedIn por noite**.
