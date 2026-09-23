# RELATÓRIO SOC6 — OS DOIS PORTÕES VERMELHOS DO CI (PARADA PELA D25)

> Branch `ci-portoes-v1` a partir de `origin/unificacao-v1 @ 4ec62114` · 2026-09-23.
> **PARADA a meio** por ordem da coordenação (D25, ~19:20: a Big Collection vem primeiro). O que
> está aqui está limpo e publicado; o resto fica descrito abaixo para retomar.
> Nada no serviço vivo; nenhum banco de teste aberto; VPN IT verificada (PASS às 19:07).

## O que se mediu

* **CI público (API sem token):** na `unificacao-v1` o `system-map.yml` tem **SYSTEM MAP CHECK
  verde** e **MAP RULES CHECK + COLETA CHECK vermelhos** desde o PRIMEIRO run da branch
  (91b5f38e, 23/09 04:14) — vieram herdados das linhas-mãe. O último run 100% verde do
  `system-map.yml` em qualquer branch é de 14/09 (`claude/gifted-shannon-8u9l78`).
* **As mensagens de erro** não se leem sem sessão do GitHub. Criei `.github/workflows/ci-diagnostico.yml`
  (sem segredo): corre no MESMO ambiente os passos vermelhos e faz commit da saída em
  `ci-diagnostico/saida/` (run 35925018824). Os 11 passos reprovam lá como no CI.

## Feito (bloco 1, commit 0d50bda8)

| Passo | Causa | Correção |
|---|---|---|
| COLETA 4n2 «a coleta tem UMA porta» | `coleta/eu_regulatorio_executor.py` tinha um helper chamado `preservar` (o nome do dono do RAW); o encanamento P3/P11 lia ali uma segunda porta. Só larga o PDF para a porta ir buscar. | renomeado `largar_pdf` → **ENCANAMENTO=PASS** (14 invariantes) |
| COLETA 3 «padrão não piorou» (parte) | o relatório **rebentava** num `join` com DOCUMENT_ID nulo e escondia 3 regras; e observações FALHADAS (sem documento) contavam como «documento sem sha / sem FACT_TIME / sem cadência» (37 e 122 falsos) | a falha não é documento: as 3 regras de observação ficam **ok (0 = chão)** |

## Por fazer

**COLETA CHECK — o que é LEI (proposta, NÃO aplicada):**
1. `padrao_da_coleta`: 3 regras de coletor pioraram (data 33 vs chão 26; fonte≠facto 32 vs 20;
   descarte 33 vs 30) — são coletores/derivadores novos desde o chão (`adaptador_linkedin`,
   `adaptador_youtube`, `executor_texto_de_html/pdf`, `executor_transcricao_midia`, `scrap_colheita`,
   `social_envelope`, `youtube_oficial`, …). Opções: cada dono põe o carimbo (vários são do Scrap),
   ou o dono da régua decide que derivadores não são coletores e/ou refixa o chão. **Decisão.**
2. `padrao_da_coleta`: 22 corridas de 14/09 sem IP de saída (chão 0). Histórico append-only: não se
   corrige; ou a regra passa a valer a partir de uma data, ou refixa-se o chão. **Decisão.**
3. `testa_golden_path_pdf` T25: exige que o orquestrador não mencione `executor_texto_de_pdf`, mas
   desde 2bbf25cd/643b7d3f (12–13/09) o orquestrador lê o DERIVED e leva o texto à Admissão — a
   própria prova dizia «será ligado depois». Atualizar a prova à arquitetura atual é **decisão do
   dono da prova**.
4. `testa_coleta_canonica`: «colete materiais de pesquisadores» dá T6 (o apelido mudou para T6 em
   `leis/territorios.py`) e o item de teste «Ensaio de campo com DOI» em T7 é hoje NÃO com prova T5
   (régua mais estrita). O fixture ficou para trás das decisões — **confirmar com o dono** e
   atualizar o fixture.
5. `testa_golden_path_pdf` T30 (carimbo do mapa): falhou no diagnóstico com clone raso; o job real
   do COLETA usa `fetch-depth: 0` — **por medir** se falha lá.

**MAP RULES CHECK — por triar (os dois ajudantes foram parados a meio):**
* `test_system_map.py`: 11 reprovadas — réguas por decidir (C-DESBLOQUEIO-PACOTE,
  C-DUAS-PORTAS-MEDIDORES, C-RECOLLECTION-CENSO); régua que carimba ≠ régua que mede
  (C-DETECTOR-CAPA-GABARITO, C-MICRO-COLETA-INSTRUMENTO); 5 réguas em Z-REGRAS sem carimbar
  («mudou o número — alguém decide»); receita com 2 consumidores (C-MICRO-COLETA-INSTRUMENTO +
  C-ORQUESTRADOR); `nao_sei_sobrevive_no_acervo`; `scanner_e_deterministico`;
  `tem_autor_LIVRO-DE-DECISOES`; 4 de ordem das zonas/famílias na vista. Mistura de dados do mapa
  (`architecture.declared.json`) e LEI.
* `test_base_da_auditoria`: a referência `claude/sala-persistente-preflight-real-v1` não existe no
  clone raso do CI (CANNOT_MEASURE); localmente acusa código funcional mudado desde essa base —
  a base declarada ficou velha. **Decisão** de qual é a base auditada (a linha da Big Collection?).
* `test_verdade_da_collection_actual` (3 sobreviventes, dependem da base acima),
  `test_reconciliacao_do_universo` (119 ≠ 155; reconciliação commitada ≠ regerada),
  `test_quatro_planos` (revisão não cobre 4 arestas), `test_cadeia_declara_io` (6 leituras órfãs;
  MEDIDO_VARRE declarado ≠ corrida), `test_ordem_por_dependencia` (classe sem contrato). Por triar.

**Ferramentas deixadas:** `.github/workflows/ci-diagnostico.yml` + `ci-diagnostico/PEDIDO.json`
(mudar `VEZ` e fazer push volta a medir); cópia limpa em `C:\Users\London1\soc6-clone` (worktree, removida
no fim desta parada).

## Não se sabe ainda
Se, com tudo o que é DEFEITO corrigido, os dois portões ficam verdes sem decisões de LEI: **NÃO SEI** —
pelo que já se mediu, não (as regras de coletor e do chão exigem decisão).
