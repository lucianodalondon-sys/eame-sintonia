# INTEGRA-NOITE · LOTE 3 — sobre o lote 2 instalado (`278cd489`)

Ramo `integra-noite-v3`, a partir do vivo `278cd489` (lote 2, instalado às 14:00). **NÃO instalado.**
Estado: **PARADO à espera de decisão da coordenação** (§4) — 3 pacotes juntos; mapa e plano por fazer.

## 1 · Os pacotes

| # | pacote | SHA | base | junção |
|---|---|---|---|---|
| 1 | dedup-doc-v1 | 05aa35c7 | 69b0e23f | limpa |
| 2 | lote3-social-v1 | 2babb52d | 69b0e23f | conflito só na ficha do mapa — ⚠️ ver §3 |
| 3 | extratores-v2-juntos | 2cbfb53f | 69b0e23f (+ quatro-chaves, conserto-regua dentro) | `.gitattributes`: ficam as duas linhas `-text` (`tests/dados/c2-juiz/**` e `tests/dados/lugar_v2/**`), bytes de amostras conferidos 12/12; `donos.generated.json` (gerado) |
| — | sala-leitura-v2 | c035495f | — | **FORA**: não está PRONTO (registo das 13:41: «a missão ainda não está PRONTA»; o `SALA-LEITURA.md` §6 diz testes COM BANCO não corridos) |
| — | lugar-do-publicador-v1 | 140f161a | — | **FORA**: não está PRONTO e não está no GitHub (só nesta máquina) |

Migrações: **nenhuma nova além da 036** (dedup-doc). A `034_o_acervo_guarda_tempo_e_lugar…` do extratores é o
MESMO blob (`407e7c6c`) que já está no vivo desde o lote 1. A 037 do lote3-social está em `supabase/propostas/`
(não é migração).

## 2 · Testes por NOME contra o vivo `278cd489` (mesmos dados, rede fechada, pastas com o nome do vivo)

`provas/integra_noite/lote3-{ramo,vivo}-v1.json`. 86 módulos; **1.206** testes no ramo, **1.027** no vivo.
- **Herdadas, iguais nome a nome: 98** — `italy_contract_test` 77 · `test_tempo_e_lugar_da_publicacao` 12 ·
  `test_forward_instrumentado` 5 · `test_collection_gate` 1 · `test_scrap_rc01_release_candidate` 1 ·
  `test_a_primeira_corrida_da_inteligencia` 1 · `test_lingua_da_porta` 1.
- **NOVAS: 5**, em dois testes do quatro-chaves (LOTE 2, já no vivo) — §4.
- Fora desta bateria (ligam um Postgres descartável, são PESADOS, correm sob a LOCK-PESADO):
  `test_sala_idempotente_por_documento`, `test_sala_dedup_por_document_key`.
  ⚠️ Erro meu: ao investigar, corri `tests.test_quatro_chaves_na_sala` inteiro (tem parte com Postgres
  descartável) **fora** da LOCK-PESADO, ~2 min, 14:25. A bateria por nome também o corre (como no lote 2).

## 3 · ⚠️ Erro meu achado e consertado: a ficha do mapa perdia-se na junção

O meu `juntar.sh` tratava tudo em `system-map/` como gerado e, no conflito, ficava com o lado do ramo. Mas
`system-map/data/architecture.declared.json` é a ficha escrita à mão. Perderam-se as fichas de:
- **LOTE 2, já instalado:** `bloqueadas-v1` 889b2166 (peça `C-BLOQUEADAS-268`) e `destravar-v1` a935a191
  (`C-BLOQUEADAS-DESTRAVAR`, `C-MICRO-PROVA-LOTE1`). O **código** deles está no vivo e inteiro; faltam só as peças
  no mapa (os ficheiros são de `curadoria/`, que a P9 não conta — por isso o validador do lote 2 passou).
- **LOTE 3:** `lote3-social-v1` 2babb52d (`C-CANAIS-41` + 9 ficheiros em peças existentes).

