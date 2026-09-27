# POTE-V2-UNICO — um só contrato Intelligence → casco

> **EXPERIMENTAL · NAO_PARA_CLIENTE.** Nada publicado, nenhum deploy. No repositório só há dado **SINTÉTICO
> declarado**. D97 e D112 **não estão escritas no repositório**: segui o resumo delas no pedido da missão.
> Base: lote 4 final `77da247` + merge de `origin/nuvem-int-casco-ponte-v1` (`f357712`, resolvido pelo
> significado: o lote 4 já trazia a ponte na versão POTE-UNICO, mais nova; nenhum ficheiro mudou).

## 1 · O que foi feito, e onde

| o quê | onde |
|---|---|
| **O contrato, escrito** (um só: `POTE_INTELLIGENCE_CASCO/v2`) | [`docs/intelligence/pote-v2/CONTRATO-POTE-V2.md`](docs/intelligence/pote-v2/CONTRATO-POTE-V2.md) |
| schema (forma) | [`docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json`](docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json) |
| validador = forma do schema + lei de `conferir_pote` (lê `.json` e o `sintonia-pote.js`) | `pacote/validar_pote_v2.py:53`, `:98` |
| `INTELLIGENCE_RUN_ID` no topo; em `CABECALHO` só por leitura declarada (`LEITURA_DE_COMPATIBILIDADE`); topo≠cabeçalho = recusa; um pote R5 não se readapta | `pacote/pote_intelligence_casco.py:483`, `:725` |
| PROVA com `URL` e `PUBLISHED_AT` (ou `NAO SEI` com `*_BASE`), `G0`, `ADMITIDA_POR` | `pacote/pote_intelligence_casco.py:172`, `:370`, `:770` |
| D112: `ENTITY_SOURCE` / `LOCATION_SOURCE` com o nome deles; lugar da fonte ≠ lugar do facto | `pacote/pote_intelligence_casco.py:457` |
| **P7**: Registro e resultado honesto (`NAO`, `NAO_TRATAR_AGORA`, `NO_DEFENSIBLE_ACTION_YET`) não dependem de `FACT_TIME`; proveniência continua obrigatória | `pacote/pote_intelligence_casco.py:182`, `:238`, `:313`, `:775` |
| **P8**: no Polso, `MERCADO.LEITURA` = `SERIE_MEDIDA` só com ≥2 pontos na mesma unidade; afirmar mudança sem série é recusado | `pacote/pote_intelligence_casco.py:259`, `:452`, `:804` |
| casco: um só carregador; pote pedido (`?pote=local`) e ausente → **NAO SEI** em cada ferramenta, sem snapshot/demo; vazio → `NAO SEI · VUOTO · <porquê>`; série vs «SEGNALE ISOLATO — NON è una variazione»; a Sala só como prova (ITEM_ID · G0 · admitida por) | `italia-portale/client/sintonia-pote-casco.js:25`, `:119`, `:127`, `:138`, `:182`, `:203` |
| portal: o leitor decide também «pedido e ausente»; bloco mostra mercado, uso sem tempo, D112, origem | `italia-portale/client/portale.html:3660`, `:4066` |
| mapa declarado: `validar_pote_v2.py` em `C-POTE-INT-CASCO`; `provas/pote_v2/*` em `C-PROVA-POTE-CASCO` | `system-map/data/architecture.declared.json` |

**Ajustes DECLARADOS de testes/mutantes antigos** (decisão desta missão: a publicação chama-se `PUBLISHED_AT` no
contrato único): `tests/test_pote_intelligence_casco.py` B2, B3, B4, I4 (só o nome do campo; a mesma prova);
`provas/_mutantes_pote_casco.py` Q3, Q6, Q7, Q8 (mesmo defeito, alvo no código novo). Fixture
`POTE-SINTETICO.json` regenerada pelo gerador (K2 confere). Nenhum teste enfraquecido.

**Fora do âmbito, dito:** sem `?pote=local` o casco continua a mostrar o legado (snapshot/demo). Trocar isso
muda o que o deploy público mostra — decisão do dono.

## 2 · P7 medido — quantas das 46 recusas voltam

O R6 real não está no repo; só as contagens. Fixture **SINTÉTICA** com as mesmas contagens
(`tests/fixtures/pote/CORRIDA-SINTETICA-R6-EQUIVALENTE.json`, gerada por `provas/pote_v2/medir_recusas_r6.py`):

| | base `f357712` | depois |
|---|---|---|
| recusas | **46** (todas `ITEM_BLOQUEADO_EM_G0`) | **1** |
| Registro delle fonti | 3 de 47 | **47 de 47** |
| cruzamento «não» (APOL) | recusado | **no Portafoglio** |
| Polso (6 preços soltos) | sem leitura de série | 6 × `SINAL_SOLTO` |

**45 de 46 voltam.** A que fica é o **controlo** (um SINAL sem tempo ancorado — sinal exige tempo). O motivo
real da 46.ª recusa do R6: **NAO SEI** (as chaves medidas não o trazem).

## 3 · Testes — antes/depois, pelo NOME

Bateria inteira (`provas/integra_noite/bateria_inteira_por_nome.py`, rede fechada), base `f357712` × ramo
`9719efc`; resultados em `provas/pote_v2/bateria-*.json`.

