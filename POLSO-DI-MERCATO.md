# POLSO-DI-MERCATO — o extrator de preço observado

Ramo `nuvem-polso-mercato-v1`, sobre a produção `69b0e23f`. Sem rede externa: só fixtures do repo e
casos sintéticos marcados. SHA final: ver o fim deste ficheiro e o `git log` do ramo.

## O que fiz

1. **`leis/preco_de_mercado.py`** (novo) — função pura `precos_do_texto(texto)`. Devolve quatro listas:
   - `OBSERVACOES`: uma por preço que tem número + moeda + unidade. Campos: COMMODITY, CULTURA, PRACA,
     PERIODO (+ `_TIPO`, `_BASIS`), PRECO ou PRECO_MIN..PRECO_MAX, MOEDA, UNIDADE (EUR/kg · EUR/t · EUR/q ·
     EUR/hl · EUR/l), ESTAGIO (PRODUTOR · INGROSSO · DETTAGLIO, + `_BASIS`), NATUREZA
     (OBSERVADO · MEDIO · ORIENTATIVO), PAPEL (OBSERVACAO · REFERENCIA_DE_COMPARACAO), SERIE, TRECHO.
   - `COMENTARIOS`: o comentário jornalístico, separado do preço, com o PORQUÊ
     (VARIACAO_SEM_NIVEL_DE_PRECO · OPINIAO · PROJECAO_NAO_E_OBSERVACAO · VOLUME_DEMANDA_OU_VENDA_NAO_E_PRECO …).
   - `RECUSADOS`: valor em euro que não é preço unitário (faturamento, capital social, preço sem unidade).
   - `COMPARACOES`: os trechos «rispetto al 2025», «come nel 2025», «dello scorso anno», «su base mensile».
2. **`tests/test_preco_de_mercado.py`** (novo) — 32 testes. Reais: BMTI 46622 e 46647 (HTML inteiro,
   IT-T10-002), Assosementi (título real, IT-T1-013), ISMEA (citação literal em `data/samples/IT-V2`),
   Cantine Riunite (IT-T7-017, texto em `data/samples/RUN-MANIFEST.json`). Sintéticos marcados: forma de
   myfruit, listino de Borsa Merci, quintal, dettaglio, conflito de estágio, publicação, projeção.
3. **`provas/_mutantes_preco_de_mercado.py`** (novo) — 20 mutantes numa cópia em `%TEMP%` (nunca na
   worktree), com `PYTHONDONTWRITEBYTECODE` e conferência de sha256. Resultado em
   `scripts/polso_mercato/MUTACAO-PRECO-DE-MERCADO-V1.json`.
4. **`scripts/polso_mercato/bateria_por_nome.py`** (novo) — bateria por nome antes/depois (forma da D70),
   rede fechada. `--parte leve` (módulos de `tests/`) e `--parte mapa` (testes do System Map, pesado).
5. **System Map**: peça nova `C-PRECO-DE-MERCADO` em `system-map/data/architecture.declared.json`
   (Z-REGUAS, contrato, DECLARED_RULE_NOT_ENFORCED — nenhum módulo de runtime a importa), e o mapa regerado
   pela cadeia.

## Onde está cada regra (ficheiro:linha)

| regra | onde |
|---|---|
| a porta só recebe o texto (publicação e coleta não entram) | `leis/preco_de_mercado.py:334` |
| cultura vem do dono (`regua_italia.CULTURAS`); commodity fora da tabela = NAO SEI | `leis/preco_de_mercado.py:63-82` |
| comparação tapada antes de procurar o período | `leis/preco_de_mercado.py:133` e `:232` |
| ano solto lido também antes de vírgula/ponto (defeito achado pelo mutante M19) | `leis/preco_de_mercado.py:161` |
| preço dentro da comparação = REFERENCIA_DE_COMPARACAO com o período dela | `leis/preco_de_mercado.py:363` |
| projeção não é observação | `leis/preco_de_mercado.py:357` |
| estágio só com marcador escrito; dois estágios = NAO SEI (CONFLITO) | `leis/preco_de_mercado.py:268` |
| montante sem unidade recusado; faturamento nunca vira preço | `leis/preco_de_mercado.py:99` |
| série só com CULTURA+PRACA+ESTAGIO+UNIDADE+MOEDA | `leis/preco_de_mercado.py:303` |

## O caso real «2,80 €/kg … 2025»

- **Assosementi (real, IT-T1-013):** «erba medica: confermato a 2,80 €/kg il prezzo orientativo per la
  campagna 2026» → 2,80 EUR/kg · ERBA_MEDICA · PERIODO `campagna 2026` · NATUREZA ORIENTATIVO · ESTAGIO NAO SEI.
