# ONDA3-REBASE — o pacote da 3.ª onda sobre o vivo e5cd691f, o ensaio integrado e o plano — 25/09/2026

Ramo `onda3-pacote-v2`, a partir de `origin/servico-20260923-0923 @ e5cd691f` (PACOTE-TEMPO-LUGAR instalado).
**NÃO instalado. NÃO disparado.** Rede FECHADA; **0 pedidos**. ⛔ **D61: a 3.ª onda está em espera — nenhum passo
do plano corre sem ordem expressa do coordenador.**

## Em palavras simples

Juntei ao vivo novo as seis peças da 3.ª onda. Numa cópia fiel do vivo, com a tabela do coletor **do disco**:
entram **16** fontes no coletor (210 → 226), as prontas para colher passam de **29 para 61**, a coorte congelável
tem **60**, numa onda **correm 36** com **150 pedidos** e no máximo 5 por site (prova do teto **PASS**). Da
LEGACY-99 entrou o A (importar), o C e o D; o **B (YouTube pela rota do canal) entrou parado**, provado por
teste. Os testes de data e lugar dão o mesmo que na produção. O desfazer volta tudo ao vivo.

## 1 · A junção

| ordem | peça | commit | conflitos |
|---|---|---|---|
| 1 | onda3-pacote-v1 = contrato-44 v1 0d56bb95 + v3 34cb3e61 (D49), reparo-fontes-v3 3384c57d, hr6-v1 e5825dc0 + D51 (1f086968), ordens-63-v2 9260aa2e (D52) | d5ae60a6 | só gerados do mapa (o conflito D52 × REVISAO-15 já vinha resolvido, aprovado) |
| 2 | receita-t8-v1 (D48) | 59e23365 | só gerados do mapa |
| 3 | legacy-99-v2 (A + C + D; **B inerte**; **sem** a rota VIDEO da v3) | 6e51f88b | **1 de código**: `curadoria/worker.py` (VALIDATE_ROUTE) |

**DA-15/D67 aplicada:** no `worker.py` ficou a linha da **produção** (rota YouTube pelo Scrap, SOC2); a do B
(`CANARIO.url_da_rota`) saiu. **E mais uma coisa, para o B ficar mesmo parado:** o mesmo commit do B
(f75009d5) mudava `curadoria/escrever_contratos.contrato_youtube`, e com isso **todo contrato novo de
YouTube** passava a nascer na rota do B, pelo caminho normal do robô. Ficou a versão da produção nesse
ficheiro (só o B mexia ali; o A não depende dele). No `worker.py` ficam 2 linhas do B no canário
(`ADAPTER_ID == CANAL_PUBLICO_YOUTUBE_V1`), que só disparam para contratos com esse adaptador — **0 no livro do vivo, antes e depois da importação** (medido).

Porquê a v2 e não a v3 da LEGACY-99: na v3 estão a rota VIDEO (D53) e a junta da JANELA-FORMAS; o A e o B estão
num só commit (f75009d5) — a v2 é a última ponta com A+C+D sem VIDEO.

## 2 · As três condições da DA-15

| | prova | resultado |
|---|---|---|
| (1) nenhum passo importa/valida YouTube pela rota do B | `tests/test_onda3_b_inerte.py` (molde novo = produção; VALIDATE_ROUTE nunca chama `url_da_rota`; o lote do plano sem YouTube) + no ensaio: contratos com o adaptador do B no livro do vivo | **4/4 OK**; mutantes (a linha do B de volta → 2 vermelhos; o molde do B de volta → 1 vermelho); **0 antes · 0 depois** |
| (2) as 21 páginas web do A validam pela produção | ensaio: as 21 importadas pelos 2 lotes (`LOTES-A-HTML.json`, 19 + 2), `worker.etapa_validate_route` com robots simulado | **21 de 21 OK**, todas pelo INDEX_URL; ficam CANARY_PENDING (o robô mede com rede) |
| (3) testes de data/lugar sem regressão | os 25 ficheiros de teste que a produção trouxe desde 88ee046f, na produção pura e no ramo (`TESTES-TEMPO-LUGAR-*.txt`) | **iguais ficheiro a ficheiro**; o único vermelho (`test_collection_gate.test_todo_caminho_ate_ao_coletor_esta_declarado`) já vem da produção; migração 033: 15/15 nos dois |

Os 2 testes do B em `tests/test_importar_do_coletor.py` ficaram **saltados com o motivo** (não apagados).

## 3 · O ensaio integrado (`v2/ensaio/`, script `ensaio_onda3_v2.sh`)

