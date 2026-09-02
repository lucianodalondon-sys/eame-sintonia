# O que a ADAMA realmente vende e sustenta na Itália

**Data:** 2026-09-01
**Duas fontes, dois pesos:**

| Camada | Fonte | Classe de evidência | O que ela prova |
|---|---|---|---|
| Regulatória | Ministero della Salute — Banca dati prodotti fitosanitari, `PROD_FTS_6_20260824`, CC BY 4.0 | `REGULATORY_FACT` | o que está **autorizado** |
| Comercial | `adama.com/italia/it` | `MANUFACTURER_CLAIM` | o que a ADAMA **comunica** |

As duas não coincidem, e a diferença é informação, não erro.

---

## 1 · Os dois números que abrem o assunto

- **163 produtos vigentes** no registro do Ministero (grupo ADAMA, vínculo por sede administrativa declarada)
- **51 páginas de produto** no catálogo público italiano

**123 registros vigentes não aparecem no catálogo público.** A enumeração do catálogo está completa
(sitemap: 261 URLs, 51 de produto, 0 bloqueadas por robots), então esse 123 é medido, não estimado.

Leitura honesta: isso é **escolha de comunicação**, não ausência de produto. Registro é o que se pode
vender; catálogo é o que se decide promover. Nenhuma das duas coisas prova venda.

---

## 2 · O portfólio por categoria — e a surpresa

### Registro (163 produtos)

| Categoria regulatória | Produtos | % |
|---|---:|---:|
| **DISERBANTE** | **77** | 47,2% |
| FUNGICIDA | 46 | 28,2% |
| INSETTICIDA | 16 | 9,8% |
| **DISERBANTE-ANTIDOTO AGRONOMICO** | **13** | 8,0% |
| INSETTICIDA-ACARICIDA | 4 | 2,5% |
| AFICIDA | 3 | 1,8% |
| MOLLUSCHICIDA | 1 | 0,6% |
| INSETTICIDA-DISERBANTE | 1 | 0,6% |
| DIRADANTE | 1 | 0,6% |
| COADIUVANTE | 1 | 0,6% |

### Catálogo público (51 produtos)

| Categoria do site | Produtos | % |
|---|---:|---:|
| **ERBICIDI** | **26** | 51,0% |
| FUNGICIDI | 14 | 27,5% |
| INSETTICIDI | 6 | 11,8% |
| SPECIALI | 5 | 9,8% |

**Somando diserbante + diserbante-antidoto: 90 de 163 produtos (55,2%) do portfólio italiano da ADAMA
são herbicidas.** No catálogo público, metade das páginas é de erbicidi.

Isto responde diretamente à instrução de que o demo ficou pesado em doença: **o portfólio italiano real
da ADAMA é, antes de tudo, um portfólio de herbicidas.** Um demo dominado por fungicida não está só
desequilibrado — está descrevendo outra empresa. Detalhe completo em
[`ADAMA-ITALY-HERBICIDE-UNIVERSE.md`](ADAMA-ITALY-HERBICIDE-UNIVERSE.md).

Linhas que **não existem** no registro italiano da ADAMA (medido, não suposto):
**nematicida**, **trattamento sementi como categoria própria**, **biologico/biosolution como categoria
própria**. Há um único `MOLLUSCHICIDA`, um `DIRADANTE` (Brevis) e um `COADIUVANTE`. Os produtos
"SPECIALI" do catálogo incluem dois fertilizantes/biostimulantes registrados por número de ato
(`0037584/22`, `0023801/18`), que **não** são prodotti fitosanitari — categoria diferente, registro
diferente. Não misturar.

---

## 3 · Cobertura de rótulo: 163 de 163

- **163 rótulos autorizados baixados e parseados. 0 falhas. 100%.**
- 49 linhas de uso autorizado (cultura + alvo + dose na **mesma** linha)
- 13 dessas linhas trazem dose
- **90 pares cultura × alvo distintos**
- Tabela de doses detectada em **80 de 163** rótulos → **a cobertura é um piso, não um teto**

