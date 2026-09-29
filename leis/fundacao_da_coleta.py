#!/usr/bin/env python3
"""COLLECTION_FOUNDATION_CLOSED != SIM  ->  INTELLIGENCE_IMPLEMENTATION_BLOCKED.

A direcao do projeto e uma so, e ela e sequencial:

    COLETA -> PRESERVACAO -> PROVENIENCIA -> PERSISTENCIA
           -> ADMISSION/READY -> COLLECTION_FOUNDATION_CLOSED
           -> e SO ENTAO inteligencia.

Este ficheiro existe porque uma regra que vive so num relatorio nao segura
nada. A tentacao de comecar a inteligencia antes da fundacao nao aparece como
uma decisao anunciada — aparece como um ficheiro pequeno que «so calcula um
score», e quando alguem repara ja ha um consumidor.

    O QUE FALTA NAO E MODELO. E FUNDACAO.

O QUE ESTA CONGELADO
--------------------
Implementacao, escrita e ativacao de: Field Voices, Opportunity, signals,
scoring, recommendations e a ligacao de inteligencia no portal.

O QUE NAO ESTA
--------------
LER essas areas. Um contrato futuro que ninguem pode ler e um contrato que se
quebra por ignorancia. Ler, medir, documentar e desenhar continua permitido —
o que nao se faz e IMPLEMENTAR.

    LER NAO E IMPLEMENTAR.
    DESENHAR NAO E ATIVAR.

COMO ISTO DEIXA DE VALER
------------------------
Nao por alguem achar que ja da. `COLLECTION_FOUNDATION_CLOSED` vira SIM quando
os criterios do mapa de fechamento estiverem satisfeitos ou com blocker
explicito — e quem muda esta constante muda junto o mapa que a sustenta.

E ele NAO significa «coletamos todas as fontes». Significa: toda CLASSE DE
ESTRADA necessaria tem arquitetura e donos fechados, ou um blocker escrito.
"""
import os

MAPA = os.path.join('docs', 'operacao', 'MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md')
# O ESTADO GERADO, nao a prosa. Quem quiser saber se a fundacao fechou le este
# ficheiro, produzido por `system-map/scripts/censo_das_estradas_it.py` — nunca
# uma tabela escrita a mao.
#
#     SISTEMA REAL -> CENSO -> ESTADO GERADO -> DOCUMENTO.
ESTADO = os.path.join('system-map', 'data', 'estradas-it.generated.json')

# O estado medido em 2026-09-08, quando o censo passou a CALCULAR em vez de
# repetir: ZERO estradas com arquitetura fechada. O mapa anterior publicava
# duas, porque uma pessoa as escreveu.
#
#     OWNER EXISTS NAO E OWNER CONNECTED.
COLLECTION_FOUNDATION_CLOSED = False

# ── DOIS CRITERIOS NOVOS, DECIDIDOS PELO DONO DO PROJETO ─────────────────
# A casa passa a exigir nascer DIAGNOSTICAVEL e EVOLUTION-READY. A lei nao se
# altera em silencio: a decisao esta em `docs/decisoes/DIARIO-DE-DECISOES.md`.
#
# OBSERVABILITY_READY NAO significa que toda rota ja rodou ao vivo. Significa
# que uma rota NOVA tem contrato OBRIGATORIO de emitir rastro, contabilidade,
# falha, diagnostico, custo e tempo — e que isso pode ser visto.
#
# EVOLUTION_READY NAO significa AI que aprende sozinha. Significa que as
# decisoes sao versionadas, os resultados ligaveis, e que baseline, politica,
# teste de fonte e champion/challenger sao representaveis.
#
#     A FUNDACAO PODE FECHAR COM POLITICA DETERMINISTICA.
#     NAO PODE FECHAR SE NAO PRODUZ OS DADOS PARA APRENDER DEPOIS.
OBSERVABILITY_READY = 'OBSERVABILITY_READY'
EVOLUTION_READY = 'EVOLUTION_READY'

CRITERIOS_NOVOS = {
    OBSERVABILITY_READY: (
        'medidas/rastro_da_coleta.py + leis/diagnostico.py + migration 024. '
        'DB_TESTED em PostgreSQL 16 descartavel; NAO aplicada em producao.'),
    EVOLUTION_READY: (
        'leis/gestao_da_coleta.py: decisao versionada, satisfacao antes do '
        'gasto, ciclo de vida da fonte, champion/challenger e rollback como '
        'contrato. Nenhuma promocao automatica.'),
}

AREAS_CONGELADAS = (
    'FIELD_VOICES', 'OPPORTUNITY', 'SIGNALS', 'SCORING',
    'RECOMMENDATIONS', 'PORTAL_INTELLIGENCE_WIRING',
)

BLOQUEIO = 'INTELLIGENCE_IMPLEMENTATION_BLOCKED'
PERMITIDO_LER = 'INTELLIGENCE_READ_ALLOWED'


def pode_implementar_inteligencia():
    """→ (pode, motivo). O padrao e NAO, e isso e a trava — nao um aviso."""
    if COLLECTION_FOUNDATION_CLOSED:
        return True, 'COLLECTION_FOUNDATION_CLOSED=SIM — a fundacao fechou'
    return False, (
        '%s · a fundacao da coleta ainda nao fechou. Ler, medir e desenhar '
        'continua permitido (%s); implementar, escrever e ativar, nao. '
        'O que falta esta em %s.' % (BLOQUEIO, PERMITIDO_LER, MAPA))


