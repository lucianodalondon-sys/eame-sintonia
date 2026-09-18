# CENSO DAS LIGAÇÕES DA COLLECTION — card por card

> **Este ficheiro é GERADO.** Não se edita à mão: edita-se o repositório e
> regenera-se. Ele sai da mesma corrida que produz `state.generated.json`, e
> por isso nunca fica a discordar da tela.
>
> Cada linha diz **quem ativa**, **o que entra**, **o que sai** e **qual é a
> prova** — e diz `NÃO SEI` onde não há prova, em vez de deixar o campo em
> branco, que é a mesma coisa dita de um modo que ninguém vai investigar.
>
> **STATUS OPERACIONAL e STATUS DA ROTA são eixos diferentes.** Um card verde
> não promove as ligações dele, e uma rota em `NÃO SEI` não rebaixa uma peça
> que funciona.

```
HEAD_DA_MEDICAO  65eadb2710206dd48b3335109958b20321e2ed47
BRANCH           claude/scrap-capabilities-wiring-v1
GERADO_EM        2026-09-18T13:12:13-03:00
CARDS            73
FONTE            system-map/data/state.generated.json
COMO_REFAZER     py system-map/scripts/generate_system_map.py
```

## Z-ACOES · os executores

### `C-COLETA-BASE` · O motor de buscar

| | |
|---|---|
| **peça real** | `coleta/coleta_checkpoint.py`, `coleta/coletor.py`, `coleta/filas.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 2 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml:209 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/ES-RESEARCHERS-OLIVE.json`, `data/samples/ES-VOICE-LINKEDIN.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 8 · saem 26 |
| **arestas provadas** | entram 8 · saem 26 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 34 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-COLETA-INSTAGRAM` · Colher o Instagram

| | |
|---|---|
| **peça real** | `coleta/instagram_coleta.py`, `coleta/instagram_diario.py`, `coleta/instagram_janela.py`, `coleta/instagram_pessoal.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | INTELIGENCIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml:203; .github/workflows/sintonia-scrap.yml:203 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | V-HTTP, V-INSTAGRAM |
| **o que entra · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 9 · saem 8 |
| **arestas provadas** | entram 7 · saem 8 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 2 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 15 · NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-COLETA-PUBLICA` · Colher o que o concorrente publica

| | |
|---|---|
| **peça real** | `coleta/comunicacao_classificar.py`, `coleta/comunicacao_coleta.py`, `coleta/comunicacao_medir.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | DESENVOLVIMENTO_MERCADO · INTELIGENCIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 3 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-COLETA, C-ORQUESTRADOR |
| **prova de quem ativa** | .github/workflows/comunicacao-publica.yml:146; .github/workflows/comunicacao-publica.yml:147; pedido/receitas.py:277 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | V-FACEBOOK, V-INSTAGRAM, V-LINKEDIN |
| **o que entra · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/CLASSIFICADO-V1.json`, `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`, `data/samples/COMPETITOR-PUBLIC-COMM/MEDICAO-PRIMEIRO-LOTE-V1.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 12 · saem 6 |
| **arestas provadas** | entram 9 · saem 6 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 2 · saem 0 |
| **data plane** | entram 3 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 15 · NÃO SEI 3 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-COLETA-YOUTUBE` · Colher o YouTube

| | |
|---|---|
| **peça real** | `coleta/youtube_janela.py`, `coleta/youtube_relevancia.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | INTELIGENCIA · TECNICO_CIENCIA |
| **status operacional** | green — algum workflow ou a cadeia canonica manda rodar isto. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml:206; .github/workflows/sintonia-scrap.yml:207 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | V-HTTP, V-YOUTUBE |
| **o que entra · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 2 |
| **arestas provadas** | entram 4 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 2 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 6 · NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-CORPUS` · Montar o corpus de fala e de ciencia

| | |
|---|---|
| **peça real** | `coleta/corpus_pesquisador.py`, `coleta/es/corpus_es.py`, `coleta/sensor_canal_identidade.py`, `coleta/speaker_identidade.py`, `coleta/speaker_universo.py` _(e mais 1)_ |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | DESENVOLVIMENTO_MERCADO · TECNICO_CIENCIA |
| **status operacional** | yellow — existe, mas nada no repositorio manda rodar nem importa — pode estar desligado. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ORQUESTRADOR |
| **prova de quem ativa** | pedido/receitas.py:105; orquestrador/orquestrador.py:862 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | V-HTTP |
| **o que entra · ficheiros** | `data/samples/EXPERT-DIRECTORY-EAME-V1.json`, `data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json`, `data/samples/RESEARCHER-CORPUS-EAME-V1.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/EXPERT-DIRECTORY-EAME-V1.json`, `data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json`, `data/samples/RESEARCHER-CORPUS-EAME-V1.json` |
| **arestas no mapa** | entram 2 · saem 5 |
| **arestas provadas** | entram 1 · saem 5 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 1 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 6 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-DERIVACAO-FORWARD` · A fronteira forward da derivação

| | |
|---|---|
| **peça real** | `coleta/derivacao_forward.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ROTA-M2 |
| **prova de quem ativa** | tests/test_m2_rota_forward.py:1 _(plano OBSERVED)_ |
| **porquê** | uma corrida medida chamou esta peca — e nao so uma linha que diz que podia chamar. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-SCRAP-SOCIAL |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 7 · saem 13 |
| **arestas provadas** | entram 7 · saem 13 |
| **OBSERVADAS** | 2 — corrida `RUN-M2-E2E` |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 18 · OBSERVED 2 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

### `C-ESTRADA-PDF` · A primeira estrada · PDF até à porta

| | |
|---|---|
| **peça real** | `coleta/golden_path_pdf.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **EXTERNO_MANUAL** — EXTERNO |
| **prova de quem ativa** | system-map/scripts/CADEIA-DO-MAPA.json · PRODUTORES_EXTERNOS · coleta/golden_path_pdf.py _(plano DECLARED)_ |
| **porquê** | a cadeia declara esta peca como PRODUTOR EXTERNO: o mapa consome o que ela deixa e nao a corre. Quem a corre e gente. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `docs/biblia/leis.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 7 |
| **arestas provadas** | entram 6 · saem 7 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 13 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **EXTERNAL_ENTRY** — entrada legitima, e o mapa di-lo com a prova |

### `C-EU-REGULATORIO-COLETA` · Colher o ato regulatório da UE

| | |
|---|---|
| **peça real** | `coleta/eu_regulatorio_executor.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — existe, mas nada no repositorio manda rodar nem importa — pode estar desligado. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ORQUESTRADOR |
| **prova de quem ativa** | pedido/receitas.py:122; orquestrador/orquestrador.py:862 _(plano OBSERVED)_ |
| **porquê** | uma corrida medida chamou esta peca — e nao so uma linha que diz que podia chamar. |
| **o que entra · dado** | V-HTTP |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 3 |
| **arestas provadas** | entram 2 · saem 3 |
| **OBSERVADAS** | 1 — corrida `?` |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 1 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 4 · OBSERVED 1 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

### `C-EXECUTOR-TEXTO-PDF` · Executor · texto a partir de PDF

| | |
|---|---|
| **peça real** | `coleta/executor_texto_de_pdf.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | coleta/derivacao_forward.py:101; coleta/golden_path_pdf.py:53; medidas/corrida_instrumentada.py:122 |
| **porquê** | estas pecas importam-na — C-DERIVACAO-FORWARD · C-ESTRADA-PDF · C-FRONTEIRA-TELEMETRIA · C-ORQUESTRADOR — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | C-IT-PDF-BRUTO |
| **o que entra · ficheiros** | `data/derivados/REGISTO-DE-ARTEFATOS.json` |
| **o que sai · dado** | C-IT-TEXTO-DERIVADO |
| **o que sai · ficheiros** | `data/derivados/REGISTO-DE-ARTEFATOS.json` |
| **arestas no mapa** | entram 4 · saem 20 |
| **arestas provadas** | entram 3 · saem 19 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED YES · PROVEN YES _(no plano OBSERVED)_ |
| **prova das ligações** | CODE 22 · NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-EXECUTOR-TRANSCRICAO-MIDIA` · Executor · transcrição de mídia

| | |
|---|---|
| **peça real** | `coleta/executor_transcricao_midia.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-PROVA-ROTAS-REAIS, C-TESTES |
| **prova de quem ativa** | provas/a_ponte_de_midia_atravessa.py:46; tests/test_c4h_executor_de_midia.py:54; tests/test_c4h_executor_de_midia.py:60 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | C-TRANSCRICAO |
| **o que entra · ficheiros** | `ferramentas/fala_local.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 5 · saem 3 |
| **arestas provadas** | entram 5 · saem 3 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 1 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 8 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-FONTES-EU` · Ler as bases oficiais da Europa

