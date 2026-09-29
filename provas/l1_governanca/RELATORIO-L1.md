# L1-GOVERNANCA-PREVIEW — relatório (D140 · D141 · D152 · red team · auditor)

Ramo `claude/l1-governanca-preview-v1`, sobre a produção `852ec0f0b` (contida).
Um commit não conhece o próprio SHA: o SHA final pronto para integrar está na
mensagem de entrega e em `C:/Users/London1/auditoria-madrugada/HANDOFF-VIVO.md`.

## Estado provado

```
COLLECTION_FOUNDATION_CLOSED = NAO     (leis/fundacao_da_coleta.py: constante False; TRAVA: "NAO")
PRODUCAO_LIBERADA            = NAO
E2E_PREVIEW_EXCEPTION        = SIM     (EXCECOES_CONTROLADAS[PREVIEW_E2E], autoridade D140)
```

## Onde a exceção vive

- **Quem decide:** `leis/fundacao_da_coleta.py` → `pode_atravessar_a_trava`,
  `excecao_vigente`, `artefatos_autorizados`. É o único sítio que responde «passa?».
- **Quem declara:** `docs/operacao/TRAVA-DA-INTELIGENCIA.json` →
  `EXCECOES_CONTROLADAS[PREVIEW_E2E]` (âmbito exato, pastas do LAB, bloqueio de
  política do C8, critérios A..N). A guarda lê-o; sozinho não abre nada.
- **Autoridade:** `docs/decisoes/DIARIO-DE-DECISOES.md` → D140 (e D141 com os 9
  requisitos do loop vivo, literal da fonte).

## O que mudou depois de 7f3dc857c (red team do bot Luciano + auditor NAO_INSTALAR)

O auditor (`VERIF-L1-7f3dc857c.md`) mostrou 13 de 16 pedidos hostis a atravessar;
o red team mostrou que três campos eram texto onde devia haver prova. Corrigido:

