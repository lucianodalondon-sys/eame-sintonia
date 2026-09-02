# BRASIL → EAME — MAPA DE PRIORIDADE

**BRAZIL_TARGET_SHA** `38e4b8d4fd183ad9aba221eb014a7799e6b6f886` (portal-sintonia, main)
**EAME_TARGET_SHA** `36c3a2d0c0e1adb61e1265836fdd61c47df77691` (eame-sintonia, collection-es)

Ambas as árvores limpas na leitura. Toda afirmação deste documento é sobre esses dois SHAs.

> **O que viaja:** lei, invariante, contraexemplo, padrão de pipeline, instrumento, teste,
> arquitetura de pergunta, dono da regra.
> **O que não viaja:** dado, peso, vocabulário, schema copiado sem a pergunta junto.

---

## A · A matriz

| BRAZIL_LESSON | BRAZIL_OWNER | BRAZIL_TEST | EAME_EQUIVALENT | STATUS | ACTION |
|---|---|---|---|---|---|
| Autor de conteúdo entra pseudonimizado, nunca nome/@ | `supabase-conteudo.sql` → `documentos.autor_hash` | constraint + `v_acervo` conta `distinct autor_hash` | `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md` (P-008 **aberta**) | **ADAPT** | virar coluna `char(64)` em `comentario`; a regra sai do documento e entra no schema |
| Dedupe é constraint, não auditoria posterior | `documentos` → `unique(fonte_id, hash_conteudo)` | o banco recusa a segunda inserção | portão `PIPELINE_DEDUPE` em `scripts/portao.py` | **ADAPT** | manter o portão *e* ganhar o unique — um denuncia, o outro impede |
| Razão publicada exige denominador declarado | `termos_medicoes.base_comentarios/base_pessoas` NOT NULL | `unique(termo, período, praça, cultura)` | `ES-T4-005-denominadores-ropf.json`, `metricas_canonicas.py` | **ALREADY_EXISTS** (regra) / **ADAPT** (lugar) | `observacao.base_denominador` NOT NULL |
| Execução vazia ≠ execução concluída | `coletas.status` inclui `'vazia'` | — | `scripts/coletor.py` (SUCCEEDED com 0 itens → PARTIAL) | **ALREADY_EXISTS** | portar o enum `run_status` com `vazia` separado |
| Custo e ator ficam gravados por execução | `coletas.ator/run_id/custo_usd` | — | `RUN-MANIFEST.json` + `scripts/proveniencia.py` (22 campos) | **ALREADY_EXISTS** | `collection_run` é transporte campo-a-campo, não redesenho |
| Cultura é conjunto, não valor único | `fontes.culturas text[]` | — | `ES-RESEARCHERS-OLIVE.json` já traz `CROP` como lista | **ALREADY_EXISTS** | — |
| A porta muda a distribuição; não eleger cultura por uma porta só | `seletor-por-porta.py`, `censo-das-portas.py` | `SHADOW-SELETOR-POR-PORTA.md` | *nenhum* | **EAME_GAP** | `conteudo.tipo` + view `v_par_por_porta`; a pergunta vira `GROUP BY` |
| CROP × ISSUE é par explícito, nunca `cult_top` | `par-explicito.py`, `contrato-multi-cultura.py` | `PAR-EXPLICITO-PORTAL-SHADOW.md` | *nenhum* — o EAME tem `CROP` e `ISSUE` como listas paralelas, não como par | **EAME_GAP** | tabela `crop_issue` + `conteudo_crop_issue` |
| Coocorrência textual não prova o par | `sonda-causa-artigo.py` | `SONDA-ARTIGO-CAUSA.md` | *nenhum* | **EAME_GAP** | `conteudo_crop_issue.relacao` com `COOCORRENCIA_TEXTUAL` e `ESPECTRO_DE_PRODUTO` marcados como fracos |
| Detecção ≠ portfólio | `separar-portfolio.py`, `sombra-do-separador.py` | `SEPARACAO-PORTFOLIO-DETECCAO-SHADOW.md` | parcial: `RADAR-ADAMA-prothioconazole.json` separa sinal de registro | **ADAPT** | `observacao` e `resposta_registrada` em tabelas distintas, sem FK entre elas |
| "Temos para?" ≠ "existe lacuna?" | `temos-para.py`, `tem-registro-para.sql` | — | *nenhum* | **EAME_GAP** | `lacuna_candidata` com CHECK que proíbe zero virar lacuna sem diagnóstico |
| Zero inesperado é chave quebrada até prova em contrário | `duas-fontes-do-portfolio.py`, `nome_do_produto.py`, `impacto-da-normalizacao.py` | `ERRO-DE-ESCRITA-MEDIDO.md` | `X-006-substance-normalisation.json`, `normalize_substance.py` | **ADAPT** | o normalizador existe; falta o *reflexo* — `lacuna_candidata.zero_diagnosticado` |
| Status atual não apaga a história | `registro_mapa.sql`, `termo_snapshot` | `prova-do-relogio.sql` | `CHANGE-EVENTS-es-2025-2026.json`, `DATA-CLOCK-manifest.json` | **ALREADY_EXISTS** | `fonte_versao` entra na chave de `registro_regulatorio` |
| Uma regra, um dono | `FERRAMENTAS-MESTRAS.md`, `invariantes-do-dado.py` | `travas.py` | `scripts/metricas_canonicas.py` + `--sync` (medido nesta sessão: reprova quando o número diverge) | **ALREADY_EXISTS** | não replicar lógica dentro do banco; views leem, não recalculam |
| Sombra antes de trocar produção | `sombra-multi-cultura.py`, `folha-cega-v2.py` | `FOLHA-CEGA-MULTI-CULTURA-V2.md` | `BENCHMARK-ORDENACAO-B2.json` (mesma pergunta, quatro ordenações) | **ALREADY_EXISTS** | usar o padrão ao trocar qualquer régua de prioridade espanhola |
| Uma leitura, N pares | `radar-do-campo.py`, `radar-multi.py` | `PRE-VOO-RADAR-MULTI-REAL.md` | *nenhum* | **EAME_GAP** | `conteudo_crop_issue` é N:N — uma leitura do acervo alimenta N pares |
| 1 pessoa → N canais | `vozes` com colunas `linkedin_url/instagram/youtube/tiktok` | — | *nenhum* | **ADAPT — não copiar** | o Brasil resolveu com colunas e trava na quinta plataforma; EAME usa `origem` → `canal` (N:N) |
| Vocabulário, praças, UF, safra, AGROFIT, TikTok | vários | — | — | **DO_NOT_COPY** | fonte espanhola é MAPA/ROPF, RAIF, ORCID, ROR |
| Supabase RLS/auth/Storage | `supabase-conteudo.sql` | — | — | **ADAPT** | escolha de fornecedor, não de modelagem; a modelagem sobrevive a troca |

