#!/usr/bin/env python3
"""
DADO PESSOAL DO INSTAGRAM — dono único do que se pode e do que não se pode guardar.

    py scripts/instagram_pessoal.py estado        # o portão está aberto? por quê?
    py scripts/instagram_pessoal.py expurgar      # apaga o acervo de comentário, inteiro

POR QUE COMENTÁRIO É OUTRA COISA
----------------------------------
O post de `@bayer_italia` é comunicação de uma EMPRESA. O comentário embaixo dele é a
frase de uma PESSOA — com nome, foto e link para o perfil dela. São dois materiais com
obrigações diferentes, e um corpus que os mistura trata a pessoa como trata a marca.

    POST CORPORATIVO ≠ COMENTÁRIO DE PESSOA FÍSICA.

Os alvos desta missão estão na Itália, na Espanha e na França. Quem comenta num post de
defensivo agrícola na Itália costuma ser revendedor ou produtor — pessoa física, no
território onde o GDPR vale.

    ESTE ARQUIVO NÃO É PARECER JURÍDICO, E EU NÃO SOU ADVOGADO.
    Ele é a CONTENÇÃO TÉCNICA que segura a coleta até a revisão jurídica da ADAMA dizer
    o que pode. Contenção não é conformidade — é o que impede de criar fato consumado
    enquanto a resposta não vem.

O QUE JÁ ESTÁ DECLARADO NESTA CASA, E QUE ESTE ARQUIVO OBEDECE
----------------------------------------------------------------
`docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md` declara
`PERSONAL_SCORING = PROHIBITED_FOR_CURRENT_PILOT` e
`NAMED_RESEARCHER_PUBLIC_SCREEN = BLOCKED_PENDING_LEGAL_REVIEW`, com origem na
pendência P-008 do diário de decisões. Nada aqui reabre isso; o que este arquivo faz é
tornar a regra EXECUTÁVEL.

AS QUATRO TRAVAS
-----------------
1. **PORTÃO.** `pode_coletar()` devolve NÃO enquanto `IG_COMENTARIOS_AUTORIZADO` não
   estiver ligado à mão por quem tem autoridade para ligar. O padrão é fechado — e um
   padrão que precisa ser lembrado não é uma trava.

2. **PSEUDÔNIMO.** O autor vira `AUTHOR_PSEUDONYM`, um HMAC-SHA256 do handle com um sal
   que vive FORA do repositório. O mesmo autor em dois posts recebe o mesmo pseudônimo —
   dá para dizer "esta pessoa comentou 3 vezes" sem guardar quem ela é. E o sal fora do
   Git é o que impede a lista de handles ser reconstruída por quem clonar o repositório.

3. **O BRUTO NÃO ENTRA NO GIT.** O RAW de comentário vai para
   `data/samples/raw-paid-personal/`, que tem `.gitignore` próprio. O manifesto guarda o
   SHA-256 do arquivo — assim a cadeia de evidência continua fechada sem que o conteúdo
   pessoal seja versionado para sempre.

    APAGAR DO DISCO NÃO APAGA DO GIT. É por isso que a pasta nasce ignorada, e não
    "limpa depois".

4. **EXPURGO ESCRITO ANTES DE PRECISAR.** `expurgar()` existe e é testado hoje, com o
   prazo em `UNDECLARED_PENDING_LEGAL_REVIEW`. Inventar "90 dias" seria precisão falsa —
   ninguém nesta casa tem autoridade para escolher esse número. Mas quando o jurídico
   disser um prazo, ele é executável no mesmo dia, e não vira projeto.
"""
import hashlib
import hmac
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

RAW_PESSOAL = os.path.join(ROOT, 'data', 'samples', 'raw-paid-personal')
ARTEFATO = os.path.join(ROOT, 'data', 'samples', 'INSTAGRAM-COMENTARIOS')
SAL = os.path.join(os.path.expanduser('~'), '.sintonia-browser', 'ig', 'sal-pseudonimo.txt')

AUTORIZADO = 'IG_COMENTARIOS_AUTORIZADO'
RETENCAO = 'UNDECLARED_PENDING_LEGAL_REVIEW'

BASE_LEGAL_ALEGADA = (
    'interesse legítimo em pesquisa de mercado B2B sobre comunicação pública de '
    'concorrente (GDPR art. 6(1)(f)) — ALEGADA, NÃO VALIDADA. Exige LIA escrita, e '
    'quem faz a LIA é o jurídico da ADAMA, não este código.')


