# INTEGRA-NOITE · LOTE 3 — sobre o vivo `dc0de726` (lote 2 + rodada1-comando)

Ramo `integra-noite-v3`, nascido do vivo `278cd489` (lote 2) e junto com o vivo **`dc0de726`**
(`rodada1-comando-v1`, instalado 17:35 — aviso da coordenação). **ff-only sobre `dc0de726`: SIM.** **NÃO instalado.**

## 1 · Os pacotes

| # | pacote | SHA | base | junção |
|---|---|---|---|---|
| 1 | dedup-doc-v1 | 05aa35c7 | 69b0e23f | limpa |
| 2 | lote3-social-v1 | 2babb52d | 69b0e23f | conflito só na ficha do mapa — ⚠️ ver §3 |
| 3 | extratores-v2-juntos | 2cbfb53f | 69b0e23f (+ quatro-chaves, conserto-regua dentro) | `.gitattributes`: ficam as duas linhas `-text` (`tests/dados/c2-juiz/**` e `tests/dados/lugar_v2/**`), bytes de amostras conferidos 12/12; `donos.generated.json` (gerado) |
| — | sala-leitura-v2 | c035495f | — | **FORA**: não está PRONTO (registo das 13:41; o `SALA-LEITURA.md` §6 diz testes COM BANCO não corridos) |
| — | lugar-do-publicador-v1 | 140f161a | — | **FORA**: não está PRONTO e não está no GitHub (só nesta máquina) |

Migrações: a **036** (dedup-doc) está no ramo como ficheiro, mas **NÃO entra no lote 3** (DA-20 3: vai pela
MIGRACOES-EM-SERIE, DA-19) — ver §5 e o plano. A `034_o_acervo_guarda_tempo_e_lugar…` do extratores é o MESMO blob
(`407e7c6c`) que já está no vivo desde o lote 1. A 037 do lote3-social está em `supabase/propostas/` (não é migração).

## 2 · Testes por NOME contra o vivo (mesmos dados, rede fechada, pastas com o nome do vivo)

**Contra o vivo `dc0de726` (final)** — `provas/integra_noite/lote3-{ramo,vivo}-v3.json` (sha256 `f058c95b…` /
`b4ca7941…`): 85 módulos (o `test_quatro_chaves_na_sala` passou para a fase pesada); **1.198** no ramo, **1.014** no
vivo; **0 novas**; as mesmas **98 herdadas**; `test_rodadas` 38/38 nos dois lados.

Contra o vivo `278cd489` (antes do aviso das 17:35):

**Depois da DA-20** — `provas/integra_noite/lote3-{ramo,vivo}-v2.json` (sha256 `f67843d9…` / `3723eb83…`):
86 módulos; **1.211** testes no ramo, **1.027** no vivo; **0 novas**; **98 herdadas**, iguais nome a nome
(`italy_contract_test` 77 · `test_tempo_e_lugar_da_publicacao` 12 · `test_forward_instrumentado` 5 ·
`test_collection_gate` 1 · `test_scrap_rc01_release_candidate` 1 · `test_a_primeira_corrida_da_inteligencia` 1 ·
`test_lingua_da_porta` 1). `test_quatro_chaves_na_sala` 22/22 (com a parte de banco), `test_periodo_e_chaves` 25/25,
`test_sala_por_nome` 11/11.

A 1.ª corrida (antes da DA-20, `lote3-*-v1.json`) deu **5 novas** — as de §4.

⚠️ Erros meus declarados: (1) ao investigar, corri `tests.test_quatro_chaves_na_sala` (liga um Postgres
descartável) **fora** da LOCK-PESADO (~2 min, 14:25); (2) a bateria por nome trazia esse teste desde o lote 2 e
correu-o também fora da trava (14:05 e 16:40). Passou para a fase pesada (§6).

## 3 · ⚠️ Erro meu achado e consertado: a ficha do mapa perdia-se na junção

