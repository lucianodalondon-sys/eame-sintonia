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