# ── D140 · A EXCECAO CONTROLADA PREVIEW_E2E, NA GUARDA E NAO SO NO PAPEL ────
# O dono decidiu (D140, 28/09): a fundacao CONTINUA NAO FECHADA, e pode existir
# UMA excecao estreita para provar SALA REAL -> INTELLIGENCE -> POTE -> CASCO
# ORIGINAL -> PREVIEW. O red team disse o resto: um bloco no JSON, sozinho, nao
# abre rota nenhuma e ainda cria contradicao com a guarda. Por isso a excecao
# vive aqui, em codigo, e o contrato so a DECLARA.
#
#     A EXCECAO NAO TOCA EM COLLECTION_FOUNDATION_CLOSED.
#     pode_implementar_inteligencia() continua a dizer NAO.
#
# ⚠️ RED TEAM DO BOT LUCIANO (29/09, sobre 7f3dc857c): a primeira versao
# aceitava TEXTO onde devia exigir PROVA — um ONDE do LAB para um ficheiro que
# nao existia, um C8 com qualquer frase, e READ_ONLY = True so dito. Os tres
# passavam. Agora cada um e CONFERIDO:
#
#     LAB   formato real do LAB: JSON numa pasta exclusiva, nome com o par, a
#           versao mais recente (DATA_UTC) do par (POTE_SHA256, RUN_ID) diz
#           VEREDITO=PASS e LAB_ORIGIN=sintonia-lab;
#     C8    comeca por um ID de decisao (Dnnn) escrito no diario, do dono, e
#           nao revogado — texto livre nao casa com nada;
#     SALA  a copia existe, o sha256 dela bate, o pote diz que foi feito DELA
#           (o sha aparece no CORTE), e nada no pedido aponta a Sala viva.
#
# O que continua a nao se provar aqui: que o conteudo do relatorio do LAB e
# VERDADEIRO. A guarda prova que ele existe e fala deste pote; ler a prova
# reversa e trabalho do LAB e do auditor.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAVA = os.path.join(RAIZ, 'docs', 'operacao', 'TRAVA-DA-INTELIGENCIA.json')
DIARIO = os.path.join(RAIZ, 'docs', 'decisoes', 'DIARIO-DE-DECISOES.md')
PUBLICACAO = os.path.join(RAIZ, 'system-map', 'CANONICAL-PUBLICATION.json')

EXCECAO_PREVIEW = 'PREVIEW_E2E'
AUTORIDADE_PREVIEW = 'D140'
MARCA_NO_DIARIO = '## D140 · EXCEÇÃO CONTROLADA DE E2E PARA PREVIEW'
PUBLICAR_NO_PREVIEW = 'PUBLICAR_POTE_NO_PREVIEW'
#: Os unicos destinos que o CODIGO conhece. O contrato pode declarar menos,
#: nunca mais: acrescentar «PRODUCAO» ao JSON nao ensina a guarda a aceita-lo.
DESTINOS_DO_PREVIEW = ('BUILD_LOCAL', 'VERCEL_PREVIEW')
HOSTS_LOCAIS = (None, '', 'localhost', '127.0.0.1')
ENTRADA_READ_ONLY = 'SALA_COPIA_READ_ONLY'
LIBERADO = 'LIBERADO_PARA_CLIENTE'
CONFERENCIAS_QUE_PASSAM = ('C1_PROVA_DO_ARQUIVO', 'C2_DATA_PROPRIA', 'C3_LUGAR_PROPRIO',
                           'C4_LIGACAO_ADAMA', 'C5_SEM_DUPLICADO',
                           'C6_ESPECIE_DO_COMPARTIMENTO', 'C7_SO_SAIDA_DA_INTELLIGENCE')
DECISAO_DO_DONO = 'C8_DECISAO_DO_DONO'
#: A Sala VIVA, como a casa a escreve (BIG-COLLECTION-RUNBOOK.md, RUN-MANIFEST):
#: nenhum pedido pode apontar para ela. Os DSN do ambiente tambem contam.
SALA_VIVA_PORTAS = ('54330',)
SALA_VIVA_ENV = ('SINTONIA_SALA_DSN', 'SUPABASE_DB_URL')
SALA_VIVA_HOSTS = ('supabase.co', 'supabase.com')
_CAMPOS_DE_LIGACAO = ('DSN', 'HOST', 'PORTA', 'PORT', 'URL', 'MORADA', 'ORIGEM')
# ⚠️ AUDITOR (VERIF-L1-7f3dc857c, 29/09): 13 de 16 pedidos hostis atravessavam.
# A guarda comparava TEXTO CRU (branch, host) e ignorava chaves que nao conhecia.
# Agora: branch e host normalizados antes de comparar, e o pedido tem uma lista
# FECHADA de chaves — chave desconhecida e recusa, nao silencio.
CHAVES_DO_PEDIDO = ('OPERACAO', 'DESTINO', 'ENTRADA', 'POTE', 'POTE_FICHEIRO', 'PROVA_REVERSA_DO_LAB')
CHAVES_DO_DESTINO = ('TIPO', 'BRANCH', 'HOST', 'PARA_CLIENTE')
CHAVES_DA_ENTRADA = ('TIPO', 'READ_ONLY', 'SNAPSHOT') + _CAMPOS_DE_LIGACAO
CHAVES_DO_SNAPSHOT = ('FICHEIRO', 'SHA256')
CHAVES_DO_LAB = ('VEREDITO', 'ONDE', 'SHA256')
_PREFIXOS_DE_RAMO = ('refs/heads/', 'refs/remotes/origin/', 'remotes/origin/', 'origin/')


def normalizar_ramo(ramo):
    """'refs/heads/Release/Canonical ' -> 'release/canonical'. None se nao ha ramo."""
    if not isinstance(ramo, str):
        return None
    r = ramo.strip().casefold()
    mudou = True
    while mudou:
        mudou = False
        for pre in _PREFIXOS_DE_RAMO:
            if r.startswith(pre):
                r, mudou = r[len(pre):], True
    return r or None


def nome_do_host(host):
    """-> (hostname normalizado, None) ou (None, motivo). So se aceita um NOME de
    host limpo: esquema, caminho, porta, utilizador ou query sao recusados."""
    from urllib.parse import urlsplit
    if host is None:
        return None, None
    if not isinstance(host, str):
        return None, 'host ilegivel %r' % (host,)
    bruto = host.strip().casefold()
    if not bruto:
        return None, None
    try:
        partes = urlsplit(bruto if '://' in bruto else '//' + bruto)
        nome = partes.hostname
        porta = partes.port
    except ValueError:
        return None, 'host ilegivel %r' % host
    if not nome or nome != bruto or porta is not None:
        return None, 'host %r nao e um nome de host limpo (so o nome, sem esquema nem caminho)' % host
    return nome, None