Cópia = worktree destacada no HEAD do vivo **e5cd691f** + os **16 livros sujos do disco** (foto; o desfazer repõe
dela). Livros que o pacote muda no Git: **0**. Merge: 0 conflitos.

| passo | antes | depois |
|---|---|---|
| D49 + D51 | — | 5 duplicadas marcadas |
| D52 | — | 62 retiradas; reverter = livro de antes **byte a byte**; re-aplicar → 62 JA_APLICADA |
| tabela do coletor (disco) | 210 · ENTRA=0 | **226** · ENTRA=16 |
| bloco A (lotes A1 19 + A2 2) | — | 21 importadas → CANARY_PENDING; 0 com a rota do B |
| portão READY / elegíveis | 183 / 73 | 161 / 69 (−21 READY_LEGACY do A e −1 da T7-174 à espera do canário; −4 elegíveis da D49) |
| **prontas** | **29** | **61** (+32, 0 perdidas) |
| **coorte congelável** | — | **60** (fica fora a ISTAT, D45) |
| **correm numa onda** | — | **36** (24 saltam por teto de domínio, 1 parcial) |
| **pedidos previstos** | — | **150** · máximo 5 por domínio · prova-teto **PASS** |
| testes da junção | — | 118 Curator + 4 hr6 + 4 B-inerte + 23 (2 saltados) + 12 + 2 + 17 + 10 + 1 + 6 + 29 + 19 + motor 62/62 + teto 7/7 — **OK** |
| desfazer | — | `reset --keep` · 0 ficheiros de código ≠ vivo · HEAD = vivo · livros = foto · prontas 29 |

| universo | prontas antes | depois | coorte | correm |
|---|---|---|---|---|
| T2 | 7 | 7 | 7 | 6 |
| T3 | 0 | 1 | 1 | 0 |
| T5 | 6 | 10 | 9 | 3 |
| T7 | 13 | 20 | 20 | 17 |
| T8 | 0 | 13 | 13 | 1 |
| T9 | 0 | 1 | 1 | 1 |
| T10 | 3 | 3 | 3 | 3 |
| T12 | 0 | 6 | 6 | 5 |
| **janela D29 (T2+T3)** | **7** | **8** | **8** | **6** |
| **total** | **29** | **61** | **60** | **36** |

União por SOURCE_ID: 0 repetidos. Janela D29 = universos T2 + T3 (regra minha, declarada: a D29 não tem campo nas fontes).

**Depende do robô com rede (não somado):** as 21 do A (a LEGACY-99 mediu 11 elegíveis com rede), a IT-T7-174 (+1),
as 15 da REVISAO-15 (até +3 READY, sem contrato no coletor). O C da LEGACY-99 (re-medir READY_LEGACY com contrato
HTML, 10 por 24 h, 1 por domínio) só liga pelo serviço, ao religar o robô.

## 4 · Plano de instalação (executa: o coordenador; um escritor no vivo) — ⛔ só com ordem (D61)

```bash
VIVO=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
PACOTE=<SHA de ONDA3-REBASE PRONTO>
D=$(date +%Y%m%d-%H%M); CORTE=/c/cutover/onda3-v2-$D; mkdir -p $CORTE
LIVROS=$(git -C $VIVO --no-optional-locks status --short | grep '^ M' | awk '{print $2}' | tr '\n' ' ')
```

1. **Parar o robô** — `PARAR.flag`; esperar o supervisor sair (≤ 60 s); fechar o observador; 0 processos
   `supervisor|worker|ponte_automatica|observador`. ⏱️ começa o tempo parado.
2. **Backup** —
   `git -C $VIVO rev-parse --short HEAD` (TEM de dar **e5cd691f**, senão PARAR) ·
   `echo $LIVROS | wc -w` (16) ·
   `git -C $VIVO fetch origin onda3-pacote-v2 && git -C $VIVO diff --name-only HEAD $PACOTE -- $LIVROS | wc -l` (TEM de dar 0) ·
   `for f in $LIVROS; do mkdir -p $CORTE/$(dirname $f); cp $VIVO/$f $CORTE/$f; done; (cd $CORTE && sha256sum $LIVROS > SHA256-ANTES.txt)` ·
   `git -C $VIVO rev-parse HEAD > $CORTE/HEAD-ANTES.txt`.
