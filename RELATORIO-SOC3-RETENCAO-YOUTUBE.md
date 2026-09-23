# RELATÓRIO SOC3 — O PRAZO DE 30 DIAS DO YOUTUBE (D20), O ROTEAMENTO E A D21

> Branch `retencao-youtube-v1` a partir de `origin/curator-youtube-v1 @ aeb2ce62` · 2026-09-23.
> Serviço vivo NÃO tocado · Collection NÃO correu · Sala real NÃO tocada · nada pago · nenhuma conta.
> Código do Scrap NÃO tocado (`coleta/scrap_*`, `adaptador_*`, `social_matriz.py`, `sintonia-scrap.yml`)
> e `pedido/receitas.py` NÃO tocado (writeset do engenheiro, `scrap-portas-v1`).

```
RETENCAO_30D          = FEITA na parte que guarda os dados (guarda/retencao_youtube_api.py + migração 033)
ENSAIO_29_30_31       = banco descartável real: só o de 31 dias vira lápide; 29 e 30 ficam
CHECAGEM_DIARIA       = --checar → PASS / FAIL / NAO_SEI (FAIL antes, PASS depois, no ensaio)
LAPIDE                = linha fica (preserved=false + motivo); tabela lapide_de_retencao guarda path, sha256, bytes, data, motivo
AUDIO_LOCAL_INTOCADO  = YES (audio/wav nem é candidato; envelope com rota yt-dlp = NAO_E_DA_API; testado)
PROPOSTA_ROTEAMENTO   = escrita e medida: hoje 6/50 chegam ao Scrap; com a proposta 50/50
D21                   = aplicada no QUALIFY: 7 canais → 5 herdam território, 2 NAO SEI
```

## 1. D20 — a retenção de 30 dias

### Onde vive (dono conferido no System Map)
`guarda/retencao_youtube_api.py`, na peça **C-DONO-DA-ESCRITA** (Z-GUARDA), a mesma de
`preservar_coleta.py` e `banco_*`. A tabela nova é a migração **033** (`supabase/**`, peça C-SUPABASE).
Nenhuma outra peça foi alterada: os armazéns (`ArmazemLocal`, `ArmazemSupabase`) continuam sem verbo
de apagar — o único apagador da casa é este, e só para esta regra.

### O que conta como «dado da API» — medido, não presumido
Nenhuma coluna do banco guarda a rota. Ela vive DENTRO do byte guardado (o envelope do Scrap traz
`ROUTE` e `DISCOVERY_ROUTES`). Por isso a regra lê o byte:

| Situação | Veredicto | Apaga? |
|---|---|---|
| JSON preservado, > 30 dias, todas as rotas `youtube-data-api-v3:*`, sha256 confere | `API` | **sim** |
| idem, com exactamente 30 dias | fora do prazo? **não** — 30 dias ainda está no prazo | não |
| `audio/wav` (áudio local) | nem é candidato | não |
| JSON com rota `yt-dlp:public_audio` | `NAO_E_DA_API` | não |
| rota mista (API + outra) | `NAO_SEI` | não |
| byte fora do armazém, ou sha256 diferente do da linha | `NAO_SEI` | não |
| a mesma cópia é também de uma observação ainda no prazo | `EM_USO_NO_PRAZO` | não |

### A lápide
Numa transacção por observação: insere a lápide (`storage_path`, `sha256` do que existia, `bytes`,
`regra`, `motivo` PRAZO_VENCIDO/RENOVADA, `rota`, `captured_at`, `apagado_em`, `prova`); põe
`raw_asset.preserved=false` com o motivo; troca o texto na **Sala** (`sala_de_espera.texto`) e nas
tabelas sociais (`conteudo.titulo/descricao`, `comentario.texto`) por uma marca «APAGADO PELA REGRA
DOS 30 DIAS». Só DEPOIS apaga o ficheiro (e os dos derivados). Se o ficheiro não sair, a checagem
diz `FAIL` com `LAPIDE_COM_BYTE_VIVO` — o erro fica à vista. **A proveniência nunca é apagada**:
a linha do `raw_asset`, o `storage_object`, a corrida e o sha256 ficam.