| | base | ramo |
|---|---|---|
| ficheiros de teste | 393 | 394 (+`tests/test_pote_v2_unico.py`) |
| testes corridos | 7.373 | 7.411 |
| ficheiros vermelhos | 77 | 77 |
| falhas por nome | 339 | 337 |

**0 falhas novas.** 2 passaram a passar (`test_topologia_persistida::o_artefato_diz_quantos_documentos_leu`,
`test_o_controle_separa_lei_de_mencao::test_M5…`): não toquei nesse código — **NAO SEI** a causa (provável
estado do mapa na worktree da base); não as reivindico.

Do pote: `tests/test_pote_v2_unico.py` **38/38** · `tests/test_pote_intelligence_casco.py` **45/45** ·
`tests/test_pote_no_casco.mjs` **118/118** (antes 93) · `tests/test_ponte_intelligence_casco.py` verde.

## 4 · Mutação

- **Nova — `provas/pote_v2/mutantes_pote_v2_unico.py`: 25/25 mortos.** Sem run id no topo, compatibilidade não
  declarada, topo≠cabeçalho, prova sem URL / NAO SEI sem base, base apagada, publicação vira tempo, schema sem
  a base, sinal solto como mudança (1 ponto; unidades diferentes; afirmar sem série; validador), recusa por falta
  de tempo em uso que não exige tempo, Registro volta a depender do tempo, todo uso dispensa tempo, proveniência
  dispensada, oportunidade «não», validador aceita uso temporal sem tempo, lugar da fonte, LOCATION_SOURCE
  some; 6 no casco. **Achado:** na 1.ª corrida K2 (leitor aceita série de 1 ponto) **sobreviveu** — faltava a
  prova; acrescentei-a (P10) e morreu.
- **Antiga — `provas/_mutantes_pote_casco.py`: 29/29 mortos.**

## 5 · Mapa

`correr_a_cadeia.py REGERAR` → `CADEIA=OK` · `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`** · commit ·
`impressao_da_arvore.py --conferir-carimbo` → **`IGUAL`** (medido de novo depois deste relatório).

## 6 · Comando para o coordenador — regerar o pote a partir da saída do motor e ver localmente

```bash
# 1. o pote, a partir do livro/entrada da corrida (o que o motor escreve; ex.: ENTRADA-DO-POTE-R6.json)
py pacote/pote_intelligence_casco.py C:/…/ENTRADA-DO-POTE-Rn.json italia-portale/client/sintonia-pote.js
# 2. conferir forma + lei (tem de dizer PASSA)
py pacote/validar_pote_v2.py italia-portale/client/sintonia-pote.js
# 3. o pote fica fora do Git (tem de responder o caminho)
git check-ignore italia-portale/client/sintonia-pote.js
# 4. publicar LOCALMENTE (so na maquina) e abrir — o ?pote=local e obrigatorio
py -m http.server 8765 --bind 127.0.0.1 --directory italia-portale/client
#    http://127.0.0.1:8765/portale.html?pote=local#sources   (#meeting #radarfuturo #market #portfolio #archive …)
```

Se a entrada ainda trouxer o id só em `CABECALHO`, o pote sai com ele no topo e a leitura escrita em
`LEITURA_DE_COMPATIBILIDADE`. Um POTE-R5 (já pote) é recusado: regenere a partir do livro da corrida.

## 7 · Design (lei do CLAUDE.md)

Claude Design **não consultado** (a missão proíbe sites externos). Reutilizei os padrões do próprio bloco do pote
(aviso âmbar `#F5B317`, linha de chave/valor, cores do extrato ADAMA); nenhum componente novo.

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND   (no extrato local; no Claude Design: NAO SEI)
NEW_PATTERN_REQUIRED = NO               (linhas de texto no padrao ja existente do bloco)
```

## 8 · NAO SEI / por decidir

1. Texto de D97 e D112 (não estão no repo). 2. Motivo real de cada recusa do R6 (só chaves medidas).
3. Se o bot marca o «não» da APOL em `CROSSING_STATE`, `RESULTADO` ou outro campo — o pote lê os três primeiros.
4. Vocabulário `USOS_BLOQUEADOS`/`USOS_DISPONIVEIS` da LINEAGE R6: não usado (sem definição no repo).
5. Mudar o padrão sem `?pote=local` (deploy público) — decisão do dono.

## EM PALAVRAS SIMPLES

Havia duas «receitas» de pote que não encaixavam. Agora há **uma só, escrita**, com um fiscal
(`validar_pote_v2.py`) que a confere. Cada coisa no pote diz **de que corrida é**, e cada prova traz **o link e
a data de publicação** — ou diz **porque não os tem**.

Consertei dois defeitos: **(P7)** o pote jogava fora tudo o que não tinha data, até o que não precisa de data
(«não vale a pena» e o registro das fontes) — agora voltam 45 de 46 (no ensaio sintético), e as 47 fontes
aparecem; **(P8)** um preço solto era mostrado como «mudança de mercado» — agora só uma série de 2+ preços na
mesma unidade pode ser lida assim; um ponto só aparece como «sinal isolado».

Na tela, se o pote for pedido e não chegar, aparece **NAO SEI** — nunca dados de demonstração no lugar.
Plantei 54 defeitos de propósito; os testes apanharam os 54. Nenhum teste que passava antes passou a falhar.
