# LEIA ANTES DE COLETAR

> **Este ficheiro é gerado do System Map.** Não o edite à mão: edite a peça
> em `system-map/data/architecture.declared.json` e rode
> `py system-map/scripts/generate_system_map.py`.

Toda missão de coleta começa procurando as réguas. Elas estão todas aqui,
e o caminho de cada uma é onde ela realmente vive.

---

## ANTES DE QUALQUER COISA: CONSULTE O ACERVO

O acervo de fontes é **capital parado** — consulta-se antes de coletar. Não se
coleta para descobrir o que já se sabe.

- **AS FONTES** — O capital parado da casa: 297 bases oficiais e abertas, mais 44 contas publicas do concorrente em 4 plataformas. Consulta-se antes de coletar.
  - `docs/fontes/ATLAS-DE-FONTES-EAME.md`
  - `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`
  - `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`
- **O que a ADAMA sabe de si** — O catalogo comercial e o portfolio da ADAMA lidos por dentro: o que vende em cada pais, com que rotulo, modo de acao e substancia — e onde ha lacuna.
  - `fontes/adama_catalogo_ler.py`
  - `fontes/adama_catalogo_montar.py`
  - `fontes/adama_catalogo_snapshot.py`

```bash
py candidatas/fonte_nova.py --listar     # a fila de fontes candidatas
py candidatas/fonte_nova.py --tipos      # os tipos aceites
```

**Fonte nova entra pela porta, e o que entra é candidata — nunca fonte.**
Fonte nasce quando alguém a abre, olha o que ela entrega e guarda evidência.

---

## AS RÉGUAS DA COLETA

Cada uma vale no **momento em que o dado entra**. Depois é tarde.

### As palavras que a busca digita

Os termos de busca, agrupados por cultura-problema, na lingua de quem trabalha no campo. Sao 103 palavras em dois ficheiros: 35 do censo de rotulos, todas italianas, e 68 do sensor, das quais 13 recortes de 17 sao da Italia.

*Por que existe:* Buscar 'septoria wheat' na Italia devolve literatura internacional, nao a conversa tecnica de quem esta no campo — o que se procura e 'septoriosi del frumento'. E o CROP e o ISSUE de cada item saem DESTA consulta, nunca de leitura livre do titulo, e e isso que torna a linha auditavel.  ⚠️ DIVIDIDO EM 2026-09-09: este cartao carregava tambem `regras/sensor_coleta.py`, que NAO e uma regua — e um COLETOR. Ele importa `apify_pool`, fala HTTP por `urlopen`, e e corrido pelo workflow `apify-sensores.yml`. Tres responsabilidades num cartao chamado «as palavras que a busca digita»: um coletor, uma medicao e um censo. UM CARTAO COM TRES DONOS NAO TEM DONO.

| | |
|---|---|
| estado | PENDING — o sistema importa esta lei em runtime para decidir: C-COLETA-YOUTUBE, C-RELEVANCIA.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| onde vive | `regras/rotulos_censo.py` |
| onde vive | `regras/sensor_medir.py` |

### De onde veio — carimbado na coleta

Carimba, em cada registo, de onde ele veio — no momento em que ele entra.

*Por que existe:* Sem procedencia, um numero vira verdade so porque esta escrito. E ela so vale se for posta na coleta: depois e tarde, porque o dado ja entrou sem ela e ninguem consegue recuperar a origem.

| | |
|---|---|
| estado | PENDING — o sistema importa esta lei em runtime para decidir: C-COLETA-BASE, C-COLETA-INSTAGRAM, C-ESTRADA-PDF, C-EXECUTOR-TEXTO-HTML.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| onde vive | `regras/proveniencia.py` |

### O contrato de cada fonte italiana

13 contratos executaveis: quem e, onde esta, como se acha, o que se espera de volta, como se sabe que e o documento certo — e COMO ELE FALHA.

*Por que existe:* Os testes precisaram de ver vermelho: oito documentos foram corrompidos de proposito, na memoria e nunca no disco, e os oito reprovaram. Um PDF que virou «Access denied» com HTTP 200 reprovou — porque 200 nao e prova de nada. Teste que nunca viu vermelho nao e teste.

| | |
|---|---|
| estado | PENDING — o sistema importa esta lei em runtime para decidir: C-CAPA-MATERIA, C-IT-CATALOGO, C-IT-COLETA, C-IT-INCREMENTALIDADE.  Mas 4 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| onde vive | `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md` |
| onde vive | `regras/boletim_data_local_test.mjs` |
| onde vive | `regras/contratos_de_fonte.py` |
| onde vive | `regras/identidade_do_motor_cli.mjs` |
| onde vive | `regras/italy_contract_test.mjs` |
| onde vive | `regras/italy_contracts.mjs` |
| onde vive | `regras/italy_pilot_guards.mjs` |
| onde vive | `regras/italy_scheduling_guards.mjs` |
| onde vive | `regras/italy_source_health.mjs` |
| onde vive | `regras/motor_de_rota.mjs` |
| onde vive | `regras/motor_de_rota_test.mjs` |

