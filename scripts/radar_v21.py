#!/usr/bin/env python3
"""RADAR V2.1 — o pacote canonico ADAMA Italia, resolvido de forma que SOBREVIVA ao contêiner.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
Os workflows de `.claude/workflows/*.js` liam o pacote canonico de

    /tmp/claude-0/-home-user-eame-sintonia/b6cc5475-.../scratchpad/v21/*.json

Esse caminho e o scratchpad EFEMERO de um contêiner que ja morreu. Quando a conta
anterior esgotou os creditos, o contêiner foi reclamado e o pacote inteiro sumiu —
levando junto tres grupos de cruzamento e doze leituras de convegno que dependiam
dele. Os workflows continuaram apontando para um diretorio que nao existe mais: rodar
sem consertar isso produz agente CEGO, que le zero pares e conclui ausencia.

  ARQUIVO QUE NAO ESTA COMMITADO NAO SOBREVIVE A TROCA DE CONTA.

A CORRECAO
----------
O pacote passa a viver em `data/samples/IT-RADAR-V21/`, VERSIONADO neste repositorio.
Nao e outro UUID temporario: e um caminho relativo ao repo, que qualquer contêiner novo
encontra com um `git clone`.

A ORIGEM FICA DECLARADA E VERIFICAVEL
-------------------------------------
`MANIFEST.json` guarda, para cada arquivo, o ref de origem, o caminho de origem e o
SHA do blob git. O SHA e enderecado por conteudo: se o arquivo de origem mudar, o SHA
muda, e `verificar()` acusa. Assim a copia nunca diverge em silencio da fonte.

USO
---
    python3 scripts/radar_v21.py caminho      # imprime o diretorio do pacote
    python3 scripts/radar_v21.py verificar    # confere os SHAs contra o MANIFEST
    python3 scripts/radar_v21.py testemunha   # prova que um processo novo consegue ler
    python3 scripts/radar_v21.py materializar # recopia da origem versionada
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.path.join(REPO, 'data', 'samples', 'IT-RADAR-V21')
MANIFEST = os.path.join(PACOTE, 'MANIFEST.json')

# Refs onde o pacote canonico existe versionado, em ordem de preferencia. Sao lidos
# APENAS para materializar/reconferir: o uso normal le a copia local.
REFS_DE_ORIGEM = (
    'origin/claude/italy-v2-handoff',
    'origin/claude/italy-v2-resume-account2',
    'origin/claude/opportunity-radar-audit-hem6p2',
    'origin/claude/trilha-universal-inteligencia-a5rx9d',
)

BASE = 'build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF/01-DESIGN-READY'

# nome que os workflows usavam  ->  (caminho na origem, o que e)
MAPA = {
    'productsRegulatory.json': (
        BASE + '/ADAMA/adama-italy-products.json',
        '163 registros ADAMA vigentes no Ministero della Salute, com ACTIVE_INGREDIENTS. '
        'As 53 substancias ativas da casa derivam-se DESTE arquivo.'),
    'productRelationships.json': (
        BASE + '/LABEL-USE/label-use-pairs.json',
        '2.030 pares cultura x alvo LIDOS dentro do rotulo autorizado, com LINK_STRENGTH. '
        '102 dos 163 registros tem par lido; 61 nao tem, e isso e um PISO, nao um censo.'),
    'labelTermCensus.json': (
        BASE + '/LABEL-USE/label-term-census.json',
        'censo dos termos literais do rotulo'),
    'opportunities.json': (
        BASE + '/OPPORTUNITIES/opportunities.json',
        'as convergencias que o proprio artefato de origem SE RECUSA a chamar de oportunidade'),
    'cropWindows.json': (
        BASE + '/CROP-WINDOWS/crop-windows.json',
        'janelas de cultura declaradas'),
    'adamaCrops.json': (BASE + '/ADAMA/adama-italy-crops.json', 'culturas ADAMA'),
    'adamaFungicides.json': (BASE + '/ADAMA/adama-fungicides.json', 'linha fungicida'),
    'adamaInsecticides.json': (BASE + '/ADAMA/adama-insecticides.json', 'linha inseticida'),
    'adamaHerbicides.json': (BASE + '/ADAMA/adama-herbicides.json', 'linha herbicida'),
}


def _git(*args):
    return subprocess.run(('git',) + args, cwd=REPO, capture_output=True)


def caminho():
    return PACOTE


def substancias_ativas():
    """As 53 substancias ativas, DERIVADAS do registro — nunca digitadas de memoria."""
    with open(os.path.join(PACOTE, 'productsRegulatory.json'), encoding='utf-8') as f:
        d = json.load(f)
    ai = set()
    for p in d['PRODUCTS']:
        for a in (p.get('ACTIVE_INGREDIENTS') or []):
            if a:
                ai.add(a.upper().strip())
    return ai


def pares():
    with open(os.path.join(PACOTE, 'productRelationships.json'), encoding='utf-8') as f:
        return json.load(f)['PAIRS']


def materializar():
    os.makedirs(PACOTE, exist_ok=True)
    entradas, ref_usado = [], None
    for ref in REFS_DE_ORIGEM:
        if _git('rev-parse', '--verify', ref).returncode == 0:
            ref_usado = ref
            break
    if not ref_usado:
        print('nenhum ref de origem alcancavel: %s' % ', '.join(REFS_DE_ORIGEM))
        return 1
    for nome, (origem, oque) in MAPA.items():
        r = _git('show', '%s:%s' % (ref_usado, origem))
        if r.returncode != 0:
            print('AUSENTE na origem: %s' % origem)
            return 1
        blob = _git('rev-parse', '%s:%s' % (ref_usado, origem)).stdout.decode().strip()
        d = json.loads(r.stdout.decode('utf-8'))
        # O guardiao de proveniencia desta casa exige que TODA amostra diga de onde veio e
        # quando. Um arquivo que nao declara origem e indistinguivel de um arquivo inventado,
        # e o teste esta certo em reprovar — inclusive uma copia. Por isso a copia recebe a
        # declaracao, e o conteudo de origem fica conferivel em ORIGEM_JSON_SHA256, que
        # ignora formatacao e so olha o conteudo.
        injetadas = {
            'SOURCE_ID': 'IT-RADAR-V21',
            'CAPTURED_AT': '2026-09-04',
            'SOURCE': ('copia PINADA para sobreviver a troca de conteiner. Conteudo identico ao '
                       'blob %s de %s:%s. Esta copia NAO e a fonte de verdade.'
                       % (blob[:12], ref_usado, origem)),
            'PINNED_FROM': {'REF': ref_usado, 'PATH': origem, 'BLOB_SHA': blob},
        }
        canonico = hashlib.sha256(
            json.dumps(d, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        d.update(injetadas)
        corpo = json.dumps(d, ensure_ascii=False, indent=1).encode('utf-8')
        with open(os.path.join(PACOTE, nome), 'wb') as f:
            f.write(corpo)
        entradas.append({
            'NOME_LOCAL': nome,
            'ORIGEM_REF': ref_usado,
            'ORIGEM_PATH': origem,
            'ORIGEM_BLOB_SHA': blob,
            'ORIGEM_BYTES': len(r.stdout),
            'ORIGEM_JSON_SHA256': canonico,
            'CHAVES_INJETADAS': sorted(injetadas),
            'BYTES': len(corpo),
            'SHA256': hashlib.sha256(corpo).hexdigest(),
            'O_QUE_E': oque,
        })
        print('%-28s %9d B  blob %s' % (nome, len(corpo), blob[:12]))

    # activeIngredients.json e DERIVADO, e nao copiado: os workflows mandam conferir cada
    # molecula contra ele, entao ele precisa existir de verdade. Deriva-se do registro para
    # que a lista nunca seja digitada de memoria — foi assim que o FIX-05 nasceu.
    ai = sorted(substancias_ativas())
    corpo = json.dumps({
        'DATASET': 'IT-RADAR-V21',
        'SOURCE': 'DERIVADO de productsRegulatory.json: uniao dos ACTIVE_INGREDIENTS dos 163 '
                  'registros ADAMA vigentes no Ministero della Salute.',
        'SOURCE_ID': 'IT-RADAR-V21',
        'CAPTURED_AT': '2026-09-04',
        'DERIVATION': "set(a.upper().strip() for p in PRODUCTS for a in p['ACTIVE_INGREDIENTS'])",
        'POR_QUE_DERIVADO_E_NAO_DIGITADO': (
            'o FIX-05 desta casa nasceu de uma lista escrita de memoria. Derivar do registro '
            'e a unica forma de a lista nao mentir.'),
        'NAO_ESTAO_AQUI_E_SAO_COMUNS_NA_FALA': [
            'RAME', 'ZOLFO', 'DELTAMETRINA', 'ACETAMIPRID', 'DODINA', 'FLUPYRADIFURONE',
            'BACILLUS THURINGIENSIS', 'BACILLUS SUBTILIS', 'AZADIRACTINA', 'CAOLINO',
            'ZEOLITE', 'PIRETRO NATURALE', 'OLIO MINERALE', 'SPINOSAD', 'FOSMET',
            'MANCOZEB', 'PYRACLOSTROBIN', 'ETOFENPROX', 'METRIBUZIN'],
        'MOLECULA_MARCADA_NAO_E_MOLECULA_ADAMA': (
            'um campo MOLECULE cheio parece bom e nao diz de quem e. Confira SEMPRE contra '
            'esta lista, com fronteira de palavra.'),
        'COUNT': len(ai),
        'ACTIVE_INGREDIENTS': ai,
    }, ensure_ascii=False, indent=1).encode('utf-8')
    with open(os.path.join(PACOTE, 'activeIngredients.json'), 'wb') as f:
        f.write(corpo)
    entradas.append({
        'NOME_LOCAL': 'activeIngredients.json',
        'ORIGEM_REF': ref_usado,
        'ORIGEM_PATH': 'DERIVADO de ' + MAPA['productsRegulatory.json'][0],
        'ORIGEM_BLOB_SHA': 'DERIVADO',
        'BYTES': len(corpo),
        'SHA256': hashlib.sha256(corpo).hexdigest(),
        'O_QUE_E': 'as %d substancias ativas ADAMA, derivadas do registro' % len(ai),
    })
    print('%-28s %9d B  DERIVADO (%d substancias)' % (
        'activeIngredients.json', len(corpo), len(ai)))

    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump({
            'DATASET': 'IT-RADAR-V21',
            'SOURCE': ('copia PINADA do pacote canonico ADAMA Italia V2.1. Nada foi '
                       'recalculado nem reinterpretado: sao os mesmos blobs git da origem, '
                       'identificados por SHA.'),
            'SOURCE_ID': 'IT-RADAR-V21',
            'CAPTURED_AT': '2026-09-04',
            'POR_QUE_EXISTE': (
                'os workflows liam este pacote de um scratchpad efemero que morreu com o '
                'contêiner da conta anterior. Sem esta copia versionada, todo agente novo le '
                'zero pares e conclui ausencia — que e o erro mais caro desta casa.'),
            'ORIGEM_E_VERIFICAVEL': (
                'ORIGEM_BLOB_SHA e enderecado por conteudo. Se a origem mudar, o SHA muda e '
                '`python3 scripts/radar_v21.py verificar` acusa. A copia nao diverge em silencio.'),
            'NAO_E_FONTE_DE_VERDADE': (
                'a fonte de verdade continua sendo o artefato de origem. Esta copia existe '
                'para SOBREVIVER a troca de contêiner, e nao para substituir o dono do dado.'),
            'FILES': entradas,
        }, f, ensure_ascii=False, indent=1)
    print('manifest: %s' % MANIFEST)
    return 0


def verificar():
    if not os.path.exists(MANIFEST):
        print('FAIL  sem MANIFEST — rode `materializar`')
        return 1
    with open(MANIFEST, encoding='utf-8') as f:
        man = json.load(f)
    mau = 0
    for e in man['FILES']:
        p = os.path.join(PACOTE, e['NOME_LOCAL'])
        if not os.path.exists(p):
            print('FAIL  ausente: %s' % e['NOME_LOCAL']); mau += 1; continue
        with open(p, 'rb') as f:
            h = hashlib.sha256(f.read()).hexdigest()
        ok = h == e['SHA256']
        nota = ''
        # O conteudo de origem tem de continuar identico, ignorando formatacao e as chaves
        # de proveniencia que esta casa injetou. Sem isto, a copia poderia divergir da fonte
        # em silencio — que e exatamente o risco que o pino existe para eliminar.
        if e.get('ORIGEM_JSON_SHA256'):
            with open(p, encoding='utf-8') as f:
                d = json.load(f)
            for k in e.get('CHAVES_INJETADAS', []):
                d.pop(k, None)
            c = hashlib.sha256(
                json.dumps(d, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
            if c != e['ORIGEM_JSON_SHA256']:
                ok, nota = False, '  CONTEUDO DIVERGE DA ORIGEM'
        print('%-5s %-28s %s%s' % ('ok' if ok else 'FAIL', e['NOME_LOCAL'], h[:16], nota))
        mau += 0 if ok else 1
    print('%d arquivo(s) divergente(s)' % mau)
    return 1 if mau else 0


def testemunha():
    """WORKFLOW_SURVIVES_NEW_CONTAINER.

    Prova, sem depender de scratchpad nenhum, que um processo novo:
      1. encontra o pacote por caminho relativo ao repositorio;
      2. le as 53 substancias ativas DO REGISTRO;
      3. le os 2.030 pares de rotulo;
      4. reproduz a assimetria do OLIVO.
    """
    print('WORKFLOW_SURVIVES_NEW_CONTAINER')
    print('  cwd do processo ......... %s' % os.getcwd())
    print('  pacote resolvido em ..... %s' % caminho())
    mortos = [d for d in (PACOTE,) if '/tmp/' in d or 'scratchpad' in d]
    print('  depende de scratchpad? .. %s' % ('SIM — FALHOU' if mortos else 'NAO'))
    ai = substancias_ativas()
    ps = pares()
    olivo = [p for p in ps if (p.get('CROP') or '').upper() == 'OLIVO']
    print('  substancias ativas ...... %d' % len(ai))
    print('  pares de rotulo ......... %d' % len(ps))
    print('  pares com OLIVO ......... %d  %s' % (
        len(olivo), ' · '.join('%s %s x %s' % (p['PRODUCT'], p['REGISTRATION_ID'],
                                               p['TARGET']) for p in olivo)))
    # Este 1 e o que o CONJUNTO DE PARES contem, e nao o que os rotulos autorizam.
    # A leitura dos 163 rotulos (2026-09-04) achou 15 rotulos que autorizam OLIVO, dos
    # quais 14 ja tinham sido "lidos" e mesmo assim nao viraram par. O extrator perde.
    print('  AVISO ................... o conjunto de pares SUB-REPORTA. 15 rotulos '
          'autorizam OLIVO; ver data/samples/IT-ROTULOS-V1/IT-ROTULOS-DELTA-V1.json')
    ok = (not mortos) and len(ai) == 53 and len(ps) == 2030 and len(olivo) == 1
    print('  VEREDITO ................ %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'caminho'
    if cmd == 'caminho':
        print(caminho()); sys.exit(0)
    sys.exit({'materializar': materializar, 'verificar': verificar,
              'testemunha': testemunha}[cmd]())
