# C-JS · as saídas públicas de dados das fontes «JavaScript» existem? (seguimento da D42 (3))

25/09/2026. **Só relatório + proposta de contrato por fonte. NÃO instalado. Nada escrito em Git**
(memória < 5 GB: o commit pediria a cadeia do mapa, que é trabalho pesado).

## Como se pediu

- Portão de egresso por consenso: `source-curator-service-v1/superficie/rede.py --portao-de-egresso IT` → PASS.
- Robots pelo leitor da casa (`curadoria/gate_de_rota.py`, via janela-formas-v1 = produção 7cdb7ea4 + D42);
  Emilia-Romagna pela cópia da medição RFC (`C:/cur/rfc/rede/robots/`), sem pedido novo.
- Teto D38 (5 por domínio) ativo; 2 s por anfitrião. Todos HTTP 200, 2026-09-25 08:57 UTC.

| domínio | pedidos | listados na missão | diferença |
|---|---:|---:|---|
| agricoltura.regione.emilia-romagna.it | 1 | 1 | — |
| agrometeopuglia.it | 2 (robots + `Bollettini.js`) | 2 | — |
| simfito.regione.campania.it | **2** (robots + `/bollettini`) | 1 | **+1**: não havia cópia do robots; o leitor da casa teve de o ir buscar (404 = AUSENTE, permitido pela D39) |

## Por fonte

### IT-T3-013 / IT-T3-028 · Emilia-Romagna, boletins de produção integrada — **EXISTE (JSON público)**

- `GET …/++api++/fitosanitario/difesa-sostenibile/bollettini/bollettini-interprovinciali-di-produzione-integrata-e-biologica-2026`
  → JSON do plone.restapi (13 513 B): `@type Document`, título «Bollettini interprovinciali … 2026»,
  `effective` 2024-01-11, `modified` 2026-02-05, `items_total` 5.
- Os 5 filhos são **sub-documentos por província**, não boletins: Bologna e Ferrara · Forlì-Cesena,
  Ravenna e Rimini · Modena e Reggio Emilia · Parma e Piacenza · Elaborazione modelli previsionali.
- Neste nível **não há** PDF nem `@@download`. **Boletim? NÃO SEI ainda. Data do boletim? NÃO SEI ainda.**
  Ficam um nível abaixo: falta 1 pedido por província (não autorizado, não feito).
- Robots (cópia RFC): `++api++` permitido.

**Proposta de contrato (receita a 2 níveis, API):**
```
FORMA              = LISTA_E_DETALHE (API JSON)
LISTING            = <contentor>/++api++  → items[].@id   (as 4 províncias; «modelli previsionali» à parte)
DETAIL             = <provincia>/++api++  → items[] com @type File/Document, effective, @@download
OUTPUT_TYPE        = PDF (se os filhos forem ficheiros) | HTML (se forem Document) — decidir pela prova
DOCUMENT_ID        = IT-T3-013:<@id do boletim>          (sem hash)
PUBLICATION_TIME   = effective do boletim ; FACT_TIME = UNKNOWN salvo se o título/corpo disser o período
RECOLLECTION       = LISTING mutável, DETAIL imutável
```
Pendente: 1 pedido de prova numa província (ex.: Bologna e Ferrara) para confirmar que os filhos são
boletins com data. Headless não é preciso.

### IT-T2-150 / IT-T2-151 · agrometeopuglia — **EXISTE uma API, mas pede uma chave**

- `Bollettini.js` (6 489 B) lê de `/api/bollettini?api=<drupalSettings.api>&tipologia=Quotidiano`
  e `…&tipologia=Settimanale`, e por província `getBollProvincia(sigla)`.
- Campos devolvidos: `NUMBER`, `DATA_EMISSIONE_FORMAT` (data de emissão), `DATA_VALIDITA_FORMAT`
  (validade), `PATH_COMP` (caminho do PDF: `../`+PATH_COMP se tiver `bollettino-elettronico`,
  senão `http://wwwold.agrometeopuglia.it/opencms/Documenti/`+PATH_COMP).
