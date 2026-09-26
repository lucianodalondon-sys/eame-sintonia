# BLOQUEADAS-268 · 25/09 (medido 23:55–00:40 local) · SÓ LEITURA do vivo

Vivo `source-curator-service-v1` @ `ce28040c`: nada escrito, nada parado, sem rede, Sala não tocada.
Fonte dos números: `curadoria/LIFECYCLE-QUEUE-V1.json` (fila), `candidatas/FONTES-CANDIDATAS.json` (fichas),
`italy_contracts_curator.json`, `LIFECYCLE-LEDGER-V1.json` e `DECISOES-SEMANTICAS-V1.json` do vivo.
Tudo linha a linha em `curadoria/BLOQUEADAS-268-V1.json` (ramo `bloqueadas-v1`), feito por `curadoria/bloqueadas_268.py`.

**280 tarefas = 268 BLOCKED + 12 FAILED = 279 fontes** (IT-T7-050 tem duas). 242 ainda são candidatas (CAND-,
sem classe T); 38 já têm SOURCE_ID (T12 17 · T7 10 · T5 4 · T8 3 · T2/T3/T10/T11 1 cada) + 1 fonte de prova.
Por tipo de tarefa: QUALIFY 241 · VALIDATE_ROUTE 18 · CANARY 16 · REPAIR_CONTRACT 4 · BUILD_CONTRACT 1.

**«Fontes ganhas» = quantas podem entrar na coleta.** Uma fonte destravada ainda tem de passar contrato + canário.
Taxa histórica medida no livro: das 822 fontes com contrato no ledger, **155 estão READY = 18,9 %**. A coluna
«esperado» é tamanho × 18,9 % — é estimativa, não promessa (para as que já têm contrato e só falharam por rede,
a taxa deve ser maior; não medi).

## Tabela — ordenada por «mais fontes destravadas por menor esforço»

| # | motivo (medido) | tarefas | ação que destrava | quem | rede? | fontes que podem entrar (esperado a 18,9 %) |
|---|---|---:|---|---|---|---|
| 1 | link com acento rebenta o pedido (`UnicodeEncodeError '\xe0'`) — IT-T7-252 peritiagrari.it | 1 | **código: CONSERTADO neste ramo** (`canario.url_segura`) + re-enfileirar | coordenador instala | sim (re-medir) | 1 (tem contrato) |
| 2 | Coldiretti fecha a ligação da saída VPN (`WinError 10054`, 5×) — IT-T7-050 coldiretti.it (canário **e** o «robots não pode ser lido» 5×), IT-T7-051/052/053 regionais, IT-T7-045 anga.it, IT-T7-058 unaprol.it | 7 (6 fontes) | outra saída IT que a Coldiretti aceite (já medido antes: 403 → 000 na saída Proton) e re-enfileirar | coordenador (VPN) | sim | até 6 (todas com contrato, T7) |
| 3 | «robots não pode ser lido — UNKNOWN» — **IT-T5-006** cnr.it/it/news | 1 | confirmar portão IT e re-enfileirar (UNKNOWN é falha de ligação, D39, não proibição) | coordenador | sim | 1 (tem contrato) |
| 4 | território já decidido COM prova, mas fora de IT (FAO, CIMMYT, CropLife INT; INRAE FR; bpi.gr GR; Biostimulants Europe, Fertilizers Europe EU) | 7 | decidir se o robô numera fontes EU/INT (hoje o QUALIFY só cunha `IT-`) | **dono** | não | até 7 (esperado ~1) |
| 5 | página nova do MESMO site de uma fonte que já existe, site com UMA só classe — lidas à mão: **HERDA_PLAUSIVEL** (SNPA linee guida, ARSARP pubblicazioni, Acta Italus Hortus, Agraria Sassari eventos, ISPRA ×3, Entomologica eventos) | 8 | regra do dono: herdar a classe do mesmo site (como a D21 faz para canais), ou decidir 1 a 1 | **dono** | não para a classe | até 8 (~1,5) |
| 6 | contrato que falta na árvore do Curator (IT-T10-034 granariamilano.it, IT-T5-041 crpv.it; + IT-PROVA-R de teste) | 3 | importar o contrato do coletor pela porta (`importar_do_coletor`, LEGACY-99 v2) e re-enfileirar | coordenador | não | até 2 |
| 7 | identidade trocada (organização real, endereço errado): «Sherwood — Foreste ed Alberi Oggi» (sherwood.it é uma rádio), «OP Alegra» (alegra.it não é a OP de Faenza) | 2 | corrigir o URL da candidata pela porta | dono/curadoria | sim (achar o URL certo) | até 2 |
| 8 | fonte responde mal: 403 (Regione Campania ×5, IT-T8-046/047 ×2), 404 (IT-T2-156, IT-T3-036 abruzzo), 422 (selfi abruzzo), login (intranet abruzzo → authra) | 11 | re-medir com rede; o login (IT-T12-036) é recusa; 404 = procurar endereço novo | curadoria | sim | até ~9 (~2) |
| 9 | **território indeterminado** e SEM leitura que decida: 47 «prova insuficiente», 32 nunca revistas, 1 janela do robots (Rete Rurale só 01–03 UTC) | 80 | provas pelo canal DECISOES-SEMANTICAS (≥1 institucional + ≥2 conteúdos, com sha256, pela saída IT) e decisão Opus/humano | dono/Opus | **sim** | até 80 (~15) |
| 10 | mesmo site, classes MISTAS (Laore, LaMMA, FEM, Agriligurianet ×2, MASAF ×2, DISTAL, Periti Agrari comunicati) | 9 | decisão semântica (a classe não se herda) | dono/Opus | sim | até 9 (~2) |
| 11 | canal YouTube (exige channel_id e molde de vídeo) | 22 | capacidade da rota do Scrap (YT-METADADOS) + D21 para herdar a classe do site | Scrap engineer | sim | até 22 (~4) |
| 12 | capacidade nova (IT-T7-164: ramo de índice «SIM») | 1 | Scrap engineer | outro dono | sim | 1 |
| 13 | robots do site PROÍBE o endereço (Regione Abruzzo ×10, politicheagricole, macfrut, nocciolapiemonteigp.it, lombardianotizie tv, pianetapsr) | 15 | **nenhuma pela D39** — só achar outra entrada que o robots permita | curadoria | sim | ~0 (cada uma, se houver entrada) |
| — | **limpeza** (não ganha fonte, tira ruído da fila): **82 propor recusa** (34 «não é fonte» e 15 «fora do agro» e 14 «semente errada» da revisão semântica anterior; 19 por regra explícita: acessibilidade/privacy/avisos ×6, WhatsApp/Spotify ×6, Parlamento/Senado/Camera/Governo ×4, turismo ×3) · **23 duplicadas** (20 «página de outra fonte», 3 «possível mesma fonte»: EIMA ×2 e a página de agricultura do ISTAT) · **8 duplicadas da organização** (a casa de um site que já é fonte) | 113 | confirmar a lista e recusar pela porta (`fonte_nova.recusar`) — 1 decisão, uma vez | **dono** | não | 0 |

