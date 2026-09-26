# PESQUISADORES-T6 — alimentar a Intelligence Scientifica (D84, ferramenta n.º 2)

- **Ramo:** `pesquisadores-t6-v1`, a partir do vivo `69b0e23f`. **Nada instalado.**
- **Sem rede.** Os testes trocam o transporte por um que falha se for chamado.
- **Não tocado:** o vivo, os contratos e a fila de candidatas.
- **A Sala não foi lida de novo.** Usei o export só-leitura que já estava gravado
  (`casco/SALA-EXPORT-LEITURA.json`, 26/09 05:39 −03, sha256 `aa8d64a6…`). Ele confirma o ponto de partida:
  - 94 itens: **51 T5**, **0 T6**;
  - **DOI no texto em 2 de 51**, de 31 fontes T5.

## 1 · O que já existe (medido no repositório)

| Peça | O que faz | O que devolve | Serve? |
|---|---|---|---|
| `coleta/corpus_pesquisador.py` | **É a receita T6 do orquestrador** (`pedido/receitas.py`). Lê OpenAlex `/works?author.id=` e ORCID `/works` + `/researcher-urls` | Catálogo `LEGADO` de **12 pessoas fechadas** (4 italianas). **Não atravessa a Admissão** | **Reaproveitado**: o transporte `_get` (nunca levanta: falha ≠ zero), a busca por palavra inteira, o resumo, e a lei «ORCID do índice não é prova» |
| `coleta/universo_ciencia_it.py` | OpenAlex por recorte (5 recortes; 02/09) | Autores por recorrência; **não guarda o DOI por trabalho**; até 12 páginas por recorte | A ideia do filtro `institutions.country_code:it` e a pausa de 3 s |
| `provas/a_rota_gratuita_ainda_e_gratuita.py` + `system-map/data/capacidade-openalex.generated.json` | Mede se o OpenAlex ainda é grátis | 14/09 (outra sessão): 17 pedidos com **HTTP 200 e corpo «Insufficient budget»**. Estado: **NÃO SEI** | Sim: o módulo novo trata esse corpo como **falha**, não como 0 trabalhos |
| `superficie/rede.py` | Checa se os hosts respondem (inclui `api.crossref.org`) | — | Não é coletor |
| Atlas: **IT-T6-001..036** | 36 pesquisadores italianos, registo ORCID, com cultura e problema | **0 com contrato** | São fontes T6 já registadas. O módulo não cria outra para quem já está lá |
| Respostas reais gravadas: `C:/sc-hot/data/raw/RESEARCHER-CORPUS/` | 12 OpenAlex + 24 ORCID, **18/09 18:25–18:27** (−03), **nesta máquina** | Trabalhos reais com DOI | Viraram o material do ensaio offline |

**Porque a Sala tem 0 T6:** dois buracos, os dois medidos.
- **(a) O QUALIFY nunca dava T6.**
  - `atribuir_source_id.territorio_de` não tinha regra para T6.
  - «Andrea Lentini — ORCID (Università di Sassari)» saía **T5**, pela palavra «Università».
  - Sem instituição no nome, saía **NÃO SEI**.
  - Rodei a função sobre 4 fichas: T5, NÃO SEI, NÃO SEI, NÃO SEI.
- **(b) A receita T6 do orquestrador aponta para um catálogo `LEGADO`, que não passa pela Admissão.**

## 2 · As consultas (cultura × problema, só o que ataca aquela cultura)

As 12 consultas são **uma por par**, todas ao OpenAlex `/works`. Cada uma leva:
- o filtro `institutions.country_code:it`: pelo menos um **autor** com afiliação italiana. Isto escolhe a PESSOA, não o lugar do estudo;
- o filtro `from_publication_date:2019-01-01`;
- `per-page=200`, ordem pela data de publicação, e só os campos de que a unidade precisa (`select=`).

| Cultura | Problemas |
|---|---|
| vite | peronospora (*Plasmopara viticola*) · oidio (*Erysiphe necator*) · botrite · tignoletta (*Lobesia botrana*) · scafoideo (*Scaphoideus titanus* / flavescência dourada) |
| melo | oidio (*Podosphaera leucotricha*) · carpocapsa (*Cydia pomonella*) |
| mais | piralide (*Ostrinia nubilalis*) · diabrotica (*D. virgifera*) |
| pomodoro | peronospora (*Phytophthora infestans*) · botrite · oidio (*Leveillula taurica* / *Oidium neolycopersici*) |

