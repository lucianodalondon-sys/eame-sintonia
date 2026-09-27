# LOTE7-INTEGRA — pacote único para instalar no vivo hoje (D114)

```text
RAMO      claude/lote7-integra-grain-rule-37g8vv
BASE      c551062  (= origin/claude/single-reference-gateway-hhhj7t = lote6 671dm9 + porta única; contém a produção 18461b92d)
PRODUÇÃO  18461b92d (servico-20260923-0923) — ancestral deste ramo: a instalação é FAST-FORWARD
REDE      nenhuma. Nada colhido. Livros vivos (curadoria/*-V1.json, data/collection-ledger, candidatas/FONTES-CANDIDATAS.json) não tocados.
SHA FINAL a cabeça de origin/claude/lote7-integra-grain-rule-37g8vv (o commit que contém este ficheiro não pode conhecer o
          próprio SHA; o relatório da sessão di-lo). Código medido: d0e0901
```

## 1 · Os merges (declarados, nenhuma história reescrita)

| # | ramo | cabeça | commit do merge | o que trouxe |
|---|---|---|---|---|
| 1 | `claude/pote-v2-unico-contract-y8o1pi` | `8982ce4` | `dfcd221` | contrato único `POTE_INTELLIGENCE_CASCO/v2` (doc + schema + `pacote/validar_pote_v2.py`), P7/P8, casco P8–P11, 38 testes |
| 2 | `claude/lote5-integra-merge-3320ja` | `7bf6360` | `657f1a8` | comentários-v1 (D106), linha-busca (D93, RAW canónico), busca-no-actions. Base comum = 18461b92d, logo só entrou o que faltava |
| 3 | `claude/cruzamentos-max-sguy1x` | `399e79f` | — | **já estava** na base (0 commits à frente; merge `dbe0cd3` da porta única). Conferido: `motor/cruzamentos_max.py` lê **só pela porta** (`Referencia.da_porta`, `:360-399`; `import porta_da_referencia as PORTA`, `:65`) — nenhum `open` de `IT-ROTULOS-PARES` nem do CSV |
| 4 | `claude/reference-maintenance-collection-8s2lwy` | `7925149` | `5e3c104` | cadência D117 no contrato IT-T4-001 (`regras/cadencia_da_referencia.mjs`), comparador de edições → `EVENTO_REGULATORIO` (`coleta/it/edicoes_do_registro.py`), régua de frescor (`leis/frescor_da_referencia.py`) |

- **DATASET_OFICIAL não entrou.** O ramo 4 só a **cita** como saída possível (`COMANDO-HOJE.md`), não a implementa.
  `git ls-remote`: `nuvem/porteiro-dataset-oficial-v1` aponta para **o mesmo** `7925149` do ramo 4 — a missão do
  porteiro ainda não entregou nada próprio. Nada mais a integrar.
- **Não integrados, por ordem:** rete-voci-dati (D115, só entrada da Intelligence) e casco-r7 (outra missão).

## 2 · Conflitos — cada um resolvido e explicado

| merge | conflitos | resolução |
|---|---|---|
| 1 pote-v2 | 14, **todos gerados** (`system-map/data/*.generated.json`, `italia-portale/client/system-map/state.generated.json`, `docs/fontes/INDICE-DE-FONTES.md`, `docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`) | lado do HEAD e **REGERADOS** pela cadeia no fim (gerado não se edita à mão) |
| 2 lote5 | 15 gerados + `architecture.declared.json` | gerados: idem. Declarado: as duas linhas acrescentaram ficheiros ao **fim da mesma lista** de provas → **união** (7 do lote6 + `mutacao_lote5_integra.py`) |
| 4 ref-manutenção | 15 gerados + `architecture.declared.json` | gerados: idem. Declarado: as duas linhas acrescentaram **peças novas** ao fim de `COMPONENTS` (4 da linha-busca × 4 da referência-manutenção) → **união**; 277 ids, 277 únicos |

