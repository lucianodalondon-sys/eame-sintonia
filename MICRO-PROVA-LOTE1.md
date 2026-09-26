# MICRO-PROVA-LOTE1 · 26/09 (03:45–06:30 local) · sem rede real

Ramo **`destravar-v1`** (a partir do vivo `83de0ccd`), não instalado. Vivo e Sala não tocados; 0 pedidos à internet.

## 0 · Uma coisa dita primeiro

**Não existe hoje, no robô, uma peça que COLHA a prova de território.** O canal de decisão existe
(`curadoria/decisao_semantica.py`, lê `DECISOES-SEMANTICAS-V1.json`) e o QUALIFY consulta-o; as provas da missão S2
foram colhidas à mão (bytes em `%TEMP%\s2`), sem ferramenta no Git. Por isso escrevi **uma peça fina**,
`curadoria/colher_prova_territorio.py`, feita SÓ de peças da casa (portão de consenso, leitor do canário, robots): lê 3
páginas por candidata e escreve PROPOSTAS no formato exato do canal. **Não é rota de coleta**: não escreve RAW, não
toca a Sala, não enfileira. Tudo o resto do circuito é o orquestrador/robô que já existe.

## 1 · Os 20 do lote 1 (`curadoria/MICRO-PROVA-LOTE1.json`)

Critério: **classes escassas** na coorte (fontes READY hoje por classe: T7 48 · T8 23 · T2 23 · T12 21 · **T5 19** ·
T10 8 · **T1 7 · T3 7** · T9 6 · T11 3 · T4 1) e o **foco do dono** (pesquisa e agronomia). **20 domínios distintos** =
**1 ronda**, ≤5 pedidos por domínio (teto D38).

| grupo | candidatas |
|---|---|
| janelas fitossanitárias/agrometeo (T3/T2 — D29; T3 só tem 7 READY) | Condifesa Ravenna · Condifesa Lombardia Nord-Est · Condifesa TVB · FEM Bollettini tecnici · Liguria Bollettini (Agriligurianet) · SIPaV · LaMMA Toscana |
| pesquisa (T5 — foco do dono) | Agraria Foggia · D3A Univpm · DAGRI Firenze · DISTAL Bologna · TESAF Padova · DBT Verona · Laimburg · ENEA · J. Entomological & Acarological Research · Italian J. of Food Science |
| agências agrícolas regionais | Veneto Agricoltura · Laore Sardegna |
| agronomia (base de dados) | Fitogest (agrofármacos) |

**Fora, e porquê:** as ordens provinciais de agrónomos (**D52**: saíram por decisão do dono); **Rete Rurale** (robots
`Visit-time` 01–03 UTC → lote próprio nessa janela); a 2.ª de um mesmo domínio (IJ Food Safety, pagepressjournals.org) → lote 2.

## 2 · Roteiro para o coordenador (numerado)

`V=…/source-curator-service-v1` (vivo). Rede só pela VPN IT; LOCK-PESADO não é preciso para a colheita (≤100 pedidos),
mas é regra da máquina para qualquer ensaio pesado.

**A · colher as provas — o robô pode CONTINUAR a correr** (a colheita não escreve livro nenhum):
1. Instalar `destravar-v1` (só ferramentas novas; o robô não as chama) — ou correr a partir de uma cópia do ramo.
2. VPN IT ligada; portão: `py superficie/rede.py --portao-de-egresso IT` → PASS (a ferramenta volta a pedir o portão
   **antes de cada candidata** e não pede nada sem PASS).
3. `py curadoria/colher_prova_territorio.py --lote=curadoria/MICRO-PROVA-LOTE1.json --bytes=<pasta FORA do Git> --saida=PROPOSTAS-LOTE1.json`
   — ~100 pedidos (≤5 por site, 3 s entre pedidos), 20 sites, ~10 min.
4. Grava: bytes de cada página em `<pasta>/<CAND>/n_PAPEL.bin` (fora do Git; o sha256 fica na proposta);
   `PROPOSTAS-LOTE1.json` com `TERRITORIO = A_DECIDIR` e a `SUGESTAO_DA_REGRA` (a regra do Atlas pelo nome/título).

**B · decidir — Opus/humano, sem rede:**
5. Para cada proposta com `PROVA_COMPLETA = true`: ler as 3 páginas e escrever `TERRITORIO` (T1..T12, tabela abaixo),
   `PAIS` **da prova**, `DECIDIDO_POR`, `PORQUE`. As de prova incompleta **não se decidem** (falta de prova não é prova).