- As buscas exatas estão em `data/derivados/PESQUISADORES-T6/PLANO.json`.
- **O par da consulta não passa para o trabalho.** A cultura e o problema do trabalho só existem se o
  título ou o resumo os nomearem, e o termo que os sustentou fica gravado.

## 3 · O contrato T6 (`docs/fontes/CONTRATO-FONTE-T6-PESQUISADOR-V1.json`, PROPOSTA)

**A fonte é o PESQUISADOR** (`https://orcid.org/<iD>`). **A unidade é o TRABALHO** (1 por obra).

| Campo | Regra |
|---|---|
| `DOI` | Do registo da obra. O Crossref confirma quando o devolve |
| `TRIAL_ID` / `DATASET_ID` | Só se estiver **escrito** (ID de ensaio; DOI Zenodo/Dryad/figshare; ou o próprio trabalho ser um dataset). Senão, NÃO SEI |
| `RESEARCHER_ID/ORCID` | Por autor, com a **escada da prova** (abaixo) |
| Instituição | A declarada **nesta obra**, por autor. É do AUTOR |
| Cultura, problema | Só se **nomeados** no texto |
| Molécula | Só os **122 ativos** de `referencia/adama/ACTIVE-INGREDIENTS.json`. Qualquer outra fica NÃO SEI, e não «nenhuma» |
| `LOCAL_DO_ESTUDO_ESCRITO` | Região italiana ou Itália **nomeada** no texto, com o termo. **Nunca a afiliação** |
| `PERIODO_DO_ESTUDO` | Anos escritos no resumo e presos ao ensaio («during 2021–2022»). **Década e publicação não contam** |

**A escada da prova da pessoa, da mais forte para a mais fraca:**
1. `ORCID_AUTODECLARADO`: o DOI está no `/works` do próprio ORCID.
2. `ORCID_NO_DEPOSITO_AUTENTICADO`: o Crossref diz que o editor depositou o ORCID e que a pessoa o autenticou.
3. `ORCID_NO_DEPOSITO_DO_EDITOR`: o Crossref diz que o editor depositou o ORCID.
4. `ORCID_LIDO_SEM_ESTE_DOI`: o ORCID foi lido e não declara esta obra.
5. `SO_INDICE`: só o OpenAlex. **Não é prova**, porque o OpenAlex copia o ORCID do perfil para todas as obras.

**Repetidos:**
- **Mesma obra = uma unidade**, com todas as consultas que a trouxeram.
- **Mesmo ensaio provado** (o mesmo `TRIAL_ID` ou `DATASET_ID`) forma um grupo `ENSAIO_PROVADO`.
- **Mesmo título + um autor em comum, com DOI diferente** (preprint e artigo) forma um grupo
  `PROVAVEL_MESMA_OBRA`, para alguém rever. **Nada é apagado nem fundido.**

**Pessoas:** a ordem é **alfabética**. Não há nota nem ranking.

### O caminho canónico, degrau a degrau

| Degrau | Estado |
|---|---|
| 1 · candidata (`candidatas/fonte_nova.registar`, tipo `CIENCIA`) | **PRONTO NO RAMO.** `fichas_candidatas()` prepara os argumentos e **não grava**. PAÍS=IT pela afiliação escrita no trabalho, com a prova na NOTA. Quem já está no Atlas sai com o número que tem (`JA_E_FONTE`) |
| 2 · QUALIFY | **CONSERTADO NO RAMO, não instalado.** `orcid.org/<iD>` passa a dar **T6**, antes de «universit». Hoje nenhuma candidata tem endereço ORCID (0 na fila), por isso **nada do que já existe muda de gaveta** |
| 3 · BUILD_CONTRACT | **FALTA.** O worker só tem molde para HTML, e ORCID/OpenAlex são APIs JSON. A fonte pararia em CAPABILITY. **Decisão do dono:** molde novo, ou contrato escrito pela porta de reparo, como na T1 |
| 4 · canário → READY → coletor | **FALTA**, porque depende do degrau 3 |
| 5 · receita T6 → Admissão → Sala | **FALTA.** A receita aponta para o catálogo `LEGADO`. Trocá-la é política de coleta: **decisão do dono** (cutover) |

