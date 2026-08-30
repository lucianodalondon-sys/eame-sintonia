# HANDOFF — COLETA DO SITE COMERCIAL DA ADAMA ITÁLIA NUMA MÁQUINA RESIDENCIAL

`COUNTRY = IT` · `SOURCE_ID = IT-T9-001` · **2026-08-30**

---

## 1 · POR QUE ESTE HANDOFF EXISTE

`adama.com` responde **HTTP 403 (Access Denied, WAF de origem)** a este ambiente. Medido
três vezes, em rodadas diferentes, por duas rotas de saída distintas, **inclusive em
`/robots.txt`** — o que significa que o bloqueio precede qualquer negociação de permissão.

**E o bloqueio não é da ADAMA.** Na sondagem de fontes desta rodada:

| Site | HTTP |
|---|---|
| `adama.com/italia/it` | **403** |
| `syngenta.it` | **403** |
| `cropscience.bayer.it` | **403** |
| `omnitrattore.it` | **403** |
| `agro.basf.it` | 200 |
| `corteva.it` | 200 |

É a **classe** de sites do setor que recusa IP de datacenter. Isso reclassifica a lacuna:
não é "a ADAMA nos bloqueia", é "a camada de afirmação do fabricante, no agronegócio, é
majoritariamente inacessível de datacenter". Vale para a Espanha e para a França também,
e a sessão principal deveria assumir isso como característica do território.

---

## 2 · O QUE ESTE HANDOFF **NÃO** AUTORIZA

A porta residencial é uma **rota legítima de acesso**, não uma técnica de evasão. O script
não faz, e não deve ser alterado para fazer:

- exportar, copiar ou reutilizar cookies de sessão de qualquer pessoa;
- falsificar credencial, token ou cabeçalho de autenticação;
- rotacionar IP, usar proxy residencial pago ou qualquer evasão de WAF;
- ignorar `robots.txt` — o script **lê e obedece**, e **para** se houver `Disallow`.

> Se o site bloquear também de casa, a resposta correta é
> `ADAMA_COMMERCIAL_SITE = BLOCKED` — não uma técnica mais agressiva. Um dado que só se
> obtém contornando proteção não entra neste repositório.

---

## 3 · COMO RODAR

Numa máquina residencial, com Python 3.11+ (só biblioteca padrão):

```bash
python3 scripts/handoff-local/coletar_adama_italia.py --saida ./adama-it-raw
```

O script:

1. lê `/robots.txt` **primeiro** e para se ele proibir;
2. percorre `/italia/it`, `/italia/it/prodotti`, `/italia/it/colture` e os links internos;
3. grava o **RAW** (HTML e PDF como saíram) em `adama-it-raw/raw/`;
4. escreve `MANIFEST.json` com URL, HTTP, content-type, bytes, **SHA-256** e hora por arquivo;
5. pausa **2,5 s** entre requisições — não reduzir.

Traga de volta **apenas a pasta gerada**. Ela já é auto-descritiva.

---

## 4 · O QUE FAZER COM O RETORNO

O bruto entra no repositório e a normalização acontece aqui, nunca na máquina de fora —
`RAW → NORMALIZED → ANALYTICAL`, com o bruto escrito primeiro.

Alvo da extração, por produto comercial:

```
PRODUCT_ID · COMMERCIAL_NAME · CATEGORY · PAGE_URL · REGISTRATION_ID
ACTIVE_INGREDIENT · FORMULATION · CROPS · ISSUES · DOSE · BBCH
APPLICATION_COUNT · APPLICATION_WINDOW · MODE_OF_ACTION · TECHNOLOGY
POSITIONING · TECHNICAL_CLAIMS · COMMERCIAL_CLAIMS
RELATED_PRODUCTS · RELATED_CONTENT
LABEL · SDS · TECHNICAL_SHEET · BROCHURES · VIDEOS
```

**Separar sempre, e não fundir:**

