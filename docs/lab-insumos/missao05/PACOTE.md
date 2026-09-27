# PACOTE FACTUAL — MISSÃO-05 · IDENTIDADE ESTÁVEL DO CRUZAMENTO (SINTONIA LAB, 27/09/2026 ~18:45 BRT)

Você é um analista independente. Não leia respostas de outros analistas. Não implemente nada. Não abra rede
privada. Pode ler os arquivos locais citados abaixo (só leitura) se quiser conferir. Português do Brasil.
Marque cada afirmação como [M] medido (com arquivo:linha ou comando), [INF] inferência, [HIP] hipótese, NÃO SEI.

## 1 · O problema, nas palavras do dono (verbatim)

«e como funciona por exemplo, a informacao, cruzamento ja esta no pote, porem chega mais uma informacao da
inteligencia que faz parte daquele cruzamento especifico, como ele se junta a ele e atualiza o casco?»
«isso e prioridade arrumar agora, senao tudo vai virar uma bagunca de duplicacao»

O portal (casco) vai ao ar HOJE (D114) mostrando a saída da Intelligence (D97: o casco só mostra o que a
Intelligence produziu; a Sala de Espera aparece só como prova).

## 2 · Como o sistema funciona hoje — [M]

Fluxo: SALA DE ESPERA (Postgres; itens READY, append-only nas revisões) → INTELLIGENCE_RUN (lê uma cópia da Sala,
produz um LIVRO por corrida) → análises (piloto de cruzamento, cruzamentos_max) → POTE (1 arquivo JSON por
corrida, contrato POTE_INTELLIGENCE_CASCO/v2, 12 compartimentos, um por ferramenta do portal) → CASCO lê o pote
inteiro e desenha.

- Pote = 1 foto por corrida; `INTELLIGENCE_RUN_ID` obrigatório no topo
  (`pacote/pote_intelligence_casco.py` @ branch claude/pote-v2-unico-contract-y8o1pi, l.40, l.566-568, l.721-726).
  Dentro de uma corrida o pote recusa OBJETO_ID repetido no mesmo compartimento («DUPLICADO_NO_COMPARTIMENTO»,
  mesmo arquivo l.467). Entre corridas não há nada: nenhum campo de «corrida anterior», nenhum DELTA.
- O casco (`italia-portale/client/sintonia-pote-casco.js`, branch claude/casco-r7-publication-yb7nsg, l.1-17) troca
  o pote inteiro; não compara com o anterior; não tem «novo/atualizado/saiu».
- Schema do objeto no pote (POTE_INTELLIGENCE_CASCO-v2.schema.json): obrigatórios OBJETO_ID, ESPECIE, CHAVES,
  PORQUE, CONTRADIZ, INCERTEZA, RESULTADO, PROVA[≥1] (ITEM_ID→RAW_OBSERVATION_ID→SOURCE_ID→DOCUMENT_ID, URL,
  PUBLISHED_AT, FACT_TIME…). `additionalProperties` não declarado (= aceita campos extra). O gerador copia chaves
  fora do contrato do compartimento para `FORA_DO_CONTRATO{nome: valor}` (l.399-403). Campos de topo extras NÃO
  são copiados pelo gerador (o topo é montado por `_cabecalho` + campos fixos).

### Como os IDs nascem hoje — [M]
| objeto | fórmula | arquivo:linha |
|---|---|---|
| SIGNAL | `"SG-"+sha256(run_id + ITEM_ID + RAW_OBSERVATION_ID + len(SIGNALS))[:16]` (entra o run_id E a posição) | motor/corrida_da_inteligencia.py:641-644 (lote6 21cc06c0) |
| FATO FUTURO | `"FUT-"+sha256(RUN + ITEM_ID + CORRIDA_UPSTREAM)[:16]` | …/PARA-O-CASCO-R7/montar_entrada_r7.py:99 |
| CROSSING piloto | `"XC-<source_id>-<ordem>-<substancia[:12]>"` (+ «@<run_id da coleta>» na R7) | provas/o_piloto_da_sala.py:350 @2b4e095f; analise_r7.py:171 |
| CROSSING max | `"XMAX-"+sha256("|".join(partes))[:16]` com partes = OBJETO_ID do piloto + REGISTRATION_ID, ou ("PM", SALA_CHAVE, cultura, praga, reg), ou ("CS", origem, reg) | motor/cruzamentos_max.py:964-1042 (branch claude/cruzamentos-max-sguy1x) |
| RENDIMENTO | `"REND-<source_id>-<run[-8:]>"` | montar_entrada_r7.py:139 |

