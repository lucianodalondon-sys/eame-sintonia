# CAP-WIN — janela de cultura mínima (Intelligence) · EXPERIMENTAL / NAO_PARA_CLIENTE

Ramo `claude/cap-win-intelligence-tn7qfi`, sobre o motor G0/v4 (`a5db06c4`) + insumos (`5683d8a`).
Desenho seguido: `docs/intelligence/CAP-WIN-DESENHO-R5.md` (W0–W8). Rede externa: nenhuma (só GitHub).
Livros vivos (`curadoria/*-V1.json`, `data/collection-ledger`, `candidatas/FONTES-CANDIDATAS.json`): **não tocados**.

## O que fiz

`motor/cap_win.py` (novo) lê o **livro** de uma corrida G0/v4 e os itens READY, e julga por
**cultura × problema × região** (com fase/BBCH, subárea e período) duas perguntas que nunca se fundem:

```text
WINDOW_DEFINED   que condição define o momento de agir?       (regra — atemporal)
WINDOW_OPEN_NOW  a fonte declara a condição satisfeita, e o facto tem tempo e é CURRENT?
```

- **W0 · par só em campo** (`JANELA_DECLARADA`: `CULTURA`, `PROBLEMA`, `REGIAO_DO_FATO`, com VALOR **e** BASE)
  — `motor/cap_win.py:389` `CHAVES_DO_PAR`, `:414` `par_em_campo`. Sem par: `NOT_POSSIBLE` (INT-LAW-091) e
  requisito `CROP_ISSUE_EM_CAMPO` / `REGION_EM_CAMPO`; o texto só entra como **sonda** (nunca vira CROP_ID).
  ⚠️ `PROBLEMA` **não existe** no contrato 033: é o nome **proposto** para o requisito do desenho.
- **W2/W3 · regra do V21 portada, não o ficheiro** (`scripts/v21_janelas.py @ 85df96f7`): 8 tipos, padrões e
  precedência `:207`; `aberta_agora` `:325` com os silêncios do V21. **Dois acréscimos declarados**, os dois
  medidos no corte ARIF × APOL:
  1. soglia não atingida escrita por extenso → `NO`, método `FONTE_DECLARA_SOGLIA_NAO_ATINGIDA` (`:286`) — o
     defeito que o desenho §3 achou no legado (resposta certa, razão errada);
  2. o plural «soglie» (`:165`): o V21 só conhecia «soglia», e o ARIF escreve «al disotto delle **soglie**».
- **O tempo só bloqueia o uso que exige tempo**: a regra entra por `LEITURA_ATEMPORAL_DE_CAPACIDADE`; o «agora»
  só pelo uso `CAP-WIN` que a corrida concede (`:552`). O que a fonte disse fica em `DECLARADO_PELA_FONTE`.
- **W4** `estado_temporal` `:441`: CURRENT / STALE / UNKNOWN pelo FACT_TIME do livro (nunca PUBLISHED_AT).
  `N_DIAS_CURRENT = 30` `:99` — **HERDADO do V21**, fixado antes de olhar; a decisão é do dono (desenho §7).
- **W5** `_apoios` `:602`: observação pelo grafo (originadores) **e** por rede declarada; a regra conta **uma vez**
  (sequências de 10 palavras partilhadas só no sentido conservador — nunca somam apoio).
- **W6** `_arestas` `:579`: `SUPPORT` / `CONTRADICTS` só entre observações do mesmo par, com período sobreposto e
  subárea compatível. Subáreas diferentes não se contradizem.
- **W7/W8** `_julgar_par` `:663`: objeto `ANALYTIC_JUDGMENT` / `CROP_WINDOW` com os campos do W7 e linhagem até
  ao RAW; `ACT_NOW` só com YES ∧ CURRENT ∧ ≥2 independentes **provados** ∧ 0 contradições (`:718`); senão
  `NO_DEFENSIBLE_ACTION_YET` com o porquê. `OPPORTUNITIES` sempre vazio.
- **Grafo**: `motor/grafo_de_dependencia.py` trazido **byte a byte** de `eb3a7b1d` (blob `34183b2f`), com as
  3 classes puras do teste dele em `tests/test_grafo_de_dependencia.py`. A integração do grafo na corrida/V21
  **não** veio (aquele ramo parte de `60faa7cb` e perderia D11/D14/D15).
- Mapa: peças `C-INT-CAP-WIN`, `C-INT-GRAFO-DEPENDENCIA`, `C-PROVA-CAP-WIN`. Ficam 🟡 PENDING («nunca lidas por
  gente»): **não recarimbei** — carimbo é leitura humana.

## O corte ARIF × APOL (fixture **SINTÉTICA**, `tests/dados/cap-win/arif-apol-mosca-sintetico.json`)

