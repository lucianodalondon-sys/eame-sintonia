# SEPARAR-A-B v5 — o YouTube pelo Scrap e a régua VIDEO, sobre o vivo ce28040c

Ramo `legacy-99-v5`, **nascido de `ce28040c`** (o vivo). Substitui a `legacy-99-v4`
(55221bec, nascida de e5cd691f). **Não instalado** — quem instala é o coordenador.

## Em palavras simples

- O robô de hoje (ce28040c) **já tinha** a parte A (copiar do coletor os contratos de
  sites), o C (revisitar as fontes antigas) e o D (link quebrado não derruba o conserto).
  Tinha também o **B antigo** — o Curator a ir sozinho à página do canal no YouTube —
  "desligado", mas ainda no código, e com uma porta aberta: se alguém pedisse o número
  de um canal ao importador, ele importava o canal pelo caminho velho.
- A v5 **fecha essa porta e tira o B antigo**. O YouTube passa a ter **um só dono**: o
  Scrap (o robô das redes sociais). O Curator só escreve no contrato qual caminho usar;
  o Scrap colhe; a régua do Curator confere o recibo.
- A régua agora exige, em cada vídeo, **4 provas** (D53): página pública do vídeo,
  título, data de publicação e o canal certo. Falta uma, não passa. A transcrição não é
  exigida.
- Os **21 sites** já foram importados no robô em 25/09 às 22h: **12 prontos** (passaram
  na régua de hoje, `DETAIL/v1`), **8** reprovados no teste, **1** à espera de nova
  tentativa. A importação sozinha não aprovou nenhum.
- Os **41 canais YouTube** antigos: no ensaio, **41 de 41** passaram para o caminho do
  Scrap, **0** barrados, todos ficaram "à espera do teste", **0** prontos sozinhos.

## Um só dono da rota YouTube — o Scrap

| Quem | O quê | Onde |
|---|---|---|
| nomeia a rota | o contrato do canal diz `SCRAP_FASE` · fase `canal-youtube` | `curadoria/rota_do_scrap_youtube.py` (produção, SOC2) |
| escreve a troca feed → Scrap nos canais antigos | bloco 4 do desbloqueio (provas + invariantes) | `scripts/desbloqueio/aplicar_desbloqueio.rota_do_scrap` (produção) |
| chama o bloco 4 só para os canais pedidos | `importar_do_coletor.py --pelo-scrap --ids=` | **novo nesta v5** |
| colhe (o canário é uma colheita) | `scrap-colheita`, API oficial (chave no runner) | Scrap |
| julga o recibo | `SOCIAL/v1` + **D53** (4 provas por vídeo) | `curadoria/regua_social.py` |
| o Curator vai ao YouTube? | **não**: `worker.etapa_canary` devolve `BLOCK DO_SCRAP` | produção |

Sai do código (estava inerte desde o ONDA3-REBASE): `canario.canario_youtube_canal`,
`url_da_rota`, `url_do_canal`, `YOUTUBE_CANAL`, o controlo `LOTE-YOUTUBE-CANAL` e o
despacho no `worker`. O adapter `CANAL_PUBLICO_YOUTUBE_V1` da tabela do coletor nem
existe nesta árvore.

## Os commits (um bloco por commit)

| Commit | Bloco |
|---|---|
| 08d74afa | **A** — `importar_do_coletor` só HTML; o canal YouTube fica `ROTA_DO_SCRAP` e é recusado |
| 4d0e0cb1 | **B antigo sai** do código; `tests/test_onda3_b_inerte.py` prova que já não existe |
| 9295d481 | **B** — `--pelo-scrap`: bloco 4 sobre os livros inteiros, grava só as pedidas, tudo ou nada, ledger do bloco 4, depois `remedir` |
| c428b379 | **VIDEO (D53)** na régua social |
| e4fd2f1a · fac8daef | mutação (v4 e v5) |
| 38c0999f · 193633b5 | ensaios (v4 sobre e5cd691f; v5 sobre ce28040c) |
| 636f089e | mapa: declara `C-LEGACY-99` |

C e D **não têm commit na v5**: o vivo já os tem, iguais aos da v4.

## Provas

- **Mutação 32/32** mortos, 0 a escrever em livros (`MUTACAO-V5.json`), com
  `tests/test_onda3_b_inerte.py` na lista.
- **Ensaio** (`ENSAIO-V5.json`; sha256 da cópia em `ENSAIO-V5-copia-livros.sha256`;
  rede fechada por proxy morto): plano `IMPORTA 0 · PELO_SCRAP 41 · FICA 11` (8 só
  `case` no coletor, 3 PDF). B: 41/41 na rota do Scrap, 0 saltos, `conferir` do Scrap OK
  41, `CANARY_PENDING` 41, régua sem canário do Scrap = `LEGACY` 41. 0 READY.
  ⚠️ O bot estava a correr quando se copiaram os livros: a cópia é uma fotografia de
  ficheiros lidos um a um, não um instante único.