Soma: 1+7+1+7+8+3+2+11+80+9+22+1+15+113 = **280**.

**IT-T5-006 e IT-T7-050 (os «robots.txt 5×»):** IT-T5-006 é o CNR (`cnr.it/it/news`), linha 3 — UNKNOWN de
robots é falha de LIGAÇÃO, não proibição; re-enfileirar com o portão IT conferido. IT-T7-050 é a Coldiretti,
linha 2 — o robots «não pode ser lido» porque a Coldiretti fecha a ligação da nossa saída (o canário dela
falhou 5× com o mesmo `WinError 10054`); sem outra saída IT, nenhum código a destrava.

## Consertos (SHA)

Ramo **`bloqueadas-v1`** sobre o vivo `ce28040c`, NÃO instalado (plano: `PLANO-INSTALACAO-BLOQUEADAS.md`):
- `aa29196a` — **link com acento** (linha 1 da tabela): `canario.url_segura`, testes e mutação acima;
  e a ferramenta de leitura `bloqueadas_268.py` + `BLOQUEADAS-268-V1.json`.
- `f06d245d` (ROBO-DIAGNOSTICO) — juntado a este ramo: o painel do robô ocioso deixa de assustar.
Nenhum outro motivo destrava por código: todos os outros pedem rede, uma decisão ou a capacidade de outro dono.

## O que o coordenador / dono decide

**Coordenador (sem decisão nova):**
1. Instalar `bloqueadas-v1` e re-enfileirar IT-T7-252 (1 fonte).
2. Saída IT que a Coldiretti aceite → re-enfileirar as 6 fontes Coldiretti (linha 2) e o CNR (linha 3).
3. Importar os 2 contratos em falta (linha 6) pela porta do LEGACY-99.

**Dono:**
4. Fontes fora de IT (linha 4): o robô passa a numerar EU/INT? — 7 com território já provado.
5. Herança de classe do mesmo site para PÁGINAS (linha 5), como a D21 faz para canais? — 8 lidas à mão.
6. Confirmar a **limpeza de 113** (lista em `BLOQUEADAS-268-V1.json`, `PROPOSTA` = PROPOR_RECUSA / DUPLICADA_DE /
   `LEITURA_A_MAO` = DUPLICADA_DA_ORGANIZACAO): nenhuma fonte perdida, fila mais limpa.
7. Autorizar uma ronda de provas com rede para as 80 + 9 (linhas 9–10) — é onde está o volume (~17 fontes).

## EM PALAVRAS SIMPLES

- Das 280 tarefas paradas, **113 não são fontes de verdade** (página de «acessibilidade», WhatsApp, turismo, uma
  rádio confundida com uma revista florestal, cópias de fontes que já temos). Não se ganha nada com elas — só
  limpar, com um «sim» do dono.
- As **mais baratas de destravar** são poucas mas quase certas: 1 que eu já consertei (um endereço com acento
  que o robô não sabia pedir), **6 da Coldiretti** que só precisam de uma VPN que o site aceite, 1 do CNR, 2
  contratos que faltam importar.
- Com **2 decisões do dono** (aceitar fontes europeias/internacionais e deixar uma página herdar a classe do
  próprio site) ficam prontas para tentar mais 15.
- O **grosso** (80 + 9 fontes) precisa que alguém confirme, com provas colhidas na internet, a que «gaveta»
  cada uma pertence. É o trabalho mais caro, e é onde estão mais fontes (umas 17, pela taxa de hoje).
- 22 são canais do YouTube: esperam a ferramenta de outra equipe. 15 o próprio site proíbe — essas não se forçam.