def _chaves_estranhas(d, permitidas):
    return sorted(k for k in d if k not in permitidas) if isinstance(d, dict) else []


def _tem_consumido_em(x):
    """consumido_em em QUALQUER nivel do pedido, e em qualquer caixa."""
    if isinstance(x, dict):
        return any('consumido_em' in str(k).casefold() or _tem_consumido_em(v) for k, v in x.items())
    if isinstance(x, list):
        return any(_tem_consumido_em(v) for v in x)
    return False
_TAMANHO_MAXIMO_DA_PROVA = 20 * 1024 * 1024
#: Quem pode assinar a prova reversa: o LAB, por identidade DECLARADA na propria
#: entrada da prova (e, alem disso, por pasta exclusiva — PASTAS_DO_LAB).
LAB_ORIGIN = 'sintonia-lab'
#: O que a prova diz quando o pote publicado nao tem envelope (formato real do LAB).
ENVELOPE_INEXISTENTE = 'NAO_EXISTE_NO_POTE_PUBLICADO'
#: ⚠️ LIMITE CONHECIDO (ponto do auditor, aceite pelo coordenador, 29/09): neste
#: PC todos os agentes correm como o MESMO utilizador Windows. A pasta exclusiva
#: NAO prova autoria — so impede reuso acidental e mistura. O que a guarda PROVA
#: e o vinculo (POTE_SHA256, RUN_ID) por igualdade de campo, que impede prova de
#: outro pote ou de outra corrida. Falsificacao deliberada por outro agente local
#: fica fora do alcance desta guarda e e coberta pela auditoria independente.
LIMITE_CONHECIDO = {
    'AUTORIA_DO_LAB': 'DECLARADA',
    'AUTORIA_PROVADA': False,
    'COMO_SE_DECLARA': 'LAB_ORIGIN na entrada da prova + pasta PASTAS_DO_LAB',
    'O_QUE_SE_PROVA': 'o vinculo (POTE_SHA256, RUN_ID) por igualdade de campo',
    'FORA_DO_ALCANCE': 'falsificacao deliberada por outro agente local (mesmo utilizador Windows); '
                       'coberta pela auditoria independente',
}
#: O ambito exato da D140, como o coordenador o pediu escrito. A guarda LE-o no
#: contrato e exige-o literal: um valor diferente nao alarga — invalida.
AMBITO_EXATO = {'DESTINO': 'SO_PREVIEW', 'SALA_LEITURA': 'SO_COPIA_READ_ONLY',
                'SALA_ESCRITA': 'NUNCA', 'CONSUMIDO_EM': 'FORA',
                'PRODUCAO': 'BLOQUEADA', 'ENDERECO_OFICIAL': 'NAO'}


def _ler_json(caminho):
    import json
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def carregar():
    """-> (trava, texto do diario, publicacao canonica), lidos do disco."""
    with open(DIARIO, encoding='utf-8') as f:
        diario = f.read()
    return _ler_json(TRAVA), diario, _ler_json(PUBLICACAO)


def excecao_vigente(trava, diario, ident=EXCECAO_PREVIEW):
    """A entrada da excecao, SO se ela ainda vale; senao None.

    Vale quando: tem a AUTORIDADE D140, a D140 esta escrita no diario, nao foi
    revogada, e diz de si propria que nao fecha a fundacao. Falta uma = None."""
    for e in trava.get('EXCECOES_CONTROLADAS') or []:
        if not isinstance(e, dict) or e.get('ID') != ident:
            continue
        if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW or not _d140_vigente_no_diario(diario):
            return None
        if e.get('REVOGADA') is not False or e.get('NAO_FECHA_A_FUNDACAO') is not True:
            return None
        ambito = e.get('AMBITO_EXATO') or {}
        if any(ambito.get(k) != v for k, v in AMBITO_EXATO.items()):
            return None
        return e
    return None


def _revogada_no_diario(ident, diario, secao=''):
    """A decisao foi revogada? Pelo Estado da seccao, ou por uma frase que a
    revoga por nome: «REVOGA D140», «D140 REVOGADA», «REVOGADA — ## D140 ·»."""
    import re
    if re.search(r'\*\*Estado:\*\*\s*REVOGAD', secao):
        return True
    n = re.escape(ident)
    return bool(re.search(r'\bREVOGA\s+(a\s+)?%s\b' % n, diario, re.I)
                or re.search(r'\bREVOGAD[AO]\b[^\w\n]{0,8}(##\s*)?%s\b' % n, diario, re.I)
                or re.search(r'\b%s\b[^\w\n]{0,8}(foi\s+)?REVOGAD[AO]\b' % n, diario, re.I))


def _d140_vigente_no_diario(diario):
    """A D140 so conta com o CABECALHO exato numa linha propria e sem revogacao."""
    if not any(linha.startswith(MARCA_NO_DIARIO) for linha in diario.splitlines()):
        return False
    return not _revogada_no_diario(AUTORIDADE_PREVIEW, diario,
                                   _secoes_do_diario(diario).get(AUTORIDADE_PREVIEW, ''))


def ramo_de_producao(ramo, publicacao):
    """Uma branch de promocao e producao — a excecao nunca vale nela. Compara-se
    NORMALIZADO: refs/heads/, origin/ e a caixa nao fazem de producao outra coisa."""
    return normalizar_ramo(ramo) in {normalizar_ramo(r) for r in publicacao.get('PROMOTION_AUTHORITY_BRANCHES') or []}


def artefatos_autorizados(trava, diario, publicacao, ramos=()):
    """{PATH: GIT_BLOB_SHA} que a excecao deixa mudar ou nascer, preso por sha.

    Vazio se a excecao nao vale, ou se QUALQUER um dos `ramos` em que se corre
    for de producao: la o congelamento e o do manifesto, sem excecao."""
    e = excecao_vigente(trava, diario)
    if e is None or any(ramo_de_producao(r, publicacao) for r in ramos):
        return {}
    return {a['PATH']: a['GIT_BLOB_SHA'] for a in e.get('ARTEFATOS_AUTORIZADOS') or []
            if isinstance(a, dict) and a.get('PATH') and len(str(a.get('GIT_BLOB_SHA') or '')) == 40}


