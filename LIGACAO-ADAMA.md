# LIGACAO-ADAMA — todo fato da Intelligence ligado à bula e ao portfólio, pela porta única

```text
ORDEM     D123 do dono (27/09): «todo fato do sintonia tem que estar linkado a bula e ao portfolio senao
          nada faz sentido, qualquer coisa». D123 não está escrita no repo: a fonte fica dita aqui e na porta.
RAMO      claude/adama-linking-gateway-a2fewj  (base c551062 = lote6 + PORTA-UNICA-REFERENCIA)
          + merge de claude/pote-v2-unico-contract-y8o1pi (o contrato único do pote não estava na base)
REDE      nenhuma. Nada coletado. Livros vivos não tocados. Casco: nenhuma linha escrita por esta missão.
HOJE      2026-09-27 (declarado nas medições)
```

## O que foi feito

| # | o quê | onde |
|---|---|---|
| 1 | **Uma função, na porta**: `ligacao_adama(ref, chaves)` → `LIGACAO_ADAMA/v1` selada (`SELO` = sha256 do conteúdo) | `motor/porta_da_referencia.py:560` |
| | estados D123: `AUTORIZADO_BULA_LIDA` · `A_CONFIRMAR` · `SO_CULTURA` · `ADAMA_SEM_PRODUTO` · `NAO_SEI` + `FALTA` | `motor/porta_da_referencia.py:438-454` |
| | só `LINHA_DA_TABELA`/`BLOCO_DA_CULTURA` de bula **lida** autoriza; `DECLARACAO_DE_PRODUTO` → A_CONFIRMAR; D117 ≥ 30 d → A_CONFIRMAR | `:446`, `:691-716` |
| | fato com **várias culturas + um problema** → A_CONFIRMAR (o fato não liga o problema a uma cultura) | `:698` |
| | `ADAMA_SEM_PRODUTO` só com leitura completa: todas as bulas ativas do grão lidas, ou a composição de **todos** os registos ativos (163/163) | `:616`, `:686`, `:714`, lei em `:762` |
| | chaves: só `CULTURA/PROBLEMA/SUBSTANCIA` com `VEM_DE`; texto → `ChaveInvalida`; valor sem procedência não conta | `:464`, `:542` |
| | travas: `NAO_PROVA=[PRESSAO_DE_CAMPO, DEMANDA]` (INT-LAW-145), `CONTA_COMO_FONTE_INDEPENDENTE=false` (INT-LAW-076), `CATALOGO_E_AUTORIZACAO=false` (D116) | `:454` |
| | `conferir_ligacao` = a lei que pote e fila aplicam (selo, porta, estados, travas, carimbo) | `:720` |
| | vocabulário CROP_*/ISSUE_* **chamado** do dono (`motor/v21_normalizar.py`), não copiado | `:436`, `:480-506` |
| 1 | consumidores chamam a porta e anexam a **todo** objeto que emitem | CAP-WIN `motor/cap_win.py:823,826` · CAP-SCI `motor/capacidade_cientifica.py:762` · motor `motor/motor_das_capacidades.py:599,659,695,748` (+ portão `:903`) · cruzamentos_max `motor/cruzamentos_max.py:1014,1016,1109,1118,1139,1169` · voce_dal_campo `motor/voce_dal_campo.py:801` · market `leis/preco_de_mercado.py:356,427` · boletim `leis/boletim_do_campo.py:662` · competitors `coleta/concorrencia_meta.py:560` |
| 1 | **o pote recusa**: `SEM_LIGACAO_ADAMA`, `LIGACAO_ADAMA_FORA_DA_PORTA`, `REFERENCIA_NAO_E_FONTE_INDEPENDENTE`; `conferir_pote` reprova edições misturadas | `pacote/pote_intelligence_casco.py:476-485`, `:757`, `:850` |
| 1 | contrato: revisão **anotada** `v2 + LIGACAO_ADAMA/v1 (D123, 2026-09-27)` (o nome continua v2 — o casco lê-o assim); schema com `$defs/ligacao` | `pacote/pote_intelligence_casco.py:80`, `docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json`, `docs/intelligence/pote-v2/CONTRATO-POTE-V2.md` §5b |
| 2 | **fila BULAS_A_LER** (sem coleta, determinística): ADAMA primeiro por nº de fatos, depois concorrentes; `LOTE_24H` por host, 5 por lote (o teto quem aplica é a Coleta, D38) | `motor/fila_bulas_a_ler.py` → `docs/intelligence/ligacao-adama/FILA-BULAS-A-LER.json` |
| 3 | **medição** sobre dados reais offline | `provas/ligacao_adama/medir.py` → `provas/ligacao_adama/MEDICAO.json` |
| 4 | **patch** da Bíblia (INT-LAW-303), **não aplicado** (`git apply --check` passa) | `docs/intelligence/ligacao-adama/PATCH-BIBLIA-INT-LAW-303.patch` |
| 5 | teste de contrato (38) + mutação | `tests/test_ligacao_adama.py`, `provas/ligacao_adama/mutantes.py` |

**Não criei outro esquema de ID** (IDENTIDADE-CRUZAMENTO: identidade pela PERGUNTA). A ligação responde à pergunta
com as chaves que o fato já tem; não entra no `OBJETO_ID`.

## 3 · Medição (HOJE 2026-09-27, edição `PROD_FTS_6_20260831`, frescor `PODE_ESTAR_DESATUALIZADO`, 20 dias)

