# CRITÉRIO DE LEITURA V1 — MISSAO-07 (fixado antes dos rótulos formais; sha256 publicado no relatório)

Quem lê: LAB (modelo Claude Opus 5.5) + os 3 motores da triangulação, cada um sozinho. NENHUM rótulo é humano (D110):
HUMAN_REVIEW = NOT_DONE. Declaração honesta: antes de fixar este critério o LAB já tinha olhado os trechos para montar o
material (não havia rótulos gravados). A amostra NÃO é aleatória do acervo: é TODO o material coletado automaticamente
em 28/09 desde 03:00 UTC (76 documentos com texto) — não dá porcentagem de outras fontes nem de outros dias.

## A. Rótulo AGRO (Estudo B e amostra dos NÃO)
Base: D62 do dono — FATO = o que muda no campo (praga, doença, clima, colheita, preço) + eventos técnicos (feiras,
congressos, dias de campo) + TODO o ecossistema do agronegócio (moléculas, sementes, política agrícola, mercado agro).
- ÚTIL-AGRO: o CORPO da matéria trata de agricultura/pecuária/agroalimentar como assunto principal (praga, cultura,
  semente, preço/custo agro, política agrícola, evento técnico do setor agro, ciência sobre planta cultivada/praga).
- NÃO-AGRO: assunto principal fora do agro (energia, materiais, nanotecnologia, biomedicina, qualidade do ar urbana,
  clima polar/oceânico, ecodesign industrial, administração do órgão sem conteúdo agro, esporte, imóveis).
- DISCUTÍVEL: agro só lateral ou institucional (evento de divulgação ao público, nomeação de diretores, silvicultura/
  viveiro florestal, aquicultura, evento com etiqueta «Agroalimentare» mas conteúdo genérico de inovação).
Palavra «ricerca», «università», «convegno» sozinha nunca faz ÚTIL: vale o assunto do corpo.

## B. Rótulo da GAVETA (Estudo A — cada SIM/retido do reroute)
Pergunta: «este documento pertence DE VERDADE à gaveta para onde o reroute o mandaria?»
- ÚTIL: pertence à gaveta (T1 cultura+momento; T2 clima com ligação agrícola; T3 praga/doença; T10 preço/mercado/custo
  agro; T5 ciência = estudo/ensaio/artigo/pesquisa com resultado; T7 rede técnica = agrônomos/cooperativas/assistência).
- FALSO: não pertence (a palavra casou mas o assunto é outro).
- DISCUTÍVEL: pertence em parte / depende de decisão do dono da régua.
Um documento pode ser ÚTIL-AGRO (A) e FALSO para a gaveta (B) ao mesmo tempo — são perguntas diferentes.

## C. Precisão
precisão = ÚTIL / (ÚTIL + FALSO) (estrita: DISCUTÍVEL conta como FALSO; larga: DISCUTÍVEL fora do denominador).
Intervalo de Wilson 95 %. n < 10 = «n pequeno, não decide sozinho».

## D. Critério do veredito por gaveta (a Sala não vira lixo)
- LIGAR: ≥ 1 SIM novo lido nesta amostra independente, FALSO = 0 nela, e a amostra do autor também sem FALSO.
- NÃO LIGAR: qualquer FALSO nesta amostra OU precisão estrita < 80 % somando amostras.
- MEDIR MAIS: 0 SIM novo nesta amostra (nada a medir) ou só DISCUTÍVEIS.
- Ruído que JÁ entra sem reroute (T5) é medido à parte e não é culpa do reroute; mas se a porta atual já deixa
  entrar NÃO-AGRO, o veredito tem de dizê-lo.