| antes | agora |
|---|---|
| branch comparada crua | normalizada (`refs/heads/`, `origin/`, caixa, espaços) antes de comparar, na guarda e em `artefatos_autorizados` |
| host comparado cru (`==`, `endswith`) | só nome de host limpo (urllib.parse): esquema, caminho, porta ou utilizador = recusa |
| chaves desconhecidas ignoradas | lista FECHADA de chaves no pedido, no destino, na entrada, no snapshot e na prova do LAB |
| `consumido_em` só no topo | em qualquer nível e em qualquer caixa, incluindo dentro do pote |
| C8 `startswith('FALHOU')` | «falhou» em qualquer caixa e sítio = falha; C8 tem de COMEÇAR por uma decisão `Dnnn` do diário, do dono, não revogada |
| D140 contava se a marca aparecesse | só como cabeçalho numa linha própria, e não revogada («REVOGADA — ## D140», «REVOGA D140», «D140 foi REVOGADA») |
| LAB: `ONDE` qualquer texto | JSON numa pasta exclusiva do LAB, sha256 fixado no pedido; a entrada do par (`POTE_SHA256`, `RUN_ID`) diz `VEREDITO=PASS` e `LAB_ORIGIN=sintonia-lab` (rodada 3) |
| `READ_ONLY = True` só dito | a cópia da Sala existe, o sha256 bate, o CORTE do pote cita-a, nada aponta a Sala viva (54330, DSN do ambiente, Supabase) |
| branch/host alegados | medidos em runtime: branch real (git/build) igual à declarada; host de preview responde `deployment.generated.json` com `SOURCE_BRANCH` igual à declarada |

### Rodada 3 (VERIF-L1-cb8f20bcf: LB1–LB6)

A prova do LAB segue o **formato real do LAB**: um objeto JSON por ficheiro,
`PROVA-REVERSA_pote-<sha16>_run-<RUN_ID>[-N].json` (nunca sobrescreve), com
`LAB_ORIGIN`, `DATA_UTC`, `POTE_SHA256` (canónico), `RUN_ID`, `ENVELOPE_HASH`,
`VEREDITO` (só PASS|FAIL) e o resto. A guarda compara por IGUALDADE DE CAMPO o par
(`POTE_SHA256`, `RUN_ID`), exige `VEREDITO=PASS`, `LAB_ORIGIN=sintonia-lab` (e não o
produtor), `ENVELOPE_HASH` igual ao do pote (ou `NAO_EXISTE_NO_POTE_PUBLICADO`) e o
nome do formato real. Com várias versões do mesmo par vale a MAIS RECENTE pelo
`DATA_UTC` de dentro do JSON (nunca pela ordem do nome: `-10` vem antes de `-2`);
empate, data ausente ou inválida = FAIL; um FAIL recente derruba um PASS antigo.
Índice, lista, texto solto ou `POTE_REJEITADO` com este pote = recusa.

NÃO SEI: o pote v2 de hoje não tem campo de envelope (nem o schema nem o pote R9).
A guarda procura `ENVELOPE_HASH` no topo do pote; se o produtor usar outro nome,
a regra do envelope não o apanha — confirmar com o dono do pote. `PASTAS_DO_LAB` passou a ser só
`C:/Users/London1/sintonia-lab-provas/`; o pote do produtor nessa pasta ou em
subpasta = recusa (caminho resolvido, prefixo de diretório).

### Rodada 4 (VERIF-L1-dec120851)

- **V4a/V4b:** as versões do par procuram-se em TODA a árvore de `PASTAS_DO_LAB`
  (recursivo), não na pasta que o pedido escolheu; duas cópias da mesma prova = empate = FAIL.
- **V3b:** `DATA_UTC` mais de 5 min no futuro = inválida = FAIL.
- **K1:** lista FECHADA de chaves na prova (as 12 do formato real); desconhecida = recusa.
- **K2:** `VEREDITO` exato `PASS`|`FAIL`; chave com «rejeit» em qualquer caixa e nível = recusa.
- **K3:** `VEREDITO=PASS` com `VEREDITO_DETALHE` que diga rejeit/falh/fail = recusa.
- **K4:** `VEREDITO=PASS` exige `ELOS` E1..E7 todos `PASS` ou `OK`; qualquer outro valor = recusa.
- `LAB_ORIGIN` saiu da linha VERIFICADO e está em ALEGADO.
- Mutantes: 84/84, com o sha da lei atual.
- Scripts de aceite do auditor: `contraprova_lab_l1_v2.py` 8/8; `ataque_lab_l1_v2.py` 24/26 —
  os 2 restantes são por desenho: **V3** espera que uma prova datada de 2099 passe (contra a
  regra 4 do coordenador) e **AUT1** corre depois de o próprio script plantar, na MESMA pasta
  do LAB, um ficheiro com o nome deste par e o conteúdo de outro (LB1), que envenena o par em
  toda a árvore (regra 3). Isolado, o AUT1 passa com `AUTORIA_PROVADA=false` (testes
  `LIMITE_…` e `test_LAB_ORIGIN_sai_como_alegado…`).
- Suposição declarada: os valores de `ELOS` são textos `PASS`/`OK`; se o LAB os escrever como
  objetos, a guarda recusa (falha fechado) — confirmar com o LAB.

**LIMITE_CONHECIDO:** `AUTORIA_DO_LAB = DECLARADA` (LAB_ORIGIN + pasta), **não**
provada criptograficamente — neste PC todos os agentes correm como o mesmo
utilizador Windows, e a pasta só impede reuso acidental e mistura. O que a guarda
PROVA é o vínculo (`POTE_SHA256`, `RUN_ID`), que impede prova de outro pote ou de
outra corrida. Falsificação deliberada por outro agente local fica fora do alcance
desta guarda e é coberta pela auditoria independente. A guarda diz isto no próprio
resultado (`AUTORIA_PROVADA=false`), e um teste reprova se ela passar a dizer mais.

O que continua ALEGADO e sai assim no motivo (não conta como prova):
`PARA_CLIENTE=False` (só restringe), o CONTEÚDO da prova do LAB, o AUTOR da prova
do LAB (`AUTORIA_PROVADA=false`), `TRANSACTION_READ_ONLY` dentro do CORTE.

## Bloqueio de política (decisão do dono)

`BLOQUEIO_DE_POLITICA_C8` na TRAVA: o contrato v2.2 exige C8 por objeto; a guarda
só aceita C8 com ID de decisão registada. Hoje nenhuma decisão do diário cobre a
liberação de itens NOVOS, e um C8 humano por objeto impede o loop vivo (D141,
requisito 9). Falta o dono decidir o critério — não é decisão desta missão.

## Os potes reais da R9 (`provas/l1_governanca/GUARDA-NOS-POTES-R9.json`)

RECUSADOS, sem nenhuma prova simulada: (1) nenhum ficheiro da pasta R9 tem o sha256
da cópia que o CORTE cita; (2) a prova reversa do LAB ainda não existe; (3) o C8
dos 2 objetos é texto livre («Luciano (dono), sala SINTONIA DIRETORIA 28/09: …»),
sem ID no diário.

## Provas

- `tests/test_excecao_preview_e2e.py`: casos (a)–(f), D152 (`PREVIEW_PODE_RECEBER=SIM`,
  `PRODUCAO_PODE_RECEBER=NAO`, `VAZAMENTO_PREVIEW_PARA_PRODUCAO=0`), red team,
  adendos, e um teste por pedido hostil do auditor (L01–L14).
- Mutantes: `provas/l1_governanca/mutantes_excecao_preview.py` → 59 mutantes, um por
  verificação; resultado em `MUTANTES-EXCECAO-PREVIEW.json`. Funciona em LF e em CRLF.
- Scripts do auditor contra um clone limpo: `ataque_guarda_l1_real.py` e `ataque_lab_l1.py`
  (resultados na entrega `auditoria-madrugada/ENTREGA-L1-R3.md`).

## Critérios A..N

Medidos pela lei, pela cadeia (`estradas-it.generated.json → CRITERIOS_A_N`):
PASS I, L · FAIL A, C, D, E, F, G, J, N · NAO_SEI B, H, K, M. Para o preview é
obrigatório o L; os 14 são exigidos para produção e para fechar a fundação.

## O que não foi feito

Nada instalado no vivo. Nenhum publicador real chama a guarda ainda: quem ligar o
Casco ao preview (L3) tem de chamar `pode_atravessar_a_trava`.

FIM
