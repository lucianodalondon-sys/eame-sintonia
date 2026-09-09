# SINTONIA · SECURITY FOUNDATION (S0)

> Este ficheiro nao declara que o SINTONIA e seguro.
> Declara, com medicao, ONDE ele esta.

```
SECURITY_BRANCH       claude/security-foundation-v1
SECURITY_BASE_BRANCH  claude/system-map-freshness-v1
SECURITY_BASE_HEAD    baaddcf191778e01297427e7a0b167d66c9c4354
WORKTREE              isolado (nao partilha ficheiros com nenhuma missao activa)
MEASURED_AT           2026-09-09
```

**WHY_THIS_BASE.** Medido, nao herdado. `claude/system-map-freshness-v1` e a
unica linha que contem integralmente `claude/collection-foundation-integration-v1`
(0 commits a frente dela) e carrega a maior superficie de cliente publicada
(95 ficheiros, 30.461.784 bytes em `italia-portale/client/`, contra 94 ficheiros
em `main`). `main` esta 1 commit a frente e esse commit e um registo de workflow,
nao superficie de aplicacao. Escolher `main` por habito teria auditado uma
superficie menor do que a que ja esta publicada.

Nada foi mergeado em nenhuma linha activa. Nada de force push. Producao,
System Map, Collection e Supabase live nao foram tocados.

---

## 1. O QUE E PUBLICO HOJE — MEDIDO, NAO ASSUMIDO

O repositorio **e publico**. Medido pela API do GitHub em 2026-09-09:
`"private": false`, `"visibility": "public"`, criado 2026-08-28.
Um anonimo ve **85 branches**, **0 delas protegidas**, e pode clonar
**1.517 ficheiros / 196.872.709 bytes**.

| Familia | Ficheiros | Bytes |
|---|---:|---:|
| ACERVO / evidencia | 599 | 137.906.986 |
| Cliente do portal (servido) | 95 | 30.461.784 |
| Arquitectura interna / research / handoff | 204 | 6.379.301 |
| Esquema de base de dados | 45 | 4.760.130 |
| System Map | 58 | 3.704.745 |
| Motor proprietario (colectores, portoes, guarda) | 152 | 2.419.258 |
| CI / tooling | 98 | 1.159.993 |
| Regras / leis | 33 | 494.339 |
| Outros | 233 | 9.586.173 |

### O que esta LIVE, sem qualquer autenticacao

Provado por pedido HTTP anonimo a `sintonia-eame-preview.vercel.app`:

| Recurso | HTTP | Bytes |
|---|---:|---:|
| `/italy-handoff-v21.js` | 200 | 11.198.842 |
| `/portale` | 200 | 1.090.951 |
| `/meeting-intelligence-snapshot.json` | 200 | 646.889 |
| `/accesso` | 200 | 20.698 |

Dentro do ficheiro de 11 MB servido em producao, contado no bytes descarregados:
**3.352 URLs de fonte distintos**, **7.133 registos `CLIENT_SAFE:false`**,
**3.323 registos `QA_UNREVIEWED`**, **981 campos `DERIVATION_FORMULA`**.

### O que esta LIVE nos previews

**Deployment Protection esta DESLIGADA** (medido no projecto Vercel
`sintonia-eame-preview`, equipa London Creative, plano Pro:
`passwordProtection.enabled=false`, `ssoProtection.enabled=false`,
`trustedIps.enabled=false`). Cada push de branch cria um URL de preview
anonimamente acessivel. Os ultimos 20 deployments sao todos previews.

No preview mais recente, resposta 200 anonima para:
`/system-map/` (9.254 B), `/system-map/state.generated.json` (**1.058.169 B**),
`/italy-v21.js` (**10.359.119 B**), `/casa` (57.623 B).

> **PREVIEW URL ≠ ACCESS CONTROL.** Esta provado, nao inferido.

---

## 2. O QUE PROTEGE A IP — E O QUE SO PARECE PROTEGER

**Protege de facto:**
- `.vercelignore` + `outputDirectory` — duas fechaduras reais. `/data`, `/build`,
  `/research`, `/docs`, `/supabase`, `/scripts`, `/tests`, `/.github` e todo o
  `*.md` nao chegam ao contentor. Confirmado live: `/package.json`,
  `/.vercelignore`, `/supabase/migrations/*.sql` respondem 404 no dominio publico.
  **Esta barreira e boa e deve ser preservada.**
- Vendor local em vez de CDN — nenhum script de terceiros e carregado em runtime.
  Medido: os unicos hosts externos referenciados no HTML sao `www.w3.org`
  (namespaces SVG).
- Ausencia de segredos. Ver seccao 4.

