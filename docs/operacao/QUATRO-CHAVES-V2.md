# QUATRO-CHAVES-V2 — as quatro chaves sobre o vivo, lidas e escritas PELO NOME

> Ramo `quatro-chaves-v2`, a partir do vivo `ce28040c`. **NÃO instalado.** Só o coordenador instala.
> Missão: `auditoria-madrugada/missao-quatro-chaves.txt` · origem do pedido:
> `auditoria-madrugada/AVISO-INSTALACAO-2-QUATRO-CHAVES.txt`.

## 1. O problema que o AVISO levantou

A INSTALAÇÃO-2 deixou as quatro chaves (CULTURA · REGIÃO_DO_FATO · FASE · JANELA) de fora por dois
motivos:

1. o ramo da nuvem trazia a **sua própria 033** — e a Sala real já tem a 033 única (com
   `janela_declarada`, o DDL da nuvem tal e qual). O livro-razão tem uma 033 só;
2. `admissao/sala_de_espera.py` lia a Sala **por posição** (`c[18]`…`c[21]`, e a nuvem somava
   `c[22]`) e escrevia com duas listas paralelas (nomes num sítio, valores noutro). Juntar duas
   linhas que acrescentam colunas obrigava a renumerar — e **um índice errado não dá erro**: lê ou
   grava a coluna vizinha em silêncio.

## 2. O que mudou

| Commit | O quê |
|---|---|
| `9bd6397b` | A linha da nuvem (`nuvem-quatro-chaves-sala-v1 @ ffc5d6da`) trazida **tal e qual** sobre `ce28040c`: `admissao/admissao.py` (dono das quatro chaves: `janela_declarada()`, `janela_para_o_ready()`, `JANELA_NAO_MEDIDA`), `admissao/sala_de_espera.py`, `BIBLIA-CANONICA-DA-COLETA.md`, `tests/test_quatro_chaves.py`, `tests/test_quatro_chaves_na_sala.py`, `tests/test_a_linhagem_do_ready.py`, `data/derivados/QUATRO-CHAVES-NA-SALA/`. **Sem migração nova e sem desfazer novo**: o ramo da nuvem nesse ponto já não traz 033 própria. |
| `4dd0a25b` | `admissao/sala_de_espera.py` refeito **pelo nome**: uma tabela única coluna↔campo. |

### A tabela única (`admissao/sala_de_espera.py`)

- `COLUNAS_LIDAS` — a lista de colunas que `ler()` pede. O `select` nasce dela
  (`"select " + ", ".join(COLUNAS_LIDAS)`), e cada valor é casado com o seu nome por `zip`.
  Se o número de valores ≠ número de colunas → `SalaIndisponivel` (rebenta alto, não lê torto).
- `COLUNAS_ESCRITAS` — a lista de colunas que `pousar()` grava. As **três** listas do script SQL
  (tabela `_entrada`, `insert` na Sala, `select` de `_entrada`) passam a ser a mesma `{colunas}`.
- `COLUNA_E_CAMPO` (17 pares) e `COLUNA_E_CAMPO_JSON` (`fato`, `completude_tempo_lugar`,
  `tempo_lugar_evidencia`, `janela_declarada`) — o único sítio que diz «esta coluna é aquele campo
  do READY». Ler e escrever usam a mesma tabela.
- `pousar()` monta um dicionário `coluna → valor` e confere que as chaves são exatamente
  `COLUNAS_ESCRITAS` antes de gerar o SQL.

Acrescentar uma coluna futura = uma linha na tabela. Não há número de posição para renumerar.

### O que ficou igual, de propósito

- **Nenhuma migração.** A 033 única já está na Sala real, com `janela_declarada` `json not null`
  e default = «não medido» (`JANELA_NAO_MEDIDA` é igual ao default byte a byte — teste da nuvem).
  Continua uma só 033 em `supabase/migrations/` e um só `033_desfazer.sql`.
- Leis intactas: a região do fato nunca vem de `source_location`; ausência = `NAO SEI`;
  FACT_TIME ≠ PUBLISHED_AT ≠ CAPTURED_AT; DA-6 (só o extrator do fato escreve `fact_time` — o
  teste estrutural da nuvem continua verde).
- ⚠️ `listar_pendentes()` ainda lê `c[0]`, `c[1]`, `c[2]` de um `select run_id, ordem, item_id`
  escrito na **mesma linha**. Não mexi: três colunas, lista e leitura lado a lado, fora do alvo do
  AVISO. Fica anotado.

## 3. Testes

