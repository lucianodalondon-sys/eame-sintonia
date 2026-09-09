# RELATÓRIO DE TESTE — SINTONIA SCRAP · FONTES ITÁLIA

**Data:** 2026-09-07
**Repositório:** `lucianodalondon-sys/eame-sintonia` · branch `claude/eame-competitor-public-communication` · commit `b596607`
**Catálogo produzido:** `../fontes/ITALY-SOURCE-MASTER-V1.md` · `../../candidatas/ITALY-SOURCE-MASTER-V1.json`

---

## RESUMO EM UMA LINHA

O ambiente automatizado exigido pela missão **não subiu** (causa encontrada e corrigida — §9).
Mas a VPN italiana **foi confirmada** e **duas rotas foram observadas** por navegação assistida:
o usuário navegou no próprio Chrome italiano e enviou capturas; o agente registrou.
**Nenhum veredito GREEN foi emitido** — há observação confirmada, não há documento preservado.

> **ATUALIZAÇÃO no meio da sessão.** As seções 1–3 abaixo descrevem o estado *antes* da
> VPN ser confirmada. Ficam como estavam, por honestidade de registro. O que mudou está em §9.

---

## 1 · O QUE A MISSÃO EXIGIA

```
SINTONIA SCRAP
+ BROWSER NORMAL
+ VPN LOCALIZADA NA ITÁLIA
```

com a **REGRA 0** explícita:

```
BLOCKED_EM_DATACENTER ≠ BLOCKED_EM_BROWSER_ITALIANO
```

---

## 2 · O QUE FOI MEDIDO NO AMBIENTE

| # | item | método | resultado |
|---|---|---|---|
| 1 | IP de saída do navegador interno | `GET https://ipinfo.io/json` | `188.240.57.237` · `237.57.240.188.baremetal.zare.com` · **Edinburgh, Scotland, GB** · AS25369 Hydra Communications Ltd · `Europe/London` |
| 2 | natureza do IP | hostname `baremetal.zare.com` | **DATACENTER** — nem italiano, nem residencial |
| 3 | Chrome real do usuário | `claude-in-chrome / tabs_context_mcp` | **not connected** (3 tentativas) |
| 4 | navegadores pareados na conta | `list_connected_browsers` | **`[]`** — lista vazia (4 tentativas ao longo da sessão) |
| 5 | extensão instalada? | captura de tela da Chrome Web Store enviada pelo usuário | **SIM** — botão "Remover do Chrome" visível. Instalada, porém **sem sessão iniciada**. |
| 6 | interpretador Python | `py --version`, busca por `python.exe` no disco | **AUSENTE** — `py` resolve para `C:\actions-runner-2\_work\_tool\Python\3.12.10\x64\python.exe`, caminho inexistente; `AppData\Local\Programs\Python\Python312\` tem `Lib`, `DLLs`, `Scripts`, **mas não o binário** |
| 7 | Node | `node --version` | **v24.18.0** — disponível |

### Diagnóstico do item 5

A extensão está instalada, mas **instalada ≠ conectada**. A ponte só sobe quando o painel
lateral da Claude é aberto no Chrome e faz login na mesma conta desta sessão. Até lá,
`list_connected_browsers` devolve lista vazia — que foi exatamente o observado.

---

## 3 · POR QUE NÃO PROBAMOS ASSIM MESMO

Rodar as ~46 rotas do IP de Edimburgo produziria uma tabela cheia de números e
**vereditos negativos sem valor**:

- um `403` de Edimburgo mede o WAF reagindo a **um datacenter britânico**, não a um
  produtor italiano navegando de casa;
- registrar isso como `RED` violaria a REGRA 0 e contaminaria o acervo com uma condenação
  que a Fase C teria de desfazer;
- o Atlas já tem o precedente que prova o risco: a MISSÃO registrou e depois **corrigiu**
  a leitura *"todo `ec.europa.eu` está inacessível deste ambiente"*, que estava errada
  (`EU-T4-002`). Repetir o padrão seria repetir um erro já catalogado.

**Decisão:** nenhuma fonte recebeu GREEN, YELLOW ou RED. Todas estão `NOT_TESTED`.

---

## 4 · A REGRA ASSIMÉTRICA PARA A FASE C

Vale para qualquer IP não-italiano, e deve ser aplicada literalmente:

| observação | conclusão permitida |
|---|---|
| **abriu e entregou documento real** | **sinal válido.** Se abre de fora, abre da Itália — exceto geo-bloqueio explícito, que se reconhece pela mensagem, não pelo código HTTP. |
| **403 · 503 · WAF · challenge · captcha** | **sinal nulo.** `NÃO SEI`. Obrigatório remedir de IP italiano antes de qualquer RED. |
| **404** | **sinal válido, mas sobre a URL, não sobre a fonte.** Caminho errado ≠ fonte inexistente. O caso `corteva.it/notizie.html → 404` do Atlas é exatamente isto: navegar o menu, não adivinhar a URL. |
| **200 com HTML sem conteúdo** | **sinal válido e negativo sobre a rota.** O acervo já classifica isso como `FAILED_WITH_REASON` (seis rotas de feed espanholas, `ES-T7-001..027`). `HTTP 200` não basta. |

---

## 5 · FICHA DE PROBE — MODELO PARA A FASE C

Cada fonte do catálogo deve receber esta ficha quando o navegador italiano estiver ligado.
**Nenhuma foi preenchida nesta rodada.**

```
SOURCE_ID
OWNER_ID
EXIT_IP / EXIT_COUNTRY        ← obrigatório: prova que era Itália
BROWSER                        ← qual navegador, qual versão
ROTA_NAVEGADA                  ← os cliques, não só a URL final
RESULTADO                      ← ACCESS_OK | BLOCKED | LOGIN_REQUIRED | WAF | NOT_FOUND
CONTENT_AVAILABLE              ← SIM | NÃO | PARCIAL
DOCUMENTO_OBTIDO               ← caminho do arquivo bruto
MIME / BYTES / SHA256
SOURCE_DATE / CAPTURED_AT
SOURCE_LOCATION / FACT_LOCATION
ORIGINAL_LANGUAGE / ORIGINAL_TITLE
EVIDENCE_CLASS
JS_NECESSÁRIO                  ← a página renderiza sem JavaScript?
LOGIN / CAPTCHA / PAGINAÇÃO
ESTRUTURA                      ← URL estável? data visível? identidade de documento?
ATRITO_QUALITATIVO             ← em palavras, não em segundos falsos
AUTOMATION_FEASIBILITY         ← HIGH | MEDIUM | LOW | NOT_AUTOMATABLE | NÃO SEI
WHAT_IT_PROVES
WHAT_IT_DOES_NOT_PROVE
VERDICT                        ← GREEN | YELLOW | RED | NÃO SEI
```

**Sobre tempo:** a missão dispensa benchmark de tempo preciso quando ele não foi medido de
forma confiável. `ATRITO_QUALITATIVO` em palavras é preferível a um número inventado.

---

## 6 · ORDEM DE EXECUÇÃO QUANDO O AMBIENTE SUBIR

Antes de qualquer fonte:

```
0. abrir ipinfo.io/json no Chrome  →  confirmar "country": "IT"
   se não for IT, PARAR. Nada medido antes disso vale.
