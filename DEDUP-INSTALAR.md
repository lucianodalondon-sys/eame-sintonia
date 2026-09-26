# DEDUP-INSTALAR — dedup + versões (036) prontos para o lote 3

Missão DEDUP-PARA-INSTALAR · 26/09/2026 · ramo `dedup-doc-v1` sobre o vivo `69b0e23f`.
**NÃO instalado.** Vivo não tocado. Sala real só lida (`pg_dump` e `SELECT` com
`default_transaction_read_only = on`). Sem rede. Detalhe da regra e das versões: `DEDUP-DOC.md`.

Porquê agora: a Sala tem **14 repetições de 13 documentos** e a Intelligence conta-as duas vezes
(defeito D12 do bot da Intelligence). O dedup impede novas; as 14 antigas ficam (a Sala não apaga) e
estão listadas em `DEDUP-DOC.md` §3.

## 1 · Quem pousa entrega armazém + extratores (item 2 da lista)

| escritor da Sala | antes | depois |
|---|---|---|
| `orquestrador/orquestrador.py::pela_porta` | `espera.pousar(run_id, aceites)` | `pousar(..., armazem=armazem, extratores=registo())`; `correr` passa o `ArmazemLocal` que já criava |
| `coleta/rota_forward_documento.py::levar_a_espera` | `espera.pousar(run_id, [pronta])` | idem; `atravessar` passa o armazém que já recebia |

- Registo novo `coleta/extratores_de_texto.py::registo()` → `{producer: extrair}` para `texto-de-html` e
  `texto-de-pdf`. **Não reimplementa nada:** chama o `extrair()` de cada executor, a `receita()` dele e o
  `hash_dos_parametros` do dono da escrita (`guarda/preservar_derivado.py`).
- Import tardio (só quem pousa o carrega). Assinaturas: só um parâmetro opcional novo (`armazem=None`).

## 2 · Conserto: o extrator HTML mudou a receita sem mudar a versão

Medido na Sala real: os derivados 66 (20/09) e 1060 (25/09) da IT-T9-011 dizem ambos `texto-de-html`
**"1"**; o 66 nasceu sem parâmetros e o 1060 com `TEXT_OWNER = coleta/texto_fonte.py::limpar` (ligado em
`f0c6ea6f`, 21/09).

- `EXECUTOR_VERSION` do HTML sobe para **"2"** (declarado no código, com o porquê).
- A receita vive num só sítio: `receita()` em cada executor; `derivar_um` usa-a.
- `tests/test_a_receita_tem_versao.py`: tabela `(producer, versão) → hash da receita`, **só se
  acrescenta**; reprova se a receita mudar sem subir a versão, ou se a versão subir sem registo.
- ⚠️ **Efeito na instalação:** depois do "2", revisitar uma página HTML já derivada em "1" gera um
  derivado **novo** (a identidade da derivação inclui a versão) — mais linhas em `derived_artifact` e mais
  ficheiros `texto-de-html-2-*.txt` no armazém. Na Sala, o dedup barra a 2.ª linha e o decisor re-extrai
  para comparar (é exatamente o caso que o item 1 liga). Os ficheiros `texto-de-html-1-*` antigos (ex.:
  os do `GABARITO-T1-V1.json`) não mudam.

## 3 · Testes e mutação (leves, sem banco, zero rede — proxy morto)

Pelo nome, **contra a base `d899f09e`** (antes) e depois:

| teste | base | depois |
|---|---|---|
| test_a_rota_do_html | 30 OK | 30 OK |
| test_forward_instrumentado | 21 OK | 21 OK |
| test_o_pedido_atravessa | 19 OK | 19 OK |
| test_a_linhagem_do_reaproveitamento | 30 OK | 30 OK |
| test_a_ponte_do_derived | 33 OK | 33 OK |
| test_fonte_atravessa | 21 OK | 21 OK |
| test_lingua_da_porta | 1 FAIL `test_o_mapa_da_porta_vive_num_sitio_so` | **a mesma**, herdada |
| test_estagio_atravessa_a_fronteira | 1 ERROR `test_correr_julga_a_unidade_da_fronteira` | **a mesma**, herdada (já registada a 25/09) |
| test_a_receita_tem_versao (novo) | — | 4 OK |
| test_quem_pousa_entrega_o_armazem (novo) | — | 4 OK |
| test_versao_do_documento | 11 OK | 11 OK |

