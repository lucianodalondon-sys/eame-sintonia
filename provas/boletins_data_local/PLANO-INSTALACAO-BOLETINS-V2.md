# BOLETINS · plano de instalação (NÃO instalar — quem instala é o coordenador)

**Versão 3 (boletins-v3), a partir do vivo `83de0ccd` (C9, 26/09 02:01).** Substitui a versão 2 (sobre `ce28040c`).

Ramo `boletins-v3` = `boletins-v2` (3a001f06: lista única de réguas + todos os boletins) **+ o vivo `83de0ccd`**.
A junção só teve conflito em ficheiros GERADOS (mapa, `docs/fontes/INDICE-DE-FONTES.md`,
`docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`): ficaram os do vivo e refizeram-se pela cadeia do mapa.
Nenhum conflito de código.

## O que traz

- **Uma lista única de réguas** (`curadoria/ready_split.REGUAS_QUE_ADMITEM = {DETAIL/v1, SOCIAL/v1,
  PAGINA_BOLETIM/v1}`): portão, ponte, worker, red teams e testes perguntam à mesma lista. Sai `REGUAS_CORRENTES`.
- **Os boletins:** receita PDF e «página = boletim» (D42), porta com `STRIP_SUFFIX`/`IDENTITY`/`PDF_SEM_EXTENSAO`,
  data e lugar declarados pela rota (D61/D62/D69: `PUBLISHED_AT`, `FACT_TIME` só ligado ao facto,
  `BULLETIN_PERIOD` como evidência, `FACT_LOCATION`, cada um com BASE), texto do link com BASE `INDICE` (DA-13),
  leitor `PDF_TEXT` único (`coleta/texto_de_pdf.mjs`).
- **Buraco do vivo fechado:** os red teams do portão (`RT-A10`, «READY_LEGACY entra na Collection») voltam a ter
  âncora e a morrer.

## Conferências feitas antes do PRONTO

| conferência | resultado |
|---|---|
| **ff-only** sobre o vivo | `83de0ccd` é antepassado de `boletins-v3`: a instalação é avanço rápido, sem junção nova |
| **os 16 livros vivos** (os `M` de `git status` na pasta viva: `curadoria/*-V1.json`, `italy_contracts_curator.json`, `italy_contracts_onboarded.json`, `data/collection-ledger/*.ndjson`, `data/samples/LIVRO-DE-DECISOES.json`, `RUN-MANIFEST.json`, `candidatas/FONTES-CANDIDATAS.json`) | **nenhum** está nos 135 ficheiros do writeset (`v3/16-livros.txt`, `v3/writeset-v3.txt`) · o writeset não toca em `data/` |
| **testes por NOME contra o vivo** (`testes_por_nome.py`: 22 módulos do Curator, 7 de `tests/`, 8 de Node — o mesmo corredor nas duas árvores, com os MESMOS dados) | as falhas do ramo são as do vivo, nome a nome: `italy_contract_test` 77 = 77 (`v3/ict-vivo.txt` = `v3/ict-ramo.txt`); `test_collection_gate` 1 = 1 (os 3 caminhos sem classificação); `test_reconciliar_livros` 0 = 0. Os módulos novos dos boletins (motor 29/29, coletor local 6/6, Curator 12/12…) passam |
| mutação (sobre `ce28040c`, código igual) | lista única 3/3 · D61+DA-13 17/17 · porta+canário 9/9 · red team da ponte 17/17 |

⚠️ Uma leitura enganadora medida e desfeita: na pasta de trabalho, `test_zy_censo_dos_livros_reais` e 7 verificações
da prova de contratos falhavam «só no ramo» — eram do AMBIENTE (livro de coletas local da pasta), não do código;
com os mesmos dados, ramo e vivo dão os mesmos nomes.

## Passos

1. Parar o bot. `git status` na pasta viva: guardar a lista (os 16 livros ficam como estão — o writeset não os toca).
   Guardar `git rev-parse HEAD` (= `83de0ccd`).
2. `git merge --ff-only origin/boletins-v3` na pasta viva.
3. Conferir que os 16 livros continuam com as MESMAS alterações de antes (`git status` igual ao do passo 1).
4. `PYTHONIOENCODING=utf-8 py system-map/scripts/correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`;
   `PORTOES_POS_COMMIT` → `IMPRESSAO_DO_CARIMBO=IGUAL`. (O validador reescreve gerados com o HEAD novo: repor
   esses gerados com `git checkout -- <ficheiros>`, **nunca** `git checkout -- .`, que apagaria os livros.)
5. Provas rápidas sem rede: `node regras/boletim_data_local_test.mjs` · `node regras/motor_de_rota_test.mjs` ·
   `cd curadoria && py -m unittest test_regua_social test_pagina_boletim test_um_so_canario_promove`.
6. Religar o bot.
7. **Desfazer:** guardar `git status`/`git diff`; `git reset --keep 83de0ccd`; religar.

## ⚠️ NÃO correr o red team da ponte na pasta viva

`curadoria/red_team_ponte_curador.py` corre `test_reconciliar_livros`, que **escreve fontes de teste (`IT-T99-00x`)
no livro de contratos da pasta onde corre** (`curadoria/italy_contracts_curator.json`). Medido duas vezes na bancada.
Corre-se numa cópia, nunca no vivo. **Se alguém o correr no vivo por engano:**

1. parar o bot;
2. `git diff curadoria/italy_contracts_curator.json > <pasta de prova>/diff-livro-red-team.patch` (guardar a prova);
3. conferir no diff que as linhas a mais são SÓ `IT-T99-*` (se houver alterações do bot misturadas, NÃO repor —
   chamar o coordenador);
4. repor SÓ esse ficheiro: `git checkout -- curadoria/italy_contracts_curator.json`;
5. religar o bot.

## Não vai na instalação

Nenhum contrato. Os 9 contratos de boletim propostos (`CONTRATOS-PROPOSTOS-D61.json`) entram depois pela porta
(`reparar_contrato.aplicar`) e pelo `onboardar_rotas_provadas` — decisão do dono. O que já colhe não muda.
