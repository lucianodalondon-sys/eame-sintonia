# FUNDAÇÃO DO SYSTEM MAP V2

> **Esta branch ainda não tem mapa.** Tem o chão onde ele vai ser construído.
> A topologia, o modelo, os cartões e as setas são da próxima missão — e
> deliberadamente não existem aqui.

A primeira tentativa do V2 (`claude/dazzling-sagan-s53805`) reprovou na
auditoria de aceitação. A causa-raiz não foi a interface nem os portões: foi a
**fundação**. Ela foi construída sobre `main`, e `main` não é a linha onde a
máquina vive.

    O MAPA ESTAVA CERTO SOBRE A ÁRVORE ERRADA.

---

## 1 · A BASE, E POR QUE É ESTA

```
BASE      claude/system-map-current-collection-truth-v2 @ 2e73fc1f
MEDIDO    2026-09-14
```

Quatro candidatas foram medidas — não escolhidas pelo nome:

| branch | data | ficheiros | contém a máquina? |
|---|---|---|---|
| `main` | 12/09 | 1294 | **não** — sem Bíblia, sem `orquestrador/`, sem Sala de Espera |
| `claude/gifted-shannon-8u9l78` | 14/09 15:13 | 1313 | não — é `main` + 1 commit |
| `release/canonical` | 14/09 05:47 | 1550 | parcial — é o **dono da publicação** |
| **`…current-collection-truth-v2`** | **14/09 13:38** | **1898** | **sim** |

**As duas linhas vivas são irmãs, não ancestrais.** Base comum em 09/09:
`release/canonical` avançou 74 commits; esta base avançou **366**. Nenhuma
branch do repositório contém as duas — medido sobre as 236 branches remotas.

### Por que não `release/canonical`

Ela é a autoridade de **publicação**, e isso está escrito por ela própria em
[`system-map/CANONICAL-PUBLICATION.json`](../CANONICAL-PUBLICATION.json):

```
CANONICAL_DEPLOY_OWNER       = release/canonical
PROMOTION_AUTHORITY_BRANCHES = [release/canonical]
```

O mesmo ficheiro diz, na primeira secção, a frase que decide a questão:

> `CANONICAL PUBLISHED != LATEST SOURCE`

O endereço oficial serve a versão **aprovada**, que por desenho não é a versão
**atual**. Um mapa que observa a máquina tem de observar a fonte, não o alias.
Tratar o dono do endereço como dono da verdade seria confundir publicação com
arquitetura — e o contrato proíbe-o em voz alta.

`release/canonical` fica registada como **autoridade de publicação**, e o seu
contrato viaja nesta base (o ficheiro está aqui, igual).

### O que a base errada custou, medido

| o que o V2 antigo afirmou | o que a base correta mostra |
|---|---|
| «`coleta/social_scrap.py` não existe nesta árvore» | **existe** |
| «`guarda/social_guarda.py` não existe nesta árvore» | **existe** |
| orquestrador em `pedido/orquestrador.py` | gaveta própria: `orquestrador/orquestrador.py` |
| 15 gavetas | **16** — `orquestrador` é uma delas |
| Sala de Espera sem implementação | `admissao/sala_de_espera.py` |
| sem RAW, DERIVED, STRUCTURED | contratos próprios, abaixo |

113 ficheiros de código de máquina existem aqui e não em `release/canonical`;
4 no sentido inverso.

---

## 2 · AS AUTORIDADES

Localizadas, **não transplantadas**. Arquitetura vem daqui — nunca do mapa.

| autoridade | path | ref | estado |
|---|---|---|---|
| Lei do repositório | `AGENTS.md` | nesta base | presente |
| Instruções permanentes | `CLAUDE.md` | nesta base | presente |
| **Bíblia da Coleta** | `BIBLIA-CANONICA-DA-COLETA.md` | nesta base | **2889 linhas** |
| Bíblia, índice legível por máquina | `docs/biblia/leis.json` | nesta base | `V1.4` · `CANONICAL` · derivado da Bíblia |
| Bíblia, validador | `provas/valida_biblia.py` | nesta base | presente |
| Censo das leis · conflitos · emendas | `docs/biblia/` | nesta base | 8 ficheiros |
| **RAW — identidade da observação** | `docs/operacao/IDENTIDADE-DA-OBSERVACAO-RAW.md` | nesta base | presente |
| **Storage — identidade do artefato** | `docs/operacao/IDENTIDADE-DO-ARTEFATO.md` | nesta base | presente |
| **Derived** | `docs/operacao/A-CASA-DO-DERIVADO.md` | nesta base | presente |
| **Structured** | `docs/operacao/CONTRATO-DOS-STRUCTURED-TARGETS.md` | nesta base | + 3 contratos irmãos |
| **Admission** | `docs/operacao/BASELINE-ADMISSION-T3-V1.md` | nesta base | presente |
| **Fronteira Admission → Intelligence** | `docs/operacao/ESTUDO-FRONTEIRA-ADMISSION-INTELLIGENCE-V1.md` | nesta base | presente |
| **Sala de Espera** | `docs/decisoes/ADR-SALA-DE-ESPERA-V1.md` | nesta base | ADR |
| Intelligence — trava | `docs/operacao/TRAVA-DA-INTELIGENCIA.json` | nesta base | presente |
| Intelligence — linhagem do pacote | `italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json` | nesta base | presente |
| Identidade | `docs/regras/MODELO-DE-IDENTIDADE-EAME.md` | nesta base | presente |
| Executor — contrato de retorno | `docs/operacao/CONTRATO-DE-RETORNO-DO-EXECUTOR-V1.md` | nesta base | presente |
| SCRAP — dono e evolução | `docs/decisoes/ADR-SINTONIA-SCRAP-EVOLUTION.md` · `docs/decisoes/ADR-SCRAP-SOCIAL-NA-BIBLIA.md` | nesta base | ADR |
| Portal — produto | `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` | nesta base | presente |
| **Publicação** | `system-map/CANONICAL-PUBLICATION.json` | nesta base | dono = `release/canonical` |
| Decisões | `docs/decisoes/` | nesta base | 6 ADR + diário (1463 linhas) |
| **KNOW-HOW canónico** | `SINTONIA-EAME-KNOW-HOW.md` | **`claude/sintonia-eame-know-how-v1` @ 4208fd05** | **FORA desta base** |