- **Mesmo preço com «come nel 2025» (sintético):** PERIODO = NAO SEI; o 2025 fica em COMPARACOES.
- **«rispetto ai 2,80 €/kg del 2025» (sintético):** duas observações. A principal fica com o período dela;
  a de 2,80 é REFERENCIA_DE_COMPARACAO com PERIODO 2025.

⚠️ **Achado, fora do meu âmbito:** o leitor de tempo do facto `leis/fato_do_texto.py` (dono: LUGAR-FATO)
**ainda comete o erro** nesta árvore. Para «Erba medica: il prezzo orientativo resta di 2,80 €/kg come nel
2025, stabile per gli agricoltori italiani della campagna.» ele devolve `fact_time = 2025`
(CAMPO · AMARRADO_AO_ACONTECIMENTO · APPROXIMATE). O marcador «come nel» não está no `_RE_COMPARACAO` dele
(`leis/fato_do_texto.py:198`). Não mexi: é outro dono. O ramo `extrator-evento-v2` (fora desta base) trata
anos de comparação; se cobre «come nel», NAO SEI.

## Real, medido nos bytes do repo

| fixture | o que sai |
|---|---|
| BMTI 46622 (cereais, HTML inteiro) | 1 observação: grano duro fino · FRUMENTO · CUN · INGROSSO · 265 EUR/t · PERIODO `luglio` com «MES SEM ANO» · SERIE `FRUMENTO\|CUN\|INGROSSO\|EUR/t\|EUR`. As variações (+1,7%, +1,3%, −6,6%, −12%) vão para COMENTARIOS; os 5 milhões de toneladas não viram preço; «€ 2.387.372,16» do rodapé é RECUSADO |
| BMTI 46647 (olio) | 0 observações: a página capturada só tem o rodapé com € |
| ISMEA (linha da tabela) | 5,12 EUR/kg · OLIVO · PERIODO `2026-7` · PRACA e ESTAGIO NAO SEI (a linha não os escreve) |
| Cantine Riunite (IT-T7-017) | 47,20 EUR/q · PRODUTOR («riconosciuto ai soci») · MEDIO · CULTURA NAO SEI · PERIODO NAO SEI (a data da notícia 16/12/2025 não entra); «266 milioni di euro» RECUSADO; «ritenuto … di soddisfazione» é OPINIAO |

## Testes antes/depois, por nome

Base = cópia limpa de `69b0e23f` (worktree destacada em `%TEMP%`). Rede fechada (proxy numa porta morta).

| parte | antes | depois | falhas novas por nome |
|---|---|---|---|
| leve (6 módulos: preço, fato_do_texto, lugar_do_fato, artefato_tempo_do_fato, admissao_multilingue, social_bruto) | 102 testes + 1 módulo AUSENTE, 0 vermelhos | 134 testes (102 + 32 novos), 0 vermelhos | **0** |
| mapa (`system-map/tests`) | ver abaixo | ver abaixo | ver abaixo |

Ficheiros: `scripts/polso_mercato/BATERIA-LEVE-ANTES.json`, `BATERIA-LEVE-DEPOIS.json`.

## Mutação

**20/20 mortos** (`scripts/polso_mercato/MUTACAO-PRECO-DE-MERCADO-V1.json`). Inclui M1 (comparação desligada:
o caso 2,80/2025), M2 («come nel» fora), M3 (publicação não tapada), M4 (tapa só o marcador), M5/M6 (preço da
régua vira observação / perde o período), M7 e M18 (montante e faturamento), M8 (projeção), M9 (conflito de
estágio), M10 (CUN), M11 (série), M12 (milhar italiano), M16 (procura/venda), M17 (a porta aceita a
publicação), M19 (ano da comparação sem tapa).

Na primeira corrida o **M19 sobreviveu** (19/20). A causa era um defeito meu: o padrão do ano solto não lia
«2025,» nem «2025.» (a pontuação a seguir estava proibida). Corrigido em `leis/preco_de_mercado.py:161`, com
teste positivo novo (`test_ano_solto_antes_da_virgula_e_lido_quando_nao_e_comparacao`). Depois: 20/20.

## Limites (NAO SEI dito)

- **Ninguém usa isto ainda.** É uma lei escrita, não ligada à entrada do dado (DECLARED_RULE_NOT_ENFORCED).
  Ligá-la ao coletor/Sala é decisão de arquitetura, não tomada aqui.
- **Estágio só por marcador escrito.** CUN e Borsa Merci contam como INGROSSO por definição (são praças de
  atacado) — está escrito na base de cada observação. Onde o texto não diz, fica NAO SEI.
