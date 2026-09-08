#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O BANCO DESCARTÁVEL — um banco de verdade, que não é a produção.

POR QUE ISTO EXISTE
-------------------
Os testes do dono da escrita provavam a **lógica** com um dicionário. Isso
deixava de fora exatamente a classe de erro que interessa:

    SQL ACEITE  ≠  LINHA GRAVADA

Um dicionário não tem `unique`, não tem `on conflict do nothing`, e não sabe
gravar menos linhas do que lhe pediram sem se queixar. Um banco sabe. Por isso
esta peça existe: para que a reconciliação seja lida de uma tabela real.

O QUE ELA É, E O QUE NÃO É
--------------------------
    É        um SQLite em ficheiro temporário ou em memória, criado e deitado
             fora em cada teste. Tem `UNIQUE`, `FOREIGN KEY`, `CHECK` e
             `on conflict do nothing` a sério.

    NÃO É    Postgres. E não finge ser.

O esquema aqui é uma **TRADUÇÃO** das duas tabelas da `migration 001`, não uma
cópia: SQLite não tem `enum`, `bigserial` nem `timestamptz`. As travas que
importam para esta prova — `storage_path UNIQUE`, `sha256 NÃO único`, `run_id`
obrigatório e com chave estrangeira — são fielmente reproduzidas, e é isso que
está a ser provado.

⚠️ **E a diferença fica declarada, não escondida.** A mesma bateria corre
contra **Postgres 16 de verdade** no workflow `banco-descartavel.yml`, com a
`migration 001` original aplicada num contentor que morre no fim. Quando só
esta correu, o estado honesto é `DB_TESTED (SQLITE)` — nunca `DB_TESTED
(POSTGRES)`.

NENHUMA LIGAÇÃO A PRODUÇÃO
--------------------------
Este ficheiro não conhece `SUPABASE_URL`, não faz rede, e não sabe ler
credencial nenhuma. O caminho do banco é sempre dado por quem o instancia.
"""
import sqlite3

from guarda.preservar_derivado import MemoriaDoDerivado

# TRADUÇÃO da migration 001 — as duas tabelas que a garantia forward toca.
# Cada trava aqui existe na original, e está anotada com o que ela prova.
ESQUEMA = """
create table collection_run (
  id            integer primary key autoincrement,
  run_id        text not null unique,       -- 001: unique. Duas corridas nao partilham nome
  platform      text not null,
  actor         text,
  actor_version text,
  input         text,
  query         text,
  mission       text,
  source_country text not null default 'NAO_SEI',
  started_at    text not null,
  finished_at   text,
  dataset_id    text,
  item_count_raw integer,
  item_count_normalized integer,
  cost_usd      real,
  cost_method   text check (cost_method is null or cost_method in
                ('PLATAFORMA_USAGE_TOTAL','DIFERENCA_DE_SALDO',
                 'TABELA_DE_PRECO','NAO_SEI')),
  source_version text,
  -- 001 usa um enum. SQLite nao tem enum; o CHECK guarda os mesmos cinco valores.
  status        text not null default 'rodando' check (status in
                ('rodando','concluida','vazia','parcial','falhou')),
  error         text,
  capture_method text,
  rule_version  text not null,
  -- 001: custo declarado tem de dizer COMO foi medido.
  constraint custo_declarado_diz_como_foi_medido
    check (cost_usd is null or cost_method is not null)
);

create table raw_asset (
  id            integer primary key autoincrement,
  -- 001: NOT NULL com chave estrangeira. E a trava que impede byte sem corrida —
  -- exatamente a que NAO se relaxa para caber o legado italiano.
  run_id        text not null references collection_run(run_id),
  -- 001: UNIQUE. O grao e o OBJETO GUARDADO.
  storage_path  text not null unique,
  media_type    text not null,
  bytes         integer not null,
  -- 001: indice, NAO unique. O mesmo conteudo pode estar em dois enderecos.
  sha256        text not null,
  captured_at   text not null,
  source_url    text,
  preserved     integer not null default 1,
  not_preserved_reason text,
  constraint bruto_ausente_precisa_de_motivo
    check (preserved = 1 or not_preserved_reason is not null),
  -- 022: o alvo da chave estrangeira COMPOSTA de derived_artifact. Nao e regra
  -- nova — (id, sha256) ja era unico porque id e chave primaria — e sem ela o
  -- SQLite recusa a FK com «foreign key mismatch», tal como o Postgres.
  unique (id, sha256)
);
create index raw_hash_idx on raw_asset (sha256);
create index raw_run_idx  on raw_asset (run_id);