⚠️ O know-how é a única autoridade que **não** vive aqui. Fica registada a
referência; não foi copiada. Copiá-la criaria um segundo dono.

---

## 3 · A REGRA QUE ESTA FUNDAÇÃO ESTABELECE

```
GENERATED_MAP_ARTIFACT  CANNOT_BE  CANONICAL_AUTHORITY
```

A auditoria encontrou **7 laços** em que o V2 antigo citava ficheiros gerados
pelo próprio sistema do mapa — `casco.generated.json`,
`sources.generated.json`, `regras/LEIA-ANTES-DE-COLETAR.md` — como se fossem
autoridade canónica.

Um artefato gerado pode provar **«o scanner viu isto»**. Nunca pode provar
**«isto é a arquitetura»**. Quando o mapa declara a sua própria medição como
lei, ele deixa de observar e passa a inventar — e o portão dele aprova, porque
está a comparar-se consigo mesmo.

**O que é permitido:** um ficheiro gerado como `observado_por` — evidência de
medição, sempre rotulada como tal.
**O que é proibido:** um ficheiro gerado como `authority`.

Esta regra vale a partir daqui. O próximo modelo nasce com ela.

---

## 4 · O QUE VEIO DA PRIMEIRA TENTATIVA, E O QUE NÃO VEIO

Cada ficheiro foi medido, não julgado de memória: procurou-se dentro dele os
identificadores da topologia antiga.

| ficheiro | papel | neutro? | decisão | porquê |
|---|---|---|---|---|
| `app/index.html` | casca | SIM | **REUSABLE** | 0 ids da topologia antiga; 0 nomes das 158 peças desta base |
| `app/map.css` | forma | SIM | **REUSABLE** | só apresentação; tokens do ADAMA DS por `<link>` |
| `app/map.js` | tela | SIM | **REUSABLE** | lê o que lhe derem; 0 factos da máquina medidos lá dentro |
| `scripts/scan_machine.py` | medidor | **NÃO** | REBUILD | embute os canais (`V-YOUTUBE`…) — isso é arquitetura |
| `scripts/validate_map_v2.py` | portão | **NÃO** | REBUILD | embute **15** gavetas; esta base tem **16** |
| `scripts/generate_map_v2.py` | estado | parcial | REBUILD | acoplado ao esquema antigo; e tem de passar a permitir `CANONICAL = NO` |
| `tests/test_map_v2.py` | provas | **NÃO** | REBUILD | 22 ocorrências da topologia antiga, como asserção |
| `tests/red_team.py` | ataques | **NÃO** | REBUILD | 17 ocorrências; e o ataque 4 só via se o artefato **existe**, nunca se ele **prova** |
| `model/machine.model.json` | modelo | — | **DISCARD** | é a topologia que reprovou |
| `data/machine.measured.json` | medido | — | **DISCARD** | medição da árvore errada |
| `data/state.v2.generated.json` | estado | — | **DISCARD** | derivado do modelo que reprovou |
| `provas/*.png` | prova visual | — | **DISCARD** | retratam o mapa que reprovou |
| `README.md` | doc | — | REBUILD | descreve a topologia antiga |

**Transplantado: 3 ficheiros.** Nenhum modelo, nenhum estado gerado, nenhuma
aresta, nenhum dono, nenhuma autoridade, nenhuma contagem.

A primeira tentativa não foi apagada: vive em `claude/dazzling-sagan-s53805`,
e as ideias do validador e do red team continuam lá para serem lidas — como
referência, nunca como dado.

---

## 5 · O QUE ESTA MISSÃO NÃO FEZ

Nada da máquina foi tocado: Collection, Intelligence, Admission, Sala de
Espera, SCRAP, banco, migrations, Portal e ferramentas ficaram exatamente como
estavam na base.

**SCRAP-SOCIAL.** Na primeira tentativa, `.github/workflows/scrap-social.yml`
foi reatribuído a `C-SINTONIA-SCRAP`, contra uma decisão que já existia. Nesta
base o dono é **`C-SCRAP-ROTA`** (zona `Z-EXECUCAO`), e assim fica. A
reatribuição errada **não** atravessou: ela só existiu na branch antiga.

**EOL.** O ruído CRLF↔LF que inflou um diff para 18 mil linhas era um defeito
da linhagem de `main`. Nesta base tudo está em LF — fonte e cópia publicada —
e os três ficheiros transplantados também. **Nada foi corrigido porque nada
estava errado aqui.**

---

## 6 · O PRÓXIMO PASSO

Reconstruir o **modelo canónico** do V2 a partir das autoridades da secção 2 —
começando pela Bíblia e por `docs/biblia/leis.json`, que já é legível por
máquina.

As medições desta base (`system-map/data/*.observada.json`,
`topologia.generated.json`, `donos.generated.json`, `fluxo.generated.json`)
são material de **medição**, e entram como `observado_por`. Os 158 cartões do
mapa desta base **não** são Bíblia: são outra projeção, e o V2 não os herda.

    SYSTEM MAP OBSERVA A MÁQUINA. NÃO A DEFINE.