### Quem esta autorizado a ser coletado

A regua que decide se uma conta publica entra na coleta: identidade provada e conta local do pais.

*Por que existe:* Estar na lista nao e autorizacao. Sem esta regua, oito execucoes pagas ja foram queimadas nesta casa devolvendo o alvo errado.

| | |
|---|---|
| estado | PENDING — so peca de prova a importa. NENHUM modulo de runtime a importa (DECLARED_RULE_NOT_ENFORCED).  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| onde vive | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| onde vive | `regras/comunicacao_identidade.py` |
| onde vive | `regras/comunicacao_lote.py` |
| onde vive | `regras/comunicacao_universo.py` |

---

## COM O QUE SE VAI

- **A coorte unica da Big Collection (D25)** — Le o plano do runbook (micro_coleta.py plano), o portao, as provas do canario e o dono dos contratos do coletor, e escreve COORTE-BIG-COLLECTION-V1.json: as PRONTAS com contrato executavel + regua DETAIL/v1 + canario com prova <= 7 dias, fonte a fonte, com o sha256 dos livros lidos. Nao decide nada novo.
- **A fala vira texto, sem fatura** — Transcreve o audio dos videos na propria maquina, com whisper local. `fala_local.py` e o DONO UNICO do reconhecimento; `reel_transcricao.py` e a cadeia que liga um Reel publico ao texto falado, com RAW e DERIVED separados; os dois programas de lote chamam o mesmo dono.
- **A impressao digital do contrato que o robo vai usar (PONTE-ONBOARD)** — sha256 canonico de SOURCE_ID + OUTPUT_TYPE + ACQUISITION — exactamente o que onboardar_rotas_provadas escreve na tabela do coletor. O canario de rotas grava-o na prova (CONTRATO_SHA256, PROVADO_EM); o onboarding so escreve a linha se a impressao provada for igual a do contrato de agora e a prova tiver <= 7 dias. O supervisor chama o onboarding a cada volta (onboardar_se_mudou: so quando a prova muda ou de 10 em 10 min). mutacao.py desliga cada guarda e exige que um teste caia.
- **Abrir PDF, ODS e HTML** — Tira o texto de dentro de um PDF, de uma planilha ODS ou de uma pagina.
- **Apify — a rota paga** — Guarda e reveza as chaves de acesso das coletas pagas, e limpa qualquer mensagem de erro antes de escrever no log.
- **C9-INSTALAR-PREP — o ensaio do C9-IDIOMA sobre o vivo (relatorio da 3.a onda, antes e depois)** — ensaio_c9.sh: copia fiel do vivo (worktree no HEAD + os livros do disco), relatorio da micro-coleta com os RUN_IDs da 3.a onda ANTES (codigo da producao) e DEPOIS (C9, --estado=ONDA-WEB-ESTADO.json), Sala so lida (default_transaction_read_only), sem rede HTTP; merge --ff-only e desfazer por reset --keep.
- **Censo das lanes antes de unificar** — Mede, so a ler o git, que ficheiros cada lane mudou, quais sao iguais, quais divergem e onde o codigo entra em conflito de verdade; e as ferramentas da unificacao (missao 5): resolver o codigo, unir livros por chave e o ledger por estado, medir a suite e provar em copia descartavel; e as do ensaio do cutover (X1): medidores que mandam PARAR antes do passo seguinte, a fotografia dos livros extra e os passos 5b/5c/7b que o SWITCH_PLAN nao tinha.
- **Condutor da Big Collection (1.a onda, BC5)** — Corre a coorte congelada UMA fonte de cada vez pela porta canonica (micro_coleta.correr), fotografa a Sala antes/depois de cada fonte e aplica os disjuntores do BIG-COLLECTION-RUNBOOK §6 (egresso fora de IT, Sala a descer, >30 min, 3 FAILED seguidas, C6, proveniencia partida, pedidos acima do teto). Nao decide elegibilidade nem admissao: pergunta aos donos.
- **Disparador da onda web (2.a onda em diante) — coorte oficial conferida e teto por dominio na onda (D38)** — Corre a onda uma fonte de cada vez pela porta canonica (micro_coleta.correr). Le a coorte do lugar oficial (COORTE-BIG-COLLECTION-V1.json no commit), confere disco = commit, sha256 declarado e ESTADO=CONGELADA; nomeia um livro do teto por onda (SINTONIA_TETO_ONDA) que o transporte soma por dominio registavel; a fonte de dominio esgotado salta com TETO_DOMINIO (nao e FAILED); disjuntor por dominio + os 7 da BC5; --so-plano sem rede reparte o teto e preve os pedidos.
- **HR-6 — re-medir pelo caminho canonico as READY que o portao manda a olho humano** — remedir_hr6.py: READY + HUMAN_REVIEW_REQUIRED -> CANARY_PENDING + VALIDATE_ROUTE pela fila (so mostra; --aplicar escreve); o worker re-mede com canario.escolher_alvo (tenta o item mais fundo, volta ao 1.o se falhar). ronda_*.py e hr6-*.sh: as rondas e a copia da missao (rede so pelo portao IT, 1 fonte por dominio, D38). Nada aqui promove.
- **INTEGRA-ONDA2 — o ensaio integrado da 2.a onda e a prova do teto sobre o plano do MICRO** — ensaio_integra.sh: o ensaio integrado numa copia fiel do vivo com a rede FECHADA (clone local + livros do vivo; onboarding com a prova de rotas ja feita, plano do runbook, coorte congelada so na copia, onda_web --so-plano, plano do MICRO, prova do teto sobre os dois planos, desfazer). prova_teto_micro.py: plano do MICRO so com as fontes de um lote e a prova independente do teto (C-PROVA-TETO-DOMINIO) no pior caso de 5 pedidos por fonte PRONTA. Sem rede.
- **LEGACY-99: as READY_LEGACY de volta pela regua de hoje (ensaios e mutacao)** — revalidar_em_rondas.py: revalida READY_LEGACY numa COPIA pelo caminho canonico (ready_split.remedir -> worker), em rodadas de 1 fonte por dominio, com urlopen embrulhado (rede fechada por omissao, D41.3; teto 5 por dominio contado, D38) e o portao de consenso antes de cada rodada. video_com_o_guardado.py: as fontes YouTube pela regua VIDEO/v1 (D53) sobre as paginas /watch ja guardadas na Sala (so leitura, sha256 conferido), sem rede. mutacao*.py: cada guarda nova desligada tem de fazer cair um teste, e o mutador acusa quem escrever num livro. [onda3-pacote-v2: so A+C+D da v2; B inerte (DA-15/D67); sem a rota VIDEO]
- **O navegador — a rota gratis** — Abre a pagina publica pelo proprio navegador e le o que ela ja mostra de graca.
- **PACOTE-ONDA3 — o ensaio integrado da 3.a onda** — ensaio_onda3.sh: ensaio integrado numa worktree destacada no HEAD do vivo + os ficheiros sujos do vivo lidos na hora (para se o pacote tocar um livro no Git); D49/D51, D52, provas de rota ja feitas, onboarding, o que o robo vai medir, plano, coorte PROVISORIA da 3.a onda, onda_web --so-plano, prova do teto, desfazer a partir da foto. Sem rede.
- **Reconciliar os bytes da micro real da BC4 (so plano, pelo dono)** — Le da Sala real (so SELECT, read-only) o storage_path e o sha256 das 4 observacoes (raw_asset 1406-1409) e dos 4 derivados (909-912) da micro real da BC4, confere o sha256 dos bytes na origem e, so com --aplicar, escreve-os na raiz operacional do armazem pelo ArmazemLocal.enviar, no MESMO caminho relativo. Nenhuma linha da Sala muda.

