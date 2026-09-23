# RELATÓRIO — B4 · O BOT DE FONTES ESTAVA PARADO COM TRABALHO POR FAZER

Missão: `C:/Users/London1/auditoria-madrugada/missao-b4-bot-parado.txt`.
Ramo: `bot-impasse-v1`, base `origin/unificacao-v1` @ `940f3b14`.
Instalado no serviço vivo `source-curator-service-v1`, ramo `servico-20260923-0923`
(`cd4203db` → `bdc310e4` → `3fcec513`, publicado).
Data: 2026-09-23. Houve uma tela azul às 12:50 a meio da missão; o trabalho estava no
disco sem commit e foi retomado sem perda.

```
CAUSA_PROVADA              = SIM (três donos, três defeitos — §1)
TAREFAS_CRIADAS_AO_VIVO    = 11   (fila 2530 -> 2541, 17:39:43Z, SOCIAIS_ENFILEIRADAS 0)
WORKER_A_TRABALHAR         = SIM  (PID 40908: 2 voltas, 32 etapas — 18 OK · 4 RETRY · 5 BLOCK · 5 FAIL; saiu limpo)
DUPLICADOS                 = 0    (as 11 nao tinham tarefa nenhuma; 2.a corrida do FEEDER: 0 criadas, 932 ignoradas)
READY_PROMOVIDAS_PELA_B4   = 0    (READY_TOTAL 143 antes e depois)
SINAL_DE_DISCOVERY         = 186 NOT_NEEDED -> 0 DISCOVERY_NEEDED (fora do backlog: 175 HTML + 4 amostra ja tentadas)
DISCOVERY_AO_CHEGAR_A_ZERO = ACTIVO no vivo desde 17:55:42Z (DISCOVERY_ASSINATURA_FILA gravada)
TESTES                     = 69 verdes nas suites tocadas · mutacao 7/7 mortas
SUITE_DO_CURATOR_POR_NOME  = ver §4
SYSTEM_MAP_CHECK           = PASS
TEMPO_PARADO               = 1693 s (1.a troca: inclui esperar a VPN voltar a IT) · 38 s (2.a troca)
EGRESSO                    = US as 14:10 (BLOCKED, bot deixado parado) · IT as 14:38 e 14:50 (PASS)
```

Legenda: **FATO MEDIDO** = saída de comando que corri; **INFERÊNCIA** = o que concluo;
**NÃO SEI** = sem prova.

## 1 · A causa (FATO MEDIDO, só leitura, 23/09 ~16:40Z)

| livro | o que dizia | porquê |
|---|---|---|
| FEEDER (`ponte_candidatas`) | 932 lidas, 0 enfileiradas | 808 no BRIDGE-LEDGER (733 QUALIFY · 69 POLICY · 6 CAPABILITY) + 124 na caracterização = 932 |
| fila | 0 elegíveis | QUALIFY: 537 DONE · **196 BLOCKED**; todo o resto DONE/BLOCKED/FAILED |
| sinal (`nivel_da_fila`) | backlog 186, NOT_NEEDED | 175 HTML «nunca caracterizadas» + 11 NEEDS_MORE_SAMPLING |
| gatilho | DISCOVERY_EM_INTERVALO (~54 min) | intervalo fixo de 3600 s, mesmo com fila e acervo a zero |

- **D1 · as 11 NEEDS_MORE_SAMPLING não tinham tarefa em lado nenhum.** Estão na
  caracterização, e a ponte tomava «está na caracterização» por «já entrou no curator».
  `alimentar_fila` também não as apanha, porque não têm SOURCE_ID. Nenhuma das 11 estava no
  BRIDGE-LEDGER, e nenhuma tinha tarefa na fila.
- **D2 · as 175 já tinham virado tarefa.** 175 de 175 HTML_NOVAS têm QUALIFY, e 175 de 175
  estão BLOCKED («território indeterminado pelo nome»). O sinal contava-as como trabalho por
  fazer, e por isso escrevia NOT_NEEDED.
- **D3 · o gatilho esperava o intervalo** mesmo quando o trabalho real tinha acabado de
  chegar a zero.

## 2 · As correções, cada uma no seu dono

| dono | mudança |
|---|---|
| `ponte_candidatas._ja_no_curator` | NEEDS_MORE_SAMPLING fica fora do «já no curator». `REGRA_VERSAO` entra na assinatura do FEEDER; sem isso a regra nova ficava em NO-OP, porque a assinatura antiga só via candidatas e fila |
| `gatilho_discovery.assinatura_da_condicao` | + `REGRA_VERSAO` + bytes da caracterização (a ponte passou a lê-la) |
| `baldes_das_candidatas` | publica `HTML_NOVAS_IDS` e `NEEDS_MORE_SAMPLING_IDS` |
| `nivel_da_fila.medir` | desconta das duas listas as que já tiveram QUALIFY; mostra-as em `FORA_DO_BACKLOG` (`HTML_QUALIFY_BLOQUEADO`, `NEEDS_MORE_SAMPLING_JA_TENTADAS`) |
| `gatilho_discovery.talvez_alimentar` | re-mede os elegíveis DEPOIS do feeder. Com fila e acervo a zero **e a fila diferente da do último discovery** → dispara já (`DISCOVERY_ANTECIPADO`). Fila igual → o intervalo manda. Grava `DISCOVERY_ASSINATURA_FILA` depois de cada discovery |

