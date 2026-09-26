# LEI-PESQUISADORES — os pesquisadores e o sinal precoce entram na lei

Missão LEI-PESQUISADORES-E-SINAL-PRECOCE (coordenação 26/09, 14:40; ordem escrita do dono **D85**). Ramo
`lei-pesquisadores-v1`, a partir do vivo `278cd489`. **Só lei e know-how, sem código de produção.** Sem rede; nada
coletado; nada instalado.

Fontes lidas: D85 em `auditoria-madrugada/DECISOES-DONO-2026-09-23.md` · `ALINHAMENTO-DONO-COLLECTION-INTELLIGENCE.txt`
· `ALINHAMENTO-COLLECTION-INTELLIGENCE-MATRIZ.md` (secções A–E) · `RESULTADO-MONITORIZACAO.md` e `SINAL-PRECOCE-PDF.md`
(as medidas de hoje do sinal precoce) · a exportação MUR `MUR-07-AGRI-05-DOCENTES.json`.

> ⚠️ **Uma correção ao pedido.** O pedido trazia «Salerno *Prays citri* 4 → 40». O relatório de origem já se tinha
> corrigido: o 4 → 40 é da ***Ceratitis capitata*** (mosca-do-mediterrâneo) nos citrinos de Angri, e a *Prays citri*
> ficou em **0**. Escrevi a versão corrigida em todo o lado.

## 1. O que entrou

| onde | o quê | IDs |
|---|---|---|
| **Bíblia da Coleta V1.4 → V1.5** | PARTE XXI «O que o campo diz, e quem o diz» — 4 leis (a 704 veio da D88, acréscimo das 19:25) | `COL-LAW-701` · `702` · `703` · `704` |
| **Bíblia da Intelligence V0.3 → V0.4** | secção 38 «O sinal fitossanitário, o modelo e quem sabe» — 6 leis; uma linha nova em `CAP-FUT` e em `CAP-SCI` | `INT-LAW-310..315` |
| **Know-how** | §222 depois da §221; linha nova no topo («Última atualização material») | §222 |
| registos da lei | matriz de conformidade (3 linhas, placar V1.5, G-43..45), `docs/biblia/leis.json` regerado, diário de decisões, cartão da Bíblia da Intelligence no registo (V0.4), teste de integração da Bíblia (bloco 7xx) | — |

## 2. Bíblia da Coleta — o diff conceitual

**`COL-LAW-701` · A série que a fonte declara chega como veio.** Capturas, ovos/larvas/adultos, voo, geração,
% de infestação, incidência, severidade e limiar chegam **valor a valor, como escritos**, com local/armadilha, data,
organismo, cultura, fase e trecho. **Proibido**: resumir («1,4,11,29» ≠ «a subir»), média, tendência, completar
semana em falta, dar nome a coluna de cabeçalho não lido (fica NAO SEI), converter unidade sem guardar a original,
apagar o zero declarado. O limiar é declaração da fonte, não observação. *A tendência é da Intelligence.*
`IT = ABSENT` (sem campo no READY; o leitor de PDF vive num ramo de missão).

**`COL-LAW-702` · A fonte diz a espécie do que afirma.** O claim **pode** levar `CLAIM_KIND` = OBSERVACAO · PREVISAO ·
MODELO · RECOMENDACAO · CENARIO · HIPOTESE · **UNKNOWN por omissão**, tirado da **marca no trecho** — nunca do tipo da
fonte, do `SOURCE_DECLARED_EVIDENCE_CLASS` (é do contrato) nem da data. Espécie não se promove. Frase com duas
espécies = dois claims ou UNKNOWN. **Estende a 202 (um campo a mais no que o claim pode preservar); continua
`TARGET`.** `IT = ABSENT`.

**`COL-LAW-703` · A pessoa-fonte prova-se pela lista-mestra, e segue-se pela porta canónica.** Identidade =
**lista-mestra oficial (MUR «Cerca Università»; fora do MUR a lista de cada instituição) + instituição + setor**.
ORCID/OpenAlex/Crossref/IRIS ligam obras, não provam identidade sozinhos. Nome igual sem instituição+setor =
AMBIGUO; homónimos nunca se fundem. Canais públicos entram pelas candidatas com os TIPOS existentes e PARA_QUE;
ligam-se à pessoa **por prova**. Limites D16–D24 inteiros (sem login/cookie/conta/CAPTCHA/rota paga; LinkedIn só
POST público; minimização; apagar a pedido; 5 pedidos/domínio/rodada). `IT = ABSENT`.

