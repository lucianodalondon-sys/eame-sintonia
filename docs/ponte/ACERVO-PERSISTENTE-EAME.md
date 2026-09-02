# ACERVO PERSISTENTE — EAME

Proposta da MISSÃO 11A-BRIDGE-ES. **Nada foi executado.** Nenhuma tabela criada, nenhuma
migration rodada, nenhum dado movido.

`PROJECT_NAME = eame-sintonia` (Supabase, vazio).

---

## 1 · O que foi medido, dos dois lados

| | Brasil `38e4b8d` | EAME `36c3a2d` |
|---|---|---|
| `.git` | 9,6 MB | 7,2 MB |
| dados versionados | 216 KB em `dados/` + **19 MB em `coletas-do-navegador/`** | 13 MB em `data/samples/` |
| maior arquivo | `2026-08-09-2228.json` — **6,6 MB** | `ES-T5-002-corpus-documentos.json` — **4,5 MB** |
| arquivos versionados | 812 | 62 JSON |
| persistência real | Postgres/Supabase, 34 tabelas com DDL no Git | **só Git** |

O Brasil versiona três JSONs de 6,6 MB de coleta bruta. É a evidência empírica de que Git
foi usado como depósito — e a razão pela qual o banco existe lá.

### O número que muda o diagnóstico

Os arquivos grandes do EAME foram escritos **1 ou 2 vezes cada**:

```
4.5M  1 commit   ES-T5-002-corpus-documentos.json
512K  2 commits  ES-T8-001-videos.json
180K  1 commit   ES-VOICE-LINKEDIN.json
```

A dor do Git **ainda não aconteceu aqui** — não porque o acervo seja pequeno, mas porque
ainda não houve coleta recorrente. Um corpus de 4,5 MB reescrito uma vez é barato. O mesmo
corpus reescrito a cada rodada é que estoura o histórico e torna o diff ilegível.

**O gatilho da migração é cadência, não tamanho.**

---

## 2 · As três casas

### GIT — o que precisa ser revisável, versionado e pequeno
Código; migrations; testes; contratos; `scripts/`; documentação; `RUN-MANIFEST.json` e
`DATA-CLOCK-manifest.json` como manifesto; **snapshots canônicos pequenos** que servem de
fixture (`PORTAO-DE-REDE-ES-CURRENT.json`, `VERIFICACAO-ADVERSARIAL-PORTOES.json`,
`X-007-canonical-agro-dictionary.json`); os PDFs de versão do MAPA que provam mudança
(`ES-T4-004-versoes/`, 292 KB cada).

Critério: **cabe num diff que uma pessoa lê?** Se sim, Git.

### SUPABASE POSTGRES — o que precisa ser consultável
Todo o acervo estruturado: `collection_run`, `origem`, `pessoa`, `organizacao`, `canal`,
`conteudo`, `transcricao`, `comentario`, `crop`, `issue`, `crop_issue`, `observacao`,
`derivacao`, `resposta_registrada`, `registro_regulatorio`.

Critério: **alguém vai querer filtrar, agrupar ou juntar isto?** Hoje "todos os vídeos de
um canal entre duas datas" exige carregar 512 KB de JSON na memória e iterar. Isso é uma
consulta, não um script.

### SUPABASE STORAGE — o bruto pesado
Datasets da Apify, HTML, PDFs grandes, transcrições longas, exports do ROPF.
No Postgres fica só o ponteiro: `raw_asset(storage_path, sha256, bytes, run_id, captured_at)`.

Critério: **é evidência que quase nunca se lê inteira, mas nunca pode sumir?** Storage.

> `data/samples/raw-paid/` (2,2 MB, 11 gzips) é o caso de fronteira. Fica no Git **por ora** —
> é pequeno e é prova. Migra para Storage quando a coleta virar recorrente, que é o mesmo
> gatilho de tudo.

---

## 3 · O que NÃO copiar do Brasil

**`vozes` com canal em coluna.** `linkedin_url`, `instagram`, `youtube`, `tiktok`, `site`
são cinco colunas para cinco plataformas. Funciona até a sexta, e "quantos canais esta
pessoa tem?" vira leitura de colunas nulas em vez de `count(*)`. O EAME precisa de
`origem → canal` (1:N) porque a lei "uma palestra republicada em 5 lugares não são 5
evidências" depende de contar origens e obras distintas.

