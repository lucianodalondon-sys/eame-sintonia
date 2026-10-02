"""Leva o CRUZAMENTO-COMERCIAL.json de uma remessa a uma COPIA do client, para um ENDERECO DE TESTE.

Nunca escreve no repositorio. Falha fechada: SHA256SUMS da remessa tem de conferir com o ficheiro, senao nada e
gerado. Escreve so `sintonia-cruzamento-publicado.js` na pasta de destino (a copia que vai ser implantada).

    python gerar_cruzamento_publicado.py <pasta cruzamento-comercial> <client da copia>
"""
import hashlib, json, os, sys, datetime


def main(pasta, destino):
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
        'REMESSA': os.path.basename(os.path.dirname(os.path.abspath(pasta))),
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