### Medições desta missão — [M]
1. POTE-R6 (IR-ec52d01c…) × POTE-R7 (IR-e09acab6…): 47 e 47 objetos; **OBJETO_ID iguais = 0**; objetos com o
   MESMO conteúdo (compartimento + espécie + ITEM_IDs da prova) = **43, todos com ID diferente**. Ex.: windows,
   SINAL do item derived:11 → R6 `SG-bd9e632048e29455`, R7 `SG-88e86b69caf55bea`.
2. Os 3 cruzamentos da R6 (`XC-IT-T3-008-0-TAUFLUVALINA` ×2, `XC-IT-T3-010-0-AZOXYSTROBIN`) **não existem com o
   mesmo ID na R7** (0/3): a R7 acrescentou o sufixo «@<run da coleta>».
3. R7 = 86 cruzamentos, pergunta única «o rótulo ADAMA lido autoriza a substância citada na cultura do boletim?»;
   86 pares (substância, documento) distintos, sobre 15 itens/documentos e 30 substâncias. Estados:
   PARTIAL_GRAO_INCOMPATIVEL 48 · POSSIBLE_ANSWER_NO 29 · YES_A_CONFIRMAR 5 · NOT_POSSIBLE 4. Depois de
   cruzamentos_max: PARTIAL 48 · UNRESOLVED 24 · NO 7 · CONFIRMED_YES 3 · NOT_POSSIBLE 4.
   Só 5/86 têm a cultura LIGADA à substância no texto (cabeçalho de boletim de uma cultura); nos outros a cultura é a
   lista do DOCUMENTO (ENTITY_SOURCE = DOCUMENT, «NAO SEI por entidade»).
4. Duplicata real hoje: FOLPET × vite aparece em 2 cruzamentos (CAND-1221 Arezzo → UNRESOLVED; CAND-1228 Cantina
   Negrar 12/05 → CONFIRMED_YES). A pergunta «o rótulo ADAMA cobre folpet em vite?» é UMA; o casco mostra 2 cartões
   com estados diferentes.
5. PORTFOLIO_MATCH (cruzamentos_max): 14 objetos; **13 são a MESMA pergunta** OLIVO × MOSCA_OLIVO, estado
   SEM_PAR_LIDO, um por boletim (APOL, ARIF n.37, ARIF n.38, Campania 2×, Siena, …). 13 cartões para 1 resposta.
6. COMPETITIVE_SET: 125 objetos vindos de 2 itens de origem; 122 PRODUCT_ID distintos.
7. Sala (cópia R7, 242 itens): `raw_document_key` ausente em 38; 13 documentos aparecem 2× (ex.:
   «CAMPANIA:SA:16-09-2026» em dois run_id de coleta, mesmo raw_sha256) — o mesmo boletim entrou duas vezes.
8. ARIF: boletim n.37 (cabeçalho «09 - 15 settembre 2026») e n.38 (cabeçalho «16 - 22 settembre 2026», mas
   FACT_TIME gravado «2026-09-07/2026-09-13», base «RELATIVA_A_PUBLICACAO») — a janela do fato não é o período do
   cabeçalho em todos os casos; mesma instituição, semanas consecutivas.

## 3 · Lei e decisões que já valem — [M]

