# LEI-PESQUISADORES — pesquisadores, sinal precoce e acesso: o que virou lei proposta, e o que é operação

Missão LEI-PESQUISADORES-E-SINAL-PRECOCE (coordenação 26/09, 14:40) e os acréscimos D87 (18:25), D88 (19:25), código
com a lei antiga (19:45) e texto do bot Luciano (19:50). Ordens escritas do dono: **D85**, **D87**, **D88**. Ramo
`lei-pesquisadores-v1`, sobre o vivo **`dc0de726`**. Só lei, know-how e texto de código (docstrings e uma constante
declarada, sem mudar comportamento). Sem rede; nada coletado; nada instalado.

Fontes: `DECISOES-DONO-2026-09-23.md` (D85, D87, D88) · `ALINHAMENTO-COLLECTION-INTELLIGENCE-MATRIZ.md` (A–F) ·
`ESTUDO-ORQUESTRACAO-24H-LUCIANO.md` (§6, §7, §8-R5) · `ESTUDO-SCRAPLING-DEEPSEEK.md` (rec. 1) ·
`RESULTADO-MONITORIZACAO.md`, `SINAL-PRECOCE-PDF.md`, `SINAL-PRECOCE-SERIES.md` · a exportação MUR.

> ⚠️ **Correção ao pedido:** «Salerno *Prays citri* 4 → 40» está errado na origem. O 4 → 40 é da ***Ceratitis
> capitata***; a *Prays citri* ficou em **0**. Escrito certo em todo o lado.

## 1. O que entrou

| onde | o quê | estado |
|---|---|---|
| **Bíblia da Coleta V1.4 → V1.5** | PARTE XXI: `COL-LAW-219` medição declarada não vira resumo · `COL-LAW-220` material público e fronteira de acesso (D88) | **PROPOSTA** — `LAW_STATUS CANONICAL` só depois da aprovação do dono · `IT ABSENT` |
| **Bíblia da Intelligence V0.3 → V0.4** | `INT-LAW-137` regra de modelo e condição de risco não provam ocorrência (secção 13, a seguir à 136) | **PROPOSTA** · `IMPLEMENTATION ABSENT` |
| **Código** | `coleta/scrap_http.py`, `coleta/social_rotas.py`, `leis/social_matriz.py`: a lei antiga («não finge ser navegador de gente») reescrita a citar a D88/`COL-LAW-220`; `scrap_http.POLITICA_DE_ACESSO` declarada e **não lida** (`LIGADA_AO_COMPORTAMENTO = False`) | comportamento **igual** (secção 6) |
| **Know-how** | §222 (a seguir à §221) + linha no topo | operação: MUR, ORCID, prioridade, D87, sinal precoce |
| registos | matriz de conformidade (2 linhas, placar V1.5, G-43/G-44), `docs/biblia/leis.json` regerado, diário de decisões, cartão da Bíblia da Intelligence (V0.4), teste de integração da Bíblia (bloco 2xx: 18 → 20) | — |

**Os textos das três leis são os do bot Luciano**, palavra por palavra nas partes REGRA / PODE / NÃO DEVE / PROVA.
Acrescentei só o que a casa exige de cada lei: POR QUÊ, MEDIDO, LIGA-SE A, ORIGEM, e na 220 a tabela «antes → com
esta lei» e a distinção origem ≠ programa. **IDs medidos livres** em 559 pontas de ramo: 0 usam `COL-LAW-219`,
`COL-LAW-220` ou `INT-LAW-137`.

**Uma primeira redação desta missão tinha nove leis** (COL-LAW-701..704, INT-LAW-310..315). Foi **substituída** pelas
três do bot, que são mais curtas e já trazem as correções da secção F. Nada dela ficou nas Bíblias.

## 2. As correções da matriz (secção F), aplicadas

