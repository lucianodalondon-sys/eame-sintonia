#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINKEDIN · A MÍDIA DE UM POST PÚBLICO ATÉ À SALA — canário operacional.

    python provas/linkedin_midia_publica_ate_a_sala.py

A PERGUNTA
----------
Um post PÚBLICO do LinkedIn atravessa a Collection inteira pela rota oficial —
`SOURCE/REQUEST → ORCHESTRATOR → ADAPTADOR → RUN → RAW OBSERVATION → STORAGE
OBJECT → DERIVED AUDIO → LOCAL ASR → STRUCTURED → ADMISSION → SALA`?

O QUE ELE NÃO FAZ
-----------------
· Não usa fornecedor pago (medido: ele devolve o MESMO endereço da página).
· Não usa login, cookie, sessão de terceiro, conta falsa, CAPTCHA ou proxy.
· Não inventa `SOURCE_ID`, `DOCUMENT_ID` nem `RAW_OBSERVATION_ID`.
· Não corre contra banco descartável: a bancada operacional é esta, e a
  composição é a canônica (`orquestrador.persistencia`).

O BANCO, E POR QUE ELE É EXPLÍCITO
----------------------------------
`SINTONIA_COLLECTION_DSN` é o binding operacional da Collection. `SINTONIA_SALA_DSN`
é outro dono, outra pergunta. Sem a primeira declarada, o runtime diz `AUSENTE` e
os RAW_OBSERVATIONS saem vazios — e isso NÃO é um PASS.

      SEM DSN NÃO SE ESCREVE NUMA SALA POR ACIDENTE.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import scrap_executor as sx                                    # noqa: E402
import scrap_registo as reg                                    # noqa: E402
from coleta import derivacao_forward as fwd                    # noqa: E402
from coleta import rota_forward_documento as m2                # noqa: E402
from guarda import preservar_coleta as pc                      # noqa: E402
from orquestrador import persistencia as P                     # noqa: E402

POST = ('https://www.linkedin.com/posts/cosemar-ozono_si-tienes-olivos-sabes-lo-'
        'que-es-llegar-activity-7475836883001024512-wyDU')

#: A FONTE. Ela NÃO nasce aqui, e não é derivada do endereço: é a linha de
#: `docs/fontes/ATLAS-DE-FONTES-EAME.md` que já existe para a camada LinkedIn do
#: tier ES. Achado declarado: essa linha está no atlas SEM FICHA — sem nome, sem
#: método de acesso, sem evidência. É a fonte que esta casa já usou para trazer
#: este corpus, e é por isso que ela é usada; a falta de ficha vai no relatório.
FONTE = 'ES-T8-002'
PAIS = 'ES'

CAPACIDADE = 'linkedin.public_post.media_resolution'
ARMAZEM = os.path.join(RAIZ, 'data', 'collection-store')

FALHAS = []


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-58s %s' % ('ok' if ok else 'FALHA', titulo[:58],
                               str(detalhe)[:60]))
    if not ok:
        FALHAS.append(titulo)