| | |
|---|---|
| **peça real** | `coleta/agrifood_ue.py`, `coleta/cellar.sh`, `coleta/denominaciones.py`, `coleta/ephy.sh`, `coleta/eppo_gd.py` _(e mais 4)_ |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | REGULATORIO_PORTFOLIO · TECNICO_CIENCIA |
| **status operacional** | green — outra peca do sistema importa isto para funcionar. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ORQUESTRADOR |
| **prova de quem ativa** | pedido/receitas.py:236; orquestrador/orquestrador.py:862 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | V-HTTP |
| **o que entra · ficheiros** | `data/samples/ES-ADAMA-PORTFOLIO-ROPF.json`, `data/samples/IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json`, `supabase/importacoes/ES-REGULATORIO-ROPF-2026-08-29.sql` |
| **o que sai · dado** | C-SUPABASE |
| **o que sai · ficheiros** | `data/samples/IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json` |
| **arestas no mapa** | entram 4 · saem 8 |
| **arestas provadas** | entram 3 · saem 8 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 11 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-INGRESSO` · A porta de entrada da coleta

| | |
|---|---|
| **peça real** | `coleta/ingresso.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — esta no caminho: alguem o chama antes de publicar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | coleta/derivacao_forward.py:325; coleta/golden_path_pdf.py:51; coleta/rota_forward_documento.py:71 |
| **porquê** | estas pecas importam-na — C-DERIVACAO-FORWARD · C-ESTRADA-PDF · C-ORQUESTRADOR · C-ROTA-M2 — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `leis/artefato.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 17 |
| **arestas provadas** | entram 6 · saem 17 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 23 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-IT-COLETA` · Colher as fontes italianas

| | |
|---|---|
| **peça real** | `coleta/italy_executor.py`, `coleta/italy_find_docs.mjs`, `coleta/italy_pilot_collect.mjs`, `coleta/italy_probe.mjs`, `coleta/italy_recurrent_collect.mjs` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | INTELIGENCIA · TECNICO_CIENCIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 2 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ORQUESTRADOR |
| **prova de quem ativa** | pedido/receitas.py:170; orquestrador/orquestrador.py:862 _(plano OBSERVED)_ |
| **porquê** | uma corrida medida chamou esta peca — e nao so uma linha que diz que podia chamar. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `candidatas/ITALY-SOURCE-MASTER-V1.json`, `candidatas/italy_profiles.mjs`, `coleta/italy_pilot_collect.mjs` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 7 · saem 14 |
| **arestas provadas** | entram 6 · saem 13 |
| **OBSERVADAS** | 1 — corrida `?` |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 18 · NÃO SEI 2 · OBSERVED 1 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

### `C-ROTA-M2` · A rota forward do documento (M2)

| | |
|---|---|
| **peça real** | `coleta/rota_forward_documento.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-MAPA-TESTES, C-PROVA-COLETA, C-PROVA-ROTA-M2-ATRAVESSA, C-PROVA-ROTAS-REAIS, C-PROVA-SALA-DE-ESPERA-SEM-MORADA, C-PROVA-UNIDADE-POUSA-NA-ESPERA, C-TESTES |
| **prova de quem ativa** | provas/a_linhagem_do_ready.py:60; provas/a_ponte_de_midia_no_postgres.py:67; provas/a_rota_m2_atravessa.py:72 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 8 · saem 13 |
| **arestas provadas** | entram 8 · saem 13 |
| **OBSERVADAS** | 3 — corrida `RUN-M2-E2E` |
| **control plane** | entram 0 · saem 3 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED YES · PROVEN YES _(no plano OBSERVED)_ |
| **prova das ligações** | CODE 18 · OBSERVED 3 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-ROTULOS` · Baixar e ler os rotulos oficiais

| | |
|---|---|
| **peça real** | `coleta/cruzar_regua_rotulo.py`, `coleta/mapa_regfi.py`, `coleta/pdf_text.py`, `coleta/preservar_pdf.py`, `coleta/ropf_pre_requisito.py` _(e mais 2)_ |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | REGULATORIO_PORTFOLIO · TECNICO_CIENCIA |
| **status operacional** | green — outra peca do sistema importa isto para funcionar. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ORQUESTRADOR |
| **prova de quem ativa** | pedido/receitas.py:157; orquestrador/orquestrador.py:862 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | V-HTTP |
| **o que entra · ficheiros** | `build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/01-DESIGN-READY/ADAMA/adama-italy-products.json`, `data/raw/IT-ROTULOS/_MANIFESTO.json`, `data/samples/ES-ADAMA-PORTFOLIO-ROPF.json` |
| **o que sai · dado** | C-SUPABASE |
| **o que sai · ficheiros** | `data/raw/IT-ROTULOS/_MANIFESTO.json`, `data/samples/IT-CRUZAMENTO/IT-CONVERSA-X-ROTULO.json`, `data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json` |
| **arestas no mapa** | entram 4 · saem 11 |
| **arestas provadas** | entram 3 · saem 11 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 14 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-SCRAP-COLHEITA` · O adapter do SCRAP para a porta canonica · a aresta que faltava

| | |
|---|---|
| **peça real** | `coleta/scrap_colheita.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ORQUESTRADOR |
| **prova de quem ativa** | pedido/receitas.py:315; orquestrador/orquestrador.py:862 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 5 · saem 13 |
| **arestas provadas** | entram 5 · saem 13 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 18 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-SCRAP-SOCIAL` · SINTONIA SCRAP · o executor da aquisicao social

| | |
|---|---|
| **peça real** | `coleta/adaptador_aberto.py`, `coleta/adaptador_facebook.py`, `coleta/adaptador_instagram.py`, `coleta/adaptador_linkedin.py`, `coleta/adaptador_x.py` _(e mais 11)_ |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas ha 16 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ROTA-M2, C-SCRAP-EVIDENCIA, C-SCRAP-ROTA, C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/scrap-evidencia.yml:82; .github/workflows/scrap-social.yml:277; .github/workflows/scrap-social.yml:278 _(plano OBSERVED)_ |
| **porquê** | uma corrida medida chamou esta peca — e nao so uma linha que diz que podia chamar. |
| **o que entra · dado** | C-DERIVACAO-FORWARD, C-ORQUESTRADOR, C-TRANSCRICAO, V-HTTP, V-YOUTUBE |
| **o que entra · ficheiros** | `coleta/coleta_checkpoint.py`, `coleta/coletor.py`, `coleta/instagram_janela.py` |
| **o que sai · dado** | C-ADMISSAO |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 24 · saem 20 |
| **arestas provadas** | entram 21 · saem 20 |
| **OBSERVADAS** | 3 — corrida `RUN-M2-E2E` |
| **control plane** | entram 4 · saem 0 |
| **data plane** | entram 5 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 38 · OBSERVED 3 · NÃO SEI 3 |
| **lei da Bíblia** | COL-LAW-006/007 · RAW primeiro, e RAW nao e derivado |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

## Z-ADMISSAO · 4 · A PORTA DE ADMISSAO

### `C-ADMISSAO` · A porta de admissao

| | |
|---|---|
| **peça real** | `admissao/admissao.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — esta no caminho: alguem o chama antes de publicar.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-ROTA-M2 |
| **prova de quem ativa** | tests/test_m2_rota_forward.py:1 _(plano OBSERVED)_ |
| **porquê** | uma corrida medida chamou esta peca — e nao so uma linha que diz que podia chamar. |
| **o que entra · dado** | C-IT-TEXTO-DERIVADO, C-IT-TEXTO-PESQUISAVEL, C-SCRAP-SOCIAL |
| **o que entra · ficheiros** | `data/samples/LIVRO-DE-DECISOES.json` |
| **o que sai · dado** | C-READY |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 29 |
| **arestas provadas** | entram 4 · saem 28 |
| **OBSERVADAS** | 2 — corrida `RUN-M2-E2E` |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 3 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 30 · NÃO SEI 3 · OBSERVED 2 |
| **lei da Bíblia** | COL-LAW-042/043 · a admissao decide com prova, e READY nao e «o script terminou» |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

