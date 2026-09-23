#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D24 · O REEL PÚBLICO DE UMA PESSOA DO AGRO NO INSTAGRAM — o canário real.

POR QUE ESTE CANÁRIO EXISTE
---------------------------
A D24 (dono real, 2026-09-23, `DECISOES-DONO-2026-09-23.md`) autorizou, por
escrito, o VÍDEO de PESSOAS do agro **em qualquer plataforma já coberta pela
matriz do Scrap**. A D22 já tinha autorizado os Reels do Instagram por URL
directa. Nas duas, o dono assumiu o risco e a plataforma continua a proibir —
o desenho da casa é escrever as DUAS frases lado a lado, como se fez no áudio
do YouTube (`PUBLIC_AUDIO_ONLY`, D17.4/C13) e no vídeo de organização do
LinkedIn (`PUBLIC_ORG_VIDEO_ONLY`, D23).

O que faltava era a MEDIÇÃO desta metade: um Reel público de uma PESSOA do agro,
por URL directa, sem conta, sem login, sem cookie de sessão e sem contornar
muro nenhum.

    MEDIR ANTES DE DECLARAR. O CANÁRIO CORRE COM A ROTA ESTAGIADA EM MEMÓRIA,
    E A LEI SÓ PASSA A `PROVED` DEPOIS DE ELE DEVOLVER OS NÚMEROS.

ORDEM, E ELA IMPORTA
--------------------
```
1 · portão de egresso IT (antes)      — o ambiente de rede é medido, não suposto
2 · a decisão da matriz, sem estágio  — o ponto de partida fica escrito
3 · estágio declarado da rota D24     — em memória, por este processo, e só aqui
4 · a aquisição (a cadeia provada)    — reel_transcricao.transcrever_reel
5 · portão de egresso IT (depois)     — a corrida inteira aconteceu em IT?
6 · a matriz é restaurada             — este canário não muda a lei, mede-a
```

    UM CANÁRIO QUE MUDASSE A LEI PARA SI PRÓPRIO NÃO MEDIRIA NADA.

O QUE ESTE CANÁRIO NÃO FAZ
--------------------------
Não usa conta, login, cookie de sessão, navegador logado, CAPTCHA nem rota paga.
Não recolhe contatos, seguidores, mensagens nem comentários de terceiros. Não
toca no perfil como fonte: o alvo é a PUBLICAÇÃO, e a base é DESCARTÁVEL
(`guardar=False` → a oficina é um `tempfile.mkdtemp`, e nada entra no acervo).

Uso:
    python provas/canario_d24_reel_de_pessoa.py [url_do_reel]