Linhas apagadas conferidas (`git diff --numstat … | awk '$2>0'`) em cada merge: só as mudanças que o próprio ramo
fez. Nenhum teste apagado. Os ajustes de teste que entraram são os **declarados pelos ramos**:
`test_pote_intelligence_casco.py` (PUBLICADO_EM → PUBLISHED_AT, contrato v2), `test_c14c`/`test_d24` (D106).

### A junção que só aparece com os ramos juntos

`tests/test_porta_unica_referencia.py::test_A1` reprovou depois do merge 4: `coleta/it/edicoes_do_registro.py`
(nascido no ramo 4, sem ver a varredura da porta) nomeia `PROD_FTS` em código (`:97` regex do nome da edição;
`:380` texto de proveniência). É **produtor** — compara edições **brutas** do CSV do Ministero e emite
`EVENTO_REGULATORIO`; não abre `referencia/adama`. Entrou nas `EXCECOES` como `PRODUTOR`, ao lado de
`rotulos_ler.py`, com **AJUSTE DECLARADO** no teste (`tests/test_porta_unica_referencia.py:68-72`). A varredura
continua a reprovar qualquer outro ficheiro novo.

## 3 · Regra de GRÃO na porta (achado do LAB, PESQUISA-CRUZAMENTOS F.2-1)

A porta devolvia `AUTORIZADO_NA_BULA_LIDA` para qualquer uso lido, fosse qual fosse o `LINK_LEVEL`. O
cruzamentos-max já separava (`NIVEIS_FORTES`), mas **só ele**: CAP-WIN, boletim, concorrência e CAP-SCI recebiam SIM
de declaração de produto.

| o quê | onde |
|---|---|
| `NIVEIS_QUE_AUTORIZAM = (LINHA_DA_TABELA, BLOCO_DA_CULTURA)` | `motor/porta_da_referencia.py:101` |
| `autorizacao_do_uso(uso, frescor)` — **a regra única**: D117 por cima; nível fora do conjunto (DECLARACAO_DE_PRODUTO, ausente, NÃO SEI) = `A_CONFIRMAR` com o porquê | `motor/porta_da_referencia.py:288` |
| `autorizados`: cada produto com o seu estado; ESTADO geral só é SIM se houver uso de grão forte | `:315`, `:350`, `:365` |
| `por_alvo`: `CULTURAS_NA_BULA` só de grão forte; as outras em `CULTURAS_SO_DECLARADAS`; registo nasce `A_CONFIRMAR` | `:424`, `:447` |
| CAP-SCI **herda** (deixou de montar o seu SIM): pede `PORTA.autorizacao_do_uso` a cada uso | `motor/capacidade_cientifica.py:683-684` |
| cruzamentos-max **herda** (deixou de ter lista própria): `NIVEIS_FORTES = PORTA.NIVEIS_QUE_AUTORIZAM` | `motor/cruzamentos_max.py:209` |
| CAP-WIN, boletim, concorrência Meta | já perguntavam à porta — herdam sem mudar código |

**Testes** — `tests/test_porta_unica_referencia.py` classe `I_Grao` (`:484`, 6 testes): I1 a regra; I2 varre as
341 perguntas cultura × alvo da edição (nenhum SIM de declaração, e todo SIM tem grão forte); I3 par só de
declaração sai `A_CONFIRMAR` com o porquê; I4 com todos os usos declaração, **os cinco consumidores** (porta,
CAP-WIN, boletim, por_alvo, CAP-SCI) saem `A_CONFIRMAR`; I5 `por_alvo` e as culturas; I6 a regra mora só na porta
(identidade de `NIVEIS_FORTES` e nenhum religado com os literais).

**Medida** — `provas/lote7_integra/medir_grao_na_porta.py` → `MEDIDA-GRAO-NA-PORTA.json`. ANTES = a porta de
`c551062` **lida do git** (não simulada); DEPOIS = esta; HOJE 2026-09-27; mesmos livros (impressão igual).