**`documentos.cultura` singular.** O Brasil guarda `culturas text[]` na fonte mas `cultura
text` no documento. A assimetria força o colapso justamente onde a evidência mora — e é
por isso que o par CROP × ISSUE lá só existe na camada analítica. Aqui o par nasce colado
à evidência, em `conteudo_crop_issue`.

**Um único campo de lugar.** `praca` responde ao mesmo tempo "de onde é a fonte" e "sobre
onde fala". Com um campo só, o confundidor de Córdoba não tem como ser nem formulado.

**Vocabulário, praças, UF, safra, AGROFIT, e os pesos calibrados no Brasil.** Nada disso
viaja. E `RLS`/`auth`/`Storage` são escolha de fornecedor: a modelagem sobrevive a trocar
Supabase por outro Postgres.

---

## 4 · Migrations propostas

Em `supabase/migrations/`, versionadas no Git, **não executadas**.

| | objetivo |
|---|---|
| `001_fundacao_geografia_e_proveniencia` | `pais`, `geografia` (source ≠ fact), `collection_run` (o RUN_MANIFEST em Postgres), `raw_asset` com CHECK que exige motivo quando o bruto não foi preservado |
| `002_identidade_pessoa_org_canal` | `pessoa` ≠ `organizacao`; `pessoa_identificador` **sem** unique(sistema,valor) para que conflação continue representável; `origem` com CHECK de exclusividade; `canal` chaveado por `channel_id`, nunca por nome |
| `003_conteudo_documento_video_transcricao` | `conteudo` com `obra_id` (independência), `hash_conteudo`, as duas geografias, pessoa declarada ≠ dona do canal; `transcricao` com `caption_source`; `comentario` com `autor_hash` |
| `004_crop_issue_par_explicito` | `crop`, `issue` ancorados nos ids reais do MAPA (448 cultivos, 708 plagas); `crop_issue`; `conteudo_crop_issue.relacao` distinguindo ocorrência de coocorrência e de espectro de rótulo |
| `005_camada_analitica_observado_vs_derivado` | `observacao` com denominador NOT NULL; `derivacao` com `limitacao` NOT NULL e `CONFOUNDER_OPEN` como estado; `resposta_registrada` com disponibilidade comercial default `NAO_SEI`; `lacuna_candidata` com CHECK que proíbe zero virar lacuna sem diagnóstico |
| `006_regulatorio_e_rls` | `registro_regulatorio` com `fonte_versao` **na chave** (status atual não apaga história); `registro_uso`; RLS em todas |
| `007_views_de_apoio` | `v_acervo`, `v_independencia_por_par`, `v_par_por_porta`, `v_execucao_degradada`, `v_cadeia_quebrada` |

Quatro leis viraram **constraint**, não lembrete:

```sql
CHECK (preserved OR not_preserved_reason IS NOT NULL)          -- bruto ausente é declarado
CHECK (num_nonnulls(pessoa_id, organizacao_id) = 1)            -- pessoa ≠ organização
CHECK (estado <> 'LACUNA_CANDIDATA' OR zero_diagnosticado)     -- zero é chave quebrada
observacao.base_denominador NOT NULL                            -- razão exige denominador
```

---

## 5 · Lote de prova antes de escalar

Dados que o EAME **já tem**, nada de coleta nova:

| tabela | origem | n |
|---|---|---|
| `collection_run` | `RUN-MANIFEST.json` | 10 execuções reais |
| `raw_asset` | `data/samples/raw-paid/` | 11 gzips, com SHA-256 já no DATA-CLOCK |
| `origem` / `canal` | `ES-T8-001-baseline-canais.json` | 5 canais |
| `conteudo` | `ES-T8-001-videos.json` | 10 vídeos |
| `transcricao` | `ES-T8-001-transcricoes.json` | 5 |
| `pessoa` | `RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json` | 5 pesquisadores com ORCID |
| `registro_regulatorio` | export ROPF | 12 registros ADAMA de OLIVO |