"""
import hashlib
import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ('coleta', 'leis', 'ferramentas', 'regras', 'superficie', ''):
    sys.path.insert(0, os.path.join(RAIZ, _g) if _g else RAIZ)
import _gavetas  # noqa: E402,F401
import social_matriz as mz            # noqa: E402 — o dono da política
import rede as superficie             # noqa: E402 — o dono do portão de egresso
import reel_transcricao as rt         # noqa: E402 — a cadeia provada do Reel

RUN_ID = 'D24-REEL-PESSOA-20260923'
EGRESSO_EXIGIDO = 'IT'

#: A PESSOA, E O QUE PROVA QUE É DO AGRO.
#: Nome e papel vêm de PUBLICAÇÃO PRÓPRIA de terceiro (imprensa italiana que a
#: entrevistou) — não de inferência nossa sobre o handle.
PESSOA = {
    'ACCOUNT_HANDLE': 'dr.agricultura',
    'NOME_PUBLICO': 'Alessandro Giglietti',
    'PAPEL': 'dottore agronomo (laureado em Agraria, Univ. Firenze) — divulgador',
    'PAIS_DECLARADO': 'IT',
    'EVIDENCIA_DO_PAPEL': ('imprensa italiana: Gazzetta di Siena e Corriere.it '
                           'publicam a entrevista do agronomo, identificando-o pelo '
                           'handle @dr.agricultura'),
}

#: O REEL — descoberto pela JANELA PÚBLICA da própria casa, deslogada, sobre a
#: GRADE do perfil (a rota que a matriz declara em `INSTAGRAM/INCREMENTAL`).
#: Nenhum buscador, nenhum serviço que revenda dados da plataforma.
DISCOVERY_METHOD = 'PUBLIC_BROWSER · grade pública do perfil, deslogada (coleta/instagram_janela.py)'
URL_DO_REEL = (sys.argv[1] if len(sys.argv) > 1
               else 'https://www.instagram.com/reel/DdW2PPWAqht/')


def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def _rota_d24():
    """A rota que a D24 manda declarar — construída AQUI para poder ser medida."""
    return mz.r('instagram:reel-publico-de-pessoa-do-agro', 'LOCAL_EXECUTOR',
                'SIM', 'PROVED', 'zero',
                'Reel PÚBLICO de pessoa do agro, por URL directa e sem conta: '
                'a cadeia que já estava provada (yt-dlp + ASR local) atravessa o '
                'portão da matriz com os DOIS eixos escritos — o dono autorizou '
                '(D22/D24) e a plataforma proíbe (DISALLOWED, medido no robots.txt '
                'vivo). Sem perfil, sem login, sem cookie, sem muro contornado, '
                'sem contatos, sem seguidores, sem DM e sem comentários.',
                'docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md',
                owner_authorized='SIM', platform_policy='DISALLOWED',
                limite='PUBLIC_PERSON_VIDEO_ONLY')


def main():
    out = {'RUN_ID': RUN_ID, 'QUANDO': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'DECISAO_DO_DONO': 'D24 · DECISOES-DONO-2026-09-23.md',
           'LIMITE': 'PUBLIC_PERSON_VIDEO_ONLY', 'PESSOA': PESSOA,
           'ALVO': URL_DO_REEL, 'DISCOVERY_METHOD': DISCOVERY_METHOD,
           'CUSTO_USD': 0.0}

    # ── 1 · O AMBIENTE DE REDE, ANTES ───────────────────────────────────────
    antes = superficie.portao_de_egresso(EGRESSO_EXIGIDO)
    out['EGRESS_BEFORE'] = antes['EGRESS_COUNTRY_CODE']
    out['EGRESS_GATE_BEFORE'] = antes['EGRESS_GATE']
    if antes['EGRESS_GATE'] != 'PASS':
        out['RESULTADO'] = 'PARADO_NO_PORTAO_DE_EGRESSO'
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 1

    # ── 2 · O PONTO DE PARTIDA, SEM ESTÁGIO ─────────────────────────────────
    d_antes = mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')
    out['DECISAO_SEM_ESTAGIO'] = {'DECISAO': d_antes['DECISAO'], 'ROTA': d_antes['ROTA']}

    # ── 3 · O ESTÁGIO, DECLARADO ────────────────────────────────────────────
    original = list(mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT'])
    mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT'] = original + [_rota_d24()]
    d_depois = mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')
    out['ESTAGIO_DECLARADO'] = {
        'PORQUE': ('a lei só passa a `PROVED` depois de este canário devolver os '
                   'números; o estágio vive só neste processo e é restaurado no fim'),
        'DECISAO_COM_ESTAGIO': d_depois['DECISAO'], 'ROTA': d_depois['ROTA'],
        'OWNER_AUTHORIZED': d_depois.get('OWNER_AUTHORIZED'),
        'PLATFORM_POLICY_STATUS': d_depois.get('PLATFORM_POLICY_STATUS'),
        'LIMITE': d_depois.get('LIMITE')}
    try:
        # ── 4 · A AQUISIÇÃO — pela cadeia provada, com base DESCARTÁVEL ─────
        ident = rt.identidade_do_url(URL_DO_REEL)
        ident['COUNTRY_SCOPE'] = PESSOA['PAIS_DECLARADO']
        registo = rt.transcrever_reel(ident, run_id=RUN_ID, guardar=False)
        out['IDENTIDADE'] = {'PLATFORM': ident.get('PLATFORM'),
                             'POST_ID': ident.get('POST_ID'),
                             'SOURCE_URL': ident.get('SOURCE_URL')}
        out['OFICINA_DESCARTAVEL'] = registo.get('OFICINA')
        out['OFICINA_E_A_GAVETA'] = registo.get('OFICINA_E_A_GAVETA')
        out['MEDIA_STATE'] = registo.get('MEDIA_STATE')
        out['MEDIA_KIND_USED'] = registo.get('MEDIA_KIND_USED')
        out['AUDIO_ONLY_ACQUISITION'] = registo.get('AUDIO_ONLY_ACQUISITION')
        out['TRANSCRIPT_STATE'] = registo.get('TRANSCRIPT_STATE')
        out['CAPTURE_ATTEMPTS'] = registo.get('CAPTURE_ATTEMPTS')
        out['RAW_LINHAS'] = len(registo.get('RAW') or [])
        out['DERIVED'] = {k: v for k, v in (registo.get('DERIVED') or {}).items()
                          if k in ('AUTHOR_TEXT', 'NATIVE_CAPTION', 'TRANSCRIPT_TEXT',
                                   'DERIVED_TEXT', 'ASR_OWNER', 'DERIVATION_METHOD')}
        out['CAPTION_TEXT_CHARS'] = len(registo.get('CAPTION_TEXT') or '') \
            if isinstance(registo.get('CAPTION_TEXT'), str) else None
        out['ERRO'] = registo.get('ERROR') or registo.get('ERRO')
        # ── os bytes, medidos no disco, com hash — a prova que não se finge ──
        cru = registo.get('RAW')
        midia = cru[0] if isinstance(cru, list) and cru else (cru if isinstance(cru, dict) else {})
        out['RAW_CHAVES'] = sorted(midia)[:40] if isinstance(midia, dict) else None
        caminhos = {k: v for k, v in (midia or {}).items()
                    if isinstance(k, str) and k.endswith('STORAGE_LOCATION')}
        out['FICHEIROS'] = {}
        for k, v in caminhos.items():
            if isinstance(v, str) and os.path.exists(v):
                out['FICHEIROS'][k] = {'BYTES': os.path.getsize(v), 'SHA256': _sha256(v)}
            else:
                out['FICHEIROS'][k] = {'BYTES': None, 'SHA256': None}
    finally:
        # ── 6 · A MATRIZ VOLTA AO QUE ERA ──────────────────────────────────
        mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT'] = original
        out['MATRIZ_RESTAURADA'] = (mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO']
                                    == d_antes['DECISAO'])

    depois = superficie.portao_de_egresso(EGRESSO_EXIGIDO)
    out['EGRESS_AFTER'] = depois['EGRESS_COUNTRY_CODE']
    out['EGRESS_GATE_AFTER'] = depois['EGRESS_GATE']
    out['RESULTADO'] = ('ADQUIRIDO' if out.get('MEDIA_STATE') == 'MEDIA_OK'
                        else 'MEDIA_STATE=%s' % out.get('MEDIA_STATE'))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())