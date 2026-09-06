# LABEL INTELLIGENCE PILOT · ITALIA

Frente isolada. Nao e P0.2. Nao toca `sintonia/canonical`, Passaporte, Universal,
Supabase, motor/43 nem o portal oficial. Nao faz deploy. Tudo vive aqui dentro.

    CANONICAL_READ_ONLY = SIM   (canonical foi LIDO e apontado, nunca escrito)

## O que este piloto responde

O cliente paga alguem para "coletar rotulos". Nao sabemos qual pedaco dessa frase
ele paga. Entao o piloto prova os pedacos, um por um, e a conversa passa a ser
**"quais destes voces pagam hoje?"** — ver `docs/ROI-SUBSTITUICAO.md`.

## Comece por aqui

| arquivo | o que e |
|---|---|
| `ENTREGA-FINAL.md` | o relatorio, gerado dos artefatos |
| `census/RECONCILIACAO.md` | por que "163/163" e "19/163" nunca se contradisseram |
| `demo/label-intelligence.html` | a demo shadow — abra no navegador |
| `AUDITORIA.json` | a recontagem independente das nossas proprias afirmacoes |
| `docs/CONTRATO-DO-ROTULO.md` | as cinco camadas que nunca sao sinonimo |

## As leis que o codigo obedece

    LABEL_DOWNLOADED     != LABEL_STRUCTURED
    TEXT_FOUND           != AUTHORIZED_USE_PROVED
    CAPTURED_AT          != EFFECTIVE_AT
    EXPIRY               != WITHDRAWAL
    CATALOG_PRESENCE     != MARKET_PRESENCE
    PARSER_FAILURE       != REGULATORY_ABSENCE

A ultima e a mais cara. Quando o leitor nao acha a tabela, grava `PARSE_STATE`,
nunca "produto sem usos autorizados".

## Reproduzir do zero

```bash
# 1. registro oficial + historico semanal (60 instantaneos, ~280 MB)
python3 bin/registro_it.py --weeks 60 --end 2026-08-31

# 2. conferir os 163 rotulos contra a linha de base ja lida em canonical
git fetch --depth 1 origin sintonia/canonical
git archive FETCH_HEAD data/samples/IT-ROTULOS-V1 | tar -x -C /tmp/canon
python3 bin/rotulo_reverificar.py \
  --manifesto /tmp/canon/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json \
  --observed-at $(date -u +%F)

# 3. juntar as camadas
python3 bin/consolidar.py \
  --registro registry/snapshots/PROD_FTS_6_20260831.csv \
  --registro-url https://www.dati.salute.gov.it/sites/default/files/opendata/PROD_FTS_6_20260831.csv \
  --pares /tmp/canon/data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json \
  --hoje $(date -u +%F)

# 4. escolher a demo, gerar alertas, montar a tela, auditar, relatar
python3 bin/selecionar_demo.py --por-linha 5
python3 bin/alertas.py --hoje $(date -u +%F)
python3 bin/build_demo.py
python3 bin/auditar.py
python3 bin/relatorio.py
```

## Perguntas do cliente, na linha de comando

```bash
python3 bin/consultar.py cultura vite
python3 bin/consultar.py alvo peronospora
python3 bin/consultar.py cruzar frumento fusarium
python3 bin/consultar.py rotulo 015275      # qual rotulo esta valendo
python3 bin/consultar.py mudou 015275       # esse rotulo mudou?
python3 bin/consultar.py vencendo 90
python3 bin/consultar.py sem-leitura        # o que ainda nao foi lido
python3 bin/consultar.py mudancas
```

## Duas armadilhas de rede, medidas aqui

**O host das etichette manda cadeia TLS incompleta.** Omite a intermediaria
`TI Trust Technologies OV CA`. O portal de dados abertos do mesmo Ministero manda
a cadeia completa, entao a intermediaria que falta num host se pega no outro:
`recon/it-chain-fix.pem`. Nada de `verify=False`.

**O mesmo host manda um `Public-Key-Pins` truncado sem CRLF.** O curl 8 aborta com
`Header without colon`; o wget tolera. Por isso o cliente HTTP dos rotulos e wget
e o do registro e curl — cada um onde funciona, e escrito no docstring de cada
script para ninguem "consertar" de volta.

E o servlet de busca e **intermitente**: a mesma consulta alterna entre a ficha
certa e um erro generico. `bin/rotulo_localizar.py` repete com sessao nova e
espera crescente, e grava `SEARCH_REJECTED` — estado de coleta — em vez de
"sem rotulo".

## O que NAO esta provado

- **Diff historico do proprio rotulo.** A maquinaria roda e rodou sobre os 163.
  Em 7 dias nenhum documento mudou. `VERSION MONITORING READY`,
  `HISTORICAL LABEL DIFF NOT YET PROVED`.
- **Rotulo fisico / foto de embalagem.** Fora desta rota. Nao tentado.
- **Dose em todo o universo.** Ver `ENTREGA-FINAL.md` para o estado real.

## Nao integrar

A demo e SHADOW de proposito. Ao terminar, para. Ver a recomendacao no fim de
`ENTREGA-FINAL.md`.
