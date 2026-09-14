# CONTRATOS DAS FONTES — o que cada fonte promete, e o que fazer quando ela quebra

**Data:** 2026-08-29 · **MISSÃO 08**

Este documento não repete o `ATLAS-DE-FONTES-EAME.md`, que registra **o que a fonte tem**.
Aqui está **como se busca, o que se espera de volta, e o que acontece quando não vem**.

> Uma fonte sem contrato é uma fonte que só funciona enquanto a pessoa que a descobriu
> estiver por perto.

---

## SAÚDE DE FONTE — definição objetiva

Implementada em `medidas/source_health.py`, não em prosa.

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
RETRIEVAL_METHOD          coleta/ephy.sh download [destino]
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
RETRIEVAL_METHOD          coleta/mapa_regfi.py {producto|export|total|divergencia}
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
RETRIEVAL_METHOD          provas/chain.py run it-prothioconazole — o nome datado do
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
RETRIEVAL_METHOD          coleta/cellar.sh {sparql|act|substances}
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

## IT-T10-001 · ARPAV — venda declarada de fitossanitários no Vêneto — `IMPORTANT`

A primeira fonte desta casa que mede **movimento de produto**, e não autorização de produto.

```
SOURCE_ID                 IT-T10-001
OWNER                     ARPAV, por delegação da Regione del Veneto
COUNTRY                   ITALY — **apenas a região do Vêneto**
PRIMARY/SECONDARY         PRIMARY · OPEN DATA (CC BY 4.0)
PURPOSE                   X-013 · pacote de rota do Field Sales · inteligência de mercado
                          regional (quem está forte onde, e onde há espaço)
CANONICAL_URL             https://www.arpa.veneto.it/dati-ambientali/open-data/fitosanitari
RETRIEVAL_METHOD          py coleta/canal_mercado.py --coletar --ano AAAA
HTTP_METHOD               GET direto no CSV
                          .../vendite-fitosanitari/vendita_agrofarmaci_veneto_AAAA.csv/@@download/file
PARAMETERS                só o ano, no caminho do ficheiro
AUTH_REQUIRED             não
BASE_LEGAL                D.Lgs 150/2012 art. 16 — o titular da autorização de venda declara
                          até 28/02 do ano seguinte, pelo portal ARPAV Web FAS
OUTPUT_TYPE               CSV UTF-8 com BOM, separador ',', decimal '.'
EXPECTED_FIELDS           Provincia di vendita · N. Reg. · Prodotto fitosanitario venduto ·
                          Quantità (Kg o litri)
IDENTITY_KEYS             (provincia, num_registrazione) — e é `num_registrazione` que liga
                          esta fonte ao registro IT-T4-001, com casamento medido de 100%
DATE_FIELD                nenhum por linha. O ano é do ficheiro inteiro
VERSION_FIELD             não existe campo de versão: a versão é o **sha256 do ficheiro**
UPDATE_BEHAVIOR           anual, substituição integral por ano
HISTORICAL_OR_FORWARD     acervo por ano na própria página (histórico), mas cada ano é um
                          ficheiro que pode ser reescrito sem aviso → **arquivar**
EXPECTED_FAILURES         · rodapé: as últimas linhas são NOTA da fonte (base legal e aviso
                            de carregamento), não dado — descartadas com EXCLUSION_REASON
                            `RODAPE_DA_FONTE` e preservadas no ledger;
                          · acento no cabeçalho (`Quantità`) — a conferência normaliza sem
                            acento, senão reprova uma fonte sã;
                          · decimal com PONTO: tratar ponto como separador de milhar
                            multiplica o volume por mil. Já aconteceu nesta casa, na leitura
                            manual anterior ao coletor;
                          · 200 com HTML no lugar do CSV
FAIL_CLOSED_RULE          saúde por SCHEMA e IDENTIDADE, nunca por HTTP 200: cabeçalho
                          esperado, província dentro do conjunto do Vêneto, chave presente.
                          Lista vazia é FAILED, nunca «zero vendas». Reprovando, o coletor
                          levanta SystemExit e NÃO escreve tabela nenhuma
FALLBACK                  nenhum. Outras regiões italianas publicam o equivalente? **NÃO SEI**
ARCHIVE_REQUIREMENT       **obrigatório** — bruto no collection-store, versão = sha256
DEPENDENT_CASES           X-013 · pacote RTV por província
DEPENDENT_CLAIMS          nenhuma claim de share em valor pode depender desta fonte:
                          ela mede VOLUME. Quota em valor continua NÃO SEI
O_QUE_NAO_PROVA           quem comprou · qual revenda vendeu · preço · valor · cultura de
                          destino · onde foi aplicado · quota de mercado
```