```

Depois, na ordem da missão:

| # | fonte | SOURCE_ID | o que a amostra precisa provar |
|---|---|---|---|
| 1 | Terre dell'Etruria — mosca dell'olivo | `IT-T3-005` | data · ponto · fenologia · captura · infestação · recomendação |
| 2 | Campania SFR / SIMFITO | `IT-T3-002` / `IT-T3-003` | bollettino 2026 com província · cultura · avversità |
| 3 | ALSIA Basilicata | `IT-T2-005` / `IT-T3-004` | **duas rotas separadas**, não uma fonte genérica |
| 4 | Sicilia fitosanitario | `IT-T3-007` | e classificar: field signal, guideline ou deroga? |
| 5 | MASAF OP/AOP | `IT-T7-002` | nome · tipo · setor · região · reconhecimento |
| 6 | ISMEA | `IT-T10-001` | produto · praça · data · preço · unidade · variação |
| 7 | BMTI | `IT-T10-002` | análise real recente de grano duro / mais |
| 8 | FEM | `IT-T3-012` | ao menos uma amostra T3 |
| 9 | CAI | `IT-T7-003` | um conteúdo técnico real — homepage não conta |
| 10 | AGRIOS | `IT-T3-011` | direttive / aggiornamenti / deroghe |
| 11–15 | ARPAE · ARPAV · CNR-IBE · CREA · Giornate Fitopatologiche | `IT-T2-001` `IT-T2-002` `IT-T2-003` `IT-T5-001` `IT-T5-003` | uma edição/documento real cada |

Depois: Agrintesa · Apofruit · Apo Conerpo · Ortofruit · VOG · Melinda · CAVIT/PICA ·
ICQRF · Fieragricola · Enovitis · EIMA · SIRFI · CNR IRIS.

**Teto de coleta:** 1 amostra boa por fonte; 2–3 documentos **apenas** quando for preciso
provar recorrência. Sem crawler histórico, sem paginação ilimitada.

---

## 7 · O QUE ESTA RODADA ENTREGOU DE FATO

| entregue | não entregue |
|---|---|
| inventário do que já existia (6 fontes italianas, com veredito de origem) | probe de qualquer fonte |
| modelo OWNER × SOURCE × TERRITORY × ROLE, com 44 owners e 46 canais | amostra bruta |
| a dívida de taxonomia `T13`, com custo de migração medido e testes identificados | migração do T13 |
| a armadilha de contagem do `IT-T12-001` | contrato de fonte |
| as duplicidades e sobreposições a medir antes de operacionalizar | veredito e prioridade P0–P3 |
| a regra assimétrica de leitura de bloqueio | execução dos testes (`tests/`, sem Python) |

**Nenhum artefato canônico foi alterado.** O `ATLAS-DE-FONTES-EAME.md` continua com
37 SOURCE_IDs e o placar intacto — condição para não quebrar
`tests/test_handoff.py:111`, `tests/test_canonico.py` e `tests/test_metricas.py`.

---

## 8 · PENDÊNCIAS ABERTAS POR ESTA RODADA

| id | pendência | dono |
|---|---|---|
| **IT-P-001** | ligar Chrome + VPN italiana e confirmar `country: IT` | Luciano |
| **IT-P-002** | restaurar o Python da máquina — `tests/` não executa | Luciano |
| **IT-P-003** | decidir o destino de `IT-T9-001` (ficha compartilhada FR/ES/IT vs. uma por empresa) — mexe no placar canônico | Luciano |
| **IT-P-004** | decidir a migração `T13 → T7 + T10`, que exige Atlas + marcadores + 3 arquivos de teste na mesma mudança | Luciano |

---

## 9 · ATUALIZAÇÃO — VPN CONFIRMADA E PRIMEIRA OBSERVAÇÃO

### 9.1 · A causa da desconexão do Chrome — encontrada

Sete tentativas de pareamento falharam. Diagnóstico feito **nesta máquina**:

| verificado | resultado |
|---|---|
| Claude Code v2.1.220 | ✅ acima do mínimo |
| chave de registro do Windows | ✅ existe |
| manifesto do native host | ✅ existe e autoriza o ID correto da extensão |
| script lançador `.bat` e binário alvo | ✅ existem |
| **`~/.claude/settings.json`** | ❌ **bloco `env` desviava tudo para um gateway de terceiro** |

O arquivo continha `ANTHROPIC_BASE_URL` apontando para um domínio não-Anthropic, com
`ANTHROPIC_AUTH_TOKEN` próprio, mais `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` e
`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`. O terminal exibia `API Usage Billing` em vez de plano.

**Ação, autorizada pelo usuário** ("foi um teste antigo, pode apagar"): as 4 linhas foram
removidas. Backup íntegro em `~/.claude/settings.json.bak-2026-09-07`.

**Limitação medida:** a sessão em curso **continua** com as variáveis antigas — processo em
execução não as descarta. O pareamento só será possível numa **sessão nova**.

**Não removido, por mudar comportamento sem pedido explícito:**
`ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8` e `ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-6`
— prendem o terminal em modelos antigos.

### 9.2 · VPN italiana — CONFIRMADA

```
205.147.30.20 · Milan · Lombardy · country: IT · AS208172 Proton AG · Europe/Rome
```

**Ressalva obrigatória:** é IP de **VPN comercial**, não de ISP residencial italiano.
Qualquer bloqueio observado deste IP deve ser registrado como
`POSSIVEL_BLOQUEIO_DE_FAIXA_VPN` — **nunca** como "bloqueia a Itália".

### 9.3 · Método usado: OBSERVAÇÃO ASSISTIDA

O agente **não navegou**. O usuário abriu as páginas no próprio Chrome italiano e enviou
capturas de tela; o agente leu e registrou. Declarado assim para não passar por probe
automatizado — são coisas diferentes, com força de evidência diferente.

### 9.4 · `IT-T7-001` · terretruria.it — `ACCESS_OK`

Homepage abriu do IP italiano: sem login, sem captcha, sem challenge anti-robô.

**Correção ao catálogo:** o menu `SERVIZIO AGRONOMICO` tem **sete** sub-rotas, não três:
`COLTURE` · `CONTATTI` · `MONITORAGGIO MOSCA DELL'OLIVO` · `QUADERNO DI CAMPAGNA` ·
`PROGETTI` · `WEBINAR` · `PAROLA DI TERRE`. O owner `IT-OWN-008` tem mais canais que os
registrados. Ampliar depois de medir cada um.

