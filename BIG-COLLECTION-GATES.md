# BIG-COLLECTION-GATES — os gates do §25, medidos (BC1, 23/09/2026)

> O §25 do `MANDATO-CONTINUO-V2-BOT-LUCIANO.md` tem **20** gates, não 25. Todos foram
> medidos contra a árvore `origin/unificacao-v1` @ `940f3b14` e, quando pedem o serviço,
> contra a produção (bot `cd4203db`, ponte `5c02bbe4`), só com leitura no vivo. Veredito
> **YES** só com um comando corrido hoje e o resultado dele; o que só um documento afirma
> fica **NAO_SEI**.
>
> ⚠️ O PC caiu (tela azul) por volta das 13 h. O serviço e a Sala real ficaram
> desligados e não voltaram sozinhos. Os gates 1 a 3 mostram as duas leituras: antes e
> depois da queda.

## Resultado

**GATES_YES = 16 / 20** (BC3, 23/09 ~18 h). YES: 1, 2, 3 (voltam sozinhos pela Tarefa
`SINTONIA-Arranque`; o bot **só** com egresso IT), 4, 5, 6, **7 = SAFE pela D25**, 8, 9, 11, 14,
15, 17, 18, 19, 20. Destes, 4 valem **só sem internet ou só em cópia** (5, 8, 9, 14) e 1 só
para it/pt/en (11). **NO: 2** (10 capa/matéria, 12 unificação). **NAO_SEI: 2** (13 micro pela
rede real, 16 suíte inteira). Pelo §25, a Big Collection **ainda não** pode avançar, e hoje
**nem a rede está em IT**.

**BC2 também:** a Sala real (54330) voltou pelo `ligar_sala.cmd` depois da queda; integridade
só-leitura: as 5 tabelas com o **md5 igual** ao backup da BC1 (61 / 1405 / 1097 / 908 / 389).
Prova: `ferramentas/big_collection/BC2-SALA-RELIGADA.json`.