A migração 033 tem três travas no próprio banco: `regra` só `YOUTUBE_API_III_E_4_30D`; `motivo` só
PRAZO_VENCIDO/RENOVADA; `rota` só `youtube-data-api-v3:%` — uma lápide de áudio é recusada pelo banco.

### Renovar
«Renovar» é uma colheita NOVA (outra observação). A cópia velha, passados 30 dias, sai com motivo
`RENOVADA`; a nova fica. Se a renovação trouxe bytes IGUAIS (a mesma cópia no armazém), a cópia não
sai enquanto a observação nova estiver no prazo.

### O ensaio (banco descartável real: initdb + 32 migrações pela cadeia canónica)
`tests/test_retencao_youtube_api.py` — **16 testes, OK**:
* 29/30/31 dias → só o de 31 vira lápide; os ficheiros de 29 e 30 continuam;
* áudio `wav` 31 dias e JSON `yt-dlp` 31 dias → intocados; JSON da API sem byte → `NAO_SEI`, intocado;
* texto na Sala, título/descrição/comentário sociais e o ficheiro do derivado saem; 2 lápides (raw + derivado);
* renovar: a velha sai com `RENOVADA`, a nova fica; 2.ª passagem = 0 lápides;
* cópia partilhada com observação no prazo → não sai;
* checagem: `FAIL` antes, `PASS` depois; lápide com byte vivo → `FAIL`;
* byte trocado (sha256 diferente) → `NAO_SEI`, não se apaga;
* o banco recusa lápide com rota que não é da API; `--aplicar` num banco não descartável sem
  `--operacional` → recusado (exit 4).

### A checagem diária
`py guarda/retencao_youtube_api.py --checar` (só lê; exit 0 só com PASS). O cron **não** foi ligado:
tem de correr na máquina onde vive o armazém local (o orquestrador escreve em `ArmazemLocal(RAIZ)`),
e ligar um horário contra a memória operacional é passo de virada — está no
`docs/operacao/PARA-O-RUNBOOK-X2-SOCIAL.md`, passos 5-6.

### O que falta (e de quem é)
1. **Cópia remota (bucket `raw` da Supabase)**: se o byte também foi enviado para lá, não sai.
   `ArmazemSupabase` não tem verbo de apagar, por desenho. Dar-lho é decisão do dono do armazenamento.
2. **A rota não tem coluna.** Ler o byte funciona, mas custa uma leitura por candidata e fica `NAO_SEI`
   quando o byte não está aqui. Proposta para o engenheiro do Scrap / C-INGRESSO: gravar a rota da
   observação numa coluna (`raw_asset.rota`), para a checagem ser SQL puro. Não fiz: toca o envelope
   do Scrap e o ingresso.

## 2. PROPOSTA — «o YouTube é sempre o Scrap» (para o engenheiro aplicar)

Medido (`provas/roteamento_youtube_proposta.py`, sem rede, só planos):

| | chega ao Scrap | vai para outro executor | ninguém serve |
|---|---|---|---|
| HOJE | **6** (T8, T9) | **34** (`italia-recorrente`, filtro `canal_id` cai) | **10** (T12 não tem executor) |
| COM A PROPOSTA | **50** | 0 | 0 |

Pedido sem fase, em todos os territórios: **inalterado** (medido).

**A mudança** — `pedido/receitas.py`, dentro de `resolver()`, imediatamente antes de
`return Plano(` (linha **752** em `aeb2ce62`):

```python
    # O YOUTUBE (e toda a fase do Scrap) E SEMPRE O SCRAP. A plataforma decide o
    # executor; o territorio decide o assunto. A lista de fases e a que o proprio
    # registo `scrap-colheita` declara em `serve_fases` — nada inventado aqui.
    scrap = next((e for e in EXECUTORES.get("T9", []) if e.get("id") == "scrap-colheita"), None)
    if scrap and fase in (scrap.get("serve_fases") or ()):
        execs = [scrap] + [e for e in execs if e.get("id") != "scrap-colheita"]
```

