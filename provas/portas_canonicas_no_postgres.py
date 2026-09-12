#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C10.6D — O COMANDO QUE O WORKFLOW CORRE ENTRA PELA CASA CERTA.

    BANCO_DESCARTAVEL_URL=postgresql://... py provas/portas_canonicas_no_postgres.py

Não basta provar que a função Python funciona. O que esta prova mede é o
**comando final do YAML**: ela parseia o workflow, extrai o que cada fase manda
correr, e confere que o alvo é a entrada canônica — não a implementação.

    WORKFLOW É DISPARADOR. WORKFLOW NÃO É MOTOR DE COLETA.

E depois corre o caminho inteiro, offline, contra Postgres de verdade:

    comando do workflow → coleta/social_scrap.py coletar
    → scrap_executor.COLLECT → CHECK → roteador (portão · sessão · gasto)
    → adaptador → implementação

`NETWORK_REAL = 0`: o navegador é substituído por um que grita se alguém o subir.
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

DSN = (os.environ.get('BANCO_DESCARTAVEL_URL') or '').strip()
LOCAL = ('localhost', '127.0.0.1', '::1', '@postgres', '/var/run/postgresql')
WF = '.github/workflows/sintonia-scrap.yml'

#: As fases que a C10.6D classificou como COLLECTION com rota canônica.
CANONICAS = ('janela', 'janela-perfis', 'janela-objetos')
#: As que ela classificou como COLLECTION SEM rota canônica: têm de RECUSAR.
BLOQUEADAS = ('diario', 'yt-canais', 'yt-objetos', 'yt-legendas', 'yt-alvos',
              'yt-transcrever', 'bio', 'posts', 'reels', 'comentarios')
#: As implementações que nenhuma fase de Collection pode voltar a chamar direto.
IMPLEMENTACOES = ('instagram_janela.py', 'instagram_diario.py',
                  'youtube_janela.py', 'youtube_transcrever.py',
                  'instagram_transcrever.py', 'reel_transcricao.py',
                  'youtube_oficial.py')

TOCOU = []


