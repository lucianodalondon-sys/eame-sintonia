# REGUA-DO-TIPO-DE-FATO — relatório

- **Ramo:** `regua-fato-v1`, a partir de `reguas-t4t5t9-v1`, com `origin/lugar-fato-v1` (`b28d7471`) junto.
  O merge é `d17de643` e só teve conflito em gerados, que a cadeia refaz.
- **Rede fechada:** proxy `127.0.0.1:9`.
- **O vivo e a Sala não foram tocados.** As 78 linhas vêm da cópia só-leitura que a LUGAR-FATO fez com
  um único SELECT (`C:/Users/London1/lugar-fato/sala-78.json`, sha256 `8924d03d…11ce6`). Não repeti o SELECT.
- **O mesmo método da T1/T2, com a ordem cumprida:**
  1. protocolo (`df053f0a`);
  2. amostra e prova cega separadas antes de ler (`d60263cb`);
  3. gabarito (`b5a65579`);
  4. correções registadas (`15693826`);
  5. classificador congelado (`2c00a0bb`);
  6. só então os rótulos da cega (`7dc7d4e3`);
  7. a medida da cega, sem mudar uma linha.

## Veredito: `NAO PRONTO` — 73 % no gabarito, 58 % na prova cega; o alvo era ≥ 90 %

| | Gabarito (114 textos, dentro da amostra) | Prova cega (49 textos nunca usados) |
|---|---|---|
| Saem de `NAO_SEI` | 37 de 114 | 12 de 49 |
| **Certos, quando dá um tipo** | **27 de 37 = 73 %** | **7 de 12 = 58 %** |

Por tipo: `OURO` = quantos o rótulo tem; `diz` = quantas vezes o classificador disse esse tipo; `certo` = quantas dessas bateram com o rótulo.

| Tipo | Gabarito: ouro · diz · certo | Cega: ouro · diz · certo |
|---|---|---|
| CAMPO_FITOSSANITARIO | 5 · 5 · 3 | 2 · 1 · 1 |
| CAMPO_CLIMA | 4 · 3 · 2 | 0 · 0 · 0 |
| CAMPO_PRODUCAO_COLHEITA | 2 · 2 · 1 | 0 · 0 · 0 |
| MERCADO_PRECO | 9 · 9 · 7 | 6 · 5 · 4 |
| EVENTO_TECNICO | 14 · 4 · 4 | 3 · 3 · **0** |
| REGULATORIO_MOLECULA | **0** · 0 · 0 | 0 · 0 · 0 |
| NEGOCIO_AGRO | 9 · 4 · 2 | 1 · 1 · 0 |
| INSTITUCIONAL_NAO_FATO | 47 · 10 · 8 | 25 · 2 · 2 |

⚠️ **Nenhum tipo está pronto de verdade.** O ficheiro de medida escreve `PRONTO` para EVENTO no
gabarito (4 de 4) e para INSTITUCIONAL na cega (2 de 2). Isso é a regra do protocolo aplicada a
números **pequenos demais**. O EVENTO caiu para **0 de 3** na cega: a palavra «edizione», que
acrescentei a olhar para o gabarito, apanhou um telejornal e um artigo de preços. Isto é a prova cega a
fazer o seu trabalho. **Não mexi em nada depois de a abrir.**

- Precisão e recall do gabarito são medidos **dentro da amostra**, com os rótulos que eu mesmo escrevi.
- **Rótulos:** feitos por Claude, `VALIDADO_POR_HUMANO = NAO`.
- **Correções:** 3, só por erro de leitura provado no texto (`rotulos/CORRECOES-GABARITO.json`).
  - Os 2 Notiziari da ARIF começam pela previsão do tempo, mas ~2/3 são fitossanitários. Eu só tinha
    lido a abertura.
  - A revista «La Pianura» é um número inteiro, com vários artigos.
  - Revi **todos** os 27 textos longos, não só os que o classificador contrariou.

### Porque não chega (o que os erros dizem)
1. **Faltam exemplos.** Em 163 textos lidos, CLIMA tem 4, PRODUCAO 2 e REGULATORIO **0 em prosa**.
   - O acervo é o mesmo da REGUAS-T4-T5-T9: agências de ambiente, páginas institucionais e títulos do YouTube.
   - 72 dos 163 são INSTITUCIONAL e 36 são NAO_SEI, quase todos títulos soltos.
