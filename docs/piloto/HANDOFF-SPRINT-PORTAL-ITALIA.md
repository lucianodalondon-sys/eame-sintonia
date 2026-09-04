# HANDOFF DO SPRINT PORTAL ITÁLIA → LINHA B

**Artefato:** `data/samples/IT-HUMAN-SENSORS/IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json`
**Gerador:** `scripts/handoff_portal_it.py` · **SOURCE_HEAD medido:** `470c951`

> **O artefato é a entrega; este documento é a leitura dele.** Se os dois divergirem, o
> artefato vence — ele é remedido a cada corrida, este texto não.

---

## POR QUE ELE É DETERMINÍSTICO, E POR QUE ISSO NÃO É CAPRICHO

```
$ python3 scripts/handoff_portal_it.py
SHA256 : 1283b4f7a292798f19a964421966316603e7c25aaa9d5b52aa7764bba74ec560

$ python3 scripts/handoff_portal_it.py
SHA256 : 1283b4f7a292798f19a964421966316603e7c25aaa9d5b52aa7764bba74ec560

HASH_IDENTICO = SIM
```

Duas coisas foram deliberadas para que esse "igual" signifique alguma coisa:

**Nada é transcrito.** Cada número do handoff é remedido, na hora, dos mesmos arquivos que a
Linha B recebe. Esta rodada encontrou nove números **certos** digitados à mão dentro de um
gerador que promete o contrário — e a lição foi que estar certo não basta:

> **Um número certo que ninguém consegue auditar é pior que um errado: o errado alguém derruba.**

**Não há relógio.** `CAPTURED_AT` é a **data do commit de `SOURCE_HEAD`**, não a hora de
execução. Um carimbo de relógio faria duas corridas idênticas darem hashes diferentes, e o
"rodei duas vezes e deu igual" deixaria de provar qualquer coisa.

`SOURCE_HEAD` é `470c951` — o estado **medido**, anterior ao commit que publica o próprio
handoff. É o que interessa a quem for reproduzir.

---

## AS SEIS CLASSES, E O QUE CAI EM CADA UMA

| classe | achados |
|---|---|
| **`PORTAL_NOW`** | 01 · azoxistrobina + protioconazol |
| **`PORTAL_WITH_METHOD`** | 02 · autorizações ADAMA · 03 · revogado × scaduto · 05 · pessoas e papéis · 06 · cobertura territorial |
| **`METHOD_ONLY`** | 04 · social/YouTube |
| **`OWNER_DECISION`** | 09 · rótulo "oportunidade" · 10 · protótipo |
| **`CODE_FIX_HANDOFF`** | 07 · correção de datas · 08 · `PROD_FTS` |
| **`DO_NOT_SHOW`** | 14 frases, cada uma com o texto que entra no lugar |

`DO_NOT_SHOW` não é um apêndice: é a lista que a tela consulta **antes** de escrever uma
frase, não depois.

---

## O ÚNICO `PORTAL_NOW`, E ELE BASTA

Azoxistrobina **e** protioconazol no mesmo produto dão **exatamente quatro registros**, todos
vigentes. A lista é o universo, não uma amostra:

| produto | registro | titular | vencimento |
|---|---|---|---|
| MAXENTIS | 018067 | ADAMA ITALIA S.R.L. | **31/05/2027** |
| KOJAMI | 019095 | ADAMA ITALIA S.R.L. | **31/05/2027** |
| PROMINO XTRA | 019093 | CAC CHEMICAL GMBH | **31/03/2028** |
| AMISTAR ERA 240 EC | 019194 | CAC CHEMICAL GMBH | **31/03/2028** |

- **FATO:** quatro registros vigentes, dois de cada lado, com as datas acima.
- **INTERPRETAÇÃO:** o concorrente tem **~10 meses a mais** de janela autorizada na mesma dupla.
- **AÇÃO QUE SÓ A ADAMA DECIDE:** se a renovação de 31/05/2027 já está em curso, e se a
  diferença de janela importa comercialmente.

**Fonte oficial:** Ministero della Salute — Banca dati prodotti fitosanitari, CC BY 4.0.

> **A trava que impede o erro fácil:** ato europeu e registro nacional **não são duas fontes
> independentes** — o nacional deriva do europeu. Contá-los como duas confirmações infla a
> confiança de um fato que tem uma origem só.

---

## O QUE MUDA DE VERDADE NA APRESENTAÇÃO

**Os números com dois eixos.** "155 autorizações ADAMA" é um de quatro. A matriz inteira está
no artefato: `STRICT` 89 · `AMPLIADO` 155, e isso somando **cinco razões sociais**; só
`ADAMA ITALIA S.R.L.` dá 39 e 77. Agrupar as cinco é **julgamento humano**, não fato do
registro. E `Sospeso` (3) e `Autorizzato provvisoriamente` (2) ficam em **`NÃO SEI`
declarado** — não estão vigentes nem revogados, e nenhuma regra dona existe ainda.