def agora():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def main():
    print('=' * 88)
    print('LINKEDIN · MIDIA PUBLICA → COLLECTION → SALA')
    print('=' * 88)

    # ─ AS FERRAMENTAS, ANTES DE QUALQUER AFIRMAÇÃO ───────────────────────
    import fala_local as fl
    import executor_transcricao_midia as ponte
    ha_asr, porque = fl.disponivel()
    print('ASR DISPONIVEL  = %s%s' % ('YES' if ha_asr else 'NO',
                                      '' if ha_asr else ' — ' + porque))
    print('PONTE DE MIDIA  = %s' % ('aceita video/mp4' if ponte.aceita('video/mp4')
                                    else 'NAO ACEITA video/mp4'))
    if not ha_asr or not ponte.ha_ferramenta():
        print('\nNAO_EXERCITADO — falta ferramenta, e isto NAO e um PASS:')
        print('  · ffmpeg=%s · faster-whisper=%s'
              % (ponte.ha_ferramenta(), ha_asr))
        print('\nLINKEDIN_MIDIA_ATE_A_SALA = NOT_EXERCISED')
        return 3

    # ─ A BANCADA OPERACIONAL ─────────────────────────────────────────────
    dep = P.dependencias_do_runtime(os.environ)
    print('RUNTIME         = %s' % dep.ESTADO)
    if dep.ESTADO != P.OPERACIONAL:
        print('  PORQUE: %s' % dep.PORQUE)
        print('\nSEM_BANCADA_OPERACIONAL — declarar SINTONIA_COLLECTION_DSN')
        print('\nLINKEDIN_MIDIA_ATE_A_SALA = NOT_EXERCISED')
        return 3
    memoria, rastro = dep.memoria, dep.banco_do_rastro

    reg.carregar_adaptadores()
    run_id = '%s-T8-%s-%s' % (PAIS, time.strftime('%Y-%m-%d-%H%M%S'),
                              hashlib.sha256(POST.encode()).hexdigest()[:16])
    print('RUN_ID          = %s' % run_id)
    print('FONTE           = %s' % FONTE)

    # ─ 1 · A AQUISIÇÃO, PELO EXECUTOR CANÔNICO ───────────────────────────
    print('\n1 · AQUISICAO (executor canonico)')
    objetos, trace = sx.COLLECT(platform='LINKEDIN', capability=CAPACIDADE,
                                run_id=run_id, post_url=POST)
    print('  RESULT        = %s' % trace.get('RESULT'))
    print('  ROUTE         = %s' % trace.get('ROUTE'))
    print('  COST_STATE    = %s · USD %s' % (trace.get('COST_STATE'),
                                             trace.get('ACTUAL_COST_USD')))
    if trace.get('RESULT') != 'OK' or not objetos:
        diz(False, 'a aquisicao devolveu um objeto', trace.get('RESULT'))
        print('\nLINKEDIN_MIDIA_ATE_A_SALA = FAIL')
        return 1
    env = objetos[0]
    bruto = env['RAW']
    caminho_media = os.path.join(RAIZ, bruto['RAW_REFERENCE'])
    with open(caminho_media, 'rb') as f:
        bytes_media = f.read()
    sha = hashlib.sha256(bytes_media).hexdigest()
    diz(sha == bruto['RAW_SHA256'], 'o SHA medido bate com o do envelope',
        sha[:16])
    print('  MEDIA_BYTES   = %d · SHA %s' % (len(bytes_media), sha[:16]))
    print('  RENDICOES     = %s · escolhida %s bps'
          % (bruto['RENDITIONS_FOUND'],
             (bruto.get('RENDITIONS') and min(
                 [r['BITRATE_BPS'] for r in bruto['RENDITIONS']
                  if r['BITRATE_BPS']] or [None])) or 'N/D'))
    print('  FFPROBE       = video=%s audio=%s dur=%s'
          % (bruto['VIDEO_STREAMS'], bruto['AUDIO_STREAMS'],
             bruto['VIDEO_DURATION']))
    diz(bruto['AUDIO_STREAMS'] and bruto['AUDIO_STREAMS'] >= 1,
        'a midia traz faixa de som', bruto['AUDIO_STREAMS'])
    diz(bruto.get('PLATFORM_POLICY_STATUS', '').startswith('RESTRICTED'),
        'o estado da plataforma continua RESTRICTED, e nao virou ALLOWED')

    # ── 2 · O RAW, PELO DONO FORWARD ──────────────────────────────────────
    print('\n2 · RAW_OBSERVATION (guarda/preservar_coleta)')
    corrida = {'RUN_ID': run_id, 'PLATFORM': 'LINKEDIN',
               'ACTOR': 'adaptador_linkedin.midia_do_post_publico',
               'ACTOR_VERSION': '1.0.0', 'SOURCE_COUNTRY': PAIS,
               'MISSION': 'LINKEDIN-MEDIA-PUBLICA-V1',
               'STARTED_AT': agora(), 'RULE_VERSION': 'v1',
               'CAPTURE_METHOD': 'HTTP_GET'}
    artefato = {'COUNTRY': PAIS, 'SOURCE_SLUG': FONTE.lower(), 'SOURCE_ID': FONTE,
                'ARTIFACT_KIND': 'MEDIA',
                'NAME': 'linkedin-post-%s.mp4' % env['NATIVE_ID'],
                'SOURCE_NATIVE_ID': env['NATIVE_ID'],
                'SHA256': sha, 'BYTES': len(bytes_media),
                'MEDIA_TYPE': 'video/mp4',
                'CAPTURED_AT': agora(), 'SOURCE_URL': POST}
    armazem = pc.ArmazemLocal(ARMAZEM)
    recibo = pc.preservar(corrida, [artefato], armazem,
                          lambda o: bytes_media, memoria=memoria)
    print('  PRESERVAR     = %s' % json.dumps(
        {k: v for k, v in recibo.items()
         if k in ('ESTADO', 'OBJETOS_PLANEADOS', 'OBSERVACOES_PLANEADAS',
                  'CONFERIDOS', 'ESCRITOS')}, ensure_ascii=False))
    raw_id = int(memoria._valor(
        "select id from public.raw_asset where run_id = '%s' and sha256 = '%s'"
        % (run_id, sha)))
    storage_path = memoria._valor(
        "select storage_path from public.raw_asset where id = %d" % raw_id)
    storage_obj = memoria._valor(
        "select coalesce(storage_object_id::text,'NAO_TEM') from public.raw_asset"
        " where id = %d" % raw_id)
    print('  RAW_OBSERVATION_ID = %s  (= raw_asset.id)' % raw_id)
    print('  STORAGE_PATH       = %s' % storage_path)
    print('  STORAGE_OBJECT_ID  = %s' % storage_obj)
    diz(raw_id > 0, 'RAW_OBSERVATION_ID e um id do banco', raw_id)

    # ── 3 · O CANAL DA FONTE (pré-condição de identidade) ─────────────────
    print('\n3 · O CANAL DA FONTE')
    canal_id = _canal(rastro, FONTE)
    print('  CANAL_ID      = %s' % canal_id)
    diz(bool(canal_id), 'o canal da fonte existe ou foi criado', canal_id)

    # ── 4 · DERIVED — a Ponte de Mídia, sem saber de onde o byte veio ─────
    print('\n4 · DERIVED (coleta/derivacao_forward → ponte de midia)')
    unidade = {'RAW_ASSET_ID': raw_id, 'PDF': caminho_media,
               'MEDIA_TYPE': 'video/mp4', 'CAPTURED_AT': agora(),
               'SOURCE_ID': FONTE}
    r_der = fwd.correr([unidade], banco_do_rastro=rastro, run_id=run_id,
                       armazem=armazem, memoria=memoria, source_id=FONTE,
                       route_class_id=None, relogio=agora)
    print('  DERIVED       = %s' % json.dumps(r_der, ensure_ascii=False,
                                              default=str)[:400])
    filho = _filho(memoria, raw_id)
    if filho:
        print('  DERIVED_ARTIFACT_ID = %s · kind=%s · sha=%s'
              % (filho['id'], filho['kind'], filho['sha256'][:16]))
    diz(bool(filho), 'nasceu um derivado do RAW')

    # ── 5 · STRUCTURED → ADMISSION → SALA, pela estrada que já existia ────
    print('\n5 · STRUCTURED → ADMISSION → SALA (rota forward M2)')
    texto = _texto(memoria, armazem, filho) if filho else ''
    print('  TRANSCRIPT_CHARS = %d' % len(texto))
    diz(len(texto) > 0, 'o derivado traz texto legivel', len(texto))
    parent = _parent_sha(memoria, raw_id)
    unidade = {'CONTENT_ID': 'LI-%s' % (filho['sha256'][:16] if filho else 'SEM'),
               'TEXTO': texto, 'TIPO': 'nota_tecnica', 'SOURCE_ID': FONTE,
               'ROUTE_CLASS_ID': None, 'RAW_ASSET_ID': raw_id,
               'CAPTURED_AT': agora(), 'URL': POST,
               'DERIVED_ARTIFACT_ID': filho['id'] if filho else None,
               # ── O ESTAGIO VIAJA, E E ELE QUE ESCOLHE AS PERGUNTAS ──────
               # Isto NÃO é um fato de campo: é a TRANSCRIÇÃO de um vídeo, um
               # artefacto DERIVADO de um RAW que já está no acervo. Declarar
               # `DERIVED` é dizer o que a coisa é — e é por isso que a porta
               # deixa de perguntar «quando o fato aconteceu» (que um texto
               # derivado não sabe) e passa a perguntar linhagem e identidade,
               # que ele sabe.
               #
               #     A PORTA ESTAVA CERTA. A PERGUNTA É QUE ERA A ERRADA.
               'ARTIFACT_TYPE': 'DERIVED',
               'PARENT_SHA256': parent,
               'PARENT_ARTIFACT_ID': (filho or {}).get('raw_asset_id') or raw_id}
    r_s = m2.estruturar(rastro, unidade=unidade, run_id=run_id, canal_id=canal_id)
    print('  STRUCTURED    = %s · conteudo_id=%s'
          % ((r_s or {}).get('STATE'), (r_s or {}).get('CONTEUDO_ID')))
    diz(bool(r_s), 'a unidade foi estruturada')

    dec = None
    if (r_s or {}).get('STATE') in ('OK', 'REOBSERVED'):
        dec = m2.admitir(rastro, unidade=unidade, run_id=run_id,
                         conteudo_id=r_s.get('CONTEUDO_ID'))
    print('  ADMISSION     = %s' % getattr(dec, 'resultado', 'NAO_CORREU'))
    diz(dec is not None, 'a Admissao correu')

    espera = (m2.levar_a_espera(rastro, unidade=unidade, decisao=dec,
                                run_id=run_id)
              if dec is not None else {'ESTADO': None, 'PORQUE': 'a porta nao correu'})
    print('  READY         = %s' % (espera.get('ESTADO') or 'NOT_RUN'))
    print('  SALA          = %s' % (espera.get('FICHEIRO') or 'NOT_RUN'))
    linha_sala = _uma(memoria,
                      "select coalesce(ordem::text,'NAO_TEM') from"
                      " public.sala_de_espera where run_id = '%s' limit 1" % run_id)
    print('  SALA_ROW_ID   = %s' % linha_sala)
    diz(getattr(dec, 'resultado', None) == 'SIM' or linha_sala != 'NAO_TEM',
        'a Sala decidiu sobre a unidade (SIM pousa; NAO/ERRO produzem NOT_RUN)')

    print('\n' + '=' * 88)
    print('RESUMO')
    print('=' * 88)
    print('RUN_ID             = %s' % run_id)
    print('SOURCE_ID          = %s' % FONTE)
    print('RAW_OBSERVATION_ID = %s' % raw_id)
    print('STORAGE_PATH       = %s' % storage_path)
    print('STORAGE_OBJECT_ID  = %s' % storage_obj)
    print('CANAL_ID           = %s' % canal_id)
    print('DERIVED_ARTIFACT_ID= %s' % (filho['id'] if filho else None))
    print('TRANSCRIPT_CHARS   = %d' % len(texto))
    print('ADMISSION          = %s' % getattr(dec, 'resultado', 'NAO_CORREU'))
    print('SALA_ROW_ID        = %s' % linha_sala)
    print('FALHAS             = %s' % (FALHAS or 'nenhuma'))
    return 0 if not FALHAS else 1


