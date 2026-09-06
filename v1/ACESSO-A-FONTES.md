# ACESSO AS FONTES — medido nesta sessao, nao lembrado

Registro exigido pela decisao operacional de nao migrar. Tudo abaixo foi medido
agora, neste ambiente, com HTTP real.

## De onde este ambiente sai

    IP      160.79.106.128
    ORG     AS396982 Google LLC
    LOCAL   Columbus, Ohio, US

Isto importa por um motivo so: o ambiente sai dos **Estados Unidos**, e mesmo
assim as tres fontes oficiais italianas respondem normalmente. E evidencia
direta contra bloqueio geografico nas fontes que a Label Intelligence usa.

## As fontes que a ferramenta precisa

| # | fonte | resultado agora |
|---|---|---|
| 1 | `dati.salute.gov.it` — CSV do registro oficial | **HTTP 200**, 4.594.276 bytes |
| 2 | `fitosanitari.salute.gov.it` — buscador de etichette | **OK**, 46.542 bytes |
| 3 | `EtichettaServlet` — PDF da etichetta | **OK**, 459.625 bytes, comeca com `%PDF-` |

    GEO_BLOCK_PROVADO_NAS_FONTES_OFICIAIS = NAO
    VPN_NECESSARIA_PARA_A_MISSAO          = NAO

A fonte 2 exige completar a cadeia TLS (`bin/chain.sh`), porque o servidor do
Ministero omite a intermediaria. Isso e configuracao do servidor deles, nao
bloqueio, e ja esta resolvido.

## A unica fonte que falha, e o que ela e

    SOURCE          = site COMERCIAL da ADAMA Italia
    URL             = https://www.adama.com/italia/it
    WHAT_IS_MISSING = catalogo comercial e materiais de produto do proprio
                      fabricante. NAO e fonte regulatoria e NAO alimenta nenhum
                      numero desta ferramenta.
    ACCESS_FAILURE  = HTTP 403 "Access Denied", com corpo generico e
                      Reference # de WAF
    VPN_MAY_HELP    = UNKNOWN

### Por que `UNKNOWN` e nao `YES`

Tres medidas, e nenhuma delas sustenta bloqueio geografico:

1. **O cabecalho denuncia o WAF.** A resposta traz `server-timing: ak_p; desc=...`,
   assinatura da Akamai, com `x-robots-tag: noindex, nofollow` e um
   `Reference #`. E resposta de bot manager, nao de filtro de pais.
2. **Bloqueia tudo, nao so o conteudo italiano.** `adama.com/`, `adama.com/en` e
   `adama.com/italia/it` devolvem 403 identico. Se fosse geo, a versao `/en`
   teria respondido de um IP americano.
3. **Nao e caracteristica do pais.** No mesmo minuto, `corteva.it` respondeu 301
   normalmente; `syngenta.it` tambem devolveu 403. Ou seja: o padrao segue o
   fornecedor de WAF, nao a geografia.

Uma VPN italiana troca o IP, mas nao troca a impressao digital de cliente
automatizado, que e o que a Akamai mede. Pode ajudar se a regra for de reputacao
de IP; nao ajuda se for de comportamento. **Nao sabemos, e por isso fica
`UNKNOWN`.**

    FALHA DE ACESSO != AUSENCIA
    403 DE WAF      != GEO_BLOCK

## Consequencia para a missao

Nenhuma. As tres fontes oficiais estao acessiveis, e o site comercial nao
alimenta nenhum campo da ferramenta. Nao ha coleta pendente que justifique
missao local com VPN.

Se um dia fizer falta o catalogo comercial — que seria contexto, nunca prova
regulatoria — a linha acima ja esta preenchida com o que se sabe e com o que
nao se sabe.