### 9.5 · `IT-T3-005` · Monitoraggio mosca dell'olivo — `ACCESS_OK`, sem veredito

A fonte **prioridade 1 da missão existe e é pública.**

| observado | valor |
|---|---|
| documento | *Bollettino del periodo dal **31-08-2026** al **06-09-2026*** |
| periodicidade aparente | **semanal** (período fechado de 7 dias declarado) |
| defasagem | **1 dia** — fonte viva |
| granularidade | **PONTO** — ~60–80 pontos geolocalizados em mapa |
| `FACT_LOCATION` | costa toscana: Lucca, Pisa, Livorno, Piombino, Grosseto, Orbetello |
| `SOURCE_LOCATION` | Livorno (sede) — **diferente** do local do fato |

**Duas camadas, e a separação importa:**

| camada | acesso |
|---|---|
| *Mappa infestazione attiva* | **ABERTA**, sem cadastro |
| *Mappa catture adulti* | **`LOGIN_REQUIRED`** — a página declara *"Solo per utenti registrati"* |

A camada fechada é classificada `PUBLIC_CAPABILITY`. **Não se tentou contornar autenticação.**

**`RAW_EVIDENCE_STATE = NOT_PRESERVED`.** A evidência é captura de tela, não documento com
MIME/BYTES/SHA256. Testemunho de leitura **não** foi convertido em evidência re-verificável.

**`VERDICT = NÃO SEI` — promissora. Por que não GREEN:** GREEN exige amostra real capturada e
preservada. Falta: legenda das cores, o que um ponto revela ao ser clicado, e **prova de
recorrência** — uma edição não prova frequência, então `UPDATE_FREQUENCY` segue `NÃO SEI`.

**O que mudou:** `IT-T3-005` deixou de ser hipótese. A rota existe, é pública, é semanal e é
por ponto — o perfil que, no acervo inteiro, só a RAIF andaluza (`ES-T3-001`) tem hoje, e ali
para uva. Aqui seria azeitona.

### 9.6 · Próximos passos concretos

