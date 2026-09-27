# LOTE6-INTEGRA — as quatro entregas de 27/09 numa árvore só

Missão `nuvem-lote6-integra-v1`. Base: **`18461b92`** (lote 4 final, o vivo). Ramo:
`claude/lote6-integra-671dm9`. Fast-forward sobre `18461b92`: **SIM** (`18461b92` é ancestral).

## O que entra (as quatro cabeças, inteiras)

| entrega | ramo | cabeça | como entrou |
|---|---|---|---|
| boletim-por-secao | `claude/bulletin-by-section-c39nij` | `6b0a7c0` | já no 1.º commit (linear sobre a base) |
| metodo-puglia | `claude/metodo-puglia-rm5sdo` | `52da843` | merge `098f863` |
| estudos-chaves | `claude/extract-study-metadata-x1m3tv` | `99ca619` | merge `09eb5ec` |
| int-r7-caps | `claude/int-r7-caps-motor-5rwp2n` | `f323964` | merge `a053238` (ramo com base antiga `60faa7cb`) |

Os quatro `git merge-base --is-ancestor <cabeça> HEAD` = SIM. A lista commit a commit é
`git log --reverse 18461b92..<SHA final>`.

## Conflitos — resolvidos pelo significado

- **Gerados do mapa**, `CENSO-DAS-LIGACOES`, `INDICE-DE-FONTES` (gerado): saídas da cadeia → refeitas
  por `correr_a_cadeia.py REGERAR`, nunca à mão.
- **`architecture.declared.json`**: união por peça (id). `C-INT-GRAFO-DEPENDENCIA` ficou com a frase do
  lote 4 (o grafo JÁ está ligado à corrida G0 e ao V2.1 aqui; a frase do int-r7 dizia que não) + a
  CAP-WIN como utilizadora. Entraram 6 peças do int-r7 e a C-AFIRMACAO-DA-FONTE do metodo-puglia.
- **`motor/corrida_da_inteligencia.py`**: os dois lados (comentário do SIGNAL_ID do lote 4 +
  `TEMPO_LUGAR_EVIDENCIA` do G0/v4, usado pelos campos `FACT_*_KIND` do sinal).

## As junções — lei e código a dizer o mesmo