### `C-SALA-DE-ESPERA` · A Sala de Espera

| | |
|---|---|
| **peça real** | `admissao/sala_de_espera.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml:384 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-INT-ESPINHA |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 20 |
| **arestas provadas** | entram 3 · saem 19 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 22 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-042/043 · a admissao decide com prova, e READY nao e «o script terminou» |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

## Z-BIBLIA · 0 · A CONSTITUIÇÃO DA COLETA

### `C-BIBLIA` · A Bíblia canônica da coleta

| | |
|---|---|
| **peça real** | `BIBLIA-CANONICA-DA-COLETA.md`, `docs/biblia/CENSO-DA-INFRAESTRUTURA.md`, `docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md`, `docs/biblia/CONFORMIDADE-ITALIA.md`, `docs/biblia/EMENDA-V1-1.md` _(e mais 4)_ |
| **papel** | STORAGE · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | yellow — e uma lei sem prova executavel apontando para ela. |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | 9 ficheiro(s) e nenhum executavel: aqui guarda-se, nao se corre _(plano CODE)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 7 |
| **arestas provadas** | entram 1 · saem 7 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 8 |
| **lei da Bíblia** | COL-LAW-005 · COLETAR != ADMITIR != JULGAR |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

## Z-CANDIDATAS · de onde vem uma fonte

### `C-DECISAO-DA-FILA` · A decisao da fila de fontes

| | |
|---|---|
| **peça real** | `candidatas/ITALY-CONTRACT-CANDIDATES-2026-09-15.csv`, `candidatas/ITALY-SOURCE-DECISIONS-2026-09-15.csv`, `candidatas/decidir_fila_italia.py`, `candidatas/reconciliar_fichas_orfas.py`, `candidatas/xlsx_simples.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | INTELIGENCIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 5 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-TESTES |
| **prova de quem ativa** | tests/test_fila_italia_decisoes.py:33; tests/test_fila_italia_decisoes.py:303 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `candidatas/ITALY-CONTRACT-CANDIDATES-2026-09-15.csv`, `candidatas/ITALY-SOURCE-DECISIONS-2026-09-15.csv`, `candidatas/ITALY-SOURCE-DISCOVERY-2026-09-14.xlsx` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 4 · saem 2 |
| **arestas provadas** | entram 4 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 6 |
| **lei da Bíblia** | COL-LAW-053 · a fonte tem cadastro unico e reconciliado |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-IT-CATALOGO` · O levantamento das fontes italianas

| | |
|---|---|
| **peça real** | `candidatas/ITALY-SOURCE-MASTER-V1.json`, `candidatas/ITALY-SOURCE-MASTER-V1.md`, `candidatas/italy_fill_manifests.mjs`, `candidatas/italy_fill_manifests_browser.mjs`, `candidatas/italy_fix_semantics.mjs` _(e mais 3)_ |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | INTELIGENCIA · TECNICO_CIENCIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 2 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | candidatas/decidir_fila_italia.py:383; coleta/italy_probe.mjs:23; coleta/italy_recurrent_collect.mjs:29 |
| **porquê** | estas pecas importam-na — C-DECISAO-DA-FILA · C-FONTE-DO-ATLAS · C-IT-COLETA · C-IT-CONTRATOS — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `candidatas/ITALY-SOURCE-MASTER-V1.json`, `regras/italy_contracts.mjs`, `regras/italy_source_health.mjs` |
| **o que sai · dado** | C-IT-CONTRATOS |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 15 |
| **arestas provadas** | entram 1 · saem 15 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 16 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-053 · a fonte tem cadastro unico e reconciliado |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-PORTA-FONTE` · A porta de entrada de fonte nova

| | |
|---|---|
| **peça real** | `candidatas/FONTES-CANDIDATAS.json`, `candidatas/fonte_nova.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | INTELIGENCIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 2 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | candidatas/decidir_fila_italia.py:100; system-map/scripts/scan_sources.py:480; tests/test_fila_italia_decisoes.py:38 |
| **porquê** | estas pecas importam-na — C-DECISAO-DA-FILA — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `candidatas/FONTES-CANDIDATAS.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 3 |
| **arestas provadas** | entram 0 · saem 3 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 3 |
| **lei da Bíblia** | COL-LAW-053 · a fonte tem cadastro unico e reconciliado |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

## Z-ENTRADA · 1 · ENTRADA DE COLETA

### `C-CI-COLETA` · Os botoes que disparam a coleta

| | |
|---|---|
| **peça real** | `.github/workflows/apify-conexao.yml`, `.github/workflows/apify-sensores.yml`, `.github/workflows/comunicacao-publica.yml` |
| **papel** | DISPATCH_ENTRYPOINT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | green — este workflow manda rodar script do repositorio. |
| **QUEM ATIVA** | **EXTERNO_MANUAL** — EXTERNO |
| **prova de quem ativa** | .github/workflows/apify-conexao.yml · on: workflow_dispatch; .github/workflows/apify-sensores.yml · on: workflow_dispatch; .github/workflows/comunicacao-publica.yml · on: workflow_dispatch _(plano CODE)_ |
| **porquê** | o `on:` so tem `workflow_dispatch`: a unica porta e a mao de alguem. NENHUM orquestrador o dispara, e `workflow_dispatch` prova exactamente isso. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`, `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 6 |
| **arestas provadas** | entram 2 · saem 6 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 5 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 8 |
| **lei da Bíblia** | COL-LAW-010 · um pedido nao conhece implementacao |
| **VEREDITO** | **EXTERNAL_ENTRY** — entrada legitima, e o mapa di-lo com a prova |

## Z-EXECUCAO · 3 · IT · SCRAP — os botoes da aquisicao

### `C-SCRAP-EVIDENCIA` · SCRAP evidencia entre jobs · o bruto pago atravessa, ou nao atravessa

| | |
|---|---|
| **peça real** | `.github/workflows/scrap-evidencia.yml` |
| **papel** | DISPATCH_ENTRYPOINT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — este workflow manda rodar script do repositorio.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **EXTERNO_EVENTO** — EXTERNO |
| **prova de quem ativa** | .github/workflows/scrap-evidencia.yml · on: push, workflow_dispatch _(plano CODE)_ |
| **porquê** | um acontecimento do repositorio acorda este botao. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 3 |
| **arestas provadas** | entram 0 · saem 3 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 1 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 3 |
| **lei da Bíblia** | COL-LAW-013/014 · contrato comum do executor e capacidades declaradas |
| **VEREDITO** | **EXTERNAL_ENTRY** — entrada legitima, e o mapa di-lo com a prova |

### `C-SCRAP-ROTA` · SCRAP rota e sessao · o despachador (auth_mode)

| | |
|---|---|
| **peça real** | `.github/workflows/scrap-social.yml` |
| **papel** | DISPATCH_ENTRYPOINT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — este workflow manda rodar script do repositorio.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **EXTERNO_MANUAL** — EXTERNO |
| **prova de quem ativa** | .github/workflows/scrap-social.yml · on: workflow_dispatch _(plano CODE)_ |
| **porquê** | o `on:` so tem `workflow_dispatch`: a unica porta e a mao de alguem. NENHUM orquestrador o dispara, e `workflow_dispatch` prova exactamente isso. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/SOCIAL-IT/YOUTUBE-PILOTO-IT.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 5 |
| **arestas provadas** | entram 1 · saem 5 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 4 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 6 |
| **lei da Bíblia** | COL-LAW-013/014 · contrato comum do executor e capacidades declaradas |
| **VEREDITO** | **EXTERNAL_ENTRY** — entrada legitima, e o mapa di-lo com a prova |

### `C-SINTONIA-SCRAP` · SCRAP aquisicao · o despachador (Instagram, YouTube)

| | |
|---|---|
| **peça real** | `.github/workflows/sintonia-scrap.yml` |
| **papel** | DISPATCH_ENTRYPOINT · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | yellow — este workflow manda rodar script do repositorio.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **EXTERNO_MANUAL** — EXTERNO |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml · on: workflow_dispatch _(plano CODE)_ |
| **porquê** | o `on:` so tem `workflow_dispatch`: a unica porta e a mao de alguem. NENHUM orquestrador o dispara, e `workflow_dispatch` prova exactamente isso. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 13 |
| **arestas provadas** | entram 1 · saem 13 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 11 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 14 |
| **lei da Bíblia** | COL-LAW-013/014 · contrato comum do executor e capacidades declaradas |
| **VEREDITO** | **EXTERNAL_ENTRY** — entrada legitima, e o mapa di-lo com a prova |

