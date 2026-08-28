# CONTRATOS DAS FONTES — o que cada fonte promete, e o que fazer quando ela quebra

**Data:** 2026-08-29 · **MISSÃO 08**

Este documento não repete o `ATLAS-DE-FONTES-EAME.md`, que registra **o que a fonte tem**.
Aqui está **como se busca, o que se espera de volta, e o que acontece quando não vem**.

> Uma fonte sem contrato é uma fonte que só funciona enquanto a pessoa que a descobriu
> estiver por perto.

---

## SAÚDE DE FONTE — definição objetiva

Implementada em `scripts/source_health.py`, não em prosa.

| estado | condição |
|---|---|
| **HEALTHY** | respondeu · o tipo de conteúdo bate · **todos** os campos do contrato presentes · a chave de identidade existe, é única e não é vazia · volume dentro da faixa esperada |
| **DEGRADED** | usável, mas o contrato mudou: campo novo, identidade duplicada, volume fora de ±10% |
| **FAILED** | não respondeu · respondeu outro tipo · lista vazia · campo do contrato ausente · identidade ausente ou vazia |
| **UNKNOWN** | não foi verificada nesta execução. **Não é sinônimo de saudável** |

**`HTTP 200` não basta para HEALTHY.** O caso que obriga a regra é o 200 com página de
erro: status bom, corpo lixo. Por isso a checagem é de **schema e identidade**, nunca de
status. E **lista vazia é `FAILED`**, nunca "zero resultados" — a diferença entre "não há"
e "não consegui ver" é a diferença entre um relatório e uma mentira.

---

## FR-T4-001 · ANSES E-Phy — `CRITICAL`

```
SOURCE_ID                 FR-T4-001
OWNER                     ANSES (França), publicado via data.gouv.fr
COUNTRY                   FRANCE
PRIMARY/SECONDARY         PRIMARY · OPEN DATA
PURPOSE                   BQ1, BQ3, CASE-014, cross-market cereal
CANONICAL_URL             https://www.data.gouv.fr/api/1/datasets/575e9fac88ee38072a640390/
RETRIEVAL_METHOD          scripts/ephy.sh download [destino]
HTTP_METHOD               GET (API do catálogo) + GET (ZIP resolvido)
PARAMETERS                nenhum — o id do dataset é fixo
AUTH_REQUIRED             não
OUTPUT_TYPE               ZIP com CSV UTF-8, separador ';'
EXPECTED_FIELDS           numero AMM · nom produit · titulaire · Substances actives ·
                          Etat d'autorisation · Numéro AMM du produit de référence
IDENTITY_KEYS             numero AMM
DATE_FIELD                Date de première autorisation · Date de retrait du produit
VERSION_FIELD             last_update do dataset (API) — a URL do recurso muda a cada semana
UPDATE_BEHAVIOR           semanal, substituição integral
HISTORICAL_OR_FORWARD     FORWARD-ONLY — o dump só traz o estado de hoje
EXPECTED_FAILURES         reset de conexão transitório (observado no cold start da M08);
                          mudança do título do recurso quebra o seletor "zip + utf8"
FAIL_CLOSED_RULE          `set -euo pipefail` + retry exponencial 4×; sem CSV, a cadeia
                          levanta ChainFailure e não devolve número
FALLBACK                  nenhum equivalente. O E-Phy é o próprio open data.
ARCHIVE_REQUIREMENT       **obrigatório e semanal** — é FORWARD-ONLY; o que não for
                          arquivado deixa de existir
DEPENDENT_CASES           CASE-014 · CASE-011 · cross-market cereal
DEPENDENT_CLAIMS          DECK safe-claim 1 e 8
```

**Estabilidade da rota: ALTA.** Único identificador que precisa ser estável é o do dataset,
e ele é. O nome do recurso muda toda semana e por isso **não** está escrito no script.

## ES-T4-005 · MAPA / ROPF — `CRITICAL`

