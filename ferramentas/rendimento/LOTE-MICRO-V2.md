# LOTE-MICRO-V2 — a lista FIXA da micro, depois da R1

Escrita **antes da rede** a 25/09/2026, de madrugada. Bot vivo 5ba9647e: R1 instalada às 01:50; régua T2 instalada.
Ficheiro: `LOTE-MICRO-V2.json` · sha256 `761af4501650ac59e213931869d87bf1d55b68a850645253c2d3b9501e2ba9b7`. **Não foi corrida.** Corre o coordenador, pelo orquestrador oficial.
Substitui a V1: a Bonifica Romagna saiu porque a revisão da R1 não a deixou ficar READY.

## Em palavras simples

**6 fontes, escolhidas antes de ir buscar nada.** Os endereços que a coleta vai pedir ficam já escritos.

| # | Fonte | O que é | Precisa de | Documentos | SIM esperado |
|---|---|---|---|---|---|
| 1 | **IT-T10-018 myfruit** | notícias de fruta: 11 novas, a corrida traz 3 | **nada** | 3 | ~1 |
| 2 | **IT-T3-002 Campania** | **boletim fitossanitário** de Salerno, edição **23/09**, nunca guardada | revalidar READY_LEGACY | 1 | ~1 |
| 3 | **IT-T3-010 APOL** | **boletim da mosca da oliveira nº 11, de 21/09**, nunca guardado | revalidar READY_LEGACY | 1 | ~1 |
| 4 | **IT-T2-002 ARPAV** | **boletim agrometeo** por zona (fase da planta, defesa integrada, evaporação) | revalidar READY_LEGACY | 4 | ~3 |
| 5 | **IT-T3-023 Terra e Vita** (R1) | secção de defesa das plantas: «ferrugem das drupáceas» | ficar READY no vivo **e** ter contrato no coletor | 1 | ~0,3 |
| 6 | **IT-T7-049 Copagri** (R1) | «Giornata europea del biologico» | as mesmas duas | 1 | ~0,2 |

- **Previsão:** 11 documentos e ~6 SIM, ou seja **~57%**. Se as 3 READY_LEGACY não forem revalidadas: 5 documentos e ~1,7 SIM, **~34%**. Os dois passam os **16,7%**.
- ⚠️ **É uma estimativa com pouca base:** 46 textos na myfruit e só **1 a 4** em cada boletim. **0 SIM é possível.**
- **Regra fixada agora:** fonte cuja condição falhar conta como **«não correu»**, e não como 0 SIM.

## Três coisas que o coordenador precisa de saber antes de correr

1. **Das 25 READY da R1, só 1 está READY agora** (IT-T12-024, 01:50). As outras 24 ainda estão no estado antigo. O bot está a trabalhar: o supervisor corre, e os livros foram escritos às 01:50. Numa cópia, as 40 levaram ~15 min.
2. **Nenhuma das 25 da R1 tem contrato na tabela do coletor.** O contrato só existe no curador, e o orquestrador oficial recusa-as como fonte desconhecida. As fontes 5 e 6 **só correm se alguém importar o contrato** para a tabela do coletor. Sem isso, contam como «não correu».
3. **Os boletins de verdade estão todos em READY_LEGACY:** aprovados pela régua antiga e nunca revistos. O portão recusa-os. A R1 não muda isto. Para entrarem, é preciso **revalidá-los no Curator**. É uma decisão do coordenador, e é aí que está a maior parte dos SIM esperados.

## Ficam de fora (decidido antes da rede)

- **As outras 23 da R1.** Nenhuma tem contrato no coletor. As de T12 e T8 não têm régua. As T2 da R1 não têm ligação agrícola. Nas T5 e T7, a régua sobre o item revisto deu NÃO ou NÃO_SEI.
- **IT-T7-141:** a janela é uma listagem, não uma notícia.
- **IT-T2-051 e IT-T2-034:** notícias das ARPA sem ligação agrícola.
- **IT-T7-041:** a revisão da R1 não a deixou ficar READY.
- **IT-T3-008 (boletim da Puglia):** a página de índice só abre com navegador, e a rota de reserva adivinha a edição por datas, com até 30 pedidos. Passa o teto de 5 pedidos por site.

## Provas no ramo (`ferramentas/rendimento/`)

- `LOTE-MICRO-V2.json` (+ `.sha256`): a lista, os endereços previstos, a previsão e o antes da rede. O antes da rede inclui o vivo 5ba9647e, o estado do portão das 6 fontes, a Sala (69 / 1425 / 927 / 402), o sha256 do livro do coletor e o egresso PASS.
- `lote-v2-entrada.json`: a escolha, escrita à mão, com o porquê de cada fonte.
- `medidas/entrada-boletins.json` e `medidas/entrada-r1-escolha.json`: as capas medidas esta madrugada. Portão de consenso PASS antes e depois, 12 pedidos.
- `medidas/boletins-contratos.json`: a regra dos `case` do coletor escrita como contrato, **só para medir**.
- `medidas/r1-revisao-contratos.json`: o contrato que a revisão da R1 leu.
- `lote_micro.mjs`: agora lê a lista de um ficheiro. A V1 refaz-se igual a partir de `lote-v1-entrada.json` (endereços e previsão conferidos).