| insumo | fatos | AUTORIZADO_BULA_LIDA | A_CONFIRMAR | SO_CULTURA | ADAMA_SEM_PRODUTO | NAO_SEI | motivo dominante do NAO_SEI |
|---|---|---|---|---|---|---|---|
| 86 cruzamentos R7 (`docs/intelligence/r7/ANALISE-R7.json`, sha `2ecdabd4…` = o de `nuvem/identidade-cruzamento-v1`) | 86 | 0 | 0 | 0 | 0 | **86** | CULTURA (86) |
| 14 pares por secção R7 (olivo × mosca…) | 14 | 0 | **14** | 0 | 0 | 0 | — |
| sinais R7 no insumo offline | **9 de 19** | 0 | 0 | 0 | 0 | 9 | CULTURA (9) |
| acervo `ENTRADA-INTELLIGENCE-ACERVO.json` (git `organize-collection-system-japwor`, sha `a756e961…`) | 2080 | 31 | 125 | 349 | 0 | 1575 | CULTURA (1575) |
| **tudo** | **2189** | **31** | **139** | **349** | **0** | **1670** | **CULTURA (1670)** |

- **Motivo dominante de NAO_SEI = CULTURA, em 100 % dos NAO_SEI.** Nos cruzamentos a cultura do boletim é lista do
  DOCUMENTO (ENTITY_SOURCE = DOCUMENT, D112) e não entra como chave; o que têm é a substância — os 86 levam os
  produtos ADAMA registados com ela (`REGISTRADO_COM_A_SUBSTANCIA`), não autorização. No acervo, 1575/2080 itens não
  têm `CROP_IDS`. (Ref. do coordenador na Sala real: 150/242 com CULTURA, 92 NAO SEI — mesma direção.)
- **ADAMA_SEM_PRODUTO = 0**: com 61 bulas ativas por ler, a porta não pode dizer que não há. Só dá por substância
  sem registo ativo (ex.: ALACLOR, prova no teste D2) — nenhum fato medido cai lá.
- `A_CONFIRMAR` do acervo inclui CROP_DURUM_WHEAT: as bulas escrevem FRUMENTO (= CROP_WHEAT_GENERIC no vocabulário do
  dono), e trigo duro ≠ trigo genérico. É grão, não ausência.
- **Os 10 sinais da R6 não estão em ficheiro nenhum deste repo: NÃO MEDIDOS.** Os 9 do insumo não trazem chave.

**Fila:** 61 bulas ADAMA a ler (as 61 ativas não lidas), 14 com DOCUMENT_ID/URL (`www.adama.com`, 3 lotes de 24 h),
47 sem URL na referência (host NAO SEI: a Coleta acha-as pelo número de registo). 30 substâncias pedem cadastro
concorrente — **NAO SEI** (lacuna 3: a edição só traz registos ADAMA; `CONCORRENTES_MESMA_SUBSTANCIA = []`).

## Ajustes declarados (teste/fixture — nenhuma asserção afrouxou)

- `tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json`, `…-V2-UNICO.json`: cada objeto recebeu a ligação que **a porta**
  dá a uma corrida sintética sem referência (`NAO_SEI · FALTA=REFERENCIA`), por `provas/ligacao_adama/ligar_fixtures.py`
  (D123). `POTE-SINTETICO*.json` regenerados pelo comando que os testes K2 citam — **mesmos 7 objetos e mesmas
  recusas, pelo motivo**, antes e depois.
- `provas/pote_v2/medir_recusas_r6.py`: a fixture R6-equivalente ganha a mesma ligação sintética (regerada com `--escrever`).
- `docs/intelligence/r7/CRUZAMENTOS-MAX*.json`: regenerados com o HOJE que o JSON commitado declara (2026-09-27); as
  CONTAGENS não mudaram, só entrou a `LIGACAO_ADAMA`.
- `leis/preco_de_mercado.py`: `precos_do_texto(texto)` manteve a assinatura (o teste que proíbe publicação/coleta
  de entrar continua igual); sai com ligação `NAO_SEI/REFERENCIA`, e `com_ligacao_adama(res, ref)` liga com a porta aberta.

**Dívidas declaradas:** a substância em `coleta/concorrencia_meta.py` vem do **criativo** (lida pelo vocabulário da
referência), não da Collection; a cultura em `voce_dal_campo`/`preco_de_mercado` é a que **essas capacidades** já liam
do texto (o `VEM_DE` diz). A porta, ela própria, não lê texto nenhum. O casco não mostra a ligação (fora de escopo:
«não mexer no casco»).

## Testes — bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

BATERIA_PLACEHOLDER

## Mutação

MUTACAO_PLACEHOLDER

## System Map

MAPA_PLACEHOLDER

## EM PALAVRAS SIMPLES

Agora cada coisa que o SINTONIA diz — um estudo, uma janela, uma voz de campo, um preço, um cruzamento de
boletim — sai com uma etiqueta que responde «e o que é que a bula ADAMA diz sobre isto?». Essa etiqueta só pode ser
feita por uma porta, sempre com a mesma edição da bula e a data dela, e leva um lacre: se alguém a fizer à mão ou a
mexer, o pote recusa o objeto. Objeto sem etiqueta também é recusado.

A etiqueta é honesta: «autorizado» só quando a bula foi lida e diz a cultura e a praga na mesma linha; «a confirmar»
quando a bula não foi lida ou só diz as coisas em listas separadas; «só cultura» quando o fato não diz a praga;
«ADAMA sem produto» só quando a porta leu tudo e não há mesmo; e «não sei» a dizer o que falta. Ela nunca diz que há
pressão de praga nem procura, e nunca conta como mais uma fonte.

Medido: de 2189 fatos, 31 saem autorizados, 139 a confirmar, 349 só cultura, e 1670 «não sei» — todos porque **falta a
cultura** no fato. O próximo passo não é na porta: é a Coleta trazer a cultura de cada fato, e ler as 61 bulas que a
fila pede.
