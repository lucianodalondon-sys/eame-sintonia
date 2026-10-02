# PROVA · 7 boletins ERSA FVG entram na árvore IT · PDF → texto → RAW → porta

**Data:** 2026-10-02 · **Missão:** SCRAP · **Decisão do owner:** DA (reversível), registada pelo Coordenador no HANDOFF-VIVO.
**Worktree:** `C:/Users/London1/orca/workspaces/eame-sintonia/scrap-pdf-fds` · **Ramo:** `scrap/pdf-fds-20261002` · **Base:** `82d3f4913` (não publicado; commit local).
**Capacidade usada:** `coleta/executor_texto_de_pdf.py` (pdftotext) + `coleta/golden_path_pdf.py` + `admissao/admissao.py`. **Nenhuma ferramenta nova.**

## O que se fez

1. Os 7 brutos foram **copiados** (não movidos, não apagados) de `C:/eame-sintonia/.tmp/pdf/`
   para a árvore IT do collection-store: `data/collection-store/italy/IT-T3-027/`.
2. SHA256 dos 7 conferido nos dois lados: **7/7 iguais**. Originais intactos.
3. Corrida canónica `py coleta/golden_path_pdf.py` com recibo em
   `system-map/data/golden-path-pdf.generated.json`.

## Medição (números reais da corrida DERIV-PDF-20261002T191843Z, STATUS SUCCESS)

| | |
|---|---:|
| RAW_INPUT (PDF italianos vistos) | 56 |
| RAW_TEXT_LAYER_PRESENT | 7 |
| RAW_NEEDS_OCR | 0 |
| RAW_EXTRACTION_ERROR | 0 |
| DERIVED_EMITTED / DERIVED_LANDED | 7 / 7 |
| ADMISSION_SEEN / ADMISSION_SIM | 7 / 7 |
| LOST | 0 |
| RAW_IMUTAVEL | 56 conferidos · 0 alterados · 0 desaparecidos → IMUTAVEL |
| COST_USD | 0.0 (rota gratuita provada; rede NÃO; OCR NÃO) |

## Os 7 documentos (pai RAW = impressão digital dos bytes)

| PDF | chars | RAW (pai) | ADMISSÃO |
|---|---:|---|---|
| actinidia12.pdf | 6 080 | RAW-10792df218470d6e | SIM |
| drupacee19.pdf | 9 849 | RAW-74778e8b689924a6 | SIM |
| ersa_mais15.pdf | 6 312 | RAW-9f0aa1ed9e2ecd8a | SIM |
| melo25.pdf | 17 187 | RAW-f74a097c88e8ba7f | SIM |
| orticolo2708.pdf | 37 737 | RAW-d7f1ba8b67182ad5 | SIM |
| patata2508.pdf | 16 405 | RAW-40eefe113bb879e2 | SIM |
| vite33.pdf | 7 976 | RAW-0d07e5eaed61f184 | SIM |

Os 7 `DERIVED-TEXT_EXTRACTION-*` estão em `data/derivados/REGISTO-DE-ARTEFATOS.json`, cada um
com o seu `PARENT_ARTIFACT_ID` = `RAW-<sha256[:16]>` do boletim de origem. **Linha provada
PDF → texto → RAW → porta.**

## O que NÃO se afirmou

- A ligação de cada documento com a página de índice da fonte fica **UNKNOWN** (ordem do Coordenador).
- O contrato da IT-T3-027 está `CONTRACTED_CANARY_FAILED` com tipo HTML de índice: o RAW diz
  qual a fonte dona do documento; **não** diz que o índice foi coletado agora.
- `PRECISION = UNKNOWN`: passar 7 de 7 é COBERTURA. Não há gabarito humano para dizer que
  estão certos.

## Achado (fora do escopo desta missão — não corrigido)

A porta admitiu os 7 pelo **universo T5 (SCIENCE)**, porque o cabeçalho do boletim traz
«SERVIZIO FITOSANITARIO E CHIMICO, **RICERCA, SPERIMENTAZIONE** ED ASSISTENZA TECNICA»:
as palavras-gatilho são `ricerca` e `sperimentazione`. A fonte dona é **fitossanitária (T3)**.
O rótulo do universo pode estar errado — palavra da fonte não é o tema da fonte.
Achado registado, não corrigido aqui.
