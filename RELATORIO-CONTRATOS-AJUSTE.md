# RELATÓRIO — CONTRATOS-AJUSTE

Ramo `contratos-ajuste-v1`, a partir de `capa-materia-v1 @ a1dbebcc`. **Não instalado.**
Ordem da cia.it: não mexida (CONTRATOS-12).

## 1 · ISTAT (IT-T5-090) aponta as matérias

**Onde:** `regras/italy_contracts_onboarded.json`, linha da `IT-T5-090` (`ACQUISITION.LINK_PATTERN`).
O padrão anterior fica guardado ao lado (`LINK_PATTERN_ANTERIOR`), com o motivo (`LINK_PATTERN_PORQUE`).

```
antes: o padrão genérico do molde (qualquer secção com "comunicat", "pubblicazion", "ricerca"…)
agora: ^https?://(www\.)?istat\.it/(?:comunicato-stampa|notizia)/[a-z0-9]+(?:-[a-z0-9]+)+/?$
```

A prova de que o defeito era real: a única coisa que a 1.ª onda guardou da istat foi uma
**página de secção** (`…/ricercatori/eventi-segnalati-dalle-societa-scientifiche/`, 24/09 10:12).

Medido no índice guardado de 25/09 (sha256 em `INDICES-D40-V1.json`), sem rede:

| | antes | agora |
|---|---|---|
| ligações aceites | 42 | 20 (12 `comunicato-stampa` + 8 `notizia`) |
| páginas de secção entre elas | 12 (`attivita-e-servizi…`, `comunicati-e-analisi/…`, `documenti/…`, `newsletter/…`) | 0 |
| alvos D40 | `promozione-della-ricerca`, `rivista-di-statistica-ufficiale`, `istat-working-papers` | `linnovazione-nelle-imprese-anni-2022-2024`, `la-ricerca-e-sviluppo-in-italia-anni-2024-2026`, `conti-economici-nazionali-anni-2010-2025` |

Ficam de fora também `evento/`, `news-dati-alla-mano/` e `newsletter/`: a missão pediu
`/comunicato-stampa/` e `/notizia/`. Se `news-dati-alla-mano` (7 ligações, textos de divulgação)
interessar, é uma palavra a mais no padrão.

**Confirmação com rede (autorizada, 1 pedido):** portão de egresso PASS IT; o 1.º alvo novo
(`linnovazione-nelle-imprese-anni-2022-2024`) deu HTTP 200, 137.093 bytes, e o retrato do próprio
coletor (`coleta/retrato_html.mjs::retratoDoHtml`) diz **MATERIA_PROVAVEL** — 19.771 letras em
parágrafos. Ficheiro fora do Git em `C:/Users/London1/alvos-novos-20260925/confirmacao/`, sha256 em
`scripts/capa_materia/CONFIRMACAO-ISTAT-V1.json`.

⚠️ **Se isto rende SIM: NÃO SEI.** Os comunicados de hoje falam de inovação nas empresas,
investigação, contas nacionais, preços — nenhum título é agrícola. Não passei nenhum pela régua.

## 2 · Prazo de revisita da IT-T7-042 (balsamico)

**Dono da regra:** `regras/incrementalidade.mjs:304` — `decidirSobreDetalhe`, ramo
`DETAIL_CONTENT === "MUTABLE"`: com `TTL_SECONDS` revisita só quando a última visita passou do
prazo (`TTL_EXPIRED`); sem prazo, revisita sempre. **A regra não mudou.** Mudou o dado:

`regras/italy_contracts_onboarded.json`, linha da `IT-T7-042`: `RECOLLECTION.TTL_SECONDS`
`null` → `259200` (3 dias), com `TTL_PORQUE`. É o mesmo prazo que a T1 deu à IT-T7-017 e à
IT-T10-022; a balsamico só ficou sem ele por estar, na altura, fora da coorte
(`RELATORIO-TTL-MUTABLE-T1.md`: «tem o mesmo perfil e ficou sem prazo»).

Simulação da T1 para esta fonte (`provas/TTL-MUTABLE-SIMULACAO-T1.json`, corrida diária):
**9,49 → 3,13 revisitas por corrida, 3 edições, 0 perdidas, atraso máximo 2,33 dias.**

Nada apagado: o histórico no livro fica; a lei de preservação não mudou; a fonte continua
`MUTABLE` e continua a ser revisitada enquanto o índice mostrar a matéria.