- **Boletim? SIM (PDF). Data? SIM (emissão e validade)** — segundo o código; a resposta da API **não foi pedida**.
- **O parâmetro `api` não está** no `drupalSettings` da página guardada. Há uma `key` longa ao lado
  do `REMOTE_ADDR` (o nosso IP): muito provavelmente uma chave **por visita, presa ao IP**. NÃO SEI
  se é a mesma coisa que `api`.
- Robots (lido agora pelo leitor da casa): `Bollettini.js` permitido. O script **não guardou** o
  robots.txt em ficheiro, por isso **NÃO SEI** se `/api/` é permitido — perguntar ao leitor por esse
  caminho antes do primeiro pedido à API.

**Proposta de contrato (só depois da decisão do dono):**
```
FORMA              = LISTA_E_DETALHE (API JSON → PDF)
LISTING            = /api/bollettini?api=<CHAVE>&tipologia=Quotidiano|Settimanale
DETAIL             = PDF por PATH_COMP (dois anfitriões: www e wwwold)
OUTPUT_TYPE        = PDF
DOCUMENT_ID        = IT-T2-150:<tipologia>:<NUMBER>
PUBLICATION_TIME   = DATA_EMISSIONE_FORMAT ; FACT_TIME = DATA_VALIDITA_FORMAT
```
**Decisão do dono:** usar uma chave tirada da página em cada visita (presa ao nosso IP) é aceitável?
Se sim: 3 pedidos de prova (página → chave, API, 1 PDF). Se não: fica fora, ou headless (D42).

### IT-T3-026 · SIMfito Campania — **NÃO é saída pública**

- `/bollettini` (2 421 B): título «MTE», aplicação ExtJS (`lib/ext/…`, `app/login.js`, `app/utils.js`).
  É uma aplicação **com login**, não uma página de boletins.
- **Boletim? NÃO (atrás de login). Data? NÃO.**
- Robots: 404 = AUSENTE (permitido pela D39) — mas o muro é o login, não o robots.

**Proposta de contrato:** nenhum. Estado `AUTH` (como as autorizações da Campania, D32) — fora da coleta
pública. Headless não resolve: o problema é a senha, não o JavaScript.

## Resumo

| fonte | saída pública? | boletim | data | próximo passo |
|---|---|---|---|---|
| Emilia-Romagna (013/028) | SIM, JSON | NÃO SEI (1 nível abaixo) | NÃO SEI | 1 pedido por província, depois receita a 2 níveis |
| agrometeopuglia (150/151) | SIM, API com chave | SIM (pelo código) | SIM (pelo código) | decisão do dono sobre a chave por visita |
| SIMfito (026) | NÃO, login | — | — | `AUTH`, fora |

## Provas (fora do Git, com sha256)

| ficheiro | sha256 |
|---|---|
| `C:/cur/cjs/confirmar_js.py` | `dec5e6b594826be7a1d3c3f740f0a1c33bbcbdf2a4fac39071a86ade5d64b57f` |
| `C:/cur/cjs/INDICE.json` | `8aa51c5d6300f2621f62743dd1a8f3b94ffd0f372707c5515a82fb867e55bba7` |
| `C:/cur/cjs/bytes/4f6b71dffef27eb25411.bin` (ER, JSON) | `4f6b71dffef27eb2541139e07cf83f29545885db3e58163d6650057d3fb77a09` |
| `C:/cur/cjs/bytes/888e05885c499f9116c8.bin` (Bollettini.js) | `888e05885c499f9116c8c804b80f9378afc2772fb7b0f514ad0c96e4f5196a03` |
| `C:/cur/cjs/bytes/bac2a9116137905a30a1.bin` (SIMfito) | `bac2a9116137905a30a1e725aae38c3dec3389a11f91383da7d7342141ffb066` |
