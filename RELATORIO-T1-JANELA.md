# RELATÓRIO · T1-JANELA — a régua T1 (CROP & PRODUCTION) para janelas de cultura (D29)

Branch `regua-t1-janela-v1`, a partir de `origin/regua-t2-v1` (= instalado, T2 D29 + T2C + EGR).
**NÃO instalado.**

## Em palavras simples

Antes, a porta não tinha regra nenhuma para T1: dizia «não se aplica» a tudo — os 45 boletins de
janela que medimos na T2 davam 45/45 «não se aplica» em T1. Agora T1 tem régua: diz SIM quando o
texto **nomeia uma cultura** (vinha, oliveira, macieira, tomate…) **e** traz **dois sinais de
momento** diferentes — fase da planta, estádio (floração, pintor…), limiar de intervenção, capturas
de praga, tratamento, colheita ou sementeira escritas em frase. Com menos do que isso fica «não sei»:
não entra e não é rejeitado. A porta só admite; quem decide a janela é a Intelligence.

## Números

| O quê | Resultado |
|---|---|
| Gabarito T1-V1 (lido à mão, 181 textos, regra de escolha fixa) | **55 YES / 80 NO / 46 NAO_SEI** |
| T1 antes | 181/181 `NAO_SE_APLICA` (não havia régua) |
| T1 agora, no gabarito (dentro da amostra) | **51/55 YES apanhados**, **2 falsos SIM** em 80 NO → precisão **0,962**, recall **0,927**; 0 YES viram NAO |
| — boletins por cultura (estrato 1) | 51/52, **0** falsos SIM |
| — notícias com colheita/sementeira (estrato 2, escolhido por palavra) | **0/3** apanhadas, **2** falsos SIM (uma publicação sobre inovação; a página-menu do Serviço Fitossanitário da Campania) |
| Outros universos (T2 T3 T4 T5 T7 T9 T10) antes/depois, 1.309 textos | **0 mudanças em 9.163 julgamentos** |
| T1 no acervo (1.309) | **57 SIM · 833 NAO_SEI · 419 NAO** (antes: tudo `NAO_SE_APLICA`) |
| Mutação numa cópia | **8/8 mortos** |

## ⚠️ Ressalvas

1. **Dentro da amostra**: as palavras foram escolhidas olhando para o gabarito. Os rótulos são meus
   (`VALIDADO_POR_HUMANO = NAO`).
2. **O gabarito é quase todo boletim**: 52 dos 55 YES são boletins por cultura. O acervo quase não
   tem notícias de campo; as 3 notícias de colheita que tem **não são apanhadas** (ficam NAO_SEI) — a
   régua pede dois momentos e elas só têm um («a colheita começou»). Afrouxar para um momento
   apanhava-as mas deixava entrar 8 páginas de serviço/campanhas (medido). Para T1 cobrir notícias de
   colheita é preciso um gabarito de notícias (rede) — não existe ainda.
3. **O que T1 NÃO cobre**: área, produção, rendimento, preço, previsão de safra (a outra metade do
   Atlas). Esta régua é só a parte «calendário/desenvolvimento» que a D29 pede.
4. Sobreposição com T2: quase todos os SIM de T1 são também SIM de T2 (os mesmos boletins). Não é
   erro — um boletim fala do tempo E da fase — mas a Sala pode receber o mesmo documento duas vezes,
   uma por universo (a Sala já tem a chave por universo, D2).
5. Inglês (culturas e momentos) escrito e **não medido**.
6. Consertei dois erros meus antes de medir: índices trocados na rotulagem do estrato 1; e um teste
   que usava «fioritura» + «invaiatura» como dois momentos (são o mesmo conceito).

## O que muda (writeset)

| Ficheiro | Muda |
|---|---|
| `admissao/admissao.py` | **único código de produção**: `PERGUNTAS_DO_UNIVERSO["T1"]` (7 momentos), `CULTURA_OBRIGATORIA`, ramo T1 em `_do_universo`, `PALAVRA_INTEIRA`/`TRANSVERSAIS = {"T2","T1"}`, `VERSAO_DA_REGRA = "9"` |
| `tests/test_regua_t1.py` (novo, 18) | o mecanismo |
| `tests/test_a_regra_de_t2.py` | T1 entra na lista de universos com régua (com a razão) |
| `tests/test_estagio_atravessa_a_fronteira.py` | o teste que usava T1 «sem régua» passa a T11 |
| `scripts/regua_t2/MEDICAO-REGUA-T2-V2/V3.json` | refeitas na versão 9: números iguais |
| `scripts/regua_t1/**`, este relatório, `system-map/data/architecture.declared.json` | evidência e mapa |

