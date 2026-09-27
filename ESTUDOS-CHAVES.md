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

## Testes, mutação, mapa

(preenchido abaixo)

## EM PALAVRAS SIMPLES

(preenchido abaixo)