## 4 · O ensaio offline (respostas gravadas, **zero pedidos**)

**O material do ensaio** está em `tests/fixtures/pesquisadores_t6/`, e o sha256 dos originais está no
`MANIFEST.json`. O `montar.py` refaz tudo.
- São respostas **reais** de 18/09 de 4 pesquisadores de instituições italianas: Quaglino (Milão), Mori
  (Verona), Blandino (Turim) e Logrieco (ISPA).
- Mais **1 controlo negativo**: Delmotte, do INRAE. Tem trabalhos de videira × peronóspora e **nenhum
  autor italiano**.
- ⚠️ **Essas respostas foram pedidas POR AUTOR, não pela consulta nova.** A consulta nova nunca foi
  gravada. O ensaio simula o filtro dela: o par tem de estar no texto e tem de haver um autor com
  afiliação IT.

**Resultado** (`data/derivados/PESQUISADORES-T6/ENSAIO-OFFLINE.json`):
- **24 encontros trabalho × par → 21 trabalhos** depois de tirar os repetidos. 1 grupo ficou
  `PROVAVEL_MESMA_OBRA`: o preprint e o artigo do *mating-type locus* da *Plasmopara*.
- **Por par:** vite×scafoideo 11 · vite×peronospora 5 · vite×botrite 2 · pomodoro×botrite 2 · mais×piralide
  1 · mais×diabrotica 1. Os outros 6 pares deram 0, porque estes 5 pesquisadores não trabalham neles.
  **Isto não mede o universo.**
- **Campos preenchidos, em 21:**
  - DOI 21 · cultura 21 · problema 21;
  - local do estudo escrito 12 · período do estudo 2;
  - molécula **1** (deltametrina);
  - TRIAL_ID **0** · DATASET_ID **0**.
- **Pessoas:** 78 com afiliação italiana em algum trabalho; o controlo francês **não entra**.
- **Prova da pessoa** (autores italianos): `SO_INDICE` 103 · `ORCID_AUTODECLARADO` 14 · `ORCID_LIDO_SEM_ESTE_DOI` 5.
- **Candidatas T6 propostas: 59.** Ficam de fora 19 pessoas com o par no texto mas sem ORCID, porque
  sem ORCID não há endereço de fonte. **0** já estavam no Atlas.

**Lido à mão (os 21):**
- **1 erro achado e consertado:** «In the 1990s» (a história da doença) virava período 1990. Agora uma década não conta, e há teste para isso.
- **Conferidos:**
  - o levantamento na Geórgia fica sem local, porque não é a Itália;
  - o acetamiprido fica sem molécula, porque não está nos 122 ativos ADAMA (limite declarado);
  - a Toscana e o Piemonte vêm do texto, com o termo.

**Testes:** 24 em `tests/test_pesquisadores_t6.py`, todos OK e sem rede.
- **Prova de mutação:** estraguei o código de 6 maneiras, uma de cada vez, e **os testes pegaram os 6 estragos**. Os estragos foram:
  - tirar o filtro de autor italiano;
  - tirar a verificação de afiliação;
  - tirar a regra da década;
  - tirar a regra ORCID→T6;
  - teto 6 em vez de 5;
  - não parar no corpo de erro.
- **Testes do curador que passam pelo QUALIFY** (d21_heranca, decisao_semantica, soc2_curator_youtube,
  gatilho_discovery, ponte_candidatas): **92 OK**.

## 5 · Pedidos por domínio (teto 5 por domínio por rodada, contado antes de pedir)

| Domínio | Pedidos | Rodadas | Papel |
|---|---|---|---|
| `api.openalex.org` | 12 (1 por par, 1.ª página) | **3** (5 + 5 + 2) | **Obrigatório** |
| `api.crossref.org` | 1 por 40 DOI (os filtros `doi:` repetidos funcionam como «ou») | ⌈DOI ÷ 40 ÷ 5⌉ | Incremental: prova da obra |
| `pub.orcid.org` | 1 por pessoa (`/works`), por ordem alfabética | ⌈pessoas ÷ 5⌉ | Incremental: prova da pessoa |

- **No ensaio:** 21 DOI dariam 1 pedido ao Crossref, e 59 pessoas dariam 12 rodadas no ORCID.
- **Na rede real** cada par pode trazer até 200 trabalhos. A única medida que existe é de 02/09: flavescência
  com 135 trabalhos e milho×broca/diabrótica com 27. **Não sei quantos serão hoje.**
