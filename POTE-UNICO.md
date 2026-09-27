# POTE-UNICO — uma corrida da Intelligence, um pote, o casco lê

> **EXPERIMENTAL · NAO_PARA_CLIENTE.** Nada publicado, nenhum deploy. O pote real vive fora do Git e do
> deploy (`sintonia-pote.js`, como os `.local.js` da Sala). No repositório só há dado **sintético declarado**.
> D95/D96 **não estão escritas no repositório**: o contrato abaixo segue o resumo delas no pedido da missão.

## 1 · O contrato v2 — `POTE_INTELLIGENCE_CASCO/v2`

Dono: [`pacote/pote_intelligence_casco.py`](pacote/pote_intelligence_casco.py). Um ficheiro **por corrida**.

```
POTE
├─ SCHEMA "POTE_INTELLIGENCE_CASCO/v2" · MARCA "EXPERIMENTAL · NAO_PARA_CLIENTE" · NAO_PARA_CLIENTE true
├─ INTELLIGENCE_RUN_ID   obrigatório (sem ele: recusado)
├─ SOURCE_HEAD · CORTE   da corrida; ausentes = "NAO SEI" à vista (nunca inventados)
├─ RESULT_STATE · RUN_SCHEMA · CORRIDA_SINTETICA · ENTRADA ("CORRIDA" | "PAYLOAD_V1") · LEI
├─ COMPARTIMENTOS  (os doze, sempre todos)
│   └─ <comp> { NOME_IT, VISTAS_DO_CASCO[], ESPECIES_ADMITIDAS[], CONTRATO_CHAVES[],
│              ESTADO "COM_OBJETOS" | "VAZIO", PORQUE_VAZIO, PORQUE_TEXTO,
│              OBJETOS[], LACUNAS[], RECUSADOS_AQUI, UNIVERSO{INTELLIGENCE_RUN_ID, OBJETOS, LEITURA} }
│        OBJETO { OBJETO_ID, ESPECIE, ESPECIE_DITA_POR ("INTELLIGENCE" | "CONTRATO_V1"),
│                 ESTADO "EXPERIMENTAL_CANDIDATE", MARCA, CHAVES{contrato, NAO SEI por extenso},
│                 CHAVES_NAO_SEI[], FORA_DO_CONTRATO{nome: valor}, PORQUE, CONTRADIZ, INCERTEZA,
│                 PROVA[ { ITEM_ID, CORRIDA_UPSTREAM, RAW_OBSERVATION_ID, SOURCE_ID, DOCUMENT_ID,
│                          URL, PUBLICADO_EM, COLHIDO_EM, FACT_TIME, INTELLIGENCE_RUN_ID } ] }
├─ LACUNAS_SEM_COMPARTIMENTO[]
└─ RECUSADOS[ { COMPARTIMENTO, OBJETO_ID, MOTIVO, DETALHE } ]
```

| compartimento | ferramenta | vistas do casco que o leem | espécies admitidas |
|---|---|---|---|
| `meeting` | Radar delle Opportunità | `#meeting` (+ `radar`, `msignals`, `mradar`) | OPORTUNIDADE · CROSSING · FINDING · SINAL |
| `future` | **Radar Futuro** | `#radarfuturo` | **só** FATO_PRESENTE_SOBRE_O_FUTURO |
| `windows` · `market` · `voices` · `competitors` · `science` | as de sempre | a do mesmo nome | SINAL · FINDING · CROSSING |
| `portfolio` | Portafoglio / Etichette | `#portfolio`, `#etichette` | SINAL · FINDING · CROSSING |
| `archive` | Archivio (objetos que a corrida produziu) | `#archive`, `#future` («Archivio segnali») | SINAL · FINDING · CROSSING · OPORTUNIDADE · FATO_PRESENTE_… |
| `sources` | Registro delle fonti | `#sources` | **só** RENDIMENTO_DE_FONTE |
| `field` · `casa` | — | nenhuma (sem rota / portão da casa) | nenhuma → `CASCO_SEM_CONTRATO_DE_INTELLIGENCE` |

⚠️ **O compartimento `future` é o Radar Futuro; a vista `#future` do casco é o «Archivio segnali» e lê `archive`.**
O nome igual não é a mesma coisa — o casco já as tratava como populações separadas.

**Porquês de um vazio:** `CASCO_SEM_CONTRATO_DE_INTELLIGENCE` · `SEM_OBJETOS_NESTA_CORRIDA` ·
`CORRIDA_<estado>` (ERROR, NOT_RUN, RUNNING, EMPTY_RESULT…) · `ENTRADA_V1_SEM_VAGA`.