Reposto no ramo (`9c67b95b`) pelo que cada pacote ACRESCENTOU à sua base (só acréscimos; nenhuma remoção, nenhum
campo em conflito). Quatro ficheiros de código novos que nenhum pacote declarou: `leis/boletim_do_campo.py` →
C-LUGAR-COLETA · `coleta/extratores_de_texto.py` → C-EXECUTOR-TEXTO-HTML · `admissao/versao_do_documento.py` →
C-SALA-DE-ESPERA · `provas/migracao_036_ensaio_copia.py` → C-PROVA-COLETA. O `juntar.sh` passou a tratar a ficha
como código (script fora do Git, sha256 `a96b1d06…`; o de reposição `20a768e3…`). Instalar o lote 3 repõe as
peças do lote 2 no mapa do vivo.

## 4 · ⛔ PARADO — duas decisões

**4.1 · A regra do PERÍODO (extratores × quatro-chaves) — decisão de conteúdo.**
`test_quatro_chaves_na_sala`: `test_4_item_sem_chaves_fica_nao_sei`, `test_a_ausencia_e_a_do_contrato_e_nao_o_resultado_da_porta`,
`test_d62_a_precisao_conta_o_que_ha_e_nao_julga`. Um item com `fact_time = "2026-05-02"` e **sem
`fact_time_basis`** tinha as 4 chaves em `NAO SEI`; agora a chave PERÍODO sai `2026-05-02` (e a precisão conta 3
chaves em vez de 2).
- Medido **sem banco** (classe `OContratoLevaAsQuatroChaves`): vivo `278cd489` **13/13 OK**; o **extratores-v2-juntos
  sozinho `2cbfb53f` já falha as mesmas 2** — não é da junção. A regra nova é de propósito
  (`docs/operacao/PERIODO-E-CHAVES.md` §1: «o PERÍODO só de FACT_TIME»), e o próprio documento diz que
  `test_quatro_chaves_na_sala` com banco **não foi corrido**.
- Opções: **(A)** vale a regra nova → atualizo os 3 testes do quatro-chaves (o item «sem chaves» passa a ter
  `fact_time` NAO SEI; a D62 conta 3). **(B)** o período só sai de um `FACT_TIME` **com base provada** → conserto
  de 1 condição em `admissao.periodo_do_fato` (código do extratores), com teste e mutação. B é coerente com o G0/v2
  da Intelligence (FACT_TIME sem base bloqueia) e com «ausência de prova = NAO SEI».

**4.2 · `test_sala_por_nome` (dedup-doc × quatro-chaves) — só o teste.**
`test_cada_valor_vai_para_a_sua_coluna`, `test_as_tres_listas_de_colunas_sao_a_mesma`: `ClientePostgresAusente`.
O dedup-doc fez o `pousar` perguntar primeiro ao banco «a 036 existe?» (`_consultar`); estes testes só substituem
a escrita (`_executar`), e a pergunta nova vai ao `psql` de verdade. O código está certo (tem de perguntar).
Proposta: no teste, `_consultar` responde «036 não aplicada» — o que se mede (cada valor na sua coluna, as 3
listas iguais) não muda. Não aplicado.

**4.3 · Para o plano B (não trava o código): a 036 pela cadeia aplica também a 034 antiga.**
`DEDUP-INSTALAR.md` §4–5: a Sala está na 033; a cadeia canónica aplica **034 (a do vivo = TEMPO_LUGAR, numeração
antiga) + 036**. A D79 diz 034 = lápide, 035 = TEMPO_LUGAR (ramo `acervo-tempo-lugar-v1`, fora dos lotes). Decisão
tua: aplicar a 036 só depois da renumeração D79, ou aplicá-la sozinha fora da cadeia, ou aceitar a 034 antiga.

## 5 · Falta (depois das decisões)

consertos aprovados → bateria por nome outra vez → sob LOCK-PESADO: os 2 testes com Postgres (ramo × vivo) + UM
mapa → plano único A/B → PRONTO.