2. **Fronteiras por decidir** (`PROPOSTA-TAXONOMIA-FACT-KIND.md`):
   - **GDO (supermercado):** **3 dos 10 erros do gabarito**. Rotulei «não é facto» pela D62; o
     classificador diz MERCADO/NEGOCIO.
   - **Empresa a falar de técnica (Koppert):** 1 erro.
3. **Palavras de negócio e de evento são genéricas.** «azienda», «società», «evento», «edizione»
   aparecem em quase todo o texto institucional.

## O que foi feito

### 1. Taxonomia (proposta escrita) — `PROPOSTA-TAXONOMIA-FACT-KIND.md`
- Tem os 8 tipos da missão e mais `NAO_SEI`, cada um com **2 exemplos reais**.
- REGULATORIO só tem exemplo em **tabela**: o registo do Ministero della Salute (`IT-T4-001`, CSV
  copiado do armazém). Em prosa há 0.
- Casos de investigação sem tipo: **3 de 114 (2,6 %)**. Fica abaixo do limite de 10 % do protocolo, por
  isso **nenhum tipo novo é proposto**.
- ⚠️ **Nome repetido:** `superficie/ask_sintonia.py:246` já usa `FACT_KIND` para a frescura da resposta
  do benchmark (CURRENT / HISTORICAL / STRUCTURAL).

### 2. Gabarito
- **Sala:** as **78 linhas** são **63 textos diferentes** (há linhas com o mesmo texto). 44 foram para o
  gabarito e 19 para a cega.
- **Acervo:** 100 textos, sorteados de 1.127 com a semente 62062. 70 foram para o gabarito e 30 para a cega.

### 3. O classificador — `leis/tipo_do_fato.py` (função pura)
- **Regra 1 · só o corpo:** conta só o corpo, pelo `corpo()` da LUGAR-FATO, e tira também as linhas em
  MAIÚSCULAS (menu). Sem corpo = `NAO_SEI`.
- **Regra 2 · conceitos:** conceitos por **palavra inteira**. Cada conceito conta uma vez; um tipo precisa
  de ≥ 2 conceitos diferentes.
  - «raccolta» e «resa» só contam com o produto ou a medida a seguir.
  - Sem isso, «raccolta dei dati» e «resa possibile» contavam.
- **Regra 3 · evento:** evento anunciado na abertura (as 3 primeiras linhas diferentes) **e** com palavra
  agro vence os outros tipos. Aviso académico (exame, aula) não é evento.
- **Regra 4 · negócio:** precisa de ≥ 3 conceitos e ≥ 2 palavras agro.
- **Regra 5:** empate ou sinal fraco = `NAO_SEI`.
- **Regra 6:** INSTITUCIONAL só com ≥ 3 linhas de corpo, 0 conceitos e 0 palavras agro. Um título solto fica `NAO_SEI`.
- **Nada é descartado.**
- `tests/test_tipo_do_fato.py`: **22 testes verdes**. Os 23 da LUGAR-FATO continuam verdes.
- **Mutação:** `mutar_tipo_do_fato.py` dá **17 de 17 mortos**, e só conta quando um teste falha por asserção.
  - O M8 da primeira versão «morria» por erro de execução, o que não provava nada. Foi refeito.
  - O teste do «um conceito só» foi acrescentado **depois** de congelar. É teste, não classificador:
    o sha do classificador é o mesmo.
- **0 mudanças nos universos:** `git diff reguas-t4t5t9-v1 -- admissao/ orquestrador/ coleta/ supabase/`
  vem vazio. O classificador não é chamado por ninguém.

### 4. Ligação ao LUGAR-FATO e ao PACOTE-TEMPO-LUGAR
- **`fato_com_tipo(texto, publication_time, publication_time_basis)`** devolve os campos de
  `campos_do_fato` mais `fact_kind` e `fact_kind_basis`, com esta regra:
  - facto `CAMPO_*` → o lugar e o tempo **de EVENTO ou de MERCADO nunca o preenchem**; fica `NAO SEI`,
    com o porquê na base;
  - facto `EVENTO_TECNICO` → só lugar e tempo **de EVENTO**. O lugar da praga citada no evento fica na
    EVIDENCIA.
  - Os outros tipos não mexem no lugar nem no tempo.