**Entrada:** o livro da corrida (contrato v1 + `SOURCE_HEAD`, `CORTE`, `ESPECIE` por objeto, `URL`/datas na
prova) **ou** um payload `PONTE_INTELLIGENCE_CASCO/v1` já pronto (a escolha é pelo `SCHEMA`, nunca adivinhada).
Do payload v1: espécie = SINAL (é o que o objeto v1 é por contrato), URL/datas/SOURCE_HEAD/CORTE = `NAO SEI`,
e a prova é a que a v1 já conferiu (`PROVA_CONFERIDA_POR`).

## 2 · O que foi feito, e onde

| o quê | onde |
|---|---|
| **P1** — a LINEAGE indexa-se pelo par `(CORRIDA_UPSTREAM, ITEM_ID)`; sem upstream e item em 2 corridas → `PROVA_AMBIGUA` | `pacote/ponte_intelligence_casco.py:160`, `:174`, `:184`, `:211` |
| a regra de G0 passa a ser parâmetro (`admite`), para o pote a **chamar** em vez de a copiar | `pacote/ponte_intelligence_casco.py:184` |
| os doze compartimentos, vistas e espécies | `pacote/pote_intelligence_casco.py:119` |
| **P2/P5** — facto futuro bloqueado em G0 **só** por `FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA` prova um FATO_PRESENTE_SOBRE_O_FUTURO, e nada mais | `pacote/pote_intelligence_casco.py:95` e `:198` |
| espécie fora do compartimento é recusada (futuro nunca vira oportunidade; o pote não muda espécie) | `pacote/pote_intelligence_casco.py:276` |
| **P3** — Registro: `RENDIMENTO_DE_FONTE` provado só pela própria fonte; Archivio dos objetos produzidos | `pacote/pote_intelligence_casco.py:288` (e `COMPARTIMENTOS`) |
| **P4** — fora do contrato viaja com **nome e valor** (FACT_LOCATION continua FACT_LOCATION; REGION_ID fica NAO SEI) | `pacote/pote_intelligence_casco.py:254` |
| prova até ao RAW com URL e datas; publicação nunca vira tempo do facto | `pacote/pote_intelligence_casco.py:212` |
| payload v1 → pote (e o `future` da v1, que era o Archivio segnali, cai em `archive`) | `pacote/pote_intelligence_casco.py:162`, `:414` |
| portão de saída independente | `pacote/pote_intelligence_casco.py:494` |
| destino: dentro do portal **só** `client/sintonia-pote.js` | `pacote/pote_intelligence_casco.py:569` |
| **casco** — carregador (só com `?pote=local`) + leitor (FILTER/EXPLAIN/RENDER; sem sort, sem cruzamento) | `italia-portale/client/sintonia-pote-casco.js:21`, `:78`, `:100`, `:139` |
| futuro visualmente diferente: tracejado, azul secundário, «NON è un'opportunità»; oportunidade verde | `italia-portale/client/sintonia-pote-casco.js:63` |
| URL que não é http(s) não vira link | `italia-portale/client/sintonia-pote-casco.js:110` |
| portal: `<script>` do carregador, precedência (as bandeiras do legado apagam-se), bloco único | `italia-portale/client/portale.html:80`, `:4056`, `:4058`, `:12232`, `:3637` |
| fora do Git e do deploy | `italia-portale/client/.gitignore`, `italia-portale/client/.vercelignore`, `.vercelignore` |
| mapa: `C-POTE-INT-CASCO` (Z-PACOTE), `C-PROVA-POTE-CASCO` (Z-PROVA), leitor em `C-PORTAL-MODELO` | `system-map/data/architecture.declared.json` |

**Sem telas novas:** o bloco do pote é a MESMA rota de cada ferramenta, que com o pote desenha o compartimento
em vez do legado. Sem pote, o casco fica igual (provado: P1 do teste do casco e os 82 portões do portal).

## 3 · Comando para o coordenador (local, com dado real)

```bash
# a partir do livro/entrada de uma corrida (o que o bot da Intelligence monta):
py pacote/pote_intelligence_casco.py C:/…/PARA-O-CASCO-Rn/ENTRADA-DA-PONTE-Rn.json italia-portale/client/sintonia-pote.js
# ou a partir de um payload PONTE_INTELLIGENCE_CASCO/v1 já gerado:
py pacote/pote_intelligence_casco.py C:/tmp/ponte/payload-r2-real.json italia-portale/client/sintonia-pote.js
# depois abrir (o ?pote=local é obrigatório):
#   italia-portale/client/portale.html?pote=local#meeting     (ou #radarfuturo, #sources, #archive, …)
git check-ignore italia-portale/client/sintonia-pote.js   # tem de responder o caminho (= fora do Git)
```

Qualquer outro destino dentro de `italia-portale/` é recusado (código 3). Para o Radar Futuro e o Registro
encherem, a Intelligence tem de pôr os objetos em `ITENS_POR_FERRAMENTA.future` / `.sources` com a `ESPECIE`
certa; a entrada R2 de 26/09 não os trazia (`NAO SEI` se a LINEAGE dela traz `G0_FALTA` — o motor escreve-o).