**`COL-LAW-704` · O que é público pode ser alcançado por outra rota técnica; o que é pago não (D88, acréscimo 19:25).**
**Permitido** para material público: passar anti-robô (Cloudflare/Turnstile), navegador real com JavaScript, navegador
furtivo, outro agente, outra rota. **Nunca**: conta paga, paywall, assinatura, material não público. **Só com o dono**:
login com conta (mesmo gratuita), cookie de sessão, CAPTCHA por serviço pago, proxy pago. **Continua**: uso interno,
dado pessoal, teto por domínio (a D88 escreve ≤ 5 em 24 h), VPN IT provada, **a rota usada escrita no RAW**, nada pago
sem aprovação, `PLATFORM_POLICY_STATUS` medido ao lado de `OWNER_AUTHORIZED`. A lei tem a tabela «antes → agora»:
D16 (contorno de login/robots), D23/D24 (login wall/CAPTCHA/bloqueio) e a própria `COL-LAW-703`, cuja lista «NÃO DEVE»
foi alinhada. `robots.txt`: a D88 não fala dele — **não foi tocado**. `IT = PARTIAL` (teto, egresso e proveniência
existem; a permissão não está ligada na matriz do Scrap — G-46).

**Números novos:** 701..704, porque a faixa 6xx já foi usada por um ramo lateral (Card Contract, 601..617).
Medido em **559 pontas de ramo**: 0 usam `COL-LAW-7xx` ou `INT-LAW-31x`.

## 3. Bíblia da Intelligence — o diff conceitual

| lei | diz |
|---|---|
| `INT-LAW-310` | **SINAL PRECOCE → CONFIRMAÇÃO → ALERTA → RECOMENDAÇÃO → INTERVENÇÃO.** O boletim não é o 1.º sinal. Os degraus são posição temporal de objetos que já existem (não objetos novos, `INT-LAW-272`); cada um guarda o seu tempo; degrau em falta = UNKNOWN e COLLECTION_GAP. |
| `INT-LAW-311` | Contrato mínimo de **MODEL_RULE**: origem, variáveis de entrada, limiares, fase, validade (cultura·organismo·região·período), horizonte, desempenho, limites. Sem validade ou limiares = hipótese, nunca regra. É o «contrato mais forte» que a `INT-LAW-095` pedia e não dizia qual. |
| `INT-LAW-312` | **Condição compatível com risco ≠ ocorrência.** Regra × clima × fase × lugar dá, no máximo, sinal de risco. Clima previsto dá condição prevista. Só observação no campo faz passar a ocorrência. |
| `INT-LAW-313` | **Resistência** exige espécie, população, local, período, n, molécula/modo de ação, método, resultado e limites; vale para a população testada; **nunca** vira «o produto não funciona». |
| `INT-LAW-314` | **Expansão geográfica/invasora** é espécie do `CAP-FUT`: deteção ≠ estabelecimento ≠ expansão. |
| `INT-LAW-315` | O **`CAP-SCI` recebe a Cadeia B** (relação causal, MODEL_RULE, limiar, resistência) além da força de evidência; fontes além do artigo (tese, dataset, código, DSS, *proceedings*, seminário); a pessoa vem provada da Collection (`COL-LAW-703`). |

Cabeçalho `VERSION = V0.4`, `REVISED = 2026-09-26`; o veredito da V0.3 passou a `HISTORICO` (não se apagou) e há um
`33.4 VEREDITO CORRENTE — V0.4`. `IMPLEMENTATION_AUTHORIZED` é a **mesma cadeia de caracteres**. Leis: 173 → 179;
**alteradas: 0**. Os contratos `CAP-FUT` e `CAP-SCI` ganharam **uma linha cada**, que aponta para a lei nova — é a única
mexida fora da secção 38, e está declarada no veredito.

## 4. O que já existia → o que esta lei acrescenta (nada foi duplicado)