def _sal():
    """O sal do pseudônimo. Fica fora do repositório; nasce sozinho se não existir.

    Sal em disco fora do Git, e não em variável de ambiente, porque ele precisa ser o
    MESMO entre execuções: pseudônimo que muda a cada rodada não permite dizer "esta
    pessoa comentou de novo" — e transformaria uma pessoa em N pessoas na contagem.
    """
    if os.path.exists(SAL):
        with open(SAL, 'rb') as f:
            v = f.read().strip()
        if v:
            return v
    os.makedirs(os.path.dirname(SAL), exist_ok=True)
    v = os.urandom(32).hex().encode()
    with open(SAL, 'wb') as f:
        f.write(v)
    try:
        os.chmod(SAL, 0o600)
    except OSError:
        pass
    return v


def pseudonimo(handle):
    """handle → `IGP-<12 hex>`. Estável entre execuções, irreversível sem o sal."""
    if not handle:
        return 'IGP-SEM-AUTOR'
    d = hmac.new(_sal(), str(handle).strip().lower().encode('utf-8'),
                 hashlib.sha256).hexdigest()
    return 'IGP-' + d[:12]


def pode_coletar(env=None):
    """→ (pode, motivo). O padrão é NÃO, e isso é a trava — não um aviso."""
    amb = env if env is not None else os.environ
    v = (amb.get(AUTORIZADO) or '').strip().lower()
    if v in ('1', 'sim', 'yes', 'true'):
        return True, ('autorizado à mão por %s=%s. A autorização é de OPERAÇÃO, e não '
                      'substitui a revisão jurídica: o artefato continua nascendo '
                      'LEGAL_REVIEW=PENDING.' % (AUTORIZADO, v))
    return False, (
        'PORTÃO FECHADO. Comentário é dado pessoal de pessoa física na UE e esta casa já '
        'declarou PERSONAL_SCORING = PROHIBITED_FOR_CURRENT_PILOT (pendência P-008). '
        'Para coletar assim mesmo, quem tem autoridade liga %s=1 — e assume a decisão. '
        'Post corporativo NÃO passa por este portão: ele é comunicação de empresa.'
        % AUTORIZADO)


def normalizar_comentario(bruto, *, objeto, run_id):
    """RAW → o registro que PODE ser guardado. O handle não entra, o pseudônimo entra.

    O TEXTO fica inteiro, e isso é decisão: resumir a frase mata a evidência, e a frase
    é justamente o que a missão foi buscar. O que sai é a IDENTIDADE do autor.
    """
    def g(*nomes):
        for n in nomes:
            v = bruto.get(n)
            if v not in (None, '', [], {}):
                return v
        return 'NOT_KNOWN'

    autor = g('ownerUsername', 'username', 'author', 'authorName', 'owner')
    return {
        'COMMENT_ID': g('id', 'commentId', 'pk'),
        'OBJECT_ID': objeto.get('SHORTCODE') or objeto.get('OBJECT_ID'),
        'ACCOUNT_HANDLE': objeto.get('ACCOUNT_HANDLE'),
        'COMPANY': objeto.get('COMPANY'),
        'COUNTRY_SCOPE': objeto.get('COUNTRY_SCOPE'),
        'PLATFORM': 'INSTAGRAM',
        # A frase, inteira e no idioma original. É a evidência.
        'COMMENT_TEXT_RAW': g('text', 'comment', 'body'),
        # A pessoa, não.
        'AUTHOR_PSEUDONYM': pseudonimo(autor if autor != 'NOT_KNOWN' else None),
        'AUTHOR_HANDLE': 'REDACTED_BY_POLICY',
        'AUTHOR_PROFILE_URL': 'REDACTED_BY_POLICY',
        'AUTHOR_AVATAR_URL': 'REDACTED_BY_POLICY',
        'AUTHOR_ENTITY_KIND': 'UNKNOWN',
        'AUTHOR_IDENTITY_STATE': 'UNVERIFIED',
        'AUTHOR_SCORING': 'PROHIBITED_FOR_CURRENT_PILOT',
        'LIKE_COUNT': g('likesCount', 'likeCount', 'voteCount'),
        'PUBLISHED_AT': g('timestamp', 'createdAt', 'date'),
        'PUBLISHED_AT_RELATIVE': g('publishedTimeText', 'timeAgo'),
        'IS_REPLY': 'YES' if bruto.get('repliesCount') is None and bruto.get('parentId') else 'NO',
        # O lugar do fato não sai do idioma nem da conta que publicou.
        'COUNTRY_OF_FACT': 'NOT_KNOWN',
        'REGION_OF_FACT': 'NOT_KNOWN',
        'SPEECH_TYPE': 'NOT_CLASSIFIED',
        'EVIDENCE_CLASS': 'FIELD_VOICE_OBSERVED',
        'NAO_E': ('FIELD_PROBLEM_CONFIRMED. Voz não é incidência: alguém dizer que tem '
                  'um problema não mede que o problema exista naquele lugar.'),
        'COLLECTION_RUN_ID': run_id,
        'LEGAL_REVIEW': 'PENDING',
        'LEGAL_BASIS_CLAIMED': BASE_LEGAL_ALEGADA,
        'RETENTION_STATE': RETENCAO,
        'PERSONAL_DATA': 'YES',
    }


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for p in iter(lambda: f.read(1 << 20), b''):
            h.update(p)
    return h.hexdigest()