- **Sem Crossref nem ORCID, a unidade existe** com `SO_INDICE`, que o contrato diz que **não é prova**.
- Cada rodada faz os 3 domínios em paralelo, com **até 5 pedidos em cada um**. A regra está no código
  (`assert`), e o `ESTADO.json` guarda o que já foi feito, para a rodada seguinte continuar dali.

## 6 · O comando que TU corres na rede

```
cd C:/Users/London1/orca/workspaces/eame-sintonia/pesquisadores-t6     (ramo pesquisadores-t6-v1)
py coleta/pesquisadores_t6.py --rede --rodada=1 --saida=C:/Users/London1/sintonia-sala-italia/pesquisadores-t6/rede
py coleta/pesquisadores_t6.py --rede --rodada=2 --saida=C:/Users/London1/sintonia-sala-italia/pesquisadores-t6/rede
py coleta/pesquisadores_t6.py --rede --rodada=3 --saida=C:/Users/London1/sintonia-sala-italia/pesquisadores-t6/rede
```

**O que cada rodada faz:**
- até **5 + 5 + 5** pedidos, com 3 s entre eles;
- guarda cada resposta tal como veio, com o sha256 em `RODADA-<n>.json`;
- escreve `UNIDADES-T6.json` (trabalhos, grupos, pessoas e as fichas de candidata propostas).
- **Não escreve** na fila, no Atlas, nos contratos nem na Sala.

**Quando algo corre mal:**
- **Se o OpenAlex responder «Insufficient budget»**, esse domínio **pára** na rodada. A resposta fica
  guardada como `FALHA-r<n>-…` e o par fica por fazer.
- Com o OpenAlex parado nesse ponto, **Crossref e ORCID só trabalham sobre o que já tiver chegado**. Se
  nada chegou, não há DOI nem pessoas, e não fazem nenhum pedido. **Isto é NÃO SEI, não zero.**
- Se o dono tiver chave do OpenAlex, basta `OPENALEX_API_KEY=<chave>` no ambiente. É opcional.

**Para reler sem rede:** `py coleta/pesquisadores_t6.py --ler --saida=<a mesma pasta>`.

## Limites

1. **A capacidade do OpenAlex hoje é NÃO SEI.** A última resposta boa nesta máquina é de 18/09 18:27; a
   medida de 14/09, de outra sessão, disse «sem orçamento».
2. **A leitura do Crossref não foi provada com uma resposta real**, porque nenhuma foi gravada nesta casa.
   Os nomes dos campos vêm da documentação pública. O teste usa uma resposta **sintética**, marcada como tal.
3. **O ensaio mede o método, não o universo:** são 5 pessoas escolhidas antes, não o que as 12 consultas vão trazer.
4. **O local do estudo pára na região.** Província e comune ficam NÃO SEI: o gazetteer italiano é de outro dono.
5. **Molécula: só os 122 ativos ADAMA.** Molécula de concorrente fica NÃO SEI, como o acetamiprido no ensaio.
6. **TRIAL_ID** só é lido quando está escrito. No ensaio foram 0 de 21.
7. **Os degraus 3 a 5 do caminho canónico são decisões do dono.** Até lá, nada do que a rede trouxer chega à Sala.
8. **Mapa: não corrido** (o LOCK-PESADO está ocupado). É PRONTO-SEM-MAPA.

## Ficheiros

| Ficheiro | O que é |
|---|---|
| `coleta/pesquisadores_t6.py` | Consultas, teto, unidade, deduplicação, provas, fichas de candidata, rodada com rede, `--ler` |
| `curadoria/atribuir_source_id.py` | + a regra `orcid.org/<iD>` → T6 |
| `tests/test_pesquisadores_t6.py` | 24 testes |
| `tests/fixtures/pesquisadores_t6/` | As respostas gravadas (cortadas), o `MANIFEST.json` e o `montar.py` |
| `docs/fontes/CONTRATO-FONTE-T6-PESQUISADOR-V1.json` | O contrato (proposta) |
| `data/derivados/PESQUISADORES-T6/ENSAIO-OFFLINE.json` | O ensaio: 21 unidades, 78 pessoas, 59 fichas |
| `data/derivados/PESQUISADORES-T6/PLANO.json` | As 12 buscas e o plano |