## Z-FERRAMENTAS · as ferramentas da execucao

### `C-APIFY-POOL` · Apify — a rota paga

| | |
|---|---|
| **peça real** | `ferramentas/apify_pool.py`, `ferramentas/contrato_ator.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outras pecas importam ou carregam isto.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-COLETA, C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/apify-conexao.yml:68; .github/workflows/apify-sensores.yml:117; .github/workflows/sintonia-scrap.yml:206 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 4 · saem 12 |
| **arestas provadas** | entram 4 · saem 8 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 2 · saem 4 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 12 · NÃO SEI 4 |
| **lei da Bíblia** | COL-LAW-013 · contrato comum do executor |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-LEITORES` · Abrir PDF, ODS e HTML

| | |
|---|---|
| **peça real** | `ferramentas/html_text.mjs`, `ferramentas/italy-forward-only-live.cmd`, `ferramentas/italy_extract_fields.mjs`, `ferramentas/ods_peek.mjs`, `ferramentas/pdf_peek.mjs` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | green — outras pecas importam ou carregam isto. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | regras/italy_source_health.mjs:38; system-map/scripts/censo_das_derivacoes.py:121 |
| **porquê** | estas pecas importam-na — C-IT-CONTRATOS — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/ITALY-T3-005-MONITORAGGIO/points-2026-09-07.json`, `ferramentas/ods_peek.mjs` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 2 |
| **arestas provadas** | entram 0 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 2 |
| **lei da Bíblia** | COL-LAW-013 · contrato comum do executor |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-NAVEGADOR` · O navegador — a rota gratis

| | |
|---|---|
| **peça real** | `ferramentas/cdp.py`, `ferramentas/navegador.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outras pecas importam ou carregam isto.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml:205; .github/workflows/sintonia-scrap.yml:205 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 8 |
| **arestas provadas** | entram 1 · saem 6 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 2 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 7 · NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-013 · contrato comum do executor |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-TRANSCRICAO` · A fala vira texto, sem fatura

| | |
|---|---|
| **peça real** | `ferramentas/fala_local.py`, `ferramentas/instagram_transcrever.py`, `ferramentas/reel_transcricao.py`, `ferramentas/youtube_transcrever.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA · TECNICO_CIENCIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 2 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/sintonia-scrap.yml:207 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/REEL-TRANSCRICOES/TRANSCRICOES-REEL.json`, `ferramentas/fala_local.py` |
| **o que sai · dado** | C-EXECUTOR-TRANSCRICAO-MIDIA, C-SCRAP-SOCIAL |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 14 |
| **arestas provadas** | entram 3 · saem 14 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 2 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 17 |
| **lei da Bíblia** | COL-LAW-013 · contrato comum do executor |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

## Z-FONTES · as fontes

### `C-ADAMA-IT` · O que a ADAMA sabe de si

| | |
|---|---|
| **peça real** | `fontes/adama_catalogo_ler.py`, `fontes/adama_catalogo_montar.py`, `fontes/adama_catalogo_snapshot.py`, `fontes/adama_it_eu.py`, `fontes/adama_it_frac.py` _(e mais 6)_ |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | REGULATORIO_PORTFOLIO · TECNICO_CIENCIA |
| **status operacional** | yellow — so peca de prova a importa. NENHUM modulo de runtime a importa (DECLARED_RULE_NOT_ENFORCED).  Mas ha 2 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | motor/v21_ingest.py:266; pacote/lastmile_entregar.py:65; provas/consumo_da_referencia_adama.py:60 |
| **porquê** | estas pecas importam-na — C-LASTMILE · C-V21-INGEST — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/01-DESIGN-READY/ADAMA/adama-italy-products.json`, `data/samples/IT-ADAMA-CATALOG/2026-09-15/catalog-enumeration.json`, `data/samples/IT-ADAMA-CATALOG/2026-09-15/catalog-page-manifest.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/IT-LASTMILE/IT-ADAMA-CATALOGO.json`, `research/adama-italy-product-intelligence-deep/EU-SOURCE-540-2011.json`, `research/adama-italy-product-intelligence-deep/MOA-SOURCE-FRAC.json` |
| **arestas no mapa** | entram 1 · saem 4 |
| **arestas provadas** | entram 1 · saem 4 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 5 |
| **lei da Bíblia** | COL-LAW-009 · fonte, endpoint, rota, executor, item e artefato sao seis coisas |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-AS-FONTES` · AS FONTES

| | |
|---|---|
| **peça real** | `docs/fontes/ATLAS-DE-FONTES-EAME.md`, `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`, `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json` |
| **papel** | STORAGE · medido no plano CODE |
| **dono** | UNKNOWN |
| **status operacional** | yellow — 210 bases oficiais com ficha e 44 contas publicas mapeadas. Mas so 5 das bases tem contrato de busca escrito: nas outras 205, hoje so uma pessoa consegue ir la  |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | 3 ficheiro(s) e nenhum executavel: aqui guarda-se, nao se corre _(plano CODE)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | V-FACEBOOK, V-INSTAGRAM, V-LINKEDIN, V-YOUTUBE |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 19 |
| **arestas provadas** | entram 0 · saem 15 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 4 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 15 · NÃO SEI 4 |
| **lei da Bíblia** | COL-LAW-009 · fonte, endpoint, rota, executor, item e artefato sao seis coisas |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

## Z-GUARDA · A SALA DE ESPERA

### `C-ADAMA-ES` · O portao do catalogo espanhol · projeto futuro

| | |
|---|---|
| **peça real** | `guarda/es/adama_es_gate.py`, `guarda/es/adama_es_import_rules.py`, `guarda/es/workflows/adama-es-gate.yml` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | REGULATORIO_PORTFOLIO |
| **status operacional** | yellow — portao que ninguem chama. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-PROVA-COLETA, C-TESTES |
| **prova de quem ativa** | provas/testa_coleta_canonica.py:134; tests/es/test_adama_es_gate.py:21 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/ADAMA-ES-HANDOFF-GATE-V1.json`, `data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json`, `data/samples/CAPTURE-VS-REGISTRATION-CONTRACT-V1.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/ADAMA-ES-HANDOFF-GATE-V1.json` |
| **arestas no mapa** | entram 1 · saem 2 |
| **arestas provadas** | entram 1 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 3 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-ARMAZEM-IT-SEM-LIVRO` · Armazém italiano no Supabase (sem livro de entrada)

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | STORAGE · medido no plano DECLARED |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — AMARELO, e não verde, de propósito. Os 195 objetos estão preservados — e um armazém cheio com o livro de entrada em branco PARECE saúde e é o contrário. Enquant |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | declarado `kind: acervo` em architecture.declared.json — nenhum ficheiro medido sustenta ou contradiz isto _(plano DECLARED)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 0 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** |  |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **ALVO_SEM_ESCRITOR_MEDIDO** — alvo declarado e explicado; nenhuma aresta medida o enche — quem lá escreve escreve em SQL, e o scanner mede ficheiros |

### `C-CI-PERSIST` · Os botoes que cuidam do banco

| | |
|---|---|
| **peça real** | `.github/workflows/auditoria-live.yml`, `.github/workflows/banco-descartavel.yml`, `.github/workflows/supabase-conexao.yml`, `.github/workflows/supabase-migrate.yml`, `.github/workflows/supabase-storage.yml` |
| **papel** | DISPATCH_ENTRYPOINT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — este workflow manda rodar script do repositorio.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **EXTERNO_EVENTO** — EXTERNO |
| **prova de quem ativa** | .github/workflows/auditoria-live.yml · on: push, workflow_dispatch; .github/workflows/banco-descartavel.yml · on: push, workflow_dispatch; .github/workflows/supabase-conexao.yml · on: push, workflow_dispatch _(plano CODE)_ |
| **porquê** | um acontecimento do repositorio acorda este botao. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `supabase/migrations/008_verificacao_pos_aplicacao.sql`, `supabase/tests/regressoes_catalogo_es.sql`, `supabase/tests/regressoes_regulatorio_es.sql` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 14 |
| **arestas provadas** | entram 2 · saem 14 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 11 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 16 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **EXTERNAL_ENTRY** — entrada legitima, e o mapa di-lo com a prova |