```
SOURCE_ID                 ES-T4-005
OWNER                     MAPA — D.G. de Sanidad de la Producción Agroalimentaria
COUNTRY                   SPAIN
PRIMARY/SECONDARY         PRIMARY · **PUBLIC APPLICATION ROUTE**
PURPOSE                   BQ1, BQ3, CASE-015, modelo de identidade
CANONICAL_URL             https://servicio.mapa.gob.es/regfiweb/
RETRIEVAL_METHOD          scripts/mapa_regfi.py {producto|export|total|divergencia}
HTTP_METHOD               GET (grade, ficha, PDF) · POST (export)
PARAMETERS                NumRegistro · Titular · Fabricante · IdEstado · IdSustancia …
                          (export: dataDto[<filtro>])
AUTH_REQUIRED             não
OUTPUT_TYPE               HTML (grade) · JSON (ficha e export) · PDF (ficha oficial)
EXPECTED_FIELDS           numRegistro · nombre · titular · fabricante · fabrica ·
                          formulado · estado · tramite · 6 pares de datas (48 campos)
IDENTITY_KEYS             numRegistro (3.084 únicos) · idProducto (interno, volátil)
DATE_FIELD                fechaInscripcion · fechaCaducidad · fechaModificacion ·
                          fechaLimiteVenta · fechaTramite
VERSION_FIELD             `Fecha` no envelope do export + o aviso de atualização na home
UPDATE_BEHAVIOR           semanal ("Última actualización de la base de datos: <data>")
HISTORICAL_OR_FORWARD     FORWARD-ONLY, e pior: **sobrescreve o trâmite**. O histórico só
                          existe nas versões que nós arquivarmos
EXPECTED_FAILURES         rota renomeada · `IdEstado` mudar de semântica · grade voltar a
                          exigir sessão · export passar a exigir antiforgery token
FAIL_CLOSED_RULE          contrato COMPLETO de 48 campos: campo novo → DEGRADED, campo
                          ausente → FAILED. Ficha não encontrada levanta, não devolve vazio
FALLBACK                  **nenhum equivalente.** Ver FALHA-DE-FONTE-ESPANHA.md
ARCHIVE_REQUIREMENT       **obrigatório.** Uma versão arquivada (2026-08-29). Enquanto
                          houver só uma, o estado é BASELINE_ESTABLISHED
DEPENDENT_CASES           CASE-015 · cross-market cereal (perna ES)
DEPENDENT_CLAIMS          safe-claims 10, 13 e 14
```

### As quatro rotas, medidas

| rota | input | output | status | content-type | paginação | identidade | depende de JS? | depende de hidden input? | comportamento na falha |
|---|---|---|---|---|---|---|---|---|---|
| `Productos/ProductosGrid` | filtros por query string | HTML da grade | 200 | text/html | **5 por página**, total no rodapé (`de un total de N`) | `data-id` = idProducto | **não** para consumir; sim para descobrir | sim (rota vem de `pathProductos`) | filtro inválido → grade vazia, **não** erro |
| `Productos/GetProductoById` | `idProducto` | JSON de 48 campos | 200 | application/json | — | numRegistro | não | sim | id inexistente → JSON nulo |
| `Productos/ExportFichaProductoPdfGet` | `idProducto` | PDF, 5 páginas | 200 | application/octet-stream | — | doc `<id>-<edição>` | não | sim | id inexistente → PDF vazio/erro |
| `Exportaciones/ExportJsonProductos` | `dataDto[...]` (POST) | JSON com `Contenido` (string) + `Fecha` | 200 | application/json | **nenhuma** — devolve tudo | numRegistro | não | sim | filtro vazio → conjunto completo |

> **Não é uma API oficial.** O MAPA não documenta nenhuma destas rotas como API pública.
> O termo correto é **PUBLIC APPLICATION ROUTE**: são as chamadas que o navegador de
> qualquer visitante faz, declaradas em `<input type="hidden">` na própria página e em
> `/regfiweb/js/site.min.js`. Chamá-las de API sugere um compromisso de estabilidade que
> o MAPA não assumiu.

### `IdEstado` — o filtro e o campo respondem perguntas diferentes