**C · entrar no circuito — o robô PARADO** (um só escritor na fila e no livro):
6. Parar o robô (`CUTOVER-RUNBOOK.md` passo 1). Guardar `git status`/`git diff` do vivo.
7. `py curadoria/colher_prova_territorio.py --aplicar=DECIDIDAS-LOTE1.json` — escreve em `curadoria/DECISOES-SEMANTICAS-V1.json`
   só as que o **validador do próprio canal** aceita; um «NAO SEI» antigo da mesma candidata é substituído e guardado em
   `ANTERIOR` (duas entradas = conflito que o QUALIFY recusa).
8. Reabrir as QUALIFY pela porta da fila:
   `py -c "import sys; sys.path.insert(0,'curadoria'); import fila as F; print(len(F.recuperar_bloqueadas_por_defeito(['territorio indeterminado pelo nome'], {F.QUALIFY})))"`
   → reabre as **212**; as que não têm decisão **voltam a bloquear sozinhas, sem rede** (medido: 192/192 BLOCK, 0 pedidos).
9. **Portão IT confirmado outra vez** — ⚠️ o worker NÃO verifica o egresso por si (medido: nenhuma chamada a
   `portao_de_egresso` em `worker.py`/`canario.py`); o canário das fontes novas vai à rede pela saída que a máquina tiver.
10. Religar o robô. Ele faz, sozinho: QUALIFY (aloca o SOURCE_ID canónico pela decisão) → BUILD_CONTRACT (molde da casa)
    → VALIDATE_ROUTE (robots) → CANARY (régua DETAIL/v1) → **READY_FOR_COLLECTION**, ou REPAIR/FAILED com motivo.
    Grava: fila, ledger, evidência, `SOURCE-ID-ALLOCATION-V1.json`, `italy_contracts_curator.json`.

**D · da fonte PRONTA à coorte:**
11. Canário da rota do lado do coletor, para os SOURCE_ID novos que ficaram READY:
    `py medidas/canario_rotas_elegiveis.py --fontes=<IDs> --juntar` (≤4 pedidos por fonte) → `ROTAS-ELEGIVEIS-V1.json`.
12. O supervisor chama o **onboarding** sozinho (`onboardar_se_mudou`) — ou `py curadoria/onboardar_rotas_provadas.py --aplicar`:
    entra a linha em `regras/italy_contracts_onboarded.json` para quem é **ELIGIBLE no portão + ROUTE_PROVEN** com o mesmo contrato (≤7 dias).
13. A coorte da onda seguinte é congelada por `ferramentas/big_collection/coorte_unica.py` sobre o plano da onda.
**RAW:** nada é escrito em RAW até a onda colher; as provas de território vivem fora do Git com sha256.

**O que conta como prova, por gaveta** (1 página INSTITUCIONAL + 2 de CONTEÚDO, URLs e bytes distintos):
T1 produtor/OP/consórcio — campanha e produção · T2 serviço meteo/agrometeo/ARPA — boletins datados · T3 serviço
fitossanitário/consórcio de defesa — avisos datados · T4 quem emite norma — decretos/registos · T5 universidade/instituto
— publicações/projetos · T6 página oficial da PESSOA (D21/D24) · T7 associação/cooperativa/ordem — notícias técnicas ·
T8 redação — artigos agrícolas · T9 empresa — comunicados · T10 bolsa/observatório — cotações · T11 feira — edição ·
T12 ente público — atos e avisos agrícolas.

## 3 · Ensaio a seco (cópia fiel do vivo + servidor local)

Cópia: checkout do ramo (`83de0ccd` + as ferramentas) + os **16 livros sujos do vivo copiados e conferidos (16/16 sha256
iguais)**. Um **servidor HTTP real em 127.0.0.1** faz de conta que é os 20 sites; `urllib.request.urlopen` (o único ponto
por onde o Curator pede páginas) é redirigido para ele, e o `geturl()` devolve o endereço original. Toda a outra rede
fechada (proxy para porta 9). Ferramenta: `curadoria/ensaio_micro_prova_lote1.py`.

**Desenho** (escolha do ensaio, **não previsão**): 17 sites bons; 3 falham de propósito, um em cada ponto.

**Resultado** (`curadoria/ENSAIO-MICRO-PROVA-LOTE1.json`): **0 pedidos à internet**, 202 ao servidor local (20 hosts):

