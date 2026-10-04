"""Leva o CRUZAMENTO-COMERCIAL.json de uma remessa a uma COPIA do client, para um ENDERECO DE TESTE.

Nunca escreve no repositorio. Falha fechada: SHA256SUMS da remessa tem de conferir com o ficheiro, senao nada e
gerado. Escreve so `sintonia-cruzamento-publicado.js` na pasta de destino (a copia que vai ser implantada).

    python gerar_cruzamento_publicado.py <pasta cruzamento-comercial> <client da copia>
    python gerar_cruzamento_publicado.py <FAST-AUTO>/INTELLIGENCE-CURRENT.json <client da copia>   (estado vivo)
"""
import hashlib, json, os, sys, datetime


VIVO_NOME = 'INTELLIGENCE-CURRENT.json'


def _sums(path):
    sums = {}
    for linha in open(path, encoding='utf-8'):
        p = linha.split()
        if len(p) >= 2:
            sums[p[-1].lstrip('*')] = p[0]
    return sums


def envelope_do_vivo(arq):
    """ESTADO VIVO ACUMULADO da Intelligence (FAST-AUTO/INTELLIGENCE-CURRENT.json) -> envelope que o leitor do casco
    ja desenha. O casco NAO acumula, NAO decide destino, NAO tira nem poe itens: so confere e reembala.
    Falha fechada (devolve (None, motivo)): .sha256 ao lado nao confere, TIPO errado, ID das gavetas sem objeto,
    DESTINO_FERRAMENTA do objeto diferente das gavetas onde a Intelligence o pos, NAO_PUBLICAR em qualquer objeto."""
    raw = open(arq, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    s = arq + '.sha256'
    if not os.path.isfile(s) or _sums(s).get(os.path.basename(arq)) != sha:
        return None, 'sha256 do estado vivo nao confere'
    v = json.loads(raw.decode('utf-8'))
    if v.get('TIPO') != 'INTELLIGENCE-CURRENT':
        return None, 'TIPO nao e INTELLIGENCE-CURRENT'
    objs = {o.get('ID'): o for o in (v.get('OBJETOS') or [])}
    fora = {(x.get('ID') if isinstance(x, dict) else x) for x in (v.get('FORA_DA_SUPERFICIE') or [])}
    gav = {}
    for g, ids in (v.get('DESTINOS') or {}).items():
        if g == 'NAO_PUBLICAR':
            continue  # nunca vai ao cliente
        for i in ids or []:
            if i not in objs:
                return None, 'gaveta ' + g + ' cita ' + str(i) + ' sem objeto'
            gav.setdefault(i, set()).add(g)
    sel = []
    for i, gs in gav.items():
        o = objs[i]
        if i in fora or (o.get('VIVO') or {}).get('SITUACAO', 'ATIVO') != 'ATIVO':
            continue
        d = o.get('DESTINO_FERRAMENTA') or []
        if 'NAO_PUBLICAR' in d:
            return None, i + ': NAO_PUBLICAR numa gaveta publicavel'
        if set(d) != gs:
            return None, i + ': DESTINO_FERRAMENTA ' + str(sorted(d)) + ' != gavetas ' + str(sorted(gs))
        sel.append(o)
    ordem = [o.get('ID') for o in (v.get('OBJETOS') or [])]
    sel.sort(key=lambda o: ordem.index(o.get('ID')))
    cont = {k: 0 for k in ('SINAL', 'LEAD', 'GAP', 'OPORTUNIDADE')}
    for o in sel:
        if o.get('CLASSE') in cont:
            cont[o['CLASSE']] += 1
    c = {'ESTADO': v.get('ESTADO'), 'VERSAO': v.get('VERSAO'), 'FONTE': 'INTELLIGENCE-CURRENT',
         'GERADO_EM': v.get('ATUALIZADO_EM'), 'ULTIMA_RODADA_APLICADA': v.get('ULTIMA_RODADA_APLICADA'),
         'RODADAS_APLICADAS': [r.get('RUN_ID') for r in (v.get('RODADAS_APLICADAS') or [])],
         'DESTINOS': {g: [i for i in ids if i in {o['ID'] for o in sel}] for g, ids in (v.get('DESTINOS') or {}).items()
                      if g != 'NAO_PUBLICAR'},
         'CONTAGEM': cont, 'OBJETOS': sel}
    env = {'CRUZAMENTO_SHA256': sha, 'FONTE': 'INTELLIGENCE-CURRENT',
           'REMESSA': 'ESTADO-VIVO ate ' + str(v.get('ULTIMA_RODADA_APLICADA')),
           'PUBLICADO_EM': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           'CRUZAMENTO': c}
    return env, None


def main(pasta, destino):
    if os.path.abspath(destino).replace('\\', '/').lower().startswith('c:/g/'):
        print('RECUSADO: destino e uma worktree; so copia de implantacao')
        return 3
    if os.path.basename(pasta) == VIVO_NOME:
        env, motivo = envelope_do_vivo(pasta)
        if not env:
            print('RECUSADO:', motivo)
            return 2
        corpo = ('/* GERADO por italia-portale/audit/casco/gerar_cruzamento_publicado.py a partir do ESTADO VIVO '
                 'ACUMULADO (INTELLIGENCE-CURRENT.json), nao da ultima rodada. */\n'
                 'window.SINTONIA_CRUZAMENTO_PUBLICADO = ' + json.dumps(env, ensure_ascii=False) + ';\n')
        open(os.path.join(destino, 'sintonia-cruzamento-publicado.js'), 'w', encoding='utf-8', newline='\n').write(corpo)
        print('OK', env['CRUZAMENTO_SHA256'], 'VIVO', env['REMESSA'], 'CONTAGEM', json.dumps(env['CRUZAMENTO']['CONTAGEM']),
              'GAVETAS', json.dumps({g: len(i) for g, i in env['CRUZAMENTO']['DESTINOS'].items() if i}))
        return 0
    f = os.path.join(pasta, 'CRUZAMENTO-COMERCIAL.json')
    raw = open(f, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    sums = {}
    for linha in open(os.path.join(pasta, 'SHA256SUMS.txt'), encoding='utf-8'):
        p = linha.split()
        if len(p) >= 2:
            sums[p[-1].lstrip('*')] = p[0]
    if sums.get('CRUZAMENTO-COMERCIAL.json') != sha:
        print('RECUSADO: SHA256SUMS nao confere', sums.get('CRUZAMENTO-COMERCIAL.json'), sha)
        return 2
    c = json.loads(raw.decode('utf-8'))
    destino_js = os.path.join(destino, 'sintonia-cruzamento-publicado.js')
    if os.path.abspath(destino).replace('\\', '/').lower().startswith('c:/g/'):
        print('RECUSADO: destino e uma worktree; so copia de implantacao')
        return 3
    env = {
        'CRUZAMENTO_SHA256': sha,
        # rodada FAST-AUTO: a pasta E a rodada (<FAST-AUTO>/<RUN_ID>); remessa antiga: <remessa>/cruzamento-comercial
        'REMESSA': (os.path.basename(os.path.abspath(pasta)) if os.path.basename(os.path.abspath(pasta)).startswith('FAST-')
                    else os.path.basename(os.path.dirname(os.path.abspath(pasta)))),
        'PUBLICADO_EM': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'CRUZAMENTO': c,
    }
    corpo = ('/* GERADO por italia-portale/audit/casco/gerar_cruzamento_publicado.py — SO na copia de teste. */\n'
             'window.SINTONIA_CRUZAMENTO_PUBLICADO = ' + json.dumps(env, ensure_ascii=False) + ';\n')
    open(destino_js, 'w', encoding='utf-8', newline='\n').write(corpo)
    print('OK', sha, 'CONTAGEM', json.dumps(c.get('CONTAGEM')), '->', destino_js)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
