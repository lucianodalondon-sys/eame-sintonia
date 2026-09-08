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

from guarda.preservar_coleta import Memoria

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
    check (preserved = 1 or not_preserved_reason is not null)
);
create index raw_hash_idx on raw_asset (sha256);
create index raw_run_idx  on raw_asset (run_id);
"""


class MemoriaDescartavel(Memoria):
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
        # `public.` nao existe em SQLite. E a unica reescrita de dialeto, e ela
        # e mecanica — nao mexe em valor, trava nem semantica.
        self.con.executescript(sql.replace("public.", ""))

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
    def contar(self, tabela: str) -> int:
        return self.con.execute("select count(*) from %s" % tabela).fetchone()[0]

    def fechar(self):
        self.con.close()