| # | gate | veredito | prova (comando) | resultado medido | falta · dono |
|---|---|---|---|---|---|
| 1 | SOURCE_CURATOR_CONTINUOUS | **YES**, e volta sozinho pelo arranque (BC3), **só com egresso IT** | Tarefa `SINTONIA-Arranque` + `ferramentas/arranque/arranque_sintonia.ps1`; `supervisor.py --estado` | BC3: de tudo parado, o arranque não lançou o supervisor porque o egresso era **BR** (real: a VPN caiu às ~17:49), e fica a medir de minuto a minuto. A guarda pôs o bot quieto pelo `PARAR.flag` às 17:54, sem rede pelo Brasil medida. O arranque automático do supervisor com egresso IT **ainda não foi visto** (a VPN não voltou durante a prova) | religar a VPN IT e ler no `arranque-AAAAMMDD.log` o `SUPERVISOR lancado` · coordenador |
| 2 | DISCOVERY_CONTINUOUS | **YES** quando o supervisor corre; parada de propósito fora de IT | o mesmo | corre dentro do supervisor: segue o gate 1 | o mesmo do 1 |
| 3 | BRIDGE_AUTOMATIC | **YES**, e volta sozinho pelo arranque (BC3) | Tarefa `SINTONIA-Arranque`; `ponte_automatica.py --saude` | BC3: de tudo parado, observador lançado da `ponte-viva` com `--lane`; `A_TRABALHAR`, `SAUDAVEL`. Sala de pé em 8 s, com md5 igual ao backup; vigia lançado; segundo arranque ignorado (mutex + IgnoreNew) | um logon real (proibido reiniciar na missão) |
| 4 | PROMOTION_PROVEN | **YES** | diário da ponte + livro do bot; `provar_ponte_curador.py` e `test_ponte_promocao` numa cópia | ao vivo: portão 29 → 36 (as 7 da D10) → 37 (IT-T8-051); recalculado sobre uma cópia dos livros da ponte = 37; testes 13/13 | — |
| 5 | DEMOTION_PROVEN | **YES só em cópia** | `provar_ponte_curador.py`, `test_ponte_promocao.PontaAPontaNaFotografia` | cópia: 12 → 11, `SAIRAM=[IT-T99-001]`. Ao vivo, nenhuma das 18 travessias tirou fonte do portão | ver um rebaixamento real sair do portão · coordenador |
| 6 | SINGLE_WORKER_INVARIANT | **YES** | `test_supervisor` (30), `test_worker_pendurado` (11), `test_fila_windows` (13), `test_status_liveness` (4), `test_worker_volta_sobrevive` (4), numa cópia; lista de processos | todos OK; ao vivo, 4 workers um de cada vez. Ressalva: a trava é do supervisor, não do worker | — |
| 7 | APPROVED_SOURCE_ROUTE_COVERAGE (= SAFE) | **SAFE** pela D25 (coorte = READY do portão com rota provada; cada fonte dela tem rota provada) · **NO** se a coorte forem as 37 READY inteiras | canário real `medidas/canario_rotas_elegiveis.py` nas 27 (egresso IT) + dono `curadoria/onboardar_rotas_provadas.py --aplicar` + `micro_coleta.py plano` | BC2: canário 20 ROUTE_PROVEN / 4 UNKNOWN / 3 CAPABILITY_BLOCK; onboardar ENTRA 18 / FICA 7; **PRONTAS 10 → 19**; as 18 de fora aparecem cada uma com o seu `FALTA` (8 sem receita web T8, 7 sem contrato, 1 T12, 1 T9, 1 rota), não caladas como ELIGIBLE. Fonte a fonte em `ferramentas/big_collection/BC2-FONTES-27.json` | receitas web T8/T12/T9 (10 fontes) · dono das receitas; as 4 UNKNOWN (rede/robots desta saída) e as 3 CAPABILITY · curador |
| 8 | INCREMENTALITY_PROVEN | **YES, só sem internet** | `ensaio_offline.py --duas-passagens` (8 fontes do G1 e, à parte, as 3 do BC1) · `node regras/incrementalidade_test.mjs` · `node provas/recollection_indice_local.mjs` · `node provas/ttl_mutable_local.mjs` | 2.ª passagem: 0 re-pedidos, 0 «mudou» falso, 0 «novo» falso, Sala +0 (G1: 89 puladas, 10 revistas; BC1: 55 puladas). Testes 31/0 · 13/0 · 12/0 | provar pela rede real · A4/A5 |
| 9 | RECOLLECTION_PROVEN | **YES, só sem internet** | `node regras/recollection_test.mjs` · `provas/recollection_http_local.mjs` · `recollection_timeout_local.mjs` · `paridade_duas_rodadas.mjs` · `regras/paridade_test.mjs` | 31/0 · 15/0 · 8/0 (o processo pendura depois do resumo; morto aos 280 s) · 13/0 · 32/0 | matéria real e site lento que responde · lane de recoleta |
| 10 | LISTING_DETAIL_GATE_PROVEN | **NO** (em `940f3b14`) | `py scripts/detector_capa/medir_gabarito.py` | juiz actual: **63/109** capas passariam como notícia; **6/37** notícias barradas como capa. A V1 entrou na linha na 6.ª passagem (`de4dec2b`, V1A) e **não foi medida lá** | medir a V1A no gabarito, com amostra maior · lane V1A/LD |
| 11 | MULTILINGUAL_GATE_PROVEN | **YES para it/pt/en** | `py -m unittest tests.test_admissao_multilingue tests.test_politica_nao_sei tests.test_lingua_da_porta tests.test_lingua_unica` · `py provas/a_porta_le_italiano.py` · ensaio C9 | 19/19 · 79 com 1 falha (só a barra `\` do Windows contra `/`) · 20/0 · C9 PASS | fr/es/de saem NÃO SEI de propósito («língua sem régua»): uma fonte espanhola sairia toda NÃO SEI · dono da Admission |
| 12 | CANONICAL_UNIFICATION_PROVEN | **NO** | `git merge-base --is-ancestor <ramo> origin/unificacao-v1` | a produção (`cd4203db` / `5c02bbe4`) **não está em linha nenhuma**; a linha andou para `de4dec2b` durante a medição (6.ª passagem: A4, V1A, D1, A3, SOC2/SOC3); a A5 (`cortesia-coleta-v1`) só tem um checkpoint **não testado** | passo I do runbook (instalar a linha na produção, provado sobre `de4dec2b`: 11/11 livros = produção) · coordenador + M5 |
| 13 | MICRO_COLLECTION_PROVEN | **NAO_SEI** | `ensaio_offline.py` (G1, 8 fontes; BC1, 3 fontes) | G1: 8/8, 99 = 99 = 99, SIM 12 / NÃO 34 / NÃO SEI 53, Sala +12, C3–C9 PASS. BC1: 3/3, 55 = 55 = 55, SIM 12 / NÃO 10 / NÃO SEI 33, Sala +12, C3–C9 PASS. C1 FAIL e C2 PENDENTE_HUMANO nos dois (sem internet); `LISTINGS_REJECTED` sem contador no código | a micro com rede real neste código (a A4 correu noutro ramo, com SIM 0) · coordenador / A4 + A5 |
| 14 | PROVENANCE_COMPLETE | **YES para documentos novos, só sem internet** | ensaio (C4) · `py provas/red_team_collection_ate_a_sala.py` com banco descartável | 0 falhas; cadeia completa em 99/99 (G1) e 55/55 (BC1); o banco recusa 4/4 ligações falsas | acervo antigo e Sala real não medidos · dono da Sala |
| 15 | CRITICAL_RED_TEAM_SURVIVORS = 0 | **YES (0)**, com 2 roteiros de ataque velhos | `recollection_red_team.mjs` (+ `_estrito`) · `paridade_red_team.mjs` · `curadoria/red_team_ponte_curador.py` · `provas/red_team_duas_portas.py` · `provas/mutacao_do_gate.py` · `provas/red_team_collection_ate_a_sala.py` · `provas/a_sala_sobrevive_ao_processo.py` | 12/12 · 12/12 · 8/8 · 17/17 · 14/14 · 13/13 · 28/28 · 30 ataques. Corridos como estão, dois mentem: o M4 da paridade procura uma linha que já não existe e conta «1 sobrevivente» (feito à mão, morre); o duas-portas pendura no M05 (o texto aparece 2× na Admission; corrigido só na cópia, 14/14) | actualizar os dois roteiros · donos da paridade e da Admission |
| 16 | NEW_FAILURES = 0 | **NAO_SEI** | `py -m unittest discover -s tests` na árvore instalada, comparado por nome com a base | não medido hoje: a suíte inteira leva mais de 30 min e pesa na memória, e a máquina tinha acabado de cair. A última medição é da M5E (5.ª passagem), e é só um documento. A branch BC1 não mexe em código | medir no dia, antes do passo 0 · coordenador |
| 17 | SYSTEM_MAP_CHECK = PASS | **YES** | `py system-map/scripts/correr_a_cadeia.py VALIDAR` na branch BC1 | `SYSTEM_MAP_CHECK=PASS` no commit final desta branch | — |
| 18 | KNOW_HOW_UPDATED | **YES** | `SINTONIA-EAME-KNOW-HOW.md` | secção sem número da BC1 (este commit) | — |
| 19 | WORKTREE_CLEAN | **YES** (branch BC1) | `git status --short` | 0 linhas depois do commit final | a produção tem livros sujos por natureza (o bot escreve) |
| 20 | LOCAL_HEAD = REMOTE_HEAD | **YES** (branch BC1) | `git rev-parse HEAD origin/big-collection-runbook-v1` | iguais no fecho | — |

## O que falta, por dono

| dono | o quê | gates |
|---|---|---|
| coordenador / dono | **religar a VPN IT** (caiu para o Brasil às ~17:49 de 23/09; o bot está quieto pela guarda até lá). O arranque automático está instalado (BC3) | 1, 2 |
| coordenador + M5 | instalar a linha na produção (passo I do runbook) e, depois, medir de novo 10 e 13 sobre essa árvore | 12, 10, 13 |
| A5 → M5 | robots e ritmo dentro do coletor (`cortesia-coleta-v1`, hoje só um checkpoint não testado), juntados à linha | 13, e o B2 do runbook |
| dono das receitas web | receita web para T8 (8 fontes Edagricole, já com contrato), T12 (1) e T9 (1) | 7 (ondas seguintes) |
| curador | as 4 UNKNOWN (robots ilegível desta saída: cnr, coldiretti veneto, unaprol; DNS: indire) e as 3 CAPABILITY_BLOCK | 7 (ondas seguintes) |
| dono da identidade | IT-T2-056/-106 (páginas de idioma da ARPAE) e os 5 da CIA / 2 da Terra e Vita (mesmo site e padrão) | — |
| coordenador | uma micro pela rede real, com a Sala real, sobre a linha instalada | 13, 8, 9, 14 |
| coordenador | a suíte por nome no dia (mais de 30 min; não correr com a máquina apertada) | 16 |
| donos da paridade e da Admission | os dois roteiros de ataque velhos | 15 |
| M5 (ponte) | `provar_ponte_curador.py` e `red_team_ponte_curador.py` escrevem a fonte de teste IT-T99-001 no `italy_contracts_curator.json` da árvore onde correm | — |