---

## IT-T10-003 · ISTAT — distribuição por província, país inteiro — `IMPORTANT`

```
SOURCE_ID                 IT-T10-003
OWNER                     ISTAT
COUNTRY                   ITALY — nação + 24 recortes regionais + 111 províncias
PRIMARY/SECONDARY         PRIMARY · SDMX aberto
PURPOSE                   onde há mercado, de que tipo, fora do Vêneto
CANONICAL_URL             https://esploradati.istat.it/SDMXWS/rest/data/IT1,101_22_DF_DCSP_FITOSANITARI_1,1.0/all
RETRIEVAL_METHOD          py coleta/mercado_italia.py --coletar
HTTP_METHOD               GET com `Accept: application/vnd.sdmx.data+csv;version=1.0.0;labels=both`
PARAMETERS                startPeriod (a casa usa 2015)
AUTH_REQUIRED             não
OUTPUT_TYPE               CSV SDMX rotulado
EXPECTED_FIELDS           REF_AREA · DATA_TYPE · PLANT_PROTECTION_PROD · LEVEL_OF_TOXICITY ·
                          TIME_PERIOD · OBS_VALUE
IDENTITY_KEYS             (REF_AREA, TIME_PERIOD, PLANT_PROTECTION_PROD, LEVEL_OF_TOXICITY)
DATE_FIELD                TIME_PERIOD (ano)
VERSION_FIELD             não há: a versão é o sha256 do ficheiro
UPDATE_BEHAVIOR           anual, acervo cumulativo
HISTORICAL_OR_FORWARD     histórico — a série inteira volta a cada pedido
EXPECTED_FAILURES         · **a armadilha da toxicidade**: cada combinação aparece 4 vezes
                            (ALL · NC · HARM · TOX). Sem filtrar `LEVEL_OF_TOXICITY = ALL`,
                            o número sai **28× menor** e nada na tela avisa;
                          · o túnel de saída fecha em resposta grande (~7 MB) — 3 tentativas;
                          · `Accept` errado devolve **406** com a lista dos aceites;
                          · dataflow com id antigo devolve **404** dizendo que não achou o DSD
FAIL_CLOSED_RULE          conferência de schema + identidade: campos do contrato presentes e
                          **pelo menos 100 territórios**. Lista vazia é FAILED. Linha fora do
                          indicador em kg ou fora de toxicidade ALL é descartada COM motivo,
                          nunca somada
FALLBACK                  nenhum equivalente nacional conhecido
ARCHIVE_REQUIREMENT       recomendável — o acervo é estável, mas a rota já mudou de domínio
DEPENDENT_CASES           mapa nacional de demanda · prova cruzada do Vêneto
DEPENDENT_CLAIMS          nenhuma claim de MARCA pode depender desta fonte: ela mede categoria
O_QUE_NAO_PROVA           marca · produto · titular · quem vendeu · quem comprou · preço ·
                          aplicação (distribuído ≠ aplicado)
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
| **IT-T10** | CSV estático por ano | **o sha256 do ficheiro** | por ano, reescrevível | **obrigatório** | MÉDIA |
| **ISTAT** | SDMX aberto | **o sha256 do ficheiro** | **sim, a série inteira** | recomendável | ALTA |

**A assimetria não é de qualidade do fato — é de rota e de história.** Publicar as cinco
como "fonte oficial verificada" apagaria a diferença que decide o risco operacional.