O meu `juntar.sh` tratava tudo em `system-map/` como gerado e, no conflito, ficava com o lado do ramo. Mas
`system-map/data/architecture.declared.json` é a ficha escrita à mão. Perderam-se as fichas de:
- **LOTE 2, já instalado:** `bloqueadas-v1` 889b2166 (peça `C-BLOQUEADAS-268`) e `destravar-v1` a935a191
  (`C-BLOQUEADAS-DESTRAVAR`, `C-MICRO-PROVA-LOTE1`). O **código** deles está no vivo e inteiro; faltam só as peças
  no mapa (os ficheiros são de `curadoria/`, que a P9 não conta — por isso o validador do lote 2 passou).
- **LOTE 3:** `lote3-social-v1` 2babb52d (`C-CANAIS-41` + 9 ficheiros em peças existentes).

Reposto no ramo (`9c67b95b`) pelo que cada pacote ACRESCENTOU à sua base (só acréscimos; nenhuma remoção, nenhum
campo em conflito). Código novo que nenhum pacote declarou: `leis/boletim_do_campo.py` → C-LUGAR-COLETA ·
`coleta/extratores_de_texto.py` → C-EXECUTOR-TEXTO-HTML · `admissao/versao_do_documento.py` → C-SALA-DE-ESPERA ·
`provas/migracao_036_ensaio_copia.py` → C-PROVA-COLETA. O `juntar.sh` passou a tratar a ficha como código (script
fora do Git, sha256 `a96b1d06…`; o de reposição `20a768e3…`). **Instalar o lote 3 repõe as peças do lote 2 no mapa
do vivo.**

## 4 · As decisões DA-20 (coordenação 16:40) — aplicadas

**1 · O período só sai de data COM prova (opção B).** `admissao.periodo_do_fato` (código do extratores-v2,
PERIODO-E-CHAVES): um `FACT_TIME` sem `fact_time_basis`, ou com uma base que diz que não sabe («UNKNOWN»,
«NOT_KNOWN», «NAO SEI»), dá período **NAO SEI** — o mesmo critério do G0/v2 da Intelligence (`base_ignorante`).
O que estava escrito fica em `EXPRESSAO`. Testes: `DA20_SemProvaNaoHaPeriodo` (3, com contraprova) em
`tests/test_periodo_e_chaves.py`; os 3 do `test_quatro_chaves_na_sala` voltaram a passar **sem mudar**.
(Medido antes: o `extratores-v2-juntos` **sozinho** `2cbfb53f` já falhava — não era da junção.)

**2 · `test_sala_por_nome`** — o `pousar` do dedup-doc pergunta primeiro ao banco se a 036 existe
(`_consultar`). Código do dedup intacto.
- DA-20 (16:40): o teste leve responde «não» (fica, corre em qualquer máquina).
- **D90 (bot Luciano, 19:50): não basta responder** — `AEscritaEPeloNomeNoLivroDeMigracoesReal` herda os 2 testes
  (`test_cada_valor_vai_para_a_sua_coluna`, `test_as_tres_listas_de_colunas_sao_a_mesma`) e corre-os num
  **Postgres descartável montado pela cadeia canónica a partir de uma árvore com todas as migrations do ramo menos a
  036**: a pergunta «a 036 existe?» é respondida pelo BANCO. Mais 3 testes: o `schema_migracao` real não tem a 036
  (e tem a 033; a tabela de versões não existe) · o banco responde que não e o `pousar` não toca na tabela ·
  **`pousar` de ponta a ponta sem nada substituído** (bruto real em `raw_asset`, READY da porta) grava 1 linha e diz
  `036 nao aplicada`. `test_sala_por_nome` passou para a fase pesada (liga Postgres).

**3 · A 036 não entra; o lote 3 funciona sem ela.** O `pousar` sem o caderno de versões pousa como antes e diz no
relato `036 nao aplicada`. Testes: `SemA036OPousarContinuaAPousar` (2, com contraprova) em
`tests/test_sala_por_nome.py`. Na fase pesada (§6) os testes da Sala correm também numa cópia **sem o ficheiro 036**.
O ficheiro da 036 **fica no ramo** (é do pacote; a série é da DA-19) — por isso a instalação **não corre a cadeia de
migrações** (plano, A).