**O corte "só até 28 dias depois da publicação" NÃO foi implementado**: troca "revisita enquanto o
índice mostrar" por "revisita até N dias", e isso é lei. A pergunta está em
[`PERGUNTA-BOT-LUCIANO-HORIZONTE-DE-REVISITA.md`](PERGUNTA-BOT-LUCIANO-HORIZONTE-DE-REVISITA.md).
Número que pesa: aplicado a todas, um corte em 28 dias perderia **6 de 19** edições medidas da Riunite
(a mais atrasada veio 72 dias depois). Na balsamico perderia 0 de 3.

## 3 · Previsão por corrida (mesmos 14 índices de 25/09, livro da produção sha256 `a054c336…`)

| | ALVOS-NOVOS-2 (a1dbebcc) | CONTRATOS-AJUSTE hoje | CONTRATOS-AJUSTE em 27/09 13:00 |
|---|---|---|---|
| documentos novos por corrida (D40 + D38) | 27 | **27** | 27 |
| dos quais istat | 3 páginas de secção | **3 comunicados de imprensa** | 3 comunicados |
| pedidos da balsamico em revisitas | 3 | **0** (visitadas a 24/09, dentro do prazo) | 3 (o prazo venceu) |
| alvos novos nos índices | 130 (com listas e secções) | 98 | 98 |

- O número de documentos novos **não sobe**: os 3 da istat já contavam; o que muda é que agora são
  matérias. A balsamico não troca revisitas por matérias novas — não tem nenhuma nova no índice.
- A balsamico poupa 3 pedidos em cada 2 de 3 corridas diárias. Esses pedidos são do domínio dela
  (D38 é por domínio); não abrem lugar a outra fonte.
- `MEDICAO-CONTRATOS-AJUSTE-HOJE-V1.json` e `…-27-09-V1.json` (hora simulada) em `scripts/capa_materia/`.
- **SIM na Admissão: NÃO SEI**, como na ALVOS-NOVOS. A leitura pelos títulos da ALVOS-NOVOS continua a
  valer (myfruit e plantgest prováveis; o resto duvidoso ou não).

## 4 · Testes e mutação

- `regras/motor_de_rota_test.mjs` **62/62** (2 novos: o contrato da istat, com ligações reais do índice,
  aceita as 3 matérias e recusa as 6 secções; a balsamico salta a 1 e a 2,99 dias e volta a 4 dias
  com `TTL_EXPIRED`, e continua MUTABLE).
- `incrementalidade_test` 31/31, `recollection_test` 31/31, `paridade_test` 32/32.
- `italy_contract_test`: 348 / 77 — **as mesmas 19 linhas FAIL** da base.
- `curadoria.test_contrato_unico` e `tests.test_retirada_por_decisao` (leem a tabela): OK aqui e na base,
  com a rede fechada (proxy para 127.0.0.1:9).
- Mutação na cópia `C:/capa-base @ 3471b047`: **6/6 mortos**
  (`scripts/capa_materia/MUTACAO-CONTRATOS-AJUSTE-V1.json`): padrão antigo; aceitar
  `comunicati-e-analisi`; perder `notizia`; balsamico sem prazo; prazo de 28 dias; balsamico IMMUTABLE.

## 5 · Uma divergência a saber

O contrato do curador (`curadoria/italy_contracts_curator.json`) continua com o padrão antigo da
istat. O curador **não reescreve** linhas que já têm contrato no coletor
(`curadoria/onboardar_rotas_provadas.py:89-90`), por isso o ajuste não se perde. O curador também
não o vê. Alinhar os dois é da bancada dos contratos.

## 6 · Writeset

```
regras/italy_contracts_onboarded.json   (IT-T5-090 LINK_PATTERN; IT-T7-042 TTL_SECONDS)  ← só isto muda a coleta
regras/motor_de_rota_test.mjs           (2 testes)
scripts/capa_materia/medir_d40.mjs      (saída e hora simulada por argumento)
scripts/capa_materia/confirmar_istat.py · CONFIRMACAO-ISTAT-V1.json
scripts/capa_materia/MEDICAO-CONTRATOS-AJUSTE-HOJE-V1.json · MEDICAO-CONTRATOS-AJUSTE-27-09-V1.json
scripts/capa_materia/mutar_contratos.py · MUTACAO-CONTRATOS-AJUSTE-V1.json
RELATORIO-CONTRATOS-AJUSTE.md · PERGUNTA-BOT-LUCIANO-HORIZONTE-DE-REVISITA.md
system-map (declarado + gerados)
```

