# RELATÓRIO — INDEPENDÊNCIA DE FONTES (nuvem-independencia-v1)

Missão: `C:/nuvem/prompts/nuvem-independencia-v1.txt` · defeitos **D12** e **D16** da Intelligence
(1.ª rodada real, 26/09). Base da missão: `69b0e23f`; entregue **sobre o vivo `dc0de726`** (rebase sobre `278cd489` às 14:00 e sobre `dc0de726` às 17:55, avisos da coordenação). Rede externa: **nenhuma** (testes com proxy numa porta morta).
D11/D13/D14/D15 **não tocados**.

## O que fiz

Um **grafo de dependência mínimo** (INT-LAW-070..077, métricas separadas da INT-LAW-092), com UM dono,
usado pela corrida da Intelligence e pelo motor de oportunidades V2.1.

Três camadas, que nunca se comprimem:

| camada | regra | métrica |
|---|---|---|
| SINAL | cada entrada que chegou | `EXTERNAL_SIGNAL_COUNT` |
| EVIDÊNCIA | mesmo documento (mesmo SHA-256, `DOCUMENT_ID` ou endereço) = **uma** | `EVIDENCE_BASE_COUNT` |
| FONTE | mesmo originador = **uma** | `INDEPENDENT_SOURCE_COUNT` (+ MIN/MAX quando há NÃO SEI) |

Mais: `DOMINANT_SOURCE` e `DOMINANT_SOURCE_SHARE_PCT` (o «6 de 9 = 66,7 % myfruit.it»),
`STRUCTURAL_VALIDATION_COUNT` (rótulo/registo/catálogo não são fonte, INT-LAW-076) e
`CONVERGENCE` = `CONVERGE` **só** com ≥2 originadores **provados** sobre o **mesmo fato declarado**;
`NAO_CONVERGE` com um só possível; `NAO SEI` quando falta prova.

Quem é o originador, por esta ordem: republicação/origem **declarada** pela Collection → **página** da
plataforma (`PAGE_ID`) → **instituição** quando o endereço é um resolvedor (doi.org, handle.net) →
**domínio registável** (canal, se for plataforma) → `SOURCE_ID`. Unir a mais só esconde independência,
nunca a fabrica. Sem nenhum destes → NÃO SEI (nunca conta como fonte nova).

### Ficheiro:linha

- `motor/grafo_de_dependencia.py` (novo) — `chaves_de_documento` :187 · `chaves_de_originador` :201
  (resolvedores :214, a exceção do SOURCE_ID de plataforma :229) · `grafo` :279 (o mesmo documento une
  a fonte :319, convergência pelo MÍNIMO provado :353, fonte dominante :379) · `por_fato` :391.
- `motor/corrida_da_inteligencia.py` — import :64 · `CAMPOS_PARA_O_GRAFO` :212 · `chave_do_fato` :218
  (só o envelope `FATO`: subject|predicate, fact_id, claim_id; nada inferido) · `dependencia` :236 ·
  `SIGNAL_ID` passa a levar a leitura (antes dois itens com o mesmo `ITEM_ID` davam o MESMO id) ·
  `livro["DEPENDENCIA"]` :353 · `DUPLICATA_DE` marcado no sinal :357. Os sinais **não** são apagados:
  a linhagem guarda cada leitura; as contagens vivem em `DEPENDENCIA`, nunca em `len(SIGNALS)`.
- `motor/v21_oportunidades.py` — `TIPOS_ESTRUTURAIS` :244 · `dependencia` :248 · teto de
  `MULTI_SOURCE` pelas fontes independentes provadas :748 (o valor do arquétipo fica em
  `MULTI_SOURCE_DECLARED`, INT-LAW-093) · fusão de cartões leva os apoios fundidos ao grafo :1034 ·
  `DEPENDENCY_GRAPH` no registo gravado :1094.
- `system-map/data/architecture.declared.json` — peça `C-INT-GRAFO-DEPENDENCIA` ao lado de `C-INT-CORRIDA`.
- Provas: `provas/independencia/` (`testes_por_nome.py`, `mutantes.py`, `antes_e_depois_v21.py`,
  `base-69b0e23f.json`, `depois.json`, `MUTANTES.json`, `V21-ANTES-E-DEPOIS.json`).
- Teste: `tests/test_independencia_de_fontes.py` — 35 testes.

## O que o dado real mostrou (pacote V2.1, ZIP versionado, só leitura)

