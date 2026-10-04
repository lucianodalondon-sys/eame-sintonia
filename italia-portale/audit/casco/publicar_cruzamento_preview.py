"""Publica SOZINHO o cruzamento comercial mais novo no ENDERECO DE TESTE. Nunca em Production.

Uma passagem idempotente (a tarefa agendada SINTONIA-CASCO-CRUZAMENTO chama de 10 em 10 min):
  0. (04/10, ordem do dono) FONTE = ESTADO VIVO ACUMULADO <FAST-AUTO>/INTELLIGENCE-CURRENT.json (escolher_vivo);
     a ultima rodada fica so para auditoria/historico. O texto do passo 1 abaixo e o comportamento ANTIGO.
  1. (antigo) segue a rodada AUTOMATICA da Intelligence: <FAST-AUTO>/ULTIMA.txt (uma linha RUN_ID=<id>, gravada por ultimo)
     -> <FAST-AUTO>/<id>/CRUZAMENTO-COMERCIAL.json, conferido pelo SHA256SUMS.txt DESSA rodada. Ponteiro fora do
     formato, id com / \\ .., sha que nao bate ou ficheiro em falta = nao faz nada (falha fechada). A pasta
     sintonia-fluxo-unico/remessa-* deixou de ser fonte (fica como historico);
  2. se o sha do cruzamento E o commit do casco sao os mesmos da ultima publicacao, sai sem fazer nada;
  3. monta uma copia do client a partir do COMMIT (git archive, nunca a pasta de trabalho), escreve o envelope com
     gerar_cruzamento_publicado.py, `vercel deploy` (preview, sem --prod) e `vercel alias set` para o nome fixo;
  4. prova por curl que o alias serve o sha novo; so entao grava ULTIMO.json.
Bandeira <estado>/PARAR = nao publica.
"""
import argparse, datetime, glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ALIAS = 'sintonia-cruzamento-teste.vercel.app'
ESCOPO = 'london-creative'
PROJETO = 'sintonia-eame-preview'


def log(estado, linha):
    with open(os.path.join(estado, 'PUBLICACOES.log'), 'a', encoding='utf-8') as fh:
        fh.write(datetime.datetime.now().isoformat(timespec='seconds') + ' ' + linha + '\n')
    print(linha)


