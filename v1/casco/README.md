# CASCO — a ferramenta

Standalone. Abre no navegador, nao depende de servidor, nao toca o portal oficial.

    sh v1/casco/build.sh     # monta label-intelligence.html de shell + css + js + payload

O HTML e **gerado**: nenhum numero e digitado nele. Se o payload mudar, a tela muda.

## As nove telas

| tela | responde |
|---|---|
| O QUE MUDOU | o que mudou entre dois instantaneos oficiais, e o que apenas continua valendo |
| PRODUTO 360 | tudo o que sabemos de um produto, e o que nao sabemos |
| LINHA DO TEMPO | as 54 versoes arquivadas, e a diferenca entre documento, campo e evento |
| CULTURA x ALVO | quais produtos tem uso provado em X, com a classe de evidencia |
| CALENDARIO | o que vence em 30/90/180 dias e 12 meses, so com data da fonte |
| POR AREA | quem pode precisar olhar, com a regra que autoriza |
| FILA DE REVISAO | o que a maquina recusou adivinhar |
| COBERTURA | nove coberturas separadas, nunca um numero unico |
| BUSCA | consulta sobre os intelligence objects, nunca sobre PDF cru |

A evidencia nao e uma tela: e uma gaveta que abre de qualquer afirmacao material,
em um clique, com fonte, documento, hash, local, regra e parser.

## Tres coisas que o casco NAO faz

**Nao interpreta documento.** Ele nunca abre PDF nem CSV. Consome os intelligence
objects que a inteligencia ja resolveu. Se um campo nao existe, ele viaja como
`NOT_KNOWN` ate a tela.

**Nao preenche vazio.** Todo token de ignorancia (`NOT_KNOWN`, `NOT_PROVED`,
`NOT_PRESERVED`, `NOT_PRESENT`, `UNKNOWN`) e renderizado com o proprio nome, em
roxo. Nao existe "-", "0" ou "N/A" significando "nao sei" nesta interface.

**Nao emite acao.** O maximo que aparece e `RECOMMENDED_REVIEW`, que e convite a
olhar. Roteamento diz quem pode precisar ver, nunca o que fazer, e cada estado
aponta a regra `C-*` que o autoriza.
