# RELEVANCIA-ELEGIVEIS-V1 — a rota existe; o conteúdo serve para a Sala?

Missão 3b · branch `relevancia-elegiveis-v1` · base 88ce30a8 · 2026-09-22.
Instrumento: `medidas/relevancia_antes_da_coleta.py` · dados: `curadoria/RELEVANCIA-ELEGIVEIS-V1.json`.

Cadeia, toda da casa e sem cópia: bytes → `coleta/executor_texto_de_html.extrair` →
`orquestrador.item_documental_para_a_porta` → `admissao.decidir(item, universo)` em
memória. `admissao.escrever()` nunca é chamado; `LIVRO-DE-DECISOES.json` com o mesmo
sha256 antes e depois (499ebc99…); zero ligação à base. Universo = o do SOURCE_ID
(mesma leitura da missão 4). A leitura temática isolada (`_do_universo`) concorda com
`decidir` em 26/26: a prontidão passou e a porta chegou ao tema.

Egresso: **BR (177.95.91.48, Londrina) nas 13 idas**. A coleta real exige IT; o texto
das matérias não depende do egresso, mas fica declarado.

## Por fonte

| SOURCE_ID | U | amostras (decidir) | SIM previsto | classe | coorte | porquê |
|---|---|---|---|---|---|---|
| IT-T10-018 myfruit | T10 | NAO_SEI ×2 (1 sinal: prezzi) | 0/2 hoje · 5/9 na Sala real | TEMA | **ENTRA_NA_MICRO** | a única com SIM já medido na Sala; o dia decide |
| IT-T9-021 Fiera Didacta | T9 | SIM ×2 (evento, novita, fiera) | 2/2 | FONTE | **FICA_FORA** | feira de escolas (circular do MIM a diretores). T9 = «o que o concorrente publica»; o SIM vem de palavras genéricas. ⚠️ decisão minha contra um SIM da régua — declarada e contestável |
| IT-T10-022 Zootecnica Intl | T10 | NAO_SEI ×2 (0 sinais) | 0/2 · 0/10 na Sala | REGUA | **FICA_FORA** | em inglês; a lista T10 não tem inglês |
| IT-T7-017 Riunite | T7 | NAO ×2 (prova de T5/T9/T10) | 0/2 · 0/30 | FONTE | **FICA_FORA** | comunicação de marca |
| IT-T7-033 Chianti Classico | T7 | NAO_SEI ×2 (1 sinal: consorzio) | 0/2 · 0/15 | FONTE | **FICA_FORA** | marca; secções úteis são séries paradas (adenda da missão 3) |
| IT-T7-042 Balsamico | T7 | NAO_SEI ×2 (1 sinal: consorzio) | 0/2 · 0/10 | FONTE | **FICA_FORA** | idem |
| IT-T7-043 Agrofarma | T7 | NAO (T4 etichetta, T9 evento, T5 ricerca) · NAO_SEI (agronomi) | 0/2 | UNKNOWN | **NAO_SEI** | conteúdo de defesa vegetal (biocontrole) que a régua T7 não lê; pode ser universo mal catalogado (T4/T9) — decisão de catálogo |
| IT-T12-041 BURA | T12 | NAO_SE_APLICA ×2 | 0/2 garantido | REGUA | **FICA_FORA** | a porta não tem régua T12 |
| IT-T12-057 Giovani Lombardia | T12 | NAO_SE_APLICA ×2 | 0/2 | REGUA (+FONTE provável) | **FICA_FORA** | sem régua; amostras: fórum de jovens, prémio de estudantes |
| IT-T12-074 Open Innovation | T12 | NAO_SE_APLICA ×2 | 0/2 | REGUA (+FONTE provável) | **FICA_FORA** | sem régua; webinar de financiamento, prémio de estudantes |
| IT-T2-034 ARPA Marche | T2 | NAO_SE_APLICA ×2 | 0/2 | REGUA | **FICA_FORA** | a porta não tem régua T2 |
| IT-T2-051 Arpae | T2 | NAO_SE_APLICA ×2 | 0/2 | REGUA | **FICA_FORA** | sem régua; vagas de emprego, balneabilidade |
| IT-T2-056 Arpae (2.ª ficha) | T2 | NAO_SE_APLICA ×2 | 0/2 | REGUA | **FICA_FORA** | sem régua; e duplicada de T2-051 |

```
SOURCES_SAMPLED = 13 · SAMPLES = 26 · EGRESS = BR em 13/13 idas
COHORT_IN = 1 (IT-T10-018)
COHORT_OUT = 11 — REGUA sem universo T2/T12: 6 · FONTE marca: 3 · FONTE feira escolar: 1 · REGUA inglês: 1
NAO_SEI = 1 (IT-T7-043)
ADMISSION_CHANGED = NO · DB_WRITES = 0
```

## Recomendações (separadas; nenhuma aplicada)

1. **Régua para T2 e T12** — dono: `admissao/admissao.py::PERGUNTAS_DO_UNIVERSO`. Hoje, 6
   de 13 fontes com rota produzem **0 garantido**. Antes de escrever palavras, decidir
   se essas fontes são mesmo desses universos: as amostras de T12-057/074 e T2-051
   não parecem agro.
2. **T9 aceita palavras genéricas** (`evento`, `fiera`, `novita`) — uma feira de escolas
   passa como «concorrente». Mesmo dono.
3. **Inglês em T10** — já pedido pela missão 4 (Zootecnica).
4. **IT-T7-043 Agrofarma** — conferir o universo no catálogo (T4 regulatório ou T9
   indústria?) antes de a pôr na micro.
5. **Duplicada T2-051/T2-056** — decisão de identidade no Atlas.