### Produtos por termo de cultura presente no rótulo

| Cultura | Produtos | | Cultura | Produtos |
|---|---:|---|---|---:|
| GRAPEVINE | 61 | | ALFALFA | 25 |
| WHEAT_GENERIC | 61 | | TRITICALE | 25 |
| TOMATO | 57 | | COMMON_WHEAT | 24 |
| SUGARBEET | 48 | | RICE | 15 |
| APPLE | 48 | | DURUM_WHEAT | 14 |
| BARLEY | 46 | | OLIVE | 12 |
| POTATO | 45 | | SORGHUM | 9 |
| MAIZE | 36 | | | |
| SOYBEAN | 33 | | | |
| SUNFLOWER | 32 | | | |

⚠️ `CROP_TERM_PRESENT ≠ AUTHORIZED_ON_CROP`. O termo aparece em contexto de uso no rótulo; **não** diz
para qual alvo. Só as 49 linhas de uso autorizado ligam cultura a alvo.

### Grupos de mecanismo de ação declarados no rótulo

HRAC 1(A) 20 · HRAC B 8 · HRAC G 7 · HRAC 3(K1) 7 · IRAC 3 6 · FRAC 8 5 · FRAC 3 4 · HRAC 2 4 ·
HRAC 27(F2) 3 · IRAC 3A 2 · HRAC 5(C1) 2 · HRAC 12(F1) 2 · HRAC 2(B) 2 · HRAC 4(O) 2 · FRAC 11 2 ·
HRAC 1 2 · HRAC 5 1 · FRAC 5 1 · IRAC 1A 1 · HRAC O 1 · IRAC 28 1

Cobertura de mecanismo: 70 declarados, 68 não declarados, 25 limitados pela fonte do PDF.

---

## 4 · Vencimentos — o fato mais acionável do portfólio

| Janela | Produtos |
|---|---:|
| Já vencido em 2026-08-30 | **8** |
| Vence em até 7 dias | **7** |
| Vence em até 6 meses | **71** |
| Sem data de vencimento | 0 |

**71 de 163 (43,6%) vencem dentro de seis meses.** Isso é agenda regulatória verificável, com data e
número de registro, para cada produto.

⚠️ `EXPIRY ≠ WITHDRAWAL`. Re-registro é rotina. O estado de renovação de cada um é **NÃO SEI** — o
registro não publica isso. O valor está em *quando olhar*, não em *o que vai acontecer*.

---

## 5 · O catálogo público, lido no navegador em 2026-09-01

Rota confirmada de novo hoje: **só abre em navegador com janela gráfica.** `curl` devolve HTTP 403
(143 bytes); headless devolve "Access Denied" (183 bytes). A rota de filtro
(`/products/crop-protection?f[0]=treatment:NNN`) é interceptada pelo WAF (`bm-verify`) mesmo com janela —
as páginas de produto e de cultura abrem normalmente.

### 5.1 As 51 páginas de produto

**ERBICIDI (26):** Activus® ME · Agil® · Arrodim® · Clematis® · Contatto® 320 · Davai® · Diode® ·
Edaptis® · Elegant® 2fd · FullPage® Rice Cropping Solution · Goltix® · Goltix® TOP · Highcard® ·
Leopard® 5 EC · Max-Ace® Rice Cropping Solution · Nicogan® V.O. · Sonavio® · Stopper P · Sulcotrek® ·
Sultan® · Taifun® MK CL · Taifun® MK CL PFNPE · Timeline® Trio · Tomigan · Trimmer® 50 WG · Valley

**FUNGICIDI (14):** Avastel® · Banjo® · Folpan® 80 WDG · Folpan® Energy · Folpan® Gold · Maganic® ·
Mavita® 250 EC · Maxentis® · Merpan® 80 WDG · Mirador® SC · Nimrod® 250 EW · Seedron® · Stavento® ·
Zakeo® 250 SC

**INSETTICIDI (6):** Apyza® WG · Cosayr® 200 SC · Lamdex® Extra · Mavrik® Smart · Pirimor® 50 ·
Schermo® 0.5 G

