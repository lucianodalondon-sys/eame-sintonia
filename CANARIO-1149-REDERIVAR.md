# CANARIO-1149-REDERIVAR — o mesmo RAW 2272, re-derivado numa cópia, até a Sala

MISSÃO `nuvem-canario-1149-rederivar-v1` · 28/09/2026 (D131/D132) · ramo `claude/canario-1149-rederivar-ial9hh`,
filho de `origin/claude/derivacao-estrutura-v2-d76w9o @ 620d1b19b` · **nada fundido; produção, Sala real, coleta e
VPN intocadas.** Lido antes: `origin/nuvem/canario-1149-v1:docs/lab-insumos/canario-1149/`
(`CANARIO_1149_MAPA_DE_RESPONSABILIDADE.md`, `resp-scrap-1149-derivacao.txt`, `RAW-2272.html`, `LINHA-DA-SALA.json`).

---

## ESTADO

| | |
|---|---|
| Runner | `provas/canario_1149/rederivar_um_raw.py` — **pronto e provado numa cópia de teste** (Postgres 16 descartável, migrations pela cadeia, RAW 2272 real byte a byte). **Não corrido na cópia do coordenador** (127.0.0.1:54391 não está na nuvem). |
| Estrada | página original → derivação v4 → comparação → o mesmo item → **Sala: FUNDIDO POR DOCUMENTO** (0 linhas novas, versão 036 = `IGUAL` «bytes do RAW iguais»). |
| Achado | **«texto derivado novo do mesmo RAW» não tem caminho canónico até a linha da Sala → `DONO = NAO DEFINIDO`.** A estrada PARA na Sala; Intelligence → pote → Casco continuam a ler o texto achatado. Sem atalho. |
| Admissão (efeito) | `provas/canario_1149/admissao_antes_depois.py`. Árvore (216 páginas, 214 julgadas): **0 decisões mudam**. Armazém (628): **não corrido aqui** — é do coordenador. |
| Testes | `tests/test_canario_1149_rederivar.py`: **13/13** com Postgres; sem ele 8 correm e 5 saltam dizendo porquê. |
| Mutação | **8/8 travas mortas** (porta do vivo, porta implícita, morada remota, sem marca, marca vazia, sem `--aplicar` escreve, armazém da cópia dentro do original, 2.ª linha do mesmo bruto). |
| System Map | regerado pela cadeia, **VALIDAR PASS**; `C-PROVA-ROTA-DO-HTML` reivindica `provas/canario_1149/*.py`. `test_system_map`: 10 reprovações **pré-existentes** (a base tem 11). Ver §6. |
| Fora | `limpar()`, `executor_texto_de_html`, `admissao/`, `sala_de_espera`, `fato_do_texto`, ontologia — **não tocados**. Nenhuma heurística de DATA_DO_FATO em lado nenhum. |

---

## O QUE O RUNNER FAZ — e o que ele só chama

```
py provas/canario_1149/rederivar_um_raw.py --dsn <copia> --raw-id 2272 --armazem <raiz> --saida <pasta>
        [--aplicar] [--armazem-da-copia <pasta>] [--universo T5] [--livros "<glob;glob>"]
```

Ele não deriva, não julga e não pousa. Chama, **pela ordem da coleta real** (`orquestrador.correr`, que é quem
produziu o `derived:1149` — `scripts/micro_coleta/micro_coleta.py:18`):

| etapa | dono chamado |
|---|---|
| unidade a partir da linha REAL de `raw_asset` | `coleta/ingresso.unidades_para_a_derivacao` |
| recado de tempo e lugar da observação | `coleta/italy_executor.tempo_e_lugar` (com o livro do coletor, se `--livros`) |
| DERIVED | `coleta/derivacao_forward.correr` → `ingresso.executor_para` → `executor_texto_de_html.derivar_um` (limpar/3, v4) → `guarda/preservar_derivado` |
| STRUCTURED | `orquestrador.pela_estruturacao` → `guarda/preservar_documento` |
| ADMISSION | `orquestrador.item_documental_para_a_porta` → `admissao.decidir` |
| READY | `admissao.pronto_para_inteligencia` → `sala_de_espera.pousar(armazem=…, extratores=coleta.extratores_de_texto.registo())` |
| corrida de reprocesso | `coleta/coleta_checkpoint.abrir_corrida` / `fechar_corrida` — `platform=REPROCESSO`, `mission=REPROCESSO_CANARIO_1149`, `capture_method=SEM_REDE…`, run_id `REPROCESSO_CANARIO_1149-<utc>-<hex>` |