3. **Merge** — `git -C $VIVO merge --ff-only $PACOTE`.
4. **Livros iguais** — `(cd $VIVO && sha256sum $LIVROS) | diff - $CORTE/SHA256-ANTES.txt && echo LIVROS IGUAIS` 🛑 se não: DESFAZER.
5. **Testes (sem rede)** —
   `py -B -m unittest curadoria.test_retirar_por_decisao curadoria.test_gatilho_discovery curadoria.test_gatilho_ocioso curadoria.test_retirar_duplicadas_d49 curadoria.test_canario_detalhe curadoria.test_reparar_contrato curadoria.test_revisao_ready curadoria.test_um_so_canario_promove curadoria.test_ready_split` (118 OK) ·
   `for t in tests/test_onda3_b_inerte.py tests/test_importar_do_coletor.py tests/test_legacy_recheck.py tests/test_legacy_colchetes.py tests/test_onda_web.py tests/test_onda_web_fontes.py tests/test_teto_dominio.py tests/test_canario_rotas_contrato_certo.py tests/test_onboardar_rotas_provadas.py tests/test_prova_teto_dominio.py; do py -B $t; done` ·
   `bash ferramentas/onda3_pacote/v2/tl-testes.sh $VIVO $CORTE/TESTES-TEMPO-LUGAR.txt` → comparar com `ferramentas/onda3_pacote/v2/TESTES-TEMPO-LUGAR-PRODUCAO.txt` ·
   `node regras/motor_de_rota_test.mjs ; node provas/teto_dominio_local.mjs`.
6. **Mapa** — com a LOCK-PESADO: `py system-map/scripts/correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`.
7. **Duplicadas e retiradas** — `py -B curadoria/retirar_duplicadas_d49.py` (5 APLICA) → `--aplicar` → (5 JA_APLICADA);
   `sha256sum curadoria/italy_contracts_curator.json > $CORTE/CONTRATOS-ANTES-D52.txt`;
   `py -B curadoria/retirar_por_decisao.py --decisao D52` (APLICA 62) → `--escrever` → (JA_APLICADA 62).
   Desfazer só da D52: `--decisao D52 --reverter --escrever` (= `CONTRATOS-ANTES-D52.txt`, provado).
8. **HR-6** — `py -B ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-174` → `--aplicar`.
9. **Bloco A — só as 21 páginas web, 2 lotes (nenhum canal YouTube)** —
   `py -B curadoria/importar_do_coletor.py` (conferir) →
   `py -B curadoria/importar_do_coletor.py --aplicar --ids=$(py -c "import json;print(','.join(json.load(open('ferramentas/onda3_pacote/LOTES-A-HTML.json',encoding='utf-8'))['LOTES'][0]))")` (19) →
   o mesmo com `['LOTES'][1]` (2). Conferir: nenhum contrato com `CANAL_PUBLICO_YOUTUBE_V1`.
10. **Provas de rota (0 pedidos)** — juntar PONTE + C44 + HR6 como no §5 passo 9 do `RELATORIO-E-PLANO-ONDA3.md`
    (válidas: PONTE até 02/10 06:38Z, C44 até ~09:46Z, HR6 até 10:42Z).
11. **Entrada no coletor (no DISCO; é livro, sem commit)** — `py -B curadoria/onboardar_rotas_provadas.py` (ENTRA=16) →
    `--aplicar` (226 fontes) → `py -B scripts/micro_coleta/micro_coleta.py plano` (esperado **61** prontas) →
    `git -C $VIVO push origin HEAD:servico-20260923-0923` (só o código do merge).
12. **Religar o robô** — `rm PARAR.flag`. O robô mede com rede (portão IT): as 21 do A, a IT-T7-174, as 15 da
    REVISAO-15; o C da LEGACY-99 começa a re-medir READY_LEGACY (10 por 24 h, 1 por domínio). ⏱️ acaba o tempo parado.
13. **Coorte da 3.ª onda PROVISÓRIA + só-plano + prova-teto (sem rede)** — como o §5 passo 12 do
    `RELATORIO-E-PLANO-ONDA3.md` (ensaio: coorte 60, correm 36, 150 pedidos, PASS). Congelar só por decisão.

**DESFAZER** (provado na cópia): `PARAR.flag` → `git -C $VIVO reset --keep $(cat $CORTE/HEAD-ANTES.txt)` →
`for f in $LIVROS; do cp $CORTE/$f $VIVO/$f; done` → `sha256sum` = `SHA256-ANTES.txt` → `rm PARAR.flag`.
Se o robô já correu (passo 12), **não** repor os livros: repor só a tabela do coletor e a prova de rotas, tirar a
marca das 5 D49/D51, `retirar_por_decisao.py --decisao D52 --reverter --escrever`. Se o passo 11 já fez push:
**não forçar**; o coordenador decide.