def preparar_pasta():
    """A pasta do bruto pessoal nasce IGNORADA pelo Git. Não é limpeza posterior."""
    os.makedirs(RAW_PESSOAL, exist_ok=True)
    gi = os.path.join(RAW_PESSOAL, '.gitignore')
    if not os.path.exists(gi):
        with open(gi, 'w', encoding='utf-8') as f:
            f.write('# Bruto de COMENTÁRIO — dado pessoal de pessoa física.\n'
                    '# Esta pasta existe para NÃO entrar no Git, e é por isso que ela\n'
                    '# se ignora inteira, incluindo este arquivo.\n'
                    '#\n'
                    '#     APAGAR DO DISCO NÃO APAGA DO GIT.\n'
                    '#\n'
                    '# Quem versionar isto uma vez não desfaz mais: o conteúdo fica na\n'
                    '# história do repositório para sempre, e o expurgo vira reescrita\n'
                    '# de história em vez de um `rm`.\n'
                    '*\n')
    return RAW_PESSOAL


def estado():
    pode, motivo = pode_coletar()
    return {
        'GATE': 'OPEN' if pode else 'CLOSED',
        'WHY': motivo,
        'RETENTION_STATE': RETENCAO,
        'LEGAL_REVIEW': 'PENDING',
        'LEGAL_BASIS_CLAIMED': BASE_LEGAL_ALEGADA,
        'RAW_DIR': os.path.relpath(RAW_PESSOAL, ROOT).replace('\\', '/'),
        'RAW_DIR_IS_GITIGNORED': os.path.exists(os.path.join(RAW_PESSOAL, '.gitignore')),
        'RAW_FILES': (len([n for n in os.listdir(RAW_PESSOAL) if not n.startswith('.')])
                      if os.path.isdir(RAW_PESSOAL) else 0),
        'SALT_PRESENT': os.path.exists(SAL),
        'SALT_LOCATION': 'fora do repositório, em ~/.sintonia-browser/ig/',
        'PURGE_READY': True,
        'PURGE_HOW': 'py scripts/instagram_pessoal.py expurgar',
    }


def expurgar(confirmar=False):
    """Apaga o acervo de comentário: bruto, artefato e sal. Nada de meio-termo.

    O sal vai junto de propósito. Sem ele, os pseudônimos que por acaso tenham vazado
    para outro artefato deixam de poder ser ligados a qualquer handle, mesmo por quem
    tenha a lista de handles. Apagar a chave é o que torna o expurgo definitivo.
    """
    alvos = [RAW_PESSOAL, ARTEFATO, SAL]
    if not confirmar:
        return {'DRY_RUN': True, 'ALVOS': alvos,
                'AVISO': 'nada foi apagado. Rode com --confirmar para executar.'}
    apagados = []
    for a in alvos:
        if os.path.isdir(a):
            shutil.rmtree(a, ignore_errors=True)
            apagados.append(a)
        elif os.path.isfile(a):
            os.remove(a)
            apagados.append(a)
    return {'DRY_RUN': False, 'APAGADOS': apagados,
            'O_QUE_ISTO_NAO_APAGA': (
                'commits antigos, se algum comentário chegou a ser versionado por engano. '
                'Por isso a pasta nasce ignorada.')}


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'estado'
    if cmd == 'estado':
        preparar_pasta()
        print(json.dumps(estado(), ensure_ascii=False, indent=1))
    elif cmd == 'expurgar':
        print(json.dumps(expurgar('--confirmar' in sys.argv), ensure_ascii=False, indent=1))
    elif cmd == 'pseudonimo':
        print(pseudonimo(sys.argv[2] if len(sys.argv) > 2 else ''))
    else:
        print('uso: instagram_pessoal.py {estado|expurgar [--confirmar]|pseudonimo <handle>}')
        raise SystemExit(2)