**Mutação** (`provas/integra_noite/mutacao_da20.py` → `mutacao-da20-RESULTADO.txt`): **6 mutantes, 6 mortos** —
P1 a trava do período desligada · P2 «UNKNOWN» passa por prova · P3 «NAO SEI»/falta de base passa · P4 sem a 036 o
`pousar` rebenta · P5 o `pousar` não pergunta pela 036 · **P6 o mesmo, apanhado pelo livro de migrações REAL** (D90,
com Postgres, sob a LOCK-PESADO). Ficheiros repostos (sha256). Na 1.ª volta um mutante
**sobreviveu**: a condição tinha uma 2.ª metade redundante (a falta de base já chega como «NAO SEI», que a busca
apanha) — saiu do código (`fd40775c`), não se inventou teste para ela.

## 5 · O rodada1-comando-v1 — junto (vivo `dc0de726`)

Junto por `merge` (não `rebase`: a história dos pacotes fica como está e o ramo contém o vivo → ff-only).
Nenhum ficheiro em comum com o lote 3 (só as rodadas). Conflito **só na ficha do mapa**: os dois lados acrescentaram
ao fim da lista de C-ONDA-WEB; aplicado o único acréscimo do rodada1-comando (`ensaio_rodada.py`), medido contra a
base `278cd489` — nenhuma remoção nem campo mudado.

## 6 · Fase pesada (LOCK-PESADO) e mapa

Sob a LOCK-PESADO (20:00), 10,2 GB livres. `C:/cur/t2b/pesado_l3.sh`: `test_sala_idempotente_por_documento`,
`test_sala_dedup_por_document_key`, `test_quatro_chaves_na_sala`, `test_sala_por_nome` em três cópias
(`provas/integra_noite/lote3-pesado-{ramo,vivo,sem036}.txt`, sha256 `f4ecb5cd…` / `7af453cd…` / `9613bb64…`):

| cópia | resultado |
|---|---|
| **ramo** | **60/60 OK** |
| vivo `dc0de726` | 37 corridos; `test_sala_dedup_por_document_key` não existe lá (vem com o dedup-doc) — o resto OK |
| **ramo SEM o ficheiro da 036** | **52/60**: falham **só** os 7 testes de versões (`test_V1`…`test_V7`, precisam da tabela da 036) e `test_o_livro_de_migracoes_real_nao_tem_a_036` (confere que ELE tirou a 036 da árvore — nesta cópia ela já não estava). Passam sem a 036: dedup A/B/C/C2/U1/U3/L/R, idempotência 5/5, quatro-chaves na Sala 22/22, escrita por nome 15/15 (incluindo o `pousar` ponta a ponta) |

Mapa único: ver o commit do mapa (é o SHA do PRONTO).

## 7 · Plano único de instalação (o coordenador instala; um escritor; sem rede)

**A · Código (tudo de uma vez, ff-only, robô PARADO):**
1. `curadoria/PARAR.flag`; esperar a volta acabar. Guardar `git rev-parse HEAD` (= `dc0de726`), `git status` e
   `sha256sum` dos livros `M` (**17** às 17:40, só leitura; 18 na instalação do lote 2 — contar na hora).
2. `git merge --ff-only <SHA do PRONTO>`.
3. Os livros: `git status` e sha256 IGUAIS ao passo 1. Medido às 17:40: o writeset (`dc0de726`..ramo) não toca
   nenhum dos 17; nenhum ficheiro do writeset está solto ou `M` no vivo; em `data/` só entram **49 provas NOVAS**
   (`data/derivados/EXTRATORES-V2-JUNTOS|EXTRATOR-EVENTO-V2|PERIODO-E-CHAVES`), nenhuma mudada.
4. `correr_a_cadeia.py VALIDAR` (o P1 acusa os livros `M`: aceitar SÓ se a lista for exatamente essa) e
   `PORTOES_POS_COMMIT` → IGUAL. Repor os gerados que o validador reescreve pelo nome.