### `C-DERIVED-ARTIFACT` · ALVO · a casa do derivado (migration 022)

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | STORAGE · medido no plano DECLARED |
| **dono** | ENGENHARIA |
| **status operacional** | green — VERDE porque a 022 foi APLICADA em producao e o esquema foi lido de volta objeto a objeto, e porque um produtor real escreveu a primeira linha — uma captura ita |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | declarado `kind: acervo` em architecture.declared.json — nenhum ficheiro medido sustenta ou contradiz isto _(plano DECLARED)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 0 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** |  |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **ALVO_SEM_ESCRITOR_MEDIDO** — alvo declarado e explicado; nenhuma aresta medida o enche — quem lá escreve escreve em SQL, e o scanner mede ficheiros |

### `C-DONO-DA-ESCRITA` · O dono canônico da escrita do bruto (OBSERVED)

| | |
|---|---|
| **peça real** | `guarda/banco_descartavel.py`, `guarda/banco_operacional.py`, `guarda/cliente_postgres.py`, `guarda/memoria_descartavel.py`, `guarda/memoria_postgres.py` _(e mais 2)_ |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 3 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | admissao/admissao.py:73; admissao/sala_de_espera.py:89; coleta/coleta_checkpoint.py:46 |
| **porquê** | estas pecas importam-na — C-ADMISSAO · C-COLETA-BASE · C-DONO-DO-DERIVADO · C-INGRESSO · C-PERSISTENCIA-DA-PORTA-CLI — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 23 |
| **arestas provadas** | entram 1 · saem 23 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 24 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-DONO-DO-DERIVADO` · O dono canônico da escrita do derivado (OBSERVED)

| | |
|---|---|
| **peça real** | `guarda/preservar_derivado.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | coleta/executor_texto_de_pdf.py:299; coleta/executor_transcricao_midia.py:303; guarda/memoria_descartavel.py:43 |
| **porquê** | estas pecas importam-na — C-DONO-DA-ESCRITA · C-EXECUTOR-TEXTO-PDF · C-EXECUTOR-TRANSCRICAO-MIDIA — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 7 |
| **arestas provadas** | entram 1 · saem 7 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 8 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-DONO-DO-DOCUMENTO` · O dono canônico do documento estruturado (OBSERVED)

| | |
|---|---|
| **peça real** | `guarda/preservar_documento.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — existe, mas nada no repositorio manda rodar nem importa — pode estar desligado. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | orquestrador/orquestrador.py:512 |
| **porquê** | estas pecas importam-na — C-ORQUESTRADOR — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 1 |
| **arestas provadas** | entram 0 · saem 1 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 1 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-IMPORTAR` · Levar o dado para o banco

| | |
|---|---|
| **peça real** | `guarda/catalogo_importar.py`, `guarda/importar_italia.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-REGRESSAO |
| **prova de quem ativa** | .github/workflows/calendario-regressoes.yml:235 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/ADAMA-ES-CONFIRMACAO-REGULATORIA-DO-PAR.json`, `data/samples/ADAMA-ES-PRESERVACAO-PLANO.json`, `data/samples/ADAMA-ES-PRESERVACAO-RELATORIO.json` |
| **o que sai · dado** | C-SUPABASE |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 4 |
| **arestas provadas** | entram 3 · saem 4 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 7 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-IT-PDF-BRUTO` · Evidência bruta em PDF (Itália)

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | STORAGE · medido no plano DECLARED |
| **dono** | ENGENHARIA |
| **status operacional** | gray — CINZENTO porque o mapa continua a não conseguir LER um PDF — o scanner não abre ficheiro binário, e isso não mudou. O que mudou é que já não precisa: o executor |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | declarado `kind: acervo` em architecture.declared.json — nenhum ficheiro medido sustenta ou contradiz isto _(plano DECLARED)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-EXECUTOR-TEXTO-PDF, C-IT-TEXTO-PESQUISAVEL |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 2 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 2 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

### `C-IT-PRESERVAR` · Guardar com impressao digital

| | |
|---|---|
| **peça real** | `data/collection-ledger/italy/observations.ndjson`, `data/collection-ledger/italy/runs.ndjson`, `guarda/italy_preserve.mjs` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — existe, mas nada no repositorio manda rodar nem importa — pode estar desligado. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | coleta/italy_executor.py:87; medidas/padrao_da_coleta.py:65; provas/a_collection_preserva_o_fato.py:85 |
| **porquê** | estas pecas importam-na — C-IT-COLETA · C-IT-CONTRATOS · C-PADRAO-COLETA · C-RELATORIO-FLUXO — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `superficie/rede.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 13 |
| **arestas provadas** | entram 1 · saem 13 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 14 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-IT-TEXTO-DERIVADO` · Texto derivado, com pai

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | green — Cada artefato tem nome próprio, impressão digital, pai, impressão digital do pai e versão de quem o fez. Perdidos: 0. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | — NÃO SEI |
| **porquê** | nenhuma peca do mapa a manda correr com prova, e ela nao e botao, nem produtor externo declarado, nem contrato, nem canal. UNKNOWN nao e NAO: pode haver quem a chame por um caminho que o mapa ainda nao mede. |
| **o que entra · dado** | C-EXECUTOR-TEXTO-PDF |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-ADMISSAO |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 1 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-IT-TEXTO-PESQUISAVEL` · O texto que a máquina consegue ler

| | |
|---|---|
| **peça real** | `data/samples/IT-ARPAV-VENETO/boll.txt`, `data/samples/IT-ARPAV-VENETO/fe.txt`, `data/samples/IT-ARPAV-VENETO/frutticolo_24_260826.txt`, `data/samples/IT-ARPAV-VENETO/lug_full.txt`, `data/samples/IT-ARPAV-VENETO/olivicolo_29_020926.txt` _(e mais 15)_ |
| **papel** | STORAGE · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | gray — ⚪ NAO SEI. Os ficheiros existem, mas nada no repositorio aponta para eles e eles nao apontam para nada. Nao da para provar o que isto faz hoje. |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | 20 ficheiro(s) e nenhum executavel: aqui guarda-se, nao se corre _(plano CODE)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | C-IT-PDF-BRUTO |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-ADMISSAO |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 1 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | NÃO SEI 2 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

### `C-SCRAP-GUARDA` · A guarda de credencial e de sessao do SCRAP

| | |
|---|---|
| **peça real** | `guarda/social_guarda.py`, `guarda/social_sessao.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — esta no caminho: alguem o chama antes de publicar.  Mas ha 2 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-SCRAP-ROTA, C-SECURITY-CHECK |
| **prova de quem ativa** | .github/workflows/scrap-social.yml:277; .github/workflows/security-check.yml:58 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `coleta/instagram_janela.py`, `docs/operacao/HOW-TO-PROVISION-LOCAL-SESSION.md`, `guarda/social_sessao.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 6 |
| **arestas provadas** | entram 6 · saem 6 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 2 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 12 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-SUPABASE` · O banco onde o dado fica guardado

| | |
|---|---|
| **peça real** | `guarda/sql_conferir.py`, `supabase/consultas/ADAMA-ES-CATALOGO-14-PERGUNTAS.sql`, `supabase/ensaios/ADAMA-ES-ENSAIO-CINCO-CASOS.sql`, `supabase/ensaios/CAPTURA-AS-OF-DUAS-CAPTURAS.sql`, `supabase/ensaios/CICATRIZES-LOCALIZACAO-E-RELEVANCIA.sql` _(e mais 49)_ |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas ha 10 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CADEIA-V21 |
| **prova de quem ativa** | motor/cadeia_canonica.sh:205 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 4 · saem 16 |
| **arestas provadas** | entram 4 · saem 16 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 20 |
| **lei da Bíblia** | COL-LAW-044 · armazenamento nao e estado logico |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

## Z-MEDIDAS · as medidas da coleta

### `C-BANCO-NO-SECO` · O banco a seco

| | |
|---|---|
| **peça real** | `medidas/banco_no_seco.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-PROVA-EXECUTOR-CONTA, C-TESTES |
| **prova de quem ativa** | provas/o_executor_conta_se.py:36; tests/test_forward_instrumentado.py:28 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `supabase/migrations/024_a_corrida_conta_o_que_passou.sql` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 2 |
| **arestas provadas** | entram 1 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 3 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-CENSO-EXECUTORES` · Censo dos executores — caminhos, papeis e cobertura