O lote precisa provar cinco coisas, e **falhar é resultado válido**:

1. **identidade** — dois OpenAlex IDs da mesma pessoa não viram duas pessoas; e o mesmo ID
   cobrindo duas pessoas continua expressável como conflação;
2. **dedupe** — o mesmo vídeo por duas queries entra uma vez; título igual não colapsa;
3. **proveniência** — de qualquer conteúdo chega-se a `run_id → actor → input → raw_asset → sha256`;
4. **relações** — `v_independencia_por_par` conta obra distinta, não linha;
5. **round-trip** — o que sai do Postgres reproduz o JSON de origem campo a campo; onde não
   reproduzir, a diferença é o achado.

---

## 6 · A comparação pedida

| | A · tudo em Git | B · Postgres | C · Postgres + Storage |
|---|---|---|---|
| hoje (62 JSON, 13 MB, 1–2 escritas) | **funciona** | ocioso | ocioso |
| coleta recorrente | histórico estoura; diff ilegível | resolve consulta; bruto ainda incha o Git | **resolve os dois** |
| consulta ad-hoc | carregar JSON inteiro | SQL | SQL |
| revisão humana do dado | diff legível enquanto pequeno | perde o diff | mantém no Git o que é pequeno |
| custo de errar | reescrever arquivo | migration | migration |

```
RECOMMENDED_EAME_MODEL = C — Postgres + Storage, com Git mantendo
                             código, migrations, contratos, manifestos e
                             snapshots canônicos pequenos.
```

A escolha não é "banco é melhor que Git". É que as três casas respondem perguntas
diferentes, e hoje o Git está respondendo as três — o que ainda dá certo só porque a coleta
não recomeçou.

---

## 7 · O que a leitura da proveniência brasileira corrigiu aqui

Quatro achados, lidos do repositório Brasil. **A refutação ainda não rodou sobre eles.**

**O custo não diz como foi medido.** No Brasil, três métodos diferentes — `usageTotalUsd`
da plataforma, diferença de saldo, e tabela de preço — escrevem na **mesma coluna
`custo_usd`**, e a coluna não registra qual produziu o número. O leitor do acervo chamou
isso de *"o defeito de schema mais importante desta dimensão"*. Somar os três produz um
total que não existe. Corrigido: `collection_run.cost_method` com CHECK que exige o método
sempre que houver custo. E `NULL ≠ 0` — nulo é "não medido", zero é "medido e deu zero".

**Uma FK nulável não garante o elo.** `documentos.coleta_id` existe como FK desde o início,
mas o preenchimento é **parcial e não uniforme por porta — zero em várias células**. O custo
operacional foi medido: o freio de fonte-seca da fila lê `coletas` e por isso **enxerga só
um quarto do acervo**. Elo faltando vira decisão errada, não só lacuna de metadado. Aqui
`run_id` é `NOT NULL` em `conteudo`, `transcricao` e `comentario`: a linha não existe sem a
execução que a produziu.

**Uma tabela, duas semânticas.** `coletas` mistura RODADA (`fonte_id` nulo) com VISITA A UMA
FONTE (`fonte_id` preenchido). Os dois denominadores nunca podem ser somados, e a casa teve
de descobrir isso depois. `collection_run` é uma linha por execução de ator, e só.

**Proveniência é prospectiva.** A proibição de backfill está escrita como princípio no
Brasil: *"inventar o elo depois seria fabricar proveniência"*. Adotada como comentário de
tabela, não como intenção.

### E uma correção à recomendação da seção 6

Eu apresentei a opção C (Postgres + Storage) como se fosse herança do Brasil. **Não é.**
A varredura mediu, por grep sobre todo o repositório, que **não existe object storage em
lugar nenhum** do Sintonia Brasil — nem S3, nem bucket, nem Supabase Storage. A decisão
brasileira está no `.gitignore`: o repositório guarda o **contrato**, o banco guarda o
**veredito com o número**, e o **texto bruto fica em disco local não versionado**.

Isso significa que o bruto pesado brasileiro **não é durável** — ele vive na máquina de quem
rodou. A opção C não copia o Brasil: ela resolve algo que o Brasil não resolveu. Continua
sendo a recomendação, mas agora pelo motivo certo, e sem precedente para se apoiar.