```
IdEstado=1 ("VIGENTE") == Estado == 'Vigente'
                          OR (Estado == 'Cancelado' AND fechaLimiteVenta >= hoje)
```

| número | responde |
|---|---|
| **1.998** (filtro) | *quantos produtos ainda podem ser legalmente comercializados hoje* |
| **1.993** (campo) | *quantas autorizações estão em vigor hoje* |

Os cinco da diferença — `16192`, `25454`, `ES-00195`, `ES-01106`, `ES-01107` — são
cancelados dentro do **prazo legal de escoamento**. Verificado por **igualdade de
conjunto**, não de contagem. E **1.998 tem data de validade**: cai sozinho quando o
último prazo vencer (03 e 30/09/2026).

## IT-T4-001 · Ministero della Salute — `CRITICAL`

```
SOURCE_ID                 IT-T4-001
OWNER                     Ministero della Salute (Itália)
COUNTRY                   ITALY
PRIMARY/SECONDARY         PRIMARY · WEB (arquivo estático datado)
PURPOSE                   BQ1, BQ3, CASE-014, cross-market cereal
CANONICAL_URL             https://www.dati.salute.gov.it/it/dataset/fitosanitari/
RETRIEVAL_METHOD          scripts/chain.py run it-prothioconazole — o nome datado do
                          arquivo é DESCOBERTO na página do dataset, nunca chutado
HTTP_METHOD               GET (página) + GET (CSV)
PARAMETERS                nenhum
AUTH_REQUIRED             não
OUTPUT_TYPE               CSV ';', 17.695 linhas, ~4,6 MB
EXPECTED_FIELDS           num_registrazione · denominazione_prodotto · ragione_sociale ·
                          sostanze_attive · stato_amministrativo ·
                          data_scadenza_autorizzazione · motivo_della revoca
IDENTITY_KEYS             num_registrazione
DATE_FIELD                data_registrazione · data_scadenza_autorizzazione ·
                          data_decreto_revoca · data_decorrenza_revoca
VERSION_FIELD             **a data no nome do arquivo** (`PROD_FTS_6_20260824.csv`)
UPDATE_BEHAVIOR           novo arquivo datado; os antigos parecem permanecer publicados
HISTORICAL_OR_FORWARD     traz revogação e motivo — é a fonte T4 com mais história nativa
EXPECTED_FAILURES         mudança do padrão do nome · mudança do HTML da página (o regex
                          de descoberta é a dependência real) · 200 com HTML no lugar do CSV
FAIL_CLOSED_RULE          se o regex não achar nenhum `PROD_FTS_*.csv`, levanta. Se o corpo
                          começar com `<html`, levanta.
FALLBACK                  o mesmo arquivo em `.json` e `.xml`, na mesma pasta
ARCHIVE_REQUIREMENT       recomendável, não crítico — o nome datado já é uma versão
DEPENDENT_CASES           CASE-014 · cross-market cereal (perna IT)
DEPENDENT_CLAIMS          safe-claim 1
```

**Estabilidade da rota: MÉDIA.** A URL da página é estável; o nome do arquivo não, e por
isso é descoberto. A dependência real é o **HTML da página**, não o dado.

## ES-T3-001 · RAIF Andalucía — `CRITICAL`