def sha_de(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def confere(pasta):
    j = os.path.join(pasta, 'CRUZAMENTO-COMERCIAL.json')
    s = os.path.join(pasta, 'SHA256SUMS.txt')
    if not (os.path.isfile(j) and os.path.isfile(s)):
        return None
    sums = {}
    for linha in open(s, encoding='utf-8'):
        p = linha.split()
        if len(p) >= 2:
            sums[p[-1].lstrip('*')] = p[0]
    h = sha_de(j)
    return h if sums.get('CRUZAMENTO-COMERCIAL.json') == h else None


FAST_AUTO_PADRAO = r'C:/Users/London1/sintonia-sala-italia/intelligence-experimental/FAST-AUTO'


def escolher(raiz):
    """ULTIMA.txt -> {RUN_ID, PASTA, SHA}; None se qualquer coisa nao confere."""
    try:
        linhas = [x.strip() for x in open(os.path.join(raiz, 'ULTIMA.txt'), encoding='utf-8') if x.strip()]
    except OSError:
        return None
    if len(linhas) != 1:
        return None
    m = re.fullmatch(r'RUN_ID=(FAST-[0-9A-Za-z_-]+)', linhas[0])
    if not m:
        return None
    run = m.group(1)
    pasta = os.path.join(raiz, run)
    h = confere(pasta)
    if not h:
        return None
    return {'RUN_ID': run, 'PASTA': pasta, 'SHA': h}


def escolher_vivo(raiz):
    """FONTE DO CASCO = ESTADO VIVO ACUMULADO (<FAST-AUTO>/INTELLIGENCE-CURRENT.json + .sha256), nunca a ultima
    rodada isolada. None se o arquivo ou o sha nao conferem (a tela fica no que ja estava no ar). Sem recuo para
    ULTIMA.txt: recuar traria de volta o defeito de uma rodada vazia zerar as ferramentas."""
    arq = os.path.join(raiz, 'INTELLIGENCE-CURRENT.json')
    s = arq + '.sha256'
    if not (os.path.isfile(arq) and os.path.isfile(s)):
        return None
    h = sha_de(arq)
    linhas = [x.split() for x in open(s, encoding='utf-8') if x.strip()]
    if not any(len(p) >= 2 and p[0] == h and p[-1].lstrip('*') == 'INTELLIGENCE-CURRENT.json' for p in linhas):
        return None
    try:
        run = json.load(open(arq, encoding='utf-8')).get('ULTIMA_RODADA_APLICADA') or '?'
    except ValueError:
        return None
    return {'RUN_ID': 'VIVO@' + run, 'PASTA': arq, 'SHA': h}


def vercel(args, cwd):
    exe = shutil.which('vercel') or shutil.which('vercel.cmd')
    assert '--prod' not in args and 'promote' not in args and 'rollback' not in args, 'proibido: production'
    return subprocess.run([exe] + args + ['--scope', ESCOPO], cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=900)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fast-auto', default=FAST_AUTO_PADRAO)
    ap.add_argument('--repo', default=r'C:/g/casco-cruz')
    ap.add_argument('--ref', default='claude/casco-cruzamento-v1')
    ap.add_argument('--estado', default=os.path.expanduser('~/sintonia-casco-preview/cruzamento'))
    ap.add_argument('--forcar', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.estado, exist_ok=True)
    if os.path.exists(os.path.join(a.estado, 'PARAR')):
        log(a.estado, 'PARADO bandeira PARAR')
        return 0
    esc = escolher_vivo(a.fast_auto)
    if not esc:
        log(a.estado, 'NADA INTELLIGENCE-CURRENT.json ausente ou .sha256 nao confere em ' + a.fast_auto)
        return 0
    pasta, h, run = esc['PASTA'], esc['SHA'], esc['RUN_ID']
    commit = subprocess.run(['git', '-C', a.repo, 'rev-parse', a.ref], capture_output=True, text=True).stdout.strip()
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        log(a.estado, 'ERRO ref do casco ilegivel ' + a.ref)
        return 2
    ult = {}
    up = os.path.join(a.estado, 'ULTIMO.json')
    if os.path.exists(up):
        ult = json.load(open(up, encoding='utf-8'))
    if not a.forcar and ult.get('CRUZAMENTO_SHA256') == h and ult.get('COMMIT') == commit:
        log(a.estado, 'IGUAL ' + h[:12] + ' RUN_ID=' + run + ' ' + commit[:9] + ' ja no ar em ' + ult.get('URL', '?'))
        return 0
    tmp = tempfile.mkdtemp(prefix='cruz-pub-')
    try:
        arq = subprocess.run(['git', '-C', a.repo, 'archive', '--format=tar', commit, 'italia-portale/client', 'vercel.json'],
                             capture_output=True)
        if arq.returncode:
            log(a.estado, 'ERRO git archive')
            return 2
        subprocess.run(['tar', '-xf', '-', '-C', tmp], input=arq.stdout, check=True)
        open(os.path.join(tmp, 'package.json'), 'w').write('{"name":"cruz-teste","private":true,"scripts":{"build":"echo sem build"}}\n')
        cli = os.path.join(tmp, 'italia-portale', 'client')
        g = subprocess.run([sys.executable, os.path.join(AQUI, 'gerar_cruzamento_publicado.py'), pasta, cli],
                           capture_output=True, text=True)
        if g.returncode:
            log(a.estado, 'RECUSADO gerador: ' + (g.stdout + g.stderr).strip()[-300:])
            return 2
        r = vercel(['link', '--yes', '--project', PROJETO], tmp)
        if r.returncode:
            log(a.estado, 'ERRO vercel link ' + r.stderr[-300:])
            return 2
        r = vercel(['deploy', '--yes'], tmp)
        m = re.findall(r'https://sintonia-eame-preview-[a-z0-9]+-london-creative\.vercel\.app', r.stdout + r.stderr)
        if r.returncode or not m:
            log(a.estado, 'ERRO vercel deploy ' + (r.stdout + r.stderr)[-300:])
            return 2
        url = m[0]
        r = vercel(['alias', 'set', url, ALIAS], tmp)
        if r.returncode:
            log(a.estado, 'ERRO alias ' + (r.stdout + r.stderr)[-300:])
            return 2
        prova = ''
        for _ in range(6):
            try:
                corpo = urllib.request.urlopen('https://' + ALIAS + '/sintonia-cruzamento-publicado.js?t=' + str(time.time()), timeout=30).read().decode('utf-8')
                if h in corpo:
                    prova = 'SHA_NO_AR'
                    break
            except Exception:
                pass
            time.sleep(10)
        if not prova:
            log(a.estado, 'ERRO alias nao serve o sha ' + h[:12] + ' DEPLOY=' + url)
            return 2
        novo = {'FONTE': 'INTELLIGENCE-CURRENT', 'CRUZAMENTO_SHA256': h, 'RUN_ID': run, 'PASTA': pasta, 'COMMIT': commit, 'URL': 'https://' + ALIAS + '/portale',
                'DEPLOY': url, 'EM': datetime.datetime.now().isoformat(timespec='seconds')}
        json.dump(novo, open(up, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        log(a.estado, 'PUBLICADO ' + h + ' RUN_ID=' + run + ' commit=' + commit[:9]
            + ' URL=https://' + ALIAS + '/portale DEPLOY=' + url + ' PROVA=' + prova)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
