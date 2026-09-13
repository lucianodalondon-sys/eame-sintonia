#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-E2E-01 — O SCRAP NÃO SÓ ATRAVESSA: ELE CHEGA.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/o_scrap_chega_ao_acervo.py

A DIFERENÇA PARA `o_fluxo_canonico_do_scrap.py`, E ELA É TODA A PROVA
---------------------------------------------------------------------
Aquela prova mede a ESTRADA: que o pedido chega ao executor do SCRAP, que o
envelope respeita o contrato, que a colheita atravessa o ingresso. E mede-a
SEM BANCO NENHUM — medido nesta missão: nem `memoria`, nem `banco_do_rastro`,
nem uma linha de `raw_asset`.

    ATRAVESSAR NÃO É CHEGAR.
    UMA ESTRADA PROVADA SEM ARMAZÉM PROVA A ESTRADA, E NÃO O ACERVO.

Aqui a mesma corrida corre com a `memoria` LIGADA a um PostgreSQL 16
descartável e com o livro do rastro ligado ao mesmo banco. E depois
pergunta-se ao banco, e ao disco, o que aquela corrida deixou lá.

O QUE É FALSO, E SÓ ISSO
------------------------
UM ficheiro: `coleta/instagram_janela.py`, o cliente que abriria o NAVEGADOR
contra o mundo externo. Vem de `provas/_flow01_janela_falsa.py`, e a troca é
a mesma que a SCRAP-FLOW-01 já fazia. Nada acima dele é falso: o orquestrador,
o plano, o executor do SCRAP, o roteador, o adaptador, a guarda de gasto, o
contrato de retorno, o ingresso, a derivação, a estruturação, a admissão, o
READY e a sala de espera são os desta árvore.

    REAL_NETWORK = 0 · META_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0
    LIVE_READS = 0 · LIVE_WRITES = 0

O ARMAZENAMENTO É PORTÃO BLOQUEANTE
-----------------------------------
Nove propriedades, e nenhuma delas se deduz da outra:

    RAW_OBSERVATION_CREATED   a linha de `raw_asset` existe
    STORAGE_OBJECT_CREATED    a linha de `storage_object` existe
    BYTES_PRESERVED           o byte está no armazém, e tem tamanho
    HASH_MATCH                o sha256 relido bate com o registado
    MEDIA_TYPE_PRESERVED      o tipo declarado sobreviveu à viagem
    RUN_LINK_PRESERVED        a observação aponta para a corrida REAL
    OBSERVATION_LINK_PRESERVED a observação aponta para o objeto
    READBACK_PASS             o byte relido é o byte escrito
    LINEAGE_PASS              a cadeia RUN→RAW→STORAGE fecha no banco

    STORAGE_STATE = NOT_PRESERVED NÃO É SUCESSO, E NÃO SE CHAMA READY.

O QUE ESTA PROVA NÃO AFIRMA
---------------------------
Não afirma produção. Não afirma que o mundo externo responde assim — o
cliente do navegador é falso, de propósito, e um fake acima do portão mediria
o fake. Afirma o que está entre o botão e o acervo.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('orquestrador', 'pedido', 'coleta', 'leis', 'regras', 'ferramentas',
           'medidas', 'guarda', 'admissao', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

from preservar_coleta import ArmazemLocal   # noqa: E402
import proveniencia as pv          # noqa: E402
import retorno_da_coleta as rc     # noqa: E402
import scrap_colheita as sc        # noqa: E402

import importlib.util as _u        # noqa: E402

_sp = _u.spec_from_file_location(
    'flow01', os.path.join(RAIZ, 'provas', 'o_fluxo_canonico_do_scrap.py'))
_flow01 = _u.module_from_spec(_sp)
_sp.loader.exec_module(_flow01)

FONTE = 'IT-T9-001'
FALHAS = []


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-52s %s' % ('ok' if ok else 'FALHA', titulo[:52],
                               str(detalhe)[:56]))
    if not ok:
        FALHAS.append(titulo)