**SPECIALI (5):** Brevis® · Budge® · Exelgrow® · Parleaf · Powerfilm®

141 documentos ligados (51 fichas de segurança, 51 etiquetas, 23 brochuras, 13 comunicações,
2 extensões de uso, 1 leaflet). ⚠️ O `robots.txt` proíbe `*/ajax/`, e a lista "Tutti i documenti" de cada
produto vive nessa rota — **os 141 são um piso**.

### 5.2 As sete páginas de cultura (linhas técnicas)

`vite` · `mais` · `cereali` · `soia` · `riso` · `pomodoro` · `pomacee`

Estas páginas são o material mais rico do site para o demo: trazem ciclo agronômico, sintomatologia,
lista real de infestantes italianas, época de aplicação e resistências — em italiano técnico correto.

**Culturas com produto registrado e SEM página de cultura:** olivo (12 produtos), barbabietola (48),
patata (45), girasole (32), erba medica (25), sorgo (9). Isto é lacuna de comunicação, não de registro.

### 5.3 Novidades que o site anuncia em 2026 (lidas hoje)

| Novidade | O que é | Ligação |
|---|---|---|
| **Autorizzazione art. 51** | extensão de SONAVIO® às colture minori **sedano e finocchio** | fato regulatório novo, posterior ao nosso censo de 30/08 |
| **Isondalis® Formulation Technology** | tecnologia de formulação que melhora desempenho de herbicidas **no milho** | camada de herbicida, milho |
| **Linea Insetticidi Melo 2026** | gama completa de inseticidas para melicoltura | 48 produtos citam APPLE no rótulo |
| **Linea Protezione Soia** | nova linha técnica para soja | 33 produtos citam SOYBEAN |
| **Folpan® Energy** | fungicida contra peronospora da vite, "ultima novità a catalogo" | vite |
| **Linea Protezione Vite 2026** | brochura, "oltre 60 anni di esperienza" | vite |
| **Catalogo 2026** | PDF completo | — |

### 5.4 Pessoas reais da ADAMA Itália citadas publicamente

**Mirco Casagrandi — Marketing Technical Manager, ADAMA Italia.** Assina como entrevistado o artigo
"Occhio all'Amaranto: come gestire le resistenze nella pianta di soia" no blog da própria ADAMA.
É um nome real, público e atribuível — e a única pessoa nomeada que a varredura do site encontrou.

---

## 6 · Cruzamento: registro × site

| Estado | Contagem | Leitura |
|---|---:|---|
| `LOCAL_REGISTERED` (no catálogo **e** no registro medido) | 41 | o par sólido |
| `LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED` | 10 | precisa verificação |
| `REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG` | **123** | vendável, não promovido |
| Registro citado fora do registro medido (`CLAIM_OUTSIDE_MEASURED_REGISTRY`) | 7 | ⚠️ **investigar** |
| Duas páginas partilhando um registro (`017995`) | 1 par | Highcard® e Max-Ace® Rice Cropping Solution |
| Página sem número de registro | 1 | Nimrod® 250 EW |
| Registro em formato não-Ministero | 2 | Budge®, Exelgrow® — são fertilizantes, registro de outra natureza |

**Os 7 `CLAIM_OUTSIDE_MEASURED_REGISTRY` são a discrepância que não pode ser varrida para debaixo do
tapete.** Hipóteses possíveis, nenhuma testada: registro concedido depois de `PROD_FTS_6_20260824`
(24/08/2026); registro sob outra razão social fora do escopo `ADAMA_GROUP_IT_CORE`; erro de digitação na
página. **Lacuna aberta.**

---

## 7 · O que este documento NÃO prova

- não prova venda, participação de mercado, estoque, margem nem preferência de distribuidor
- não prova janela de aplicação: a coluna de época **não** foi extraída dos rótulos
- não prova que uma cultura sem linha na tabela está fora do registro — prova que a linha não foi lida
- não prova que os 123 registros fora do catálogo estão "parados"
- não prova nada sobre 2027: os vencimentos são datas, não previsões
