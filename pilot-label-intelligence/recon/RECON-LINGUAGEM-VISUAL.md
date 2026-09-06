# RECON — linguagem visual da casa (para a demo SHADOW)

O portal em `prototype/portal/index.html` esta **CONGELADO** (`prototype/portal/CONGELADO.md`,
decisao D-007). Esta missao NAO o toca. Mas ele define a linguagem visual da casa, e a demo
shadow deve falar a mesma lingua para nao parecer um corpo estranho na apresentacao.

## Paleta herdada

    --bg:#0f1214   fundo
    --pn:#161b1f   painel
    --ln:#232b31   linha
    --tx:#e6edf3   texto
    --dim:#8b98a5  texto secundario
    --ac:#4ea3ff   acento

## O que mais importa herdar: o sistema de selos

O portal ja carrega um sistema de honestidade visual, e ele resolve exatamente o problema
desta missao — mostrar o que e real sem inflar:

    --real:#2ea043  REAL      dado medido na fonte
    --der:#c9a227   DERIVED   calculado a partir de dado real
    --demo:#d1712a  DEMO      forma do produto, nao dado
    --con:#8b5cf6   CONCEPT   ainda nao construido

A demo de rotulos reusa esses selos com o vocabulario desta missao:

| selo | significado aqui |
|---|---|
| REAL | linha lida do PDF oficial, com citacao recuperavel |
| DERIVED | contagem/agregacao sobre linhas reais |
| DEMO | forma de tela sem dado por tras |
| CONCEPT | automacao desenhada, nao ligada |

Regra: nenhum bloco da demo pode ficar sem selo.
