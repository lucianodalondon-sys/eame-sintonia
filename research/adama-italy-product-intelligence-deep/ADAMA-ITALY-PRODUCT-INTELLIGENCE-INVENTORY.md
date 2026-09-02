# INVENTÁRIO — ADAMA ITALY PRODUCT INTELLIGENCE

**Data:** 2026-09-02 · **Regra da missão:** inventariar antes de coletar. Só se coleta contra `PARTIAL`, `REAL_GAP` e `CONFLICT`.

O achado que mudou a missão: **o censo comercial de 51 produtos e as 51 etichette já existiam**, capturados
em 2026-08-30 na branch `claude/adama-it-local-catalog`, por navegador **com janela** na máquina local.
Recoletar teria sido desperdício — e impossível daqui. Esta missão reconciliou em vez de recoletar.

---

## Onde o acervo já estava

| Ativo | Onde | O que traz |
|---|---|---|
| `IT-ADAMA-CATALOG-CENSUS.json` | branch `claude/adama-it-local-catalog` | 51 produtos + 141 documentos, com sha256 |
| `IT-ADAMA-PRESERVACAO-RELATORIO.json` | mesma branch | 195 arquivos brutos preservados, hash conferido, gate CLOSED |
| `IT-T4-001-adama-portfolio.json` | branch `claude/adama-italia-scrape-qov10l` | 602 registros do grupo, do registro oficial |
| `RADAR-ADAMA-EAME.md` | `docs/adama/` | já registrava o 403 do site em duas rotas |
| `ATLAS-DE-FONTES-EAME.md` | `docs/fontes/` | ficha da fonte IT-T4-001, com a limitação de cultura/alvo |

---

## Classificação por campo desejado

| Campo | Estado | Por quê |
|---|---|---|
| Produto comercial (nome, URL, categoria) | COMPLETE | 51 páginas capturadas e hasheadas; categoria impressa lida da página |
| Produto regulatório (registro, titular, datas) | COMPLETE | 602 linhas do Ministero, versão 2026-08-31 |
| Número de registro publicado pela ADAMA | COMPLETE | 50 dos 51 publicam; 1 não publica nenhum |
| Identidade comercial ↔ regulatória | **CONFLICT** | o censo fechava 41; cruzando contra o registro INTEIRO fecham 49 — 7 são de outro titular |
| Titular da autorização | COMPLETE | do registro, campo `ragione_sociale` |
| Substância ativa por produto | COMPLETE | do registro, com cada componente de mistura separado |
| Estado 'vivo' das 163 autorizações | **CONFLICT** | estado administrativo estava sendo lido como 'vigente hoje' — §3 mede a diferença |
| Data de vencimento | COMPLETE | do registro; é o dado que a Itália dá e a França não dá |
| HRAC / WSSA | PARTIAL | 35 dos 169 ingredientes; a lista HRAC não cobre fungicida nem substância antiga |
| IRAC | PARTIAL | 22 dos 169 |
| FRAC | **REAL_GAP** | PDF oficial baixado; a extração perde dígitos — `M 04` sai `M 0` |
| Etichette (existência, URL, sha256) | COMPLETE | 51 etichette no manifesto, 47 legíveis na captura local |
| Etichette (conteúdo lido) | **REAL_GAP** | os PDF vivem fora do Git e num bucket sem credencial aqui |
| Cultura × alvo × dose × BBCH × carência | **REAL_GAP** | depende do conteúdo da etichetta |
| Cultura declarada na página do produto | UNKNOWN | as culturas na página são links de busca, não declaração de autorização |
| Estado de aprovação EU da substância ativa | **REAL_GAP** | EU Pesticides Database: 307 → `sorry.ec.europa.eu` em toda rota de dados |
| Linhagem regulatória | PARTIAL | o dataset traz uma linha por registro; só continuidade por nome exato é sustentável |
| Sitemap do site ADAMA | COMPLETE | 261 URLs, 51 de produto — lido na captura local |
| Licença / distribuição para os 7 de outro titular | UNKNOWN | nenhuma fonte pública lida prova contrato entre as partes |

---

## O que esta missão coletou de novo

Só contra `PARTIAL`, `REAL_GAP` e `CONFLICT`:

- **HRAC** (`hracglobal.com`, 365 ingredientes parseados) e **IRAC** (`irac-online.org`, 280) — camada de MoA que não existia.
- **A resolução do conflito das 163** — nova, e é o item mais importante do pacote.
- **O cruzamento contra o registro inteiro**, que revelou os 7 produtos de outro titular.
- **FRAC**: tentado, baixado, e conscientemente NÃO publicado.

Nada do que já estava provado foi recoletado para inflar volume.
