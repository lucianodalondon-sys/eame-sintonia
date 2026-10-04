#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-E2E-02 — AS TRAVAS MORDEM, E MORDEM A FORMA QUE O SCRAP ESCREVE.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/as_travas_do_scrap_no_postgres.py

A PERGUNTA, E É UMA SÓ
----------------------
    AS LEIS QUE O ESQUEMA DECLARA CONSEGUEM RECUSAR A LINHA ERRADA —
    OU ESTÃO LÁ COMO DECORAÇÃO?

    UMA CONSTRAINT LISTADA NÃO É UMA CONSTRAINT PROVADA.
    CAN DO != DID DO.

`provas/o_scrap_chega_ao_acervo.py` prova que a linha CERTA entra. Isso é
metade: um esquema sem travas também deixa entrar a linha certa, e deixa
entrar todas as outras a seguir.

    QUE O BOM PASSE NÃO PROVA QUE O MAU PARE.

O MÉTODO, E O QUE O TORNA DIFERENTE DE ESCREVER SQL À MÃO
----------------------------------------------------------
Cada ataque parte da LINHA REAL que a corrida do SCRAP escreveu — lida do
banco, e não inventada aqui — e muda UM campo, o que a lei proíbe. Se o
banco aceitar, a lei não existe.

    UM ATAQUE CONTRA UMA LINHA INVENTADA MEDE A INVENÇÃO.
    ELE TEM DE PARTIR DA FORMA QUE A ROTA ESCREVE DE VERDADE.

E o oposto também se mede, e é metade do valor: antes de cada ataque, a
MESMA escrita sem a mutação tem de PASSAR. Uma trava que recusa tudo não é
uma trava — é uma porta emperrada, e passaria neste ficheiro sem a
contraprova.

    UMA TRAVA QUE RECUSA TUDO PASSA NUM TESTE QUE SÓ VERIFICA RECUSAS.

NENHUMA LIGAÇÃO A PRODUÇÃO
--------------------------
A mesma tranca dos outros: a URL é decomposta, o `hostname` tem de ser
exatamente local e o banco tem de estar na lista curta dos descartáveis.

    LIVE_READS = 0 · LIVE_WRITES = 0 · REAL_NETWORK = 0 · PAID_USD = 0
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('orquestrador', 'pedido', 'coleta', 'leis', 'regras', 'ferramentas',
           'medidas', 'guarda', 'admissao', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import importlib.util as _u        # noqa: E402

_sp = _u.spec_from_file_location(
    'e2e01', os.path.join(RAIZ, 'provas', 'o_scrap_chega_ao_acervo.py'))
_e2e = _u.module_from_spec(_sp)
_sp.loader.exec_module(_e2e)

_spg = _u.spec_from_file_location(
    'prova_pg', os.path.join(RAIZ, 'provas', 'preservar_coleta_no_postgres.py'))
_pg = _u.module_from_spec(_spg)
_spg.loader.exec_module(_pg)

FALHAS = []
SHIM = os.path.join(RAIZ, 'provas', '_e2e01_janela_admissivel.py')


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-50s %s' % ('ok' if ok else 'FALHA', titulo[:50],
                               str(detalhe)[:58]))
    if not ok:
        FALHAS.append(titulo)


