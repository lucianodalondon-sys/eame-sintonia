# ESTUDOS-CHAVES — cultura, praga e lugar do estudo nos estudos T5

- **Ramo:** `claude/extract-study-metadata-x1m3tv`, a partir de `1ef772c0`.
- **Sem rede. Sem banco.** A Sala real não foi tocada; os 100 estudos reais **não estão** no repositório.

## O problema medido (pelo coordenador, na Sala real)

Os 100 estudos T5 (`EU-T5-001`, OpenAlex) tinham a `janela_declarada` com CULTURA, PROBLEMA, FASE e
REGIAO_DO_FATO = NÃO SEI em 100/100. A causa, lida no código: fora da régua T1, a porta só lia a cultura
no **título** e com o vocabulário **italiano** (`admissao._cultura_fora_da_regua`). Um resumo científico
escreve «grapevine», «Plasmopara viticola», «olive».

## O que foi feito

| # | O quê | Onde |
|---|---|---|
| 1 | Extrator determinístico de CULTURA, PROBLEMA e LUGAR DO ESTUDO no título+resumo (en/it) | `leis/estudo_chaves.py` |
| 2 | Ligado à porta: `janela_declarada()` usa-o **só no universo T5** | `admissao/admissao.py` (`UNIVERSOS_DE_ESTUDO`, `_estudo_de`, `janela_declarada`) |
| 3 | O olivo e as duas pragas dele entram **no léxico T6 que já existe** | `coleta/pesquisadores_t6.py` (`CULTURAS['olivo']`, `PROBLEMAS["mosca dell'olivo"]`, `PROBLEMAS['xylella']`) |
| 4 | Script de reprocesso: devolve as revisões, **não grava** | `admissao/reprocessar_estudos_chaves.py` |
| 5 | Fixtures SINTÉTICAS (17 títulos/resumos inventados e marcados) | `tests/fixtures/estudos_chaves/ESTUDOS-SINTETICOS.json` |
| 6 | Testes (28) | `tests/test_estudo_chaves.py` |
| 7 | Mutação (13 defeitos plantados) | `provas/estudos_chaves/mutacao_estudos_chaves.py` → `MUTACAO-ESTUDOS-CHAVES.json` |

**Sem segundo vocabulário.** `leis/estudo_chaves.py` não escreve nome de cultura, praga ou lugar: compõe o
léxico T6 (`pesquisadores_t6.CULTURAS/PROBLEMAS/REGIOES_EN/EXONIMOS/ZONAS_IT`), o vocabulário de pragas
(`leis/boletim_do_campo.py`, nome por `MESMO_PROBLEMA`), a régua T1 (`admissao.CULTURA_OBRIGATORIA[_EN]`)
e o gazetteer (`leis/fato_local.py`). Há teste que reprova se aparecer forma sem dono, ou nome de praga
escrito no código do extrator. O que faltava (*Olea europaea*, *olive fly*) entrou no léxico T6, declarado.

## As leis, e onde estão provadas

- **D112 · ENTITY_SOURCE = SPAN.** Cada valor traz `SPANS` com o trecho **literal** (`texto[INICIO:FIM]`,
  maiúsculas e acentos da fonte) e `BASE` = os trechos. Sem trecho, não há valor.
- **Ambíguo = NÃO SEI.** As formas que os donos já declararam ambíguas («vite» = vidas, «mais», «pero»,
  «mora», «vine») sozinhas não dão cultura; ficam em `AMBIGUAS`. Contam só se a mesma cultura tiver outra
  forma sem ambiguidade. Província homônima de palavra comum («Potenza», «Prato», «Latina», «Lodi»,
  «Fermo», «Cuneo») só conta depois de «provincia di / province of».
- **Lugar do estudo** só quando a frase diz que algo foi feito ali: verbo/nome de experimento na mesma
  frase («trials», «conducted», «samples were collected», «prove sperimentali», «condotte») **e** o lugar
  logo depois de uma preposição («in Tuscany», «field trials in Apulia and Sicily», «in the province of
  Lecce»). «Xylella is widespread in Apulia» e «has become established in Apulia» (linguagem de
  incidência) ficam NÃO SEI; «established», «located» e «raccolta» sozinha **não** são pista de ensaio.