Mutantes (todos mortos, **6/6**): L1 `correr` não passa o armazém · L2 `pela_porta` não o passa ao
`pousar` · L3 `levar_a_espera` sem extratores · L6 `atravessar` não passa o armazém · L4 receita muda
sem subir a versão · L5 versão sobe sem registo.

Não corridos (pesados ou com rede): `test_m2_rota_forward`, `test_o9_caminho_instrumentado`.

## 4 · Runbook — aplicar a 036 na Sala real (NÃO executado; só o coordenador instala)

Pré: LOCK-PESADO + ≥ 5 GB; robô, supervisor e observador **parados**; código do ramo instalado no vivo
antes ou no mesmo passo (sem o código, a 036 fica vazia e nada a lê — inofensiva).

```bash
S=$HOME/sintonia-sala-italia
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH" PGPASSFILE="$S/pgpass.conf"
DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
B=/c/inst/$(date +%Y%m%d-%H%M)-dedup-036; mkdir -p $B

# 1 · backup + sha256 (pg_dump só lê)
PGOPTIONS="-c default_transaction_read_only=on" pg_dump -Fc --no-owner --no-privileges -f $B/sala.dump "$DSN"
sha256sum $B/sala.dump | tee $B/sala.dump.sha256

# 2 · impressão do conteúdo ANTES (tem de ser igual depois)
IMP="select count(*)||' '||md5(string_agg(t::text,'' order by run_id,ordem)) from public.sala_de_espera t"
PGOPTIONS="-c default_transaction_read_only=on" psql -X -A -t -c "$IMP" "$DSN" | tee $B/antes.txt

# 3 · ensaio na CÓPIA deste dump (tem de dar tudo verde — §5)
py provas/migracao_036_ensaio_copia.py --dump $B/sala.dump --saida $B/ensaio.json

# 4 · aplicar pela cadeia canónica (036 = PASS; TODAS as outras = SKIP — se não, PARAR)
bash motor/cadeia_canonica.sh migrations "$DSN" | tee $B/up.txt

# 5 · idempotente: outra vez → 036 SKIP HASH=MATCH
bash motor/cadeia_canonica.sh migrations "$DSN" | tee $B/up2.txt

# 6 · conteúdo igual, tabela nova vazia, 2 gatilhos
PGOPTIONS="-c default_transaction_read_only=on" psql -X -A -t -c "$IMP" "$DSN" | tee $B/depois.txt
diff $B/antes.txt $B/depois.txt && echo CONTEUDO_IGUAL
PGOPTIONS="-c default_transaction_read_only=on" psql -X -A -t -c \
  "select count(*) from sala_de_espera_versao; select count(*) from pg_trigger where tgname like 'sala_de_espera_versao_%'" "$DSN"   # 0 e 2

# 7 · religar robô, supervisor e observador
```

**Desfazer** (só com o backup do passo 1 à mão):
`psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/036_desfazer.sql "$DSN"` — apaga
só a tabela de versões e a linha 036 do livro-razão; `sala_de_espera` não é tocada. Caminho completo de
volta: `pg_restore` do `$B/sala.dump`. Código: `git revert` dos commits do ramo.

## 5 · Ensaio completo numa cópia da Sala

ENSAIO_PENDENTE

## 6 · As 4 pastas temporárias antigas (NÃO apagadas)

Em `C:\Users\London1\AppData\Local\Temp` (medido 26/09 ~10:52):

| pasta | última modificação | tamanho | ficheiros |
|---|---|---:|---:|
| `migracao-033-5qn_0jp6` | 2026-09-25 18:09 | 69 MB | 1.735 |
| `sala-idempotente-h66abp21` | 2026-09-25 09:19 | 51 MB | 1.565 |
| `sala-idempotente-sjw2adb5` | 2026-09-23 08:26 | 53 MB | 1.733 |
| `sala-idempotente-tjqa3s_p` | 2026-09-23 09:26 | 52 MB | 1.630 |

Todas são clusters de Postgres de teste (têm `pg/servidor.log`), **de 23 e 25/09 — anteriores às minhas
corridas de 26/09**; nenhum Postgres está ligado sobre elas. Total ≈ 225 MB.