**Corrida de reprocesso: o contrato permite.** `coleta_checkpoint.abrir_corrida` regista uma execução cunhada pelo
chamador («Registar não é cunhar»), e o orquestrador já tem o conceito («REPROCESSAR NAO E COLHER … a corrida nova
continua a ser nova», `orquestrador.py:1081-1092`). Não parei aqui.

**Duas divergências do pedido, declaradas:**

1. **Não uso `rota_forward_documento.levar_a_espera()`.** Ela monta o READY com o tradutor da rota M2
   (`rota_forward_documento.item_para_a_porta`, que **não lê o fato do texto**); o 1149 veio pela rota documental do
   orquestrador (`item_documental_para_a_porta`, que lê). Pousar por ela daria um READY diferente do item que a porta
   julgou — o contrário de «O QUE A PORTA JULGOU E O QUE TEM DE POUSAR». Uso os **mesmos três donos** que ela chama
   (`decidir` · `pronto_para_inteligencia` · `pousar` com armazém e extratores, como `test_quem_pousa_entrega_o_armazem`
   exige), com o item certo.
2. **Não uso `orquestrador.pela_porta()` inteira**: ela escreve o livro de decisões em
   `data/samples/LIVRO-DE-DECISOES.json` **da árvore** (caminho fixo, `admissao.py:79`) — escrita fora da cópia. A
   decisão vai para `<saida>/DECISAO-<run>.json`. Consequência: não há passagem `ADMISSION`/`READY` no rastro — o
   mesmo que a rota do orquestrador faz hoje (ela também não as emite). `DERIVED` é emitida por `derivacao_forward`.

**A trava** (antes de abrir ligação): morada local sem desvio (os donos `guarda/banco_descartavel` ou
`guarda/banco_operacional` dizem sim) · porta **escrita** e ∉ {5432, 54330 = a Sala real} · e, já ligada, a
**marca de cópia** `public._copia_descartavel` com ≥ 1 linha. O runner **nunca** cria a marca. As variáveis que ligariam
um dono a outro banco (`SUPABASE_DB_URL`, `SINTONIA_COLLECTION_DSN`, `BANCO_DESCARTAVEL_URL`, `PG*`) saem do processo.
Rede: `socket.socket` vira armadilha durante a corrida.

**Sem `--aplicar`**: só `select` e cálculos puros. **Com `--aplicar`**: escreve só na cópia e no armazém da cópia (o RAW
copiado com sha256 batido + o derivado novo); o `--armazem` original é **lido** (um ficheiro).

**A trava contra duplicar:** se o RAW não tiver identidade provada (`FORWARD_IDENTIFIED`) e já houver linha dele no
universo, a DEDUP-DOC não funde e `pousar` gravaria **uma 2.ª linha do MESMO bruto** (item_id novo). O runner PARA
antes de chamar `pousar` e diz `DONO_DO_CAMINHO = NAO DEFINIDO`.

---

## EVIDÊNCIA

Tudo abaixo correu nesta nuvem, contra **Postgres 16 real** (`ensaio_offline.Base`: `initdb` numa porta livre,
`create database sala_italia`, `motor/cadeia_canonica.sh migrations`), semeado com: o RAW 2272 **real**
(`tests/fixtures/canario_1149/RAW-2272.html`, `sha256 f2158520f2362956756e31864406962e68ce6632206a4ce56e078e826a953d01`,
82 925 bytes — o mesmo do `origin/nuvem/canario-1149-v1`), `identity_state = FORWARD_IDENTIFIED`, um derivado antigo
achatado (`limpar/1`, a cópia literal conferida do `replay_acervo.py`, receita «texto-de-html 2») e a linha da Sala
pousada **pelo dono** (`pousar`) com o item da rota documental. **Os ids (derived:1, derived:2) são da cópia de teste,
não os do vivo.**

### 1 · Sem `--aplicar` (previsão) — nada escrito