**O teste** — `tests/test_roteamento_youtube_proposta.py` (já na árvore, 4 testes, OK): hoje importa
`promover_o_scrap` da prova; depois de aplicado, trocar o import para `receitas.resolver` e as quatro
frases têm de continuar verdade (50/50 no Scrap; 44 hoje fora; sem fase = igual; a lista de fases é
a do registo, sem duplicar o executor).

Ressalva: o orquestrador ainda exige a frase com o apelido do território (`leis/territorios.py`);
o pedido continua a dizer o território — ele só deixa de decidir o executor.

## 3. D21 — o canal herda o território do site da mesma organização

Regra no QUALIFY (canal existente), em `curadoria/rota_do_scrap_youtube.heranca_do_site`. Só para
YouTube, só quando o nome não decidiu, só com:
* **ligação oficial** escrita na ficha: `ONDE_VIU = «declarado no site oficial do dono: <site>»`, ou
  `NOTA` com `DISCOVERED_FROM=<página>` + `DISCOVERY_METHOD=CRAWL_LINK` (o crawler tirou o link do site);
* o site com SOURCE_ID e território na casa (tabela, livro do Curator ou ficha do Atlas), por host exato;
* um só território — dois = conflito = `NAO SEI`. Nome ou logotipo: nada compara nomes.

A prova fica no registo de alocação (`MESMA_ORGANIZACAO`) e no `TERRITORY_REASON`.
Resultado nos 7 canais novos (`curadoria/D21-HERANCA-DO-TERRITORIO-V1.json`):

| Canal | Site (ligação) | Território |
|---|---|---|
| CAND-0300 | regione.sicilia.it (crawl) — 9 fontes, todas T12 | **T12** |
| CAND-0423 | crea.gov.it (crawl) — 13 fontes, todas T5 | **T5** |
| CAND-0219 Olio Officina | olioofficina.it (declarado) — IT-T5-046 | **T5** |
| CAND-0221 Soc. Entomologica | societaentomologicaitaliana.it (declarado) — IT-T3-020 | **T3** |
| CAND-0332 = CAND-0335 ARPAE | arpae.it (crawl) — IT-T2-001/039/051/… | **T2** (um só número) |
| CAND-0193 Granarolo | granarolo.it — sem SOURCE_ID | **NAO SEI** |
| CAND-0234 Interpoma | interpoma.it — só candidata | **NAO SEI** |

«Aplicar» aqui é a regra no circuito, provada com a lane redirecionada: o número de fonte real é
cunhado pelo serviço quando as tarefas QUALIFY correrem (runbook, passo 3). Os números do ensaio
(IT-T12-128, IT-T5-085, …) são os que o registo daria hoje, não reservas.

## TESTS · MUTATION

* `tests/test_retencao_youtube_api.py` 16 OK (banco real) · `tests/test_roteamento_youtube_proposta.py`
  4 OK · `curadoria/test_d21_heranca.py` 13 OK · `test_soc2_curator_youtube` + `test_worker_qualify` OK.
* Mutação D21: **9/9 mortos** (1.ª ronda 8/9 — «sem ligação» sobrevivia porque o motivo não era
  conferido; o teste passou a exigir o motivo certo).
* Mutação da retenção: **18/18 mortos**, banco descartável real. Cada ataque começa num banco
  copiado de um modelo recém-migrado (`create database … template`), e cada morte vem do teste certo
  (o nome do teste que o matou está registado). ⚠️ A 1.ª ronda estava CONTAMINADA: o lixo de um
  ataque (linhas cujo armazém já tinha sido apagado) fazia o seguinte falhar, e contaria mortes que
  não eram do ataque. Foi parada, o banco que ela deixou ligado foi desligado, e refeita isolada.
* Vizinhos (17 módulos + os novos, 292 testes): as mesmas 3 falhas da base `ffef59cf`, por nome.
* Bancos descartáveis de 22/09 de outras sessões continuam ligados nesta máquina (3); não são desta
  missão e não lhes toquei.
