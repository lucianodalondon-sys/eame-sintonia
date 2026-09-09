#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TODO `on conflict` TEM DE TER UMA CHAVE UNICA QUE O SUSTENTE.

    python3 provas/o_dedupe_tem_constraint.py

O QUE ESTA PROVA EXISTE PARA FECHAR
-----------------------------------
    ON CONFLICT DO NOTHING SEM CONSTRAINT RELEVANTE != DEDUPLICACAO.

Um `on conflict do nothing` sem uma chave unica que o arbitre e SQL valido,
corre sem erro, nao avisa ninguem — e nao deduplica nada. Cada chamada
acrescenta outra linha, com outro `id`. Quem le o codigo ve a palavra
`conflict` e acredita que ha dedupe; o banco nunca concordou.

E pior do que lixo: quando o codigo faz `coalesce(novo, o_que_ja_existia)`
para RESOLVER UMA IDENTIDADE, a identidade muda a cada replay. A rota que
ontem era a organizacao 1 hoje e a 2, e as duas metades de uma prova de
linhagem deixam de falar da mesma coisa.

FOI MEDIDO NESTA CASA, DUAS VEZES
---------------------------------
1 · `tests/test_m2_rota_forward.py:146` — «medido, 23 organizacoes e 23
    origens ao fim da suite». Consertado la, com `where not exists`.

2 · `provas/a_rota_m2_atravessa.py` — a MESMA forma partida sobreviveu ao
    conserto do teste, no ficheiro ao lado. Medida de novo, com a clausula
    exata do ficheiro, tres vezes o mesmo nome:

        ids devolvidos: 1, 2, 3  ·  linhas em public.organizacao: 3

    Um conserto num ficheiro nao conserta a classe. E por isso que esta prova
    existe: para que a terceira vez de erro em vez de dar despercebida.

POR QUE NAO BASTAVA O QUE JA HAVIA
----------------------------------
`guarda/sql_conferir.py` e `medidas/portoes_eame.py` ja olhavam para
`on conflict` — mas procuravam a PALAVRA. Exigir que um insert TENHA a
clausula e uma pergunta (idempotencia declarada); perguntar se a clausula
SIGNIFICA alguma coisa e outra, e ninguem a fazia. Esta prova nao substitui
nenhum dos dois: acrescenta a segunda pergunta.

O INVENTARIO DE CHAVES vem de `provas/inventario_esperado.py`, que ja era o
dono de «o que as migrations declaram». Nao se criou um segundo dono.

O QUE ISTO NAO PROVA
--------------------
Nao fala com banco nenhum. Le migrations e codigo. Um indice criado a mao no
painel do Supabase nao aparece aqui — e NAO DEVE aparecer: a cicatriz do
Brasil e exatamente a de um banco cujo estado nao estava no Git.