- **Regressão por nome** e **mapa**: ver o fim deste documento.

## Plano de instalação (o coordenador instala; um escritor; nada de rede)

**0 · Antes**
- Confirmar que o vivo ainda é `ce28040c`. Se andou: **não** fazer ff; pedir rebase.
- Corte com sha256: `curadoria/italy_contracts_curator.json`,
  `regras/italy_contracts_onboarded.json`, `curadoria/LIFECYCLE-*.json`,
  `curadoria/DESBLOQUEIO-LEDGER-V1.jsonl`.

**1 · Código** (ff-only sobre `ce28040c` = **SIM** enquanto o vivo for `ce28040c`)
```
git fetch origin legacy-99-v5
git merge --ff-only origin/legacy-99-v5
```
Reiniciar o supervisor. Nada muda nos livros por si só: o B só age com `--pelo-scrap`.

**2 · B — os 41 canais para a rota do Scrap** (com o bot PARADO: `curadoria/PARAR.flag`)
```
py curadoria/importar_do_coletor.py                 # conferir: PELO_SCRAP=41
py curadoria/importar_do_coletor.py --pelo-scrap --ids=<lote>
```
- Não faz pedidos à rede (o Scrap só é **lido** nos ficheiros dele). Lotes de 10 bastam;
  cada lote é tudo-ou-nada e diz o porquê se o bloco 4 saltar um canal.
- Esperado: cada canal em `CANARY_PENDING`, contrato `SCRAP_FASE`, `COLETADO_POR` na tabela
  do coletor, 2 linhas por canal no `DESBLOQUEIO-LEDGER-V1.jsonl`.
- Tirar o `PARAR.flag`. O `VALIDATE_ROUTE` pára em `CANARY_PENDING` (é do Scrap).

**3 · O canário deles** é uma colheita do Scrap, pedida pelo orquestrador e julgada por
`py curadoria/regua_social.py --corridas ... --aplicar` — é **outra onda**, com o teto
D38 (YouTube = 1 plataforma, 5 pedidos por corrida). Não faz parte desta instalação.

**Desfazer**
- Livros: repor do corte (o livro de estados é só de acrescentar: voltar por transição nova).
- Código: `git reset --keep ce28040c` e reiniciar o supervisor.

## A ordem com a SOCIAL-QUALIFICAR (para não pisar)

Medido: os **9 canais** do ensaio da SOCIAL-QUALIFICAR **não** estão entre os **41**
(0 canais em comum, 0 SOURCE_ID em comum). Os ficheiros em comum são só os do mapa
(`system-map/data/architecture.declared.json` e os gerados).

1. **Código:** instalar **uma** das duas por ff-only sobre `ce28040c`; a segunda passa a
   não ser ff — junta-se por cima (`merge --no-ff`), o conflito do
   `architecture.declared.json` é só "as duas acrescentaram uma peça no fim" (ficam as
   duas), e os gerados regeneram-se pela cadeia. Sugestão: **LEGACY-99 v5 primeiro** (só
   Curator, sem rede), SOCIAL depois.
2. **Livros:** nunca os dois ao mesmo tempo. O passo 2 acima escreve no livro do Curator,
   na tabela do coletor e no livro de estados; o semear do QUALIFY social escreve na fila
   e na alocação, e o bot escreve contratos. **Primeiro** o `--pelo-scrap` com o bot
   parado; **depois** tirar o `PARAR.flag` e semear o QUALIFY social.
3. **Rede (teto D38):** o canário dos 41 canais e a micro social gastam a **mesma**
   plataforma (YouTube). Nunca na mesma corrida; a micro social primeiro, os 41 depois,
   em lotes que caibam em 5 pedidos por corrida.
4. A colisão de canal está guardada nos dois lados: o bloco 4 recusa um canal que já
   seja de outra fonte (tabela, livro **ou alocação**), e o worker recusa um segundo
   contrato para o mesmo canal.

## O que isto não prova

- Não há no disco **nenhum recibo real** da fase `canal-youtube` (a chave da API está no
  runner): a D53 foi provada com exemplos. Os 12 recibos reais de áudio (19–23/09)
  falham a D53, mas a régua de antes já os reprovava todos.
- A D53 pede as 4 provas em **cada** vídeo: um vídeo privado no meio da lista reprova a
  corrida inteira (escolha conservadora; diz o nome da prova que falta).
- Achado: a régua social antiga aceitava `PUBLISHED_AT = "UNKNOWN"` (só recusava
  `"NAO SEI"`). A D53 fecha isso para `canal-youtube`; nas outras fases continua aberto.
- Ninguém sabe ainda quantos dos 41 canais passam no canário do Scrap.
