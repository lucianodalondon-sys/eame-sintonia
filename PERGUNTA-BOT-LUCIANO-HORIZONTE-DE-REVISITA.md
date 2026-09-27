# PERGUNTA PARA O BOT LUCIANO — até quando se revisita uma matéria que muda?

(CONTRATOS-AJUSTE, 25/09/2026. Não decidido pela bancada: muda uma lei da casa.)

## A pergunta

Hoje a lei é: **uma matéria que o contrato diz que muda (MUTABLE) é revisitada enquanto o índice
do site a mostrar** — com prazo, de X em X dias; sem prazo, em todas as corridas. Nenhuma edição se perde.

A coordenação propôs: **parar de revisitar 28 dias depois da publicação**, com base no atraso
máximo medido na balsamico (27,1 dias).

**Aceita trocar "revisita enquanto o índice a mostrar" por "revisita só até N dias depois da
publicação"? Se sim, com que N, e para todas as fontes que mudam ou só para algumas?**

## O que os números dizem (TTL-MUTABLE-DATAS-T1.json, 52 matérias das 3 fontes de notícia que mudam)

| fonte | matérias | editadas mais de 1 dia depois | edição mais atrasada | perdidas com corte em 28 dias |
|---|---|---|---|---|
| IT-T7-042 balsamico | 12 | 3 | 27,1 dias | **0 de 3** |
| IT-T10-022 zootecnica | 10 | 3 | 7,2 dias | **0 de 3** |
| IT-T7-017 riuniteciv | 30 | 19 | 72,0 dias | **6 de 19** |

Ressalva: cada página só mostra a ÚLTIMA edição. O número de edições é um mínimo.

## O que já foi feito sem mudar a lei

A balsamico recebeu o mesmo **prazo de 3 dias** que a Riunite e a Zootecnica já têm desde a T1.
Continua a revisitar enquanto o índice a mostrar, mas no máximo uma vez a cada 3 dias.
Simulação da T1 para ela: de 9,5 para 3,1 revisitas por corrida diária, 0 edições perdidas,
atraso máximo 2,3 dias.

## O que muda conforme a resposta

- **Não** → fica como está (prazo de 3 dias). Nada a fazer.
- **Sim, N = 28, só a balsamico** → 0 edições perdidas nos dados de hoje; poupa as revisitas
  de matérias com mais de 28 dias que ainda estejam no índice.
- **Sim, N = 28, todas** → a Riunite perde 6 de 19 edições medidas.
- Qualquer "sim" pede: data de publicação lida de cada matéria (hoje só a T1 a extraiu, fora
  do coletor) e uma regra nova em `regras/incrementalidade.mjs::decidirSobreDetalhe`, com testes.