| Bateria | Resultado | Prova |
|---|---|---|
| `tests.test_sala_por_nome` (6 testes, sem banco: cada campo volta da SUA coluna; nº de valores errado rebenta; nenhum `c[n]` em `ler`; cada valor do insert vai para a SUA coluna; as 3 listas de colunas são a mesma) | ANTES do refeito: FAILED (5 erros) · DEPOIS: 6/6 OK | `data/derivados/QUATRO-CHAVES-V2/testes-por-nome-ANTES.txt`, `…-DEPOIS.txt` |
| Sem banco: `test_sala_por_nome` + `test_quatro_chaves` + `test_quatro_chaves_na_sala` (parte sem banco) + `test_a_linhagem_do_ready` | 43/43 OK | `…/testes-sem-banco-DEPOIS.txt` |
| Mutação da leitura/escrita pelo nome (M1 coluna vizinha na tabela · M2 sem conferir contagem · M3 JSON gravam todos o FATO · M4 JSON leem todos o fato · M5 lista escrita à mão de volta) | 5 mutantes, 5 mortos, ficheiro reposto (sha256) nos 5 | `…/mutacao.py.txt`, `…/mutacao-RESULTADO.txt` |
| Bateria da nuvem COM banco (`QUATRO_CHAVES_EXIGIR_BANCO=1`, Postgres descartável próprio) | 22/22 OK (203,8 s) | `…/testes-COM-BANCO.txt` |

## 4. Ensaio no Postgres DESCARTÁVEL restaurado do último backup

Registo: `data/derivados/QUATRO-CHAVES-V2/ensaio_backup.py.txt` → `ENSAIO-BACKUP.json`.
Sala real não tocada (porta 54330 recusada no próprio script; base `sala_ensaio_qc2` num cluster
temporário na porta 54391, desligado e apagado no fim). Sem rede (proxy 127.0.0.1:9).

Backup: `~/sintonia-sala-italia/backups/sala_italia-20260925-193339.dump`
(sha256 `a05beb22acf33425a63275d19ef74a63c8d4002612cf825600adaf207ee83616`). `pg_restore`: código 0, sem avisos.

| O que se mediu | Resultado |
|---|---|
| A coluna `janela_declarada` existe na cópia restaurada | SIM |
| Linhas da Sala restaurada, lidas pelo código novo (pelo nome) | 80 linhas em 60 corridas → 80 lidas, nenhuma rebentou |
| Dessas, com a janela igual ao «não medido» do dono (`JANELA_NAO_MEDIDA`) | 80 de 80 — as linhas antigas leem o default, ninguém as reescreveu |
| Ida e volta: um item T1 novo (boletim de vite, `fact_location` Valpolicella) → `decidir` → `pronto_para_inteligencia` → `pousar` → `ler` | decisão SIM · pousar PASSED · **0 campos do READY diferentes** entre o que foi e o que voltou |
| A mesma linha lida direto na coluna, por SQL | `published_at_basis`=NAO SEI · `source_location_basis`=NAO SEI · `fact_location`=Valpolicella · CULTURA=["vite","vigneti"] · REGIÃO_DO_FATO=Valpolicella — cada valor na SUA coluna |
| Controlo negativo: janela sem `CULTURA.BASE` | RECUSADA pela trava da 033 (`janela_declara_as_quatro_chaves`) |
| Linhas no fim | 81 (80 + 1 do ensaio; a negativa não entrou) |
| Cluster temporário | desligado e apagado; 0 processos postgres sobrantes |

⚠️ 1.ª tentativa (02:55Z) parou antes de medir: faltava declarar `SINTONIA_PSQL_EXE`; o
restauro correu, o cluster foi desligado e apagado. A 2.ª (02:59Z–03:01Z) é a registada acima.

Limite: a Sala restaurada tem 80 linhas — todas antigas, todas com janela «não medido». O ensaio
prova que o código novo as lê sem torcer; não prova nada sobre extração de chaves em volume.

## 5. Plano de instalação (para o coordenador — eu NÃO instalo)

1. **Banco: nada.** A 033 única já está na Sala real. Não correr migração nenhuma. Conferir antes,
   só leitura: `select column_name from information_schema.columns where table_name='sala_de_espera'
   and column_name='janela_declarada'` → 1 linha.
2. **Código:** juntar `quatro-chaves-v2` no vivo (`merge --no-ff`). O ramo parte de `ce28040c`
   (o vivo atual); se o vivo andar entretanto, os pontos de atrito prováveis são
   `admissao/admissao.py` e `admissao/sala_de_espera.py` — nesse caso **não** renumerar nada:
   qualquer coluna nova do outro lado entra como uma linha em `COLUNAS_LIDAS` / `COLUNAS_ESCRITAS`
   / `COLUNA_E_CAMPO`.
3. **Depois de juntar, antes de ligar:** `py -m unittest tests.test_sala_por_nome
   tests.test_quatro_chaves tests.test_quatro_chaves_na_sala tests.test_a_linhagem_do_ready`
   (esperado 43/43 sem banco) e, com LOCK-PESADO, o mesmo ensaio num restauro do backup do dia.
4. **Linhas antigas da Sala** ficam com a janela no default «não medido» (é o que o ensaio mede
   acima) — ninguém as reescreve; UNKNOWN não vira fato.
5. **Desfazer:** reverter o merge. O banco não muda, portanto não há desfazer de banco.
6. Mapa do System Map regerado pela cadeia neste ramo (ver o commit `mapa:` a seguir a este).