def _sha256_ficheiro(caminho):
    import hashlib
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def sha256_do_pote(pote):
    """O sha256 do pote CANONICO: JSON com chaves ordenadas, sem espacos, UTF-8.
    Nao depende de como o ficheiro foi escrito — so do que o pote diz."""
    import hashlib
    import json
    return hashlib.sha256(json.dumps(pote, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def _caminho(rel):
    if not isinstance(rel, str) or not rel.strip():
        return None
    return rel if os.path.isabs(rel) else os.path.join(RAIZ, rel)


def _dentro_de(f, pastas):
    real = os.path.normcase(os.path.realpath(f))
    for p in pastas or []:
        raiz = os.path.normcase(os.path.realpath(_caminho(p) or ''))
        if raiz and os.path.isdir(raiz) and os.path.commonpath([real, raiz]) == raiz:
            return True
    return False


def nome_da_prova_do_lab(sha_canonico, run_id, versao=1):
    """O nome que o LAB da a prova (formato real do LAB, 29/09):
    PROVA-REVERSA_pote-<16 primeiros do sha canonico>_run-<RUN_ID>.json, e -2, -3
    quando o mesmo par volta a ser provado (nunca sobrescreve)."""
    base = 'PROVA-REVERSA_pote-%s_run-%s' % (str(sha_canonico)[:16], run_id)
    return base + ('.json' if versao == 1 else '-%d.json' % versao)


def _versao_do_nome(nome, sha_canonico, run_id):
    """1, 2, 3... se o nome e de uma prova DESTE par; None se nao e. Compara-se o
    prefixo exato — um RUN_ID que acabe em '-0001' nao se confunde com versao."""
    base = nome_da_prova_do_lab(sha_canonico, run_id)[:-len('.json')]
    if nome == base + '.json':
        return 1
    if nome.startswith(base + '-') and nome.endswith('.json'):
        meio = nome[len(base) + 1:-len('.json')]
        if meio.isdigit() and int(meio) >= 2 and str(int(meio)) == meio:
            return int(meio)
    return None


def _data_utc(valor):
    """DATA_UTC em ISO -> datetime com fuso (sem fuso = UTC). None se ausente ou invalida."""
    from datetime import datetime, timezone
    if not isinstance(valor, str) or not valor.strip():
        return None
    try:
        d = datetime.fromisoformat(valor.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _ler_prova(f):
    import json
    try:
        with open(f, encoding='utf-8') as h:
            return json.load(h)
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _envelope_do_pote(pote):
    e = pote.get('ENVELOPE_HASH')
    return e if isinstance(e, str) and e.strip() else None


def conferir_prova_do_lab(lab, sha_canonico, run_id=None, pastas_do_lab=(), pote_ficheiro=None,
                          produtores=(), envelope=None):
    """-> motivo da recusa, ou None. FORMATO REAL DO LAB (29/09), sem inventar outro.

    Um objeto JSON por ficheiro, na pasta exclusiva do LAB, com o nome
    PROVA-REVERSA_pote-<sha16>_run-<RUN_ID>[-N].json. A guarda compara por
    IGUALDADE DE CAMPO: POTE_SHA256 (canonico) e RUN_ID deste pote, LAB_ORIGIN ==
    'sintonia-lab' (e nao o produtor), VEREDITO so PASS|FAIL e tem de ser PASS,
    ENVELOPE_HASH igual ao do pote quando o pote tem envelope (senao
    'NAO_EXISTE_NO_POTE_PUBLICADO'). Com varias versoes do mesmo par, vale a MAIS
    RECENTE pelo DATA_UTC DE DENTRO do JSON — nunca pela ordem do nome ('-10'
    vem antes de '-2' no alfabeto). Empate de DATA_UTC = FAIL; DATA_UTC ausente ou
    invalida = FAIL. Um FAIL recente derruba um PASS antigo.

    Isto NAO prova autoria (LIMITE_CONHECIDO): prova o vinculo ao pote e a corrida."""
    if not isinstance(lab, dict):
        return 'sem a prova reversa do LAB'
    f = _caminho(lab.get('ONDE'))
    if not f or not os.path.isfile(f):
        return 'a prova do LAB %r nao existe' % lab.get('ONDE')
    if not _dentro_de(f, pastas_do_lab):
        return 'a prova do LAB nao esta numa pasta do LAB (PASTAS_DO_LAB da excecao)'
    if pote_ficheiro and _dentro_de(pote_ficheiro, pastas_do_lab):
        return 'o pote do produtor esta dentro da pasta do LAB: o produtor nao prova a si mesmo'
    fixado = str(lab.get('SHA256') or '').lower()
    if len(fixado) != 64 or _sha256_ficheiro(f) != fixado:
        return 'o sha256 da prova do LAB nao bate com o fixado no pedido'
    if os.path.getsize(f) > _TAMANHO_MAXIMO_DA_PROVA:
        return 'a prova do LAB e grande demais para ser lida'
    obj = _ler_prova(f)
    if obj is None:
        return 'a prova do LAB nao e estruturada (JSON): texto solto nao prova nada'
    if not isinstance(obj, dict):
        return 'a prova do LAB nao e UM objeto de prova (formato real do LAB)'
    rej = obj.get('POTE_REJEITADO')
    if any(isinstance(r, str) and r.strip().lower() == sha_canonico
           for r in (rej if isinstance(rej, list) else [rej])):
        return 'a prova do LAB diz POTE_REJEITADO para este pote'
    if obj.get('POTE_SHA256') != sha_canonico or run_id is None or obj.get('RUN_ID') != str(run_id):
        return ('a prova do LAB nao e do par (POTE_SHA256, RUN_ID) deste pote (corrida %r): diz (%r, %r)'
                % (run_id, str(obj.get('POTE_SHA256'))[:16], obj.get('RUN_ID')))
    if obj.get('LAB_ORIGIN') != LAB_ORIGIN:
        return 'a prova nao vem de %s (LAB_ORIGIN=%r)' % (LAB_ORIGIN, obj.get('LAB_ORIGIN'))
    if str(obj.get('LAB_ORIGIN')).strip().casefold() in {str(x).strip().casefold() for x in produtores if x}:
        return 'LAB_ORIGIN e o proprio produtor do pote'
    if obj.get('VEREDITO') not in ('PASS', 'FAIL'):
        return 'a prova do LAB tem VEREDITO=%r (so PASS ou FAIL)' % obj.get('VEREDITO')
    esperado = envelope or ENVELOPE_INEXISTENTE
    if obj.get('ENVELOPE_HASH') != esperado:
        return 'ENVELOPE_HASH da prova (%r) nao e o do pote (%r)' % (obj.get('ENVELOPE_HASH'), esperado)
    if _versao_do_nome(os.path.basename(f), sha_canonico, run_id) is None:
        return 'o nome da prova nao e %s[-N]' % nome_da_prova_do_lab(sha_canonico, run_id)[:-len('.json')]
    # as versoes do MESMO par, na mesma pasta: vale a mais recente pelo DATA_UTC de dentro
    pasta = os.path.dirname(f)
    versoes = []
    for nome in sorted(os.listdir(pasta)):
        if _versao_do_nome(nome, sha_canonico, run_id) is None:
            continue
        caminho = os.path.join(pasta, nome)
        v = _ler_prova(caminho)
        quando = _data_utc(v.get('DATA_UTC')) if isinstance(v, dict) else None
        if quando is None:
            return 'a versao %s da prova deste par tem DATA_UTC ausente ou invalida: FAIL' % nome
        if not isinstance(v, dict) or v.get('POTE_SHA256') != sha_canonico or v.get('RUN_ID') != str(run_id):
            return 'a versao %s tem o nome deste par e o conteudo de outro: FAIL' % nome
        versoes.append((quando, caminho, v))
    ultima = max(q for q, _c, _v in versoes)
    no_topo = [(c, v) for q, c, v in versoes if q == ultima]
    if len(no_topo) > 1:
        return 'empate de DATA_UTC entre %d provas deste par: FAIL (lado cauteloso)' % len(no_topo)
    caminho, v = no_topo[0]
    if os.path.normcase(os.path.realpath(caminho)) != os.path.normcase(os.path.realpath(f)):
        return 'ha prova mais recente deste par (%s, VEREDITO=%r): a do pedido ja nao vale' % (
            os.path.basename(caminho), v.get('VEREDITO'))
    if obj.get('VEREDITO') != 'PASS':
        return 'a prova mais recente deste par diz VEREDITO=%r' % obj.get('VEREDITO')
    return None


def _secoes_do_diario(diario):
    """{ 'D140': texto da seccao } — so as seccoes `## Dnnn ·` / `## Dnnn —`."""
    import re
    secoes, atual, linhas = {}, None, []
    for linha in diario.splitlines():
        if linha.startswith('## '):
            if atual:
                secoes[atual] = '\n'.join(linhas)
            m = re.match(r'## (D\d{2,4})\s*[·—-]', linha)
            atual, linhas = (m.group(1) if m else None), [linha]
        elif atual:
            linhas.append(linha)
    if atual:
        secoes[atual] = '\n'.join(linhas)
    return secoes


def decisao_registada(c8, diario):
    """-> (ID, None) se o C8 comeca por uma decisao do DONO escrita no diario e
    nao revogada; senao (None, motivo). Texto livre nunca casa."""
    import re
    m = re.match(r'\s*(D\d{2,4})\b', str(c8 or ''))
    if not m:
        return None, 'C8 nao comeca por um ID de decisao (Dnnn): texto livre nao e autorizacao'
    ident = m.group(1)
    sec = _secoes_do_diario(diario).get(ident)
    if sec is None:
        return None, 'a decisao %s nao esta registada no diario' % ident
    if _revogada_no_diario(ident, diario, sec):
        return None, 'a decisao %s foi revogada' % ident
    if not re.search(r'\bdono\b', sec, re.I):
        return None, 'a decisao %s nao e do dono' % ident
    return ident, None


def _aponta_a_sala_viva(valor):
    v = str(valor or '').lower()
    if not v:
        return False
    if any(':' + p in v or v == p for p in SALA_VIVA_PORTAS):
        return True
    if any(h in v for h in SALA_VIVA_HOSTS):
        return True
    return any(os.environ.get(n) and os.environ[n].strip().lower() in v for n in SALA_VIVA_ENV)


def _valores(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _valores(v)
    elif isinstance(x, list):
        for v in x:
            yield from _valores(v)
    else:
        yield x


def conferir_entrada(ent, pote):
    """-> motivo da recusa, ou None. READ_ONLY nao se diz: prova-se com a copia."""
    if not isinstance(ent, dict) or ent.get('TIPO') != ENTRADA_READ_ONLY or ent.get('READ_ONLY') is not True:
        return 'a Sala so entra por copia/snapshot READ_ONLY'
    for k in _CAMPOS_DE_LIGACAO:
        if _aponta_a_sala_viva(ent.get(k)):
            return 'a entrada aponta para a Sala VIVA (%s): so a copia entra' % k
    snap = ent.get('SNAPSHOT')
    if not isinstance(snap, dict):
        return 'READ_ONLY sem prova: falta a copia/snapshot da Sala'
    f = _caminho(snap.get('FICHEIRO'))
    declarado = str(snap.get('SHA256') or '').lower()
    if not f or not os.path.isfile(f):
        return 'READ_ONLY sem prova: a copia/snapshot da Sala nao existe'
    if len(declarado) != 64 or _sha256_ficheiro(f) != declarado:
        return 'o sha256 da copia da Sala nao bate com o declarado'
    corte = pote.get('CORTE')
    if not isinstance(corte, dict) or declarado not in {str(v).lower() for v in _valores(corte)}:
        return 'o pote nao diz que foi feito desta copia (o sha256 nao esta no CORTE)'
    ro = corte.get('TRANSACTION_READ_ONLY')
    if ro is not None and not str(ro).lower().startswith('on'):
        return 'o CORTE do pote diz TRANSACTION_READ_ONLY=%r' % ro
    if any(_aponta_a_sala_viva(v) for v in _valores(corte)):
        return 'o CORTE do pote aponta para a Sala VIVA'
    return None


class Verificador:
    """O que a guarda consegue ver com os PROPRIOS olhos, em runtime.

    ADENDO DO RED TEAM (29/09): BRANCH, HOST e PARA_CLIENTE eram ALEGACOES do
    pedido. O que se consegue medir mede-se aqui; o resto sai no motivo como
    ALEGADO e nao conta como prova. Os testes trocam esta classe por uma falsa
    (sem rede, sem git); a guarda nao muda."""

    ENV_DO_RAMO = ('VERCEL_GIT_COMMIT_REF', 'GITHUB_HEAD_REF', 'GITHUB_REF_NAME')

    def ramo_real(self):
        """A branch em que ESTA arvore corre: a do build (Vercel/CI) ou a do git."""
        for k in self.ENV_DO_RAMO:
            if os.environ.get(k):
                return os.environ[k]
        import subprocess
        try:
            r = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=RAIZ,
                               capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            return None
        ramo = r.stdout.strip() if r.returncode == 0 else ''
        return ramo if ramo and ramo != 'HEAD' else None

    def deployment(self, host):
        """O que o PROPRIO deployment diz de si (system-map/deployment.generated.json,
        que nasce no build). None se nao responder — e ai nada esta provado."""
        import json
        import urllib.request
        try:
            with urllib.request.urlopen('https://%s/system-map/deployment.generated.json' % host,
                                        timeout=15) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:  # noqa: BLE001 — qualquer falha = nao verificado
            return None


def conferir_destino(d, ramo, publicacao, verificar):
    """-> (motivo da recusa ou None, [verificado]). A branch e o host medem-se."""
    # A branch declarada ja foi recusada se e de producao (normalizada). Aqui so
    # se exige que a MEDIDA seja igual a declarada — logo tambem nao e producao.
    if d.get('TIPO') == 'BUILD_LOCAL':
        real = verificar.ramo_real()
        if not real:
            return 'a branch real nao se consegue medir: BRANCH fica ALEGADA e nao prova nada', []
        if normalizar_ramo(real) != normalizar_ramo(ramo):
            return 'branch declarada %r, branch real %r' % (ramo, real), []
        return None, ['BRANCH=%s (medida no git/build)' % real]
    host = nome_do_host(d.get('HOST'))[0]
    dep = verificar.deployment(host)
    if not isinstance(dep, dict):
        return ('o deployment %s nao respondeu: HOST e BRANCH ficam ALEGADOS e nao provam nada'
                % host), []
    src = dep.get('SOURCE_BRANCH')
    if normalizar_ramo(src) != normalizar_ramo(ramo):
        return 'branch declarada %r, o deployment %s diz SOURCE_BRANCH=%r' % (ramo, host, src), []
    return None, ['HOST=%s respondeu SOURCE_BRANCH=%s (Vercel)' % (host, src)]


def _produtores_do_pote(pote):
    """Quem produziu o pote, pelo que ele diz: o PRODUTOR do topo e o LIBERADO_POR
    de cada objeto. O LAB nao pode ser nenhum deles."""
    quem = {pote.get('PRODUTOR')}
    for e in (pote.get('COMPARTIMENTOS') or {}).values():
        for o in (e or {}).get('OBJETOS') or []:
            quem.add(o.get('LIBERADO_POR'))
    return {q for q in quem if isinstance(q, str) and q.strip()}


def _objetos_nao_liberados(pote, diario):
    """Os objetos do pote que o contrato de liberacao v2.2 nao deixa sair."""
    run = pote.get('INTELLIGENCE_RUN_ID')
    maus, n = [], 0
    for comp, e in (pote.get('COMPARTIMENTOS') or {}).items():
        for o in (e or {}).get('OBJETOS') or []:
            n += 1
            oid = '%s/%s' % (comp, o.get('OBJETO_ID', '?'))
            c = o.get('CONFERENCIA_DE_LIBERACAO') or {}
            c8 = str(c.get(DECISAO_DO_DONO) or '')
            if o.get('LIBERACAO') != LIBERADO:
                maus.append(oid + ' sem LIBERACAO=' + LIBERADO)
            elif any(c.get(k) != 'PASSOU' for k in CONFERENCIAS_QUE_PASSAM):
                maus.append(oid + ' com conferencia C1..C7 que nao PASSOU')
            elif not c8.strip() or 'falhou' in c8.casefold():
                maus.append(oid + ' sem ' + DECISAO_DO_DONO)
            elif decisao_registada(c8, diario)[0] is None:
                maus.append(oid + ': ' + decisao_registada(c8, diario)[1])
            elif o.get('LIBERADO_POR') != 'INTELLIGENCE' or o.get('LIBERADO_NA_CORRIDA') != run:
                maus.append(oid + ' nao liberado pela Intelligence nesta corrida')
    return maus, n


def _validar_pote_v2(pote):
    import sys
    pacote = os.path.join(RAIZ, 'pacote')
    if pacote not in sys.path:
        sys.path.insert(0, pacote)
    import validar_pote_v2  # noqa: PLC0415 — so quem pede para atravessar paga o import
    return validar_pote_v2.validar(pote)


def pode_atravessar_a_trava(pedido, trava, diario, publicacao, validar=_validar_pote_v2, verificar=None):
    """-> (pode, motivo). O padrao e NAO. So o caminho do preview declarado passa.

    pedido = {OPERACAO, DESTINO: {TIPO, BRANCH, HOST, PARA_CLIENTE},
              ENTRADA: {TIPO, READ_ONLY, SNAPSHOT: {FICHEIRO, SHA256}},
              POTE, POTE_FICHEIRO?, PROVA_REVERSA_DO_LAB: {VEREDITO, ONDE}}"""
    if pedido.get('OPERACAO') != PUBLICAR_NO_PREVIEW:
        return False, '%s · operacao %r: a Sala nunca se escreve por aqui, e a excecao so publica no preview' % (
            BLOQUEIO, pedido.get('OPERACAO'))
    if _tem_consumido_em(pedido):
        return False, '%s · consumido_em fica FORA da excecao (D140): outra decisao' % BLOQUEIO
    estranhas = _chaves_estranhas(pedido, CHAVES_DO_PEDIDO)
    if estranhas:
        return False, '%s · chave(s) que a guarda nao conhece: %s — desconhecido e recusa' % (BLOQUEIO, estranhas)
    e = excecao_vigente(trava, diario)
    if e is None:
        return False, '%s · sem a excecao %s vigente (autoridade %s no diario, nao revogada)' % (
            BLOQUEIO, EXCECAO_PREVIEW, AUTORIDADE_PREVIEW)
    d = pedido.get('DESTINO')
    if not isinstance(d, dict):
        return False, '%s · destino ilegivel %r: sem destino dito, nada sai' % (BLOQUEIO, d)
    for nome, sub, perm in (('DESTINO', d, CHAVES_DO_DESTINO), ('ENTRADA', pedido.get('ENTRADA'), CHAVES_DA_ENTRADA),
                            ('SNAPSHOT', (pedido.get('ENTRADA') or {}).get('SNAPSHOT')
                             if isinstance(pedido.get('ENTRADA'), dict) else None, CHAVES_DO_SNAPSHOT),
                            ('PROVA_REVERSA_DO_LAB', pedido.get('PROVA_REVERSA_DO_LAB'), CHAVES_DO_LAB)):
        estranhas = _chaves_estranhas(sub, perm)
        if estranhas:
            return False, '%s · %s com chave(s) desconhecida(s): %s' % (BLOQUEIO, nome, estranhas)
    tipos = set(DESTINOS_DO_PREVIEW) & set((e.get('ESCOPO') or {}).get('DESTINOS_TIPO') or [])
    if d.get('TIPO') not in tipos:
        return False, '%s · destino %r fora do escopo do preview' % (BLOQUEIO, d.get('TIPO'))
    if d.get('PARA_CLIENTE') is not False:
        return False, '%s · destino para cliente (ou nao dito): a excecao nunca entrega a cliente' % BLOQUEIO
    ramo = d.get('BRANCH')
    if not ramo or ramo_de_producao(ramo, publicacao):
        return False, '%s · branch %r e de producao (ou nao dita)' % (BLOQUEIO, ramo)
    host, erro = nome_do_host(d.get('HOST'))
    if erro:
        return False, '%s · %s' % (BLOQUEIO, erro)
    if host and host == nome_do_host(publicacao.get('CANONICAL_HOST'))[0]:
        return False, '%s · %s e o endereco do produto, nao um preview' % (BLOQUEIO, host)
    if d.get('TIPO') == 'BUILD_LOCAL' and host not in HOSTS_LOCAIS:
        return False, '%s · build local com host publico %r' % (BLOQUEIO, host)
    if d.get('TIPO') == 'VERCEL_PREVIEW' and not (host and host.endswith('.vercel.app')
                                                  and host != 'vercel.app'):
        return False, '%s · preview da Vercel sem host de deployment' % BLOQUEIO
    problema, verificado = conferir_destino(d, ramo, publicacao, verificar or Verificador())
    if problema:
        return False, '%s · %s' % (BLOQUEIO, problema)
    alegado = ['PARA_CLIENTE=False (intencao do pedido: so restringe, nao abre nada)']
    pote = pedido.get('POTE')
    if not isinstance(pote, dict):
        return False, '%s · sem pote' % BLOQUEIO
    problema = conferir_entrada(pedido.get('ENTRADA'), pote)
    if problema:
        return False, '%s · %s' % (BLOQUEIO, problema)
    verificado.append('COPIA DA SALA sha256=%s existe, bate e o CORTE do pote cita-a'
                      % str(pedido['ENTRADA']['SNAPSHOT']['SHA256'])[:16])
    alegado.append('TRANSACTION_READ_ONLY dentro do CORTE (dito pelo motor que fez a copia)')
    lab = pedido.get('PROVA_REVERSA_DO_LAB')
    if not isinstance(lab, dict) or lab.get('VEREDITO') != 'PASS':
        return False, '%s · sem a prova reversa do LAB (VEREDITO=PASS e onde esta)' % BLOQUEIO
    problema = conferir_prova_do_lab(lab, sha256_do_pote(pote), pote.get('INTELLIGENCE_RUN_ID'),
                                     e.get('PASTAS_DO_LAB') or (), _caminho(pedido.get('POTE_FICHEIRO')),
                                     _produtores_do_pote(pote), _envelope_do_pote(pote))
    if problema:
        return False, '%s · %s' % (BLOQUEIO, problema)
    verificado.append('LAB: %s e a prova MAIS RECENTE (DATA_UTC) do par (POTE_SHA256, RUN_ID) deste pote, '
                      'sha256 fixado, VEREDITO=PASS, LAB_ORIGIN=%s, ENVELOPE_HASH conferido'
                      % (os.path.basename(lab['ONDE']), LAB_ORIGIN))
    alegado.append('o CONTEUDO da prova reversa do LAB (nao e relido aqui)')
    alegado.append('o AUTOR da prova do LAB: AUTORIA_DO_LAB=DECLARADA (LAB_ORIGIN + pasta), AUTORIA_PROVADA=false '
                   '(todos os agentes correm como o mesmo utilizador Windows)')
    violacoes = validar(pote)
    if violacoes:
        return False, '%s · o pote reprova nos gates do pote v2: %s' % (BLOQUEIO, violacoes[0])
    maus, n = _objetos_nao_liberados(pote, diario)
    if n == 0:
        return False, '%s · pote sem objeto liberado: nada a publicar' % BLOQUEIO
    if maus:
        return False, '%s · %d objeto(s) nao liberado(s), o pote inteiro fica: %s' % (BLOQUEIO, len(maus), maus[0])
    if 'OBJETOS_LIBERADOS' in pote and pote['OBJETOS_LIBERADOS'] != n:
        return False, '%s · OBJETOS_LIBERADOS=%r e o pote traz %d' % (BLOQUEIO, pote['OBJETOS_LIBERADOS'], n)
    verificado.append('C8: cada objeto cita decisao do dono registada e nao revogada')
    return True, ('EXCECAO %s (%s) · %d objeto(s) liberado(s) para %s na branch %s · '
                  'COLLECTION_FOUNDATION_CLOSED continua %s · VERIFICADO: %s · '
                  'ALEGADO (nao conta como prova): %s · AUTORIA_PROVADA=false' % (
                      EXCECAO_PREVIEW, AUTORIDADE_PREVIEW, n, d['TIPO'], ramo,
                      'SIM' if COLLECTION_FOUNDATION_CLOSED else 'NAO',
                      '; '.join(verificado), '; '.join(alegado)))


# ── OS 14 CRITERIOS A..N, MEDIDOS — E NAO DIGITADOS ─────────────────────────
# Ate 28/09 a lista de cumpridos vivia escrita a mao no contrato (08/09). Aqui
# cada criterio le um campo que o censo das estradas MEDIU. Onde nenhum campo
# medido responde a pergunta, a resposta e NAO_SEI — nunca PASS por omissao.
PASS, FAIL, NAO_SEI = 'PASS', 'FAIL', 'NAO_SEI'
_DEGRAU_DO_CRITERIO = {'C': 'RAW', 'D': 'RUN', 'E': 'CHECKPOINT', 'F': 'DERIVED', 'G': 'STRUCTURED'}


def _degrau_tem_dono(estado, degrau):
    """Todas as classes que nao estao BLOCKED com razao escrita: o degrau tem
    dono LIGADO a estrada? Dono que existe e nao esta ligado nao conta."""
    falta, nao_sei, ok = [], [], []
    for r in estado.get('ROUTE_CLASSES') or []:
        rid = r.get('ROUTE_CLASS_ID')
        if r.get('BLOCKED_REASON'):
            continue
        s = (r.get('STEPS') or {}).get(degrau) or {}
        if s.get('STATE') == 'NOT_APPLICABLE':
            continue
        if not s.get('OWNER_EXISTS'):
            falta.append(rid)
        elif s.get('CONNECTED_TO_ROUTE') is True:
            ok.append(rid)
        elif s.get('CONNECTED_TO_ROUTE') is False and s.get('ABSENCE_IS_CONCLUSIVE'):
            falta.append(rid)
        else:
            nao_sei.append(rid)
    base = '%s: %d classes com dono ligado, %d sem dono ligado %s, %d por provar %s' % (
        degrau, len(ok), len(falta), falta, len(nao_sei), nao_sei)
    return (FAIL if falta else NAO_SEI if nao_sei else PASS), base


def medir_criterios(estado):
    """estado = o que censo_das_estradas_it.py escreve. -> {letra: {ESTADO, MEDIDA}}."""
    v = estado.get('VEREDITOS') or {}
    f = estado.get('FONTES_IT') or {}
    m = {}
    desconhecidas = f.get('SOURCES_ROUTE_UNKNOWN')
    m['A'] = ((NAO_SEI if desconhecidas is None else PASS if desconhecidas == 0 else FAIL),
              'FONTES_IT.SOURCES_ROUTE_UNKNOWN = %s de %s' % (desconhecidas, f.get('TOTAL')))
    m['B'] = (NAO_SEI, 'nenhum campo das estradas mede «writer improvisado»')
    for letra, degrau in _DEGRAU_DO_CRITERIO.items():
        m[letra] = _degrau_tem_dono(estado, degrau)
    orq = estado.get('ORQUESTRADOR') or {}
    m['H'] = ((FAIL, 'ORQUESTRADOR.EXISTE = false') if orq.get('EXISTE') is False else
              (NAO_SEI, 'orquestrador existe e alcanca %s executores; quantos existem nao entra '
                        'nesta medida — existir nao e cobrir' % orq.get('EXECUTORES_ALCANCADOS')))
    apify = (estado.get('APIFY') or {}).get('DEFAULT')
    m['I'] = ((NAO_SEI if apify is None else PASS if apify == 0 else FAIL),
              'APIFY.DEFAULT = %s' % apify)
    git = estado.get('GIT_COMO_BANCO_OPERACIONAL')
    m['J'] = ((NAO_SEI if git is None else FAIL if git else PASS),
              'GIT_COMO_BANCO_OPERACIONAL: %s' % ', '.join(
                  '%s (%s linhas)' % (x.get('FICHEIRO'), x.get('LINHAS')) for x in git or []) or 'nenhum')
    m['K'] = (NAO_SEI, 'nenhum campo das estradas mede retry/queda')
    sem_decisao = v.get('M1_BLOCKED_SEM_DECISAO_ESCRITA')
    sem_prova = v.get('M1_FONTES_SEM_PROXIMA_PROVA')
    m['L'] = ((NAO_SEI if sem_decisao is None or sem_prova is None else
               PASS if not sem_decisao and not sem_prova else FAIL),
              'BLOCKED sem decisao escrita = %s; UNKNOWN sem proxima prova = %s' % (sem_decisao, sem_prova))
    m['M'] = (NAO_SEI, 'o veredito do validador do mapa nao entra no estado das estradas')
    m['N'] = (FAIL, 'por regra (NOTA_SOBRE_O_N): so se cumpre no fim, e conta como pendente ate la')
    return {k: {'ESTADO': e, 'MEDIDA': x} for k, (e, x) in sorted(m.items())}


if __name__ == '__main__':
    pode, motivo = pode_implementar_inteligencia()
    print('COLLECTION_FOUNDATION_CLOSED = %s' % ('SIM' if COLLECTION_FOUNDATION_CLOSED else 'NAO'))
    for k, v in sorted(CRITERIOS_NOVOS.items()):
        print('%-24s %s' % (k, v[:60]))
    print('INTELLIGENCE_IMPLEMENTATION  = %s' % ('LIBERADA' if pode else BLOQUEIO))
    print()
    print(motivo)
