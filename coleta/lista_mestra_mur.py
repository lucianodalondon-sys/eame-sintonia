#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LISTA MESTRA DE PESQUISADORES — o MUR (CERCA UNIVERSITA) como identidade oficial.

    py coleta/lista_mestra_mur.py --cruzar --mur=<MUR-*.json> --rodadas=<pasta T6> [--para=F]
    py coleta/lista_mestra_mur.py --plano  --mur=<MUR-*.json> --rodadas=<pasta T6>
    py coleta/lista_mestra_mur.py --rede --rodada=N --mur=<MUR-*.json> --rodadas=<pasta T6> --saida=<pasta>
    py coleta/lista_mestra_mur.py --ler  --mur=<MUR-*.json> --rodadas=<pasta T6> --saida=<pasta>

O «LATTES ITALIANO» QUE JA EXISTE
---------------------------------
O MUR publica, sem login, o cadastro de TODOS os docentes universitarios: nome, universidade,
departamento, cargo e setor (SSD). E a IDENTIDADE OFICIAL da pessoa. O OpenAlex e o ORCID dizem
o que ela PUBLICOU. Esta lista junta as duas coisas sem as confundir:

    MUR        quem e, onde esta, em que setor          (fonte oficial, nao se corrige)
    OpenAlex   o que publicou, com quem, sobre o que    (indice: erra instituicao, parte pessoas)
    ORCID      o que ELA declarou                        (prova da pessoa)

A LIGACAO E SEMPRE NOME + UNIVERSIDADE, NUNCA SO O NOME
------------------------------------------------------
    MUR_E_OBRAS      apelido e nome (ou inicial) batem E a universidade do MUR aparece numa
                     instituicao italiana declarada numa obra dessa pessoa
    SO_NOME          o nome bate, a universidade nao: NAO se liga (homonimo possivel)
    VARIOS_IDS       mais de um id OpenAlex bate com nome E universidade: ficam todos, sem fundir
    NAO_ENCONTRADO   nas obras que ja temos nao ha ninguem com esse nome: e o que falta ir buscar