def ler(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8', errors='replace').read()


def comandos_por_fase():
    """O que o `case` do workflow manda correr, fase a fase. Parseado, não grep."""
    import yaml
    doc = yaml.safe_load(ler(WF))
    runs = []

    def varre(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'run' and isinstance(v, str):
                    runs.append(v)
                varre(v)
        elif isinstance(o, list):
            for v in o:
                varre(v)
    varre(doc)
    por_fase, fase = {}, None
    for bloco in runs:
        if 'case "${{ inputs.fase }}"' not in bloco:
            continue
        for linha in bloco.splitlines():
            nu = linha.strip()
            if not nu or nu.startswith('#'):
                continue
            m = re.match(r'([\w|*-]+)\)\s*(.*)$', nu)
            if m:
                fase = m.group(1)
                resto = m.group(2)
                for f in fase.split('|'):
                    por_fase.setdefault(f, [])
                if resto:
                    for f in fase.split('|'):
                        por_fase[f].append(resto)
                continue
            if fase:
                for f in fase.split('|'):
                    por_fase.setdefault(f, []).append(nu)
    return por_fase


def main():
    falhas_ = []
    por_fase = comandos_por_fase()

    # ── 1 · O COMANDO DO WORKFLOW APONTA PARA A ENTRADA CANÔNICA ──────────
    print('═══ FASE 17 · O COMANDO EXACTO DO WORKFLOW ═══')
    for f in CANONICAS:
        cmds = ' '.join(por_fase.get(f) or [])
        alvo_ok = 'social_scrap.py' in cmds and 'coletar' in cmds
        direto = [i for i in IMPLEMENTACOES if i in cmds]
        print('  %-16s entrada_canonica=%-5s implementacao_direta=%s'
              % (f, alvo_ok, direto or 'NO'))
        if not alvo_ok:
            falhas_.append('%s: o comando nao aponta para a entrada canonica' % f)
        if direto:
            falhas_.append('%s: o workflow ainda corre %s' % (f, direto))

    print()
    print('═══ AS FASES SEM ROTA CANONICA RECUSAM ═══')
    for f in BLOQUEADAS:
        cmds = ' '.join(por_fase.get(f) or [])
        recusa = 'recusar' in cmds
        direto = [i for i in IMPLEMENTACOES if i in cmds]
        print('  %-16s recusa=%-5s implementacao_direta=%s'
              % (f, recusa, direto or 'NO'))
        if not recusa:
            falhas_.append('%s: deixou de recusar' % f)
        if direto:
            falhas_.append('%s: continua a correr %s' % (f, direto))

    # ── 2 · NENHUMA FASE CAI NUM RAMO QUE NINGUEM RECLAMA ─────────────────
    import yaml
    doc = yaml.safe_load(ler(WF))
    opcoes = ((doc.get('on') or doc.get(True))['workflow_dispatch']['inputs']
              ['fase']['options'])
    orfas = [o for o in opcoes if o not in por_fase]
    print()
    print('  fases oferecidas=%d · sem ramo proprio=%d %s'
          % (len(opcoes), len(orfas), orfas or ''))
    if orfas:
        falhas_.append('fases sem ramo proprio caem no `*`: %s' % orfas)

    # ── 3 · O CAMINHO INTEIRO, CONTRA POSTGRES DE VERDADE ─────────────────
    if not DSN:
        print('\nBANCO_DESCARTAVEL_URL ausente — a metade durável não corre.')
        print('PORTAS_CANONICAS=%s' % ('PASS' if not falhas_ else 'FAIL'))
        return 0 if not falhas_ else 1
    if not any(m in DSN for m in LOCAL):
        print('PORTAS_CANONICAS=RECUSADA_ENDERECO_NAO_LOCAL')
        return 1

    import coleta_checkpoint as ck
    import cdp
    import social_scrap as ss

    # ⚠️ A ARMADILHA É A PROVA, NÃO A FALHA.
    # A rota canônica desta capacidade é `PUBLIC_BROWSER`: ela SOBE navegador.
    # Interromper-lhe o navegador prova duas coisas ao mesmo tempo — que o
    # caminho chegou mesmo à implementação certa, e que nada saiu daqui.
    #
    #     UMA PROVA DE WIRING NÃO PRECISA DA PLATAFORMA.
    #     PRECISA DE CHEGAR ATÉ À PORTA E PARAR LÁ.
    def _intercepta(*a, **k):
        TOCOU.append('cdp.subir')
        raise cdp.Erro('navegador interceptado pela prova: nada sai daqui')
    cdp.subir = _intercepta
    cdp.abrir = _intercepta

    banco = ck.Banco(DSN)
    try:
        banco.executa('select 1 from public.collection_run limit 1')
    except Exception:                                             # noqa: BLE001
        print('\nschema ausente; a metade durável não corre.')
        print('PORTAS_CANONICAS=%s' % ('PASS' if not falhas_ else 'FAIL'))
        return 0 if not falhas_ else 1

    print()
    print('═══ FASE 15 · O CAMINHO INTEIRO, OFFLINE, CONTRA POSTGRES ═══')
    rc = ss.coletar('janela-perfis', run_id='RD-JANELA', banco=banco)
    linhas = banco.executa(
        "select status::text, coalesce(checkpoint_id::text,'-'),"
        " coalesce((select string_agg(e.etapa::text||'/'||e.estado::text,' ')"
        "   from public.etapa_da_corrida e where e.run_id = r.run_id),'-')"
        " from public.collection_run r where r.run_id = 'RD-JANELA'")
    if not linhas or not linhas[0] or not linhas[0][0]:
        falhas_.append('a fase canonica nao deixou RUN nenhuma')
        print('  NAO HOUVE RUN')
    else:
        status, cid, etapas = linhas[0][:3]
        print('  rc=%s · RUN=%s · checkpoint=%s · etapas=%s'
              % (rc, status, cid, etapas))
        if 'CHECK' not in etapas:
            falhas_.append('a etapa CHECK do boundary nao foi escrita')
        if 'DISCOVER' not in etapas:
            falhas_.append('a etapa DISCOVER do adaptador nao foi escrita — o '
                           'caminho nao chegou ao adaptador')
        if status == 'rodando':
            falhas_.append('a RUN ficou aberta')
        # ⚠️ UM PROCESSO VIVO NÃO DEIXA ETAPA PENDURADA.
        if 'RUNNING' in etapas:
            falhas_.append('uma etapa ficou em RUNNING com o processo vivo: %s'
                           % etapas)

    print()
    print('NAVEGADOR_INTERCEPTADO = %d   (a rota chegou à porta e parou lá)'
          % len(TOCOU))
    print('SAIDA_DE_REDE_REAL     = 0')
    if not TOCOU:
        falhas_.append('a armadilha do navegador nunca disparou — o caminho '
                       'não chegou à implementação, e esta prova mediria o ar')
    for f in falhas_:
        print('  ✗ %s' % f)
    print('PORTAS_CANONICAS=%s' % ('PASS' if not falhas_ else 'FAIL'))
    return 0 if not falhas_ else 1


if __name__ == '__main__':
    raise SystemExit(main())