**Nao protege nada:**
- O ecra `accesso.html` **nao e autenticacao**. O `submit` faz
  `window.location.href = 'casa.html'`. Nao ha sessao, cookie, JWT, nem
  verificacao de servidor. A propria pagina declara-o:
  *"Ambiente dimostrativo — nessuna autenticazione."* Isto e honesto, e um
  DEMO. Nao e login.
- Repositorio privado nao protegeria o JavaScript. O cliente e servido na
  integra a quem abre a pagina.
- Minificacao/ofuscacao nao existem aqui e nao ajudariam: o corpus e JSON.

---

## 3. CLIENTE E MOTOR ESTAO NO MESMO SITIO

O `italy-v21.js` (10,4 MB) carrega **26 coleccoes / 7.078 registos canonicos**,
dos quais **3.882 sao `CLIENT_SAFE=false`**. Entre elas:

```
sources                189    (registo de fontes, com URL e endpoint)
cropEconomicWeight   2.978    (com DERIVATION_FORMULA e IS_DERIVED_BY_SINTONIA)
products.relationships 2.030
competitors            577
science                 88   researchers  60   voices  79   channels  62
```

Contado no bloco: **1.438 URLs de fonte distintos** no ficheiro de branch,
**3.352** no ficheiro servido em producao.

Um concorrente que abra o DevTools obtem: onde o SINTONIA colhe, com que
frequencia, com que estado de acesso e limitacao por fonte, o que ele deriva e
com que formula, o que ele considera nao-verificado, e o corpus inteiro.

> **CLIENT NEEDS THE ANSWER ≠ CLIENT NEEDS THE ENGINE.**
> Hoje o browser recebe a receita inteira, nao a resposta.

O `state.generated.json` do System Map acrescenta a planta: **145 componentes**,
**556 arestas**, **1.351 ficheiros rastreados**, e **9 BURACOS nomeados com
ficheiro e numero de linha** — os pontos fracos declarados do proprio sistema.
Para um auditor isso e virtude. Publicado anonimamente, e um mapa de ataque.

---

## 4. SEGREDOS — VARRIDO, TREE E HISTORIA

**Nenhum segredo real encontrado. Nenhuma rotacao exigida por esta medicao.**

- Tree actual: 3 ficheiros com correspondencia, todos falsos positivos
  (padroes de deteccao em `pacote/pacote_montar.py`, DSNs `localhost` de teste).
- Historia: **9.809 blobs** varridos em todos os refs. Correspondencias
  resolvidas para 4 ficheiros: DSNs `postgresql://…@localhost:5432/descartavel`
  de CI descartavel, e uma constante literalmente chamada `FAKE_JWT` em testes.
  Um dos testes existe precisamente para provar que o DSN nunca e registado em log.

Valores nao sao impressos aqui, nem foram testados contra qualquer servico.

```
SECRET_SCAN_CURRENT_TREE = DONE     SECRETS_FOUND = 0
SECRET_SCAN_HISTORY      = DONE     ROTATION_REQUIRED = NO
SERVICE_ROLE_IN_CLIENT   = NO   (medido: 0 ocorrencias em italia-portale/client)
```

Nota de lei: `PRIVATE NOW ≠ NEVER PUBLIC`. Aqui a lei nao morde, porque nada
sensivel esteve la. O que esteve publico — e continua — e a tecnologia, nao a
credencial.

---

## 5. BASE DE DADOS

Medido nas 24 migrations, nao apenas na 006.

```
TABELAS CRIADAS          66
RLS ENABLED              54
SEM RLS                  12
CREATE POLICY             0        <-- zero, em todo o repositorio
GRANT explicito           0
VIEWS security_invoker   21        <-- correcto
VIEWS security definer    0
```

Duas leituras, ambas verdadeiras:

1. As 54 tabelas com RLS e sem politica sao **deny-all** para `anon` e
   `authenticated`. So `service_role` (que ignora RLS) chega la. Seguro por
   ausencia — e tambem significa que **nao existe modelo de autorizacao nenhum**.
2. As **12 tabelas sem RLS** sao a superficie a medir com urgencia. No default
   do Supabase, uma tabela do schema `public` sem RLS e legivel — e por vezes
   escrivel — pela chave publicavel via PostgREST. Entre elas estao
   `fonte_externa`, `decisao_de_coleta` e `etapa_da_corrida`: o registo de
   fontes e as decisoes do colector. Isto e IP nuclear.

Nao foi tocado nada live (proibido nesta missao), por isso o estado real fica
`UNKNOWN` ate haver prova. E o unico item candidato a P0 desta rodada.

> **RLS ENABLED ≠ RLS POLICY PROVED. AUTHENTICATED ≠ AUTHORIZED.**
> E a prova futura tem de testar ALLOW **e** DENY.

---

## 6. CADEIA DE FORNECIMENTO E CI