Bíblia da Intelligence V0.4 (`BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`, lote6 21cc06c0, 2535 linhas):
- INT-LAW-030 (l.256) não comprimir SIGNAL/CROSSING/FINDING/OPPORTUNITY; INT-LAW-031 (l.278) claim consumida
  precisa identidade estável, mas a Intelligence não fabrica identidade da Collection; INT-LAW-037 (l.304) crossing
  = relação provada com chaves; INT-LAW-039 (l.322) identidade/estado da Opportunity independem da UI.
- INT-LAW-042 (l.351) participar do mesmo run não cria aresta; INT-LAW-045 (l.371) lineage permite impact analysis;
  INT-LAW-050/051 (l.379-385) run tem identidade; INT-LAW-054 (l.411) «parece a mesma pergunta» não é cache key.
- INT-LAW-071..078 (l.476-526) mesmo originador não vira N fontes; mesma redação em N territórios = N aplicações,
  1 instituição; INT-LAW-079 (l.528) divergência ≠ contradição; mudança de recomendação no tempo = TEMPORAL_CHANGE.
- INT-LAW-081..084 (l.549-571) similaridade não prova equivalência; conceito canônico ≠ termo local; conflito de
  normalização fica conflito. INT-LAW-091 (l.579) chave faltando ⇒ NOT_POSSIBLE/UNKNOWN/PARTIAL.
- INT-LAW-092 (l.587) contar EXTERNAL_SIGNAL_COUNT, INDEPENDENT_SOURCE_COUNT, STRUCTURAL_VALIDATION_COUNT separados.
- INT-LAW-100 (l.612) SOURCE_LOCATION ≠ FACT_LOCATION; FACT_TIME ≠ PUBLICATION_TIME ≠ OBSERVED ≠ COLLECTED.
- INT-LAW-125 (l.729) mudança de judgment registra PREVIOUS/NEW/WHAT_CHANGED/WHY/NEW_EVIDENCE.
- INT-LAW-210..213 (l.1003-1015) histórico append-only; ACTIVE_STATE muda sem apagar HISTORICAL_STATE; correção
  registra causa; outcome posterior não reescreve julgamento passado. INT-LAW-220 (l.1025) new data ≠ new logic;
  INT-LAW-224 (l.1037) mudança semântica exige migration explícita.
- CAP-OPP JOIN_KEYS CROP_ID×ISSUE_ID×REGION_ID×TIME_WINDOW (l.1741); CAP-PORT PRODUCT_ID×CROP_ID×TARGET_ID×
  REGISTRATION_VERSION×GEO (l.1767); CAP-FUT ISSUE_ID×GEO×HORIZON_WINDOW (l.1790); CAP-LABEL (l.1819); CAP-WIN
  CROP×REGION×PHENOLOGY×TIME_WINDOW (l.1850).
- **Não existe regra de identidade estável de cruzamento ENTRE corridas.** (grep por CROSSING_ID/episódio/upsert/
  bitemporal: 0 ocorrências normativas.)

Decisões do dono: D97 casco só mostra saída da Intelligence · D104.1 sem banco paralelo (uma verdade canônica, dentro
do Postgres existente) · D104.3 vocabulário agrícola canônico (aliases, códigos externos, nome original nunca apagado)
· D111/D112 lugar só do texto; procedência por entidade; NÃO SEI; 3 distritos com o mesmo texto = 3 aplicações, 1
instituição; «tratar→não tratar» = mudança temporal; previsão ≠ fato; 4-5% × 10-15% = DIVERGENT, contradição
UNRESOLVED · D116 bulas/portfolio = biblioteca de referência VERSIONADA; consulta obrigatória em cruzamento que afirma
autorização; nova coleta oficial = nova versão · D117 frescor: 14 dias sem checagem ⇒ «pode estar desatualizado», 30 ⇒
autorização «a confirmar» · Sala append-only (`sala_de_espera_revisao`, trigger recusa UPDATE/DELETE,
supabase/migrations/033:222-243) · D119: até a conclusão, nenhuma equipe cria novo esquema de ID; novos cruzamentos
no pote de hoje levam marca de ID provisório.

