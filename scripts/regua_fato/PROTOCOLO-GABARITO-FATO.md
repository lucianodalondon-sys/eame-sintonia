# PROTOCOLO DO GABARITO DO TIPO DE FACTO (FACT_KIND) — escrito ANTES dos rótulos e do classificador

REGUA-DO-TIPO-DE-FATO · 2026-09-25 · ramo `regua-fato-v1` (de `reguas-t4t5t9-v1` + `lugar-fato-v1`).
Mesmo método da T1/T2: primeiro o gabarito, depois a régua, e a régua é medida no gabarito e numa prova
cega. Este ficheiro é commitado antes do primeiro rótulo e antes de qualquer linha do classificador.

## O que é (D62)

FACTO = o que muda no campo (praga, doença, clima, colheita, preço) + eventos técnicos (feiras,
congressos, dias de campo) como tipo próprio + todo o ecossistema do agronegócio (moléculas, empresas).
O `FACT_KIND` é **só uma etiqueta**: não descarta nada, não muda veredito de gaveta, e `NAO_SEI` é uma
resposta válida.

## A taxonomia proposta (um tipo principal por item: o assunto dominante do CORPO)

| FACT_KIND | Pergunta ao conteúdo | Não é |
|---|---|---|
| `CAMPO_FITOSSANITARIO` | fala de praga, doença, infestante, monitorização, capturas, limiar, defesa/tratamento de uma cultura? | a molécula como produto registado (→ REGULATORIO) |
| `CAMPO_CLIMA` | fala do tempo ou clima que muda as condições do campo (chuva, seca, geada, granizo, calor, balanço hídrico, previsão agrometeorológica)? | qualidade do ar, poluição, ruído, resíduos sem ligação à agricultura (→ NAO_FATO) |
| `CAMPO_PRODUCAO_COLHEITA` | fala de fenologia, sementeira, colheita, rendimento, volumes de produção, áreas, qualidade da colheita, variedades? | preço (→ MERCADO) |
| `MERCADO_PRECO` | fala de preço, cotação, volumes vendidos, exportação, consumo, retalho de produto agro? | loja ou empresa como notícia de negócio sem preço/volume (→ NEGOCIO) |
| `EVENTO_TECNICO` | anuncia ou relata feira, congresso, convénio, workshop, webinar, dia de campo, curso técnico **do mundo agro**? | evento de outro setor (→ NAO_FATO); «eventos extremos» (→ CLIMA) |
| `REGULATORIO_MOLECULA` | fala de registo, autorização, revogação, derrogação, restrição de um produto fitossanitário, fertilizante ou semente; substância ativa; LMR; rótulo? | regulamento que não é de produto (→ NEGOCIO ou NAO_FATO) |
| `NEGOCIO_AGRO` | fala de empresa do agro, produto comercial, lançamento, aquisição, investimento, loja agro, apoio/financiamento ao setor, política agrícola? | abertura de loja fora do agro (→ NAO_FATO) |
| `INSTITUCIONAL_NAO_FATO` | é menu, página institucional, administração, outro setor (saúde, impostos, ambiente sem campo, universidade sem agro)? | — |
| `NAO_SEI` | texto curto demais, ou mistura sem assunto dominante | — |

Regras de decisão, na ordem:
1. Lê-se o **corpo**: menu, cabeçalho e rodapé não contam (a regra do corpo é a de `leis/fato_do_texto.corpo`).
2. Um só tipo: o do assunto que ocupa mais do corpo. Evento sobre pragas → `EVENTO_TECNICO` (o facto é
   o evento; a praga é o tema dele).
3. Investigação classifica-se pelo assunto (ensaio sobre uma praga → FITOSSANITARIO). Conteúdo agro que
   não cabe em nenhum tipo: `NAO_SEI` com `PORQUE` a começar por `SEM_TIPO`. **Se passar de 10 % do
   gabarito, o relatório propõe um tipo novo.**
4. Duas linhas da Sala com o mesmo texto (sha256 do texto normalizado) são rotuladas uma vez; a contagem
   diz linhas e textos.

## Os textos (sem rede)

- **Sala, 78 linhas**: a cópia só-leitura `C:/Users/London1/lugar-fato/sala-78.json` (um único SELECT
  da LUGAR-FATO, 25/09 09:43; sha256 `8924d03d848554c4c8df60aea2c24cbe688c63d84a002ba7447879f923a11ce6`).
  Não se volta a ler a Sala.
- **Acervo, 100 textos**: sorteados do mesmo acervo da REGUAS-T4-T5-T9 (`scripts/regua_t4t5t9/amostrar.py`:
  REGUA-T2-V1, REGUA-T1-V1, cópia do armazém `C:/ajustes/armazem-textos`, `data/derivados/texto`),
  sem os textos que já estão nas 78. **Semente 62062.**
- Os textos ficam fora do Git: `%USERPROFILE%/sintonia-gabarito/REGUA-FATO-V1/textos/<id>.txt`.

## Prova cega, e a ordem

- **30 %** de cada conjunto (Sala e acervo) vai para a **PROVA CEGA**, pelo sorteio da mesma semente,
  **antes** de ler.
- Ordem obrigatória:
  1. rotular o GABARITO;
  2. escrever o classificador olhando só o gabarito;
  3. **congelar o classificador num commit**;
  4. só então rotular a prova cega;
  5. medir a prova cega sem mudar uma linha.