Melhor do que o esperado, e vale registar o que ja esta certo:

- **`permissions:` declarado explicitamente em todos os 15 workflows.**
  Nenhum `write-all`.
- **Nenhum `pull_request_target`.** Este era o risco grave: existem
  **5 workflows em runners self-hosted (Windows, maquina do dono)** num
  repositorio publico. Todos correm **so** em `workflow_dispatch`. Um fork nao
  os alcanca. A porta esta fechada — mas esta fechada por convencao, nao por
  regra: basta alguem acrescentar `pull_request` a um deles.
- Sem `curl | bash`. Sem segredos passados a terceiros. Sem checkout de codigo
  nao confiavel.
- Actions em tag movel (`@v4`, `@v5`), todas first-party da `actions/`. Risco
  baixo, nao nulo.
- **Sem lockfile.** `package.json` nao declara dependencias e o vendor esta
  commitado — a superficie npm e efectivamente zero.
- **Sem CODEOWNERS. Sem `dependabot.yml`. Sem branch protection (0/85).**

---

## 7. CABECALHOS E FRONTEND

Presentes hoje (medido em `curl -I` na producao):
`strict-transport-security: max-age=63072000; includeSubDomains; preload`
(default da plataforma), `x-content-type-options: nosniff`,
`referrer-policy: strict-origin-when-cross-origin`.

Ausentes: **CSP**, `frame-ancestors`/`X-Frame-Options`, `Permissions-Policy`,
politicas cross-origin. Presente e provavelmente indesejado:
`access-control-allow-origin: *`.

**Nao colar uma CSP da internet.** Medido: `casa.html`, `portale.html` e
`accesso.html` usam `<style>` inline e `<script>` inline, ha `data:` URI no
favicon, e `babel-standalone` (3,1 MB) esta no vendor — o que implica avaliacao
de codigo em runtime. Uma CSP `script-src 'self'` parte o portal hoje.
`CSP_REQUIRED = YES`, `BREAKAGE_RISK = HIGH`, `SAFE_POLICY_CANDIDATE` = comecar
por `frame-ancestors 'none'` e `Permissions-Policy`, que nao dependem de inline.

DOM: `innerHTML` e usado (18x em `system-map/map.js`, 7x em `support.js`,
2x em `casa.html`). Nao ha entrada de utilizador: o portal e estatico, nao le
parametros de URL para o DOM, e nao faz `fetch` para lado nenhum excepto
`state.generated.json` local. Sem API, sem serverless, sem superficie SSRF.
Classificacao: **risco baixo hoje, risco alto no dia em que existir input**.

---

## 8. AS DUAS PERGUNTAS

### Se a TI da ADAMA auditasse amanha

**Reprovaria:** ausencia de autenticacao e de autorizacao; ausencia de
isolamento por pais; previews sem proteccao; ausencia de politicas RLS provadas;
ausencia de log de acesso e de auditoria; ausencia de backup/restore provado;
ausencia de plano de resposta a incidente; repositorio publico com codigo de
producao.

**Passaria:** higiene de segredos (limpa, tree e historia); permissoes de CI
explicitas; ausencia de `pull_request_target`; separacao build-input/public-output
via `.vercelignore`, provada por HTTP; TLS e HSTS; sem dependencias externas em
runtime; views com `security_invoker`.

**Ainda nao existe:** SSO, MFA, RBAC, WAF, rate limit, retencao, apagamento,
pentest, DPIA.

### Se um concorrente copiasse amanha

Obteria, hoje, sem nenhum obstaculo: o corpus canonico inteiro, o registo de
fontes com URLs e endpoints, as formulas de derivacao, a marcacao de qualidade
por registo, o mapa de 145 componentes e 556 arestas com os 9 pontos fracos
nomeados por ficheiro e linha, e 197 MB de repositorio com o motor de coleccao,
os portoes e as regras.

O que **nao** obteria: credenciais, dados da ADAMA (nao existem no sistema hoje),
e o julgamento humano por tras das regras. Isso e pouco consolo.

---

## 9. PRIORIDADES

```
P0  Superficie anon do Supabase nas 12 tabelas sem RLS.
    ESTADO: UNKNOWN — nao medido live por proibicao desta missao.
    Impacto se confirmado: leitura (ou escrita) anonima do registo de fontes
    e das decisoes do colector. CONTENCAO MINIMA: habilitar RLS nas 12.
    P0_CONFIRMADO_NESTA_RODADA = 0. P0_A_MEDIR = 1.

P1  Motor + acervo proprietario servidos ao browser (11,2 MB, live, provado).
P1  Repositorio publico com 197 MB de tecnologia; 0/85 branches protegidas.
P1  Fronteira cliente/servidor inexistente — o portal E o motor.
P1  Autorizacao real inexistente (nem pais, nem papel, nem departamento).

P2  Deployment Protection desligada — previews anonimos com o System Map.
P2  Runners self-hosted em repo publico protegidos so por convencao.
P2  Logging e auditoria inexistentes.
P2  CSP, frame-ancestors, Permissions-Policy, CORS `*`.

P3  Mapeamento ASVS, evidencia formal, pentest, formalizacao contratual da IP.
```