| Classe | O que é |
|---|---|
| `REGULATORY_FACT` | o que a etichetta do Ministero autoriza — **já temos, 163/163** |
| `MANUFACTURER_TECHNICAL_CLAIM` | o que a ADAMA afirma tecnicamente |
| `MANUFACTURER_COMMERCIAL_CLAIM` | o que a ADAMA comunica comercialmente |
| `DERIVED_INTERPRETATION` | o que nós derivamos |

---

## 5 · O CROSSWALK, QUANDO O CATÁLOGO CHEGAR

```
ADAMA COMMERCIAL PRODUCT  ↔  MINISTERO REGISTRATION  ↔  OFFICIAL LABEL
```

Preferência de chave, nesta ordem: **`REGISTRATION_ID` exato** → titular + composição →
nome comercial como apoio. **Nunca fuzzy-match silencioso.**

Estados: `MATCHED_EXACT` · `MATCHED_WITH_EVIDENCE` · `AMBIGUOUS` · `COMMERCIAL_ONLY` ·
`REGULATORY_ONLY`.

> **A subtração está proibida.** `163 − 52` **não** é "111 produtos não comercializados".
> As unidades são diferentes: uma autorização não é um produto de catálogo, e um produto
> de catálogo pode ter várias autorizações. Quem fizer essa conta está comparando coisas
> que não se comparam.

E os ~52 produtos citados no enunciado da missão permanecem **`UNVERIFIED_INPUT`** até
serem reproduzidos na fonte. Não entram como fato em artefato nenhum.

---

## 6 · O QUE JÁ TEMOS SEM O SITE

A camada **regulatória** está completa e é mais forte para a pergunta do piloto:

- **163/163 rótulos oficiais** (100 %), com SHA-256, 33,8 MB preservados;
- **49 linhas de uso autorizado** ligando cultura ↔ alvo ↔ dose;
- **90 pares cultura × alvo** distintos;
- modo de ação declarado em **70** produtos;
- calendário de vencimento completo.

O que falta é exclusivamente a **camada de afirmação do fabricante** — posicionamento,
claims, pack sizes, catálogo, materiais. Nada disso é `REGULATORY_FACT`, e nada disso
muda nenhum dos três hero cases.

`LOCAL_BROWSER_HANDOFF_STATUS = READY_TO_RUN`

---

## 7 · SEGUNDO ALVO DO MESMO HANDOFF — O BOLETIM DE MILHO DO VÊNETO

Isto não é ADAMA e não é WAF. É uma dívida de **preservação** que só uma máquina com
navegador fecha, e ela vale mais do que parece: o Vêneto tem **24,8 % do milho italiano**
e hoje está fora da cobertura *e* fora da ausência por falta de índice.

**O que se sabe funcionar:**

```
https://www.venetoagricoltura.org/myportal/AVPISP/api/content/download?id=<id>
```

devolve o PDF real do *Bollettino Colture Erbacee* da AVISP. O portal é um SPA Angular
que não renderiza no servidor; o `<id>` só apareceu em resultado de busca pública.

**O que falta e por que:** não há endpoint de listagem alcançável deste ambiente. A
procura por um foi **encerrada, não contornada** — sondar API não documentada de um
portal público não está autorizado por este handoff nem por nenhum outro.

**O que a máquina local deve fazer, e só isto:**

1. Abrir o portal da AVISP **no navegador, como qualquer leitor**, e navegar até o índice
   do *Bollettino Colture Erbacee* de **2026**.
2. Anotar, para cada edição de 2026: **número · data · título · URL do PDF**.
3. Baixar as edições cujo título trate de **milho / piralide / diabrotica / micotossine**,
   com pausa de 2,5 s entre requisições e respeitando o `robots.txt`.
4. Gravar em `data/raw/IT/avisp/` com **SHA-256, tamanho e data** no manifesto.