```
SOURCE_ID                 ES-T3-001
OWNER                     Junta de Andalucía
COUNTRY                   SPAIN (Andalucía)
PRIMARY/SECONDARY         PRIMARY · OPEN DATA (CKAN), CC BY 4.0
PURPOSE                   BQ2, CASE-013, CASE-008, CASE-012
CANONICAL_URL             https://www.juntadeandalucia.es/datosabiertos/portal/api/3/
                          action/package_show?id=raif
RETRIEVAL_METHOD          CKAN → ZIP → XML. **PASSO MANUAL**: a URL que o CKAN devolve
                          aponta para `gdc-pdpopendata-ckan.paas.junta-andalucia.es`,
                          host inalcançável daqui; trocar por `www.juntadeandalucia.es`
                          mantendo o caminho
HTTP_METHOD               GET
AUTH_REQUIRED             não
OUTPUT_TYPE               ZIP com XML (Access export; nomes de tag em `_x00NN_`)
EXPECTED_FIELDS           PROVINCIA · MUNICIPIO · CODPARCELA · FECHA ·
                          "1702 Repilo: % Hojas  con Repilo Visible" (52 campos)
IDENTITY_KEYS             CODPARCELA + FECHA
DATE_FIELD                FECHA
VERSION_FIELD             atributo `generated` na raiz do XML + a data no título do recurso
UPDATE_BEHAVIOR           semanal durante a safra
HISTORICAL_OR_FORWARD     **HISTÓRICO** — 2006–2026 no mesmo pacote. É a única fonte
                          crítica que não exige arquivamento para ter história
EXPECTED_FAILURES         host do CKAN mudar de novo · nome de campo mudar (os nomes têm
                          espaço duplo e número de ordem: `1702 Repilo: % Hojas  con…`)
FAIL_CLOSED_RULE          zero leituras do campo levanta — "sem doença" e "sem dado" não
                          podem produzir a mesma saída
FALLBACK                  visor web do RAIF (consulta, não dump)
ARCHIVE_REQUIREMENT       baixo — a fonte republica a série inteira
DEPENDENT_CASES           CASE-013 · CASE-008 · CASE-012
DEPENDENT_CLAIMS          safe-claims 4, 5, 6 e 12
```

## EU-T4-001 · CELLAR / Publications Office — `CRITICAL`

```
SOURCE_ID                 EU-T4-001
OWNER                     Publications Office of the EU
COUNTRY                   EUROPE
PRIMARY/SECONDARY         PRIMARY · OPEN DATA (SPARQL + content negotiation)
PURPOSE                   BQ1, BQ3, CASE-014
CANONICAL_URL             https://publications.europa.eu/webapi/rdf/sparql
RETRIEVAL_METHOD          scripts/cellar.sh {sparql|act|substances}
HTTP_METHOD               GET
PARAMETERS                query SPARQL · CELEX · iso3 do idioma
AUTH_REQUIRED             não
OUTPUT_TYPE               JSON (SPARQL) · XHTML (texto integral)
EXPECTED_FIELDS           CELEX · data · título · texto integral
IDENTITY_KEYS             CELEX
DATE_FIELD                data do ato
VERSION_FIELD             o próprio CELEX é imutável
UPDATE_BEHAVIOR           acervo cumulativo — atos não são reescritos
HISTORICAL_OR_FORWARD     **HISTÓRICO por natureza**
EXPECTED_FAILURES         timeout do endpoint SPARQL · negociação de conteúdo devolver
                          o idioma errado sem avisar
FAIL_CLOSED_RULE          exigir `Accept-Language` iso3 e conferir o idioma recebido
FALLBACK                  EUR-Lex por CELEX (mesma casa, outra rota)
ARCHIVE_REQUIREMENT       baixo — o acervo é estável
DEPENDENT_CASES           CASE-014 · CASE-011
DEPENDENT_CLAIMS          safe-claims 1 e 3
```

---

## ASSIMETRIA — três verdes não são o mesmo verde

| | rota | versão vem de | histórico nativo | arquivamento | estabilidade |
|---|---|---|---|---|---|
| **FR** | dump aberto, id de dataset fixo | API do catálogo | **não** (forward-only) | **obrigatório semanal** | **ALTA** |
| **ES** | rota da aplicação | envelope do export | **não**, e sobrescreve trâmite | **obrigatório** | **MÉDIA-BAIXA** |
| **IT** | arquivo estático datado | **o nome do arquivo** | sim (revogações) | recomendável | MÉDIA |
| **RAIF** | CKAN + troca manual de host | atributo do XML | **sim, 20 anos** | baixo | MÉDIA |
| **EU** | SPARQL público | o CELEX é imutável | **sim** | baixo | ALTA |

**A assimetria não é de qualidade do fato — é de rota e de história.** Publicar as cinco
como "fonte oficial verificada" apagaria a diferença que decide o risco operacional.