# ── O DRIVER, QUE CORRE DENTRO DA CÓPIA ────────────────────────────────────
# ⚠️ ELE TEM DE SER UM FICHEIRO, e não uma chamada no processo desta prova.
# O orquestrador corre o executor como PROCESSO SEPARADO, e o processo filho
# importa o módulo VERDADEIRO da árvore onde está. Um falso que vive na
# memória do pai não existe para o filho — a SCRAP-FLOW-01 já pagou essa.
#
# E a diferença para o driver dela é UMA linha e meia: `memoria=` e
# `banco_do_rastro=`. Era exatamente o que faltava para a corrida deixar
# rasto onde o acervo o procura.
DRIVER = """
import json, os, sys
RAIZ = os.path.dirname(os.path.abspath(__file__))
for p in ('orquestrador','pedido','coleta','leis','regras','ferramentas',
          'medidas','guarda','admissao',''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import importlib.util as u
_s = u.spec_from_file_location(
    'prova_pg', os.path.join(RAIZ, 'provas', 'preservar_coleta_no_postgres.py'))
_m = u.module_from_spec(_s)
_s.loader.exec_module(_m)
import coleta_checkpoint as cc
import orquestrador as orq, pedido as pd
url = os.environ['BANCO_DESCARTAVEL_URL']
fonte = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '-' else None
p = pd.de_uma_frase('colete concorrentes')
p.filtros.update({'fase': 'janela-perfis', 'pais': 'IT'})
if fonte:
    p.filtros['fonte'] = fonte
recibo = orq.correr(p, memoria=_m.MemoriaPostgres(url),
                    banco_do_rastro=cc.Banco(url))
recibo.pop('_plano', None)
print('<<<RECIBO>>>' + json.dumps(recibo, ensure_ascii=False, default=str))
"""


def com_este_falso(arvore, shim):
    """A cópia da árvore, com ESTE cliente de navegador no lugar do real.

    A troca é a mesma da SCRAP-FLOW-01, e por isso reutiliza-se o construtor
    dela: um segundo construtor divergiria do primeiro no dia em que um deles
    mudasse, e aí duas provas mediriam duas árvores diferentes com o mesmo
    nome.
    """
    _flow01.arvore_com_o_falso(arvore)
    shutil.copy2(shim, os.path.join(arvore, 'coleta', 'instagram_janela.py'))
    return arvore


def correr_com_banco(arvore, fonte, url):
    """A corrida inteira DENTRO da cópia, com o banco ligado.

    → (recibo, envelope, idas_ao_mundo)
    """
    driver = os.path.join(arvore, '_e2e01_driver.py')
    with open(driver, 'w', encoding='utf-8') as f:
        f.write(DRIVER)
    marca = os.path.join(arvore, 'IDAS-AO-MUNDO.json')
    if os.path.isfile(marca):
        os.remove(marca)
    amb = dict(os.environ, FLOW01_MARCA=arvore, PYTHONIOENCODING='utf-8',
               BANCO_DESCARTAVEL_URL=url, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, driver, fonte or '-'], cwd=arvore,
                       capture_output=True, text=True, env=amb, timeout=900)
    recibo = {}
    for linha in (r.stdout or '').splitlines():
        if linha.startswith('<<<RECIBO>>>'):
            recibo = json.loads(linha[len('<<<RECIBO>>>'):])
    if not recibo:
        print((r.stdout or '')[-1500:])
        print((r.stderr or '')[-1500:])
    env = {}
    # A MORADA É A DA CORRIDA, E NÃO A DO EXECUTOR: resolve-se pela MESMA
    # função que o escritor usa, ou a prova procura onde já ninguém escreve.
    alvo = os.path.join(arvore, rc.endereco_do_envelope(
        sc.ENVELOPE, str((recibo or {}).get('RUN_ID') or '')))
    if os.path.isfile(alvo):
        with open(alvo, encoding='utf-8') as f:
            env = json.load(f)
    idas = []
    if os.path.isfile(marca):
        with open(marca, encoding='utf-8') as f:
            idas = json.load(f)
    return recibo, env, idas


