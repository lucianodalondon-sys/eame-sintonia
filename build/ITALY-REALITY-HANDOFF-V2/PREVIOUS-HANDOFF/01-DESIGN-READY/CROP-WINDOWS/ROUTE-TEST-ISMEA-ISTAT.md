# TESTE DE ROTA — ISMEA / ISTAT a partir deste ambiente

## 0. IP de saída (confirmado)

`curl -s https://ipinfo.io/json` →

```json
{"ip":"179.172.231.127","hostname":"179-172-231-127.user.vivozap.com.br",
 "city":"São Paulo","region":"São Paulo","country":"BR",
 "org":"AS26599 TELEFÔNICA BRASIL S.A"}
```

É **exatamente o IP citado no bloqueio da ISMEA**. Linha residencial Vivo, São Paulo, Brasil. Não é IP de datacenter.

## 1. Tabela rota × HTTP × bytes × veredito

| # | Rota testada | HTTP daqui | Bytes | Veredito |
|---|---|---|---|---|
| 1 | `https://www.ismea.it/` | **404** (corpo "Blocked") | 7.891 | **BLOQUEIO POR IP.** Barracuda WAF, IP de origem 20.250.13.178 |
| 2 | `https://www.ismeamercati.it/` | **000** (timeout TCP, 23 s) | 0 | Rota de rede não fecha handshake. Site **está no ar** (ver §2) |
| 3 | `https://esploradati.istat.it/` | **000** — 9/9 tentativas, `time_connect=0.000` | 0 | **Handshake TCP nunca abre daqui.** Resolve `01a-filtro.istat.it` / 193.204.90.13 |
| 4 | `https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1` | **000** — 3/3 | 0 | Mesma parede. A API SDMX mora atrás do mesmo host |
| 5 | `https://www.regione.veneto.it/` | **500** (1 vez, corpo real) / **000** (5 vezes) | 49.688 / 0 | Rota instável daqui. Site **está no ar** (ver §2) |
| 6 | `https://sdmx.istat.it/SDMXWS/rest/dataflow/IT1` | **302 → `https://sdmx.istat.it`** (loop) | 0 | Endpoint SDMX legado desativado. Não é bloqueio: é aposentadoria |
| 7 | `https://dati.istat.it/` | **302 → `avvisi.istat.it/IdotStat/`** | 608 | Aviso de migração, sem dado |
| 8 | `https://avvisi.istat.it/IdotStat/` | **200** | 608 | Alcançável, mas só o aviso |
| 9 | `https://www.istat.it/` | **200** | 268.391 | **FUNCIONA** |
| 10 | `https://www.istat.it/statistiche-per-temi/agricoltura/` | **200** | 213.185 | **FUNCIONA** (páginas/publicações, não cubo de dados) |
| 11 | `https://www.dati.gov.it/` | **200** | 258.152 | **FUNCIONA** |
| 12 | CKAN `dati.gov.it` `package_search?q=ismea` | **200** | 224 | Fonte alcançada, `"count": 0`. Idem `organization_list?q=ismea` → `[]` |
| 13 | **Eurostat** `aei_fm_salpest09` (venda de defensivos, IT) | **200** | 38.214 | **FUNCIONA** — JSON, `updated 2026-08-11`, série 2011–2024 |
| 14 | **Eurostat** `apro_cpsh1` (produção vegetal, IT) | **200** | 19.369 | **FUNCIONA** — `updated 2026-08-28` |
| 15 | **Eurostat** `apro_cpshr` (produção por região NUTS-2, ITH3 = Veneto) | **200** | 30.562 | **FUNCIONA** — `updated 2026-05-28` |
| 16 | FAOSTAT `faostatservices.fao.org/api/v1` | **401** | 28 | `Missing Authorization Header` — exige chave. Não seguido (lei 7) |
| 17 | Proxy `r.jina.ai` → ismea.it | **403** | 5.676 | Falhou **no proxy** (desafio Cloudflare), não na ISMEA |
| 18 | Proxy `api.allorigins.win` → 3 alvos | **522** ×3 | 16 | Proxy fora do ar. Inconclusivo |
| 19 | Proxy `api.codetabs.com` → 3 alvos | **522** ×3 | 16 | Proxy fora do ar. Inconclusivo |
| 20 | Wayback `esploradati.istat.it` (CDX 2024+) | 302 / `warc/revisit` | 515–770 | **Sem conteúdo.** Só a casca do SPA. Zero snapshot em 2026 |
| 21 | Wayback `ismea.it/banca-delle-terre` `20260703175448` | **200** | 38.263 | **Conteúdo REAL de 2026**, 4× "Banca delle Terre" |
| 22 | Wayback `ismea.it/Comunicati-Stampa` `20260117091502` | 200 | 2.736 | **Falso positivo:** contém `captcha` 3×. É a página de desafio arquivada |
| 23 | Wayback `ismeamercati.it` snapshot mais novo `20260605025951` | 301 | 634 | Só o redirect. Digest `3I42H3S6…` = corpo vazio |

## 2. A prova de que o problema é o IP, e não a fonte

Medi as mesmas URLs a partir de nós em outros países (check-host.net, `permanent_link` público):

