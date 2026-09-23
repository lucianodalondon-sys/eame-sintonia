# RELATÓRIO V1A — A V1 LIGADA: O INDEX_URL DO CONTRATO É CAPA, SÓ COM A RÉGUA A MANDAR

Branch `v1-ligada` = `origin/unificacao-v1` + merge de `origin/receitas-gabaritos-v1` (K1, 5b0c599a).
Sem rede. Nada na Sala. Nenhum serviço vivo tocado. Collection não corrida.

## 1 — O merge

Quatro conflitos reais, resolvidos por significado (commit bfb99224):

| ficheiro | resolução |
|---|---|
| `SINTONIA-EAME-KNOW-HOW.md` | ficam os dois lados; o §192 da K1 colidia com o §192 da unificação (RECOLLECTION-R1) e foi **renumerado §196** |
| `scripts/desbloqueio/aplicar_desbloqueio.py` | fica a lista V1..V4 (a V4 é o aditamento da K1) |
| `system-map/data/architecture.declared.json` | `why_here` da C-DETECTOR-CAPA-GABARITO = dívida Node + texto unido |
| gerados (mapa, censo) | lado da unificação; refeitos pela cadeia |

## 2 — Onde a V1 vive, e quem a chama

A regra está num sítio só por linguagem:

- `curadoria/retrato_html.py::veredito(retrato, *, url, contrato, regua_a_mandar)`
- `coleta/retrato_html.mjs::veredito(retrato, contrato, { url, reguaAMandar })` — enxertado de
  `origin/aquisicao-detalhe-v1` (f98f234c), onde vivia sozinho

CAPA só quando as três coisas acontecem ao mesmo tempo: a página é o `INDEX_URL` do contrato
(mesma normalização da régua: sem barra final, minúsculas), o contrato é `HTML_LINK_DISCOVERY`
e a fonte passa os 4 passos (`ready_split.regua_manda` → `regua_de == DETAIL/v1`). Em qualquer
outro caso fica o veredito do detector.

O portão (`gate_capa_nao_e_materia` / `gateCapaNaoEMateria`) passou a **exigir** `url` e a régua
por nome. Um chamador que se esqueça rebenta com TypeError; não julga calado.

**CHAMADORES_MUDADOS**

| chamador | o que passa |
|---|---|
| `admissao/admissao.py::_e_materia` (a pergunta `materia` da porta) | `url_da_pagina` do item, contrato e régua do dono; `VERSAO_DA_REGRA` 6→7 |
| `curadoria/canario.py::canario_html` | a morada do item aberto; `_regua_manda(SOURCE_ID)` |
| `medidas/canario_rotas_elegiveis.py` | idem |
| `medidas/micro_colheita.py` | idem |
| `curadoria/test_retrato_html.py`, `tests/test_politica_nao_sei.py` | `url=None, regua_a_mandar=False` (o comportamento que já provavam) |
| Node nesta árvore | nenhum chamador de `gateCapaNaoEMateria` fora do próprio ficheiro |
| Node **fora** desta árvore | `coleta/italy_pilot_collect.mjs` e `curadoria/canario_do_motor.mjs`, em `aquisicao-detalhe-v1`: **não mudados**; ao juntar, o `add/add` do `.mjs` conflitua e a chamada sem `{ url, reguaAMandar }` levanta |

Leitores do retrato que **não** são o portão, e ficam como estavam: `provar_listagem.py` (prova
uma listagem candidata, antes de haver contrato), `politica_nao_sei.py` (recebe o veredito já
julgado), `ready_split.passos_da_promocao` (lê o item guardado na evidência do canário).

**O dado que faltava.** A porta não sabia de que endereço vinha a página. `raw_asset.source_url`
já existia e era lido; passou a viajar: `preservar_coleta.observacoes_confirmadas` →
`ingresso.unidades_para_a_derivacao` → `derivacao_forward.correr` → `orquestrador.pela_estruturacao`
→ `item_documental_para_a_porta` (`url_da_pagina`). Efeito lateral declarado:
`orquestrador` já passava `r.get("SOURCE_URL")` a `preservar_documento`, que recebia `None`;
agora `documento_estruturado.source_url` passa a ser escrito nas linhas novas. Não é identidade
do documento (`NAO_SAO_IDENTIDADE_DE_DOCUMENTO`) e o reencontro compara só `hash_texto` e `source_id`.

## 3 — A medição com o código real

`medidas/medir_v1a.py` passa cada página pelo caminho de produção: `executor_texto_de_html._retrato`
→ `item_documental_para_a_porta` → `admissao._e_materia`. O estado das fontes é o da K1 «depois
das receitas», numa cópia (pós-B2 + contratos G1 V1..V4 + promoções do canário K1). O script
confere que a cópia dá as mesmas 25 fontes bem configuradas que a K1, e pára se não der.
Decisões humanas da quarentena ficam de fora (mede-se a regra).

| conjunto | capas que entram (V1 desligada → ligada) | notícias barradas | notícias retidas |
|---|---|---|---|
| original (109 capas / 37 notícias) | 37 → **30** | 6 → 6 | 8 → 8 |
| controlo desenvolvimento (31 / 15) | 6 → **5** | 4 → 4 | 1 → 1 |
| **controlo cego** (18 / 5) | 4 → **3** | 0 → 0 | 0 → 0 |

Reproduz a simulação da K1 número a número. A V1 disparou em 17 páginas: todas capas verdadeiras,
todas de fontes que passam os 4 passos (11 original, 5 desenvolvimento, 1 cego).