1. Sessão **nova** do Claude Code → `/login` → `/chrome` → *Reconnect extension*.
2. Em `IT-T3-005`: legenda · clicar num ponto · arquivo de edições anteriores · **preservar com hash**.
3. Só então converter `NÃO SEI` em veredito.

---

## 10 · FASE C RETOMADA — `IT-T3-005` COM EVIDÊNCIA PRESERVADA

**Data:** 2026-09-07, 13:04Z e 13:29Z. **Os quatro pendentes do item 9.6.2 foram fechados.**

### 10.1 · Correção de método — a extensão do Chrome não era pré-requisito

A §9 assumiu que, sem parear a extensão, não havia coleta possível. **Estava errado.**
A VPN é do sistema inteiro: o `curl` desta máquina também sai pela Itália.

```
curl https://ipinfo.io/json  →  205.147.30.20 · Milan · IT · AS208172 Proton AG
curl https://www.terretruria.it/monitoraggio  →  HTTP 200 · 274.247 bytes · text/html
```

Fica registrado porque muda o custo de toda a Fase C: **enquanto a VPN estiver ligada, a
coleta com hash roda sem navegador.** A ressalva de §9.2 continua valendo — é IP de VPN
comercial, não de ISP residencial.

`robots.txt` do site: `User-agent: * / Allow: /`. Nenhuma autenticação foi usada ou contornada.

### 10.2 · Documento preservado — `RAW_EVIDENCE_STATE = PRESERVED`

`data/samples/ITALY-T3-005-MONITORAGGIO/` · manifesto em `MANIFEST.json`

| campo | valor |
|---|---|
| documento | `monitoraggio-2026-09-07.html` |
| MIME | `text/html; charset=UTF-8` |
| BYTES | 274.247 |
| SHA256 | `2e488a8232ba980fa46f7dbca28478fdac0e30e4440d9675823c5f3479d2d122` |

**Estabilidade medida:** duas coletas, com 25 minutos de intervalo, devolveram **o mesmo
SHA256**. A página é byte-estável — o hash serve como prova re-verificável, não há ruído
por requisição.

O `points-2026-09-07.json` (139 pontos) é **derivado**, não evidência. A evidência é o HTML.

### 10.3 · A legenda das cores — RESOLVIDO

Extraída do próprio documento preservado, não de leitura de tela.

| cor | *Legenda infestazione* | *Legenda catture* |
|---|---|---|
| LIGHTGREY | Dato non rilevato | Dato non rilevato |
| GREEN | Nessuna allerta | Stazionario |
| YELLOW | Pre allerta | In aumento |
| RED | Allerta | In forte aumento |
| BLUE | Sotto trattamento | — |

A escala de catture é comparativa: *"rispetto alla settimana precedente"*. A legenda é
pública; o **valor** de catture por ponto continua `LOGIN_REQUIRED`.

### 10.4 · O que um ponto revela ao ser clicado — RESOLVIDO

Seis campos:

```
nome do ponto (COMUNE, localidade)   ex.: "ALBERESE, Alberese-cimitero"
point_id interno do site             ex.: 22635
Latitudine / Longitudine             ex.: 42.6603, 11.0995   (4 casas decimais)
Data di campionamento                ex.: 04-09-2026         (dia exato da coleta em campo)
Infestazione attiva                  ex.: 0%, Sotto trattamento  (% inteiro + rótulo + cor)
Catture adulti                       "Dato per utenti registrati"  → LOGIN_REQUIRED
```

**Achado que importa para a operação:** os 139 blocos de ponto **já vêm no HTML da página
pública**. O clique no mapa só revela um bloco que já estava baixado. Não há API nem XHR a
descobrir — o dado por ponto está inteiro dentro do documento com hash acima.

### 10.5 · Correção de contagem — são 139 pontos, não 60–80

O catálogo dizia ~60–80, estimados a olho no mapa. A contagem no documento dá **139 point_id
únicos e 139 pares lat/lon únicos**.

Edição de 31-08 a 06-09-2026: **110 pontos com valor, 29 sem dado.** Dos 110 —
95 *Nessuna allerta* · 5 *Pre allerta* · 4 *Allerta* · 6 *Sotto trattamento*.
Datas de campionamento presentes: 31-08, 01-09, 02-09, 03-09 e 04-09.
O próprio boletim cita **5% de infestação ativa** como o limiar para *intervento larvicida*.

### 10.6 · O arquivo de edições anteriores — RESOLVIDO, com resposta NEGATIVA

**Não existe arquivo público.** Três medições:

1. o link `/bollettini` está no **rodapé do site** e devolve **HTTP 404**;
2. o `sitemap.xml` oficial tem **927 URLs** e **uma única** rota de monitoramento
   (`/monitoraggio`) — nenhuma página de arquivo, nenhum PDF de boletim;
