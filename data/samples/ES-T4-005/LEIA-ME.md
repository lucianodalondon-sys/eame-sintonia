# PRIMEIRA VERSÃO ARQUIVADA DO REGISTRO ESPANHOL

`ropf_20260829.json.gz` — projeção do export oficial do ROPF
(`POST /regfiweb/Exportaciones/ExportJsonProductos`), timestamp do servidor
`2026-08-29T00:21:08+02:00`, **3.084 registros**.

**É uma projeção, não o export inteiro.** Guardamos os campos que tornam a comparação
com a próxima versão possível: registro, nome, titular, fabricante, planta, formulado,
estado e as datas. Ficaram de fora observações, símbolos de perigo, textos de segurança
e ids internos — que não entram em nenhum change event previsto.

**Esta é a versão A.** `STATUS_CHANGE`, `HOLDER_CHANGE`, `COMPOSITION_CHANGE`,
`DATE_CHANGE` e `MANUFACTURER_CHANGE` estão em `POSSÍVEL, não provado` justamente porque
ainda não existe a versão B. Ver `docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md` §2.

Reproduzir a coleta: `python3 scripts/mapa_regfi.py export`