**Duas edições a re-obter em primeiro lugar** — foram lidas nesta branch e **não foram
preservadas** (`RAW_EVIDENCE_STATE = NOT_PRESERVED`, confissão, não ausência):

| Edição | Conteúdo lido | Estado |
|---|---|---|
| **n. 53 — Micotossine nel mais** | risco sazonal pelo DSS **Mais.net** (Horta) sobre as estações das aziende da Veneto Agricoltura; **aflatossina ALTA** em todas as estações, fumonisina de média-alta a alta; verificação do nível de infecção das sedas com o **CREA-CI**. Ano **NÃO SEI** — não foi registrado na leitura. | `NOT_PRESERVED` |
| **n. 18/2025 — Nottue** | primeira captura de *Agrotis ipsilon* em **Cartura (PD)**, 03/03/2025; modelo de graus-dia `(Tmax−Tmin)/2 − 10,4 °C`. | `NOT_PRESERVED` |

**O que o retorno destrava, e o que não destrava.** Com o índice de 2026 em mãos, o
Vêneto ganha denominador e a cobertura de campo do milho sobe de **17,1 %** para até
**~42 %** — o que reforça `IT-HERO-002` de forma material.

**Enquanto o índice não chegar, a linha do Vêneto não pode ser promovida.**
`EDIÇÃO LIDA ≠ SÉRIE MEDIDA`. Ler duas edições prova que a série existe e trata de milho;
não diz quantas edições de 2026 existem. Promover a região porque *finalmente li alguma
coisa* é a forma local de `COBERTURA ALTA ≠ COBERTURA CORRETA`, e há teste que reprova
essa promoção: `test_edicao_lida_nao_promove_a_regiao_a_coberta`.

`AVISP_INDEX_HANDOFF_STATUS = READY_TO_RUN`

---

## 8 · TERCEIRO ALVO — OS QUATRO RECORTES DE PESQUISADORES NO OPENALEX

Mesma natureza do item 7: não é WAF, não é ADAMA, e **não é conteúdo que se obtenha com
mais paciência daqui**.

**O que foi medido.** A primeira coleta estrangulou o IP deste ambiente ao paginar de 100
em 100 a cada 1,6 s. Eu corrigi a paginação (200 por página, 8 s entre chamadas) e anotei
que uma pausa resolvia. **Nova tentativa em 30/08, ~8 horas depois, com a paginação já
lenta e três esperas de 25 s / 50 s / 75 s: HTTP 429 no primeiro recorte.** O bloqueio é
sobre o **IP de saída**, com duração maior que a sessão.

**O que falta obter** — quatro recortes `CROP × ISSUE`, todos com o número de obras já
conhecido da primeira sondagem:

| Recorte | Obras | Consulta |
|---|---:|---|
| `VINE_FLAVESCENCE` | 135 | `grapevine AND (flavescence OR Scaphoideus)` |
| `MAIZE_BORER_DIABROTICA` | 30 | `maize AND (Ostrinia OR Diabrotica)` |
| `OLIVE_BACTROCERA` | 70 | `olive AND (Bactrocera OR "olive fly")` |
| `DURUM_FUSARIUM` | 78 | `"durum wheat" AND (Fusarium OR mycotoxin OR deoxynivalenol)` |

**Como rodar:** `python3 scripts/italia_pesquisadores.py` numa máquina residencial, ou
daqui mesmo com um `mailto` reconhecido pelo OpenAlex (a API dá cota maior ao *polite
pool*). O script já pagina devagar e **já falha suave**: um recorte estrangulado sai como
`THROTTLED_NOT_EMPTY` com contagem `None`, e a coleta continua nos outros.

**A regra que não pode ser relaxada no retorno:** `SOURCE FAILURE ≠ ZERO`. Recorte que a
fonte recusou **não** é recorte sem pesquisadores, e não pode entrar no artefato com `0`.

`OPENALEX_HANDOFF_STATUS = READY_TO_RUN`