| | candidatas |
|---|---|
| prova completa (≤5 pedidos cada: robots, entrada, chi-siamo, 2 conteúdos) | 18 |
| decisão entrou no canal pelo validador do canal | 18 |
| QUALIFY → SOURCE_ID canónico (ex.: Condifesa Ravenna IT-T3-067, ENEA IT-T5-190, LaMMA IT-T2-165) | 18 |
| BUILD_CONTRACT → VALIDATE_ROUTE → CANARY → **READY_FOR_COLLECTION** | 17 |
| portão **ELIGIBLE** + rota do coletor **ROUTE_PROVEN** + linha na tabela do coletor | **17 = PRONTA** |
| **NÃO**, cada uma no ponto desenhado | 3 |

- **Fitogest** (robots proíbe tudo): 1 pedido (o robots), prova parada, sem decisão → QUALIFY volta a BLOCK.
- **Laimburg** (casca JS, os mesmos bytes em todo o lado — como medido a 23/09): 2 pedidos, prova incompleta, sem decisão → BLOCK.
- **Laore** (notícias curtas): decidida T12, IT-T12-152, contrato e rota OK, **canário PASS_PARCIAL** («o gate passou por
  não parecer capa, mas o corpo é MIXED/NAO_SEI») → CONTRACTED_CANARY_FAILED → portão `ESTADO_NAO_READY` → rota do coletor
  `CAPABILITY_BLOCK`.
- As **192 QUALIFY reabertas fora do lote**: 192 BLOCK, **0 tentativas de rede** (`ENSAIO-REABERTAS-SEM-REDE.json`).

⚠️ **Erro meu, corrigido:** na 1.ª corrida a «notícia curta» de Laore tinha 4 parágrafos de ~380 caracteres (~1 500,
acima do mínimo de 800) e **passou** — o desenho estava errado, não o robô. Corrigi para 1 parágrafo de ~190 e corri de
novo numa cópia **nova**. A 1.ª corrida fica guardada (`ENSAIO-MICRO-PROVA-LOTE1-CORRIDA1-DESENHO-ERRADO.json`).

## 4 · Quantas fontes entrariam na coorte da 4.ª onda

| cenário | como | fontes novas |
|---|---|---|
| **rendimento medido (18,9 %)** — o pedido | 20 × 18,9 % (das 822 fontes com contrato, 155 READY) | **≈ 4** |
| **melhor caso** | todas as 20 com prova completa, decisão, canário e rota | **20** |
| ⚠️ cauteloso (a considerar) | a PROVA também falha: na S2, 25 decididas em 181 tentativas (13,8 %); 20 × 13,8 % × 18,9 % | **≈ 0,5** |

A coorte congelada da 3.ª onda tem 60 fontes: o lote 1 leva-a a **~64** no rendimento medido, **80** no melhor caso.
O 13,8 % da S2 foi medido com outro método (páginas à mão, sem «chi siamo»): é um aviso, não uma previsão.

## Código (ramo `destravar-v1`)

`02cb2c43` `colher_prova_territorio.py` + testes 8/8 + `MICRO-PROVA-LOTE1.json` · `c22001c2`/`1f0fd2d1` o ensaio a seco ·
e o commit desta entrega (resultados do ensaio, verificação das 192, relatório, peça no mapa). Mapa: INTEGRA (PRONTO-SEM-MAPA).

## EM PALAVRAS SIMPLES

- Escolhi **20 fontes** para a primeira rodada: consórcios de defesa das plantas, boletins, departamentos de agronomia
  e institutos de pesquisa — exatamente o tipo que o robô tem pouco e o dono mais quer.
- Faltava uma peça: **ninguém tinha a ferramenta que lê as 3 páginas de prova** (quem a fonte é + 2 coisas que ela
  publica). Escrevi-a só com peças que o robô já tem; ela não coleta notícia nenhuma, só guarda a prova.
- Testei o caminho inteiro **sem internet**, com sites de mentira aqui na máquina: das 20, **17 chegaram a «pronta para
  coletar»** e 3 pararam exatamente onde eu tinha armado a falha. Na primeira tentativa eu armei mal uma das falhas
  (a notícia «curta» não era curta) — corrigi e testei de novo.
- **Quanto se ganha de verdade:** pela taxa de hoje, **umas 4 fontes novas** na próxima onda; no melhor caso, 20. Pode
  ser menos, porque achar a prova certa na internet já falhou muito antes.
- O coordenador colhe as provas com o robô ligado; para **pôr as decisões dentro** do robô, tem de o parar um instante.