- **Nas 78 da Sala** (`MEDIDA-TIPO-DO-FATO-SALA-78-V1.json`):
  - 49 de 78 saem de `NAO_SEI`: MERCADO 14, INSTITUCIONAL 11, EVENTO 11, FITO 7, NEGOCIO 3, CLIMA 2, PRODUCAO 1;
  - a ligação mudou **1 lugar**: IT-T5-010 «Veneto ; Ferrara ; Italia ; Roma (EVENTO)» passou a NAO SEI,
    porque o texto saiu PRODUCAO;
  - **0 itens descartados**;
  - lembrete: a 58 % de precisão, cerca de 4 em cada 10 destes tipos estão errados.
- **Campo no item** (proposta para o PACOTE-TEMPO-LUGAR):
  - `fact_kind` e `fact_kind_basis`, texto, com `NAO_SEI` por omissão;
  - chamados no mesmo sítio onde o pacote chamar `campos_do_fato`, trocando-o por `fato_com_tipo` (que
    devolve tudo o que ele devolve);
  - **a Sala não tem coluna**: seria uma migração aditiva, numerada **depois** de o coordenador resolver
    as duas 033;
  - não criei migração nenhuma.

## Recomendação

**Não instalar como campo em que a Intelligence confie.** Com 58 % na cega, o `fact_kind` erraria cerca
de 4 em cada 10 vezes que diz um tipo.

1. Se o pacote o levar, deve ir só como **evidência** (`fact_kind_basis` com a marca `NAO_MEDIDO`),
   nunca como filtro nem como chave de janela.
2. O que falta é o mesmo da T4/T5/T9: **textos reais** de clima, colheita, regulatório e negócio. Isso
   pede coleta com rede e está EM ESPERA (D61).
3. As **fronteiras do dono**: GDO; empresa a falar de técnica.
4. Depois, **um gabarito novo** e **uma prova cega nova** com o mesmo protocolo (a desta está gasta).

## Evidência fora do Git (sha256)
- Textos do gabarito e da cega (163): `%USERPROFILE%/sintonia-gabarito/REGUA-FATO-V1/textos`.
  O sha256 de cada um está em `A-ROTULAR-FATO.json` (`SHA256_NORMALIZADO`).
- Cópia da Sala: `C:/Users/London1/lugar-fato/sala-78.json`, `8924d03d848554c4c8df60aea2c24cbe688c63d84a002ba7447879f923a11ce6`.
- Classificador congelado: `leis/tipo_do_fato.py` @ `2c00a0bb`.

---

# v2 · decisões D71–D73 aplicadas (25/09, tarde)

**Veredito: continua `NAO PRONTO`. Na prova cega o acerto NÃO subiu: desceu de 58 % para 46 %.**

Ordem cumprida:
1. adenda 1 ao protocolo (`2a35147f`);
2. reetiquetagem do gabarito e da cega **antes** de mexer no classificador (`7fe88bf6`, `reetiquetar_v2.py`);
3. classificador v2 ajustado **só** no gabarito e congelado (`3297a5d9`);
4. medida da cega sem mudar nada.

## O que mudou
- **Nome do campo:** `agro_fact_kind` e `agro_fact_kind_basis` (D73). `fato_com_tipo` devolve os mesmos nomes.
- **D71:** empresa a explicar técnica = o tipo técnico. Koppert e os ácaros passaram a
  `CAMPO_FITOSSANITARIO`, com `PUBLICADOR: Koppert` no rótulo. No classificador: quando o assunto técnico
  tem tantos conceitos ou mais do que a voz da empresa, vence o técnico.
- **D72:** tipo novo **`MARKETING_CONCORRENCIA`**.
  - Rótulos: 9 no gabarito e 3 na cega, com `EMPRESA` / `PRODUTO` / `QUEM_FALOU` (`NAO SEI` quando o texto não diz).
  - No classificador: voz de empresa do agro («il nostro», «presenterà», «nuova linea», «gamma», «brand»…).
  - Numa feira, só é MARKETING se a empresa estiver no **lead**. A feira em si continua `EVENTO_TECNICO`.
  - ⚠️ O classificador **não** extrai empresa, produto nem quem falou. Isso está só nos rótulos.