**A demonstração italiana que a Espanha não consegue fazer.** `Revocato` (13.216) e `Scaduto`
(765) são estados distintos, e **223 autorizações estão revogadas com vencimento ainda
futuro** — 22 delas ADAMA. É a prova de que **data de validade sozinha não responde se um
registro está utilizável**. Com o limite dito junto: motivo declarado em **1.119 de 13.216**;
nos outros, por que foi revogado é `NÃO SEI`.

**A camada social não entrega fato de campo.** `HAS_CAPTION` é `NÃO SEI` em 150 de 150 —
**140 nunca foram tentados** e os 10 tentados, todos do mesmo canal, deram `PORTA_NAO_ABRIU`.
Nenhum vídeo respondeu "não há faixa". `ULTIMA_COLETA` é nula em **243 de 243** fontes: sem
segunda passagem não há linha de base, e sem linha de base **"mudou" não existe**.

**Papel não é pessoa.** 278 entradas de papel, 114 provadas, **90 entidades** com ao menos um
papel provado, de 221. Papéis de campo provados: **5**. Agrônomo, produtor e consultor
provados: **0**.

**O mapa responde "temos olhos aqui", nunca "há problema aqui".** E carrega as duas leituras:
**72** células `GOOD` com a expansão territorial declarada, **30** sem ela.

---

## O QUE A LINHA B NÃO PRECISA REFAZER

**A correção de datas já está feita.** `datas_no_texto('2026-08-24')` devolvia `2026-08-02`;
**257 das 365 datas ISO de 2026 voltavam erradas, sempre para trás** — fazendo toda fonte
parecer mais velha do que é. Consertado em `scripts/fonte_territorial.py`, preso por
`tests/test_datas.py`, que varre o ano inteiro em quatro formatos. **Entregar o commit e o
teste ao dono canônico pela rota correta; não reimplementar.**

**A dívida que fica junto:** os artefatos territoriais já gravados saíram da leitura
defeituosa. **Nenhum número de recência territorial vai à tela antes de remedir** — e remedir
não exige coleta nova.

---

## O QUE ESTÁ NAS MÃOS DO DONO

**`PROD_FTS` — bloqueador condicional.** `ask_sintonia.py:19`, `normalize_substance.py:34` e
`data_clock.py:25` apontam para `PROD_FTS_6_20260824.csv`; em disco o arquivo é `PROD_FTS.csv`.
`chain.py` já resolve por prefixo. **Não corrigido aqui: esta branch não é dona dessa porta.**

> **Se Ask Sintonia, `normalize_substance` ou o data clock italiano forem usados na demo,
> este defeito precisa estar resolvido pelo dono ANTES da apresentação.**

**"Radar Opportunità".** O documento dono da regra (`ARQUITETURA-DE-PRODUTO-ATUAL.md`) declara
que MT3 entrega `ACTIVATION QUESTION` e proíbe `SALES OPPORTUNITY`, `UNDERUSED ASSET` e
`WHITE SPACE CONFIRMED`. O rótulo da tela atual é **relato do dono, não medição minha**:
`italia-portale/client` não existe nesta branch e esta sessão está proibida de tocá-lo.
Registrar o relato como medida seria o erro que este handoff inteiro combate. **Não renomeado
aqui.** Decide a sessão dona do Portal Itália.

**Protótipo.** `PROTOTYPE_FROZEN = SIM` (D-007) continua de pé. Os nove números digitados à
mão ficam registrados como **dívida real**, e `CANDIDATE_DEPLOY_AFFECTED = NÃO`.

---

## LIMITES QUE VIAJAM COM O PACOTE

- Nenhuma coleta de rede nesta rodada. **Custo = 0.**
- Nenhuma afirmação se apoia em legenda: nenhuma foi obtida (**D-040**).
- `data/raw/IT-T4-001/PROD_FTS.csv` **não é versionado** (D-003). Em clone novo os achados
  01, 02 e 03 voltam como `NÃO SEI` em vez de números — o hash do CSV está em
  `ARTEFACT_HASHES` para identificar o snapshot.
- O snapshot do registro é de **2026-08-24** e envelhece: 7 dos 20 próximos vencimentos
  publicados já haviam passado em 2026-09-04. **Futuro se calcula contra a data de leitura.**
- **P-012 (GDPR) segue aberta:** a camada nomeia pessoas com afiliação e ORCID.

---

**Parado aqui.** Nada foi coletado, nenhum protótipo foi tocado, nenhum rótulo foi renomeado,
nenhum documento foi reclassificado.