| | |
|---|---|
| **peça real** | `system-map/data/provas-de-execucao.json`, `system-map/scripts/censo_dos_executores.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — existe teste que exercita isto.  Mas ha 2 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-CENSO-CARDS-SENSORES, C-CENSO-DOS-BURACOS, C-MAPA-GERADOR, C-PROVA-COLETA, C-PROVA-ROTA-M2-ATRAVESSA, C-TESTES |
| **prova de quem ativa** | provas/a_rota_m2_atravessa.py:121; provas/os_portoes_da_collection.py:47; system-map/scripts/censo_cards_sensores.py:140 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `provas/a_rota_m2_atravessa.py`, `provas/paridade_da_lingua.py`, `system-map/data/provas-de-execucao.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 6 |
| **arestas provadas** | entram 3 · saem 6 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 9 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-CENSO-OBSERVABILIDADE` · Censo da observabilidade

| | |
|---|---|
| **peça real** | `system-map/scripts/censo_da_observabilidade.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — existe, mas nada no repositorio manda rodar nem importa — pode estar desligado. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-PROVA-COLETA, C-TESTES |
| **prova de quem ativa** | provas/paridade_da_lingua.py:220; tests/test_lingua_unica.py:73 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `leis/evolucao.py`, `leis/gestao_da_coleta.py`, `provas/o_executor_conta_se.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 9 · saem 2 |
| **arestas provadas** | entram 9 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 11 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-CICATRIZES-BR` · Cicatrizes do Brasil (lei portada)

| | |
|---|---|
| **peça real** | `medidas/cicatrizes_brasil.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | green — o sistema importa esta lei em runtime para decidir: C-REGRA-COLETA. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | medidas/portoes_eame.py:41; medidas/portoes_eame.py:296; tests/test_cicatrizes_brasil.py:21 |
| **porquê** | estas pecas importam-na — C-REGRA-COLETA — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/BRAZIL-LESSONS-TRANSFER-EAME.json`, `regras/proveniencia.py`, `tests/test_operacao.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/BRAZIL-LESSONS-TRANSFER-EAME.json` |
| **arestas no mapa** | entram 2 · saem 4 |
| **arestas provadas** | entram 2 · saem 4 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 6 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-CONTRATO-CAMPOS` · O que a coleta tem de trazer

| | |
|---|---|
| **peça real** | `medidas/voz.py` |
| **papel** | CONTRACT_OR_RULE · medido no plano CODE |
| **dono** | DESENVOLVIMENTO_MERCADO · TECNICO_CIENCIA |
| **status operacional** | green — o sistema importa esta lei em runtime para decidir: C-REGRA-COLETA. |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | rule_role medido: nao le nem escreve artefato: enuncia vocabulario ou contrato _(plano CODE)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 2 |
| **arestas provadas** | entram 0 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 2 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

### `C-FRONTEIRA-TELEMETRIA` · A fronteira instrumentada

| | |
|---|---|
| **peça real** | `medidas/corrida_instrumentada.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-TESTES |
| **prova de quem ativa** | tests/test_o10r_a_verdade_dos_nomes.py:25; tests/test_o10r_a_verdade_dos_nomes.py:329 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `coleta/executor_texto_de_pdf.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 2 |
| **arestas provadas** | entram 6 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 8 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-PADRAO-COLETA` · O padrao do departamento de coleta

| | |
|---|---|
| **peça real** | `medidas/PADRAO-DA-COLETA-CHAO.json`, `medidas/padrao_da_coleta.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | green — esta no caminho: alguem o chama antes de publicar. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-MAPA |
| **prova de quem ativa** | .github/workflows/system-map.yml:544 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/collection-ledger/italy/observations.ndjson`, `data/collection-ledger/italy/runs.ndjson`, `data/samples/RUN-MANIFEST.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 4 · saem 1 |
| **arestas provadas** | entram 4 · saem 1 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 5 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-RASTRO` · O rastro da coleta — etapa, aresta, contagem e falha

| | |
|---|---|
| **peça real** | `medidas/rastro_da_coleta.py`, `medidas/scanner_da_coleta.py` |
| **papel** | CONTRACT_OR_RULE · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 2 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | rule_role medido: nao le nem escreve artefato: enuncia vocabulario ou contrato _(plano CODE)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 5 · saem 14 |
| **arestas provadas** | entram 5 · saem 14 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 19 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

### `C-REGRA-COLETA` · A regra de coleta externa

| | |
|---|---|
| **peça real** | `medidas/PORTOES-DE-COLETA-10B.md`, `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md`, `medidas/portao.py`, `medidas/portoes_eame.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | INTELIGENCIA · TECNICO_CIENCIA |
| **status operacional** | yellow — so peca de prova a importa. NENHUM modulo de runtime a importa (DECLARED_RULE_NOT_ENFORCED).  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-TESTES |
| **prova de quem ativa** | tests/test_coleta_externa.py:41; tests/test_portao.py:12 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `.github/workflows/supabase-migrate.yml`, `coleta/regulatorio_importar.py`, `data/samples/DATA-CLOCK-manifest.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/PORTOES-EAME.json` |
| **arestas no mapa** | entram 11 · saem 2 |
| **arestas provadas** | entram 11 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 13 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

### `C-RELATORIO-FLUXO` · Relatório do fluxo

| | |
|---|---|
| **peça real** | `system-map/scripts/relatorio_do_fluxo.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — existe, mas nada no repositorio manda rodar nem importa — pode estar desligado. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | — NÃO SEI |
| **porquê** | nenhuma peca do mapa a manda correr com prova, e ela nao e botao, nem produtor externo declarado, nem contrato, nem canal. UNKNOWN nao e NAO: pode haver quem a chame por um caminho que o mapa ainda nao mede. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/collection-ledger/italy/observations.ndjson`, `data/collection-ledger/italy/runs.ndjson` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 0 |
| **arestas provadas** | entram 2 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 2 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **TERMINAL** — saida terminal neste escopo |

### `C-SAUDE-FONTE` · A saude de cada fonte

| | |
|---|---|
| **peça real** | `medidas/source_health.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | green — so peca de prova a importa. NENHUM modulo de runtime a importa (DECLARED_RULE_NOT_ENFORCED). |
| **QUEM ATIVA** | **SO_A_PROVA_A_CORRE** — C-RECORRENCIA, C-TESTES |
| **prova de quem ativa** | provas/chain.py:43; tests/test_falhas.py:22 _(plano CODE)_ |
| **porquê** | na coleta, NINGUEM a manda correr: quem a abre vive todo em Z-PROVA — provas e instrumentos de medicao. A peca esta construida e medida, e nao esta no caminho de coleta nenhuma. UMA PORTA POR ONDE SO PASSA QUEM A VEIO MEDIR AINDA NAO E UMA PORTA. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/DATA-CLOCK-manifest.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 2 |
| **arestas provadas** | entram 1 · saem 2 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 3 |
| **lei da Bíblia** | COL-LAW-028/029 · a fonte tem saude, e o drift tem controlo negativo |
| **VEREDITO** | **SYSTEM_GAP** — construida e medida; na coleta ninguem a corre |

## Z-ORQUESTRADOR · 2 · ORQUESTRADOR

### `C-ORQUESTRADOR` · O orquestrador

| | |
|---|---|
| **peça real** | `orquestrador/orquestrador.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-COLETA, C-PEDIDO, C-SINTONIA-SCRAP |
| **prova de quem ativa** | .github/workflows/comunicacao-publica.yml:139; .github/workflows/sintonia-scrap.yml:471; system-map/data/pedido-t4.observado.json:1 _(plano OBSERVED)_ |
| **porquê** | uma corrida medida chamou esta peca — e nao so uma linha que diz que podia chamar. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `coleta/executor_texto_de_pdf.py`, `guarda/preservar_documento.py` |
| **o que sai · dado** | C-SCRAP-SOCIAL |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 15 · saem 25 |
| **arestas provadas** | entram 15 · saem 24 |
| **OBSERVADAS** | 3 — corrida `?` |
| **control plane** | entram 3 · saem 7 |
| **data plane** | entram 0 · saem 1 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 36 · OBSERVED 3 · NÃO SEI 1 |
| **lei da Bíblia** | COL-LAW-011/012 · um dono da orquestracao; ele controla e nao transporta dado |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

### `C-PERSISTENCIA-DA-PORTA-CLI` · A composicao da persistencia na porta CLI · a aresta que o workflow nao tinha

| | |
|---|---|
| **peça real** | `orquestrador/persistencia.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas ha 1 ficheiro(s) novos que nunca foram lidos por gente. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | orquestrador/orquestrador.py:62; tests/test_a_porta_cli_liga_o_banco.py:42; tests/test_a_porta_cli_liga_o_banco.py:211 |
| **porquê** | estas pecas importam-na — C-ORQUESTRADOR — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 3 |
| **arestas provadas** | entram 2 · saem 3 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 5 |
| **lei da Bíblia** | COL-LAW-011/012 · um dono da orquestracao; ele controla e nao transporta dado |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