```text
2030 USOS          por LINK_LEVEL: LINHA_DA_TABELA 886 · BLOCO_DA_CULTURA 626 · DECLARACAO_DE_PRODUTO 518
                   ANTES 2030 SIM  ->  DEPOIS 1512 SIM + 518 A_CONFIRMAR       518 SIM caem (todos DECLARACAO)
341 PERGUNTAS      cultura x alvo: ANTES 341 SIM -> DEPOIS 220 SIM + 121 A_CONFIRMAR   (ex.: BARBABIETOLA x ALOPECURUS)
R7 · 86 REFEITOS   0 mudancas (48 PARTIAL · 22 UNRESOLVED · 7 NO · 5 YES_A_CONFIRMAR · 4 NOT_POSSIBLE, iguais)
R7 · 14 PORTFOLIO  0 mudancas (13 SEM_PAR_LIDO · 1 NAO_SEI); pela porta os 14 sao NAO SEI antes e depois
```

Os 86 refeitos perguntam **substância × cultura** (sem alvo): a declaração de produto prova a cultura, e a regra
(que é sobre cultura × alvo) não os toca. O portfólio da R7 já usava os níveis fortes; agora lê-os da porta.
`docs/intelligence/r7/CRUZAMENTOS-MAX.json` **não foi regerado** (estados iguais; só mudaria `LIDO_SOBRE_A_ARVORE`).

## 4 · Bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `c551062` (porta única = lote6 + porta) | 314 | 7030 | 131 |
| lote7 (código `d0e0901`, mapa regerado) | 320 | 7190 | 131 |

- **Novas: 0. Sumidas: 0.** As 131 são as herdadas da base, pelo nome (maiores: `test_atomicidade_da_intelligence` 8,
  `test_c10_6_crash_retry` 7, `test_c13_executor_wiring` 7, `test_a_sala_de_espera_tem_um_dono` 6,
  `test_audio_youtube_wiring` 6, `test_c10_5d_decisao_instagram` 6, `test_pacote_de_revisao_t3` 6; lista inteira no JSON).
- 6 módulos novos, **0 falhas**: `test_pote_v2_unico` 38 · `test_comentarios_v1` 32 · `test_busca_no_actions` 30 ·
  `test_linha_busca` 23 · `test_edicoes_do_registro` 20 · `test_frescor_da_referencia` 11. `test_porta_unica_referencia`
  37 → 43 (+6 do grão).
- Fora da bateria Python: `node regras/cadencia_da_referencia_test.mjs` → 35 passaram, 0 falharam.
- ⚠️ Medida intermédia, dita: sobre `5a35c40` (antes de regerar o mapa) houve **1 nova**,
  `test_o_controle_separa_lei_de_mencao.test_M5_o_ponto_fixo…` — o carimbo do mapa não batia com a árvore porque os
  gerados dos merges ainda eram os do HEAD. Depois do REGERAR (`d0e0901`) ela passa; é o próprio M5 a provar que
  a regra de regerar funciona.
- JSON: `provas/lote7_integra/BATERIA-BASE-c551062.json`, `…/BATERIA-DEPOIS-d0e0901.json`.
- O commit seguinte a `d0e0901` só acrescenta este relatório, os JSON/TXT de prova e o mapa regerado (código igual).

## 5 · Mutação — as peças integradas continuam a morder

Cada suíte na versão desta árvore (código de `d0e0901`; entre `5a35c40` e `d0e0901` só mudou o ficheiro de
mutantes do cruzamentos-max). Log inteiro: `provas/lote7_integra/MUTACAO-LOTE7.txt`. **196 MORTOS, 0 VIVOS, 0 NÃO APLICADOS.**