-- TRADUCAO da migration 022. Sem `jsonb` (aqui e texto) e sem `~` (o CHECK de
-- formato do hash fica de fora — quem o prova e o Postgres, no CI). O que
-- importa para o writer esta fielmente reproduzido: a chave da receita, a
-- coerencia pai-id/pai-sha, e o storage_path unico.
create table derived_artifact (
  id              integer primary key autoincrement,
  raw_asset_id    integer not null,
  parent_sha256   text not null,
  kind            text not null,
  producer        text not null,
  producer_version text not null,
  pipeline_version text,
  parameters      text,
  parameters_hash text not null,
  serie_posicao   integer,
  sha256          text not null,
  bytes           integer not null check (bytes >= 0),
  media_type      text not null,
  storage_path    text not null unique,
  derived_at      text not null,
  created_at      text not null default (datetime('now')),
  derivation_batch text,
  -- 022: o pai por ID e o pai por SHA tem de ser o MESMO pai.
  foreign key (raw_asset_id, parent_sha256) references raw_asset (id, sha256),
  -- 022: a identidade da receita. NULLS NOT DISTINCT nao existe em SQLite, e
  -- por isso `serie_posicao` NULL nao colide aqui — o Postgres e que prova
  -- essa metade, e esta escrito assim para nao se acreditar no contrario.
  unique (parent_sha256, kind, producer, producer_version, parameters_hash,
          serie_posicao)
);
create index derived_parent_idx on derived_artifact (parent_sha256);
"""


class MemoriaDescartavel(MemoriaDoDerivado):
    """Um banco real por teste, deitado fora no fim.

    `aplicar` não devolve contagem de propósito — nem devia. O que ela
    devolveria seria a opinião do cliente sobre o que aconteceu, e é essa
    opinião que não vale. Quem conta é `objetos_da_corrida`, com um `SELECT`.
    """

    def __init__(self, caminho=":memory:"):
        self.con = sqlite3.connect(caminho, isolation_level=None)
        self.con.row_factory = sqlite3.Row
        self.con.execute("pragma foreign_keys = on")
        self.con.executescript(ESQUEMA)
        self.aplicacoes = 0
        # Uma maneira de simular a falha que interessa: o SQL corre, mas menos
        # linhas ficam. E o caso H — callback executa e grava a menos.
        self.engolir_inserts_de_objeto = 0

    # ── escrita ─────────────────────────────────────────────────────────
    def aplicar(self, sql: str) -> None:
        if self.engolir_inserts_de_objeto:
            sql = self._engolir(sql)
        self.aplicacoes += 1
        # AS DUAS UNICAS REESCRITAS DE DIALETO, e ambas mecanicas: nao mexem em
        # valor, trava nem semantica.
        #   `public.`  nao existe em SQLite — nao ha esquemas nomeados.
        #   `now()`    chama-se `datetime('now')` aqui. O relogio continua a ser
        #              o DO BANCO, que e o que importa: o fecho nunca herda o
        #              `started_at`, nem aqui nem no Postgres.
        #     o SQLite guarda JSON como texto; o cast e do Postgres.
        self.con.executescript(
            sql.replace("public.", "").replace("now()", "datetime('now')")
               .replace("::jsonb", ""))

    def _engolir(self, sql: str) -> str:
        """Deixa cair N inserts de `raw_asset`, sem erro nenhum.

        É a simulação do que `on conflict do nothing` faz de verdade: o SQL
        corre inteiro, devolve sucesso, e o banco fica com menos linhas do que
        se pediu. Se a reconciliação viesse do número ESPERADO, isto passaria
        despercebido — e é por isso que ela vem de um `SELECT`.
        """
        fora, engolidos = [], 0
        for linha in sql.splitlines():
            if linha.startswith("insert into public.raw_asset") \
                    and engolidos < self.engolir_inserts_de_objeto:
                engolidos += 1
                continue
            fora.append(linha)
        return "\n".join(fora) + "\n"

    # ── leitura: é daqui que sai a reconciliação ────────────────────────
    def corrida(self, run_id: str):
        cur = self.con.execute(
            "select * from collection_run where run_id = ?", (run_id,))
        linha = cur.fetchone()
        return dict(linha) if linha else None

    def objeto_em(self, storage_path: str):
        cur = self.con.execute(
            "select * from raw_asset where storage_path = ?", (storage_path,))
        linha = cur.fetchone()
        return dict(linha) if linha else None

    def objetos_da_corrida(self, run_id: str):
        cur = self.con.execute(
            "select * from raw_asset where run_id = ? order by storage_path",
            (run_id,))
        return [dict(x) for x in cur.fetchall()]

    # ── contagens de conferência, para os testes ────────────────────────
    # ── as leituras que o dono do derivado precisa ──────────────────────
    def raw_por_id(self, raw_asset_id):
        # JOIN SO DE LEITURA com a corrida, para trazer o `source_country`. O
        # pais do derivado e o do bruto que o gerou — nao o que o chamador
        # disser. Nenhuma coluna nova: a informacao ja estava la, uma tabela ao
        # lado.
        cur = self.con.execute(
            "select a.*, r.source_country from raw_asset a "
            "join collection_run r on r.run_id = a.run_id where a.id = ?",
            (raw_asset_id,))
        linha = cur.fetchone()
        return dict(linha) if linha else None

    def derivado_com_identidade(self, identidade):
        # `is` em vez de `=` para que NULL case com NULL: em SQL, NULL = NULL e
        # desconhecido, e sem isto a linha de serie_posicao NULL nunca seria
        # reencontrada — o writer acharia sempre que e a primeira vez.
        onde = " and ".join("%s is ?" % c for c in identidade)
        cur = self.con.execute(
            "select * from derived_artifact where %s" % onde,
            tuple(identidade[c] for c in identidade))
        linha = cur.fetchone()
        return dict(linha) if linha else None

    def contar(self, tabela: str) -> int:
        return self.con.execute("select count(*) from %s" % tabela).fetchone()[0]

    def fechar(self):
        self.con.close()