- **Frase a frase.** Período, praça e estágio escritos noutra frase não são herdados (ex.: BMTI «Cereali
  Luglio 2026» na etiqueta da página não dá o ano ao «a luglio» do corpo). É de propósito: herdar é adivinhar.
- **Tabela de commodities curta** (18 linhas). Mirtilli, kiwi, ciliegie… saem com CULTURA NAO SEI.
- **Moeda:** só EUR e USD.
- Não medi sobre a Sala real (não existe na nuvem). Números sobre o acervo: NAO SEI.

## Fontes T10 de mercado independentes de myfruit (pedido da coordenação 11:45)

A Intelligence R2 diz que myfruit.it (IT-T10-018) dá 66,7% dos sinais e é a única fonte de mercado. Procurei
**só no que já existe** no repo e nos livros (sem rede). Pedido: PREÇO + PRAÇA + DATA + UNIDADE.

| # | fonte | estado hoje | o que o repo prova | o que falta |
|---|---|---|---|---|
| 1 | **BMTI — Borsa Merci Telematica** (IT-T10-002) | fonte registada; livro: ROUTE_FAILURE na BCR-2026-09-20 | bytes reais no repo (46622): **o extrator tira preço+praça+mês+unidade** (265 €/t, CUN, luglio) | a rota de coleta (receita da página de análise); o ano do mês vem noutra frase |
| 2 | **Borsa Merci di Bologna — CCIAA** (IT-T10-009) | fonte registada; READY_FOR_COLLECTION; 1 corrida com sucesso na Big Collection | NAO SEI se o que colhe é o listino (preço+unidade) ou a capa | abrir o documento colhido e passar pelo extrator |
| 3 | **ISMEA Mercati** (IT-T10-001) | fonte registada, status NEW | citação literal com preço+unidade+mês (5,12 €/kg, 2026-7) | praça (é nacional); ESTAGIO só no rótulo externo («na origem»); do Brasil dava GEO_IP_BLOCK — com a VPN IT de hoje, NAO SEI |
| 4 | **CSO Italy** (IT-T10-010) | fonte registada; READY_FOR_COLLECTION; 1 corrida com sucesso | nenhuma prova de preço no conteúdo | medir se publica preço aberto ou só para associados |
| 5 | **Granaria — Borsa Merci di Milano** (CAND-0157, sem SOURCE_ID) | candidata EM_ANALISE; o crawl achou páginas de listino (CAND-0499 «Listino Bioenergetico 2026-09-08») e uma «AREA MERCATO» com login (CAND-0496) | que há listinos datados públicos | registar a fonte, receita de listino, confirmar o que é aberto e o que está atrás do login |
| + | **Borsa Merci di Vercelli / Mercato di Novara** (pno.camcom.it) e **Sala Mortara** (paviaprezzi.it) — arroz | **não estão** na `FONTES-CANDIDATAS.json` (grep: 0) | o handoff V2 (`build/ITALY-REALITY-HANDOFF-V2/.../crop-summary-riso.md`) diz ALCANÇADA: listino n.30 de 01/09/2026 (PDF), CSV oficial de 31/07/2026 | entrar na fila de candidatas |

Não achei **Italmercati** em lado nenhum do repo (grep: 0). **AgriMercati** é publicação da ISMEA, não é fonte
independente. **Terra e Vita / Edagricole** (CAND-0708, «Prezzi agricoli») é imprensa como a myfruit:
independente dela, mas não é praça primária.

## EM PALAVRAS SIMPLES

Fiz um "leitor de preço". Você entrega um texto de mercado e ele devolve uma ficha por preço: qual produto,
em que mercado, em que período, quanto, em que moeda, por quilo/tonelada/quintal, e se é preço do produtor,
do atacado ou do varejo.

O cuidado principal foi com o ano. Numa frase como "2,80 €/kg, como em 2025", o 2025 é só a régua de
comparação, como dizer "estou mais alto que no ano passado". O leitor novo não confunde mais isso: sem
período escrito, ele diz "não sei". O leitor antigo de datas do projeto **ainda erra** esse caso; está
anotado, mas não mexi, porque tem outro dono.

Ele também separa o preço do comentário ("os sócios ficaram satisfeitos" não é preço) e recusa o que não é
preço ("faturou 266 milhões de euros" não vira preço, nem venda, nem procura).

Para provar que os testes funcionam, estraguei o leitor de 20 jeitos diferentes, de propósito, numa cópia.
Os testes pegaram os 20. Na primeira rodada escapou um, e isso mostrou um defeito meu, que corrigi.

Nada foi perdido e nada que já funcionava quebrou: 0 falhas novas nos testes comparados um a um.
O leitor ainda **não está ligado** à coleta. Por enquanto é uma regra escrita e testada.