| peça | suíte | resultado |
|---|---|---|
| **porta + regra de grão** | `provas/porta_unica_referencia/mutantes.py` | **29/29** (20 antigos + **G1–G9** do grão: declaração nos níveis, nível ignorado, nível ausente, qualquer uso vira SIM, `por_alvo` sem grão ×2, frescor fora da regra, CAP-SCI com SIM próprio, cruzamentos-max com lista própria). F5 **reancorado, declarado** (a CAP-SCI pede a regra à porta; mesmo defeito) |
| cruzamentos-max | `provas/_mutantes_cruzamentos_max.py` | **31/31**. P1 **reancorado, declarado**: a âncora era a linha `NIVEIS_FORTES = (...)`, que agora vem da porta; o defeito plantado é o mesmo (declaração conta como par forte) e morre em `test_E2_so_espectro_de_produto_nao_soma` |
| pote v2 único | `provas/pote_v2/mutantes_pote_v2_unico.py` | **25/25** |
| pote no casco | `provas/_mutantes_pote_casco.py` | **29/29** |
| referência-manutenção | `provas/mutacao_referencia_manutencao.py` (worktree limpa) | **16/16** |
| lote5 · junções | `provas/integra_noite/mutacao_lote5_integra.py d0e0901` (Postgres 16 descartável) | **10/10** (`MUTACAO-JUNCOES-LOTE5-d0e0901.txt`) |
| lote5 · busca no Actions | `provas/busca_no_actions/mutantes_busca_actions.py` | **17/17** |
| lote5 · comentários-v1 | `provas/comentarios_v1/mutar.py` | **14/14** |
| lote5 · comentários-regras | `provas/comentarios_bateria/mutar_regras.py` | **23/23** |

## 6 · System Map

`python3 system-map/scripts/correr_a_cadeia.py REGERAR` (depois do `git add`) · `VALIDAR` =
**SYSTEM_MAP_CHECK=PASS** · `impressao_da_arvore.py --conferir-carimbo` = **IGUAL** (conferido depois do último
commit). Os 15 gerados em conflito nos merges foram todos refeitos pela cadeia. Peças declaradas atualizadas:
`C-INT-PORTA-REFERENCIA` (a regra de grão), `C-PROVA-PORTA-REFERENCIA` (29 mutantes + `provas/lote7_integra/*`);
`LOTE7-INTEGRA.md` na lista dos relatórios. Sem `--stamp`.

## 7 · CHECKLIST DE INSTALAÇÃO NO VIVO (coordenador — **não instalado por esta sessão**)

```bash
VIVA=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1   # bot, servico-20260923-0923
C=/c/inst/$(date +%Y%m%d-%H%M)-lote7; mkdir -p $C/livros
FINAL=$(git -C $VIVA fetch -q origin && git -C $VIVA rev-parse origin/claude/lote7-integra-grain-rule-37g8vv); echo $FINAL
```

