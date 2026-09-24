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