- **Afiliação nunca vira lugar (INT-LAW-102).** «University of Florence», «conducted at the University
  of Naples» → recusado, com o motivo em `RECUSADOS`.
- **CAP-SCI.** O PROBLEMA do estudo sai `ESTADO = NOMEADO_NO_ESTUDO` (nunca PRESENTE); o lugar sai
  `KIND = LOCAL_DO_ESTUDO`; `ORIGEM.CAP_SCI.E_INCIDENCIA_DE_CAMPO = NAO`. `fact_location` declarado
  continua a mandar; FACT_TIME e FACT_LOCATION não são escritos.
- **Publicação ≠ período.** Com `published_at` declarado, a JANELA continua NÃO SEI; FASE também (fora do pedido).

## O comando exato (o coordenador corre localmente)

A entrada é JSON: lista (ou `{"ITENS": [...]}`) de `{"item_id", "texto", "published_at"}`; opcionais
`run_id`, `ordem`, `fact_location`, `fact_time`, e `janela_declarada` (a atual: igual = não repete).

```
py admissao/reprocessar_estudos_chaves.py --entrada C:/Users/London1/sintonia-sala-italia/estudos-chaves/estudos-t5.json --saida C:/Users/London1/sintonia-sala-italia/estudos-chaves/revisoes.json
```

Devolve `GRAVOU_NO_BANCO: false`, a `VERSAO_DO_EXTRATOR` (sha256 do código), a CONTA e, por item, as
revisões no formato de `sala_de_espera.rever(RUN_ID, ORDEM, REVISOES, extrator, versao, motivo)` —
campo `janela_declarada`, JSON com chaves ordenadas. Aplicar é passo do coordenador, na Sala canônica.

**Nas fixtures sintéticas** (17): 14 com cultura, 15 com problema, 9 com lugar do estudo, 1 só com forma
ambígua. **Nos 100 reais: NÃO SEI** — não estão aqui; o número sai da corrida do coordenador.

## Testes — bateria INTEIRA por nome, base `1ef772c0` × ramo `99ca6190`

Executor: `provas/integra_noite/bateria_inteira_por_nome.py` (o do LOTE4-FINAL), cada lado na sua worktree.

| | base `1ef772c0` | ramo `99ca6190` |
|---|---|---|
| ficheiros de teste | 393 | 394 (+ `tests/test_estudo_chaves.py`) |
| testes corridos | 7.373 | 7.401 |
| ficheiros vermelhos | 77 | 77 |
| falhas por nome | 338 | 337 |

**336 herdadas · 2 somem · 1 muda de texto:**

- `tests/test_estudo_chaves.py`: **28/28 OK**. Vizinhos que tocam a janela, a régua e o T6 (`test_quatro_chaves*`,
  `test_periodo_e_chaves`, `test_boletim_do_campo`, `test_extrator_evento_v2`, `test_pesquisadores_t6`,
  `test_t6_para_sala`, `test_a_linhagem_do_ready`, `test_os_consertos_da_intelligence`): todos OK.
- `system-map/tests/test_cadeia_declara_io.py::toda_leitura_real_e_explicada_por_uma_entrada_declarada` —
  **já falha na base** (declarada instável no LOTE4-FINAL). ⚠️ **No ramo a lista ganha 1 órfã que é MINHA:**
  `('CENSO_DAS_ESTRADAS_IT', 'leis/estudo_chaves.py')`. O censo segue os imports de `admissao/admissao.py` a
  dois saltos e passa a ler o extrator — a **mesma classe** de `leis/boletim_do_campo.py` e `leis/fato_local.py`,
  órfãs herdadas. Tentei declará-la em `CADEIA-DO-MAPA.json` (entrada nomeada): a órfã some, mas nasce outra
  reprovação (`a_AST_confirma_todo_caminho_declarado`: o caminho tem de estar escrito no script do censo).
  **Revertido.** Não há hoje forma de declarar uma leitura seguida por import; esconder o import para o
  censo não o ver seria pior. **Decisão do dono** (ou de quem for dono do censo): ensinar a cadeia a declarar
  leituras por import, e as três órfãs `leis/` saem juntas.
