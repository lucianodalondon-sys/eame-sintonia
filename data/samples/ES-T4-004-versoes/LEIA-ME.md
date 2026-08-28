# DUAS VERSÕES DO MESMO DOCUMENTO — por que estão versionadas

`D-003` diz que **dado bruto não é versionado**. Estes arquivos são a exceção declarada,
e a exceção é estreita:

> **Uma versão da qual um CHANGE EVENT depende deixa de ser dado bruto e passa a ser a
> prova do evento.** Sem ela, o evento não é verificável por ninguém — nem por nós.

| arquivo | versão do documento | SHA-256 |
|---|---|---|
| `dc_web_20250528.pdf` | 28/05/2025 | `ad48dc534da2be506b89adde7e2b2dd6f3b69df2511e20c99acdeebe8cf567f2` |
| `dc_web_20260826.pdf` | 26/08/2026 | `cdc389d3ebb3b3b8effdf7397a57aa56805cd8ad8c10037576c83e349eb3e7f7` |

**Fonte:** MAPA — *Denominaciones comunes*,
`https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/sanidad-vegetal/medios-de-defensa-fitosanitaria/registro-productos-fitosanitarios/dc_web.pdf`
(a URL é sempre a mesma; o conteúdo muda. É por isso que o nome do arquivo carrega a data.)

**Como reproduzir a medida e os eventos:**

```
python3 scripts/denominaciones.py data/samples/ES-T4-004-versoes/dc_web_20260826.pdf
```

**Nota de verificação:** o arquivo de 26/08/2026 baixado na MISSÃO 07 é **byte a byte
idêntico** ao baixado na MISSÃO 06. A diferença entre `1.737` e `1.786` linhas é
**inteiramente do leitor**, não da fonte — o que só foi possível afirmar porque as duas
versões estavam guardadas.