```
$ py provas/canario_1149/rederivar_um_raw.py --dsn <copia 127.0.0.1:<livre>/sala_italia> --raw-id 2272 \
      --armazem <armazem-original> --saida <saida> --armazem-da-copia <saida>/armazem-da-copia
codigo: 0
ESTADO   SO_PREVISAO (sem --aplicar nao se escreve nada)
ESCREVEU {collection_run: 0, raw_asset: 0, storage_object: 0, derived_artifact: 0, documento_estruturado: 0,
          etapa_da_corrida: 0, sala_de_espera: 0, sala_de_espera_versao: 0, sala_de_espera_revisao: 0}
DERIVACAO_PREVISTA  texto-de-html 4 · parameters_hash bb811cae3e7cf429… · REGUA limpar/3 ·
                    sha256 fbc360bdbba3e52a… · parent_sha256 f2158520… · NA_COPIA NAO_EXISTE (seria INSERTED)
SALA_PREVISTA       IDENTIDADE_DO_RAW FORWARD_IDENTIFIED · LINHAS_DESTE_DOCUMENTO_NO_UNIVERSO 1 ·
                    DEDUP_DOC «funde: o documento ja esta no universo T5 … a linha nova NAO entra» ·
                    VERSAO_036 {ESTADO: IGUAL, MOTIVO: «bytes do RAW iguais»}
```
O teste `test_2` prova o «nada escrito» por **md5 do conteúdo** das 9 tabelas, não só pela contagem, e que o armazém
original não mudou.

### 2 · Com `--aplicar`

```
$ py provas/canario_1149/rederivar_um_raw.py … --aplicar
codigo: 0 · ESTADO APLICADO_NA_COPIA
CORRIDA        REPROCESSO_CANARIO_1149-20260928T185131Z-4b60d1ff (coleta_checkpoint.abrir_corrida;
               platform REPROCESSO; mission REPROCESSO_CANARIO_1149) -> fechada `concluida`
DERIVADO_NOVO  PORTA PASSED · ESTADO INSERTED · executor texto-de-html · derived:2 · producer_version 4 ·
               sha256 fbc360bdbba3e52acc80db512d9b9db651d9acaf792e9f05fd522e006538a081 ·
               pai raw_asset 2272 · parent_sha256 f2158520… · parameters_hash bb811cae… · rastro DERIVED PASS
ESTRUTURADO    guarda/preservar_documento.py · INSERTED
ESCREVEU       collection_run +1 · derived_artifact +1 · documento_estruturado +1 · etapa_da_corrida +1 ·
               raw_asset 0 · storage_object 0 · sala_de_espera 0 · sala_de_espera_versao 0 · sala_de_espera_revisao 0
```

**Texto** — antes (a linha da Sala): **1 linha**, 8 988 caracteres, `corpo()` **0**. Depois: **82 linhas**, 8 988
caracteres, `corpo()` **7 705** (o mesmo número que o Scrap Engineer mediu). As 40 primeiras linhas:

```
Xylella fastidiosa: dalla ricerca CREA nuove strategie per l’olivicoltura - Xylella fastidiosa: dalla ricerca CREA nuove strategie per l’olivicoltura - CREA
Xylella fastidiosa: dalla ricerca CREA nuove strategie per l’olivicoltura - Xylella fastidiosa: dalla ricerca CREA nuove strategie per l’olivicoltura
Ministero dell'agricoltura, della sovranità alimentare e delle foreste
Amministrazione Trasparente
Selettore lingua
IT
EN
rss_feed
Seguici su -->
Barra di ricerca
Menù di navigazione
Il CREA keyboard_arrow_down
Conosci il CREA Organi Direzione Generale Direzione Tecnico Scientifica Direzione Coordinamento Amministrativo dei Centri di Ricerca (DiCAR) Direzione Coordinamento Risorse Umane e Finanziarie (DiRIS)
Organigramma Amministrazione Documento di Visione Strategica Piano Triennale di Attività La nostra storia La storia della sede centrale Carta Europea dei Ricercatori
CUG - Comitato Unico di Garanzia URP - Ufficio relazioni con il Pubblico Contatti
Centri di ricerca keyboard_arrow_down
Agricoltura e Ambiente Alimenti e Nutrizione Cerealicoltura e Colture Industriali Difesa e Certificazione Foreste e Legno Genomica e Bioinformatica
Ingegneria e Trasformazioni Agroalimentari Olivicoltura, Frutticoltura e Agrumicoltura Orticoltura e Florovivaismo Politiche e Bioeconomia Viticoltura ed Enologia Zootecnia e Acquacoltura
VAI ALLA SEZIONE
Cosa fa il CREA keyboard_arrow_down
Le grandi sfide del CREA Attività istituzionali e di servizio Relazioni istituzionali e internazionali Contratti di filiera e di distretto Schede tecniche Open Access
Banche Dati Biblioteche Osservatorio Innovazione Ricerca Sviluppo Riviste del CREA
Gare e Concorsi keyboard_arrow_down
Bandi di gara e contratti
Bandi di concorso
Media & Eventi keyboard_arrow_down
Notizie Comunicati Stampa Rassegna Stampa Ufficio Stampa e Comunicazione
Eventi CREAFuturo CREA Tube Media kit
Richiesta logo e patrocinio
Personale keyboard_arrow_down
Profilo ricercatore
Aggregatore Risorse
COMUNICATO STAMPA
remove
22 giu 2026
Xylella fastidiosa: dalla ricerca CREA nuove strategie per l’olivicoltura
Presentati i primi risultati dei progetti finanziati dal MASAF per contrastare la diffusione del batterio e sostenere la rigenerazione dei territori colpiti
Condividi
share
Dalla diagnosi precoce alle nuove varietà di olivo più resilienti, passando per il controllo sostenibile degli insetti vettori: la ricerca sta costruendo una nuova cassetta degli attrezzi per affrontare la sfida di Xylella fastidiosa. È questo il quadro emerso dall’incontro “Analisi e prospettive della ricerca su Xylella fastidiosa nei progetti finanziati dal Masaf” , ospitato dal CIHEAM Bari, che ha riunito istituzioni, ricercatori e rappresentanti del mondo produttivo per fare il punto sugli avanzamenti scientifici in atto, ricordando i risultati finali attesi ed evidenziando le possibili ricadute operative sul territorio.
```

**Publicação** — `PUBLISHED_AT = 2026-06-22` · `BASE = DIV.content-date (irmão de content-category)` · `PRECISAO = DIA`
(antes: `NAO SEI`). Veio do leitor da página (`executor_texto_de_html.tempo_de_publicacao`) pelo recado de
`italy_executor.tempo_e_lugar` — **o runner não o calcula**.

**Admissão, universo T5** (o da linha que já está na Sala = o do pedido):

```
RESULTADO SIM · REGRA «pertence ao universo» · VERSAO_DA_REGUA 10
MOTIVO    «fala de ricerca, tesi — que e do que «T5» trata»
PALAVRAS  [ricerca, tesi]
A_REGUA   PERGUNTAS_DO_UNIVERSO[T5] (22 termos, «tesi» incluído) · PALAVRA_INTEIRA False (substring) · SINAIS_MINIMOS 2
          dono admissao/admissao.py::_do_universo
ANTES (texto achatado): SIM · [ricerca, tesi]   ← a mesma decisão, as mesmas palavras
```

**Sala:**

```
RECIBO   ESTADO REUSED · INSERIDAS 0 · JA_NA_SALA_POR_OUTRA_CORRIDA 1 ·
         VERSOES [{ESTADO: IGUAL, MOTIVO: «bytes do RAW iguais», DOCUMENTO: IT-T5-2026-09-28-112058-…#0,
                   ITEM_ID: derived:2, ANTERIOR: derived:1}] · BACKEND POSTGRES · CANONICO true
VEREDITO FUNDIDO_POR_DOCUMENTO: a versao nova do mesmo documento NAO ganha 2.a linha
         (declarado em admissao/sala_de_espera.py, DEDUP-DOC)
PROVA    linhas do documento no universo: 1 antes, 1 depois · versões 036: [] antes, [] depois ·
         linha da corrida nova: nenhuma
DONO_DO_CAMINHO_PARA_TEXTO_NOVO  NAO DEFINIDO
```

**Os campos, como a peça dona os deu** (READY montado, não pousado; nenhum mexido):