Motor antes (`69b0e23f`) × depois, mesmas 43 oportunidades, mesmos IDs:

- **10 de 43** tinham `MULTI_SOURCE = 2` sustentado por **uma** fonte → passaram a 1 (score −1).
  - **7** (O5, preparação regulatória): todos os apoios saem do **mesmo documento** da EUR-Lex
    (o consolidado do Reg. 540/2011). Num deles, **39 sinais = 1 documento**. É o D12 no dado real.
  - **3** (O4, concorrência): todos os anúncios são da **mesma página** (Bayer Crop Science Italia).
- Estado da oportunidade (confirmada/candidata): **0 mudaram**. Confiança (ALTA/MÉDIA/BAIXA): **0 mudaram**.
- 8 de 43 têm mais sinais que documentos (o D12 medido).
- Convergência: 10 CONVERGE · 33 NAO_CONVERGE · 0 NÃO SEI.

### Dois erros meus, apanhados no dado real e corrigidos

1. A primeira versão fundia **todos os anúncios** do Facebook numa fonte (o registo chama a biblioteca
   `SRC_FACEBOOK_COM`). Quem fala é o anunciante: passou a valer `PAGE_ID`, e o `SOURCE_ID` deixou de
   unir quando quem fala já está dito. (Mutantes M12, M14d.)
2. **doi.org** aparecia como «fonte» (86 de 88 registos científicos). doi.org é o balcão, não o autor:
   passou a valer a instituição declarada; sem ela, NÃO SEI. (Mutantes M12b, M12c.)

E um erro de leitura, dito na conversa: afirmei que a coorte real da Sala (14/09) tinha o mesmo
documento duas vezes. **Não tem** — são 6 documentos de 3 publicadores (eu tinha lido os endereços
cortados). O teste diz o que é verdade.

## Testes antes/depois (por NOME)

Corredor: `provas/independencia/testes_por_nome.py` — os 51 módulos de `tests/` que tocam a Intelligence, o
motor V2.1 ou a espinha, mais o novo; rede fechada por proxy numa porta morta; uma falha só é «herdada» se a
base falhar com o **mesmo nome**.

| | árvore | módulos | testes corridos | falhas |
|---|---|---|---|---|
| ANTES | vivo `278cd489` puro | 51 (+1 que não existe lá) | 1354 | 76 |
| DEPOIS | este ramo sobre `278cd489` (`bd76facec`), com a LOCK-PESADO | 52 | 1389 (+35 do teste novo) | 77 |

- **Falhas que sumiram:** 0. **Herdadas:** 76, nome a nome iguais (as maiores: `test_security_ratchet` 23,
  `test_fase_italiana_no_workflow` 15, `test_a_sala_de_espera_tem_um_dono` 7, `test_atomicidade_da_intelligence` 5,
  `test_c2_youtube_oficial` 4 — lista inteira em `provas/independencia/base-278cd489.json`).
- **Nova: 1** — `test_o_controle_separa_lei_de_mencao.test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore`.
  É o `impressao_da_arvore.py --conferir-carimbo`: o ramo medido ainda não tinha o mapa regerado. Fecha-se com
  o commit do mapa (a conferência depois dele está na mensagem desse commit e na entrega).
- Entre `278cd489` e `dc0de726` o vivo só mudou as rodadas da coleta (`ferramentas/big_collection`,
  `tests/test_rodadas.py`) e o mapa; nenhum dos 52 módulos cita esses ficheiros (`git grep`).
- A 1.ª medição, contra `69b0e23f`, fica em `provas/independencia/base-69b0e23f.json` (1353 testes, 80
  falhas). Correu **sem** a LOCK-PESADO (deslize meu) e foi cortada a meio pela queda das abas (~10:20).
- `test_independencia_de_fontes`: **35 testes, 35 passam**, sobre `278cd489` e sobre `dc0de726`.

**Na árvore final** (sobre `dc0de726`, mapa regerado; `provas/independencia/final-dc0de726.json`), os 8
módulos que leem o mapa ou tocam o que mudei: `test_o_controle_separa_lei_de_mencao` 60/0 (o M5 passou),
`test_atomicidade_da_intelligence` 39/5 (as mesmas 5 herdadas), `test_o_mapa_da_intelligence_nao_mente`
36/0, `test_independencia_de_fontes` 35/0, `test_a_primeira_corrida_da_inteligencia` 37/0,
`test_ausencia_na_fronteira_da_corrida` 10/0, `test_corrida_abortada` 1/0, `test_completude_oportunidade`
12/0. **Falhas novas: 0.**

