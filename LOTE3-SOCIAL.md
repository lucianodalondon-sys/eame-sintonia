# LOTE3-SOCIAL — pacote único (freio + maestro + canais-41 + canais de pesquisa) e o roteiro de instalação (26/09)

Ramo **`lote3-social-v1`**, a partir do vivo **`69b0e23f`** (LOTE 1). **SEM MAPA** (a cadeia do mapa fica para a
INTEGRA ou para depois da instalação; os ficheiros novos de código vão declarados). Nada instalado, vivo e Sala real
não tocados, sem rede (servidores locais em 127.0.0.1; `HTTP(S)_PROXY=127.0.0.1:9`).

## 1 · O que está dentro

| parte | origem | como entrou |
|---|---|---|
| **freio** (teto D38 antes do pedido, D41, dedup pelo vídeo, C2) | `freio-social-v2` 35109baa | linha direta (é a base do maestro) |
| **maestro** (rodada social num comando, baixador, proposta 037 fora das migrações, D80) | `maestro-social-v2` 2111473a | linha direta |
| **roteiro dos 41 canais** (ensaio a seco, ferramentas `ferramentas/canais41/`, rodadas) | `canais-41-runbook-v1` 403bbb31 | os 7 commits próprios por cherry-pick; **sem** o commit de junção com o vivo (cccd9c0d) e **sem** o mapa regerado (403bbb31). Um conflito, só no `architecture.declared.json` (duas peças novas no mesmo sítio): ficaram as duas. **Conferido: os 14 ficheiros que o roteiro mexe (fora do mapa) são byte a byte os do 403bbb31** — nada do que a junção resolveu à mão se perdeu |
| **canais de pesquisa presos no feed** (os 9 em RETRY_AFTER, 7 de pesquisa) | `canais-pesquisa-v1` 494b7b36 | **acrescentado por mim, fora da lista da missão**: o roteiro dos 41 já traz as rodadas 22-26 para estes 9, mas o código que os leva para a rota do Scrap (`importar_do_coletor.presos_no_feed`) não estava nem no vivo nem no roteiro — sem ele essas rodadas não têm fonte |
| conserto | este ramo | o mutante do freio «o transcritor volta ao yt-dlp nu» procurava o comando ANTIGO do yt-dlp (o maestro passou a montá-lo por `argumentos_do_yt_dlp`): o script de mutação do freio **parava a meio desde o maestro-v2** — lá só corri a mutação do maestro. Corrigido aqui |

**Impressão do pacote:** 28 commits sobre `69b0e23f`; árvore `0aa07e414fe623e7bfbf4da6c7942da2760c4237`; 46 ficheiros.
**ff-only sobre `69b0e23f` = SIM.** Os 46 ficheiros **não incluem nenhum** dos 18 livros que o robô do vivo está a
escrever (medido às ~10:55). **Nenhuma migração** entra (a 037 está em `supabase/propostas/`).

## 2 · Baterias juntas (sem rede)

- **Testes das três partes juntas: 112 OK** (baixador 5 · canais-41 6 · canais presos 3 · dedup 8 · freio 11 · maestro 12
  · C2 6 · D80 8 · vídeo na Sala 6 · pelo Scrap / importar (v5) 25 · prova-teto social 22 · teto web 1 = 10/10 casos).
  O aviso real do coordenador (`bc4-aviso-vivo.txt`) ficou com o mesmo sha256.
- **Mutação:** freio **14/14** · maestro **13/13** · canais presos **3/3** (à mão).
- **Regressão** (44 suítes de Scrap/YouTube/LinkedIn/teto/onda/social/canais): vivo `69b0e23f` 844 testes · pacote 915 —
  **as mesmas 14 falhas herdadas**, linha a linha.
- **A transcrição funciona nesta máquina (medido offline):** no `py` 3.12 da casa, `fala_local.disponivel()` = sim,
  `cuda_disponivel()` = 1 placa, e o modelo `small` carrega do disco em 16,7 s com `HF_HUB_OFFLINE=1`. (Em 24/09 falhava
  pelas bibliotecas cp311; alguém as trocou para cp312.)

## 3 · ROTEIRO DE INSTALAÇÃO (o coordenador aplica)

**0 · Parar e guardar**
```
touch curadoria/PARAR.flag            # e esperar a volta do bot acabar
git rev-parse HEAD                    # tem de ser 69b0e23f — se andou, PARAR e pedir rebase
```
Cópia com sha256, antes de tudo, de: `curadoria/italy_contracts_curator.json`, `regras/italy_contracts_onboarded.json`,
`curadoria/LIFECYCLE-*.json`, `curadoria/DESBLOQUEIO-LEDGER-V1.jsonl`, `curadoria/SOURCE-ID-ALLOCATION-V1.json`,
`candidatas/FONTES-CANDIDATAS.json`, `data/collection-ledger/italy/runs.ndjson`.

**1 · Código — ff-only**
```
git fetch origin && git merge --ff-only origin/lote3-social-v1
```
Reiniciar o supervisor. Sozinho, isto não muda livro nenhum.