| campo | valor | base / porquê |
|---|---|---|
| FACT_TIME | NAO SEI | «nenhuma data explícita do texto ligada ao acontecimento … a data de publicação sozinha nunca preenche este campo» (`leis/fato_do_texto`) — **certo**: a data do encontro no CIHEAM não está escrita |
| FACT_LOCATION | NAO SEI | «nenhum lugar ligado a um acontecimento … (só mencionados: Bari)» — antes: «o texto não tem corpo (só menu/rodapé)» |
| PROBLEMA | NAO SEI | «D112: o item nomeia 2 problemas distintos (xylella, nematode)» — elo 5, ontologia (não tocado) |
| CULTURA | [olivo, vite] | `estudo-chaves-v1` (igual ao antes) |

### 3 · Testes

```
$ runuser -u postgres -- python3 -B -m unittest tests.test_canario_1149_rederivar      (Postgres 16 real)
Ran 13 tests in 8.370s
OK
$ python3 -B -m unittest tests.test_canario_1149_rederivar                               (root: o postgres recusa)
Ran 12 tests … OK (skipped=5)   ← a classe com banco salta e diz porquê
```
(O `root` desta nuvem não pode correr `initdb`; os binários do Postgres 16 foram postos em `~/orca/pgtmp/pgsql/bin` do
utilizador `postgres` — o sítio que `ensaio_offline.PG_BIN` já procura. Nada disso vai no ramo.)

| teste | o que prova |
|---|---|
| `test_o_vivo_e_recusado_pela_morada` | 5432, 54330, sem porta, host remoto, banco `postgres`, `?host=`, `?dbname=` → recusados |
| `test_mutacao_apontado_ao_vivo_recusa_sem_ligar` | `main()` com o DSN do vivo sai **2** e o `psql` **nunca** é chamado; nada na saída |
| `test_o_armazem_da_copia_nao_pode_morar_no_original` | sai 2 sem ligar |
| `test_1_sem_marca…` / `test_1b_marca…vazia` | sai 2; md5 das 9 tabelas igual |
| `test_2_sem_aplicar_nao_escreve_nada` | md5 igual; armazém original igual; armazém da cópia não nasce |
| `test_3_aplicar…` | derivado v4, pai 2272, sha do byte guardado; PUBLISHED_AT 2026-06-22 DIA; FACT_TIME ≠ publicação; T5 SIM; Sala REUSED/0 inseridas/036 IGUAL/NAO DEFINIDO; `collection_run` REPROCESSO_CANARIO_1149 concluida; original só lido |
| `test_4_aplicar_outra_vez_reaproveita` | REUSED, `derived_artifact` não cresce |
| `test_5_raw_sem_identidade_provada…` | sai 3, `SALA NAO_CHAMADA`, `sala_de_espera` não cresce, corrida `parcial` |
| `OEfeitoNaAdmissao` (3) | RAW 2272 SIM→SIM em T5 (com «tesi»); página-mutante com «prova di campo» partido por `<li>` → SIM→NAO_SEI apanhado; página sem contrato não é julgada |

### 4 · Mutação (cada trava desligada à mão, bateria corrida, ficheiro reposto — sha256 `e8f48a07…` antes e depois)

```
M1 porta do vivo aceita            -> MORTO  test_o_vivo_e_recusado_pela_morada
M2 porta implicita aceita          -> MORTO  test_o_vivo_e_recusado_pela_morada
M3 sem marca aceita                -> MORTO  test_1_sem_marca_de_copia_recusa
M4 marca vazia aceita              -> SOBREVIVEU  → acrescentei test_1b → MORTO
M5 sem trava de duplicar           -> MORTO  test_5_raw_sem_identidade_provada_para_antes_de_duplicar
M6 armazem da copia no original    -> MORTO  test_o_armazem_da_copia_nao_pode_morar_no_original
M7 sem --aplicar escreve           -> MORTO  test_2 + test_3
M8 morada remota aceita            -> MORTO  test_o_vivo_e_recusado_pela_morada
```

### 5 · Efeito na admissão — `admissao_antes_depois.py`