def tenta(url, sql):
    """Corre o SQL. → (aceitou, a razão da recusa, o nome da lei que mordeu).

    A razão vem do banco e é CURTA de propósito: ela entra no relatório, e uma
    mensagem inteira de `psql` traria o SQL com os valores dentro.
    """
    r = subprocess.run(['psql', '-q', '-v', 'ON_ERROR_STOP=1', '-c', sql, url],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return True, '', ''
    saida = (r.stderr or '').strip()
    # ── SÓ A LINHA DO ERRO, E NUNCA O `DETAIL` ──────────────────────────
    # O `DETAIL` do PostgreSQL traz a LINHA INTEIRA que falhou — sha, morada,
    # identificadores. Isso entraria no relatório e no log do workflow sem
    # ninguém ter decidido que entrava.
    #
    #     UMA MENSAGEM DE ERRO NÃO É UM SÍTIO PARA PUBLICAR DADOS.
    linhas = saida.splitlines()
    linha = next((x for x in linhas if 'ERRO' in x or 'ERROR' in x),
                 linhas[0] if linhas else '')

    # ── QUEM MORDEU, E NÃO SÓ QUE ALGO MORDEU ───────────────────────────
    # ⚠️ ESTA EXTRACÇÃO JÁ ESTEVE ERRADA, e de maneira instrutiva: apanhava o
    # PRIMEIRO nome entre aspas da mensagem — que numa violação de CHECK é a
    # TABELA (`new row for relation "raw_asset" violates check constraint
    # "..."`), e não a lei. Um ataque CORRECTO era reportado como «morreu na
    # lei errada», e eu quase fui procurar o defeito no esquema.
    #
    #     QUEM É NOMEADO PRIMEIRO NÃO É QUEM DECIDIU.
    #
    # O PostgreSQL nomeia sempre a lei a seguir à palavra `constraint`, e a
    # coluna a seguir a `null value in column`. São esses os dois padrões, e
    # não «a primeira coisa entre aspas».
    achado = re.search(r'constraint "([^"]+)"', saida)
    if achado:
        return False, linha.strip()[:150], achado.group(1)
    achado = re.search(r'null value in column "([^"]+)"', saida)
    if achado:
        return False, linha.strip()[:150], 'NOT NULL:' + achado.group(1)
    return False, linha.strip()[:150], '?'


def lit(v):
    if v is None:
        return 'null'
    return "'" + str(v).replace("'", "''") + "'"


def uma_corrida_de_verdade(url):
    """Corre o SCRAP a sério e devolve as linhas que ELE escreveu.

    Não se fabrica a linha de partida. Uma prova de travas construída sobre
    uma linha escrita à mão prova as travas contra a mão que a escreveu.
    """
    base = tempfile.mkdtemp(prefix='scrap-travas-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _e2e.com_este_falso(arvore, SHIM)
        recibo, _env, _ = _e2e.correr_com_banco(arvore, _e2e.FONTE, url)
        run_id = (recibo or {}).get('RUN_ID') or ''
        if not run_id:
            return None
        a = run_id.replace("'", "''")
        obs = _e2e.q(url, "select id, run_id, storage_path, media_type, bytes, "
                          "sha256, preserved, storage_object_id, source_id, "
                          "identity_state, captured_at "
                          "from raw_asset where run_id = '%s' order by id" % a)
        if not obs:
            return None
        o = obs[0]
        so = _e2e.q(url, "select id, storage_path, media_type, bytes, sha256 "
                         "from storage_object where id = %s" % o[7])
        return {'RUN_ID': run_id, 'RAW': o, 'OBJ': so[0] if so else None,
                'ETAPAS': _e2e.q(url, "select etapa, tentativa from "
                                      "etapa_da_corrida where run_id = '%s'" % a)}
    finally:
        shutil.rmtree(base, ignore_errors=True)


def ataque(url, lei, titulo, sql):
    """A escrita proibida TEM de morrer, e TEM de morrer NESTA lei.

    ⚠️ ESTA SEGUNDA METADE FOI PAGA, E NA PRIMEIRA CORRIDA DESTE FICHEIRO.
    Seis ataques deram «ok» sem nunca terem chegado à lei que visavam: todos
    morreram em `NOT NULL: captured_at`, uma coluna que o ataque esquecera de
    preencher. A recusa era verdadeira e o veredito era falso.

        UMA RECUSA PELA LEI ERRADA NÃO PROVA A LEI CERTA.
        «O BANCO DISSE QUE NÃO» NÃO É UMA RESPOSTA: É METADE DELA.

    Quem apanhou isso não fui eu a reler: foi a CONTRAPROVA — a mesma escrita
    sem a mutação, que tinha de PASSAR e não passava. Sem ela, este ficheiro
    reportaria oito travas a morder e teria medido uma.
    """
    aceitou, porque, quem = tenta(url, sql)
    if aceitou:
        diz(False, titulo, 'ACEITE — a lei %s não morde' % lei)
        return False
    if lei not in quem and lei not in porque:
        diz(False, titulo,
            'morreu na lei ERRADA: %s (esperava %s)' % (quem or porque, lei))
        return False
    diz(True, titulo, quem)
    return True


def contraprova(url, titulo, sql):
    """A MESMA escrita sem a mutação. Se ela não passa, o ataque não mediu nada.

        UMA TRAVA QUE RECUSA TUDO PASSA NUM TESTE QUE SÓ VERIFICA RECUSAS.
    """
    aceitou, porque, quem = tenta(url, sql)
    diz(aceitou, titulo, 'aceite' if aceitou else
        'RECUSADA por %s · %s' % (quem or '?', porque))
    return aceitou


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL')
    if not url:
        print('FALTA BANCO_DESCARTAVEL_URL — e SKIP != PASS.')
        print('TRAVAS_DO_SCRAP=NOT_MEASURED')
        return 2
    if not _pg._e_descartavel(url):
        print('RECUSADO: a URL nao e de um banco descartavel local.')
        return 2

    print(__doc__.strip().splitlines()[0])
    print('=' * 74)
    # ⚠️ O ESQUEMA, PELO DONO DELE — e nao por uma segunda copia da
    # cadeia escrita aqui. O workflow entrega um banco recem-criado, e
    # sem isto esta prova morria em «relation does not exist» a dizer
    # outra coisa qualquer.
    #
    #     UM PORTAO QUE NAO CHEGA A CORRER NAO E UM PORTAO A FALHAR:
    #     E UM PORTAO QUE NAO EXISTE.
    _e2e.garantir_o_esquema(url)

    vivo = uma_corrida_de_verdade(url)
    if not vivo:
        print('A CORRIDA DO SCRAP NAO DEIXOU LINHA — nao ha o que atacar.')
        print('TRAVAS_DO_SCRAP=NOT_MEASURED')
        return 1
    raw, obj, run_id = vivo['RAW'], vivo['OBJ'], vivo['RUN_ID']
    print('  a linha de partida veio da corrida %s' % run_id)
    print('  raw_asset id=%s · storage_object id=%s' % (raw[0], obj[0]))

    contador = {'n': 0}

    def objeto(sufixo, sha):
        """Um `storage_object` novo. Endereço e sha que não existem em lado
        nenhum: reusar os da corrida faria o ataque morrer na trava de
        unicidade — e um ataque que morre na porta errada não prova a porta
        que visava."""
        r = _e2e.q(url, "insert into storage_object (storage_path, media_type,"
                        " bytes, sha256) values (%s, %s, %s, %s) returning id"
                   % (lit('data/raw/observacoes/%s.json' % sufixo),
                      lit(obj[2]), obj[3], lit(sha)))
        return r[0][0]

    def obs(sha, oid, preserved='true', motivo=None, source=None,
            corrida=None, endereco=None):
        """A escrita de uma observação, COMPLETA — e é isso que importa.

        Todas as colunas obrigatórias vão preenchidas de propósito, com os
        valores da linha REAL. O que cada ataque muda é UM campo, e só esse.
        """
        contador['n'] += 1
        cols = ['run_id', 'storage_path', 'media_type', 'bytes', 'sha256',
                'captured_at', 'preserved', 'storage_object_id', 'source_id',
                'identity_state']
        vals = [lit(corrida or run_id),
                lit(endereco or 'data/raw/observacoes/ataque-%d.json'
                    % contador['n']),
                lit(raw[3]), str(raw[4]), lit(sha), lit(raw[10]), preserved,
                'null' if oid is None else str(oid), lit(raw[8] if source is None
                                                         else source),
                lit(raw[9])]
        if motivo is not None:
            cols.append('not_preserved_reason')
            vals.append(lit(motivo))
        return ('insert into raw_asset (%s) values (%s)'
                % (', '.join(cols), ', '.join(vals)))

    print('\n1 · A OBSERVAÇÃO E A CÓPIA FALAM DO MESMO CONTEÚDO')
    # A chave estrangeira é COMPOSTA — `(storage_object_id, sha256)`. Uma FK
    # simples deixaria a observação apontar para uma cópia de OUTRO conteúdo,
    # e a linhagem parecia inteira com o conteúdo trocado.
    #
    #     APONTAR PARA UMA CÓPIA NÃO É APONTAR PARA A CÓPIA CERTA.
    sha_a, sha_b = 'a' * 64, 'b' * 64
    id_a, id_b = objeto('aa', sha_a), objeto('bb', sha_b)
    contraprova(url, 'a linha COERENTE entra', obs(sha_a, id_a))
    ataque(url, 'a_observacao_e_a_copia_falam_do_mesmo_conteudo',
           'a observação NÃO aponta para cópia de OUTRO conteúdo',
           obs(sha_a, id_b))

    print('\n2 · PRESERVADO APONTA PARA A CÓPIA, E AUSENTE TEM MOTIVO')
    ataque(url, 'preservado_aponta_para_a_copia',
           'preserved=true sem cópia é recusado',
           obs('c' * 64, None, preserved='true'))
    ataque(url, 'bruto_ausente_precisa_de_motivo',
           'preserved=false sem motivo é recusado',
           obs('d' * 64, None, preserved='false'))
    contraprova(url, 'e COM motivo entra',
                obs('e' * 64, None, preserved='false', motivo='UPLOAD_PENDING'))

    print('\n3 · A FONTE REAL, EM QUALQUER ESTADO FORWARD')
    # `NAO SEI` é a casa a dizer que não sabe, e não uma fonte. Aceitá-lo aqui
    # faria a ausência declarada virar identidade — e uma identidade fabricada
    # envenena tudo o que vier depois dela.
    for i, fingida in enumerate(('NAO SEI', 'NAO_SEI', 'UNKNOWN', '   ', '')):
        sha = ('%d' % i) * 64
        ataque(url, 'fonte_real_em_qualquer_estado_forward',
               'source_id %r não passa por fonte' % fingida,
               obs(sha, objeto('f%d' % i, sha), source=fingida))

    print('\n4 · UMA CORRIDA NÃO CONTA DUAS HISTÓRIAS')
    ataque(url, 'collection_run_run_id_key',
           'o mesmo RUN_ID não abre uma segunda corrida',
           "insert into collection_run (run_id, platform, started_at, "
           "rule_version) values (%s, 'INSTAGRAM', now(), '3')" % lit(run_id))
    contraprova(url, 'e um RUN_ID novo abre',
                "insert into collection_run (run_id, platform, started_at, "
                "rule_version) values ('RUN-QUE-NUNCA-EXISTIU', 'INSTAGRAM', "
                "now(), '3')")

    print('\n5 · A MESMA ETAPA NÃO SE CONTA DUAS VEZES NA MESMA TENTATIVA')
    et = vivo['ETAPAS'][0] if vivo['ETAPAS'] else None
    if et:
        ataque(url, 'etapa_da_corrida_run_id_etapa_tentativa_key',
               'a etapa %s/tentativa %s não entra duas vezes' % (et[0], et[1]),
               "insert into etapa_da_corrida (run_id, etapa, tentativa, estado)"
               " values (%s, %s, %s, 'PASS')" % (lit(run_id), lit(et[0]), et[1]))
    else:
        diz(False, 'a corrida emitiu etapa para atacar', 'NENHUMA ETAPA')

    print('\n6 · SÓ O RAW NOMEIA A OBSERVAÇÃO')
    ataque(url, 'so_o_raw_nomeia_a_observacao',
           'uma etapa DERIVED não nomeia a observação',
           "insert into etapa_da_corrida (run_id, etapa, tentativa, estado, "
           "raw_asset_id) values (%s, 'DERIVED', 99, 'PASS', %s)"
           % (lit(run_id), raw[0]))
    contraprova(url, 'e a etapa RAW nomeia',
                "insert into etapa_da_corrida (run_id, etapa, tentativa, "
                "estado, raw_asset_id) values (%s, 'RAW', 98, 'PASS', %s)"
                % (lit(run_id), raw[0]))

    print('\n7 · UM ENDEREÇO, UMA CÓPIA')
    ataque(url, 'storage_object_storage_path_key',
           'dois conteúdos não moram na mesma morada',
           "insert into storage_object (storage_path, media_type, bytes, "
           "sha256) values (%s, %s, %s, %s)"
           % (lit(obj[1]), lit(obj[2]), obj[3], lit('9' * 64)))

    print('\n8 · A OBSERVAÇÃO NÃO NOMEIA UMA CORRIDA QUE NÃO EXISTE')
    sha_z = '8' * 64
    ataque(url, 'raw_asset_run_id_fkey',
           'uma observação órfã de corrida é recusada',
           obs(sha_z, objeto('zz', sha_z), corrida='CORRIDA-QUE-NUNCA-CORREU'))

    print('\n' + '=' * 74)
    if FALHAS:
        print('TRAVAS QUE NÃO MORDEM, OU QUE MORDERAM PELA LEI ERRADA (%d):'
              % len(FALHAS))
        for f in FALHAS:
            print('   · %s' % f.strip())
        print('TRAVAS_DO_SCRAP=NO')
        return 1
    print('TRAVAS_DO_SCRAP=YES · cada lei mordeu a SUA escrita, '
          'e a contraprova passou')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