---

## O PADRÃO, E O CHÃO QUE NÃO DESCE

```bash
py medidas/padrao_da_coleta.py
```

Dez regras medidas a cada corrida do CI. Ele **não** exige que esteja tudo
certo hoje — exige **não piorar**. Um coletor novo sem carimbo de data faz
o número subir, e o portão reprova nomeando o ficheiro.

O que todo registo de coleta tem de carregar:

| campo | por quê |
|---|---|
| `RAW_SHA256` | testemunho não é prova |
| `CAPTURED_AT` | quando eu vi |
| `FACT_TIME` | quando aconteceu — **não é o mesmo** |
| `SOURCE_LOCATION` / `FACT_LOCATION` | de onde veio o documento ≠ onde o fato é |
| `CADENCE_STATE` | sem ela, fonte morta parece fonte quieta |
| `EGRESS_IP` | por onde a requisição saiu |
| `ITEM_COUNT_RAW` → `NORMALIZED` | o que veio, e o que atravessou a régua |
| `COST_USD` | mesmo quando é zero — medido ≠ ausente |

---

## AS LEIS QUE NÃO SE QUEBRAM

- **NÃO SEI continua NÃO SEI.** Registrar desconhecido é resultado válido.
- **Ausência não é ausência no mundo.** «Não encontrámos nesta leitura»,
  nunca «não existe».
- **Lista vazia é FALHA, não zero.** A diferença entre «não há» e «não
  consegui ver» é a diferença entre um relatório e uma mentira.
- **`HTTP 200` não basta.** Há 200 com página de erro: status bom, corpo lixo.
- **Endereço errado nosso não é bloqueio da fonte.**
  `ROUTE_NOT_FOUND ≠ SOURCE_BLOCKED`.
- **Estado de porta não é veredito.**
  `ACCESS_CLASSIFICATION ≠ ANALYTIC_VERDICT`.
- **Número digitado à mão mente.** Contagem é calculada, nunca digitada.
- **Teste que nunca viu vermelho não é teste.**

---

Gerado de 4 réguas, 15 ferramentas e 2 peças de fonte declaradas no mapa.
