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
# O que a guarda NAO consegue provar sozinha, e por isso pede declarado no
# pedido: que a copia da Sala e mesmo READ_ONLY, e que a prova do LAB diz o que
# diz. Ela recusa quem nao declara; nao verifica o conteudo dessas duas.
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
        if e.get('AUTORIDADE') != AUTORIDADE_PREVIEW or MARCA_NO_DIARIO not in diario:
            return None
        if e.get('REVOGADA') is not False or e.get('NAO_FECHA_A_FUNDACAO') is not True:
            return None
        return e
    return None


def ramo_de_producao(ramo, publicacao):
    """Uma branch de promocao e producao — a excecao nunca vale nela."""
    return ramo in (publicacao.get('PROMOTION_AUTHORITY_BRANCHES') or [])


def artefatos_autorizados(trava, diario, publicacao, ramos=()):
    """{PATH: GIT_BLOB_SHA} que a excecao deixa mudar ou nascer, preso por sha.

    Vazio se a excecao nao vale, ou se QUALQUER um dos `ramos` em que se corre
    for de producao: la o congelamento e o do manifesto, sem excecao."""
    e = excecao_vigente(trava, diario)
    if e is None or any(ramo_de_producao(r, publicacao) for r in ramos):
        return {}
    return {a['PATH']: a['GIT_BLOB_SHA'] for a in e.get('ARTEFATOS_AUTORIZADOS') or []
            if isinstance(a, dict) and a.get('PATH') and len(str(a.get('GIT_BLOB_SHA') or '')) == 40}


def _objetos_nao_liberados(pote):
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
            elif not c8.strip() or c8.startswith('FALHOU'):
                maus.append(oid + ' sem ' + DECISAO_DO_DONO)
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


def pode_atravessar_a_trava(pedido, trava, diario, publicacao, validar=_validar_pote_v2):
    """-> (pode, motivo). O padrao e NAO. So o caminho do preview declarado passa.

    pedido = {OPERACAO, DESTINO: {TIPO, BRANCH, HOST, PARA_CLIENTE},
              ENTRADA: {TIPO, READ_ONLY}, POTE, PROVA_REVERSA_DO_LAB: {VEREDITO, ONDE}}"""
    if pedido.get('OPERACAO') != PUBLICAR_NO_PREVIEW:
        return False, '%s · operacao %r: a Sala nunca se escreve por aqui, e a excecao so publica no preview' % (
            BLOQUEIO, pedido.get('OPERACAO'))
    e = excecao_vigente(trava, diario)
    if e is None:
        return False, '%s · sem a excecao %s vigente (autoridade %s no diario, nao revogada)' % (
            BLOQUEIO, EXCECAO_PREVIEW, AUTORIDADE_PREVIEW)
    d = pedido.get('DESTINO') or {}
    tipos = set(DESTINOS_DO_PREVIEW) & set((e.get('ESCOPO') or {}).get('DESTINOS_TIPO') or [])
    if d.get('TIPO') not in tipos:
        return False, '%s · destino %r fora do escopo do preview' % (BLOQUEIO, d.get('TIPO'))
    if d.get('PARA_CLIENTE') is not False:
        return False, '%s · destino para cliente (ou nao dito): a excecao nunca entrega a cliente' % BLOQUEIO
    ramo = d.get('BRANCH')
    if not ramo or ramo_de_producao(ramo, publicacao):
        return False, '%s · branch %r e de producao (ou nao dita)' % (BLOQUEIO, ramo)
    host = d.get('HOST')
    if host and host == publicacao.get('CANONICAL_HOST'):
        return False, '%s · %s e o endereco do produto, nao um preview' % (BLOQUEIO, host)
    if d.get('TIPO') == 'BUILD_LOCAL' and host not in HOSTS_LOCAIS:
        return False, '%s · build local com host publico %r' % (BLOQUEIO, host)
    if d.get('TIPO') == 'VERCEL_PREVIEW' and not (host and str(host).endswith('.vercel.app')):
        return False, '%s · preview da Vercel sem host de deployment' % BLOQUEIO
    ent = pedido.get('ENTRADA') or {}
    if ent.get('TIPO') != ENTRADA_READ_ONLY or ent.get('READ_ONLY') is not True:
        return False, '%s · a Sala so entra por copia/snapshot READ_ONLY' % BLOQUEIO
    lab = pedido.get('PROVA_REVERSA_DO_LAB') or {}
    if lab.get('VEREDITO') != 'PASS' or not str(lab.get('ONDE') or '').strip():
        return False, '%s · sem a prova reversa do LAB (VEREDITO=PASS e onde esta)' % BLOQUEIO
    pote = pedido.get('POTE')
    if not isinstance(pote, dict):
        return False, '%s · sem pote' % BLOQUEIO
    violacoes = validar(pote)
    if violacoes:
        return False, '%s · o pote reprova nos gates do pote v2: %s' % (BLOQUEIO, violacoes[0])
    maus, n = _objetos_nao_liberados(pote)
    if n == 0:
        return False, '%s · pote sem objeto liberado: nada a publicar' % BLOQUEIO
    if maus:
        return False, '%s · %d objeto(s) nao liberado(s), o pote inteiro fica: %s' % (BLOQUEIO, len(maus), maus[0])
    if 'OBJETOS_LIBERADOS' in pote and pote['OBJETOS_LIBERADOS'] != n:
        return False, '%s · OBJETOS_LIBERADOS=%r e o pote traz %d' % (BLOQUEIO, pote['OBJETOS_LIBERADOS'], n)
    return True, ('EXCECAO %s (%s) · %d objeto(s) liberado(s) para %s na branch %s · '
                  'COLLECTION_FOUNDATION_CLOSED continua %s' % (
                      EXCECAO_PREVIEW, AUTORIDADE_PREVIEW, n, d['TIPO'], ramo,
                      'SIM' if COLLECTION_FOUNDATION_CLOSED else 'NAO'))


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