```
$ python3 -B provas/canario_1149/admissao_antes_depois.py --armazem data/collection-store --saida <pasta> --qualquer-html
ANTES   limpar/1 — copia literal em provas/derivacao_estrutura/replay_acervo.py @ e24139702 (COPIA_LITERAL_CONFERIDA=SIM)
DEPOIS  limpar/3
PERGUNTA admissao._do_universo (so a pertenca ao universo; versao da regua 10)
UNIVERSO TERRITORY do contrato (curadoria/italy_contracts_curator.json)
PAGINAS 216 · JULGADAS 214 · NAO_JULGADAS 2
TRANSICOES {NAO -> NAO: 74, NAO_SEI -> NAO_SEI: 101, SIM -> SIM: 39}
MUDARAM 0 · SIM_PARA_OUTRA 0 · OUTRA_PARA_SIM 0 · SO_AS_PALAVRAS_MUDARAM 0
```

**Porque é de esperar pouco, e onde pode morder:** `_do_universo` casa por substring (ou palavra inteira em T1/T2) no
texto inteiro, e `_dobrar` **não normaliza brancos**. Trocar espaço por quebra de linha não mexe em termos de UMA
palavra; só pode **tirar** um termo de VÁRIAS palavras que atravesse uma fronteira de bloco («prova di campo»,
«prove sperimentali» partidos por `<li>`/`<p>`). O teste-mutante prova que o script apanha exatamente isso. Nas 216 da
árvore não acontece. **No armazém (628) não sei** — o coordenador corre:

```
py provas\canario_1149\admissao_antes_depois.py --armazem C:\Users\London1\sintonia-sala-italia\armazem --saida C:\tmp\c1149-adm
   [--livros "<caminho>\**\observations.ndjson"]   ← fonte pelo RAW_SHA256; sem isto, pela pasta que for contrato
```

### 6 · System Map

```
$ python3 system-map/scripts/correr_a_cadeia.py REGERAR
  frescura   CURRENT · a arvore e as entradas sao as que foram medidas
CADEIA=OK · REGERAR
$ python3 system-map/scripts/correr_a_cadeia.py VALIDAR
  SYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio
CADEIA=OK · VALIDAR
$ python3 system-map/tests/test_system_map.py
TESTES_SYSTEM_MAP=FAIL · 10 reprovada(s): nenhuma_regua_ficou_por_decidir, regua_que_carimba_nao_e_regua_que_mede,
  as_regras_que_nao_carimbam_estao_contadas, E2_receita_continua_com_um_consumidor, nao_sei_sobrevive_no_acervo,
  tem_autor_LIVRO-DE-DECISOES, cada_familia_ocupa_um_bloco_contiguo, a_governanca_fica_fora_da_esteira,
  a_esteira_le_se_da_esquerda_para_a_direita, a_esteira_acaba_no_ready
```
**As 10 são pré-existentes:** na base `620d1b19` (worktree limpo, sem nada deste ramo) o mesmo comando dá **11**
reprovações — estas 10 + `scanner_e_deterministico`. Este ramo não cria nenhuma. Não as investiguei (fora da missão).
Declarado à mão (só isto): `provas/canario_1149/*.py` em `C-PROVA-ROTA-DO-HTML` (+ uma frase no `what`). O resto saiu
da cadeia.

### 7 · Para o coordenador correr na cópia (Windows)

```
:: 1 · MARCAR a cópia (uma vez; o runner nunca a cria)
psql -X -v ON_ERROR_STOP=1 -c "create table public._copia_descartavel (marcada_em timestamptz not null default now(), origem text not null); insert into public._copia_descartavel (origem) values ('pg_restore do dump <ficheiro> em 127.0.0.1:54391, 28/09');" "postgresql://postgres@127.0.0.1:54391/sala_italia"

:: 2 · PREVER (nada escrito)
py provas\canario_1149\rederivar_um_raw.py --dsn postgresql://postgres@127.0.0.1:54391/sala_italia --raw-id 2272 ^
   --armazem C:\Users\London1\sintonia-sala-italia\armazem --saida C:\tmp\c1149 --armazem-da-copia C:\tmp\c1149-armazem-da-copia

:: 3 · APLICAR (só na cópia) — o MESMO --armazem-da-copia em toda corrida nesta cópia
py provas\canario_1149\rederivar_um_raw.py … --aplicar
```
O banco da cópia tem de se chamar `sala_italia` (ou um nome da lista descartável); a porta tem de estar escrita. Com
`--livros` o recado de tempo e lugar leva também a confissão do coletor sobre FACT_TIME (sem ele, só contrato + página).

