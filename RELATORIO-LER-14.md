# RELATÓRIO — LER-14

Ramo `ler-14-v1`, a partir de `integra-onda2-v1 @ d235c32a`. **Não instalado.** Rede: 0 pedidos.

## O achado: as 14 já estavam lidas

As 14 fontes em REVISAO_PENDENTE da RECEITAS-182 são **14 das 15** que a REVISAO-15 leu uma a uma
(`reparo-fontes-v3 @ 3384c57d`, 25/09 08:09; a 15.ª é IT-T8-058). Ler outra vez duplicaria o
ficheiro de revisão (`curadoria/REVISAO-READY-V1.json`) — o que a missão manda evitar.

Conferido contra o livro vivo do curador (só leitura): a leitura de cada uma é do **mesmo contrato**
que está lá hoje (mesmo INDEX_URL e LINK_PATTERN) — **14 de 14**. A trava só aceita leitura do
contrato certo (`revisao_ready._mesmo_contrato`), por isso isto é o que decide se a leitura vale.

## O que este ramo faz

Junta a REVISAO-15 à integração (`git merge --no-ff origin/reparo-fontes-v3`): **zero conflitos**,
os mesmos commits (f5281334, 3384c57d), nenhum ficheiro de revisão novo. A INTEGRA-ONDA2 pode juntar
este SHA ou directamente o `3384c57d` — dá o mesmo.

## O que a trava decide (sem rede, `scripts/reparo/LER-14-DECISAO-DA-TRAVA-V1.json`)

| leitura | fontes | a trava |
|---|---:|---|
| LIMPA | 3 — IT-T7-171 (Periti Agrari), IT-T8-064 (Italus Hortus), IT-T2-157 (AMAP Marche) | deixa a régua decidir: saem READY quando o robô repetir o canário (o gatilho da REVISAO-15 re-mede uma vez a fonte com leitura nova) |
| ALVO_ERRADO | 4 — IT-T3-041, IT-T5-189, IT-T2-135, IT-T3-030 | retidas, motivo no livro |
| SERVICO_OU_INSTITUCIONAL | 5 — IT-T3-047, IT-T3-049, IT-T3-052, IT-T7-219, IT-T2-159 | retidas, motivo no livro |
| LISTA_COMO_ITEM | 1 — IT-T8-060 | retida, motivo no livro |
| NAO_SEI | 1 — IT-T7-168 (AIIA) | retida. A página foi lida; a dúvida é de **intenção**: a entrada é «aiia_news» e o padrão pega congressos (o item é o de 2022). É pergunta para o dono, não para o leitor |

**Prontas: +3.** **Elegíveis para a coleta: NÃO SEI** — READY no curador não é contrato de coleta: a
fonte ainda tem de entrar na tabela do coletor (o caminho da CONTRATO-44 / `onboardar_rotas_provadas`,
com canário ROUTE_PROVEN). No funil do coordenador é o degrau SEM_CONTRATO_DE_COLETA.

## Testes (rede fechada: proxy para 127.0.0.1:9)

- `test_revisao_ready`, `test_reparar_contrato`, `test_canario_detalhe`, `test_contrato_unico`: 87/87.
- `test_abastecimento`, `test_gatilho_discovery`, `test_impasse_b4`: 41/41 aqui e 41/41 na integração sem a junção.

## Writeset

Só o que a REVISAO-15 já trazia (`curadoria/REVISAO-READY-V1.json`, `curadoria/revisao_ready.py`,
`curadoria/gatilho_discovery.py`, `curadoria/test_revisao_ready.py`, `scripts/reparo/R1-REVISAO-15.json`,
relatório §14) + este relatório e `scripts/reparo/LER-14-DECISAO-DA-TRAVA-V1.json`.