| correção | como ficou |
|---|---|
| B4–B7 são **parciais**, não ausentes | a `INT-LAW-137` cita o que já existia (`095`, `131`, `035`, `102`, `024`, CAP-SCI/WIN/FUT) e acrescenta só o que faltava: contrato de `MODEL_RULE`, «condição compatível com risco», guarda contra extrapolar resistência. B6 fica no `CAP-FUT` como está — **nenhuma linha acrescentada** aos contratos de capacidade |
| B8: espécie da afirmação **por claim** | na `COL-LAW-219`; nunca o `SOURCE_DECLARED_EVIDENCE_CLASS` |
| B9: `STUDY_LOCATION/PERIOD` começam no claim/`FATO` | nenhuma coluna nova proposta |
| B10/B11 são operação/aquisição | só no know-how; nem Bíblia nem whitelist |
| «0 séries» superado | as leis citam 69 séries, 66 numéricas, 16 documentos |
| D85 não é verdade universal | «prioridade desta fase» no know-how; nada na Bíblia diz que pesquisador é a melhor fonte |
| D88 exige emenda fechada | `COL-LAW-220` |

## 3. O que já existia → o que as leis propostas acrescentam (nada duplicado)

| já era lei | o que acrescenta, e onde |
|---|---|
| `COL-LAW-043` (`FATO` preserva o declarado) · `202` (claim, `TARGET`) · `203` (valor original) · `214` (zero) | a proibição **explícita** de resumir a série, e a espécie da afirmação por claim (`219`) |
| `COL-LAW-019` (rota paga) · `026` (proteção da fonte) · `033` (procedência) · `205` (endpoint substituível) | a fronteira público/autorizado e a prova de cada captura contornada (`220`) |
| `INT-LAW-095` (correlação ≠ causalidade, «contrato mais forte») | o contrato de `MODEL_RULE` (`137`) |
| `INT-LAW-131` (forecast ≠ fact) · `035` · `102` · `024` | «condição compatível com risco ≠ ocorrência»; resistência não generaliza; recomendação da fonte ≠ ação (`137`) |
| `COL-LAW-009` · `034` · `205` · `042` · `INT-LAW-065` | **nada novo**: pessoa, instituição, estudo, modelo e canal já são identidades distintas; identidade ≠ expertise. Citado na abertura da PARTE XXI |
| `COL-LAW-207` · `208` · `011` · `INT-LAW-020` · `151` · `290` | **nada novo**: é a D87 (descoberta de perfis = bot de fontes + Intelligence; o Scrap captura). Citado na PARTE XXI e na §222 |

## 4. Provas das Bíblias
- `py provas/valida_biblia.py`: **11/11 PASS** — **107 leis** · IMPLEMENTED 37 · PARTIAL 48 · **ABSENT 20** ·
  NOT_APPLICABLE 2; `leis.json` regerado (`--build`).
- `tests/test_biblia.py` + `tests/test_integracao_biblia.py`: **87 passam**.
- Portão de contradição da Intelligence: **[]** (um veredito CORRENTE — o 33.4 da V0.4 —, e o fecho nomeia a secção 32).
- Intelligence: **174 leis** (era 173), 0 alteradas.
- Testes da Intelligence com o **texto final**, base `dc0de726` × ramo, cada um numa cópia própria (`test_biblia`,
  `test_integracao_biblia`, `test_os_consertos_da_intelligence`, `test_o_mapa_da_intelligence_nao_mente`,
  `test_atomicidade_da_intelligence`, `test_o_controle_separa_lei_de_mencao`): base **104 falham · 249 passam**; ramo
  **105 falham · 248 passam**. As 104 são as mesmas, pelo nome (antigas, do espelho do mapa em `test_atomicidade`).
  A **1 nova é a esperada**: `test_M5_o_ponto_fixo…` — o carimbo do mapa ainda é o das Bíblias antigas; fecha quando o
  mapa for regerado (secção 7).

## 5. A lei que estava escrita no código (D88 · estudo Scrapling, rec. 1) — sítios medidos