---

## PROBLEMA

1. **`DONO = NAO DEFINIDO`: o texto derivado novo do MESMO RAW não chega à Sala.** Três portas, e nenhuma serve:
   - **linha nova** — a DEDUP-DOC funde por documento (`sala_de_espera.py:779-839`), e o próprio código declara a
     consequência: «uma versão nova do MESMO documento … também não ganha 2.ª linha»;
   - **versão (036)** — `versao_do_documento.decidir` compara `parent_sha256` **antes** da receita: mesmo RAW ⇒
     `IGUAL` «bytes do RAW iguais», e nunca chega a re-extrair com o extrator novo. «BYTES IGUAIS NÃO CRIAM VERSÃO» está
     escrito no cabeçalho; o caso «bytes iguais, régua nova» não foi previsto;
   - **revisão (033)** — `texto` não é revisível (`CAMPOS_REVISIVEIS`, trava `revisao_so_de_campo_revisivel`).
   Resultado: a Intelligence continua a ler a linha achatada (corpo 0). **Não forcei, não apaguei, não dupliquei.**
2. **A publicação TEM caminho, mas mistura.** `PUBLISHED_AT` sai dos bytes da página, não do texto, e
   `admissao/reprocessar_tempo_lugar.py --raizes … --aplicar` já a revê pela 033. Mas corre sobre **todas** as linhas e
   recalcula FACT_TIME/FACT_LOCATION do texto **antigo** da linha. Não o corri nem o imitei: aplicar só a publicação no
   1149 seria escolher uma parte de um caminho que o dono desenhou inteiro.
3. **O Defeito A continua** (fora desta missão, só medido): T5 SIM por `ricerca` + `tesi` (substring de
   «at**tesi**»), antes e depois — a derivação nova não o conserta nem o piora.
4. **PROBLEMA continua `NAO SEI`** (xylella + nematode, D112) — elo 5, ontologia; decisão do dono.
5. **O armazém da cópia anda com a cópia do banco.** Medido no teste: uma 2.ª corrida com outro armazém deu
   `STORAGE_MISSING` (o dono tem razão: a linha existe, o byte não). Por isso `--armazem-da-copia`.
6. **A marca `_copia_descartavel` é convenção NOVA** (a missão pediu «marca/linha de cópia»; a casa não tinha). Vale
   para este runner; não é lei da casa.

## O QUE NÃO SEI

- **O resultado na cópia real (54391).** Não a vejo. Em particular: se o RAW 2272 lá é `FORWARD_IDENTIFIED` (o
  contrato IT-T5-111 declara `DOCUMENT_ID` por URL, por isso espero que sim — se não for, o runner PARA e diz); se a 036
  está aplicada nessa cópia (se não, `VERSOES = NAO_SEI «036 nao aplicada»`); os ids reais.
- **O efeito na admissão sobre as 628 páginas** — só a árvore (216) foi medida aqui.
- **Os números do armazém da v2** (628, 0 pioraram, 88→0 corpo vazio) são do coordenador; não os reproduzi.
- Nesta nuvem, `tests/test_migracao_033_sala.test_3_repousar_o_mesmo_e_retry_e_nao_conflito` falha
  (`RUN_ID_CONFLICT` ao repousar o que foi lido). Não toca em nada deste ramo (ficheiros novos só); não investiguei.
- Intelligence → pote → Casco: **não alcançados**, de propósito — a estrada parou na Sala.

## EM PALAVRAS SIMPLES

1. Pegamos a mesma página do CREA e passamos de novo pelo leitor consertado, numa cópia do banco: o texto agora tem 82 linhas separadas (antes era uma linha só), o corpo da matéria aparece, e a data de publicação 22/06/2026 foi lida do lugar certo.
2. Mas a Sala não aceitou o texto novo: ela vê que é o mesmo documento, com os mesmos bytes, e não abre linha nem versão nova — e nenhuma peça da casa tem a função de trocar o texto de uma linha que já está lá.
3. Quem decide como uma página já guardada recebe o texto corrigido ainda não foi definido; até lá, a inteligência continua lendo a versão achatada, e nós não forçamos nada.

HARD STOP.
