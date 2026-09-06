# RECON — rede e TLS das fontes oficiais italianas

Medido nesta sessao (container remoto), nao herdado de nota anterior.

## O achado que destrava a rota

`www.fitosanitari.salute.gov.it` — o buscador oficial de etichette — **envia uma
cadeia de certificados incompleta**: manda so a folha, omite a intermediaria
`TI Trust Technologies OV CA`. Por isso curl, requests e qualquer cliente com
verificacao normal falham com `unable to get local issuer certificate`.

Nao e bloqueio do proxy e nao e certificado invalido. E o servidor do Ministero
que esta mal configurado.

    leaf: C=IT, O=Ministero della Salute, CN=www.fitosanitari.salute.gov.it
    (intermediaria ausente)

`www.dati.salute.gov.it` — o portal de dados abertos do mesmo Ministero — envia a
cadeia **completa**, incluindo exatamente a intermediaria que falta no outro host:

    leaf:  C=IT, O=Ministero della Salute, CN=www.salute.gov.it
    inter: C=IT, O=TI Trust Technologies S.R.L., CN=TI Trust Technologies OV CA
    (emitida por USERTrust RSA Certification Authority)

## A correcao

Completar a cadeia, **nunca** desligar a verificacao:

    openssl s_client -connect www.dati.salute.gov.it:443 \
      -servername www.dati.salute.gov.it -showcerts \
      | extrair a 2a certificado  > ti-trust-intermediate.pem
    cat ti-trust-intermediate.pem /root/.ccr/ca-bundle.crt > it-chain-fix.pem
    curl --cacert it-chain-fix.pem https://www.fitosanitari.salute.gov.it/...

Depois disso o host responde HTTP normalmente (404 de rota errada em vez de erro
de TLS). `verify=False` nao foi usado em lugar nenhum e nao deve ser.

O arquivo `it-chain-fix.pem` esta ao lado deste documento.

## Estado medido dos hosts

| host | resultado |
|---|---|
| www.dati.salute.gov.it | HTTP 200 |
| www.fitosanitari.salute.gov.it | TLS quebrado ate a correcao acima; depois responde |
| www.adama.com/italia/it | HTTP 403 |

TLS_FIX_REQUIRED = SIM
TLS_VERIFICATION_DISABLED = NAO