**System Map:** `correr_a_cadeia.py REGERAR` → `CADEIA=OK`; `VALIDAR` → `SYSTEM_MAP_CHECK=PASS` (a 1.ª volta
reprovou P2/P8 por arrumação minha — os scripts de prova estavam na peça de `motor/` e o teste era reclamado
por duas peças; ficaram em `C-PROVA-INDEPENDENCIA`, zona `Z-PROVA`); `impressao_da_arvore.py
--conferir-carimbo` → `IGUAL`. Efeito lateral declarado: `docs/fontes/INDICE-DE-FONTES.md` passou de 729 para
750 «endereços que o código chama» — os +21 são URLs sintéticas do meu teste (o `scan_sources.py` conta todo
`https://` em `.py`, testes incluídos, como já fazia com os testes das outras equipas).

## Mutação

`provas/independencia/mutantes.py` planta **um** defeito de cada vez e restaura os bytes (sem
`git checkout`). **22 plantados, 22 mortos.** Quatro testes nasceram de mutantes que sobreviviam
(M14, M14b, M14c, M14d: a corrida esquecia SHA, endereço declarado, republicação ou página, e
ninguém reclamava). Lista em `provas/independencia/MUTANTES.json`.

## O que NÃO fiz, e o que fica NÃO SEI

- **Sindicação por texto parecido** não é detetada (INT-LAW-081: semelhança não prova equivalência).
  Cópia com bytes diferentes em outro domínio só é apanhada se a Collection declarar a origem.
  Por isso a base chama-se `ORIGINADOR_DISTINTO`, e não «independência provada».
- Os **6 de 9 sinais de myfruit.it** da rodada de 26/09 **não estão** nesta árvore (a Sala real não
  existe na nuvem). O caso é reproduzido em teste **sintético marcado** com a mesma forma.
- O ZIP publicado do V2.1 **não foi reconstruído**: o código mudou, o pacote servido não.
- Compatibilidade de tempo/geografia (resto da INT-LAW-077) **não** foi implementada aqui: a
  convergência só exige mesmo fato declarado + independência.
- **pytest não está instalado** nesta máquina (`No module named pytest`). 4 módulos do motor V2.1 são
  funções soltas `test_*`: o `unittest` corria 0 deles. O corredor desta missão chama-as uma a uma
  (declarado no próprio script). Não instalei nada.
- A LOCK-PESADO só chegou às 17:08, depois de ~6 h na fila (sessões vivas à frente, nenhuma órfã).
- O G0/v2 da outra equipa (INT-CONSERTOS-EXP, D1–D8) entrou no vivo durante a missão; os itens
  sintéticos do meu teste passaram a trazer base da data e dia da captura para serem itens válidos.
  Nenhum teste deles foi alterado.

## SHA final

O commit do mapa regerado pela cadeia, último do ramo `nuvem-independencia-v1` (o SHA sai na entrega:
um ficheiro não pode conter o SHA do commit que o contém). Pontos de volta: `independencia-v1-antes-do-rebase`
(sobre `69b0e23f`) e `independencia-v1-antes-do-rebase-2` (sobre `278cd489`), só locais.

## EM PALAVRAS SIMPLES

Imagina nove pessoas contando a mesma notícia. Se seis delas leram o **mesmo jornal**, não são nove
testemunhas: são quatro. O robô de inteligência contava nove.

Agora ele faz três contas separadas: quantos **recados** chegaram, quantos **papéis diferentes** há
(o mesmo papel lido duas vezes conta uma vez), e quantas **bocas diferentes** falaram (o mesmo
jornal, o mesmo site, a mesma página de anunciante, conta uma vez). E diz quanto pesa a boca que mais
falou — «66,7 % disto veio do mesmo sítio».

Só chama de «várias fontes concordando» quando há pelo menos **duas bocas diferentes, provadas**,
falando da **mesma coisa**. Quando não dá para saber quem falou, ele diz **NÃO SEI** em vez de
chutar.

No pacote real da Itália, isto achou 10 oportunidades (de 43) que se diziam «várias fontes» e eram
uma só — sete delas eram o mesmo documento europeu citado até 39 vezes. A nota delas desceu um
ponto. Nenhuma mudou de «confirmada» para «a validar».