5. **NÃO correr `motor/cadeia_canonica.sh migrations`** — aplicaria a 034 antiga e a 036 (DA-19/DA-20 3).
6. Provas rápidas sem rede: `py -m unittest tests.test_periodo_e_chaves
   tests.test_quatro_chaves tests.test_freio_social tests.test_maestro_social tests.test_extrator_evento_v2
   tests.test_extrator_lugar_v2 tests.test_a_receita_tem_versao tests.test_quem_pousa_entrega_o_armazem
   tests.test_sala_por_nome.AEscritaEPeloNome tests.test_sala_por_nome.SemA036OPousarContinuaAPousar` (só as
   classes leves: o resto do `test_sala_por_nome` liga um Postgres descartável).
7. Reiniciar o supervisor (mudam `orquestrador/orquestrador.py`, `coleta/`, `admissao/`); tirar o `PARAR.flag`.

**O que muda sozinho depois de A** (nada reescreve linhas antigas da Sala):
- **dedup:** o `pousar` não cria 2.ª linha para o mesmo documento (`source_id` + `document_key`,
  `FORWARD_IDENTIFIED`, mesmo universo). As 14 repetições antigas ficam.
- **extrator HTML versão «2»:** revisitar uma página já derivada em «1» gera um derivado NOVO (mais linhas em
  `derived_artifact` e ficheiros `texto-de-html-2-*` no armazém) — declarado pelo dedup-doc.
- **extratores:** cultura/praga/fase dos boletins e o período (só com prova) para o que for admitido daqui em diante.
- **freio social** (teto D38 no pedido, dedup pelo vídeo): vale para a próxima corrida social. O maestro só corre
  quando chamado.

**B · O que ESCREVE nos cadernos ou na Sala — só com o robô PARADO, cada passo é decisão do coordenador:**
1. **Os 9 canais YouTube presos** (lote3-social §3 passo 2 = o **mesmo** passo B1 do lote 2): **só se o B1 do lote 2
   ainda não foi feito.** `py curadoria/importar_do_coletor.py` (conferir os 9 `PRESO_NO_FEED`) →
   `--pelo-scrap --ids=IT-T5-042,IT-T5-043,IT-T5-044,IT-T5-045,IT-T5-047,IT-T5-048,IT-T5-050,IT-T7-016,IT-T7-018`.
   Tirar o `PARAR.flag` uma volta (9 `VALIDATE_ROUTE`, param em `CANARY_PENDING`, sem rede).
2. **Reprocesso da Sala — UM só, com tudo junto** (a régua consertada do lote 2 + os extratores + a DA-20): se o B3/B4
   do lote 2 ainda não correram, fazê-los **aqui**, uma vez. `admissao/reprocessar_tempo_lugar.py` sem escrever →
   `--aplicar` → 2.ª vez `INSERIDAS: 0`. Grava revisões novas (a Sala só acrescenta). Na cópia (EXTRATORES-V2 §5,
   antes da DA-20): cultura/região/fase/período 0/0/0/0 → 19/18/6/20; o IT-T5-186 (ENEA, «Brindisi ; Roma») perde o
   lugar pela regra da CONSERTO-REGUA. ⚠️ Com a DA-20 o período de itens sem base fica NAO SEI — o 20 da cópia
   pode baixar (não medido).
3. **036** — fora do lote 3 (MIGRACOES-EM-SERIE, DA-19).
4. **037** (lote3-social) — só proposta, em `supabase/propostas/`.
5. **A 1.ª coleta social real** — missão própria, VPN IT, rede autorizada, **`SINTONIA_ASR_DEVICE=GPU`** no ambiente
   (sem ela o transcritor usa o processador) — `LOTE3-SOCIAL.md` §4.

**⚠️ Red team da ponte:** nunca na pasta viva.

**Desfazer (código):** `PARAR.flag`; guardar `git status`/`git diff`; `git reset --keep dc0de726`;
reiniciar o supervisor.