O `LIVROS_SHA256` da `COORTE-BIG-COLLECTION-V1.json` registava a tabela antiga; é registo de quando a
coorte foi medida, e nenhum código o confere.

---

# D44 · o contrato do CURADOR da istat segue o do coletor

D44 (bot Luciano): corte de 28 dias **recusado**; prazo de 3 dias da balsamico **aprovado**.

**Dono da escrita:** `curadoria/reparar_contrato.py::aplicar` — a porta que muda SÓ a
aquisição, guarda a anterior e a prova, marca PRECISA_DE_REMEDIR, recalcula o
SOURCE_CONTRACT_HASH, passa `validar_contratos.validar` e rebenta se tocar noutro campo.
Mudança mínima nela: aceita `decisao/missao/metodo/ferramenta` (omissão = o R1 de sempre;
`test_reparar_contrato` passa igual).

**Quem escolhe:** `curadoria/alinhar_com_o_coletor.py --decisao D44 [--escrever]`. O curador
segue o coletor (o próprio livro do curador diz «o dono do contrato continua a ser
regras/italy_contracts.mjs»), só para as fontes da decisão (`DECISOES["D44"] = {IT-T5-090}`).
Invariantes: mesmas fontes pela mesma ordem, nenhuma outra muda nem um byte, cabeçalho igual.
Idempotente: a 2.ª corrida diz JA_ALINHADA.

Resultado em `curadoria/italy_contracts_curator.json`: só a linha da IT-T5-090 mudou
(LINK_PATTERN novo, REPARO_DE_CONTRATO com DECISAO D44 e a aquisição anterior, ROUTE_PROVENANCE,
hash 40a39cc3… → 1a70e0ce…). **Divergências curador×coletor nas 87 fontes que estão nos dois
livros: 0** (antes: 1, a istat).

Porque não pela porta D10 (`scripts/desbloqueio/aplicar_desbloqueio.contrato_unico`): é um pacote
de aplicação única do cutover, fechado às 7 fontes da D10.

⚠️ PRECISA_DE_REMEDIR fica `true`, como o reparo marca sempre. Medido: nenhum código lê esta marca
hoje (só quem a escreve) — não tira a istat da fila. A prova da rota nova é a confirmação de 1 pedido
(MATERIA_PROVAVEL), **não** um canário com a régua dos quatro passos.

Testes: `curadoria/test_alinhar_com_o_coletor.py` 7/7; com `test_reparar_contrato` e
`test_contrato_unico`: 66/66. Mutação na cópia `C:/capa-base @ a62f607c`: **5/5 mortos**
(`scripts/capa_materia/MUTACAO-ALINHAR-D44-V1.json`).

# APOIO AO MICRO · comparar o que veio com a previsão (só leitura)

`scripts/capa_materia/comparar_micro_com_previsao.py --estado <BIG-COLLECTION-ESTADO.json> --saida <pasta>`
(ou `--runs RUN1,RUN2,...`). Lê o livro de observações e o livro de decisões da árvore do bot e,
se houver banco, liga cada documento ao veredicto pela `micro_coleta.sql` (SELECT, banco em
read-only). Escreve só em `--saida`: `COMPARACAO-MICRO-COM-PREVISAO-V1.json` e
`DOCUMENTOS-DO-MICRO.tsv` (uma linha por documento: fonte, NOVO/VERSAO_NOVA, veredicto, na Sala?,
era alvo previsto?, endereço, regra, motivo). Previsão por omissão: `MEDICAO-CONTRATOS-AJUSTE-HOJE-V1.json` (27).

Ensaio sobre a 1.ª onda (`ENSAIO-COMPARAR-1A-ONDA-V1.json`, banco lido): 6 documentos novos em 4 fontes;
**3 SIM (todos IT-T10-018), 3 NAO, 3 NAO_SEI** — a mesma conta da BC5 e da CAPA-MATERIA. A coluna
"previsto" nesse ensaio é a de hoje, não a de 24/09: serve só para provar a leitura.
Testes: `scripts/capa_materia/test_comparar_micro_com_previsao.py` 6/6 (sem banco = NAO SEI por documento, não inventa;
endereço com 2 registos no banco não se liga à sorte; corridas de fora não contam; só escreve na saída).