## Plano de instalação (o coordenador instala)

1. Juntar `regua-t1-janela-v1` na linha instalada (conflito esperado só nos `*.generated.json` →
   regerar pela cadeia).
2. `py -m unittest tests.test_regua_t1 tests.test_regua_t2 tests.test_a_regra_de_t2
   tests.test_o_canario_da_collection tests.test_egresso_consenso` (aqui: OK; o único erro nos
   testes tocados é o pré-existente `test_correr_julga_a_unidade_da_fronteira`).
3. `pacote/metricas_canonicas.py --sync` com o PyYAML emprestado (há testes novos).
4. Efeito esperado: pares (item, T1) deixam de sair `NAO_SE_APLICA`; no acervo 57 SIM / 833 NAO_SEI /
   419 NAO; 0 mudanças nos outros universos. Voltar atrás = reverter o merge (versão volta a 8).

## Provas fora do Git

Textos: `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\textos\`, derivados do armazém e do lote-76 —
sha256 de cada um em `scripts/regua_t1/SELECAO-T1-V1.json` e conferido pela medição
(`SHA_NAO_CONFERE = []`). Rótulos brutos copiados para `scripts/regua_t1/rotulos/`.

---

## T1B (24/09) — o aperto de «página de site» e a prova cega

### 1. O aperto da T2C aplicado a T1 — medido e **NÃO aplicado**

Pedido: tirar os 2 SIM errados com o mesmo aperto de página de site/menu da T2, reutilizando a
função, sem perder os 51 certos. **Não é possível com essa função** — medido
(`scripts/regua_t1/MEDICAO-APERTO-SITE-T1-V1.json`, lista `ANCORAS["T2"]["PAGINA_DE_SITE"]`
reutilizada, nenhuma cópia):

| Variante | Certos (de 55) | Errados (de 80) | Acervo 1.309 |
|---|---|---|---|
| atual | **51** | 2 | 57 SIM |
| A — lista da T2 inteira | 39 (perde 12) | 1 | 17 SIM → NAO_SEI |
| B — só página de site com o mínimo de 2 momentos | 50 (perde 1) | 1 | 5 SIM → NAO_SEI |

- **Porquê**: os boletins ARPAV «Agrometeo Informa» trazem um link `…/newsletter/bollettino-colture-erbacee`;
  na T2 isso não os afetava porque lá a lista só vale para a via `agrometeo`, e eles entram pela via
  forte. Em T1 a lista apanha-os.
- A variante B tira a página-menu da Campania mas tira também a página de monitorização da mosca da
  oliveira da Terre dell'Etruria (certa): troca um erro por uma perda.
- A publicação sobre inovação (PDF, 172 mil caracteres) **não tem marca de site**: nenhuma variante a
  tira.
- **A régua fica como estava** (51/55, 2 errados). Os 2 erros ficam declarados.

### 2. Prova CEGA (30 textos que a régua nunca viu)

Regra de escolha commitada **antes de olhar** (`selecionar_cega.py`): textos do acervo fora dos 181
do gabarito, com ≥ 400 caracteres (463 no total); 15 ao acaso entre os que nomeiam uma cultura (110),
15 ao acaso entre os restantes; semente 25092026. **Rótulos escritos e commitados ANTES de aplicar a
régua** (`rotulos/rotulos-cega.tsv`). Resultado (`PROVA-CEGA-T1-V1.json`):

| | Resultado |
|---|---|
| Rótulo (lido às cegas) | 0 YES · 29 NO · 1 NAO_SEI |
| Régua | **0 SIM** · 16 NAO_SEI · 14 NAO |
| Falsos SIM | **0 em 29 NO** (no gabarito: 2 em 80) — os erros às cegas **não foram maiores** |

⚠️ **Limite desta prova**: nenhum dos 30 era janela — o acervo fora do gabarito quase não tem
boletins (os que havia foram para o gabarito). Por isso a prova cega mede que a régua **não inventa**
janelas; **não mede se as encontra**. Para medir isso às cegas é preciso boletins novos pela rede
(a mesma missão de gabarito da rede que a notícia de campo pede).

## PLANO DE INSTALAÇÃO (atualizado — substitui o anterior)

Nada mudou no código de produção desde `c40394e8`: o aperto foi medido e não aplicado.

1. Juntar `regua-t1-janela-v1` na linha instalada (conflito esperado só nos `*.generated.json` →
   regerar pela cadeia).
2. `py -m unittest tests.test_regua_t1 tests.test_regua_t2 tests.test_a_regra_de_t2
   tests.test_o_canario_da_collection tests.test_egresso_consenso` (aqui: OK, fora o erro
   pré-existente `test_correr_julga_a_unidade_da_fronteira`).
3. `pacote/metricas_canonicas.py --sync` com o PyYAML emprestado.
4. Efeito: T1 57 SIM / 833 NAO_SEI / 419 NAO no acervo; 0 mudanças nos outros universos;
   `VERSAO_DA_REGRA = "9"`. Os 2 falsos SIM conhecidos entram (a publicação sobre inovação e a
   página-menu do Serviço Fitossanitário da Campania).
5. Voltar atrás = reverter o merge.

---

## T1C (25/09, D35) — produção juntada, prova cega de POSITIVOS, aperto que não perde certos

1. **Produção juntada**: `origin/servico-20260923-0923 @ 5ba9647e` (R1) entrou no ramo (merge
   `970ca6a3`); só os gerados do mapa tinham conflito — regerados pela cadeia. Testes T1 + T2 + EGR +
   `curadoria/test_revisao_ready` OK (o único erro nos tocados é o pré-existente
   `test_correr_julga_a_unidade_da_fronteira`; os 2 do PyYAML são da máquina).
2. **Prova cega de POSITIVOS pela rede** (`recolher_cega_positivos.py`, regra commitada antes;
   portão de consenso PASS IT antes de cada site; **25 pedidos, no máximo 5 por site**, robots lido):
   19 boletins NOVOS (edições/zonas que não estavam no acervo) de Campania SFR ×4, ARIF ×4, APOL ×4,
   ARPAV ×4, ARPAE ×3. **Rotulados ANTES de correr a régua**: 16 YES, 3 NO (ARPAE: só tempo).
   Régua T1: **16/16 SIM, 0 falsos SIM** (os 3 da ARPAE: NAO). ⚠️ Edições novas das MESMAS séries
   do gabarito (mesmos moldes).
3. **Aperto sem perder certos**: «o momento tem de estar no corpo» — abaixo de **2 ocorrências de
   momento por 10 mil caracteres** fica NAO_SEI (`MOMENTO_SO_DE_PASSAGEM`). Tira a publicação de
   172 mil caracteres (0,1/10k); o boletim certo menos denso tem 3,8/10k. Resultado:
   **51 certos continuam, falsos SIM 2 → 1**; no acervo só 3 mudam (a publicação e 2 capturas de
   um artigo sobre a pera Conference, já rotuladas NAO_SEI); **0/9.163** nos outros universos;
   prova cega continua 16/16. Mutação **9/9**. ⚠️ Limiar escolhido dentro da amostra.
   **Não deu** para a página-menu do Serviço Fitossanitário da Campania: o detector de capa diz
   MATERIA (47 links, 2.111 caracteres de parágrafo) e a régua só vê o texto (densidade 8,8/10k,
   igual a um boletim). Tirá-la pediria dar à régua a contagem de links do retrato HTML — outra
   mudança, não feita. **Fica 1 falso SIM conhecido.**

## PLANO DE INSTALAÇÃO (atualizado — substitui os anteriores)

- **SHA**: o último commit deste ramo (dito na entrega).
- **Writeset** (fora os gerados): `admissao/admissao.py` (T1: cultura + 2 momentos + densidade;
  `VERSAO_DA_REGRA = "9"`) · `tests/test_regua_t1.py` · `tests/test_a_regra_de_t2.py` ·
  `tests/test_estagio_atravessa_a_fronteira.py` · `scripts/regua_t1/**` · `scripts/regua_t2/MEDICAO-REGUA-T2-V2/V3.json` ·
  este relatório · `system-map/data/architecture.declared.json`.
- Passos: juntar na produção (conflito só nos gerados → cadeia); testes T1+T2+EGR+revisao_ready;
  `metricas_canonicas.py --sync` com PyYAML emprestado. Efeito: T1 **54 SIM / 836 NAO_SEI / 419 NAO**
  nos 1.309; 0 mudanças nos outros universos. Voltar atrás = reverter o merge.
