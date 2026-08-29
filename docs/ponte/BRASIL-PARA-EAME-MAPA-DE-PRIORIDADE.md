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