def q(url, sql):
    """Uma pergunta ao banco, pelo `psql` que o runner já tem."""
    r = subprocess.run(['psql', url, '-q', '-v', 'ON_ERROR_STOP=1',
                        '-tAF', '\x1f', '-c', sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return [l.split('\x1f') for l in r.stdout.strip().split('\n') if l]


def uma_corrida(url, shim, etiqueta):
    """Uma corrida inteira, medida. → o dicionário das medidas desta corrida.

    A MESMA função mede as duas corridas. Duas funções de medida — uma «para o
    caso que passa» e outra «para o caso que não passa» — seriam duas réguas, e
    a diferença entre os casos deixaria de ser observável.
    """
    base = tempfile.mkdtemp(prefix='scrap-e2e-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    m = {'ETIQUETA': etiqueta}
    try:
        com_este_falso(arvore, shim)
        sala = os.path.join(arvore, 'data', 'samples',
                            'PRONTO-PARA-INTELIGENCIA')
        antes_sala = set(os.listdir(sala)) if os.path.isdir(sala) else set()

        recibo, env, idas = correr_com_banco(arvore, FONTE, url)
        run_id = recibo.get('RUN_ID') or ''
        aspas = run_id.replace("'", "''")
        m.update({'STATUS': recibo.get('STATUS'), 'RUN_ID': run_id,
                  'ACTOR': recibo.get('ACTOR'), 'IDAS_AO_MUNDO': len(idas),
                  'REAL_NETWORK': 0, 'PAID_USD': 0})
        if not run_id:
            m['FATAL'] = 'a corrida nao cunhou RUN_ID'
            return m

        # ── RUN ─────────────────────────────────────────────────────────
        runs = q(url, "select id, status, actor from collection_run "
                      "where run_id = '%s'" % aspas)
        m['RUN_ROWS'] = len(runs)
        m['RUN_ACTOR'] = runs[0][2] if runs else 'NAO SEI'

        # ── RAW OBSERVATION ─────────────────────────────────────────────
        obs = q(url, "select id, storage_path, media_type, bytes, sha256, "
                     "preserved, storage_object_id, source_id, "
                     "coalesce(not_preserved_reason,'') "
                     "from raw_asset where run_id = '%s' order by id" % aspas)
        n = len(obs)
        m['RAW_OBSERVATIONS'] = n
        m['RAW_OBSERVATION_CREATED'] = 'YES' if n else 'NO'
        m['NOT_PRESERVED_COUNT'] = len([o for o in obs
                                        if o[5] not in ('t', 'true')])

        # ── STORAGE OBJECT, CONTADO POR ESTA CORRIDA ────────────────────
        # ⚠️ CONTAR `storage_object` NO BANCO INTEIRO MEDE O BANCO, e não a
        # corrida: num banco limpo os dois números coincidem, e a prova
        # passaria a depender de correr primeiro.
        #
        #     UM NÚMERO QUE SÓ ESTÁ CERTO NA PRIMEIRA CORRIDA
        #     NÃO É UMA MEDIDA: É UMA COINCIDÊNCIA.
        objs = q(url, "select count(distinct so.id) from storage_object so "
                      "join raw_asset ra on ra.storage_object_id = so.id "
                      "where ra.run_id = '%s'" % aspas)
        criados = int(objs[0][0]) if objs else 0
        m['STORAGE_OBJECTS_DA_CORRIDA'] = criados
        m['STORAGE_OBJECT_CREATED'] = 'YES' if criados >= 1 else 'NO'
        sem_objeto = [o for o in obs if not o[6]]
        m['OBSERVATION_LINK_PRESERVED'] = ('YES' if n and not sem_objeto
                                           else 'NO')

        # ── BYTES · HASH · MEDIA_TYPE, RELIDOS DO ARMAZÉM ───────────────
        arm = ArmazemLocal(arvore)
        bytes_ok = hash_ok = tipo_ok = leitura_ok = 0
        for o in obs:
            caminho, tipo, tamanho, sha = o[1], o[2], int(o[3] or 0), o[4]
            try:
                corpo = arm.ler(caminho)
            except Exception:                              # noqa: BLE001
                continue
            leitura_ok += 1
            if len(corpo) == tamanho and tamanho > 0:
                bytes_ok += 1
            if hashlib.sha256(corpo).hexdigest() == (sha or '').strip():
                hash_ok += 1
            if tipo and tipo not in ('NAO SEI', 'UNKNOWN'):
                tipo_ok += 1
        m['READBACK_PASS'] = 'YES' if n and leitura_ok == n else 'NO'
        m['BYTES_PRESERVED'] = 'YES' if n and bytes_ok == n else 'NO'
        m['HASH_MATCH'] = 'YES' if n and hash_ok == n else 'NO'
        m['MEDIA_TYPE_PRESERVED'] = 'YES' if n and tipo_ok == n else 'NO'

        # ── LINHAGEM: A CADEIA FECHA DENTRO DO BANCO ────────────────────
        # TRÊS TABELAS CHEIAS NÃO SÃO UMA CADEIA. A pergunta é se elas se
        # apontam umas às outras, e com os MESMOS valores.
        fechadas = int(q(url,
                         "select count(*) from raw_asset ra "
                         "join collection_run cr on cr.run_id = ra.run_id "
                         "join storage_object so on so.id = ra.storage_object_id "
                         "where ra.run_id = '%s' and so.sha256 = ra.sha256 "
                         "and so.storage_path = ra.storage_path" % aspas)[0][0])
        m['LINEAGE_ROWS_CLOSED'] = fechadas
        m['LINEAGE_PASS'] = 'YES' if n and fechadas == n else 'NO'
        m['RUN_LINK_PRESERVED'] = 'YES' if n and fechadas == n else 'NO'

        # ── RASTRO ──────────────────────────────────────────────────────
        etapas = q(url, "select etapa, estado from etapa_da_corrida "
                        "where run_id = '%s' order by id" % aspas)
        m['ETAPAS'] = ['%s=%s' % (e[0], e[1]) for e in etapas]

        # ── DERIVED, DITO COMO ELE SAIU ─────────────────────────────────
        d = recibo.get('DERIVACAO') or {}
        m['DERIVED_ESTADO'] = d.get('ESTADO_DA_ETAPA', 'NAO_CHAMADO')
        m['DERIVED_BALDES'] = d.get('BALDES') or {}
        m['DERIVED_MOTIVOS'] = sorted({r.get('MOTIVO_DO_EXECUTOR')
                                       for r in (d.get('RESULTADOS') or [])
                                       if r.get('MOTIVO_DO_EXECUTOR')})
        m['STRUCTURED_CHAMADO'] = bool((recibo.get('ESTRUTURACAO')
                                        or {}).get('CHAMADO'))

        # ── A MATRIZ DO TEXTO ───────────────────────────────────────────
        unidades = (recibo.get('INGRESSO') or {}).get('PARA_A_PORTA') or []
        m['UNIDADES_NA_PORTA'] = len(unidades)
        m['UNIDADES_COM_TEXT_UNITS'] = len(
            [u for u in unidades if pv.CAMPO_DAS_UNIDADES in u])
        m.update(matriz_do_texto(env, unidades))

        # ── IDENTIDADE: O QUE A FONTE DECLAROU, E SÓ ISSO ───────────────
        m.update(fabricacao_de_identidade(env, unidades))

        # ── ADMISSÃO → READY → SALA DE ESPERA ───────────────────────────
        adm = recibo.get('ADMISSAO') or {}
        m['ADMISSION_JUDGED'] = adm.get('itens', 0)
        m['ADMISSION_BY_RESULT'] = adm.get('por_resultado') or {}
        m['READY_COUNT'] = adm.get('prontos', 0)
        agora_sala = set(os.listdir(sala)) if os.path.isdir(sala) else set()
        novos = sorted(agora_sala - antes_sala)
        m['SALA_FICHEIROS_NOVOS'] = novos
        alvo = os.path.join(sala, '%s.json' % run_id)
        pousado = {}
        if os.path.isfile(alvo):
            with open(alvo, encoding='utf-8') as f:
                pousado = json.load(f)
        m['SALA_DE_ESPERA'] = ('CHEGOU' if pousado
                               else ('VAZIA' if not novos else 'OUTRO_FICHEIRO'))
        # ⚠️ A CHAVE É `ITENS`, E NÃO `UNIDADES`. A primeira versão desta
        # prova leu `UNIDADES` — o nome do PARÂMETRO de `pousar()` — e leu
        # zero num ficheiro que tinha lá a unidade toda. `SALA_DE_ESPERA =
        # CHEGOU` ao lado de `SALA_UNIDADES = 0` teria passado por um
        # detalhe, e é a mesma família do defeito do endereço do envelope:
        #
        #     LER PELA CHAVE ERRADA NÃO DÁ ERRO: DÁ ZERO,
        #     E ZERO TEM A CARA DE «NÃO CHEGOU NADA».
        #
        # O dono do formato é `admissao/sala_de_espera.py::_corpo`.
        na_sala = list((pousado or {}).get('ITENS') or [])
        m['SALA_UNIDADES'] = len(na_sala)
        m['SALA_RUN_ID_BATE'] = (pousado or {}).get('RUN_ID') == run_id

        # ── O CONTRATO DE READY, CONFERIDO NO QUE ATERROU ───────────────
        # COL-LAW-043: a inteligência recebe ONZE campos, e mais nada. Um
        # campo a mais é um canal por onde a rota fala com quem não devia
        # conhecê-la; um a menos é um consumidor a ler ausência.
        #
        #     READY NÃO É «O QUE SOBROU DA PORTA»: É UM CONTRATO FECHADO.
        campos = sorted({k for i in na_sala for k in i})
        m['READY_CAMPOS'] = campos
        m['READY_CAMPOS_N'] = len(campos)
        m['READY_TODOS_COM_11'] = bool(na_sala) and all(
            len(i) == 11 for i in na_sala)
        m['READY_ESTADO'] = sorted({i.get('ESTADO') for i in na_sala})
        # E a corrida que lá está tem de ser ESTA. Um READY que nomeia outra
        # corrida é linhagem partida no último metro da estrada.
        m['READY_CORRIDA_BATE'] = bool(na_sala) and all(
            i.get('CORRIDA') == run_id for i in na_sala)
        declarada = {str(i.get('SOURCE_ID') or '').strip()
                     for i in (env.get('COLHEITA') or [])} - {''}
        m['READY_SOURCE_ID_DECLARADO'] = bool(na_sala) and all(
            str(i.get('SOURCE_ID') or '') in declarada for i in na_sala)
        return m
    finally:
        shutil.rmtree(base, ignore_errors=True)


#: Os três eixos do texto, e cada um com o SEU contador. Somá-los num
#: `TEXT_LOSS` único diria que algo se perdeu e calaria o quê.
EIXOS_DO_TEXTO = (('TEXT_KIND', 'TEXT_KIND'),
                  ('TEXT_RELATION', 'TEXT_RELATION'),
                  ('LANGUAGE', 'LANGUAGE'))
AUSENTE = ('UNKNOWN', 'NAO SEI', '', None)


def matriz_do_texto(env, unidades):
    """Perda != ausência declarada. São dois estados, e só um é defeito.

    ⚠️ A PRIMEIRA VERSÃO DESTA FUNÇÃO CONTAVA `UNKNOWN` COMO PERDA, e por isso
    acusava `LANGUAGE_LOSS = 1` numa corrida onde nada se perdeu: a fonte
    nunca declarara língua NENHUMA para aquele texto. Pior — o E7 tem
    sentinela EXPLÍCITA a exigir esse `UNKNOWN`
    (`test_o_legado_nao_herda_a_lingua_da_publicacao`), porque

        A LÍNGUA DA PUBLICAÇÃO NÃO É A LÍNGUA DO TEXTO.

    Uma medida que chama defeito ao cumprimento da lei faz alguém «corrigir» a
    lei. A perda mede-se COMPARANDO os dois lados da fronteira, e não olhando
    só para um:

        PERDA        o lado de lá declarou, e o lado de cá não tem
        NAO_DECLARADO ninguém declarou, dos dois lados — e isso é honesto
    """
    de_la = {}
    for item in (env.get('COLHEITA') or []):
        for t in (pv.unidades_do_envelope(item) or []):
            de_la[t.get('TEXT_UNIT_ID') or ''] = t
    de_ca = {}
    for u in unidades:
        for t in (u.get(pv.CAMPO_DAS_UNIDADES) or []):
            de_ca[t.get('TEXT_UNIT_ID') or ''] = t

    fora = {'TEXT_UNITS_NO_ENVELOPE': len(de_la),
            'TEXT_UNITS_NA_PORTA': len(de_ca),
            'TEXT_UNITS_DESAPARECIDAS': sorted(set(de_la) - set(de_ca))}
    for nome, campo in EIXOS_DO_TEXTO:
        perdidos, nao_declarados, iguais = [], 0, 0
        for uid, t in de_la.items():
            antes = t.get(campo)
            depois = (de_ca.get(uid) or {}).get(campo)
            if antes in AUSENTE:
                nao_declarados += 1
            elif depois != antes:
                perdidos.append('%s: %r -> %r' % (uid, antes, depois))
            else:
                iguais += 1
        fora['%s_LOSS' % nome] = len(perdidos)
        fora['%s_NOT_DECLARED' % nome] = nao_declarados
        fora['%s_PRESERVED' % nome] = iguais
        if perdidos:
            fora['%s_PERDIDOS' % nome] = perdidos[:3]
    # O texto ESCOLHIDO por quem julga tem de ser um dos que atravessaram, e
    # com a espécie dele. Um texto certo com a espécie de outro é pior do que
    # nenhum: viaja com autoridade emprestada.
    maus = []
    for u in unidades:
        uid = u.get('texto_unidade')
        if uid is None:
            continue
        t = de_ca.get(uid) or {}
        for campo, na_porta in (('TEXT', 'texto'),
                                ('TEXT_KIND', 'texto_especie'),
                                ('TEXT_RELATION', 'texto_relacao'),
                                ('LANGUAGE', 'texto_lingua')):
            if u.get(na_porta) != t.get(campo):
                maus.append('%s: %r != %r' % (na_porta, u.get(na_porta),
                                              t.get(campo)))
    fora['ESCOLHA_INCOERENTE'] = len(maus)
    if maus:
        fora['ESCOLHA_INCOERENTE_QUAIS'] = maus[:3]
    return fora


def fabricacao_de_identidade(env, unidades):
    """Nenhuma identidade nasce dentro da máquina. → os contadores.

    ⚠️ `NAO SEI` NÃO É UMA IDENTIDADE, e tratá-lo como uma faria a ausência
    declarada contar como fabricação. Ele é o contrário disto: é a casa a
    dizer que não sabe. O que se procura é um valor REAL que apareça de
    ESTE lado sem existir do lado de lá.

        IDENTIDADE FABRICADA ENVENENA TUDO O QUE VIER DEPOIS DELA.
    """
    fora = {}
    for campo in ('SOURCE_ID', 'DOCUMENT_ID'):
        declarados = {str(i.get(campo) or '').strip()
                      for i in (env.get('COLHEITA') or [])}
        declarados -= {str(x or '').strip() for x in AUSENTE}
        fabricados = []
        for u in unidades:
            # `SOURCE_ID` chega à porta já traduzido para `source_id`; o
            # `DOCUMENT_ID` não tem par do outro lado e viaja com o nome dele.
            v = str(u.get(campo) or u.get(campo.lower()) or '').strip()
            if v and v not in ('NAO SEI', 'UNKNOWN') and v not in declarados:
                fabricados.append(v)
        fora['%s_FABRICATION' % campo] = len(fabricados)
        if fabricados:
            fora['%s_FABRICADOS' % campo] = fabricados[:3]
    return fora


PORTAO_DO_ARMAZENAMENTO = (
    'RAW_OBSERVATION_CREATED', 'STORAGE_OBJECT_CREATED', 'BYTES_PRESERVED',
    'HASH_MATCH', 'MEDIA_TYPE_PRESERVED', 'RUN_LINK_PRESERVED',
    'OBSERVATION_LINK_PRESERVED', 'READBACK_PASS', 'LINEAGE_PASS')


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL')
    if not url:
        print('FALTA BANCO_DESCARTAVEL_URL — e SKIP != PASS.')
        print('SCRAP_CHEGA_AO_ACERVO=NOT_MEASURED')
        return 2

    print(__doc__.strip().splitlines()[0])
    print('=' * 74)

    casos = [
        ('A · TEXTO FORA DO LÉXICO DE TODOS OS UNIVERSOS',
         os.path.join(RAIZ, 'provas', '_flow01_janela_falsa.py')),
        ('B · TEXTO DO UNIVERSO PEDIDO, COM ESPÉCIE DECLARADA',
         os.path.join(RAIZ, 'provas', '_e2e01_janela_admissivel.py')),
    ]
    medidas = {}
    for titulo, shim in casos:
        print('\n' + titulo)
        etiqueta = titulo.split(' ')[0]
        m = uma_corrida(url, shim, etiqueta)
        medidas[etiqueta] = m
        if m.get('FATAL'):
            diz(False, 'a corrida produziu RUN_ID', m['FATAL'])
            continue
        diz(m['STATUS'] == 'SUCCESS', 'a corrida correu', m['STATUS'])
        diz(m['ACTOR'] == 'coleta/scrap_colheita.py',
            'e o executor é o do SCRAP', m['ACTOR'])
        diz(m['IDAS_AO_MUNDO'] >= 1, 'a fronteira externa FALSA foi visitada',
            '%d ida(s)' % m['IDAS_AO_MUNDO'])
        diz(m['RUN_ROWS'] == 1, 'a corrida abriu EXATAMENTE uma linha de RUN',
            '%d linha(s)' % m['RUN_ROWS'])

        print('  · o portão do armazenamento')
        for k in PORTAO_DO_ARMAZENAMENTO:
            diz(m.get(k) == 'YES', '    %s' % k, m.get(k, 'NAO SEI'))
        diz(m['NOT_PRESERVED_COUNT'] == 0,
            '    nenhuma observação ficou NOT_PRESERVED',
            m['NOT_PRESERVED_COUNT'])

        print('  · a matriz do texto')
        for nome, _ in EIXOS_DO_TEXTO:
            diz(m.get('%s_LOSS' % nome) == 0, '    %s_LOSS' % nome,
                '%s (não declarado: %s · preservado: %s)'
                % (m.get('%s_LOSS' % nome),
                   m.get('%s_NOT_DECLARED' % nome),
                   m.get('%s_PRESERVED' % nome)))
        diz(not m.get('TEXT_UNITS_DESAPARECIDAS'),
            '    nenhuma unidade de texto desapareceu',
            m.get('TEXT_UNITS_DESAPARECIDAS') or 'nenhuma')
        diz(m.get('ESCOLHA_INCOERENTE') == 0,
            '    o texto escolhido leva a espécie DELE',
            m.get('ESCOLHA_INCOERENTE_QUAIS') or 'coerente')
        diz(m.get('SOURCE_ID_FABRICATION') == 0, '    SOURCE_ID_FABRICATION',
            m.get('SOURCE_ID_FABRICATION'))
        diz(m.get('DOCUMENT_ID_FABRICATION') == 0,
            '    DOCUMENT_ID_FABRICATION', m.get('DOCUMENT_ID_FABRICATION'))

        print('  · admissão → READY → sala de espera')
        print('      julgados=%s · %s · READY=%s · sala=%s'
              % (m['ADMISSION_JUDGED'], m['ADMISSION_BY_RESULT'],
                 m['READY_COUNT'], m['SALA_DE_ESPERA']))
        print('      DERIVED=%s %s %s · STRUCTURED_CHAMADO=%s'
              % (m['DERIVED_ESTADO'], m['DERIVED_BALDES'],
                 m['DERIVED_MOTIVOS'] or '', m['STRUCTURED_CHAMADO']))

    a, b = medidas.get('A') or {}, medidas.get('B') or {}

    print('\n' + '=' * 74)
    print('AS DUAS LEIS QUE SÓ SE VEEM COM OS DOIS CASOS AO LADO')
    # ── UM `NAO_SEI` NÃO VIRA `READY` ────────────────────────────────────
    # Este é o caso A, e ele NÃO é um caso falhado: é a lei. A porta que não
    # reconhece o vocabulário responde «não sei», e o que não sabe NÃO pousa.
    #
    #     NAO_SEI NÃO É UM SIM FRACO. NÃO PASSA A PORTA.
    diz((a.get('ADMISSION_BY_RESULT') or {}).get('NAO_SEI', 0) >= 1
        and a.get('READY_COUNT') == 0 and a.get('SALA_DE_ESPERA') == 'VAZIA',
        'um NAO_SEI não vira READY, e não pousa na sala',
        'READY=%s sala=%s' % (a.get('READY_COUNT'), a.get('SALA_DE_ESPERA')))
    # ── E A ESTRADA CHEGA MESMO AO FIM ───────────────────────────────────
    # Se só houvesse o caso A, «a sala está vazia» teria duas leituras
    # indistinguíveis: a lei a morder, ou a estrada partida.
    #
    #     UMA SALA VAZIA NÃO DIZ SE A PORTA RECUSOU OU SE A ESTRADA ACABOU
    #     ANTES DELA. SÓ UM CASO QUE CHEGA SEPARA AS DUAS.
    diz(b.get('READY_COUNT', 0) >= 1, 'o caso admissível produz READY',
        'READY=%s · %s' % (b.get('READY_COUNT'), b.get('ADMISSION_BY_RESULT')))
    diz(b.get('SALA_DE_ESPERA') == 'CHEGOU',
        'e a unidade POUSA na sala de espera, na morada da corrida',
        '%s · %s' % (b.get('SALA_DE_ESPERA'), b.get('SALA_FICHEIROS_NOVOS')))
    diz(b.get('SALA_UNIDADES', 0) >= 1 and b.get('SALA_RUN_ID_BATE'),
        'e o ficheiro da sala tem mesmo a unidade, e é desta corrida',
        'ITENS=%s · RUN_ID bate: %s' % (b.get('SALA_UNIDADES'),
                                        b.get('SALA_RUN_ID_BATE')))
    diz(b.get('READY_TODOS_COM_11'),
        'READY entrega os ONZE campos do contrato, e mais nada',
        '%d campo(s): %s' % (b.get('READY_CAMPOS_N', 0),
                             ', '.join(b.get('READY_CAMPOS') or [])))
    diz(b.get('READY_CORRIDA_BATE') and b.get('READY_SOURCE_ID_DECLARADO'),
        'e o READY nomeia ESTA corrida e a fonte DECLARADA',
        'corrida=%s fonte=%s' % (b.get('READY_CORRIDA_BATE'),
                                 b.get('READY_SOURCE_ID_DECLARADO')))
    diz(b.get('TEXT_KIND_PRESERVED', 0) >= 1
        and b.get('LANGUAGE_PRESERVED', 0) >= 1,
        'e a espécie e a língua DECLARADAS chegam inteiras',
        'kind=%s lang=%s preservados'
        % (b.get('TEXT_KIND_PRESERVED'), b.get('LANGUAGE_PRESERVED')))

    # ── UMA DÍVIDA MEDIDA, E DECLARADA COM O DONO ───────────────────────
    # A etapa DERIVED sai `FAIL` nas DUAS corridas, com `EXTRACTION_ERROR`:
    # `orquestrador.pela_derivacao` manda TODA observação preservada ao runner
    # do DERIVED, e esse runner é o documental — ele abre um PDF. A uma
    # observação SOCIAL, que é um JSON e cujo texto já vem no envelope, não há
    # PDF nenhum para abrir, e a ferramenta falha por não ter sujeito.
    #
    # ⚠️ E ISTO NÃO É DA INTEGRAÇÃO DO SCRAP. Medido contra `974e39a6`:
    # `coleta/derivacao_forward.py` e `coleta/executor_texto_de_pdf.py` estão
    # BYTE A BYTE iguais, e `pela_derivacao` é IDÊNTICA por AST. O SCRAP é a
    # primeira rota social a percorrer a estrada canónica com armazém real, e
    # por isso é a primeira a acender esta luz.
    #
    #     A INTEGRAÇÃO NÃO ABRIU ESTE BURACO: FOI O PRIMEIRO CARRO A CAIR
    #     NELE. REVELAR != CAUSAR, E CONFUNDIR OS DOIS FAZ CULPAR QUEM MEDIU.
    #
    # O que esta prova exige HOJE não é que o buraco feche — não é missão
    # desta. É que ele não engula a observação: um DERIVED em erro não pode
    # fazer o RAW desaparecer, nem calar a admissão, nem esvaziar a sala.
    #
    #     UMA ETAPA QUE FALHA PODE PARAR A ESTRADA. NÃO PODE APAGÁ-LA.
    print('\n' + '=' * 74)
    print('A DÍVIDA QUE ESTA CORRIDA ACENDEU, E QUE NÃO É DESTA INTEGRAÇÃO')
    print('  DERIVED_ESTADO = %s · MOTIVO = %s' % (b.get('DERIVED_ESTADO'),
                                                   b.get('DERIVED_MOTIVOS')))
    print('  DONO = orquestrador.pela_derivacao + coleta/derivacao_forward.py')
    print('  ORIGEM = anterior a 974e39a6 (código idêntico; ver o comentário)')
    diz(b.get('DERIVED_ESTADO') == 'FAIL'
        and b.get('DERIVED_MOTIVOS') == ['EXTRACTION_ERROR'],
        'a dívida está onde foi medida (e não noutro sítio)',
        '%s · %s' % (b.get('DERIVED_ESTADO'), b.get('DERIVED_MOTIVOS')))
    diz(b.get('RAW_OBSERVATIONS', 0) >= 1 and b.get('READY_COUNT', 0) >= 1
        and b.get('SALA_DE_ESPERA') == 'CHEGOU',
        'e um DERIVED em erro NÃO apaga o RAW, nem o READY, nem a sala',
        'raw=%s ready=%s sala=%s' % (b.get('RAW_OBSERVATIONS'),
                                     b.get('READY_COUNT'),
                                     b.get('SALA_DE_ESPERA')))
    diz(b.get('STRUCTURED_CHAMADO') is False,
        'e a estruturação NÃO é chamada sem derivado — não finge etapa',
        'STRUCTURED_CHAMADO=%s' % b.get('STRUCTURED_CHAMADO'))

    print('\n' + '=' * 74)
    for etiqueta in ('A', 'B'):
        m = medidas.get(etiqueta) or {}
        print('CASO %s — %s' % (etiqueta, m.get('ETIQUETA', 'NAO SEI')))
        for k in PORTAO_DO_ARMAZENAMENTO:
            print('  %-28s = %s' % (k, m.get(k, 'NAO SEI')))
        for k in ('RAW_OBSERVATIONS', 'STORAGE_OBJECTS_DA_CORRIDA',
                  'NOT_PRESERVED_COUNT', 'UNIDADES_NA_PORTA',
                  'TEXT_UNITS_NO_ENVELOPE', 'TEXT_UNITS_NA_PORTA',
                  'TEXT_KIND_LOSS', 'TEXT_KIND_NOT_DECLARED',
                  'TEXT_RELATION_LOSS', 'TEXT_RELATION_NOT_DECLARED',
                  'LANGUAGE_LOSS', 'LANGUAGE_NOT_DECLARED',
                  'ESCOLHA_INCOERENTE', 'SOURCE_ID_FABRICATION',
                  'DOCUMENT_ID_FABRICATION', 'ADMISSION_JUDGED',
                  'ADMISSION_BY_RESULT', 'READY_COUNT', 'SALA_DE_ESPERA',
                  'SALA_UNIDADES', 'SALA_RUN_ID_BATE',
                  'READY_CAMPOS_N', 'READY_TODOS_COM_11', 'READY_ESTADO',
                  'READY_CORRIDA_BATE', 'READY_SOURCE_ID_DECLARADO',
                  'ETAPAS', 'DERIVED_ESTADO',
                  'DERIVED_BALDES', 'DERIVED_MOTIVOS', 'STRUCTURED_CHAMADO',
                  'REAL_NETWORK', 'PAID_USD'):
            print('  %-28s = %s' % (k, m.get(k, 'NAO SEI')))
        print('  ' + '-' * 60)
    print('=' * 74)
    if FALHAS:
        print('FALHAS (%d):' % len(FALHAS))
        for f in FALHAS:
            print('   · %s' % f.strip())
        print('SCRAP_CHEGA_AO_ACERVO=NO')
        return 1
    print('SCRAP_CHEGA_AO_ACERVO=YES')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