`git grep` em `*.py *.mjs *.js *.md` (fora de testes, dados, gerados, portal, handoff), por «finge ser navegador»,
«navegador de gente», «não resolve CAPTCHA», «troca de IP», «agente se identifica», «contornar …», «sem contorno»,
«anti-robô», «WAF_CHALLENGE», «User-Agent real»: **156 linhas**; 84 são o Atlas de fontes (estado medido de cada
fonte, p. ex. `WAF_CHALLENGE`), não lei. O resto, classificado:

| sítio | diz | o que é | feito |
|---|---|---|---|
| `coleta/scrap_http.py:38-39` | «não resolve CAPTCHA, não troca de IP…, **não finge ser navegador de gente** … nunca uma tentativa mais esperta» | **lei** que contradiz a D88 | **reescrito** a citar D88/`COL-LAW-220`; login, cookie, pago e IP continuam fora |
| `coleta/scrap_http.py:51` (`AGENTE`) | «o agente se identifica. **Não há ganho em mentir**» | **lei** que contradiz a D88 | comentário reescrito; **o valor do `AGENTE` não mudou** |
| `coleta/scrap_http.py` (novo) | — | política declarada | `POLITICA_DE_ACESSO` (não lida por nenhum código) |
| `coleta/social_rotas.py:37-38` | o mesmo bloco do `scrap_http` | **lei** que contradiz a D88 | **reescrito** |
| `leis/social_matriz.py:243, 279` | comentários: «contornar login wall, CAPTCHA **ou bloqueio**» | política que contradiz a D88 na parte «bloqueio» | reescritos: login wall e CAPTCHA pago continuam fora; anti-robô de público permitido, **ainda não usado** nestas rotas |
| `leis/social_matriz.py:439, 705` | valores da matriz: «sem contornar bloqueio», «contornar login wall/CAPTCHA/bloqueio» (fechado) | **dado** da rota: descreve o que aquela rota faz hoje | **não mexido** (mudar dado muda comportamento; é do engenheiro do Scrap) |
| `leis/social_matriz.py:851` | «medido … sem contornar muro» | registo de uma medição | não mexido (é história) |
| `guarda/social_sessao.py:76` | «não troca fingerprint, não esconde que é automação» | a guarda da **sessão com login** | não mexido: login continua com o dono |
| `ferramentas/cdp.py:27`, `ferramentas/navegador.py:8`, `coleta/instagram_janela.py:58` | «não resolve CAPTCHA» | descrição do que o código faz | não mexido: compatível (solver pago continua fora) |
| `coleta/adaptador_linkedin.py:1346-1410`, `coleta/adaptador_youtube.py:641, 852`, `coleta/scrap_capacidades.py:315` | «não contorna controlo de acesso / login / paywall» | login e paywall | compatível — não mexido |
| `curadoria/capturador.py:675`, `amostrar.py:10`, `caracterizador.py:138`, `atlas_social.py:70`, `escrever_no_atlas.py:111`, `RELATORIO-MISSAO-03.md:178` | «não contorna muro» (consentimento/login) | descrição de ferramentas | compatível — não mexido |
| `candidatas/*.mjs`, `guarda/italy_preserve.mjs:107`, `candidatas/ITALY-SOURCE-MASTER-V1.md:299`, `docs/operacao/ITALY-SINTONIA-SCRAP-SOURCE-TEST.md` | «não se tentou contornar autenticação»; `WAF_CHALLENGE` como estado | registo de medições antigas | não mexido (história); `WAF_CHALLENGE` passa a ser **re-tentável** pela 220 |
| `docs/sintonia-scrap/D23-LINKEDIN-ORG-VIDEO.md:91`, `D24-VIDEO-DE-PESSOA.md:130, 276`, `C13-YOUTUBE-PUBLIC-AUDIO.md:159`, `provas/canario_d23_*.py:29`, `provas/canario_d24_*.py:27, 309` | «sem contornar login wall, CAPTCHA ou **bloqueio**» | registo das decisões D23/D24 e dos canários | não mexido (história); a `COL-LAW-220` diz o que mudou |
| `docs/decisoes/ADR-TAXONOMIA-DE-FALHAS-E-POLITICA.md:101`, `docs/arquitetura/SINTONIA-SCRAP-TARGET.md:90` | robots lido «com o User-agent real» | robots | compatível: a D88 não fala de robots, e a 220 diz «nunca ignorar robots» |