**2 · Os 9 canais presos → rota do Scrap (bot ainda parado)**
```
py curadoria/importar_do_coletor.py                     # conferir: os 9 PRESO_NO_FEED (IT-T5-042,043,044,045,047,048,050, IT-T7-016,018)
py curadoria/importar_do_coletor.py --pelo-scrap --ids=IT-T5-042,IT-T5-043,IT-T5-044,IT-T5-045,IT-T5-047,IT-T5-048,IT-T5-050,IT-T7-016,IT-T7-018
```
Esperado: os 9 com contrato `SCRAP_FASE canal-youtube`, `CANARY_PENDING` e uma tarefa `VALIDATE_ROUTE` cada (ensaio na
cópia: 9/9). Não vai à rede.

**3 · Tirar o `PARAR.flag`.** O bot faz os 9 `VALIDATE_ROUTE` e pára em `CANARY_PENDING` (sem rede).

**Desfazer:** livros da cópia do passo 0; código `git reset --keep 69b0e23f` e reiniciar o supervisor.

## 4 · A 1.ª COLETA SOCIAL REAL (depois de instalar; missão própria, VPN IT, rede autorizada)

**O caminho que funciona HOJE sem esperar nada:** o maestro com `--canario` e o **áudio** de vídeos escolhidos.
- Pelo áudio, os itens trazem `OWNER_AUTHORIZED=SIM` e a política escrita (`social_matriz`, `FETCH_AUDIO_BYTES`): a régua
  social aceita. Pela API (`canal-youtube`) as duas marcas vêm vazias e a régua reprova tudo — é o **P1** do roteiro dos
  41 (e P2-P4: workflow, runners, banco), que **não bloqueiam** este caminho.
- **O que falta a alguém escolher: os `VIDEO_ID`** — um vídeo de **até 9 min** por canal (a listagem só corre no GitHub,
  com a chave). O maestro recusa-se a correr um canal sem vídeo (`SEM_VIDEO_E_SEM_CHAVE`, não é falha).

**Canais de agrónomos/pesquisa já na rota do Scrap no vivo (`CANARY_PENDING`, lido às ~10:50):**
IT-T7-026 **CONAF — Ordine dei Dottori Agronomi** · IT-T5-038 UNINA Agraria · IT-T5-040 CRPV · IT-T5-192 Olio Officina ·
IT-T5-193 (crea.gov.it) · IT-T5-037 CNR ISAFOM ⚠️ (é um canal do CNR em youtube.com — os pedidos vão ao youtube.com e
não ao cnr.it, mas o aviso da coordenação diz «sem CNR»: **decisão do coordenador** se entra). Depois do passo 2: os 7 de
pesquisa (Navarra, UNIBO, Minoprio, ISPRA, UNIBA, UNICT, Bolzano).

**Os comandos:**
```
py ferramentas/maestro_social/maestro_social.py --so-plano --canario --fontes=IT-T7-026,IT-T5-038,IT-T5-040,IT-T5-192,IT-T5-193
py ferramentas/maestro_social/maestro_social.py --correr --autorizado-pelo-dono --canario \
    --fontes=IT-T7-026,IT-T5-038,IT-T5-040,IT-T5-192,IT-T5-193 \
    --videos=IT-T7-026:<ID>,IT-T5-038:<ID>,IT-T5-040:<ID>,IT-T5-192:<ID>,IT-T5-193:<ID> \
    --saida=<pasta nova>
py ferramentas/maestro_social/maestro_social.py --relatorio --estado=<pasta nova>/MAESTRO-SOCIAL-ESTADO.json
```
Uma onda = 1 vídeo YouTube (4 pedidos: 3 youtube.com + 1 googlevideo.com, um só orçamento D41) — 5 canais, 5 ondas.
O freio trava o 6.º pedido; VPN conferida antes e depois de cada canal; prova-teto por onda; se parar, `--retomar`.
Precondições do maestro: as variáveis da Sala (`micro_coleta.precondicoes`) e **sem** `BANCO_DESCARTAVEL_URL`.
A transcrição corre na GPU (medido: o motor carrega). Depois: `py curadoria/regua_social.py --corridas … --aplicar
--vivo` com o bot parado.

## EM PALAVRAS SIMPLES

- **Juntei tudo num pacote só**: o freio, o maestro, o roteiro dos 41 canais, e — por conta minha — o conserto dos 9
  canais presos, porque o roteiro já contava com eles e sem o conserto eles não teriam por onde passar.
- **Nada briga:** o pacote encaixa direto em cima do que está rodando e não mexe em nenhum caderno que o robô usa.
- **Testei tudo junto:** 112 testes certos; estraguei o código de propósito de 30 jeitos e os testes pegaram os 30; nos
  testes vizinhos, só as 14 falhas velhas de sempre.
- **Achei um erro meu:** o teste de sabotagem do freio tinha deixado de funcionar desde o maestro (procurava um texto que
  eu mesmo tinha mudado). Consertei, e agora pega os 14.
- **Boa notícia:** a transcrição funciona nesta máquina (antes falhava), com a placa de vídeo.
- **Para a 1ª coleta de verdade** (vídeos de agrônomos e pesquisadores com transcrição): falta só **alguém escolher um
  vídeo curto (até 9 min) de cada canal** — CONAF, UNINA, CRPV, Olio Officina, CREA. O canal do CNR depende de você
  (a regra atual diz "sem CNR").