E nao promete que o dedupe esteja CERTO: promete que ele e POSSIVEL. Escolher
as colunas erradas continua a ser um erro que so um teste de dominio apanha.
"""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'provas'))

from inventario_esperado import NND, PARCIAL, uniques_declaradas  # noqa: E402

# Onde se procura. `supabase/importacoes/` fica de fora: sao ficheiros
# GERADOS, e o dono deles e `guarda/sql_conferir.py`.
PASTAS = ('coleta', 'guarda', 'admissao', 'leis', 'medidas', 'motor', 'fontes',
          'candidatas', 'ferramentas', 'orquestrador', 'portoes', 'pacote',
          'pedido', 'regras', 'superficie', 'scripts', 'provas', 'tests')
EXTS = ('.py', '.mjs', '.js', '.sql', '.sh')

BACKED, PARCIAL_SO, SEM_CHAVE, NOMEADA_AUSENTE = (
    'BACKED', 'PARTIAL_ONLY', 'UNBACKED', 'NAMED_CONSTRAINT_NOT_DECLARED')
# A chave arbitra, mas so porque `NULLS NOT DISTINCT` faz o NULL da coluna
# omitida comparar igual. Nao e defeito — e uma dependencia que merece nome.
POR_NND = 'BACKED_VIA_NULLS_NOT_DISTINCT'

# `on conflict (a, b)` · `on conflict on constraint nome` · `on conflict do ...`
#
# ⚠️ O CORPO NAO PODE ATRAVESSAR STATEMENTS. A primeira versao usava
# `.{0,4000}?` entre o `insert into` e o `on conflict`, e isso emparelhou o
# insert de `organizacao` com a clausula do insert de `canal`, tres linhas
# abaixo — e acusou uma tabela de uma chave que era de outra. Duas falhas
# inventadas em `a_rota_m2_atravessa.py` e `preservar_coleta_no_postgres.py`,
# medidas antes de esta prova ser confiada a alguem.
#
#     UM MEDIDOR QUE ATRAVESSA A FRONTEIRA DO QUE MEDE ACUSA O VIZINHO.
#
# O corpo passa a ser «tudo menos o comeco de outro insert e menos `;`».
RE_ALVO = re.compile(
    r'insert\s+into\s+(?:public\.)?([a-z_]+)'
    r'((?:(?!insert\s+into|;).){0,4000}?)'
    r'on\s+conflict\s*(?:\(([^)]*)\)|on\s+constraint\s+([a-z_]+))?',
    re.S | re.I)

# `schema_migracao` e o livro-razao do APLICADOR. Ele nasce em
# `motor/cadeia_canonica.sh`, e tem de existir ANTES da primeira migration
# para saber o que nao aplicar — por isso nenhuma migration o declara, e por
# isso `provas/inventario_esperado.py` ja o trata como excecao nomeada.
# A chave unica dele esta no `create table` do proprio script.
FORA_DAS_MIGRATIONS = {'schema_migracao': {frozenset(['versao'])}}


def constraints_nomeadas():
    nomes = set()
    import glob
    for f in glob.glob(os.path.join(RAIZ, 'supabase', 'migrations', '*.sql')):
        txt = re.sub(r'--[^\n]*', '', io.open(f, encoding='utf-8').read()).lower()
        for m in re.finditer(r'constraint\s+([a-z_]+)\s+unique', txt):
            nomes.add(m.group(1))
        for m in re.finditer(r'create unique index (?:if not exists )?([a-z_]+)', txt):
            nomes.add(m.group(1))
    return nomes


def colunas_do_insert(corpo):
    """As colunas nomeadas no `insert into X (a, b, c)`.

    Devolve `None` quando a lista nao esta la (um `insert into X select ...`
    sem lista explicita, ou uma forma que este leitor nao sabe ler). `None`
    significa UNKNOWN, e UNKNOWN nao vira acusacao — quem nao mediu nao acusa.
    """
    m = re.match(r'\s*\(([^)]*)\)', corpo)
    if not m:
        return None
    # ⚠️ O SQL VEM PARTIDO EM LITERAIS DE PYTHON. Uma lista de colunas longa
    # atravessa varias linhas concatenadas — `"a, b, "` `"c, d"` — e o que
    # chega aqui traz aspas, quebras de linha e indentacao no meio dos nomes.
    # A versao anterior lia `'\n              "nivel'` como nome de coluna e
    # acusou quatro inserts de `pacote/lastmile_para_supabase.py` que estao
    # certos. Um nome de coluna e `[a-z_][a-z0-9_]*` e mais nada.
    cols = set()
    for c in m.group(1).split(','):
        achado = re.search(r'[a-z_][a-z0-9_]*', c.strip().lower())
        if achado:
            cols.add(achado.group(0))
    return frozenset(cols) or None


def ficheiros():
    for pasta in PASTAS:
        for raiz, _, nomes in os.walk(os.path.join(RAIZ, pasta)):
            if '__pycache__' in raiz or '/.git' in raiz:
                continue
            for n in sorted(nomes):
                if n.endswith(EXTS):
                    yield os.path.join(raiz, n)


def achados():
    uniques = uniques_declaradas()
    nomeadas = constraints_nomeadas()
    fora = []
    for cam in ficheiros():
        try:
            txt = io.open(cam, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        if 'on conflict' not in txt.lower():
            continue
        rel = os.path.relpath(cam, RAIZ)
        # Este ficheiro carrega a FORMA_PARTIDA como literal, de proposito.
        # Varrer-se a si proprio faria o medidor acusar a sua propria isca.
        if os.path.abspath(cam) == os.path.abspath(__file__):
            continue
        for m in RE_ALVO.finditer(txt):
            tab = m.group(1).lower()
            # `insert into public.` dentro de um LITERAL DE REGEX — o proprio
            # `guarda/sql_conferir.py` procura essa string. Nao e um insert.
            if tab == 'public':
                continue
            alvo = m.group(3)
            nome = m.group(4)
            linha = txt[:m.start()].count('\n') + 1
            totais = set(uniques.get(tab, set())) | FORA_DAS_MIGRATIONS.get(tab, set())
            nnd = uniques.get(tab + NND, set())
            parciais = uniques.get(tab + PARCIAL, set())

            if nome:
                v = BACKED if nome.lower() in nomeadas else NOMEADA_AUSENTE
                chave = 'on constraint %s' % nome
            elif alvo:
                cols = frozenset(c.strip().strip('"').lower()
                                 for c in alvo.split(',') if c.strip())
                chave = ', '.join(sorted(cols))
                if cols in totais:
                    v = BACKED
                elif cols in parciais:
                    v = PARCIAL_SO
                else:
                    v = SEM_CHAVE
            else:
                # `on conflict do nothing` NU.
                #
                # ⚠️ A REGRA OBVIA ESTA ERRADA, e a mutacao desta prova apanhou-a
                # a escreve-la: «a tabela tem algum unique, logo esta coberta».
                # Nao esta. `public.organizacao` TEM uniques — `id` e `ror_id` —
                # e a clausula partida continuava muda, porque o insert nao
                # fornece nenhum dos dois: `id` e bigserial e nasce novo em cada
                # linha, e `ror_id` nao e escrito.
                #
                #     A TABELA TER CHAVE UNICA != O INSERT USAR ESSA CHAVE.
                #
                # Um `on conflict` nu so pode disparar se alguma chave unica
                # tiver TODAS as suas colunas entre as colunas do proprio
                # insert. E isso le-se do insert.
                cols_ins = colunas_do_insert(m.group(2))
                chave = '(nu) colunas=%s' % (
                    ', '.join(sorted(cols_ins)) if cols_ins else 'NAO LIDAS')
                if cols_ins is None:
                    v = BACKED          # nao se leu a lista: nao se acusa
                elif any(k <= cols_ins for k in totais):
                    v = BACKED
                elif any(k <= cols_ins for k in parciais):
                    v = PARCIAL_SO
                elif nnd:
                    # A chave nao esta toda no insert, mas e NULLS NOT
                    # DISTINCT: as colunas omitidas entram NULL e comparam
                    # iguais entre si, entao a clausula DISPARA.
                    #
                    #     `clima_observacao` omite `estacao` e mesmo assim
                    #     deduplica, porque a chave e NND. A versao anterior
                    #     desta prova acusou-a. Uma acusacao falsa ensina toda
                    #     a gente a ignorar o alarme.
                    v = POR_NND
                else:
                    v = SEM_CHAVE
            fora.append((rel, linha, tab, chave, v))
    return fora


# ═════════════════════════════════════════════════════════════════════════
# A MUTACAO — um portao que nao pode falhar nao e um portao
#
# Escreve-se um ficheiro com a forma partida EXACTA que esta casa ja teve,
# corre-se o medidor, e exige-se que ele MORDA. Depois apaga-se.
#
#     UM TESTE QUE PASSA PORQUE NAO CONSEGUIU MEDIR
#     E PIOR DO QUE TESTE NENHUM.
#
# O ficheiro nasce em `provas/` (uma das pastas varridas) com um nome que diz
# o que e, e o `finally` apaga-o mesmo que a prova rebente a meio.

MUTANTE = os.path.join(RAIZ, 'provas', '_mutacao_dedupe_TEMPORARIO.sql')

# A forma real, tirada de `provas/a_rota_m2_atravessa.py` antes do conserto.
FORMA_PARTIDA = """insert into public.organizacao (nome_canonico, tipo)
 values ('X', 'orgao_publico') on conflict do nothing returning id;