Sem rede aqui (--cruzar, --plano, --ler). A rede (--rede) so quem pode, teto 5/dominio/rodada.
Nenhum campo novo no contrato T6: isto e uma LISTA de identidade, ao lado.
"""
import json
import os
import re
import sys
import time
import urllib.parse
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import pesquisadores_t6 as T6  # noqa: E402

NAO_SEI = T6.NAO_SEI
ORCID_BUSCA = 'https://pub.orcid.org/v3.0/expanded-search/'
OPENALEX_AUTORES = 'https://api.openalex.org/authors'
NOMES_POR_PEDIDO_ORCID = 20        # uma consulta Solr com 20 (apelido E nome) em OU
ORCIDS_POR_PEDIDO_OPENALEX = 50    # filtro orcid:a|b|... (OU)

# Como a universidade do MUR aparece nas instituicoes do indice (ingles e italiano). Medido nas
# 33 universidades do setor 07/AGRI-05; uma universidade fora daqui fica NAO SEI, nao inventada.
ATENEO = {
    'PADOVA': r'padova|padua', 'Napoli Federico II': r'federico ii|naples|napoli', 'MILANO': r'\bmilan|milano\b',
    'CATANIA': r'catania', 'BARI': r'\bbari\b', 'BOLOGNA': r'bologna', 'PALERMO': r'palermo',
    'TORINO': r'turin|torino', 'SASSARI': r'sassari', 'TUSCIA': r'tuscia', 'PISA': r'university of pisa|universita di pisa',
    'UDINE': r'udine', 'Cattolica del Sacro Cuore': r'cattolica', 'PERUGIA': r'perugia', 'FIRENZE': r'florence|firenze',
    'BASILICATA': r'basilicata', 'MOLISE': r'molise', 'Politecnica delle MARCHE': r'marche',
    'Mediterranea di REGGIO CALABRIA': r'mediterranea|reggio calabria', 'TRENTO': r'trento', 'FOGGIA': r'foggia',
    'Libera Università di BOLZANO': r'bozen|bolzano', 'ROMA "La Sapienza"': r'sapienza',
    'MODENA e REGGIO EMILIA': r'modena', 'VERONA': r'verona', 'FERRARA': r'ferrara', 'BRESCIA': r'brescia',
    'SALERNO': r'salerno', 'SIENA': r'siena', 'TERAMO': r'teramo', 'SALENTO': r'salento', "Scuola Superiore Sant'Anna": r"sant.anna",
    'CAMPANIA - "L. VANVITELLI"': r'vanvitelli|campania',
}
# O catalogo de producao (IRIS/CRIS) de cada universidade. PROVADO_NO_REPO = o endereco ja aparece
# em ficheiros desta casa; os outros sao a morada habitual do IRIS e ficam A_CONFIRMAR (sem rede).
IRIS = {
    'MILANO': ('https://air.unimi.it', 'PROVADO_NO_REPO'), 'TORINO': ('https://iris.unito.it', 'PROVADO_NO_REPO'),
    'FIRENZE': ('https://flore.unifi.it', 'PROVADO_NO_REPO'), 'BOLOGNA': ('https://cris.unibo.it', 'PROVADO_NO_REPO'),
    'PADOVA': ('https://www.research.unipd.it', 'A_CONFIRMAR'), 'Napoli Federico II': ('https://www.iris.unina.it', 'A_CONFIRMAR'),
    'CATANIA': ('https://www.iris.unict.it', 'A_CONFIRMAR'), 'BARI': ('https://ricerca.uniba.it', 'A_CONFIRMAR'),
    'PALERMO': ('https://iris.unipa.it', 'A_CONFIRMAR'), 'SASSARI': ('https://iris.uniss.it', 'A_CONFIRMAR'),
    'TUSCIA': ('https://dspace.unitus.it', 'A_CONFIRMAR'), 'PISA': ('https://arpi.unipi.it', 'A_CONFIRMAR'),
    'UDINE': ('https://air.uniud.it', 'A_CONFIRMAR'), 'Cattolica del Sacro Cuore': ('https://publicatt.unicatt.it', 'A_CONFIRMAR'),
    'PERUGIA': ('https://research.unipg.it', 'A_CONFIRMAR'), 'BASILICATA': ('https://iris.unibas.it', 'A_CONFIRMAR'),
    'MOLISE': ('https://iris.unimol.it', 'A_CONFIRMAR'), 'Politecnica delle MARCHE': ('https://iris.univpm.it', 'A_CONFIRMAR'),
    'Mediterranea di REGGIO CALABRIA': ('https://iris.unirc.it', 'A_CONFIRMAR'), 'TRENTO': ('https://iris.unitn.it', 'A_CONFIRMAR'),
    'FOGGIA': ('https://iris.unifg.it', 'A_CONFIRMAR'), 'Libera Università di BOLZANO': ('https://bia.unibz.it', 'A_CONFIRMAR'),
    'ROMA "La Sapienza"': ('https://iris.uniroma1.it', 'A_CONFIRMAR'), 'MODENA e REGGIO EMILIA': ('https://iris.unimore.it', 'A_CONFIRMAR'),
    'VERONA': ('https://iris.univr.it', 'A_CONFIRMAR'), 'FERRARA': ('https://sfera.unife.it', 'A_CONFIRMAR'),
    'BRESCIA': ('https://iris.unibs.it', 'A_CONFIRMAR'), 'SALERNO': ('https://www.iris.unisa.it', 'A_CONFIRMAR'),
    'SIENA': ('https://usiena-air.unisi.it', 'A_CONFIRMAR'), 'TERAMO': ('https://iris.unite.it', 'A_CONFIRMAR'),
    'SALENTO': ('https://iris.unisalento.it', 'A_CONFIRMAR'), "Scuola Superiore Sant'Anna": ('https://www.iris.sssup.it', 'A_CONFIRMAR'),
    'CAMPANIA - "L. VANVITELLI"': ('https://iris.unicampania.it', 'A_CONFIRMAR'),
}
# O que o casco pergunta, para ORDENAR a busca (medido nos temas que o OpenAlex devolve de cada autor)
CASCO_TEMAS = ('grape', 'vine', 'viticult', 'apple', 'maize', 'corn', 'tomato', 'downy mildew', 'powdery mildew',
               'botrytis', 'phytoplasma', 'leafhopper', 'moth', 'lepidoptera', 'fruit fly', 'plant pathogen',
               'fungal', 'insect', 'pest', 'fungicide', 'insecticide', 'biological control', 'entomolog')


def _ascii(s):
    s = (s or '').replace('&quot;', '"')
    return T6.CP._texto(s)


def ler_mur(caminho):
    """→ lista de pessoas do MUR, com o nome partido: apelido = palavras em MAIUSCULAS."""
    with open(caminho, encoding='utf-8') as h:
        linhas = json.load(h)
    out = []
    for x in linhas:
        nome = (x.get('Cognome e Nome') or '').strip()
        partes = nome.split()
        apelido = [p for p in partes if p.upper() == p and any(c.isalpha() for c in p)]
        dado = [p for p in partes if p not in apelido]
        ateneo = (x.get('Ateneo') or '').replace('&quot;', '"')
        out.append({'MUR_NOME': nome, 'APELIDO': ' '.join(apelido), 'NOME': ' '.join(dado), 'ATENEO': ateneo,
                    'SSD_2024': x.get('SSD 2024'), 'SSD_2015': x.get('SSD2015'), 'FASCIA': x.get('Fascia'),
                    'STRUTTURA': x.get('Struttura di afferenza'),
                    'IRIS': IRIS.get(ateneo, (NAO_SEI, NAO_SEI))[0], 'IRIS_ESTADO': IRIS.get(ateneo, (NAO_SEI, NAO_SEI))[1]})
    return out


def _bate_nome(p, nome_indice):
    t = _ascii(nome_indice).replace('.', ' ').replace('-', ' ').split()
    # o MUR escreve o acento com apostrofo: «ZAPPALA'» e Zappalà
    ap = _ascii(p['APELIDO']).replace("'", '').replace('-', ' ').split()
    dados = _ascii(p['NOME']).split()
    if not t or not ap or not dados:
        return False
    if t[-len(ap):] != ap:                     # o apelido do MUR inteiro no fim do nome do indice
        return False
    primeiro = t[0]
    return primeiro == dados[0] or (len(primeiro) == 1 and primeiro == dados[0][:1])


def autores_das_obras(rodadas):
    """Cada autor das obras T6 com as instituicoes ITALIANAS declaradas NAS obras dele."""
    us, _, _ = T6.ler_pasta(rodadas)
    a = {}
    for u in us:
        for x in u['AUTORES']:
            r = a.setdefault(x['OPENALEX_ID'], {'NOME': x['NOME'], 'ORCID': x['ORCID_NO_INDICE'], 'INST_IT': set(),
                                                'OBRAS': 0, 'PARES': set(), 'PROVAS': set()})
            r['OBRAS'] += 1
            r['PARES'].update(u['NA_CONSULTA_E_NO_TEXTO'])
            r['PROVAS'].add(x['PROVA_DA_PESSOA'])
            for i in (x['INSTITUICOES_NESTA_OBRA'] if x['INSTITUICOES_NESTA_OBRA'] != NAO_SEI else []):
                if i['PAIS'] == 'IT' and i['NOME']:
                    r['INST_IT'].add(i['NOME'])
    return a


def cruzar(mur, autores):
    """MUR x autores das obras. → lista com o ESTADO de cada pessoa do MUR (ver o cabecalho)."""
    out = []
    for p in mur:
        rx = re.compile(ATENEO.get(p['ATENEO'], r'(?!x)x'))
        por_nome = [(oid, r) for oid, r in autores.items() if r['NOME'] and _bate_nome(p, r['NOME'])]
        bons = [(oid, r) for oid, r in por_nome if any(rx.search(_ascii(i)) for i in r['INST_IT'])]
        estado = ('MUR_E_OBRAS' if len(bons) == 1 else 'VARIOS_IDS' if bons
                  else 'SO_NOME' if por_nome else 'NAO_ENCONTRADO')
        ligados = bons
        out.append(dict(p, ESTADO=estado,
                        OPENALEX_IDS=[oid for oid, _ in ligados],
                        ORCID=sorted({r['ORCID'] for _, r in ligados if r['ORCID'] != NAO_SEI}) or NAO_SEI,
                        OBRAS_NAS_589=sum(r['OBRAS'] for _, r in ligados),
                        PARES_DO_CASCO=sorted(set().union(*[r['PARES'] for _, r in ligados])) if ligados else [],
                        PROVA=sorted(set().union(*[r['PROVAS'] for _, r in ligados])) if ligados else [],
                        SO_NOME_COM=[{'OPENALEX_ID': oid, 'NOME': r['NOME'], 'INST_IT': sorted(r['INST_IT'])[:3]}
                                     for oid, r in por_nome] if estado == 'SO_NOME' else []))
    return out


# ═══════════════════════════════════ A CONSULTA POR PESSOA (so quem pode corre com rede)
def url_orcid_busca(pessoas):
    """Um pedido ao ORCID para varias pessoas: (apelido E nome) em OU, pela busca publica."""
    def termo(p):
        apelido = re.sub(r"([AEIOU])'", lambda m: {'A': 'à', 'E': 'è', 'I': 'ì', 'O': 'ò', 'U': 'ù'}[m.group(1)],
                         p['APELIDO']).title()
        return '(family-name:"%s" AND given-names:"%s")' % (apelido, p['NOME'].split()[0])
    q = ' OR '.join(termo(p) for p in pessoas)
    return ORCID_BUSCA + '?' + urllib.parse.urlencode({'q': q, 'rows': 200})


def url_openalex_por_orcid(orcids):
    q = urllib.parse.urlencode({'filter': 'orcid:' + '|'.join(orcids), 'per-page': 200,
                                'select': 'id,display_name,orcid,last_known_institutions,topics,works_count',
                                'mailto': T6.CP.MAILTO})
    return OPENALEX_AUTORES + '?' + q


def ler_busca_orcid(pessoas, resposta):
    """⚠️ NENHUMA resposta real da busca ORCID foi gravada nesta casa: os campos
    (expanded-result, orcid-id, given-names, family-names, institution-name) sao os da API publica
    v3.0 e a 1.a rodada prova-os. Uma pessoa so ganha ORCID se apelido, nome E universidade baterem."""
    res = (resposta or {}).get('expanded-result') or []
    out = {}
    for p in pessoas:
        rx = re.compile(ATENEO.get(p['ATENEO'], r'(?!x)x'))
        ok = []
        for r in res:
            nome = '%s %s' % (r.get('given-names') or '', r.get('family-names') or '')
            if _bate_nome(p, nome) and any(rx.search(_ascii(i)) for i in (r.get('institution-name') or [])):
                ok.append(r.get('orcid-id'))
        out[p['MUR_NOME'] + '|' + p['ATENEO']] = sorted(set(ok))
    return out


def prioridade(autor_openalex):
    """Quantos temas do autor (o OpenAlex devolve-os) falam do casco. MEDIDO, nao adivinhado."""
    temas = [(t.get('display_name') or '') for t in (autor_openalex.get('topics') or [])]
    return sum(1 for t in temas if any(k in _ascii(t) for k in CASCO_TEMAS))


def plano(pessoas_em_falta, com_orcid=0):
    import math
    return {'PESSOAS_A_PROCURAR': len(pessoas_em_falta),
            'ORCID_BUSCA_PEDIDOS': math.ceil(len(pessoas_em_falta) / NOMES_POR_PEDIDO_ORCID),
            'OPENALEX_AUTORES_PEDIDOS': math.ceil(max(com_orcid, len(pessoas_em_falta)) / ORCIDS_POR_PEDIDO_OPENALEX),
            'RODADAS_MINIMAS': max(math.ceil(math.ceil(len(pessoas_em_falta) / NOMES_POR_PEDIDO_ORCID) / T6.TETO_POR_DOMINIO), 1) + 1,
            'TETO_POR_DOMINIO_POR_RODADA': T6.TETO_POR_DOMINIO,
            'ORDEM': ('1) ORCID: todos, em lotes de 20; 2) OpenAlex /authors por ORCID, em lotes de 50: '
                      'instituicao atual e TEMAS; 3) as obras (consulta 2 do T6) pela prioridade medida nos temas')}


def rodada(n, mur, rodadas, saida, pausa=T6.PAUSA):
    """Rodada n: primeiro o ORCID para os NAO_ENCONTRADO/SO_NOME (lotes de 20, <= 5 pedidos);
    quando todos tiverem sido procurados, o OpenAlex /authors pelos ORCID achados (<= 5)."""
    os.makedirs(saida, exist_ok=True)
    f_est = os.path.join(saida, 'ESTADO-LISTA-MESTRA.json')
    est = T6._ler(f_est) if os.path.exists(f_est) else {'ORCID_PROCURADOS': [], 'ORCID_ACHADOS': {},
                                                        'OPENALEX_FEITOS': [], 'RODADAS': []}
    cruz = cruzar(mur, autores_das_obras(rodadas))
    falta = [p for p in cruz if p['ESTADO'] in ('NAO_ENCONTRADO', 'SO_NOME')
             and p['MUR_NOME'] + '|' + p['ATENEO'] not in est['ORCID_PROCURADOS']]
    reg = {'RODADA': n, 'PEDIDOS': {d: 0 for d in T6.DOMINIOS}, 'RESPOSTAS': []}

    def anotar(dom, nome, d, ok, porque):
        reg['PEDIDOS'][dom] += 1
        assert reg['PEDIDOS'][dom] <= T6.TETO_POR_DOMINIO, 'teto por dominio passado'
        nome = nome if ok else 'FALHA-r%d-%s' % (n, nome)
        reg['RESPOSTAS'].append({'DOMINIO': dom, 'FICHEIRO': nome, 'SHA256': T6._guardar(saida, nome, d),
                                 'OK': ok, 'PORQUE': porque})

    for k in range(0, min(len(falta), T6.TETO_POR_DOMINIO * NOMES_POR_PEDIDO_ORCID), NOMES_POR_PEDIDO_ORCID):
        lote = falta[k:k + NOMES_POR_PEDIDO_ORCID]
        d, err = T6.CP._get(url_orcid_busca(lote))
        ok = isinstance(d, dict) and 'expanded-result' in d
        anotar('pub.orcid.org', 'orcid-busca-r%d-%d.json' % (n, k // NOMES_POR_PEDIDO_ORCID + 1), d, ok,
               '' if ok else (err or 'sem expanded-result'))
        if not ok:
            break
        for chave, orcids in ler_busca_orcid(lote, d).items():
            est['ORCID_PROCURADOS'].append(chave)
            if orcids:
                est['ORCID_ACHADOS'][chave] = orcids
        time.sleep(pausa)
    if not falta:
        todos = sorted({o for v in est['ORCID_ACHADOS'].values() for o in v} - set(est['OPENALEX_FEITOS']))
        for k in range(0, min(len(todos), T6.TETO_POR_DOMINIO * ORCIDS_POR_PEDIDO_OPENALEX), ORCIDS_POR_PEDIDO_OPENALEX):
            lote = todos[k:k + ORCIDS_POR_PEDIDO_OPENALEX]
            d, err = T6._pedir(url_openalex_por_orcid(lote))
            ok, porque = T6.resposta_valida(d) if d is not None else (False, err)
            anotar('api.openalex.org', 'autores-orcid-r%d-%d.json' % (n, k // ORCIDS_POR_PEDIDO_OPENALEX + 1), d, ok, porque)
            if not ok:
                break
            est['OPENALEX_FEITOS'].extend(lote)
            time.sleep(pausa)
    est['RODADAS'].append({'RODADA': n, 'PEDIDOS': reg['PEDIDOS']})
    with open(f_est, 'w', encoding='utf-8', newline='\n') as h:
        json.dump(est, h, ensure_ascii=False, indent=1)
    with open(os.path.join(saida, 'RODADA-LISTA-%d.json' % n), 'w', encoding='utf-8', newline='\n') as h:
        json.dump(reg, h, ensure_ascii=False, indent=1)
    return reg


def ler(mur, rodadas, saida):
    """A lista mestra com o que as rodadas trouxeram: ORCID achado, temas, prioridade medida."""
    cruz = cruzar(mur, autores_das_obras(rodadas))
    f_est = os.path.join(saida, 'ESTADO-LISTA-MESTRA.json')
    est = T6._ler(f_est) if os.path.exists(f_est) else {'ORCID_ACHADOS': {}, 'ORCID_PROCURADOS': []}
    por_orcid = {}
    for f in sorted(os.listdir(saida)) if os.path.isdir(saida) else []:
        if f.startswith('autores-orcid-') and f.endswith('.json'):
            for a in (T6._ler(os.path.join(saida, f)).get('results') or []):
                por_orcid[(a.get('orcid') or '').rsplit('/', 1)[-1]] = a
    for p in cruz:
        chave = p['MUR_NOME'] + '|' + p['ATENEO']
        achados = est['ORCID_ACHADOS'].get(chave, [])
        p['ORCID_PELA_BUSCA'] = achados or (NAO_SEI if chave in est['ORCID_PROCURADOS'] else 'NAO_PROCURADO')
        autores = [por_orcid[o] for o in achados if o in por_orcid]
        p['TEMAS'] = [t.get('display_name') for a in autores for t in (a.get('topics') or [])][:8]
        p['PRIORIDADE_CASCO'] = max((prioridade(a) for a in autores), default=NAO_SEI)
    return cruz


def main(argv):
    opt = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '1') for a in argv if a.startswith('--'))
    mur = ler_mur(opt['mur'])
    if 'cruzar' in opt or 'plano' in opt:
        cruz = cruzar(mur, autores_das_obras(opt['rodadas']))
        conta = defaultdict(int)
        for p in cruz:
            conta[p['ESTADO']] += 1
        falta = [p for p in cruz if p['ESTADO'] in ('NAO_ENCONTRADO', 'SO_NOME')]
        r = {'MUR': len(mur), 'ESTADOS': dict(conta), 'PLANO': plano(falta), 'LISTA': cruz}
        if opt.get('para'):
            with open(opt['para'], 'w', encoding='utf-8', newline='\n') as h:
                json.dump(r, h, ensure_ascii=False, indent=1)
        print(json.dumps({k: r[k] for k in ('MUR', 'ESTADOS', 'PLANO')}, ensure_ascii=False, indent=1))
        return 0
    if 'rede' in opt:
        print(json.dumps(rodada(int(opt.get('rodada', '1')), mur, opt['rodadas'], opt['saida']),
                         ensure_ascii=False, indent=1))
    if 'rede' in opt or 'ler' in opt:
        r = ler(mur, opt['rodadas'], opt['saida'])
        with open(os.path.join(opt['saida'], 'LISTA-MESTRA.json'), 'w', encoding='utf-8', newline='\n') as h:
            json.dump(r, h, ensure_ascii=False, indent=1)
        conta = defaultdict(int)
        for p in r:
            conta[(p['ESTADO'], 'ORCID' if isinstance(p['ORCID_PELA_BUSCA'], list) else p['ORCID_PELA_BUSCA'])] += 1
        print(json.dumps({'%s/%s' % k: v for k, v in conta.items()}, ensure_ascii=False, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