## 4 · Testes — antes/depois, pelo NOME

Base = `20c155e` (HEAD recebida), depois = `d827981`, cópias limpas, mesmo corredor, rede fechada.

| bateria | base | depois |
|---|---|---|
| `provas/boletins_data_local/testes_por_nome.py` — 84 módulos, 1263 testes | 91 falhas | as mesmas 91, nome a nome · **0 novas** |
| portões do portal (`italia-portale/audit/*.mjs`, `audit/casco/*.mjs`) — 82 | 48 saem ≠ 0 | os mesmos 48, mesmo código · **0 novas** ¹ |
| `tests/test_ponte_intelligence_casco.py` | 35/35 | **39/39** (+G6…G9) |
| `tests/test_pote_intelligence_casco.py` (corre o `.mjs`) | não existe | **45/45** |
| `tests/test_pote_no_casco.mjs` | não existe | **93/93** provas |

¹ `acceptance.mjs` mostrou 4/71 contra 3/71: a diferença é `B2` e depende só de
`client/system-map/deployment.generated.json` (artefato de build, `.gitignore`) — o meu script criava-o entre
passagens. Medido: com o artefato, B2 passa nas duas árvores; sem ele, reprova nas duas com o mesmo detalhe.

**Ajustes declarados (só dos meus testes/mutantes da ponte, nenhum da casa):**
`G7` — antes, dois `PASSOU` sem `CORRIDA_UPSTREAM` passavam; um ITEM_ID em duas corridas upstream são duas
observações (decisão P1 desta missão). Mutantes `M6`, `M7`, `M19`, `M21`, `M22` reescritos para o código novo; `M23` novo.
G7 **falha no código antigo** e passa no novo; G6/G8/G9 já passavam no antigo e ficam de guarda.

## 5 · Mutação

- **Pote + casco: 29/29 mortos** (`provas/_mutantes_pote_casco.py`) — 17 no pote, 9 no leitor JS, 3 na precedência do `portale.html`.
- **Ponte v1 + esqueleto: 32/32 mortos** (`provas/_mutantes_ponte_casco.py`).

## 6 · Design (lei do CLAUDE.md)

O Claude Design **não foi consultado** (a missão proíbe sites externos). Reutilizei os padrões que o próprio
casco já usa (cartão da Sala, aviso âmbar, pílula de estado) e os tokens do extrato ADAMA.

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND   (no extrato local; no Claude Design: NAO SEI)
NEW_PATTERN_REQUIRED = YES
```
Motivo: distinguir a espécie FATO_PRESENTE_SOBRE_O_FUTURO da OPORTUNIDADE — borda tracejada e pílula em
`--color-secondary-blue` (#00698F) contra `--color-corporate-green`. Se existe componente oficial: **NÃO SEI**.

## 7 · O que NÃO SEI / fica por decidir

1. `casa.html` **não** lê o pote: o portão `VIEW_READS_ONLY_ITALY_CASA` (`audit/casa-gate.mjs`) só lhe deixa
   ler `ITALY_CASA`. Ligar é decisão do dono (o compartimento `casa` existe e diz o porquê).
2. `field` não tem rota no casco. Vistas de detalhe (`mcase`, `case`, `window`…) e a busca continuam no legado.
3. As chaves de `future`, `archive` e `sources` são proposta desta missão (D84 não as tinha; D95/D96 não estão no repo).
4. Se a entrada R2 real traz `SOURCE_HEAD`, `CORTE`, `ESPECIE`: **NÃO SEI** (não está na nuvem).
5. As duas portas (`CASCO_ENTRADA_INTELLIGENCE_EXPERIMENTAL/1` da Sala e este pote) continuam as duas.

## EM PALAVRAS SIMPLES

Antes, a vitrine (o portal) mostrava um prato congelado do dia 7 e pratos de mostruário. Agora há **um pote por
fornada** da cozinha (a Intelligence), com **uma gaveta para cada balcão** da vitrine.

- Cada coisa no pote diz **o que é** (sinal, oportunidade, «facto de hoje sobre o futuro», rendimento de uma
  fonte…) e leva a **nota fiscal até ao documento bruto**, com o link e as datas.
- Gaveta vazia vem com um **bilhete a dizer porquê**.
- O «facto sobre o futuro» tem a **sua gaveta** (Radar Futuro) e outra **cor** — nunca é vendido como oportunidade.
- Se o pote estiver no computador e se abrir o portal com `?pote=local`, **o pote manda**; sem ele, tudo fica como estava.
- O pote nunca entra no Git nem vai para o ar. Provei plantando 61 defeitos de propósito: os testes apanharam os 61.