**`www.ismea.it`** — relatório `49b33a7dk5e5`
```
it2 (Itália, Milão)   → 301  ✅       de2 (Alemanha)  → 301  ✅
fi1 (Finlândia)       → 301  ✅       us4 (EUA/Miami) → 301  ✅
ca1 (Canadá, Vancouver) → 404  ❌  ← mesmo código que eu recebo
```
A ISMEA responde normalmente da Europa. Devolve 404/"Blocked" para o Canadá e para mim. **É filtro geográfico de IP.**

**`esploradati.istat.it`** — relatório `49b3339bk58c`
```
br1 (Brasil, São Paulo) → 302 ✅   rs1 (Sérvia) → 302 ✅
ru1 (Rússia)            → 302 ✅   us2 (EUA)    → 302 ✅
```
Responde **até de outro IP brasileiro**. Daqui: 9 timeouts em 9, sem sequer abrir o TCP. **Não é bloqueio de país — é esta linha/rota específica.**

**`www.ismeamercati.it`** — relatório `49b3362dka81`: 301 da Ucrânia e dos EUA; timeout da Rússia e do Vietnã. Site no ar, alcance irregular por rota.

**`www.regione.veneto.it`** — relatório `49b34962k14a`: 200 do Chipre, Cazaquistão e Turquia; timeout do Irã. Site no ar.

Citação literal do bloqueio ISMEA (corpo do 404):
> "You have been blocked / You are unable to access this website … 1a060bfd1f9-44f57107 179.172.231.127 GEO_IP_BLOCK © Barracuda Networks, Inc."

Citação literal do aviso ISTAT (`avvisi.istat.it/IdotStat/`, HTTP 200, 608 bytes):
> "Si informano gli utenti che tutti i dati presenti sulla banca dati I.Stat sono disponibili all'indirizzo https://esploradati.istat.it/databrowser/#/it"

Isto é o nó do problema: a ISTAT mandou **todo** o cubo de dados para o único host que não abre daqui.

## 3. Rotas alternativas — o que sobrou de pé

**FUNCIONA hoje, sem VPN, sem credencial:**
- **Eurostat dissemination API** (`ec.europa.eu`, IP 147.67.34.30) — três dataflows agrícolas italianos testados e servidos em JSON, inclusive **por região NUTS-2** (Veneto = ITH3). Parte é alimentada pela própria ISTAT como INS nacional.
- **`www.istat.it`** — site institucional, comunicados e publicações em PDF/HTML. É texto e tabela publicada, **não** é o cubo consultável.
- **`www.dati.gov.it`** + API CKAN — catálogo aberto nacional responde.
- **Internet Archive** — tem HTML **real de 2026** de páginas da ISMEA (confirmado em `banca-delle-terre`, 03/07/2026, 38 KB).

**NÃO funciona:**
- Qualquer coisa sob `esploradati.istat.it` — inclusive a API SDMX. Parede de TCP.
- `sdmx.istat.it` — não é bloqueio, está desativado (302 para si mesmo).
- ISMEA em `dati.gov.it`: consulta bem-sucedida, `"count": 0` e organização inexistente. **Fonte alcançada, resultado vazio** — não posso afirmar que a ISMEA não publique em lugar nenhum, só que **não achei** sob esse nome nesse catálogo.
- Espelho da ISMEA no Eurostat: **não procurei a fundo e não sei**. Não afirmo que não exista.

**Armadilha grave a registrar:** no Wayback, snapshots da ISMEA de 2026 com HTTP 200 e 1.199–1.409 bytes compartilham o digest `6L6WTIRHHRSUXLA6ELGBZJ5ESTT3NN4C` entre HTML, JS e PDF. Um deles, aberto, contém `captcha` 3×. **O arquivo capturou a página de bloqueio, não o conteúdo.** Quem contar esses como "página recuperada" vai contar bloqueio como dado.

## 4. Conclusão

> **O Market Pulse italiano NÃO PODE ter camada ISMEA-ISTAT nativa a partir deste ambiente, e o motivo é X = o IP de saída 179.172.231.127 (Vivo residencial, São Paulo) — a ISMEA o rejeita por geografia com `GEO_IP_BLOCK` do Barracuda (a mesma URL devolve 301 normal de Milão, Berlim, Helsinque e Miami), e `esploradati.istat.it`, para onde a ISTAT migrou todo o I.Stat inclusive a API SDMX, não fecha sequer o handshake TCP desta linha em 9 de 9 tentativas embora responda 302 de outro IP brasileiro; PODE, porém, ter uma camada agrícola italiana substituta hoje, via Eurostat (produção vegetal nacional e por região NUTS-2, e venda de defensivos, todos HTTP 200 com data de atualização em 2026), que é dado europeu oficial e não é o mesmo produto que ISMEA/ISTAT.**

Arquivos de prova salvos: `C:\eame-sintonia\.tmp\rota\ismea.html` (corpo do bloqueio, 7.891 bytes), `C:\eame-sintonia\.tmp\rota\datiistat.html`.

Ressalva final, na lei 1: nada aqui autoriza dizer que a ISMEA "não tem dado" ou que a ISTAT "está fora do ar". As duas estão no ar e respondem para outros. **Fonte não alcançada não é fonte vazia.** Se um dia esta máquina sair por outro IP — VPN europeia, runner em nuvem, ou o runner local do GitHub num outro link — as rotas 1 a 5 devem ser retestadas do zero antes de qualquer conclusão.