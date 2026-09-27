#!/usr/bin/env python3
"""
AS FRENTES PÚBLICAS DA CONCORRÊNCIA — o que já está na fila, e o que falta.

    python3 medidas/concorrencia_frentes.py            # regenera o quadro
    python3 medidas/concorrencia_frentes.py --conferir # 0 se o versionado bate

RÉGUA QUE MEDE (AGENTS.md: `medidas/`): não barra nada, conta quanto falta. Lê,
SÓ LEITURA, quatro livros, e escreve um quadro concorrente × frente:

    candidatas/FONTES-CANDIDATAS.json                      a fila de fontes
    curadoria/italy_contracts_curator.json                 os contratos do curador
    data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json     contas provadas pelo site oficial
    data/samples/CONCORRENCIA-META/PAGINAS-META-IT-V1.json a linha da Meta

O MESMO DESENHO DA LINHA DA META, EM LISTA
------------------------------------------
Cada frente pede o que a linha da Meta pede: uma CONTA provada por concorrente,
UMA visita por conta por rodada, snapshot datado, comparação com o anterior, e
saída pela Admissão. O quadro diz, para cada célula, em que degrau ela está:

    NA_LINHA              a linha existe e esta conta está nela (hoje: só Meta)
    CONTA_PROVADA_IT      conta com identidade PROVADA e escopo local IT
    CONTA_PROVADA_OUTRA   conta provada mas GLOBAL / escopo não provado
    NA_FILA               candidata na fila de fontes, com o estado dela
    FALTA                 nenhum dos livros tem nada — NÃO quer dizer «não existe»

    FALTA_NOS_LIVROS != A_CONTA_NAO_EXISTE

A frente diz também QUE executor já sabe colhê-la (a receita) e o limite que o
dono pôs (D22 Reels por URL direta; D23 vídeo da página pública de organização).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import meta_identidade as ident  # noqa: E402

EMPRESAS = ['BASF', 'Bayer', 'Syngenta', 'Corteva', 'FMC', 'UPL', 'Nufarm',
            'Sipcam', 'Gowan', 'Certis', 'Ascenza', 'ADAMA']
# Apelidos com prova escrita: Valagro é do grupo Syngenta (a própria fila tem
# «Valagro — Linkedin ufficiale» a apontar para linkedin.com/company/syngenta);
# «Certis Belchim» é o nome local da Certis.
APELIDOS = {'Syngenta': ['syngenta'], 'Certis': ['certis', 'certisbelchim'],
            'Sipcam': ['sipcam'], 'Ascenza': ['ascenza'], 'Gowan': ['gowan'],
            'Bayer': ['bayer'], 'BASF': ['basf'], 'Corteva': ['corteva'],
            'FMC': ['fmc'], 'UPL': ['upl'], 'Nufarm': ['nufarm'], 'ADAMA': ['adama']}

FRENTES = {
    'META_ADS': {'executor': 'concorrencia-meta', 'fase': 'meta-anuncios',
                 'limite': 'Biblioteca publica, sem login (D88)'},
    'LINKEDIN_EMPRESA': {'executor': 'scrap-colheita', 'fase': 'video-linkedin',
                         'limite': 'D23: so o video da pagina publica da organizacao; '
                                   'posts pedidos batem em ROUTE_NOT_ALLOWED'},
    'YOUTUBE': {'executor': 'scrap-colheita', 'fase': 'canal-youtube',
                'limite': 'API oficial (Data API v3)'},
    'INSTAGRAM': {'executor': 'scrap-colheita', 'fase': 'captura-reel',
                  'limite': 'D22: so Reel publico por URL DIRETA; listar os reels '
                            'de um perfil NAO esta autorizado — a frente precisa '
                            'de URL de reel, e conta sozinha nao chega'},
    'SITE_NOVIDADES': {'executor': 'italia-recorrente', 'fase': '',
                       'limite': 'HTTP direto, robots respeitado (D91)'},
}

NA_LINHA = 'NA_LINHA'
CONTA_PROVADA_IT = 'CONTA_PROVADA_IT'
CONTA_PROVADA_OUTRA = 'CONTA_PROVADA_OUTRA'
NA_FILA = 'NA_FILA'
FALTA = 'FALTA'

LIVROS = {
    'CANDIDATAS': 'candidatas/FONTES-CANDIDATAS.json',
    'CURADOR': 'curadoria/italy_contracts_curator.json',
    'CONTAS': 'data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json',
    'META': 'data/samples/CONCORRENCIA-META/PAGINAS-META-IT-V1.json',
}
SAIDA = 'data/samples/CONCORRENCIA-META/FRENTES-PUBLICAS-IT-V1.json'


def frente_do_url(url):
    u = (url or '').lower()
    if 'facebook.com/ads/library' in u:
        return 'META_ADS'
    for chave, frente in (('linkedin.com', 'LINKEDIN_EMPRESA'), ('youtube.com', 'YOUTUBE'),
                          ('youtu.be', 'YOUTUBE'), ('instagram.com', 'INSTAGRAM')):
        if chave in u:
            return frente
    if 'facebook.com' in u or 'x.com/' in u or 'twitter.com' in u or 'tiktok' in u:
        return None                                  # outra rede: fora das cinco
    return 'SITE_NOVIDADES'


def empresa_de(*textos):
    t = ' '.join(str(x or '') for x in textos).lower()
    for e in EMPRESAS:
        if any(re.search(r'(?<![a-z])' + re.escape(a) + r'(?![a-z])', t)
               for a in APELIDOS[e]):
            return e
    return None


def _ler(rel, raiz):
    with open(os.path.join(raiz, rel), encoding='utf-8') as f:
        return json.load(f)


def medir(raiz=RAIZ):
    cel = {(e, f): [] for e in EMPRESAS for f in FRENTES}
    lidos = {}
    cand = _ler(LIVROS['CANDIDATAS'], raiz).get('CANDIDATAS', [])
    lidos['CANDIDATAS'] = len(cand)
    for c in cand:
        if c.get('PAIS') not in ('IT', 'EU', None):
            continue
        e = empresa_de(c.get('NOME'), c.get('URL'))
        f = frente_do_url(c.get('URL'))
        if e and f:
            cel[(e, f)].append({'degrau': NA_FILA, 'livro': 'CANDIDATAS',
                                'id': c.get('CANDIDATA_ID'), 'estado': c.get('ESTADO'),
                                'url': c.get('URL'), 'nome': c.get('NOME')})
    cur = _ler(LIVROS['CURADOR'], raiz).get('FONTES', [])
    lidos['CURADOR'] = len(cur)
    for s in cur:
        e = empresa_de(s.get('OWNER'), s.get('NAME'), s.get('CANONICAL_ENTRY_URL'))
        f = frente_do_url(s.get('CANONICAL_ENTRY_URL'))
        if e and f:
            cel[(e, f)].append({'degrau': NA_FILA, 'livro': 'CURADOR',
                                'id': s.get('SOURCE_ID'), 'estado': 'CONTRATADA',
                                'url': s.get('CANONICAL_ENTRY_URL'), 'nome': s.get('NAME')})
    contas = _ler(LIVROS['CONTAS'], raiz).get('ACCOUNTS', [])
    lidos['CONTAS'] = len(contas)
    plataforma = {'LINKEDIN': 'LINKEDIN_EMPRESA', 'YOUTUBE': 'YOUTUBE',
                  'INSTAGRAM': 'INSTAGRAM', 'FACEBOOK': None}
    for a in contas:
        if a.get('COUNTRY') != 'IT' or a.get('ACCOUNT_IDENTITY_STATE') != 'PROVED':
            continue
        e = empresa_de(a.get('COMPANY'))
        f = plataforma.get(a.get('PLATFORM'))
        item = {'livro': 'CONTAS', 'id': a.get('ACCOUNT_CELL_ID'),
                'url': a.get('ACCOUNT_URL'), 'escopo': a.get('COUNTRY_SCOPE'),
                'autorizada': a.get('COLLECTION_AUTHORIZED')}
        if a.get('PLATFORM') == 'FACEBOOK':
            # Página de Facebook NÃO é página da Biblioteca: o número no endereço
            # é pista de PAGE_ID, e a prova tem de vir da própria Meta.
            m = re.search(r'-(\d{9,})/?$', a.get('ACCOUNT_URL') or '')
            if e and m:
                cel[(e, 'META_ADS')].append(dict(
                    item, degrau=NA_FILA, estado='PAGE_ID_CANDIDATO_DO_SITE_OFICIAL',
                    page_id_candidato=m.group(1),
                    nota='o site oficial liga esta pagina; confirmar o PAGE_ID pela '
                         'Meta antes de entrar na linha'))
            continue
        if e and f:
            cel[(e, f)].append(dict(item, degrau=(
                CONTA_PROVADA_IT if a.get('COUNTRY_SCOPE') == 'LOCAL_COUNTRY_PROVED'
                else CONTA_PROVADA_OUTRA)))
    meta = _ler(LIVROS['META'], raiz).get('PAGINAS', [])
    lidos['META'] = len(meta)
    for p in meta:
        e = empresa_de(p.get('company'))
        if not e:
            continue
        # o MESMO carimbo que a linha aplica: pagina recusada pela guarda nao
        # conta como «na linha» so por estar escrita na lista.
        entra, motivo = ident.carimbar(p)
        entra = entra and bool(p.get('EM_LINHA'))
        cel[(e, 'META_ADS')].append({
            'degrau': NA_LINHA if entra else NA_FILA, 'livro': 'META',
            'id': p.get('page_id'), 'nome': p.get('page_name'),
            'estado': 'EM_LINHA' if entra else (p.get('MOTIVO_FORA_DA_LINHA') or motivo)})
    # os PAGE_ID que já estão na linha não contam outra vez como candidatos
    na_linha = {str(p.get('page_id')) for p in meta}
    for (e, f), xs in cel.items():
        if f == 'META_ADS':
            cel[(e, f)] = [x for x in xs if not (x.get('page_id_candidato') in na_linha)]

    ordem = [NA_LINHA, CONTA_PROVADA_IT, CONTA_PROVADA_OUTRA, NA_FILA]
    quadro, faltas = [], []
    for e in EMPRESAS:
        linha = {'empresa': e, 'frentes': {}}
        for f, meta_f in FRENTES.items():
            xs = cel[(e, f)]
            degrau = next((d for d in ordem if any(x['degrau'] == d for x in xs)), FALTA)
            linha['frentes'][f] = {'degrau': degrau, 'executor': meta_f['executor'],
                                   'fase': meta_f['fase'], 'evidencias': xs}
            if degrau == FALTA:
                faltas.append('%s/%s' % (e, f))
        quadro.append(linha)
    contagem = {}
    for linha in quadro:
        for f, v in linha['frentes'].items():
            contagem.setdefault(f, {}).setdefault(v['degrau'], 0)
            contagem[f][v['degrau']] += 1
    return {'DATASET': 'CONCORRENCIA-FRENTES-PUBLICAS-IT-V1',
            'O_QUE_E': ('quadro concorrente x frente publica, medido SO por leitura '
                        'dos livros abaixo. Nada foi coletado para o montar.'),
            'LIVROS_LIDOS': {k: {'caminho': LIVROS[k], 'linhas': v} for k, v in lidos.items()},
            'FRENTES': FRENTES, 'DEGRAUS': ordem + [FALTA],
            'FALTA_SIGNIFICA': 'nenhum dos livros tem entrada. FALTA_NOS_LIVROS != A_CONTA_NAO_EXISTE',
            'CONTAGEM_POR_FRENTE': contagem, 'CELULAS_EM_FALTA': faltas,
            'QUADRO': quadro}


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n'


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    q = medir()
    destino = os.path.join(RAIZ, SAIDA)
    if '--conferir' in argv:
        with open(destino, encoding='utf-8') as f:
            igual = f.read() == _json(q)
        print('IGUAL' if igual else 'DIFERENTE — rode sem --conferir e commite')
        return 0 if igual else 1
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(_json(q))
    print(json.dumps(q['CONTAGEM_POR_FRENTE'], ensure_ascii=False, indent=1))
    print('em falta: %d celulas' % len(q['CELULAS_EM_FALTA']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
