#!/bin/sh
# Monta a cadeia TLS que o host das etichette nao manda.
#
# www.fitosanitari.salute.gov.it envia so a folha e omite a intermediaria
# "TI Trust Technologies OV CA". O que fica versionado aqui e SO a
# intermediaria (2 KB) — o resto da cadeia e o bundle do sistema, que muda com
# o tempo e nao deve virar copia congelada no repositorio.
#
# Nunca desligue a verificacao. O certificado do Ministero e valido; o que
# falta e um elo, e ele esta em recon/ti-trust-intermediate.pem.
set -e
D=$(CDPATH= cd -- "$(dirname -- "$0")/../recon" && pwd)
for CA in "$SSL_CERT_FILE" /root/.ccr/ca-bundle.crt /etc/ssl/certs/ca-certificates.crt; do
  [ -n "$CA" ] && [ -f "$CA" ] && break
done
[ -f "$CA" ] || { echo "sem bundle de CA do sistema" >&2; exit 1; }
cat "$D/ti-trust-intermediate.pem" "$CA" > "$D/it-chain-fix.pem"
echo "$D/it-chain-fix.pem"