---

## 8 · A medição derrubou a minha justificativa (a conclusão sobreviveu)

A refutação fechou: **15 agentes, 0 erros; 13 de 225 afirmações refutadas**, quase todas
correções numéricas com a tese intacta. Mas a medição do EAME derrubou uma hipótese minha
inteira, e é a que eu tinha usado para justificar a recomendação.

### O que eu disse, e o que a medição mostrou

Eu escrevi que "JSON grande reescrito inteiro estoura o histórico". **Medido: falso.**
Git deltifica JSON *pretty-printed* muito bem. As duas versões de `ES-T8-001-videos.json`:

```
ead8225  431,4 KB bruto -> 91,6 KB no pack   (sem delta base)
1e17f19  508,3 KB bruto ->  6,4 KB no pack   (delta contra a anterior)
```

Ratio agregado em `data/samples/`: **`.json` 9,87 MB → 1,60 MB no pack (0,16)**. Reescrever
o corpus de 4,5 MB é barato. **O corpus científico não é o problema de armazenamento.**

### O que é o problema

**Os gzip.** 12 blobs `.gz`, **ratio 1,00, zero com delta base**. Gzip é entropia máxima:
git não comprime nem deltifica. Cada versão nova de um `.gz` entra no pack pelo tamanho
integral, **para sempre**. `linkedin-profiles.raw.json.gz` sozinho é 1,15 MB — **17% do
pack inteiro**.

> Regra derivada da medição: **cada rodada de coleta paga soma ~2,1 MB permanentes ao pack**,
> independentemente de quanto do conteúdo se repita da rodada anterior.

**E um arquivo já quebrou o critério da §2.** `ES-T8-001-transcricoes.json`: 710 KB em
**239 linhas** — uma transcrição inteira por linha, p95 de 22.780 caracteres, máximo de
90.760. Corrigir um caractere produz um diff de 90 mil caracteres numa linha só. O critério
que escrevi — *"cabe num diff que uma pessoa lê?"* — **já está violado por este arquivo**.
Os outros ainda passam.

### Cadência projetada, com as premissas declaradas

Taxa derivada dos 252 vídeos (2010–2026, 157 canais): **1,25 vídeo novo/mês** no universo
atual. Assumindo expansão 3× (olivar + cereal + vinha):

| | registros | normalizado | bruto gz |
|---|---|---|---|
| **backfill** do universo expandido | 3.302 | **11,0 MB** | **4,5 MB** |
| **rodada mensal** | ~10 + LinkedIn | 0,2–0,8 MB | 0,09–0,41 MB |

O backfill sozinho — **15,5 MB numa rodada** — é mais que os 12 MB que `data/samples/`
acumulou em 64 commits. Transcrições são **62% do payload normalizado a partir de 4,5% dos
registros**: uma transcrição custa 25× um vídeo.

Cadência **mensal**: +3 MB/ano de gz. Sobrevivível.
Cadência **semanal** (o que o contrato de atualização pede para regulatório): **+13 MB/ano
só de gz**, e `data/samples/` cruza o teto de "dezenas de MB" escrito em
`POLITICA-RAW-ROTA-PAGA.json` **dentro do primeiro ano**.

### Conclusão corrigida

`RECOMMENDED_EAME_MODEL = C` **continua de pé — pelo motivo trocado.**

O que empurra para Storage não é o corpus, nem o volume total, nem o diff dos JSON. É que
**o `.gz` não deltifica**, e cada rodada paga é um depósito permanente e irrecuperável no
pack. Postgres resolve a consulta; **Storage resolve o que estava me preocupando pela razão
errada.**

Ordem prática que a medição sugere, e que inverte a minha:
1. **Storage primeiro** — tirar `raw-paid/` do Git antes do backfill, não depois.
2. **Postgres em seguida** — a consulta dói (30 `json.load` em 21 scripts; cruzar três
   arquivos é carregar 780 KB e fazer join em Python sem constraint), mas dói *devagar*.
3. **Git fica** com o que já resolve bem: manifestos, contratos, snapshots pequenos — onde
   o diff **é** o produto.