## 4 · Normalização que já existe — [M]
- `leis/boletim_do_campo.py:90-111` MESMO_PROBLEMA: lista declarada (ex.: «mosca dell'olivo | mosca delle olive |
  bactrocera oleae» → «mosca dell'olivo»); «não é EPPO».
- `motor/cruzamentos_max.py:68-150` CULTURAS_ROTULO / ALVOS_CANON (regex; chaves de GRUPO como CUCURBITACEE,
  MELO=«melo|meli|pomacee», FRUMENTO; cópia guardada por teste do leitor de rótulos); `chave_substancia`
  (TAU-FLUVALINATE = TAUFLUVALINATE; METALAXYL ≠ METALAXYL-M).
- `motor/normalize_agro.py` (EPPO via dicionário ES + EPPO GD, multipaís), `motor/normalize_substance.py` (CAS,
  nome, morfologia FR↔EN, sal).
- `leis/fato_local.py:174-200` comune só pela lista oficial ISTAT declarada (arquivo ausente hoje ⇒ nenhum comune).
- IAB canário Puglia (LAB): 26 entidades com IDs tipo PEST:DACUOL (EPPO:DACUOL), CROP:OLVEU, PLACE:PROV-LE,
  ZONE(DEFINIDA_PELA_FONTE) «Comprensorio LE - Pianura Salentina Sud»; aliases com estado VERIFICADO/AMBIGUO
  («mosca» sozinho = AMBIGUO).

## 5 · Proposta preliminar do coordenador (para CONFRONTAR, não aceitar)
(1) ID do cruzamento pela PERGUNTA (família + chaves canônicas: cultura, alvo, lugar resolvido, janela, produto+edição),
não pela origem; (2) provas acumulam (append), com contagem de fontes INDEPENDENTES; (3) estado muda com histórico
(de→para, quando, qual prova); (4) Opportunity/Future apontam por ID e são reavaliados; (5) pote traz DELTA desde a
corrida anterior (entrou/fortaleceu/mudou de estado/saiu) e o casco mostra «atualizado»; (6) só a Intelligence escreve.

## 6 · Restrições
Não criar banco separado nem segundo sistema (D104.1). Casco não calcula (INT-LAW-023/280). Intelligence não fabrica
identidade da Collection (INT-LAW-031/083). Portal vai ao ar hoje. Custo: soluções simples preferidas.

## 7 · PERGUNTAS
P1 CHAVE: que campos formam a identidade de cada família de cruzamento (rótulo×substância citada; portfolio_match
cultura×praga; competitive_set; janela olivo×mosca; futuro)? Como tratar granularidade (comune/província/região/
«zona costeira» não resolvida; dia/semana/validade do boletim/estação; cultura genérica «drupacee» × específica;
praga com 5 nomes) sem juntar coisas diferentes nem separar iguais? O que acontece quando a chave tem NÃO SEI?
P2 TEMPO: cruzamento de setembro e de outubro — o mesmo ou outro? «episódio» × «série»?
P3 PROVA: modelo append-only; independência (3 distritos = 1 instituição; notícia replicada = 1); contradição aberta;
mudança temporal de recomendação.
P4 ESTADOS: máquina de estados honesta e transições; gatilhos de reavaliação (prova nova, nova edição da bula, expiração
por frescor D117, correção na Sala); histórico imutável.
P5 COMPOSIÇÃO: Finding/Opportunity/Future referenciam por ID; o que acontece quando um cruzamento muda; ciclos e dupla
contagem.
P6 POTE/CASCO: manter «1 pote por corrida» + LIVRO de identidades persistente? Onde vive o livro (tabela append-only no
Postgres da Sala? arquivo versionado? DELTA dentro do pote?) Formato mínimo do DELTA sem quebrar o contrato v2.
P7 MIGRAÇÃO dos IDs atuais (XC-, XMAX-, SG-, FUT-).
P8 O que fazer ANTES de publicar o portal hoje para não nascer duplicado (mínimo, reversível).
Termine com: RECOMENDAÇÃO EM 10 LINHAS e ONDE POSSO ESTAR ERRADO (3-5 itens).
