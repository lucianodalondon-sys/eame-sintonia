# CAMINHO-SERIES-SALA-D90 · as séries de monitorização até à Sala, pelo fluxo canónico

**Pedido (D90, P0 «reprocessar antes de buscar»):** as 66 séries numéricas de `SINAL-PRECOCE-SERIES.md` vão à Sala pelo fluxo
canónico (Admission + escritor único), com OBSERVAÇÃO / PREVISÃO / RECOMENDAÇÃO separadas e os valores como vieram. Sem rede:
que documentos, que campos, o comando de ensaio numa cópia, e o que falta de contrato.

**Medido em 26/09**, Sala real **só em leitura** (`default_transaction_read_only=on`), vivo `dc0de726`, sem rede. Fotografia
da Sala: `monitorizacao/d90/RAW-SALA-LEITURA.json` (sha256 `1f138e32c80d33bb…`). Pacotes:
`monitorizacao/d90/pacotes/` (MANIFESTO sha256 `75febd45dfea95db…`). Tudo fora do Git, em `C:/Users/London1/sintonia-sala-italia/`.

## 0 · A resposta curta

- **Das 66 séries, nenhuma tem os seus 2 pontos na Sala hoje.** Cada série tem 2 medidas (2 boletins). Na Sala há RAW para
  **o 2.º boletim** de Salerno (11 séries) e de APOL (3 séries) — **14 séries com 1 ponto em 2**. As **52 da Toscana** (Terre
  dell'Etruria) têm **0 pontos**: nenhum dos 2 boletins que lemos está no RAW da Sala.
- **O que pode andar já** (ensaio pronto, abaixo): **4 derivados** `TABLE_EXTRACTION`, filhos de 4 RAW que já estão na Sala,
  com **183 linhas** (89 OBSERVAÇÃO · 94 RECOMENDAÇÃO · 20 com número). Escritos pelo dono do derivado, idempotentes.
- **O que não pode andar sem decisão:** (a) os **9 documentos** que faltam no RAW são **legado** do depósito antigo do robô, sem
  corrida (RUN_ID) no livro — a estrada `acervo-para-sala-v1` (por RUN_ID) não os apanha; (b) **não existe na Sala um sítio
  para uma linha de tabela** (a `sala_de_espera` guarda documentos; as tabelas `observacao` e `boletim_fitossanitario` existem
  com **0 linhas** e sem dono). Ver §4.

## 1 · Que documentos (17 lidos; 8 com RAW na Sala, 9 sem)

| # | Fonte | Forma | Documento | RAW na Sala (id) | Linhas | Com número | Natureza | sha256 do pai (16) |
|---|---|---|---|---|---|---|---|---|
| 1 | IT-T2-002 | ARPAV | `agro_01.pdf` (N°54) | AUSENTE | 3 | 0 | OBSERVACAO 3 | `f88c89d73d6a132a` |
| 2 | IT-T2-002 | ARPAV | `agro_09.pdf` (N°54) | AUSENTE | 4 | 0 | MISTA 1 · OBSERVACAO 3 | `3d3c1bc0e96332e8` |
| 3 | IT-T2-002 | ARPAV | `agro_16.pdf` (N°54) | AUSENTE | 3 | 0 | OBSERVACAO 3 | `8c13500d43502e64` |
| 4 | IT-T2-002 | ARPAV | `agro_24.pdf` (N°54) | AUSENTE | 4 | 0 | MISTA 1 · OBSERVACAO 3 | `0be2d204c98ad1b1` |
| 5 | IT-T2-002 | ARPAV | `agro_01.pdf` (N°56) | **2** | 0 | 0 | — (secção cortada no PDF) | `571d3cda8b7fcef6` |
| 6 | IT-T2-002 | ARPAV | `agro_09.pdf` (N°56) | **3** | 0 | 0 | — | `895c2451bfcf6aa2` |
| 7 | IT-T2-002 | ARPAV | `agro_16.pdf` (N°56) | **4** | 0 | 0 | — | `bedb247afa678c89` |
| 8 | IT-T2-002 | ARPAV | `agro_24.pdf` (N°56) | **5** | 0 | 0 | — | `cc67a0047ab08b13` |
| 9 | IT-T3-002 | SALERNO | `SA-02-09.pdf` (N°25) | AUSENTE | 15 | 11 | OBSERVACAO 15 | `0c2723e66201f966` |
| 10 | IT-T3-002 | SALERNO | `SA-16-09.pdf` (N°27) | **7** | 14 | 11 | OBSERVACAO 14 | `c5ae3bfe76d9bef6` |
| 11 | IT-T3-005 | TERRETRURIA | `monitoraggio.html` 31/08–06/09 | AUSENTE | 69 | 52 | OBSERVACAO 69 | `2e488a8232ba980f` |
| 12 | IT-T3-005 | TERRETRURIA | `monitoraggio.html` 07–13/09 | AUSENTE | 69 | 52 | OBSERVACAO 69 | `bced66652f252d09` |
| 13 | IT-T3-008 | ARIF | `…N36_02-09-2026.pdf` | AUSENTE | 81 | 0 | OBSERVACAO 32 · RECOMENDACAO 49 | `e612807928b5ada9` |
| 14 | IT-T3-008 | ARIF | `…N38_16-09-2026.pdf` | **36** | 77 | 0 | OBSERVACAO 31 · RECOMENDACAO 46 | `85cb86ebd6582997` |
| 15 | IT-T3-010 | APOL | `…n_9_del_07_09_2026.pdf` | AUSENTE | 12 | 9 | OBSERVACAO 12 | `59da05274359eff6` |
| 16 | IT-T3-010 | APOL | `…n_10_del_14_09_2026.pdf` | **1** | 12 | 9 | OBSERVACAO 12 | `2ba23d223429131e` |
| 17 | IT-T3-008 | ARIF | N37 — texto lido da Sala (`documento_estruturado`, derivado 7) | **9** | 80 | 0 | OBSERVACAO 32 · RECOMENDACAO 48 | `a8d9c53af8f73027` |

Totais: **443 linhas**; com RAW **183** (4 documentos com linhas: #10, #14, #16, #17); sem RAW **260**.

- **Onde estão os 9 AUSENTES:** 8 no depósito antigo do vivo (`source-curator-service-v1/data/collection-store/italy/…`) e 1
  (#12) em `sintonia-sala-italia/acervo-coletor-bcr/…`. Caminhos exatos em `curadoria/SINAL-PRECOCE-SERIES.json` (`DOCUMENTOS`).
  Os relatórios do vivo (`BASELINE-ADMISSION-T3-V1.json`, `A-COLLECTION-PRESERVA-O-FATO.json`) conhecem-nos com
  `RULE_VERSION reprocessamento-v1`, **sem RUN_ID** do livro novo.
- **RAW repetido:** vários sha256 aparecem 2 a 4 vezes na `raw_asset` (ex.: ARPAV N°56 nos ids 2–5, 21–24, 39–42, 217–220).
  O pai proposto é **o id que já tem derivados** (o texto) — regra em `estado_na_estrada()`.
- ARPAV N°56 (#5–#8): **0 linhas** — a secção fitossanitária vem cortada no próprio PDF. O escritor **não** escreve pacote vazio.

## 2 · Que campos (contrato proposto `TABLE_EXTRACTION/linhas-de-monitorizacao/v0`, PROPOSTA D90)

Um pacote JSON **por documento**, filho do RAW (produtor `linhas-de-monitorizacao`, `media_type application/json`). Cada linha:

| Campo | O que é | Regra |
|---|---|---|
| `CULTURA`, `LOCAL`, `ARMADILHA`, `ORGANISMO` | como o documento escreve | nada traduzido nem normalizado; ausente = `NAO SEI` |
| `METRICA_MEDIDA` | o que o documento **diz** que mede | APOL: `NAO SEI` (cabeçalho em imagem) |
| `METRICA_ESPERADA_PELO_CONTRATO` | o que o contrato da fonte **espera** (`CAMPOS_A_EXTRAIR`) | nunca substitui a medida |
| `VALOR_TAL_COMO_VEIO` | o texto exato da célula (`"5%"`, `"7/5/4→6"`, `"STAZIONARIO"`) | nunca arredondado |
| `VALOR_NUMERICO` | número **só** quando a célula é um número | rótulo → `null` |
| `UNIDADE`, `LIMIAR`, `FASE` | como vieram | |
| `DATA_DO_FACTO` + `DATA_DO_FACTO_BASE` | data e **de onde veio** (período do boletim, data de amostra) | `FACT_TIME != PUBLISHED_AT` |
| `NATUREZA` (lista) + `NATUREZA_UNICA` | `OBSERVACAO` · `PREVISAO` · `RECOMENDACAO` · `MISTA` · `NAO SEI` | frase com duas naturezas fica `MISTA` — **não se parte** |
| `TRECHO`, `CONFERE`, `ORIGEM` | o pedaço do texto de onde a linha saiu e se a máquina o reencontrou | prova da linha |
| `LINHA_ID` | sha256 (24) da linha | estável: reprocessar dá o mesmo id |

Por forma: **ARIF** — uma linha OBSERVAÇÃO («Situazione fitosanitaria») + uma RECOMENDAÇÃO («Programma di difesa»), mais uma
por limiar — a separação que o contrato do IT-T3-008 manda. **APOL** — uma linha por coluna + uma de tendência/risco.
O pacote traz também o `EVIDENCE_CLASS` da fonte, copiado do contrato.

## 3 · Os comandos (sem rede)

**3.1 · Fazer os pacotes** (já feito; repetível, dá os mesmos bytes):

```
O=C:/Users/London1/sintonia-sala-italia/monitorizacao/d90
py curadoria/d90_payload_series.py --series=curadoria/SINAL-PRECOCE-SERIES.json --raw=$O/RAW-SALA-LEITURA.json \
   --texto-arif=$O/ARIF-N37-texto-da-sala.txt --saida=$O/pacotes
# -> {"DOCUMENTOS": 17, "LINHAS": 443, "RAW_PRESENTE": 8, "RAW_AUSENTE": 9}
```

**3.2 · Ver o que seria escrito** (não toca em banco):

```
py curadoria/d90_preservar_pacotes.py --pacotes=$O/pacotes
# -> {"MODO": "A_SECO", "PEDIDOS": 4, "POR_ESTADO": {"A_SECO": 4}}
```

**3.3 · ENSAIO numa cópia da Sala** — para o coordenador. Só com `LOCK-PESADO.txt` livre, **sem** `LOCK-PRIORIDADE.txt`
ativo e ≥ 5 GB livres (às 20:00 de 26/09 o LOCK-PESADO estava com a INTEGRA-NOITE-LOTE3 — por isso **não corri**):

```
:: 1) dump SO EM LEITURA da Sala real (o comando de sempre)
C:/Users/London1/sintonia-sala-italia/backup_sala.cmd
:: 2) o ensaio: Postgres descartavel novo, restaura o dump, escreve 2 vezes, confere
py curadoria/d90_ensaio_copia.py --dump <o .dump do passo 1> --pacotes=%O%/pacotes ^
   --saida=%O%/ENSAIO-D90.json
```

Espera-se: `ENSAIO_D90 PASS`; 1.ª escrita **4 INSERTED**; 2.ª escrita **4 REUSED**; `derived_artifact` +4; `raw_asset` e
`sala_de_espera` **iguais** (md5 da tabela antes = depois). O escritor recusa a porta 54330 e o DSN de `SALA_DSN.txt`: levar à
Sala real é instalação do coordenador, depois do §4.

**Provado aqui (SQLite descartável da casa, `curadoria/test_d90.py`, 9 testes verdes):** o escritor passa por
`guarda/preservar_derivado.py` → `INSERTED` («escrita, lida de volta e conferida campo a campo»); 2.ª vez → `REUSED` (0 linhas);
a seco não escreve; recusa a Sala real; salta RAW ausente e pacote sem linhas. Mutação: tirar a trava do RAW ou a do pacote
vazio → os testes caem (2/2).

## 4 · O que falta de contrato (por ordem de bloqueio)

1. **Onde a linha mora na Sala — decisão do dono/coordenador.** A `sala_de_espera` é por documento; as revisões só aceitam 8
   campos de tempo/lugar; o JSON `fato` só serve estágio FATO. Três saídas:
   - **A · a linha fica no derivado** (este ensaio) e a Intelligence lê o `TABLE_EXTRACTION`. Não mexe em lei. A Sala só ganha
     o filho do documento.
   - **B · FATO pela Admissão** — exige mudar **COL-LAW-202** («a Collection não extrai claim», hoje TARGET) e dar às linhas
     `claim_id/subject/predicate/fact_id`.
   - **C · encher `observacao` / `boletim_fitossanitario`** (existem, 0 linhas, sem escritor): precisa de dono, de escritor único
     e do mapa `crop_issue_id` / `geografia_id` — hoje **NAO SEI** para quase todas as linhas.
   Recomendo **A agora** (não perde nada e é reversível) e decidir B/C depois de ver as linhas.
2. **`TABLE_EXTRACTION` não tem contrato nem produtor no código.** O tipo está no vocabulário fechado (migrations 022/034) e a
   Sala já tem `TABLE_EXTRACTION` do produtor `secoes-por-cultura` (raw 1, 7, 36) — sem contrato escrito. O v0 do §2 é
   **proposta**; precisa de ser aceite e o produtor `linhas-de-monitorizacao` registado.
3. **Os 9 documentos legados** (§1). Não têm corrida no livro novo; `acervo-para-sala-v1` (não instalado) trabalha por RUN_ID
   e não os cobre; `provas/o_legado_fora_do_fluxo.py` diz que corpo sem aquisição provada **não** entra por backfill
   («DECIDE != IMPLEMENT»). Saídas: **(i)** decisão de uma porta de legado; **(ii)** voltar a colher os 9 (9 pedidos, 5
   domínios, dentro do teto — mas é **rede**, fora desta missão; e os boletins antigos podem já não estar publicados).
   Sem isto, **as 52 séries da Toscana ficam fora** e as outras 14 ficam com 1 ponto em 2.
4. **O contrato da fonte não passa para a Sala.** Os 5 itens destas fontes estão na Sala com classe de evidência
   **`NAO SEI`** — o `EVIDENCE_CLASS` do `.mjs` não é copiado. O pacote carrega-o; a Admissão não.
5. **APOL:** o que cada coluna mede é **NAO SEI** (cabeçalho em imagem). O contrato **espera** capturas / % infestação / tendência
   — está no pacote como «esperada», **nunca** como «medida». Precisa de ver o PDF ou OCR.
6. **ARIF:** cultura e área de cada bloco = **NAO SEI** (títulos em imagem); N36 tem 32 blocos, N37 32, N38 31 — **não** se
   emparelha por posição.
7. **ARPAV:** o contrato do IT-T2-002 diz `AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE`, mas o boletim traz uma secção
   fitossanitária. As linhas vão como vieram; a classe da fonte precisa de ser revista pelo dono do contrato.
8. **Terre dell'Etruria 14–20/09 (raw 28)** está na Sala como OBSERVAÇÃO **sem texto extraído** — não o li; fica fora.
9. **RAW repetido** para o mesmo sha256 (até 4 ids). O ensaio escolhe o id com derivados; a regra devia ser do escritor RAW.

## EM PALAVRAS SIMPLES

- **Pediram:** levar as 66 séries de números (armadilhas, % de azeitonas picadas) para a Sala, pelo caminho oficial.
- **O que descobri:** a Sala guarda **documentos**, como um arquivo de pastas. Ainda não tem gaveta para **uma linha de
  tabela**. E das 66 séries, **nenhuma** tem as 2 medidas lá dentro: há 14 com 1 medida em 2, e as 52 da Toscana com 0.
  Os boletins que faltam (9) estão no nosso disco, mas vieram de antes do caderno atual do robô — não têm «recibo de
  entrada», e a regra diz que sem recibo não entram sozinhos.
- **O que preparei:** um pacote por boletim, com cada linha separada em **observação** («apanhámos 40 moscas»),
  **previsão** e **recomendação** («tratar se passar do limiar»), e o número **exatamente como estava escrito**.
  Para os 4 boletins que já estão na Sala, os pacotes podem entrar **como anexo do boletim** pelo escritor oficial.
  Testei numa cópia de brincar: entra uma vez, e se correr de novo não duplica.
- **Não mexi na Sala.** Só li. O ensaio numa cópia da Sala verdadeira ficou **pronto para correr**, mas não corri: o
  cadeado das tarefas pesadas estava ocupado por outra sessão.
- **O dono precisa de decidir:** (1) onde mora uma linha de tabela na Sala — eu sugiro «fica como anexo do boletim», que não
  muda nenhuma lei; (2) o que fazer com os 9 boletins antigos sem recibo — abrir uma porta para eles, ou buscá-los de novo
  na internet (9 pedidos).