- **D73:**
  - `MERCADO_VAREJO` pede a prova de varejo no **lead** (os primeiros 400 caracteres do corpo). Na página
    inteira, «insegne», «scaffale» e «e-commerce» vêm das listas de outras notícias.
  - Abertura ou ampliação de loja no lead, sem preço no lead, dá `INSTITUCIONAL`.
- **Ponto 5:** `INSTITUCIONAL` (mundo agro sem facto) separado de `NAO_FATO` (não é agro).
- **Mudaram 59 dos 114 rótulos do gabarito e 31 dos 49 da cega.** Quase todos são a divisão entre
  institucional e não-facto. Cada mudança tem `MUDOU_POR`, e o rótulo antigo ficou em `FACT_KIND_V1`.

## Números (`MEDICAO-FATO-*-V2.json`)

| | v1 | **v2** |
|---|---|---|
| Gabarito, certos quando diz um tipo | 27/37 = 73 % | **30/39 = 77 %** |
| Prova cega, certos quando diz um tipo | 7/12 = 58 % | **6/13 = 46 %** |

Na cega, por tipo (quantos o classificador disse · quantos certos):
- MERCADO_PRECO: 4 ditos, 2 certos
- MERCADO_VAREJO: 1 · 1
- FITO: 1 · 1
- NAO_FATO: 2 · 2
- **EVENTO: 3 · 0**
- NEGOCIO: 1 · 0
- INSTITUCIONAL: 1 · 0
- **MARKETING: 0 ditos, com 3 no ouro**

## Porque desceu (os 7 erros da cega)
1. **3 são o «evento» de sempre**: «edizione» (telejornal Edagricole, reportagem de preços) e «eventi»
   (Georgofili). **Sabia deste defeito desde a v1 e não o corrigi de propósito**: corrigi-lo seria ajustar a
   régua à prova cega. É o custo honesto de uma âncora escolhida a olhar para o gabarito.
2. O plano de um departamento de Biotecnologia foi lido como NEGOCIO («acquisizione», «fusioni»,
   «finanziamenti» de gestão universitária).
3. O MARKETING não acendeu nenhuma vez na cega. O curso de Chianti Classico dos consórcios saiu INSTITUCIONAL.
4. Varejo da Alemanha sem palavra de varejo no lead saiu MERCADO_PRECO. Uma escola agrária saiu MERCADO_PRECO.

⚠️ **A cega está gasta duas vezes.** Li os 49 textos na v1 e vi os erros. A medida v2 é tudo menos
otimista, mas já não é uma prova limpa. **A próxima medida precisa de textos novos.**

## Testes, mutação, Sala
- `tests/test_tipo_do_fato.py`: **32 verdes** (10 novos, para D71–D73). A LUGAR-FATO continua com 23 verdes.
- `mutar_tipo_do_fato.py`: **24/24 mortos** (7 novos, M18–M24).
  - O M19 (a D71 desligada) sobreviveu na primeira versão: o teste tinha mais conceitos técnicos do que
    de promoção, e a regra nunca era posta à prova.
  - Refiz o teste com um empate de 3 contra 3.
- **78 da Sala** (`MEDIDA-TIPO-DO-FATO-SALA-78-V2.json`):
  - 52 de 78 saem de NAO_SEI;
  - MARKETING 1, VAREJO 2, INSTITUCIONAL 6, NAO_FATO 11;
  - a ligação ao lugar mudou 1 (o mesmo IT-T5-010);
  - **0 descartados**.

## O que falta para chegar a 90 %
- **Os mesmos textos que faltavam:** clima, colheita, regulatório, e agora **comunicação de empresas**.
  O MARKETING tem só 9 exemplos no gabarito e 3 na cega.
- **Uma prova cega nova**, com textos que ninguém leu.
- A lista de empresas do setor (para anotar `EMPRESA` no classificador) é uma decisão à parte, e não a
  inventei aqui.