| ponto | o que estava | o que ficou | onde |
|---|---|---|---|
| vocabulário D112 no extrator por secção | cópia própria de `ENTITY_SOURCES`/`LOCATION_SOURCES` | lido do dono (`afirmacao_da_fonte`, `lugar_do_fato`); palavra fora da lei = `ImportError` | `leis/boletim_do_campo.py:263-289` |
| travas da lei na saída do extrator | o extrator decidia sozinho | `procedencia_da_entidade` e `fact_location` decidem antes de sair | `leis/boletim_do_campo.py:520`, `:530`, `:558`, `:590` |
| gold da Puglia | duas cópias byte-idênticas | uma: a selada `tests/fixtures/puglia/…`; a de `docs/iab/puglia` saiu | `scripts/lugar_fato/gold_puglia.py:42` |
| teste do gold contra o código | 5 `expectedFailure` contra os leitores por documento | T7 mede `ler_afirmacao` caso a caso; **30/30** | `tests/test_metodo_puglia.py:354`, `:361` |
| estudos | `ENTITY_SOURCE = «NAO SEI»` (fora da COL-LAW-221) | `UNKNOWN`; o VALOR continua `NAO SEI` | `leis/estudo_chaves.py:59`, `:152-162` |
| contrato READY (D58) | motor levava `JANELA_DECLARADA` ao lado do READY (58 `KeyError`) | dentro do READY, como o dono; cópia das capacidades já passada pela D112a | `motor/motor_das_capacidades.py:230`, `:236`, `:311` |
| relações INT-LAW-078/079 | palavras do motor (`MESMA_REDACAO`…) | + `RELATION`/`CONTRADICTION_STATUS` da lei, com a função da lei como oráculo no teste | `motor/motor_das_capacidades.py:86`, `:121`, `:411`, `:441`, `:470` |
| rito da emenda V1.5 | B9: bloco da emenda V0.4 declarava `IMPLEMENTATION_AUTHORIZED = inalterado` | o valor do cabeçalho + `IMPLEMENTATION_AUTHORIZED_MUDOU = NAO` | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` §33.4 |

Nenhum ESPERADO do dono mudou (`GOLD_SHA256` igual).

### Testes ajustados — DECLARADOS, cada um citando a decisão

- `tests/test_metodo_puglia.py` T7 — as marcas `expectedFailure` saíram porque o código passou a
  cumprir (o topo do próprio ficheiro manda tirá-las).
- `tests/test_estudo_chaves.py:82` — `ENTITY_SOURCE` sem trecho = `UNKNOWN` (COL-LAW-221/D112).
- `tests/test_motor_das_capacidades.py:93` — A3: a janela vai dentro do READY (D58).
- `tests/test_integracao_biblia.py`, `tests/test_portoes_da_collection.py` — contagens pinadas
  V1.4/105/2xx=18 → V1.5/108/21 pela emenda V1.5 **registada** (histórico constitucional + D112 no
  Diário), como esses testes exigem. A versão antiga e o 108 escrito à mão passam a reprovar.
- Fixture SINTÉTICA `tests/dados/cap-sci/…` ganhou `JANELA_DECLARADA = JANELA_NAO_MEDIDA` do dono.

## Bateria inteira, por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `18461b92` | 303 | 6611 | 131 |
| ramo (código final `3ce7094`) | 312 | 6938 | 132 |

- **Sumidas: 0.** Novas: **1** — `test_o_controle_separa_lei_de_mencao.test_M5` (carimbo do mapa; é
  medido antes do REGERAR final e fecha com ele — reconferido depois, ver o fim).
- A 1.ª corrida achou 4 novas (B9, T2_T3, matriz, total), **todas nascidas no ramo metodo-puglia**
  (medido: passam em `2ef6fef8`, falham em `52da843`). Consertadas acima.
- Herdada, não consertada aqui: `test_fundacao_da_coleta.test_a_base_de_comparacao_existe`.
- 9 módulos novos, 0 falhas: `boletim_por_secao` 36 · `cap_win` 56 · `capacidade_cientifica` 49 ·
  `estudo_chaves` 28 · `grafo_de_dependencia` 21 · `lote6_integra` 17 · `metodo_puglia` 30 ·
  `motor_das_capacidades` 64 (1 skip: **NÃO SEI** — sem Postgres portátil) · `todo_ready_atravessa_o_intake` 14.
- JSON: `provas/lote6_integra/BATERIA-BASE-18461b92.json`, `…/BATERIA-RAMO.json`.

## Mutação

| prova | resultado |
|---|---|
| **junção** `provas/lote6_integra/mutacao_juncao.py` | **12/12** (J03 1.ª forma era equivalente — `tuple()` de tupla é o mesmo objeto; trocada pelo defeito real, declarado) |
| boletim-por-secao | 21/21 (M02 ficou equivalente com a trava da lei; redefinido, declarado, como «promover E desligar a trava») |
| metodo-puglia | 6/6 |
| estudos-chaves | 13/13 |
| int-r7 · cap-win · cap-sci | 32/32 · 22/22 · 22/22 |

## Limites declarados

- O `ENTITY_SOURCE` do **motor** (int-r7) quer dizer «de que campo da Sala veio o valor»
  (`JANELA_DECLARADA.CULTURA`, contagens da LINEAGE…); o da COL-LAW-221 quer dizer «onde o nome
  estava no texto». Mesmo nome, dois sentidos. **Não resolvido aqui**: muda o contrato de saída ao
  pote v2 (outro dono). Proposta: renomear o do motor para `PROCEDENCIA_DO_VALOR` e carregar o
  `ENTITY_SOURCE` da lei quando o bloco o tiver.
- Só os boletins (T3) passam pelo extrator por secção; lint de fidelidade e espécie da afirmação
  continuam sem produção de ficha que os chame.

## EM PALAVRAS SIMPLES

Quatro equipas entregaram hoje peças que se encaixam. Juntei-as e fui ver onde se tocavam. A regra
nova da Puglia diz como se escreve «de onde veio o nome da praga» e «de onde veio o lugar»; o leitor
de boletins já fazia isso, mas com o seu próprio dicionário. Agora usa o dicionário da regra, e é a
regra que dá a última palavra. O leitor de estudos escrevia uma palavra que a regra não conhece —
corrigido. O motor novo esperava a «janela» num sítio onde a Sala já não a guarda — passou a lê-la
onde está. Nada do que o dono respondeu à mão foi mudado; onde o código não batia, mudou o código.