## 10. FASEAMENTO

**AGORA — sem risco, sem parar ninguem.** Ligar branch protection em `main` e
nas linhas activas. Confirmar secret scanning + push protection + CodeQL (todos
gratuitos em repo publico). Acrescentar `dependabot.yml` e CODEOWNERS. Ligar
Deployment Protection nos previews (o preview e para nos, nao para o mundo).
Acrescentar `frame-ancestors` e `Permissions-Policy`. Medir as 12 tabelas.
Ligar o SECURITY CHECK do ratchet. Nenhum destes muda comportamento do produto.

**ANTES DO PILOTO COM UTILIZADORES REAIS.** SSO com a identidade corporativa da
ADAMA. Sessao real de servidor. RLS com politicas provadas em ALLOW e DENY.
Modelo de autorizacao com pais, papel e departamento. Log de acesso. Repositorio
privado, com a transicao desenhada para nao partir o freshness do System Map.

**ANTES DO CONTRATO / GO-LIVE.** Fronteira cliente/servidor: o browser recebe a
projeccao, nao o corpus. Rate limit e WAF (disponiveis no plano Pro actual).
Backup e restore provados. Uma pagina de resposta a incidente. Isolamento
producao/preview.

**ANTES DA AUDITORIA DA TI DA ADAMA.** Mapeamento ASVS L2 dos requisitos
relevantes com prova executavel. Pentest. Retencao e apagamento. Evidencia por
controlo com `LAST_VERIFIED`.

## 11. ARQUITECTURA RECOMENDADA

Hipotese a confirmar, deliberadamente simples — mais servicos nao e mais
seguranca, e a stack actual (GitHub + Vercel + Supabase) chega:

```
REPO PRIVADO -> CI -> BACKEND PROTEGIDO (motor, regras, acervo)
                          |  API autorizada, projeccao minima
                      PORTAL (apresentacao + projeccao por papel)
                          |  SSO
                      UTILIZADOR ADAMA
```

`USER_FRICTION = NONE` (entra com a conta que ja tem, sem senha nova).
`DEVELOPER_FRICTION = LOW` (commit normal; so e travado ao introduzir exposicao
nova e comprovadamente perigosa).

## 12. SECURITY RATCHET

Baseline congelada em `security-baseline.json` neste commit. O gate futuro
`SECURITY CHECK` — independente de COLLECTION CHECK e de SYSTEM MAP CHECK —
responde **"esta mudanca piorou a seguranca?"**, nao "esta tudo perfeito?".

```
NEW_CRITICAL = 0   NEW_HIGH = 0   NEW_SECRET = 0
NEW_PUBLIC_ENGINE_EXPOSURE = 0
NEW_PULL_REQUEST_TARGET = 0        (a porta dos runners self-hosted)
NEW_TABLE_WITHOUT_RLS = 0
```

Divida herdada fica visivel. Regressao nova fica bloqueada.

## 13. LEIS QUE FICAM ESCRITAS

```
AUTHENTICATED ≠ AUTHORIZED
RLS ENABLED ≠ RLS PROVED
PRIVATE REPO ≠ PRIVATE CLIENT CODE
MINIFIED ≠ SECRET
HIDDEN URL ≠ ACCESS CONTROL
CLIENT NEEDS ANSWER ≠ CLIENT NEEDS ENGINE
PUBLIC DEMO ≠ PRODUCTION
PREVIEW URL ≠ ACCESS CONTROL
BUILD INPUT ≠ PUBLIC OUTPUT
SECRET DELETED ≠ SECRET NEVER EXPOSED
SECURITY TOOL EXISTS ≠ SECURITY CONTROL WORKS
CONTROL DECLARED ≠ CONTROL TESTED
OLD SECURITY DEBT ≠ PERMISSION TO ADD NEW DEBT
SECURITY ≠ BUREAUCRACY
ACCESS SCREEN ≠ AUTHENTICATION
ONE CONCEPT → ONE OWNER
```

## 14. O QUE NAO FOI TOCADO

```
PRODUCTION_TOUCHED    NO
SYSTEM_MAP_TOUCHED    NO
COLLECTION_TOUCHED    NO
SUPABASE_LIVE_TOUCHED NO
REPO_VISIBILITY       inalterada (continua publica, por decisao desta missao)
FORCE_PUSH            NO
MERGE INTO ACTIVE     NO
```
