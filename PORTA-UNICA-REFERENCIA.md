# PORTA-UNICA-REFERENCIA — bulas e portfólio por UMA porta, numa edição só

```text
ORDEM     D116 do dono: bulas e portfólio = BIBLIOTECA DE REFERÊNCIA única e versionada; toda capacidade
          que fala de produto consulta a MESMA edição; proibido duplicar a tabela-mestra.
          D117: 14 dias sem checagem -> PODE_ESTAR_DESATUALIZADO; 30 -> autorização «a confirmar».
          (D116/D117 não estão escritas no repo; a fonte fica dita aqui e no cabeçalho da porta.)
PERGUNTA  «todo o sistema de inteligência já está linkado para consultar as bulas e portfólio?»
RAMO      claude/single-reference-gateway-hhhj7t   (base 21cc06c = lote6 671dm9)
REDE      nenhuma. Nada coletado. Livros vivos não tocados.
```

## A resposta curta

**Antes: não.** Só a CAP-SCI lia a casa `referencia/adama/` — direto no disco, sem edição nem frescor.
O cruzamentos-max lia **outra cópia** (os pares do leitor de rótulos e o CSV do Ministero de **07/09**,
outra edição). CAP-WIN, concorrência Meta e boletins **não liam nada**.

**Agora: as seis capacidades que falam de produto nesta base leem pela mesma porta**, na mesma edição, e
cada uma carimba no resultado a edição que usou. O que ainda não está ligado está listado abaixo, com o porquê.

## A porta — `motor/porta_da_referencia.py`

| o quê | onde |
|---|---|
| abre a casa em **duas metades que nunca se somam**: REGISTRO (autorização, Ministero) e CATÁLOGO (vitrine, ADAMA Italia) | `motor/porta_da_referencia.py:126` |
| **edição misturada = NÃO SEI inteira** (todo livro do REGISTRO tem de declarar o mesmo `CURRENT_SNAPSHOT`) | `motor/porta_da_referencia.py:151` |
| **D117**: `< 14` FRESCA · `>= 14` PODE_ESTAR_DESATUALIZADO · `>= 30` AUTORIZACAO_A_CONFIRMAR; sem data = a confirmar | `motor/porta_da_referencia.py:111` |
| o carimbo: EDICAO, DATA_DA_EDICAO, ULTIMA_CHECAGEM_OK, ESTADO_FRESCOR, edição do catálogo, sha256 de cada livro e a impressão deles | `motor/porta_da_referencia.py:208` |
| `autorizados(cultura, alvo)` — só do REGISTRO; bula não lida = **A_CONFIRMAR**, nunca «não autoriza» | `motor/porta_da_referencia.py:280` |
| `por_substancia` (concorrência: só substância) · `por_alvo` (alvo em qualquer cultura) | `:345` · `:382` |
| `no_catalogo` — responde vitrine, **nunca** autorização | `:412` |

**Não é uma segunda biblioteca.** Não copia tabela, não escreve, não cunha id. Quem escreve continua a ser o
construtor `fontes/adama_referencia.py`. A porta vive em `motor/` porque **ler** é trabalho da inteligência — e
porque em `fontes/` cada consumidor do motor seria uma travessia COLETA→INTELIGÊNCIA a mais (o teto medido é 12;
ficou em **12**).

### A edição, medida

```text
REGISTRO   PROD_FTS_6_20260831 · edição de 2026-08-31 · ULTIMA_CHECAGEM_OK 2026-09-07 · 20 dias a 27/09
           -> PODE_ESTAR_DESATUALIZADO   (vira AUTORIZACAO_A_CONFIRMAR a 2026-10-07)
CATÁLOGO   CAT_ADAMA_IT_20260915 · 12 dias -> FRESCA
```

A data da última checagem **não é escrita à mão**: o construtor confere a edição de 31/08 contra o bruto de
07/09 que já estava no repo (`fontes/adama_referencia.py:323`) — **602 de 602, 0 entradas, 0 saídas, 0 estados
diferentes** — e grava `SNAPSHOTS.LAST_CHECK_OK` (`:767`). Conferir não é derivar: a edição continua a de 31/08.
As edições de 07/09 e 14/09 do livro de coleta **não foram incorporadas** (é a missão
`nuvem-referencia-manutencao-v1`).

## Capacidade × ligada antes/depois × edição carimbada