## 6. Testes do Scrap, base `dc0de726` × ramo (o texto não mudou comportamento)
Os 45 ficheiros de teste que importam `scrap_http`, `social_rotas` ou `social_matriz`, cada versão numa cópia própria,
rede fechada: base **1 225 passam · 30 falham** · ramo **1 225 passam · 30 falham** — **as mesmas 30, pelo nome; zero
diferenças.** A reescrita é só de texto.

## 7. O mapa
**Não regerado — PRONTO-SEM-MAPA**, por ordem da coordenação (22:05): o mapa do lote 4 é feito uma vez só pela INTEGRA.
Os `.md` de lei e as docstrings mudadas são fonte rastreada pelo mapa: até ele ser regerado, `test_M5_o_ponto_fixo…`
(`test_o_controle_separa_lei_de_mencao`) fica vermelho, e é essa a única falha nova medida (secção 4).

## 8. Limites declarados
- **As três leis são propostas.** Não estão em vigor até o dono aprovar; e mesmo em vigor, a implementação é `ABSENT`.
- **A permissão da D88 não está ligada.** A matriz do Scrap e o `AGENTE` fazem o mesmo que antes; ligar uma rota com
  impressão digital de navegador é do engenheiro do Scrap, com rota nomeada, canário, teto e proveniência.
- **Listas oficiais fora do MUR** (CNR, CREA, FEM): não medidas.
- **O que as colunas da tabela APOL medem**: NAO SEI (cabeçalho em imagem).
- A reavaliação do bot Luciano sobre esta redação fica para quando ele voltar.

## EM PALAVRAS SIMPLES
- **O que eu fiz:** escrevi na "constituição" da coleta e na da inteligência três regras novas, com o texto que o bot
  Luciano redigiu. Elas ainda **não valem**: só entram quando o dono aprovar.
  - **Números não se resumem.** Se o boletim diz "1, 4, 11, 29 insetos na armadilha", guardamos os quatro números,
    e não só "está subindo". É assim que se vê o aviso cedo — em Salerno, a mosca-do-mediterrâneo foi de 4 para 40
    capturas em duas semanas, antes de qualquer alerta.
  - **O que é público pode ser buscado por outro caminho técnico** (um navegador de verdade, passar a barreira
    anti-robô). O que é pago, precisa de senha ou é privado, **nunca**.
  - **"O clima favorece a doença" não é "a doença apareceu".** E um estudo pequeno sobre resistência não prova que
    um produto deixou de funcionar.
- **O que é operação ficou no caderno de know-how, e não na constituição:** a lista oficial de professores da Itália
  (MUR, 278 especialistas em pragas e doenças em 33 universidades), seguir as redes deles, e quem descobre perfis
  (o robô de fontes, guiado pela inteligência; o sistema de captura só captura).
- **No código:** apaguei a frase "não finge ser navegador de gente", que contrariava a decisão do dono. **O programa
  faz exatamente o mesmo que antes** — conferi com 1 225 testes nas duas versões, zero diferenças.
- **Perdeu-se alguma coisa?** Não. A primeira versão que escrevi (nove regras) foi trocada pelas três do bot, mais
  curtas; está no histórico.
- **Pode quebrar?** Nada funciona diferente. Só um teste, que confere o "mapa" do sistema, fica vermelho até alguém
  redesenhar o mapa — a coordenação vai fazer isso no lote 4.
- **O que muda para você:** decidir se aprova as três regras. Até lá, são proposta.