## Z-PEDIDO · PEDIDO — o contrato

### `C-PEDIDO` · O pedido de coleta

| | |
|---|---|
| **peça real** | `pedido/pedido.py` |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — o sistema importa esta lei em runtime para decidir: C-ORQUESTRADOR, C-RECEITAS.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | orquestrador/orquestrador.py:53; pedido/receitas.py:46; provas/a_fonte_t4_italiana_atravessa.py:71 |
| **porquê** | estas pecas importam-na — C-ORQUESTRADOR · C-RECEITAS — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 10 |
| **arestas provadas** | entram 1 · saem 10 |
| **OBSERVADAS** | 1 — corrida `?` |
| **control plane** | entram 0 · saem 1 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 10 · OBSERVED 1 |
| **lei da Bíblia** | COL-LAW-010 · um pedido nao conhece implementacao |
| **VEREDITO** | **OK** — travessia OBSERVADA numa corrida real |

### `C-RECEITAS` · A receita da coleta

| | |
|---|---|
| **peça real** | `pedido/receitas.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA |
| **status operacional** | yellow — outra peca do sistema importa isto para funcionar.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | orquestrador/orquestrador.py:54; provas/a_corrida_existe_em_cada_rota.py:49; provas/a_maquina_depois_do_crash.py:51 |
| **porquê** | estas pecas importam-na — C-ORQUESTRADOR — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `coleta/comunicacao_coleta.py`, `coleta/corpus_pesquisador.py`, `coleta/eppo_gd.py` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 14 · saem 11 |
| **arestas provadas** | entram 14 · saem 11 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 25 |
| **lei da Bíblia** | COL-LAW-010 · um pedido nao conhece implementacao |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

## Z-REFERENCIA · a referência da ADAMA

### `C-ADAMA-REFERENCE` · A referencia da ADAMA, com um dono so

| | |
|---|---|
| **peça real** | `referencia/adama/ACTIVE-INGREDIENTS.json`, `referencia/adama/AUTHORIZED-USES.json`, `referencia/adama/CATALOG-SNAPSHOTS.json`, `referencia/adama/CONTRATO-ADAMA-REFERENCE.md`, `referencia/adama/DOSES.json` _(e mais 10)_ |
| **papel** | STORAGE · medido no plano CODE |
| **dono** | REGULATORIO_PORTFOLIO · INTELIGENCIA |
| **status operacional** | yellow — existe teste que exercita esta lei. NENHUM modulo de runtime a importa — a lei esta escrita e nao esta a ser aplicada (DECLARED_RULE_NOT_ENFORCED).  Mas ha 15 f |
| **QUEM ATIVA** | **NAO_SE_ATIVA** |
| **prova de quem ativa** | 15 ficheiro(s) e nenhum executavel: aqui guarda-se, nao se corre _(plano CODE)_ |
| **porquê** | esta peca nao corre: e consultada. Perguntar quem a ativa e perguntar quem acende um livro. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 1 · saem 10 |
| **arestas provadas** | entram 1 · saem 10 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 11 |
| **lei da Bíblia** | NÃO SEI |
| **VEREDITO** | **OK** — contrato ou acervo: consulta-se, nao corre |

## Z-REGRAS · as reguas que carimbam

### `C-IDENTIDADE` · Quem esta autorizado a ser coletado

| | |
|---|---|
| **peça real** | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json`, `regras/comunicacao_identidade.py`, `regras/comunicacao_lote.py`, `regras/comunicacao_universo.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | yellow — so peca de prova a importa. NENHUM modulo de runtime a importa (DECLARED_RULE_NOT_ENFORCED).  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-COLETA |
| **prova de quem ativa** | .github/workflows/comunicacao-publica.yml:104 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/ANCORAS-EVIDENCIA-V1.json`, `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`, `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/COMPETITOR-PUBLIC-COMM/UNIVERSO-CONTAS-V1.json` |
| **arestas no mapa** | entram 2 · saem 8 |
| **arestas provadas** | entram 2 · saem 8 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 10 |
| **lei da Bíblia** | COL-LAW-031/032/033/034 · tempo, geografia, procedencia, identidade |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

### `C-IT-CONTRATOS` · O contrato de cada fonte italiana

| | |
|---|---|
| **peça real** | `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md`, `regras/contratos_de_fonte.py`, `regras/italy_contract_test.mjs`, `regras/italy_contracts.mjs`, `regras/italy_pilot_guards.mjs` _(e mais 2)_ |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | yellow — o sistema importa esta lei em runtime para decidir: C-IT-CATALOGO, C-IT-COLETA.  Mas 4 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | candidatas/italy_write_matrix.mjs:2; coleta/italy_pilot_collect.mjs:38; provas/a_autoridade_da_fonte.py:163 |
| **porquê** | estas pecas importam-na — C-IT-CATALOGO · C-IT-COLETA — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `candidatas/ITALY-SOURCE-MASTER-V1.json`, `candidatas/italy_profiles.mjs`, `coleta/italy_pilot_collect.mjs` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 8 · saem 8 |
| **arestas provadas** | entram 8 · saem 5 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 13 · NÃO SEI 3 |
| **lei da Bíblia** | COL-LAW-031/032/033/034 · tempo, geografia, procedencia, identidade |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-PALAVRAS` · As palavras que a busca digita

| | |
|---|---|
| **peça real** | `regras/rotulos_censo.py`, `regras/sensor_medir.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | DESENVOLVIMENTO_MERCADO · TECNICO_CIENCIA |
| **status operacional** | yellow — o sistema importa esta lei em runtime para decidir: C-COLETA-YOUTUBE, C-RELEVANCIA.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precis |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | coleta/youtube_relevancia.py:75; leis/regua_italia.py:57; motor/pacote_convergencia.py:101 |
| **porquê** | estas pecas importam-na — C-COLETA-YOUTUBE · C-INT-CONVERGENCIA · C-RELEVANCIA — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/raw/IT-ROTULOS/_MANIFESTO.json`, `data/samples/IT-ROTULOS/IT-CENSO-DE-TERMOS.json`, `data/samples/SENSOR-PILOT/CANAL-IDENTIDADE.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/IT-ROTULOS/IT-CENSO-DE-TERMOS.json` |
| **arestas no mapa** | entram 3 · saem 7 |
| **arestas provadas** | entram 3 · saem 7 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 10 |
| **lei da Bíblia** | COL-LAW-031/032/033/034 · tempo, geografia, procedencia, identidade |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-PROCEDENCIA` · De onde veio — carimbado na coleta

| | |
|---|---|
| **peça real** | `regras/proveniencia.py` |
| **papel** | OPERATIONAL_STEP · medido no plano CODE |
| **dono** | ENGENHARIA · INTELIGENCIA |
| **status operacional** | yellow — o sistema importa esta lei em runtime para decidir: C-COLETA-BASE, C-COLETA-INSTAGRAM, C-ESTRADA-PDF, C-EXECUTOR-TRANSCRICAO-MIDIA.  Mas 1 ficheiro(s) mudaram d |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | coleta/coletor.py:76; coleta/executor_transcricao_midia.py:72; coleta/golden_path_pdf.py:52 |
| **porquê** | estas pecas importam-na — C-CICATRIZES-BR · C-COLETA-BASE · C-COLETA-INSTAGRAM · C-DATA-CLOCK · C-ESTRADA-PDF — e IMPORTAR NAO E MANDAR CORRER. O mapa nao mede quem lhe da a ordem, e por isso nao a inventa. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/POLITICA-RAW-ROTA-PAGA.json`, `data/samples/RUN-MANIFEST.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | `data/samples/POLITICA-RAW-ROTA-PAGA.json`, `data/samples/RUN-MANIFEST.json` |
| **arestas no mapa** | entram 0 · saem 26 |
| **arestas provadas** | entram 0 · saem 26 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 26 |
| **lei da Bíblia** | COL-LAW-031/032/033/034 · tempo, geografia, procedencia, identidade |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `C-SENSOR-COLETA` · Coletor dos sensores tecnicos · canal, video e fala