- Somem: `test_M5_o_ponto_fixo…` (o mapa do ramo foi regerado) e a outra redação da mesma prova instável acima.

## Mutação — 13/13 MORTOS (`provas/estudos_chaves/MUTACAO-ESTUDOS-CHAVES.json`)

Um defeito de cada vez; a cópia limpa passa antes; cada ficheiro reposto confere por sha256.

| mutante | teste que apanha |
|---|---|
| M01 afiliação volta a virar lugar | `test_afiliacao_nunca_vira_regiao…` |
| M02 forma ambígua («vite») dá cultura | `test_forma_ambigua_sozinha_nao_da_cultura` |
| M03 trecho deixa de ser literal (D112) | `test_o_trecho_guarda_maiusculas_e_acentos_da_fonte` |
| M04 lugar sem verbo de experimento | `test_nomear_um_lugar_nao_e_dizer_onde…` |
| M05 praga do estudo vira PRESENTE (CAP-SCI) | `test_problema_e_nomeado_nunca_presente` |
| M06 «Potenza» sem «provincia di» | `test_lugar_homonimo_so_depois_de_provincia_di` |
| M07 um trecho vira duas entidades | `test_um_trecho_uma_entidade` |
| M08 lugar do estudo por cima de `fact_location` | `test_fact_location_declarado_continua_a_mandar` |
| M09 extrator lê universos que não são estudo | `test_fora_de_t5_a_janela_nao_usa_o_extrator_de_estudo` |
| M10 em T5 volta a leitura antiga do título | `test_revisoes_no_formato_de_rever` |
| M11 reprocesso repete revisão | `test_mesmo_codigo_duas_vezes_nao_repete` |
| M12 *Olea europaea* sai do léxico T6 | `test_nomes_cientificos_comuns_ingles_e_italiano` |
| M13 «established/located» voltam a ser pista | `test_linguagem_de_incidencia_nao_e_lugar_do_estudo` |

Os testes acharam **dois defeitos meus** antes do commit final, ambos consertados: (1) em T5, com a cultura
ambígua, a leitura antiga do título reintroduzia «vite» de «salvare vite»; (2) «established in Apulia»
(linguagem de incidência) virava lugar do estudo.

## Mapa

`correr_a_cadeia.py REGERAR` → `CADEIA=OK` · `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`** · commit dos gerados ·
`impressao_da_arvore.py --conferir-carimbo` → **`IGUAL`**. Peças: `leis/estudo_chaves.py` e este relatório em
`C-LUGAR-COLETA`; `admissao/reprocessar_estudos_chaves.py` em `C-SALA-DE-ESPERA`; a mutação em `C-PROVA-COLETA`.
Não recarimbei (`--stamp`): as peças tocadas ficam 🟡 até alguém reler.

## Limites

1. **Os 100 reais não foram medidos aqui** (não estão no repo). Quantos saem de NÃO SEI: NÃO SEI até a corrida.
2. Cultura/praga = **NOMEADAS** no título/resumo, não provadas como testadas (a mesma lei da molécula no T6).
3. «vite» sozinha num resumo italiano fica NÃO SEI (preço declarado da ambiguidade).
4. Lugar só na Itália (o gazetteer); estudo em Espanha fica NÃO SEI, nunca Itália.
5. FASE continua NÃO SEI nos estudos (fora do pedido); a JANELA também (só `fact_time`).
6. O léxico T6 ganhou `olivo`, `mosca dell'olivo`, `xylella`: o campo T6 de uma próxima corrida do
   `pesquisadores_t6` pode nomear mais culturas/pragas; `PARES` (as 12 consultas) não mudou.

## EM PALAVRAS SIMPLES

Os 100 estudos científicos estavam na Sala sem dizer de que planta, de que praga e de onde falavam. Agora
um leitor olha o título e o resumo e escreve, com a frase exata copiada do texto: «videira», «míldio»,
«Puglia». Se a palavra for duvidosa, diz «não sei». Se o lugar for só a universidade do autor, não conta.
E um estudo nunca vira «a praga apareceu no campo». Para os 100 reais, o coordenador corre um comando
no computador dele; o comando devolve as correções prontas e não mexe no banco sozinho.