| capacidade | antes | depois | edição carimbada | ficheiro:linha |
|---|---|---|---|---|
| **CAP-SCI** (ciência → rótulo ADAMA) | ligada **direto** ao disco, sem edição | pela porta; `REFERENCIA.CARIMBO`; D117 → `AUTORIZACAO: A_CONFIRMAR` | `PROD_FTS_6_20260831` | `motor/capacidade_cientifica.py:607`, `:622`, `:685` |
| **Motor das capacidades** (a análise da Intelligence R7) | 0 — a SCI abria sozinha, a WIN nada | abre a porta **uma vez** e dá a **mesma** referência à WIN e à SCI; `REFERENCIA_ADAMA` na saída | `PROD_FTS_6_20260831` | `motor/motor_das_capacidades.py:779`, `:822` |
| **CAP-WIN** (janela de cultura) | 0 | cada janela ganha `PRODUTOS_ADAMA` (bula lida autoriza cultura × problema?) sem mexer no `RESULT` | `PROD_FTS_6_20260831` | `motor/cap_win.py:752`, `:814`, `:819` |
| **cruzamentos-max** | **outra cópia**: `IT-ROTULOS-PARES.json` + CSV **07/09** | pela porta (`Referencia.da_porta`) | `PROD_FTS_6_20260831` | `motor/cruzamentos_max.py:359`, `:1153`, `:1166` |
| **Concorrência Meta** | 0 | `adama_no_anuncio`: substância/alvo que o criativo nomeia → registo ADAMA ativo? cultura do anúncio = NÃO SEI | `PROD_FTS_6_20260831` | `coleta/concorrencia_meta.py:526` (CLI `--adama`, `:567`) |
| **Boletim do campo / sinal** | 0 | `produtos_adama_do_boletim`: praga × cultura da **mesma secção** → autorizados; praga AUSENTE não pergunta | `PROD_FTS_6_20260831` | `leis/boletim_do_campo.py:640` |
| o piloto da sala (`provas/o_piloto_da_sala.py`) | **NÃO ESTÁ NESTA BASE** — só existe em `claude/int-pilot-sala-v1` | não tocado | **NÃO SEI** | — |
| `motor/voce_dal_campo.py` | 0 | 0 — fora do FAÇA desta missão | — | — |
| comentários | 0 | 0 — fora do FAÇA | — | — |
| portal (`italy-label-intelligence.js`) | payload selado 31/08 | não tocado (`italia-portale/` é casa estacionada) | — | — |

## O que a referência não tinha, e onde foi posto

| lacuna | estado | onde |
|---|---|---|
| **1.** citação do par e nível de ligação (o «grão» do cruzamentos-max) + estado da leitura de cada bula | **FECHADA — no construtor, não no consumidor.** Os 2030 usos são os mesmos 2030 pares do leitor, conferidos **par a par** antes de colar a citação; nasceu `LABEL-READINGS.json` (163 bulas, 102 lidas) | `fontes/adama_referencia.py:355`, `:727` |
| **2.** data de registo e de revoga | **ABERTA.** A edição de 31/08 não as traz; trazê-las é derivar edição nova | `motor/cruzamentos_max.py:175` |
| **3.** registos das outras empresas (mercado) | **ABERTA.** A referência é da ADAMA; ler o CSV direto seria uma 2.ª tabela-mestra, de outra edição | `motor/cruzamentos_max.py:175`, `:954` |

**O que isto custa no cruzamentos-max, medido:** pela porta o grão ficou **idêntico** (86/86 estados, 28/28
declarações de grupo). Mudam só duas coisas: os **3 CONFIRMED_YES → POSSIBLE_ANSWER_YES_A_CONFIRMAR** (sem data de
registo a validade na data do boletim não se prova — `:803`) e os **3 competitive sets → NÃO SEI** (lacuna 3).
Pote: portfolio 103 → 96 objetos, competitors 125 → 0. Isto não é perda de prova: era prova feita com **outra
edição**, que a D116 proíbe.

## Teste de contrato — `tests/test_porta_unica_referencia.py` (37 testes)

| | prova |
|---|---|
| **A** | varredura por AST de `motor/`, `leis/`, `coleta/`: ninguém nomeia `referencia/adama`, `IT-ROTULOS*`, `PROD_FTS*`, `COMMERCIAL-CATALOG` em código fora da porta. Exceções **declaradas uma a uma** (`:65`) — 2 produtores, 7 dívidas, 2 menções — e a lista **só encolhe** (exceção velha reprova). Os 6 religados não podem estar nela |
| **B** | cada consumidor carimba a edição da porta; o motor usa **uma** referência para WIN e SCI (prova com impressão diferente) |
| **C** | edição misturada (um livro, duas fotos correntes, catálogo) → NÃO SEI inteira |
| **D** | registo revogado na vitrine não é autorizado; apagar o catálogo não muda nenhuma autorização |
| **E** | D117 nos três degraus; aos 30 dias nada sai afirmado (porta, CAP-SCI, cruzamentos-max) |
| **F** | livros commitados = o que o construtor produz; bruto divergente não confirma |
| **G** | bula não lida → A_CONFIRMAR; a frase «a ADAMA não tem» não sai da porta |
| **H** | o carimbo é o sha256 do livro; mexer num livro muda a impressão |