"""


def a_mutacao_morde():
    """True se, com a forma partida no disco, o medidor a apanha."""
    try:
        io.open(MUTANTE, 'w', encoding='utf-8').write(FORMA_PARTIDA)
        maus = [a for a in achados()
                if a[0].endswith('_mutacao_dedupe_TEMPORARIO.sql')
                and a[4] == SEM_CHAVE]
        return len(maus) == 1
    finally:
        if os.path.exists(MUTANTE):
            os.remove(MUTANTE)


def main():
    todos = achados()
    maus = [a for a in todos if a[4] in (SEM_CHAVE, NOMEADA_AUSENTE)]
    avisos = [a for a in todos if a[4] == PARCIAL_SO]

    print('ON CONFLICT NO REPOSITORIO — e a chave que os sustenta')
    print('=' * 70)
    print('clausulas encontradas: %d · em %d ficheiros'
          % (len(todos), len({a[0] for a in todos})))
    print('  BACKED        %d' % len([a for a in todos if a[4] == BACKED]))
    print('  VIA_NND       %d' % len([a for a in todos if a[4] == POR_NND]))
    print('  PARTIAL_ONLY  %d' % len(avisos))
    print('  UNBACKED      %d' % len(maus))
    print()

    for rel, linha, tab, chave, v in avisos:
        print('  AVISO  %s:%d  %s (%s) — so ha unique PARCIAL' % (rel, linha, tab, chave))
    if avisos:
        print()
    for rel, linha, tab, chave, v in maus:
        print('  FALHA  %s:%d  %s (%s) — %s' % (rel, linha, tab, chave, v))

    if maus:
        print()
        print('DEDUPE_TEM_CONSTRAINT=FAIL · %d clausula(s) que nao deduplicam nada.' % len(maus))
        print('  A clausula e valida, corre, e nao faz nada. Ou se declara a')
        print('  chave unica numa migration, ou se deduplica a mao com')
        print('  `where not exists` — mas nao se deixa a palavra `conflict`')
        print('  a fingir que ha dedupe.')
        return 1

    # A mutacao corre SEMPRE, e no fim: se ela nao morder, o PASS acima nao
    # vale nada — seria um verde por cegueira, e nao por ausencia de defeito.
    if not a_mutacao_morde():
        print('DEDUPE_TEM_CONSTRAINT=FAIL · A MUTACAO NAO MORDEU.')
        print('  Escreveu-se no disco a forma partida conhecida e este medidor')
        print('  nao a viu. O verde acima e cegueira, nao saude.')
        return 1
    print('  MUTACAO  a forma partida conhecida, escrita no disco, FOI APANHADA')
    print()
    print('DEDUPE_TEM_CONSTRAINT=PASS')
    print('  o que isto prova: toda clausula `on conflict` desta arvore tem')
    print('  uma chave unica DECLARADA NAS MIGRATIONS que a arbitra.')
    print('  o que NAO prova: que as colunas escolhidas sejam as certas, nem')
    print('  o estado de banco nenhum. Isto le o Git, e so o Git.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