## 4 — Paridade Python / Node

`tests/test_v1a_v1_ligada.py::ParidadePythonNode` corre as 251 páginas reais dos dois gabaritos
+ 6 sintéticas, em 4 contextos (índice com régua, índice sem régua, outra página, sem endereço):

- veredito e «o gate reprova?» **iguais em todas**, e a V1 disparou dentro do teste;
- V1 e gate alimentados com o mesmo retrato dão o mesmo texto;
- ⚠️ **dívida anterior à V1, declarada:** em 8 das 251 páginas os dois detectores **contam**
  caracteres diferente. Causas medidas: em 6 o Node conta unidades UTF-16 (um emoji vale 2);
  em 1 o `\s` do JavaScript apanha U+FEFF; em 1 (IT-T2-049) a causa é **NÃO SEI**. O veredito
  é igual nas 8. Uma delas (IT-T12-030) está a 39,6 caracteres por ligação, com o limiar nos 40.
  Não se corrigiu: mudar a contagem é mudar o detector, e isso mede-se nos gabaritos antes.
  O teste falha se aparecer uma página nova na lista.

## 5 — Testes e mutação

`tests/test_v1a_v1_ligada.py`: 26 testes. Mutação (`medidas/mutacao_v1a.py`, sem bytecode,
restauro byte a byte): **11/11 mortos**, entre eles «V1 desligada» e «V1 aplicada a fonte que
não passa os 4 passos», em Python e em Node. Na primeira volta sobreviveu 1 («a porta dá a
régua por mandar sempre»): havia duas travas para a mesma coisa. Tirou-se a repetida, e o
ataque seguinte matou 11 de 11.

### A suíte completa, comparada por NOME

Base = bfb99224 (unificação + K1): 5139 testes, **286 vermelhos** (suíte inteira num processo).
V1A = c02a6882, corrida ficheiro a ficheiro (a máquina tinha 4,7 GB livres de 32; a suíte
inteira foi morta por falta de memória): **214/214 ficheiros** com resultado.

| grupo | n | prova |
|---|---|---|
| **NEW_RED_BY_NAME (da V1A)** | **2 → corrigidos** (074f0f98) | `test_raw_observation_id_volta` (a projecção conferida ganhou `SOURCE_URL`); `test_politica_nao_sei` (`medir_v1a.py` citava `politica_nao_sei` num comentário e o teste contava-o como chamador) |
| herdados, na lista da base | 281 | o mesmo nome na base |
| herdados só por correr ficheiro a ficheiro | 27 | cada ficheiro corrido sozinho NA BASE dá os mesmos nomes: `No module named 'yaml'` (20 `test_c10_*`/`test_fase_italiana_no_workflow`, 2 `test_preflight_de_egresso`, 1 `test_security_ratchet`) e 4 `test_metricas` (a contagem de testes não se mede sem o yaml) — na suíte inteira outro teste empresta o yaml |
| 10 de `test_o_controle_separa_lei_de_mencao` | 0 | transitórios: na 1.ª volta o censo filho saiu com erro e a mensagem perdeu-se (o pai lê cp1252, o filho escreve UTF-8); na 2.ª volta a V1A dá os mesmos 2 vermelhos da base (B0, M5), por nome. O S1 isolado passa. Causa da 1.ª falha: NÃO SEI ao certo — coincidiu com a pressão de memória |

`test_v21_*` (4 ficheiros) correm 0 testes em unittest na base e na V1A: são funções ao estilo pytest.

## 6 — Writeset (para a M5D reconciliar)

```
admissao/admissao.py · coleta/derivacao_forward.py · coleta/ingresso.py · coleta/retrato_html.mjs (novo)
curadoria/canario.py · curadoria/ready_split.py · curadoria/retrato_html.py · curadoria/test_retrato_html.py
curadoria/V1A-MEDICAO-V1.json (novo) · guarda/preservar_coleta.py · medidas/canario_rotas_elegiveis.py
medidas/micro_colheita.py · medidas/medir_v1a.py (novo) · medidas/mutacao_v1a.py (novo)
orquestrador/orquestrador.py · tests/test_politica_nao_sei.py · tests/test_quarentena_naosei.py
tests/test_v1a_v1_ligada.py (novo) · tests/test_raw_observation_id_volta.py · SINTONIA-EAME-KNOW-HOW.md (§196 renumerado, §197 — na UNIFICACAO-V1-F passaram a §203 e §204)
RELATORIO-V1A-V1-LIGADA.md · system-map/data/architecture.declared.json · gerados do mapa
+ tudo o que o merge da K1 trouxe (bfb99224)
```

## 7 — O que fica em aberto

- A V1 só manda onde a régua manda, e nos livros vivos de hoje a maioria das fontes dos
  gabaritos nem tem contrato (K1: 105/133). O ganho medido é o do estado pós-B2 + receitas.
- O G1 muda `LINK_PATTERN`/`INDEX_URL` no livro **sem** carimbar `ROUTE_PROVENANCE.INTEGRADO_EM`.
  A régua lê esse carimbo para dizer «contrato mudado depois da promoção»: sem ele, uma fonte
  continua DETAIL/v1 com a prova da rota antiga, e a V1 compararia a página com o índice NOVO.
  A medição fez o carimbo na cópia; no pacote real **não foi mudado** (é do G1/cutover).
- Os 2 chamadores Node em `aquisicao-detalhe-v1` e a dívida de contagem (secção 4).