def _texto(memoria, armazem, filho):
    """O texto do derivado, lido do ARMAZEM pelo caminho que o banco declara."""
    if not filho:
        return ''
    caminho = filho.get('storage_path') or ''
    try:
        dados = armazem.ler(caminho)
    except Exception:                                          # noqa: BLE001
        return ''
    try:
        return dados.decode('utf-8')
    except Exception:                                          # noqa: BLE001
        return ''


def _uma(memoria, sql, padrao='NAO_TEM'):
    """Um valor, ou `padrao` — e zero linhas é uma resposta, não uma exceção."""
    try:
        return memoria._valor(sql)
    except Exception:                                          # noqa: BLE001
        return padrao


def _parent_sha(memoria, raw_id):
    return memoria._valor(
        "select (select sha256 from public.raw_asset where id = %d)"
        % raw_id)


def _canal(rastro, fonte):
    """A pre-condicao de identidade: organizacao → origem → canal.

    ⚠️ GAP HERDADO, e nao se finge que nao e: `public.conteudo` exige
    `canal_id`, e criar um canal exige decidir DE QUEM ele e. Nenhum dono
    forward resolve isso hoje. A deduplicacao e explicita.
    """
    def q(v):
        return "'" + str(v).replace("'", "''") + "'"
    # A ORGANIZACAO e o PUBLISHER MEDIDO — o identificador publico que o proprio
    # endereco do post carrega. `tipo='empresa'` porque e o que a pagina declara
    # (`author.type = company`), e nao uma inferencia nossa.
    # A FONTE e o rotulo registado (`origem.rotulo`), e o CANAL e a pagina
    # publica dentro dessa fonte. Sao tres especies: quem publica, a fonte por
    # onde se observa, e o canal que se observa.
    nome = 'cosemar-ozono'
    org = rastro.executa(
        "with novo as (insert into public.organizacao (nome_canonico, tipo)"
        " select %s, 'empresa' where not exists"
        "  (select 1 from public.organizacao where nome_canonico = %s)"
        " returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.organizacao where nome_canonico = %s))"
        % (q(nome), q(nome), q(nome)))
    ori = rastro.executa(
        "with novo as (insert into public.origem (organizacao_id, rotulo)"
        " select %d, %s where not exists"
        "  (select 1 from public.origem where rotulo = %s) returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.origem where rotulo = %s))"
        % (int(org[0][0]), q(fonte), q(fonte), q(fonte)))
    can = rastro.executa(
        "with novo as (insert into public.canal"
        " (origem_id, plataforma, channel_id, url) values (%d, 'linkedin', %s, %s)"
        " on conflict (plataforma, channel_id) do nothing returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.canal where plataforma='linkedin'"
        "     and channel_id=%s))"
        % (int(ori[0][0]), q(nome), q('https://www.linkedin.com/company/%s' % nome),
           q(nome)))
    return int(can[0][0])


def _filho(memoria, raw_id):
    """O derivado deste CONTEUDO — e não deste `raw_asset`.

    O derivado pende do `raw_asset`, e um REUSED faz a segunda corrida apontar
    para o `raw_asset` da PRIMEIRA. Procurar só pelo id da corrida devolveria
    vazio sobre um derivado que existe — e esse vazio não é «não há»: é «não
    olhei onde ele está».
    """
    linhas = memoria._linhas(
        "select d.id, d.kind, d.sha256, d.storage_path, d.raw_asset_id"
        " from public.derived_artifact d"
        " where d.raw_asset_id in (select id from public.raw_asset"
        "   where sha256 = (select sha256 from public.raw_asset where id = %d))"
        " order by d.id desc limit 1" % raw_id,
        ('id', 'kind', 'sha256', 'storage_path', 'raw_asset_id'))
    if not linhas:
        return None
    return linhas[0]


if __name__ == '__main__':
    raise SystemExit(main())