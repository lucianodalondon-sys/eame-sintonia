#!/usr/bin/env python3
"""
recoletar.py — rebaixa a fonte primaria e CONFERE cada arquivo pelo sha256.

Os 60 instantaneos e os 163 rotulos nao sao versionados (decisao D-003 da casa).
Este script os traz de volta a partir do MANIFESTO-FONTE.json e so aceita byte
identico: arquivo que nao bater com o sha gravado NAO e aceito, e o script diz
qual. Um download parcial ou uma republicacao silenciosa da fonte aparecem aqui
em vez de contaminarem uma medicao depois.

  python3 v1/fonte/recoletar.py .                  # baixa o que falta e confere
  python3 v1/fonte/recoletar.py . --so-conferir    # nao baixa nada, so confere

Testado: o instantaneo de 2026-01-12, com 14 meses, voltou byte identico
(sha256 2956bc02a5ac9f...). A serie historica continua servida por data.

## DOIS HOSTS, DOIS CLIENTES

Os dois hosts do Ministero recusam clientes diferentes, e nao ha um so cliente
que baixe os 223 arquivos:

  * `www.dati.salute.gov.it` (os 60 CSV) responde a `curl` e devolve
    `SSLV3_ALERT_HANDSHAKE_FAILURE` ao `urllib` — o servidor recusa o
    ClientHello do Python, com ou sem cadeia extra.
  * `www.fitosanitari.salute.gov.it` (as 163 etichettas) responde ao `urllib`
    e o `curl` recusa a RESPOSTA dele: o servidor manda um `Public-Key-Pins`
    dobrado em duas linhas e o curl 8 aborta com `Header without colon`.

Por isso cada arquivo e tentado nos dois clientes, nessa ordem, e so e
declarado ERRO quando os DOIS falham. Um cliente que falha nao e fonte
indisponivel — `PARSER_FAILURE != REGULATORY_ABSENCE` vale tambem para o
cliente HTTP.

## A CADEIA TLS DO MINISTERO

`www.fitosanitari.salute.gov.it` manda so a folha e omite a intermediaria
"TI Trust Technologies OV CA". Sem o elo, `urllib` recusa a conexao com
`unable to get local issuer certificate` e as 163 etichettas viram ERRO —
que **nao e ausencia regulatoria nenhuma**, e sim um elo faltando.

O conserto e o mesmo de `pilot-label-intelligence/bin/chain.sh`: a
intermediaria versionada em `recon/ti-trust-intermediate.pem` mais o bundle
do sistema. **Nunca desligar a verificacao.** Se a cadeia falhar, o script
para e diz que falhou; nao ha modo inseguro.
"""
import json, hashlib, os, ssl, subprocess, sys, urllib.request

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '.'
SO_CONFERIR = '--so-conferir' in sys.argv
AQUI = os.path.dirname(os.path.abspath(__file__))
MAN = json.load(open(os.path.join(AQUI, 'MANIFESTO-FONTE.json'), encoding='utf-8'))
DEST = {'SNAPSHOTS': 'pilot-label-intelligence/registry/snapshots',
        'ROTULOS':   'pilot-label-intelligence/labels/pdf'}


def cadeia():
    """Monta a cadeia TLS completa e devolve o caminho. Sem ela, os PDFs falham."""
    chain = os.path.join(RAIZ, 'pilot-label-intelligence/bin/chain.sh')
    if not os.path.exists(chain):
        return None
    try:
        return subprocess.run(['sh', chain], check=True, capture_output=True,
                              text=True, timeout=60).stdout.strip() or None
    except Exception as e:
        print(f'  cadeia TLS nao montada: {e}', file=sys.stderr)
        return None


def abridor(ca):
    ctx = ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))


def baixar(url, destino, op, ca):
    """Tenta curl e depois urllib. So e falha quando os DOIS recusam."""
    erros = []
    try:
        cmd = ['curl', '-sS', '--fail', '--max-time', '300', '-o', destino, url]
        if ca:
            cmd[1:1] = ['--cacert', ca]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
        if r.returncode == 0 and os.path.getsize(destino) > 0:
            return None
        erros.append(f'curl: {(r.stderr or "").strip()[:80] or "rc=" + str(r.returncode)}')
    except Exception as e:
        erros.append(f'curl: {e}')
    if os.path.exists(destino):
        os.remove(destino)
    try:
        dados = op.open(url, timeout=300).read()
        if not dados:
            raise OSError('corpo vazio')
        with open(destino, 'wb') as fh:
            fh.write(dados)
        return None
    except Exception as e:
        erros.append(f'urllib: {e}')
    if os.path.exists(destino):
        os.remove(destino)
    return ' | '.join(erros)


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ca = cadeia()
    op = abridor(ca)
    ok = baixados = ruins = faltando = 0
    for grupo, dest in DEST.items():
        d = os.path.join(RAIZ, dest)
        os.makedirs(d, exist_ok=True)
        print(f'\n{grupo}: {MAN[grupo]["n"]} arquivo(s), '
              f'{MAN[grupo]["bytes"]/1e6:.0f} MB  -> {dest}')
        for it in MAN[grupo]['itens']:
            p = os.path.join(d, it['file'])
            if not os.path.exists(p):
                if SO_CONFERIR:
                    print(f'  FALTA     {it["file"]}')
                    faltando += 1
                    continue
                erro = baixar(it['url'], p, op, ca)
                if erro:
                    print(f'  ERRO      {it["file"]}: {erro}')
                    faltando += 1
                    continue
                baixados += 1
            s = sha256(p)
            if s == it['sha256']:
                ok += 1
            else:
                ruins += 1
                print(f'  SHA NAO BATE  {it["file"]}\n'
                      f'    esperado {it["sha256"]}\n    achado   {s}')

    print(f'\n  {ok} conferido(s) · {baixados} baixado(s) · '
          f'{ruins} com sha errado · {faltando} ausente(s)')
    if ruins or faltando:
        print('\n  A FONTE NAO ESTA INTEGRA. Nao rode portao nem red team contra ela:')
        print('  qualquer veredito seria sobre um acervo diferente do que foi julgado.')
        return 1
    print('  fonte primaria integra — igual, byte a byte, a que produziu os vereditos')
    return 0


if __name__ == '__main__':
    sys.exit(main())