---

## B · O que o Brasil resolveu e o EAME ia reconstruir

Três coisas que estavam prestes a nascer do zero aqui e já existem lá, testadas:

1. **A separação detecção/portfólio.** Ia virar mais um portão. Lá é um instrumento com sombra medida.
2. **O reflexo diante de um zero.** Sem ele, `AGUACATE = 0 registros ADAMA` viraria achado. No Brasil o mesmo formato de zero era normalização quebrada, e virou N correspondências depois do conserto.
3. **A régua por porta.** Sem ela, a fila de pessoas nasce de qualquer camada que tenha mais volume — que é exatamente como a fila olive-first nasceu.

---

## C · O que o EAME tem e o Brasil não

Não é transferência de mão única:

- **`SOURCE_LOCATION` ≠ `FACT_LOCATION`.** O Brasil tem UM campo (`praca`) para as duas. É o confundidor de Córdoba impossível de expressar. O EAME já separa em contrato, e o schema proposto separa em coluna.
- **`NOT_PRESERVED` como estado declarado.** `scripts/proveniencia.py` distingue "não preservado" de "vazio". Vira CHECK em `raw_asset`.
- **Verificação adversarial com SHA congelado.** `VERIFICACAO-ADVERSARIAL-PORTOES.json` carimba o commit auditado. Não achei equivalente no Brasil.

---

## D · Veredito da ponte

```
BRAZIL_REUSE_VALUE = HIGH
```