| | |
|---|---|
| **peça real** | `regras/sensor_coleta.py` |
| **papel** | MEASUREMENT_INSTRUMENT · medido no plano CODE |
| **dono** | DESENVOLVIMENTO_MERCADO · TECNICO_CIENCIA |
| **status operacional** | yellow — algum workflow ou a cadeia canonica manda rodar isto.  Mas 1 ficheiro(s) mudaram depois de a descricao ter sido conferida — precisa de releitura humana. |
| **QUEM ATIVA** | **PECA_INTERNA** — C-CI-COLETA |
| **prova de quem ativa** | .github/workflows/apify-sensores.yml:124 _(plano CODE)_ |
| **porquê** | ha peca no mapa que manda esta correr, e ha linha de codigo que o prova. CAN DO: a linha existe; que a corrida tenha acontecido e outra pergunta. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | `data/samples/SPEAKER-UNIVERSE-PILOT-V1.json` |
| **o que sai · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 6 · saem 7 |
| **arestas provadas** | entram 6 · saem 7 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 0 · saem 0 |
| **prova da peça** | DECLARED YES · CODE YES · OBSERVED UNKNOWN · PROVEN YES _(no plano CODE)_ |
| **prova das ligações** | CODE 13 |
| **lei da Bíblia** | COL-LAW-031/032/033/034 · tempo, geografia, procedencia, identidade |
| **VEREDITO** | **OK** — activador provado, e o mapa mostra-o |

## Z-VEICULOS · IT · SCRAP — os canais

### `V-FACEBOOK` · FACEBOOK

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | UNKNOWN |
| **status operacional** | green — 1 acao(oes) NOMEIAM este canal no codigo, cada uma com ficheiro e linha. Isto e rota DECLARADA: nao diz que algo passou por aqui, so que o caminho esta escrito. |
| **QUEM ATIVA** | **CANAL_ABERTO_POR_ROTA** — C-APIFY-POOL |
| **prova de quem ativa** | coleta/comunicacao_coleta.py:57 _(plano CODE)_ |
| **porquê** | um canal nao corre: e aberto por uma rota, e sao estas as rotas medidas que chegam aqui. A ROTA nao esta PROVADA como travessia — o mapa mede que o ficheiro nomeia o canal e sabe falar com a rede, e nao qual rota serviu qual canal. |
| **o que entra · dado** | C-AS-FONTES |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-COLETA-PUBLICA |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 1 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 3 |
| **lei da Bíblia** | COL-LAW-018/019 · a rota mais barata capaz vem primeiro |
| **VEREDITO** | **OK** — canal, aberto por rota medida |

### `V-HTTP` · PEDIDO HTTP DIRETO

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | UNKNOWN |
| **status operacional** | green — 7 acao(oes) NOMEIAM este canal no codigo, cada uma com ficheiro e linha. Isto e rota DECLARADA: nao diz que algo passou por aqui, so que o caminho esta escrito. |
| **QUEM ATIVA** | **NAO_SEI** |
| **prova de quem ativa** | — NÃO SEI |
| **porquê** | nenhuma rota medida abre este canal, e ninguem o corre. |
| **o que entra · dado** | — NÃO SEI: nenhuma aresta de dado medida |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-COLETA-INSTAGRAM, C-COLETA-YOUTUBE, C-CORPUS, C-EU-REGULATORIO-COLETA, C-FONTES-EU, C-ROTULOS, C-SCRAP-SOCIAL |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 0 · saem 7 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 0 · saem 0 |
| **data plane** | entram 0 · saem 7 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 7 |
| **lei da Bíblia** | COL-LAW-018/019 · a rota mais barata capaz vem primeiro |
| **VEREDITO** | **UNKNOWN** — nada medido diz quem lhe da a ordem |

### `V-INSTAGRAM` · INSTAGRAM

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | UNKNOWN |
| **status operacional** | green — 2 acao(oes) NOMEIAM este canal no codigo, cada uma com ficheiro e linha. Isto e rota DECLARADA: nao diz que algo passou por aqui, so que o caminho esta escrito. |
| **QUEM ATIVA** | **CANAL_ABERTO_POR_ROTA** — C-APIFY-POOL, C-NAVEGADOR |
| **prova de quem ativa** | coleta/comunicacao_coleta.py:57; coleta/instagram_coleta.py:7 _(plano CODE)_ |
| **porquê** | um canal nao corre: e aberto por uma rota, e sao estas as rotas medidas que chegam aqui. A ROTA nao esta PROVADA como travessia — o mapa mede que o ficheiro nomeia o canal e sabe falar com a rede, e nao qual rota serviu qual canal. |
| **o que entra · dado** | C-AS-FONTES |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-COLETA-INSTAGRAM, C-COLETA-PUBLICA |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 2 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 2 · saem 0 |
| **data plane** | entram 1 · saem 2 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 5 |
| **lei da Bíblia** | COL-LAW-018/019 · a rota mais barata capaz vem primeiro |
| **VEREDITO** | **OK** — canal, aberto por rota medida |

### `V-LINKEDIN` · LINKEDIN

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | UNKNOWN |
| **status operacional** | green — 1 acao(oes) NOMEIAM este canal no codigo, cada uma com ficheiro e linha. Isto e rota DECLARADA: nao diz que algo passou por aqui, so que o caminho esta escrito. |
| **QUEM ATIVA** | **CANAL_ABERTO_POR_ROTA** — C-APIFY-POOL |
| **prova de quem ativa** | coleta/comunicacao_coleta.py:57 _(plano CODE)_ |
| **porquê** | um canal nao corre: e aberto por uma rota, e sao estas as rotas medidas que chegam aqui. A ROTA nao esta PROVADA como travessia — o mapa mede que o ficheiro nomeia o canal e sabe falar com a rede, e nao qual rota serviu qual canal. |
| **o que entra · dado** | C-AS-FONTES |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-COLETA-PUBLICA |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 2 · saem 1 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 1 · saem 0 |
| **data plane** | entram 1 · saem 1 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 3 |
| **lei da Bíblia** | COL-LAW-018/019 · a rota mais barata capaz vem primeiro |
| **VEREDITO** | **OK** — canal, aberto por rota medida |

### `V-YOUTUBE` · YOUTUBE

| | |
|---|---|
| **peça real** | — nenhum ficheiro |
| **papel** | UNKNOWN · medido no plano UNKNOWN |
| **dono** | UNKNOWN |
| **status operacional** | green — 2 acao(oes) NOMEIAM este canal no codigo, cada uma com ficheiro e linha. Isto e rota DECLARADA: nao diz que algo passou por aqui, so que o caminho esta escrito. |
| **QUEM ATIVA** | **CANAL_ABERTO_POR_ROTA** — C-APIFY-POOL, C-NAVEGADOR |
| **prova de quem ativa** | coleta/youtube_janela.py:471; coleta/youtube_janela.py:37 _(plano CODE)_ |
| **porquê** | um canal nao corre: e aberto por uma rota, e sao estas as rotas medidas que chegam aqui. A ROTA nao esta PROVADA como travessia — o mapa mede que o ficheiro nomeia o canal e sabe falar com a rede, e nao qual rota serviu qual canal. |
| **o que entra · dado** | C-AS-FONTES |
| **o que entra · ficheiros** | — NÃO SEI |
| **o que sai · dado** | C-COLETA-YOUTUBE, C-SCRAP-SOCIAL |
| **o que sai · ficheiros** | — NÃO SEI |
| **arestas no mapa** | entram 3 · saem 2 |
| **arestas provadas** | entram 0 · saem 0 |
| **OBSERVADAS** | 0 |
| **control plane** | entram 2 · saem 0 |
| **data plane** | entram 1 · saem 2 |
| **prova da peça** | DECLARED YES · CODE UNKNOWN · OBSERVED UNKNOWN · PROVEN UNKNOWN |
| **prova das ligações** | NÃO SEI 5 |
| **lei da Bíblia** | COL-LAW-018/019 · a rota mais barata capaz vem primeiro |
| **VEREDITO** | **OK** — canal, aberto por rota medida |

---

## O PLACAR

```
OK                 36
UNKNOWN            18
SYSTEM_GAP         10
EXTERNAL_ENTRY     6
ALVO_SEM_ESCRITOR_MEDIDO 2
TERMINAL           1
TOTAL              73
```