3. a **Wayback Machine estava fora do ar** em 2026-09-07 (*"Internet Archive services are
   temporarily offline"*) — não deu para usar snapshot de terceiro como prova.

**Dois indícios no código-fonte que NÃO são prova**, e ficam marcados como tal:
há um `<h3>` **comentado** com *"Bollettino del periodo dal 07/09/2026 al 13/09/2026"* — a
próxima edição já preparada, mas **não publicada**; e outro comentado com *"L'attività di
monitoraggio riprenderà a Giugno 2025"*, resquício de temporada anterior. São rascunhos
dentro do HTML, não edições publicadas.

**Conclusão:** o site mostra **uma edição por vez e substitui a anterior**.

### 10.7 · Veredito — continua `NÃO SEI`, e agora falta uma coisa só

Três dos quatro pendentes viraram fato preservado. O quarto — **prova de recorrência** — não
pode ser fechado hoje, porque a fonte não guarda histórico e o arquivo de terceiro estava fora
do ar. `UPDATE_FREQUENCY` segue **`NÃO SEI`**.

**Passo único para GREEN:** recapturar `https://www.terretruria.it/monitoraggio` **depois de
2026-09-13**. Se o título mudar de período e o SHA256 mudar junto, a periodicidade semanal
fica provada por medição nossa, e o veredito pode virar GREEN.

---

## 11 · FASES C–H — RODADA COMPLETA DE 2026-09-07

### 11.1 · Ambiente e método

VPN italiana confirmada (`205.147.30.20 · Milano · IT · AS208172 Proton AG`).
Acesso por `curl` com User-Agent de navegador, saindo pelo IP italiano.

A extensão do Chrome **não** chegou a parear. Descobriu-se que **não era pré-requisito**:
a VPN é do sistema inteiro. Isso desbloqueou a missão inteira.

**Terceira categoria de assimetria, acrescentada à REGRA 0:**

```
ACCESS_OK no curl italiano   →  sinal FORTE (se abre para curl, abre para navegador)
BLOCKED no curl italiano     →  sinal FRACO
                                BLOCKED_EM_CURL_ITALIANO ≠ BLOCKED_EM_BROWSER_ITALIANO
```

**Nenhum RED foi emitido.** Todo bloqueio virou `NÃO SEI — reteste em navegador`.

### 11.2 · Ferramentas criadas (reutilizáveis)

| script | o que faz |
|---|---|
| `coleta/italy_probe.mjs` | mede a porta de todas as fontes; não preserva nada |
| `coleta/italy_find_docs.mjs` | abre uma página e lista os links que parecem documento real |
| `guarda/italy_preserve.mjs` | baixa e preserva com MIME/BYTES/SHA256; **confere a assinatura dos bytes** |
| `ferramentas/pdf_peek.mjs` · `ferramentas/html_text.mjs` | conferem que o arquivo preservado é o documento que se diz |
| `candidatas/italy_fill_manifests.mjs` | escreve os campos de julgamento decididos à mão |
| `regras/italy_contract_test.mjs` | Fase H — os guardas do contrato |

### 11.3 · Resultado por fonte

| fonte | rota | JS | login | captcha | bloqueio | estrutura | automação |
|---|---|---|---|---|---|---|---|
| Campania SFR (`IT-T3-002`) | PDF por província e data | não | não | não | não | `<PROV>-<DD>-<MM>.pdf` | **HIGH** |
| ARPAE (`IT-T2-001`) | PDF numerado por semana | não | não | não | não | `<NN>_boll_agro_<AAAAMMDD>.pdf` | **HIGH** |
| Ministero Salute (`IT-T4-001`) | CSV/XML/JSON + dicionário + RSS | não | não | não | não | data no nome do arquivo | **HIGH** |
| ISTAT (`IT-T1-001`) | API SDMX 2.1 sem chave | portal sim, **API não** | não | não | não | CSV com esquema | **HIGH** |
| Terre dell'Etruria (`IT-T3-005`) | HTML único | não | camada de capturas sim | não | não | 139 pontos no HTML | **HIGH** |
| BMTI (`IT-T10-002`) | HTML com id numérico | não | não | não | não | `/46622/` opaco | MEDIUM |
| Giornate Fito / AIPP (`IT-T5-003`) | PDF em WordPress datado | não | não | não | não | nome de arquivo livre | MEDIUM |
| AGRIOS, SIAS, ARPAV zone, MASAF OP | — | **provável** | — | — | — | — | `NÃO SEI` |
| ARIF Puglia, Bayer, Syngenta, ADAMA | — | — | — | — | **403 ao curl** | — | `NÃO SEI` |

**Atrito qualitativo:** nenhuma das fontes GREEN exigiu mais de um clique de navegação a partir
da home. A mais lenta foi a API do ISTAT: 13,6 MB em 13 segundos.
Não há medição de tempo confiável o bastante para virar número.

### 11.4 · Armadilha evitada, e ela já tinha nos pegado antes

O site da ARPAE é Plone e oferece o link do boletim com sufixo `/view` — que devolve a **casca
HTML da página**, não o PDF. Baixamos sem o `/view`, e o script confere a assinatura dos
primeiros bytes (`%PDF`) antes de declarar preservado. Os dois arquivos são PDF de verdade.

### 11.5 · Fase H — os guardas

O suíte Python do repositório **não pôde rodar**: o Python desta máquina continua quebrado
(`Python não foi encontrado`), problema já registrado e não resolvido nesta missão.

Foi escrito um guarda em Node para o contrato novo — `regras/italy_contract_test.mjs`.
**125 verificações, 0 falhas.** O que ele protege:

```
1  nenhuma fonte vira GREEN sem RAW_EVIDENCE_STATE = PRESERVED
2  toda amostra preservada tem MIME, BYTES e SHA256 de 64 dígitos
3  o hash do manifesto BATE com o arquivo no disco  ← evidência re-verificável de verdade
4  ACCESS FAILURE ficou registrado e não virou zero; nenhum RED foi emitido
5  SOURCE_LOCATION e FACT_LOCATION existem separados em toda amostra
6  OWNER_KIND nunca é um território (T1–T12)
7  uma organização pode ter vários canais; nenhum SOURCE_ID duplicado
8  nenhum T13 novo; o T13 existente só aparece como dívida declarada
9  toda amostra preservada declara WHAT_IT_DOES_NOT_PROVE
```

O guarda **encontrou uma falha real** na primeira execução: o manifesto do `IT-T3-005`, escrito
à mão mais cedo, não declarava `SOURCE_LOCATION`, `FACT_LOCATION` nem `WHAT_IT_DOES_NOT_PROVE`,
e dois arquivos estavam sem `BYTES`/`SHA256`. Foi corrigido, e só então passou.

---

## 12 · FECHAMENTO — O QUE EU TINHA ESCRITO ERRADO

Quatro formulações da §11 foram corrigidas. O detalhe está em
`../fontes/ITALY-SOURCE-MASTER-V1.md` §11 e nos manifestos. Em resumo:

| eu escrevi | está certo |
|---|---|
| Ministero della Salute = "só descoberta e identidade" | **T4 REGULATORY · REGULATORY_PRIMARY.** Descoberta é uso secundário. |
| Giornate Fitopatologiche = "só descoberta e identidade" | **T5 SCIENCE + T6 RESEARCHERS + T11 EVENTS.** Uma origem, três leituras. E dois donos: Giornate e AIPP. |
| ARPAE = `OBSERVED_FIELD_SIGNAL` | **`AGROCLIMATIC_SIGNAL`.** `AGROCLIMATIC_SIGNAL ≠ PEST_OCCURRENCE`. |
| "as outras 47 continuam sem teste" | **51 probadas · 7 com amostra e RAW preservado · 44 probadas sem amostra · 3 nunca tocadas.** |

E uma lei permanente entrou no contrato:

```
ROUTE_NOT_FOUND  ≠  SOURCE_BLOCKED
OLD_URL_FAILURE  ≠  CURRENT_SOURCE_FAILURE
```

7 dos "bloqueios" desta rodada eram endereço errado no nosso próprio catálogo.
Erro nosso não vira defeito da fonte.

---

## 13 · RODADA BROWSER — 2026-09-07

**Instrumento:** navegador com janela, saindo pelo IP italiano. A extensão do Chrome do usuário
**continua sem parear**; usou-se o navegador embutido, que atravessa a mesma VPN do sistema.
**O IP de saída do próprio navegador foi verificado antes de qualquer medição:**
`205.147.30.20 · Milano · IT · AS208172 Proton AG`. Sem isso, nada do que vem abaixo valeria.

### 13.1 · O que o navegador resolveu que o `curl` não resolvia

| fonte | o diagnóstico anterior | o que era de verdade |
|---|---|---|
| **AGRIOS** | "provável JavaScript" | **o site é em alemão.** Meu detector só falava italiano. Nunca houve bloqueio. |
| **ARPAV** | "escolha de zona é JavaScript" | 32 PDFs com URL fixa, que só o navegador revelou |
| **SIAS Sicília** | "frameset antigo, conteúdo fora do HTML" | certo — e descendo nos frames chega-se à tabela diária por estação |
| **MASAF** | "lista não aparece por navegação simples" | está em `Politiche nazionali > Filiere`; adivinhar URL nunca ia funcionar |
| **ADAMA e Bayer** | "403 — inconclusivo" | **abrem no navegador italiano.** O 403 era filtro anti-robô. |
| **ARIF Puglia** | "403 — inconclusivo" | `arifpuglia.it` dá 403 **até no navegador** — mas a ARIF publica em **outro domínio** |
| **APOL Lecce** | "sem URL no catálogo" | existe em **`http://`**, não `https://` |
| **FEM OpenPub** | "host não resolve" | é `openpub.fmach.it` |

**Três confirmações da lei `ROUTE_NOT_FOUND ≠ SOURCE_BLOCKED` numa só rodada.**

### 13.2 · O achado que mais muda o mapa

`arifpuglia.it` está morto para todo mundo. Mas a ARIF publica em **`agrometeopuglia.it`**:
*Notiziario Agrometeorologico **& Fitosanitario** Regionale*, semanal, saída às quartas,
**Anno XL** — quadragésimo ano de série. Mais um boletim meteorológico diário.

E, ao lado, a **APOL Lecce**: *Bollettino Mosca dell'olivo*, **9 edições semanais em 2026 e
14 em 2025**, com comprensório, fase fenológica, capturas em armadilha e percentual de
infestação. A edição nº 9 vale a partir de hoje.

**A Puglia deixou de ser lacuna.**

### 13.3 · Concorrentes — o que o navegador italiano conseguiu

| empresa | acesso | browser exigido | WAF | conteúdo |
|---|---|---|---|---|
| **ADAMA Italia** | `ACCESS_OK` | **SIM** | sim | artigo 03/06/2026 — Sonavio®/bifenox, inibidor de PPO, resistência em hortícolas |
| **Bayer Crop Science Italia** | `ACCESS_OK` | **SIM** | sim | *Mais Lab* — resistência de infestantes em milho, 4 técnicos nomeados, marca Dekalb |
| **Syngenta Italia** | `WAF_CHALLENGE` | — | sim | não vencido em 6s — **`NÃO SEI`, não RED** |

**Achado comparativo, observado e não inferido:** ADAMA e Bayer estão, no mesmo ano,
comunicando **o mesmo problema — resistência de plantas daninhas a herbicida** — em culturas
diferentes. São duas páginas datadas dos próprios sites.

⚠️ **Os dois não são `RAW_PRESERVED`.** Como o site recusa qualquer cliente sem navegador, os
bytes servidos não puderam ser guardados. Ficaram como **`BROWSER_RENDERED_EXTRACT`** — leitura
do DOM já montado, rotulada como tal. Não é a mesma coisa que documento preservado, e o guarda
impede que vire GREEN.

### 13.4 · As três fontes que não tinham endereço

| fonte | resultado |
|---|---|
| `IT-T3-003` **SIMFITO** | URL achada (`simfito.regione.campania.it`). Os boletins pedem **login**. `PUBLIC_CAPABILITY`, `NÃO SEI`. Não se tentou contornar. |
| `IT-T3-010` **APOL Lecce** | **Resolvida com amostra.** Era `http://`, não `https://`. **GREEN.** |
| `IT-T7-012` **PICA** | URL achada (`pica.cavit.it`) e **identidade provada**: o sistema mora no domínio da CAVIT. `AREA RISERVATA` com login → `OPERATIONAL_DATA = NOT_PUBLICLY_ACCESSIBLE`. Resultado negativo é resultado válido. |

Nenhuma das 54 rotas continua sem endereço.

### 13.5 · Onde parei, e por quê

| fonte | motivo da parada |
|---|---|
| **ISMEA Mercati** | rota do banco de preços encontrada (4 vistas), mas o painel não renderizou a tabela e nenhuma chamada de dados apareceu no tráfego. Critério de parada aplicado. `NÃO SEI`. |
| **Syngenta** | desafio anti-robô não vencido. `NÃO SEI`. |
| **Cooperativas (Agrintesa, Apofruit, Apo Conerpo, Ortofruit, VOG, Melinda, CAI)** | não alcançadas — **falta de tempo, não bloqueio**. Continuam `ROUTE_PROBED`. |
| **ICQRF, CNR IRIS, SIRFI** | idem. |

### 13.6 · Uma honestidade sobre o boletim da Puglia

O `IT-T3-008` ficou **YELLOW e não GREEN**, mesmo com amostra preservada e recorrência semanal
provada. Motivo: o documento tem 26 páginas e 55 imagens, e meu extrator simples leu só a parte
meteorológica. **A seção fitossanitária — que é a promessa da ficha — não foi lida.** Busca por
"oliv", "mosca" e "soglia" no texto extraído deu zero. Isso **não** prova que a seção não existe;
prova que não consegui ler. A REGRA 5 diz que a amostra tem de provar o que a ficha promete.

Fica P0 assim mesmo: com um extrator de PDF de verdade, provavelmente vira GREEN.

### 13.7 · Guardas

`regras/italy_contract_test.mjs` — **233 verificações, 0 falhas.**
Subiu de 144 para 233 porque entraram 16 guardas novos das leis desta rodada, e porque há mais
amostras para conferir. O guarda **encontrou duas falhas reais** durante a rodada: um manifesto
apontando para um nome de arquivo que eu tinha renomeado, e dois manifestos que faltavam. Os
dois foram corrigidos antes de passar.

Guardas novos, entre outros:

```
BROWSER_REQUIRED           ≠  SOURCE_UNAUTOMATABLE
BROWSER_RENDERED_EXTRACT   ≠  RAW_PRESERVED   (e nunca pode virar GREEN)
COMPANY_CLAIM              ≠  REGULATORY_FACT (carregada em cada manifesto de empresa)
SAMPLE_CAPTURED            =  RAW_PRESERVED + BROWSER_RENDERED_EXTRACT
fonte com login            ≠  GREEN
rota corrigida guarda      OLD_ROUTE e CURRENT_ROUTE
```

---

## 14 · CONTRATOS DE FONTE — 2026-09-07

### 14.1 · A conta não fechava, e eu errei em dois lugares diferentes

O fechamento anterior dizia 16 classificadas com `GREEN 9 · YELLOW 5 · RED 0 · NÃO SEI 2`,
e a rodada teria trazido `5 GREEN · 4 YELLOW · 3 NÃO SEI` = 12. **12 ≠ 9.**

**Erro 1 — números digitados à mão.** No JSON eu escrevi `YELLOW=5` e `NÃO_SEI=2`.
Calculado dos manifestos: `YELLOW=6` e `NÃO_SEI=1`.

**Erro 2 — erro de categoria.** Contei Syngenta, SIMFITO e PICA como "3 NÃO SEI" da rodada.
Nenhuma delas recebeu veredito analítico: são **estado de porta**. Daí o 12 falso.

**Lei nova, com guarda:**

```
ACCESS_CLASSIFICATION  ≠  ANALYTIC_VERDICT
```

Uma fonte pode ser `LOGIN_REQUIRED`, `WAF_CHALLENGE` ou `PUBLIC_CAPABILITY` **sem nunca**
receber GREEN/YELLOW/RED/NÃO SEI. Fora do placar.

A contabilidade agora é **calculada** por `provas/italy_accounting.mjs`, nunca digitada, e dois
guardas exigem que `ANALYTICALLY_CLASSIFIED == GREEN+YELLOW+RED+NÃO_SEI` e que o delta feche
**por `SOURCE_ID`**, não por subtração de números.

### 14.2 · Terceiro erro meu: a contagem do MASAF

Publiquei **269** organizações. Depois **264**. **Os dois errados.**
O certo é **272** (264 OP + 8 AOP), com **0 duplicados**.

O 269 vinha de um parse por linha que perdia códigos. O 264 vinha de um regex
`/^IT\/[A-Z]+\/\d+/` que **não casa código de AOP** — que tem *quatro* segmentos
(`IT/OLI/AOP/001`), não três. E `RAW_ROWS` são **324**: as 52 linhas a mais são cabeçalho,
título do regulamento, linhas de seção e linhas em branco do layout.

```
ROWS  ≠  UNIQUE_ORGANIZATIONS
```

### 14.3 · O leitor de PDF — e a Puglia resolvida

`pdftotext 4.06` **já estava instalado** na máquina. Testado contra os cinco PDFs:

| PDF | caracteres extraídos | resultado |
|---|---|---|
| Campania `SA-02-09` | 30.323 | OK |
| APOL `n.9` | 44.663 | OK |
| Puglia `N36` | 85.051 | OK |
| ARPAV `agro_01` | 10.758 | OK |
| AGRIOS *Direttive 2026* | 252.725 | OK |

**5 de 5.** Sem OCR — havia camada textual real o tempo todo; o que faltava era ferramenta.

**A seção fitossanitária da Puglia foi lida.** 32 blocos por cultura, cada um com
*Situazione Fenologica* / *Situazione Fitosanitaria* / *Programma di Difesa*. Pragas com nome
científico (`Bactrocera oleae`, `Plasmopara viticola`, `Tuta absoluta`, `Aonidiella aurantii`…),
limiares (**4-5%** para azeitona de óleo, 5%, 10%, 20%) e substâncias ativas nomeadas
(acetamiprid, flupyradifurone, deltametrina, spinosad, cyantraniliprole, pyriproxyfen,
*Bacillus thuringiensis*).

`IT-T3-008` foi de **YELLOW para GREEN** — **não** por eu ter conseguido ler, mas porque a
leitura mostrou que a fonte entrega o que a ficha prometia.

**Limite que permanece:** o **nome da cultura é imagem**, não texto. Pode ser *derivado* da praga
— e nesse caso o campo é `CROP_DERIVED`, **nunca** `CROP_EXTRACTED`.

### 14.4 · Treze contratos executáveis

`regras/italy_contracts.mjs` · matriz em `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md`

Cada um declara rota, identidade semântica, campo de data, frequência declarada **e** observada,
comportamento de atualização, requisito de arquivo, falhas esperadas, regra de fail-closed,
o que prova e o que não prova.

### 14.5 · Saúde ≠ veredito

`regras/italy_source_health.mjs` roda o contrato **contra o RAW já preservado**.
**13 HEALTHY · 0 DEGRADED · 0 FAILED · 0 UNKNOWN.**

São eixos diferentes: `IT-T2-002` (ARPAV) é **YELLOW** e está **HEALTHY**; `IT-T3-005`
(Terre dell'Etruria) é **NÃO SEI** e está **HEALTHY**.

### 14.6 · Os controles negativos viram vermelho

Um teste que nunca reprovou não é teste. O medidor corrompe o documento **em memória** — nunca
no disco — e exige que a saúde caia para `FAILED`. **8 mutações, 8 reprovaram.**

A mais importante: `IT-T2-001` com o PDF trocado por `<html>Access denied</html>` — exatamente a
armadilha do `/view` do Plone. **HTTP 200 e mesmo assim FAILED.**

### 14.7 · Se não coletarmos hoje, o que desaparece

Três fontes são **`FORWARD_ONLY`**:

| fonte | o que se perde |
|---|---|
| `IT-T3-005` Terre dell'Etruria | a edição semanal com os **139 pontos** e coordenadas — `/bollettini` dá 404 |
| `IT-T2-002` ARPAV Veneto | o boletim de cada uma das **32 zonas** — nome fixo, conteúdo sobrescrito |
| `IT-T2-004` SIAS Sicília | a janela de 11 dias por estação — URL fixa, janela móvel |

Para essas três vale a lei `SAME_URL ≠ SAME_DOCUMENT`: **nunca deduplicar por URL.** Hash novo é
observação nova. Medido: `agro_01` e `agro_09` têm hashes **e** datas de geração diferentes.

### 14.8 · Guardas

**270 verificações, 0 falhas.** Subiu de 233. Os novos defendem exatamente as leis desta missão —
e um deles **reprovou de verdade** durante a construção: pegou o contrato do MASAF usando "sede"
como `FACT_LOCATION`. Em vez de afrouxar o guarda, o contrato passou a explicar por que ali a sede
**é** o fato registrado — e o guarda passou a exigir essa justificativa por escrito.
