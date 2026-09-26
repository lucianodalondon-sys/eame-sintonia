# BOLETINS-V2 · plano de instalação (NÃO instalar — quem instala é o coordenador)

Ramo `boletins-v2`, sobre o **vivo `ce28040c`** (já contém `e5cd691f` = PACOTE-TEMPO-LUGAR e as 57 entregas
seguintes: HR-6 `escolher_alvo`, LEGACY-99 links malformados, canal YouTube, onda3-v2). Junta, por esta ordem:
JANELA-FORMAS (D42) → C-JS/D46 → T2-BOLETINS (D47) → Umbria (D51.3) → BOLETINS-DATA-LOCAL (D61/D62/D69,
DA-11/12/13) → **uma lista única de réguas**.

## O que resolve (a razão desta missão)

Havia **duas listas** do que conta como régua de hoje, e cada ramo só via a sua:
`REGUAS_QUE_ADMITEM = {DETAIL/v1, SOCIAL/v1}` (SOC-ONDA2, no vivo) e `REGUAS_CORRENTES = {DETAIL/v1,
PAGINA_BOLETIM/v1}` (D42, nos boletins). Agora há **uma**, com um dono (`curadoria/ready_split.py`):

    REGUAS_QUE_ADMITEM = {DETAIL/v1, SOCIAL/v1, PAGINA_BOLETIM/v1}

`REGUAS_CORRENTES` e `e_corrente()` saem; o portão, a ponte (`reconciliar_livros`), o `worker`, os red teams e os
testes perguntam todos à mesma lista. Cada régua continua juiz da sua forma e nenhuma é por omissão
(`SOCIAL/v1` só nasce com o veredito READY de `regua_social.py` para a fase do contrato — nunca no worker).

**Buraco do vivo que fica fechado:** os red teams `RT-A10` (ponte) e «READY_LEGACY entra na Collection» (canónico)
procuravam `if regua != RS.REGUA_CURRENT:` no portão, que a régua social já tinha trocado — no vivo o ataque
reporta **ANCORA_NAO_ENCONTRADA** (não corre). Aqui apontam a linha real e o ataque **morre**.

## Writeset (código e testes; `git diff --name-status ce28040c boletins-v2`)

```
A coleta/texto_de_pdf.mjs                    M coleta/italy_pilot_collect.mjs     M coleta/retrato_html.mjs
A regras/identidade_do_motor_cli.mjs         M regras/motor_de_rota.mjs           M regras/motor_de_rota_test.mjs
A regras/boletim_data_local_test.mjs
M curadoria/canario.py      M curadoria/ready_split.py      M curadoria/collection_gate.py
M curadoria/worker.py       M curadoria/reconciliar_livros.py   M curadoria/reparar_contrato.py
M curadoria/validar_contratos.py   M curadoria/red_team_ponte_curador.py   M medidas/red_team_canonico.py
A curadoria/test_boletim_data_local.py  A curadoria/test_canario_hrefs.py  A curadoria/test_canario_pdf.py
A curadoria/test_pagina_boletim.py      A curadoria/test_receita_identidade.py  A curadoria/test_receita_pdf.py
A curadoria/test_strip_suffix.py        M curadoria/test_um_so_canario_promove.py  A tests/test_pagina_boletim_local.py
A provas/janela_formas/* · provas/t2_boletins/* · provas/boletins_data_local/*   (105 ficheiros de prova)
M system-map/* (cadeia)
```

**Não vai na instalação:** nenhum contrato. Os 9 contratos de boletim propostos
(`provas/boletins_data_local/CONTRATOS-PROPOSTOS-D61.json`) entram depois pela porta (`reparar_contrato.aplicar`)
e pelo `onboardar_rotas_provadas` — decisão do dono. O que já colhe **não muda**: nenhum contrato vivo declara
`FORMA`, `STRIP_SUFFIX`, `IDENTITY` pela porta, nem BASES de data/lugar; o canário HTML sem BASES fica igual.

## Passos

1. Parar o bot (como nas instalações anteriores); `git status` limpo no vivo; guardar `git rev-parse HEAD` (= `ce28040c`).
2. `git merge --ff-only origin/boletins-v2` no vivo (o ramo **contém** `ce28040c`: é avanço rápido, sem junção nova).
3. Conferir: `PYTHONIOENCODING=utf-8 py system-map/scripts/correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`;
   `PORTOES_POS_COMMIT` → `IMPRESSAO_DO_CARIMBO=IGUAL`.
4. Provas rápidas (sem rede): `node regras/boletim_data_local_test.mjs` (29/29) · `node regras/motor_de_rota_test.mjs`
   (68/68) · `cd curadoria && py -m unittest test_regua_social test_pagina_boletim test_um_so_canario_promove
   test_boletim_data_local` (verde).
5. Religar o bot.
6. **Desfazer:** `git reset --keep ce28040c` no vivo (depois de guardar `git status`/`git diff`), religar.

## Provas (sobre `ce28040c`)

| prova | resultado |
|---|---|
| 26 módulos do Curator (social, boletins, HR-6, LEGACY-99, YouTube, onda3, revisão, ready_split…) | todos verdes |
| motor · boletim · recollection · incrementalidade · paridade | 68/68 · 29/29 · 31/31 · 31/31 · 32/32 |
| coletor de verdade, servidor local: `boletim_pdf_local` · `pagina_boletim_local` | 6/6 · 6/6 |
| mutação: lista única · D61+DA-13 · porta+canário | **3/3 · 17/17 · 9/9** |
| red team da ponte (`red_team_ponte_curador.py`) | **17/17 aplicados e mortos** (no vivo: 16, o RT-A10 sem âncora) |
| `test_collection_gate` | 22/23 — a 1 falha é **herdada**: os 3 caminhos sem classificação (`coleta/nome_da_pasta.mjs`, `onda_web.py`, `buscar_indices_d40.py`), iguais no vivo `ce28040c` |
| suíte base do red team | falha nos mesmos 2 herdados (`test_zy_censo_dos_livros_reais` + o de cima), igual no vivo |
| `regras/italy_contract_test.mjs` | 348/77 — as 77 herdadas (conferido por nome contra o vivo) |

## ⚠️ A saber

- **Um teste de reconciliação escreve no livro real da pasta onde corre** (fontes `IT-T99-00x` em
  `curadoria/italy_contracts_curator.json`) — acontece no red team; restaurei pelo Git nas duas vezes. Não é desta
  missão, mas quem correr o red team no vivo vai sujar o livro vivo.
- O teste M2b do motor passou a medir sem o fim de linha (CRLF da cópia Windows reprovava a mesma ordem).
- A âncora dos red teams RT-A12/RT-A17 (`passos["BODY_UTIL"] = (dados.get(...) is True`) foi mantida de propósito.