Dívida declarada no **A** (fora do escopo, próxima religação): `coleta/cruzar_regua_rotulo.py`,
`coleta/pesquisadores_t6.py`, `motor/pacote_convergencia.py`, `leis/data_clock.py`, e o legado V2
(`motor/normalize_substance.py`, `motor/v2_cruzamentos.py`, `motor/v2_montar_handoff.py`).
⚠️ A varredura cobre `motor/ leis/ coleta/`, como a missão pediu — **não** `provas/`, onde o piloto viveria.

## Mutação

| prova | resultado |
|---|---|
| **porta** `provas/porta_unica_referencia/mutantes.py` | **20/20** — leitura direta ×4, edição misturada ×2, motor com duas aberturas, catálogo como autorização ×2, frescor ignorado ×7, bula não lida vira «não», checagem que confirma sempre, carimbo sem o sha, cap_win sem carimbo. Cada um apanhado por teste **nomeado** (`MUTANTES.json`) |
| cruzamentos-max (já existia) | 31/31 |
| cap-win · cap-sci | 22/22 · 22/22 |
| int-r7 | 32/32 — **M5 e M28 reancorados, declarado**: a linha-alvo ganhou `referencia=ref`; o defeito plantado é o mesmo |

## Ajustes de teste, declarados

- `tests/test_cruzamentos_max.py` classe `X_Real`: recorre com o **HOJE que o JSON commitado declara** (D117: o frescor
  depende do dia; sem isto o veredito mudaria sozinho com o calendário). Nenhuma asserção afrouxou.
- `provas/int_r7/mutantes.py` M5/M28: só o texto-âncora (acima).

## Bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `21cc06c` | 312 | 6938 | 131 |
| ramo (código `3a90f23`) | 314 | 7030 | 131 |

- **Novas: 0. Sumidas: 0.** As 131 são as herdadas da base, pelo nome.
- 2 módulos novos, 0 falhas: `test_porta_unica_referencia` 37 · `test_cruzamentos_max` 55 (trazido da outra branch).
- JSON: `provas/porta_unica_referencia/BATERIA-BASE-21cc06c.json`, `…/BATERIA-DEPOIS-3a90f23.json`.
- Medida sobre `3a90f23`; o commit seguinte só acrescenta este relatório, os JSON da bateria e o mapa regerado.

## System Map

`REGERAR` pela cadeia · `VALIDAR` = **SYSTEM_MAP_CHECK=PASS** · `--conferir-carimbo` = **IGUAL** (conferido depois do
último commit). Peças novas declaradas: `C-INT-PORTA-REFERENCIA` (Z-MOTOR), `C-PROVA-PORTA-REFERENCIA` (Z-PROVA).
Frases das peças tocadas reescritas à mão. **Não** usei `--stamp`: ele recarimba o mapa inteiro, inclusive peças que
não reli — as tocadas ficam 🟡 «mudou depois da declaração», que é a verdade.
`test_system_map.py`: as mesmas 10 reprovações da base; `a_coleta_nao_conversa_com_o_motor_as_centenas` passa (12 ≤ 12).

## EM PALAVRAS SIMPLES

Antes, cada peça da inteligência que falava de produto ADAMA ia buscar a informação onde lhe dava jeito: uma abria
a pasta da referência, outra lia uma cópia antiga de outro dia, e três nem perguntavam. Era possível duas telas
dizerem coisas diferentes sobre a mesma bula sem ninguém perceber.

Agora há **uma porta só**. Quem quer saber «que produto ADAMA a bula autoriza para esta cultura e esta praga?»
pergunta à porta, e a resposta vem sempre da mesma edição, com a data dela, a data da última vez que alguém
conferiu que ela ainda bate com o Ministério, e um aviso de frescor: hoje ela tem 20 dias sem conferência, por isso
sai «pode estar desatualizada»; a partir de 7 de outubro, sem nova conferência, toda autorização sai «a confirmar».
A vitrine da ADAMA (o que está à venda) fica separada da bula (o que é permitido): estar à venda não prova que é
permitido. Bula que ninguém leu vira «a confirmar», nunca «não tem».

O preço honesto: três «sim» do cruzamentos-max tinham sido confirmados com uma edição de outro dia; com a edição
única voltam a «sim, a confirmar», porque a edição atual não traz a data de registo. Trazer essa data — e os
concorrentes — é a próxima missão (atualizar a edição), não esta.