## O classificador

- Mesmo método da T1/T2: conceitos por palavra inteira, contados **só no corpo**. Cada tipo precisa de
  sinais do seu conceito; o evento precisa também de sinal agro.
- Empate ou sinal fraco → `NAO_SEI`.
- Devolve `fact_kind`, `fact_kind_basis` (com as palavras e o trecho) e a `EVIDENCIA`.
- **Interface com a LUGAR-FATO:** o lugar de `EVENTO` ou de `MERCADO` nunca preenche o lugar de um
  facto `CAMPO_*`. Um facto `EVENTO_TECNICO` só usa lugar de EVENTO.

## Medida e o que é «pronto»

- **Por tipo:** precisão (quando o classificador diz esse tipo, o humano concorda) e recall.
- **Cobertura:** quantos saem de `NAO_SEI`.
- **Pronto para um tipo:** ≥ 10 exemplos no gabarito E precisão ≥ 90 % no gabarito. O alvo de
  referência é T1 98 % / T2 95 %.
- Com menos exemplos o tipo sai `NAO MEDIDO`, dito assim; o classificador ainda o pode dizer, com a
  marca no relatório.
- A prova cega é medida e reportada tal como sair.
- Rotulador: Claude. `VALIDADO_POR_HUMANO = NAO`.
- **Mutação:** desligar cada peça (o corpo, cada conceito, a exigência agro do evento, o NAO_SEI no empate,
  a regra de lugar por tipo) tem de reprovar um teste por asserção.
- **0 mudanças nos universos:** o classificador não toca em `admissao/admissao.py`. Prova-se com o diff.

## ADENDA 1 · 25/09 · decisões D71–D73 (dono real + bot Luciano), escrita ANTES de reetiquetar

Fonte: `auditoria-madrugada/DECISOES-DONO-2026-09-23.md` (D71, D72, D73 e a reconciliação do coordenador).

1. **Nome do campo:** `agro_fact_kind`, não `fact_kind` (D73).
2. **D71 · empresa a explicar TÉCNICA** (Koppert e os ácaros): o tipo é o do assunto técnico
   (`CAMPO_FITOSSANITARIO`, ou o tipo técnico certo). A empresa fica anotada como quem publicou.
3. **D72 · tipo novo `MARKETING_CONCORRENCIA`.** Entra aqui:
   - uma empresa (ou consórcio de marca) a promover os **próprios** produtos;
   - qualquer pessoa (agrónomo, pesquisador, influencer) a falar **bem** de um produto;
   - a presença de uma empresa num evento para mostrar produtos;
   - toda a comunicação da concorrência.
   Anotam-se `EMPRESA`, `PRODUTO` e `QUEM_FALOU` (`NAO SEI` quando o texto não diz). **Não é NAO_FATO.**
   - A feira em si (Macfrut, Interpoma) continua `EVENTO_TECNICO`. A empresa a mostrar-se na feira é MARKETING.
   - ⚠️ **Leitura minha**, a confirmar: «concorrência» lida como **qualquer empresa do agro** (sementes,
     biocontrolo, vinho, fruta), não só a proteção de culturas, porque a D72 diz «empresa X/Y».
4. **D73 · `MERCADO_VAREJO`:** varejo alimentar **só com facto de produto agrícola** (preço, oferta,
   procura, disponibilidade, origem, promoção concreta). O preço do grossista, da commodity ou da
   exportação fica em `MERCADO_PRECO`.
   - A prova de que é varejo tem de estar no **corpo** (loja, insígnia, e-commerce, prateleira,
     «online» no título), não no menu do site.
   - **Abertura ou operação de loja = `INSTITUCIONAL`.**
5. **NAO_FATO só para o que não é agro nem comunicação de concorrente.** Por isso o antigo
   `INSTITUCIONAL_NAO_FATO` divide-se em dois:
   - `INSTITUCIONAL`: conteúdo **do mundo agro** sem facto (página de ordem profissional, aviso de curso
     agrário, menu de agência agrícola, abertura de loja);
   - `NAO_FATO`: tudo o que não é agro. Decide-se pelo **conteúdo**, não pelo site.
   - ⚠️ Leitura minha dos pontos (4)+(5).
6. `NEGOCIO_AGRO` fica para empresa ou setor **sem** promoção de produto próprio (aquisição, investimento,
   apoio, política agrícola).

Taxonomia v2 (12 valores): `CAMPO_FITOSSANITARIO` · `CAMPO_CLIMA` · `CAMPO_PRODUCAO_COLHEITA` ·
`MERCADO_PRECO` · `MERCADO_VAREJO` · `EVENTO_TECNICO` · `REGULATORIO_MOLECULA` · `NEGOCIO_AGRO` ·
`MARKETING_CONCORRENCIA` · `INSTITUCIONAL` · `NAO_FATO` · `NAO_SEI`.

**Ordem:**
1. reetiquetar o gabarito **e** a cega com a v2, só pelos textos e sem correr o classificador; commit;
2. mudar o classificador **só** olhando para o gabarito; congelar; commit;
3. medir a cega sem mudar nada.

⚠️ **A cega já não é cega.** Li os 49 textos e vi os 5 erros da v1 neles. A medida nova na cega é
**otimista** e diz-se assim. Uma prova limpa pede textos novos.