**O primeiro D3 estava errado.** Disparava sempre com fila e acervo a zero: 240 crawls por
hora. Três testes de `test_abastecimento` apanharam-no (241 chamadas ao feeder onde o teste
esperava 1). A guarda contra essa rajada é agora a assinatura da fila, e tem mutação própria
(M4).

**A 2.ª troca (`aae8586c`)** saiu da prova ao vivo: das 11, 4 bloquearam, e o sinal
continuava a contá-las (backlog vivo 4). Passaram a ser descontadas como as 175.

## 3 · A prova ao vivo (FATO MEDIDO)

Das 11 que a ponte enfileirou às 17:39:43Z:

| destino | quantas | quais |
|---|---|---|
| QUALIFY → SOURCE_ID novo | 7 | IT-T8-058 · IT-T11-013 · IT-T7-163 · IT-T10-044 · IT-T7-165 · IT-T11-012 · IT-T7-164 |
| QUALIFY BLOCKED (território pelo nome = NÃO SEI) | 4 | CAND-0003 Fitogest · CAND-0058 Mangimi & Alimenti · CAND-0151 Terremerse · CAND-0156 Diachem |

Das 7 com número: 5 `CONTRACTED_CANARY_FAILED` (o molde genérico não achou item, o que bate
com «precisa de mais amostra»), 1 `RETRY_AFTER` (IT-T8-058), 1 `CAPABILITY_BLOCK`
(IT-T7-164). Nenhuma chegou a READY. As falhas de canário voltam pelo REVALIDATE do
`alimentar_fila`.

**Discovery 17:55:42Z:** disparou, gravou a assinatura da fila, e trouxe **0 candidatas com 0
pedidos à rede**. Das 70 sementes, 63 já estão gastas; as 7 que sobram são todas
GENERICA/UNKNOWN e a regra recusa-as antes da rede. **INFERÊNCIA:** o catálogo de sementes
está esgotado. O bot já não está parado por defeito de contagem; está parado porque não tem
fonte nova. Isso é trabalho do produtor de discovery (sementes novas), não desta missão.

## 4 · Testes

- Suítes tocadas: `test_impasse_b4` (22), `test_nivel_da_fila` (5), `test_gatilho_discovery`,
  `test_ponte_candidatas`, `test_abastecimento` — todas verdes.
- Mutação em cópia fora do repositório (`PYTHONDONTWRITEBYTECODE=1`): M1 ponte volta a incluir
  NEEDS_MORE_SAMPLING · M2 sinal não desconta tentadas · M3 sem disparo antecipado · M4 sem
  guarda anti-rajada · M5 regra fora da assinatura · M6 não grava a assinatura depois do
  discovery · M7 amostra não desconta tentadas → **7/7 mortas**.
- Suíte inteira do curator, comparada por nome entre `940f3b14` e `aae8586c`: ver o anexo no
  fim deste relatório.

## 5 · Instalação (o procedimento de hoje)

1. Antes: processos (1 supervisor, 0 worker, o observador da ponte que só lê), sha256 dos
   ficheiros vivos, cópia de segurança em `C:\cutover\b4-20260923-1411\antes` e `antes-2`.
2. `PARAR.flag` → o supervisor saiu sozinho (`SUPERVISOR_PARADO_POR_FLAG`).
3. `git checkout <commit B4> -- <ficheiros>` na pasta do bot, commit só desses ficheiros, push.
   Os livros do bot ficaram com o sha256 de antes (conferido).
4. Portão de egresso IT → PASS → apagar `PARAR.flag` → `Start-Process powershell -NoExit`,
   `py curadoria/supervisor.py` na pasta do bot.

**DESFAZER:** `PARAR.flag`, repor os ficheiros de `antes/` (ou `git revert 3fcec513 bdc310e4`
no ramo do bot), relançar como no passo 4.

## 6 · NÃO SEI e ressalvas

- Depois da tela azul, o supervisor reiniciado correu um discovery às 16:55Z pela saída dos
  EUA. Foram 0 pedidos à rede, porque as 7 sementes foram recusadas pela regra. Não fui eu que
  o lancei.
- O `superficie/rede.py --help` não mostra ajuda: corre a sonda de 7 endereços públicos.
  Aconteceu uma vez nesta missão (pedidos gratuitos, sem credencial).
- As 4 bloqueadas por território e as 175 continuam à espera de decisão semântica
  (`DECISOES-SEMANTICAS-V1.json`) ou de caracterização. A B4 não as destrava; só deixa de
  mentir sobre elas.