| já era lei | o que diz | o que acrescentei, e onde |
|---|---|---|
| `COL-LAW-031` / `032` | tempo e lugar têm vários sentidos | nada novo; os pontos da série levam o tempo e o lugar **da linha** (`701`) |
| `COL-LAW-201` | artefato ≠ fato; de quem é cada campo | nada novo; citado |
| `COL-LAW-202` | o claim pode preservar sujeito·predicado·objeto·tempo·lugar; `TARGET` | **+ `CLAIM_KIND`** declarado pela fonte (`702`), com a mesma regra de `TARGET` |
| `COL-LAW-203` | normalização não destrói o valor original | aplicado à série: unidade e valor originais (`701`) |
| `COL-LAW-214` | o zero tem semântica | aplicado à série: «n. 0 catture» é valor (`701`) |
| `COL-LAW-034` | identidade | aplicada à **pessoa**, com a prova em três partes (`703`) |
| `COL-LAW-043` (`FATO`) | preservar o declarado, não adivinhar | dito **para a série**, onde a tentação de resumir é maior (`701`) |
| `INT-LAW-030` / `035` / `036` | os objetos distintos; hipótese não vira facto; sinal ≠ achado | citados; os degraus da `310` não são objetos novos |
| `INT-LAW-095` | correlação ≠ causalidade, «contrato mais forte» | **o contrato** (`311`) |
| `INT-LAW-100..105` | tempo e geografia herdados | cada degrau da cadeia guarda o seu tempo (`310`); `STUDY_LOCATION/PERIOD` pedidos à Cadeia B (`315`) |
| `INT-LAW-130..136` | sinal fraco ≠ previsão ≠ facto; horizonte e incerteza | risco de modelo × clima (`312`); espécie EXPANSÃO (`314`) |
| `INT-LAW-065` / `083` | identidade ≠ expertise; a Intelligence não fabrica identidade | a pessoa da Cadeia B vem da Collection (`315` → `703`) |

**Recusadas por já terem dono (7):** «previsão não é facto» (`INT-LAW-131`), «correlação não é causalidade» (`095`),
«hipótese não vira facto por repetição» (`035`), «afiliação não é local do estudo» (`102`), «identidade não se fabrica
na Intelligence» (`083`), «tempo do facto nos boletins» (`COL-LAW-031`/`201`), «não fundir homónimos» (`COL-LAW-034`).
**D87 (acréscimo 18:25) — de quem é a descoberta de perfis:** do bot de fontes (Source Curator), guiado pelo retorno da
Intelligence; o Scrap captura e não escolhe. Escrito **dentro da `COL-LAW-703`** e na §222 como aplicação de leis que já
existiam — `COL-LAW-207`, `011`, `208`, `INT-LAW-020`, `151`, `290` (objeto `SOURCE_COLLECTION_ADVICE`) — **sem lei nova**.

A B11 (lista de núcleos italianos) ficou **no know-how**, não na lei: é registo operacional, e muda.

## 5. Provas
- `py provas/valida_biblia.py`: **11/11 PASS** — 109 leis · IMPLEMENTED 37 · **PARTIAL 49** · **ABSENT 21** ·
  NOT_APPLICABLE 2; `leis.json` regerado pelo `--build`.
- `tests/test_biblia.py` + `tests/test_integracao_biblia.py`: **87 passam** (o teste de integração passou a contar o
  bloco 7xx com 4 leis e a nomear 701..704 entre as que nunca podem desaparecer).
- Portão de contradição da Intelligence (`controle/portao_do_controle.contradicoes_da_lei`): **[]** — um só veredito
  CORRENTE, e o fecho continua a nomear a secção 32.
- Testes da Intelligence, **cada versão numa cópia própria**, base `278cd489` × ramo, um ficheiro de cada vez (a
  primeira tentativa, tudo de uma vez, foi interrompida pela máquina por falta de memória):

  | ficheiro | base | ramo |
  |---|---|---|
  | `test_biblia` · `test_integracao_biblia` | 73 · 14 passam | 73 · 14 passam |
  | `test_os_consertos_da_intelligence` (o carimbo da versão no motor) | 32 passam | 32 passam |
  | `test_o_mapa_da_intelligence_nao_mente` | 36 passam | 36 passam |
  | `test_atomicidade_da_intelligence` | **104 falham** | **as mesmas 104**, pelo nome (espelho do mapa — antigas) |
  | `test_o_controle_separa_lei_de_mencao` | 60 passam | 59 + **1 falha: `test_M5_o_ponto_fixo…`** — o carimbo do mapa ainda é o das Bíblias antigas; é exatamente o que o passo do mapa (secção 6) fecha |

## 6. O mapa
MAPA_AQUI

## 7. Limites declarados
- **Nenhuma lei nova tem implementação.** As três da Coleta nascem `ABSENT`; as seis da Intelligence dizem o que não se
  pode afirmar, não constroem nada.
- As listas oficiais fora do MUR (CNR, CREA, FEM) **não foram medidas**.
- O significado das colunas da tabela APOL continua **NAO SEI** (cabeçalho em imagem).
- O bot Luciano está fora (429): a reavaliação dele fica para quando voltar. A instalação é do coordenador.

## EM PALAVRAS SIMPLES
SIMPLES_AQUI