Reconstrução das citações do desenho; nenhum RAW no repo; URLs com `/SINTETICO/`.

| cenário | resposta |
|---|---|
| como medido na R5 (par em campo NÃO SEI) | 4 × `NOT_POSSIBLE` + 4 requisitos `CROP_ISSUE_EM_CAMPO`,`REGION_EM_CAMPO`; nenhum CROP_ID do texto |
| par em campo, tempo como medido | THRESHOLD definida pelas 3; APOL/ARIF 37 declaram `NO` mas não respondem agora (FACT_TIME NÃO SEI); só ARIF 38 responde → `NO`, 1 originador → `NO_DEFENSIBLE_ACTION_YET` |
| depois dos requisitos | THRESHOLD · aberta **NO** (`FONTE_DECLARA_SOGLIA_NAO_ATINGIDA`) · CURRENT · observação: 3 sinais, **2 originadores** (ARIF 37+38 = 1) · independentes provados **NÃO SEI**, prováveis 2 · regra **1** · Gargano costeiro = subárea UNKNOWN, **0 contradições** · **`NO_DEFENSIBLE_ACTION_YET`** — «monitorizar; a condição de intervenção não está satisfeita e a fonte declara que o tratamento não se justifica» |

É exatamente o resultado que o desenho §5 fixou antes.

## Testes antes/depois (por NOME, rede fechada)

Corredor: cada módulo de `tests/` num subprocesso, proxy numa porta morta. Resultados em
`provas/cap_win/BATERIA-BASE-5683d8a.json` e `provas/cap_win/BATERIA-DEPOIS-a7537ec.json`.

| | árvore | módulos | testes | falhas |
|---|---|---|---|---|
| ANTES | `5683d8a` | 255 | 5855 | 129 |
| DEPOIS | `a7537ec` | 257 | 5932 (+56 `test_cap_win`, +21 `test_grafo_de_dependencia`) | 129 |

**Falhas novas: 0. Sumidas: 0.** As 129 são as mesmas, nome a nome. A 1.ª passagem apanhou **uma nova**
(`test_a_porta_cli_liga_o_banco.test_1_nenhum_modulo_de_runtime_importa_provas`: eu importava a espinha de
`provas/` no runtime) — corrigido em `a7537ec` (`motor/cap_win.py:88`), sem tocar no teste. O herdado
`test_o_controle_separa_lei_de_mencao.test_M5` (carimbo) fecha com o commit do mapa.

## Mutação

`provas/cap_win/mutantes.py`: 22 defeitos plantados um a um em `motor/cap_win.py`, bytes restaurados e SHA
conferido. **22/22 mortos** (`provas/cap_win/MUTANTES.json`). Três testes nasceram de mutantes que sobreviviam:
M5 (a capacidade tem de obedecer aos usos do livro), M8 (o porquê tem de nomear a contradição), M18 (a oração
que manda parar fecha a janela).

## System Map

`correr_a_cadeia.py REGERAR` → `CADEIA=OK`; `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`**;
`impressao_da_arvore.py --conferir-carimbo` → **`IGUAL`** (conferido depois do commit final).
Efeito lateral: `docs/fontes/INDICE-DE-FONTES.md` conta +20 «endereços que o código chama» — são as URLs
sintéticas dos testes (o scanner conta todo `https://` em `.py`).

## O que fica NÃO SEI / não feito

- Se APOL e ARIF são **redes independentes**: a Collection declara (`REDE_DE_MONITORIZACAO`). Hoje NÃO SEI.
- O N de CURRENT (30, herdado) e o nome do campo `PROBLEMA`: decisões do dono / da Collection.
- ARIF 38: FACT_TIME no READY (07–13/09) ≠ período escrito (16–22/09). Registado, **não** corrigido.
- Pote (`montar_pote_r5.py`) não está neste repo: a saída traz `CAPACIDADES_EXECUTADAS["CAP-WIN"]` com versão e
  run, mas a entrada no pote não foi provada aqui.
- Clima/aplicação (§29 do mapa do dono), CAP-SCI/FIELD/OPP: fora desta missão.

## EM PALAVRAS SIMPLES

O Sintonia agora sabe responder «quando agir» sem inventar. Ele separa **saber a regra** («trate quando passar
de 4–5 % de picadas») de **saber que chegou a hora**. No caso da mosca-da-oliveira na Puglia, as duas fontes
dizem que o limite **não** foi atingido, e a APOL diz que tratar não se justifica — então a resposta é
**«ainda não há ação defensável: monitorizar»**, e isso é um resultado certo, não uma falha. Duas semanas do
mesmo boletim contam como uma testemunha só, a regra copiada do mesmo manual conta uma vez, e quando falta a
cultura, a praga ou a data no dado, o sistema diz **NÃO SEI** e pede o dado — em vez de adivinhar pelo texto.
