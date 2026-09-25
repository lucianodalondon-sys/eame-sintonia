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