| # | passo | comando / critério | 🛑 pára se |
|---|---|---|---|
| 0 | **Medir** | `git -C $VIVA rev-parse HEAD` = `18461b92dcf576816e45af27586d2d7f783d0a07`; `git -C $VIVA merge-base --is-ancestor HEAD $FINAL` sai 0; `$FINAL` = o SHA final deste relatório. Um só supervisor, worker IDLE (`py curadoria/supervisor.py --estado`) | HEAD diferente (a produção andou: refazer o ensaio) · não é ancestral |
| 1 | **Robô parado** | `PARAR.flag` com marca própria; esperar o supervisor sair; parar o observador da ponte. A tarefa `SINTONIA-Arranque` não toca flag alheio | supervisor não sai |
| 2 | **Backup** | foto dos livros sujos: `(cd $VIVA && git status --short \| awk '{print $2}' \| while read f; do find "$f" -type f; done) > $C/lista`; `while read f; do mkdir -p $C/livros/$(dirname "$f"); cp "$VIVA/$f" "$C/livros/$f"; done < $C/lista`; `(cd $C && find livros -type f \| xargs sha256sum) > $C/foto.sha`. E a Sala: `backup_sala.cmd` | cópia falha |
| 3 | **Tocam livro vivo?** | `git -C $VIVA diff --name-only HEAD $FINAL -- $(cat $C/lista)` **vazio** (este lote não traz nenhum livro vivo: medido, 0 de `curadoria/*-V1.json`, `data/collection-ledger`, `candidatas/FONTES-CANDIDATAS.json`) | sai algum nome |
| 4 | **Fast-forward** | `git -C $VIVA merge --ff-only $FINAL` (de 18461b92d até ao SHA final; sem merge, sem conflito) | recusa o ff |
| 5 | **Livros vivos iguais** | `(cd $C && sha256sum -c foto.sha)` com os ficheiros do vivo no lugar (ou `cmp` um a um): tudo `OK` | algum MUDOU → DESFAZER |
| 6 | **Testes pós-instalação** (rede fechada) | `py -m unittest tests.test_porta_unica_referencia tests.test_cruzamentos_max tests.test_capacidade_cientifica tests.test_cap_win tests.test_pote_v2_unico tests.test_pote_intelligence_casco tests.test_edicoes_do_registro tests.test_frescor_da_referencia tests.test_linha_busca tests.test_busca_no_actions` → OK; `node regras/cadencia_da_referencia_test.mjs` → OK; `py motor/porta_da_referencia.py --hoje AAAA-MM-DD` → `ESTADO LIDA`, edição `PROD_FTS_6_20260831`. Opcional: bateria inteira por nome contra `provas/lote7_integra/BATERIA-DEPOIS-*.json` — 0 novas | falha nova → DESFAZER |
| 7 | **Mapa** | `py system-map/scripts/impressao_da_arvore.py --conferir-carimbo` = `IGUAL` | DIFERENTE |
| 8 | **Supervisor religado** | tirar o flag; `Stop-ScheduledTask SINTONIA-Arranque; Start-ScheduledTask SINTONIA-Arranque` (liga observador e supervisor); `py curadoria/supervisor.py --estado` → RUNNING/IDLE, um só | não volta |
| 9 | **Publicar** | push de `servico-20260923-0923` (agora = `$FINAL`) | — |

**↩️ DESFAZER** — `PARAR.flag`; `git -C $VIVA reset -q --keep 18461b92d`; conferir a foto (`sha256sum -c`);
relançar como no passo 8.

⚠️ **O que a instalação muda no comportamento vivo:** (a) 518 usos (121 perguntas cultura × alvo) passam de SIM a
`A_CONFIRMAR` em todo consumidor da porta; (b) a partir de **2026-10-07** a edição de 31/08 passa a
`AUTORIZACAO_A_CONFIRMAR` (D117, 30 dias sem checagem) se ninguém conferir uma edição nova; (c) a coleta de
IT-T4-001 continua `BLOQUEADA_PELO_CURATOR` até decisão do dono (DATASET_OFICIAL ou D-número; `COMANDO-HOJE.md`).

## 8 · Limites declarados

- `docs/intelligence/r7/CRUZAMENTOS-MAX.json` e o pote não foram regerados (estados iguais, medido).
- Os 14 pares do portfólio da R7 perguntados **à porta** saem NÃO SEI (o vocabulário do boletim — «mosca dell'olivo» —
  não é o das bulas); o cruzamentos-max usa o seu próprio mapeamento e dá o mesmo resultado de antes.
- `--stamp` do mapa **não** foi corrido: carimbaria como «lidos por gente» ficheiros dos ramos que esta sessão não releu.

## EM PALAVRAS SIMPLES

Juntei numa árvore só as entregas que faltavam (o pote único, os comentários + a busca, a manutenção da referência),
e o cruzamentos-max já estava lá, a ler pela porta. Os conflitos eram quase todos ficheiros que a máquina gera — foram
regerados — e dois pedaços da lista de peças do mapa, que juntei. E pus a regra do grão **na porta**: uma bula só diz
«sim, autoriza» quando escreve a cultura e a praga **na mesma linha ou no mesmo bloco**; se só tem uma lista de culturas
e outra de pragas, a resposta é «a confirmar». Isso tirou o «sim» de 518 dos 2030 usos. Todos os que perguntam à porta
herdam a regra sozinhos. Nada foi instalado: o checklist acima é para o coordenador.