Alto, mas quase todo em **lei e forma**, não em código. Nenhum `.py` brasileiro roda no EAME sem reescrita — a fonte é outra, o vocabulário é outro. O que viaja e vale caro é o **schema**: `supabase-conteudo.sql` é a planta baixa, e sete das dezoito linhas da matriz saem dele diretamente.

O maior ganho não é o que copiamos. É o que **deixamos de descobrir sozinhos**: seis `EAME_GAP` acima são defeitos que só apareceriam depois de coletar, e o Brasil já pagou por eles.

---

## E · Segunda colheita — e o que ela achou no meu próprio desenho

Uma varredura paralela leu 10 instrumentos brasileiros e 5 dimensões do acervo persistente.
**Ela foi truncada:** 20 dos 35 agentes morreram em limite de sessão, e a fase de refutação
não rodou em nenhum. **Nada nesta seção passou pelo crivo adversarial** — as afirmações
carregam evidência citada pelo leitor, não verificação independente. Tratar como candidato.

Cinco achados mudaram o schema proposto. Não eram refinamento: eram defeitos.

**1 · Origem sem chave natural.** No Brasil `fontes` tem apenas `id bigserial primary key`.
Custo medido: *102 nomes repetidos em 212 fontes* (HRAC 3×, FRAC 2×, Lavoro 9×). E como o
dedupe de `documentos` é `unique(fonte_id, hash_conteudo)`, uma fonte cadastrada duas vezes
faz o mesmo conteúdo entrar duas vezes — e para o índice isso é legítimo. **O dedupe do
conteúdo nunca é melhor que a identidade da origem.** Minha `origem` tinha o mesmo buraco.
Corrigido com índice único parcial por pessoa e por organização.

**2 · NULL não colide com NULL.** No Postgres dois nulos são diferentes, então uma chave
única com coluna nulável destranca sozinha justamente para as linhas que deixaram o campo
em branco. Eu tinha o furo em **cinco** chaves — `geografia`, `transcricao`, `observacao`,
`registro_uso` — e a quinta só apareceu quando o teste que escrevi para as outras quatro
reprovou. Todas passaram a `UNIQUE NULLS NOT DISTINCT`.

**3 · Uma lei nova não pode destruir o que veio antes.** No Brasil a regra "um vídeo, uma
transcrição" foi **recusada pelo banco**: o acervo já a violava e o índice único não pôde
ser criado. O conserto foi `duplicata_de` — a cópia mais completa fica, a outra aponta para
ela, e a lei vale daqui para frente. Adotado em `conteudo`.

**4 · Constraint não pega dado semanticamente falso.** `registro_mapa` tem
`unique(produto_nome, linha_hash)` e mesmo assim **82,3% das linhas ficaram penduradas no
produto errado** — porque a mesma linha no produto errado é uma chave legitimamente
distinta. O coletor perguntava ao MAPA por uma marca e filtrava só por titular ("é da
ADAMA?"), sem a segunda pergunta ("é *deste* produto?"). Nenhuma constraint pega isso;
por isso o Brasil tem uma camada de **invariantes** acima das travas. É o mesmo papel dos
portões do EAME — e a razão de eles continuarem existindo depois do banco.

**5 · Migração versionada não prova que a trava está no banco.** O achado mais caro:
no Brasil o arquivo de schema **deixou de descrever o banco**. Quatro colunas de `fontes`
usadas por 6 coletores e pela fila inteira foram criadas à mão no painel e nunca entraram
em `.sql`; `eh_admin()` é chamada 10 vezes e não é definida em lugar nenhum; a view da fila
de coleta idem. A `fontes` real tem **63 colunas** contra as 14 declaradas, e seis existem
e nunca foram escritas — esquema morto. O próprio repositório escreve o veredito:

> «quem for montar este banco do zero amanhã monta um banco que não funciona»

Daí nasceu a `008_verificacao_pos_aplicacao.sql`: ela não cria nada, confere contra
`information_schema` e `pg_constraint` que 001–007 foram aplicadas, e levanta exceção
listando o que faltar. `tests/test_migrations.py` cobre o outro lado — que os arquivos são
coerentes entre si. **Nenhum dos dois sozinho fecha a pergunta.**
