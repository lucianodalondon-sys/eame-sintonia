#!/usr/bin/env python3
"""O CENSO DAS CLASSES DE ESTRADA DA COLETA ITALIANA.

    python3 system-map/scripts/censo_das_estradas_it.py

A unidade de analise nao e a fonte. E a CLASSE DE ESTRADA — o conjunto de
fontes que compartilham a mesma cadeia operacional:

    DISCOVER -> FETCH -> RAW -> RUN -> CHECKPOINT -> DERIVED
             -> STRUCTURED -> ADMISSION

Uma fonte nova numa estrada ja fechada nao e missao: e configuracao. So estrada
NOVA justifica canario novo.

O vocabulario de classe NAO foi inventado aqui: `leis/social_matriz.py` ja
declara `CLASSE` por rota, e as classes nao-sociais saem do codigo medido. O
que este script faz e CONTAR, para que o mapa em
`docs/operacao/MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md` nunca dependa de
memoria.
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import social_matriz as mz          # noqa: E402
import fundacao_da_coleta as fdc    # noqa: E402

CATALOGO = os.path.join(RAIZ, 'candidatas', 'ITALY-SOURCE-MASTER-V1.json')
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.generated.json')
LEDGER_GIT = os.path.join(RAIZ, 'data', 'collection-ledger', 'italy')


def fontes_it():
    with open(CATALOGO, encoding='utf-8') as f:
        return json.load(f).get('sources') or []


def rota_conhecida(fonte):
    """A rota da fonte esta declarada, ou o catalogo diz NAO SEI?

    `NAO SEI` e uma resposta legitima e por isso e CONTADA, nunca convertida
    em palpite. Enquanto ela existir, ninguem sabe quantas missoes faltam.
    """
    return not str(fonte.get('ACCESS_METHOD') or '').upper().startswith('NÃO SEI')


def classes_sociais():
    """As classes que a matriz social ja declara, com quantas rotas permitidas."""
    dec, perm, sem_razao = collections.Counter(), collections.Counter(), 0
    for _plat, caps in mz.MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, (list, tuple)):
                continue
            for r in rotas:
                if not isinstance(r, dict):
                    continue
                dec[r.get('CLASSE')] += 1
                if r.get('PERMITIDA') == 'SIM':
                    perm[r.get('CLASSE')] += 1
                if not str(r.get('NOTA') or '').strip():
                    sem_razao += 1
    return dec, perm, sem_razao


def apify():
    """Apify e default em alguma rota? A pergunta que a casa mais erra de cabeca."""
    default = fallback = 0
    for _plat, caps in mz.MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, (list, tuple)):
                continue
            for r in rotas:
                if isinstance(r, dict) and 'apify' in str(r.get('ROTA', '')).lower():
                    if r.get('PRIORIDADE') == 1:
                        default += 1
                    else:
                        fallback += 1
    return default, fallback


def git_como_banco():
    """Onde o Git ainda guarda estado operacional. Historico nao se apaga."""
    achados = []
    if os.path.isdir(LEDGER_GIT):
        for n in sorted(os.listdir(LEDGER_GIT)):
            caminho = os.path.join(LEDGER_GIT, n)
            with open(caminho, encoding='utf-8', errors='ignore') as f:
                linhas = sum(1 for _ in f)
            achados.append({'FICHEIRO': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
                            'LINHAS': linhas})
    return achados


# ═════════════════════════════════════════════════════════════════════════
# AS CLASSES DE ESTRADA — MEDIDAS, NAO DECLARADAS
# ═════════════════════════════════════════════════════════════════════════
# O MODELO diz quais etapas cada estrada tem e quem SERIA o dono. Este censo
# mede duas coisas diferentes, que a versao anterior deste mapa confundiu:
#
#     OWNER_EXISTS        o ficheiro do dono existe no disco
#     CONNECTED_TO_ROUTE  esse ficheiro toca o artefato da etapa anterior
#
#     OWNER EXISTS NAO E OWNER CONNECTED.
#
# Foi exatamente aqui que a RC-1 foi promovida cedo demais: `importar_italia.py`
# existe e escreve estrutura — mas nao le `derived_artifact` nenhum. Ele lia
# outros artefatos JSON e gerava SQL por conta propria. Um writer existir nao
# prova que ele e o writer DESTA estrada.
MODELO = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.model.json')

# O vocabulario de estado ja e da casa. `CODE` nunca vira `OBSERVED` por
# simpatia: sao duas perguntas, e uma delas custa uma execucao real.
ESTADOS = ('UNKNOWN', 'DECLARED', 'CODE', 'LOCAL_TESTED', 'DB_TESTED',
           'LIVE_SCHEMA', 'OBSERVED', 'BLOCKED', 'NOT_APPLICABLE')

# Estados que provam que a etapa ACONTECEU, nao so que ha codigo para ela.
ESTADOS_OBSERVADOS = ('OBSERVED',)
ESTADOS_PROVADOS_EM_BANCO = ('DB_TESTED', 'LIVE_SCHEMA')

ETAPAS = ('DISCOVER', 'FETCH', 'RAW', 'RUN', 'CHECKPOINT', 'DERIVED',
          'STRUCTURED', 'ADMISSION')


def _existe(caminho):
    return bool(caminho) and os.path.exists(os.path.join(RAIZ, caminho))


# ── A ESCADA DA CONEXAO ──────────────────────────────────────────────────
# A versao anterior chamava de «ligada» qualquer aresta cujo grep desse
# positivo — e o proprio censo escrevia que grep positivo era frouxo, enquanto
# `ARCHITECTURE_CLOSED` o aceitava como suficiente. Incoerente.
#
# Reproduzido em `tests/fixtures/ARESTAS/`: um ficheiro cujo unico
# `derived_artifact` esta num docstring devolvia CONNECTED=True, igual a um que
# consulta a tabela de verdade.
#
#     GREP POSITIVO NAO E EDGE PROVADA.
#
# Agora sao dois eixos que a versao anterior tinha colapsado num booleano:
#
#     CONNECTION_DISCOVERY  achar candidatos e barato — grep serve
#     CONNECTION_PROOF      provar custa mais — e so ele fecha arquitetura
SEM_EVIDENCIA = 'NO_CONNECTION_EVIDENCE'
CANDIDATA = 'CANDIDATE_CONNECTION'
POR_CODIGO = 'CODE_CONNECTED'
POR_TESTE = 'TESTED_CONNECTION'
OBSERVADA = 'OBSERVED_CONNECTION'
NAO_SE_APLICA = 'CONNECTION_NOT_APPLICABLE'

ESCADA = (SEM_EVIDENCIA, CANDIDATA, POR_CODIGO, POR_TESTE, OBSERVADA)

# O degrau minimo que FECHA uma aresta. `CANDIDATE` fica de fora de proposito:
# era exatamente ele que pintava verde cedo demais. `OBSERVED` NAO e exigido —
# arquitetura e observacao continuam eixos separados.
DEGRAU_QUE_FECHA = POR_CODIGO


def _codigo_executavel(caminho):
    """O ficheiro sem docstrings nem comentarios — so o que a maquina executa.

    Feito por AST, nao por regex: uma regex que tente remover comentarios
    tropeça na primeira `#` dentro de uma string, e passaria a mentir na
    direcao contraria.
    """
    import ast
    try:
        with open(caminho, encoding='utf-8', errors='ignore') as f:
            fonte = f.read()
        arvore = ast.parse(fonte)
    except (SyntaxError, ValueError):
        return None
    for no in ast.walk(arvore):
        # A docstring e o primeiro Expr/Constant str do corpo. Removida aqui,
        # ela deixa de poder «provar» uma ligacao que nao existe.
        corpo = getattr(no, 'body', None)
        if isinstance(corpo, list) and corpo:
            primeiro = corpo[0]
            if (isinstance(primeiro, ast.Expr)
                    and isinstance(getattr(primeiro, 'value', None), ast.Constant)
                    and isinstance(primeiro.value.value, str)):
                no.body = corpo[1:]
    # `ast.unparse` devolve so o codigo — comentarios ja se perderam no parse.
    try:
        return ast.unparse(arvore)
    except Exception:                                       # noqa: BLE001
        return None


def _liga(edge, prova_de_teste=None, prova_observada=None):
    """Em que DEGRAU esta a aresta. Devolve um nome da escada, ou None.

    None = nao ha aresta a medir (uma etapa cujo dono e um catalogo, por
    exemplo). Diferente de `NO_CONNECTION_EVIDENCE`, que e um veredito.

    O grep continua, e continua util — para o NAO. Quem nao menciona o artefato
    nem em comentario nao pode estar ligado, e isso e definitivo e barato. O que
    mudou e o SIM: mencionar so promove a candidata.
    """
    if not edge:
        return None
    ficheiro, agulha = edge
    caminho = os.path.join(RAIZ, ficheiro)
    if not os.path.exists(caminho):
        return SEM_EVIDENCIA
    with open(caminho, encoding='utf-8', errors='ignore') as f:
        bruto = f.read()
    if agulha not in bruto:
        return SEM_EVIDENCIA                # o grep NEGATIVO e prova
    if prova_observada:
        return OBSERVADA
    if prova_de_teste:
        return POR_TESTE
    codigo = _codigo_executavel(caminho)
    if codigo is None:
        # Nao e Python (ou nao compila): nao da para subir alem de candidata
        # sem inventar um segundo analisador.
        return CANDIDATA
    return POR_CODIGO if agulha in codigo else CANDIDATA


def _fecha(degrau):
    """Este degrau fecha a aresta? CANDIDATE nao fecha — era o atalho."""
    if degrau in (None, NAO_SE_APLICA):
        return True
    return ESCADA.index(degrau) >= ESCADA.index(DEGRAU_QUE_FECHA)


def rotas_medidas():
    with open(MODELO, encoding='utf-8') as f:
        modelo = json.load(f)
    saida = []
    for rc in modelo['ROUTE_CLASSES']:
        etapas, faltam = {}, []
        for nome in ETAPAS:
            passo = (rc.get('STEPS') or {}).get(nome)
            if passo is None:
                if rc.get('BLOCKED_REASON') or rc.get('DEBT_REASON'):
                    continue
                etapas[nome] = {'STATE': 'UNKNOWN', 'OWNER': None,
                                'OWNER_EXISTS': False, 'CONNECTED_TO_ROUTE': False}
                faltam.append(nome)
                continue
            estado = passo.get('STATE', 'UNKNOWN')
            assert estado in ESTADOS, 'estado fora do vocabulario: %s' % estado
            dono = passo.get('OWNER')
            existe = _existe(dono)
            ligado = _liga(passo.get('EDGE'),
                           prova_de_teste=passo.get('EDGE_TEST'),
                           prova_observada=passo.get('EDGE_OBSERVED'))
            linha = {
                'STATE': estado,
                'OWNER': dono,
                'OWNER_EXISTS': existe,
                # Os dois eixos, separados. `CONNECTED_TO_ROUTE` sobrevive como
                # booleano de leitura rapida, mas quem decide fechamento e o
                # DEGRAU — e so a partir de CODE_CONNECTED.
                'CONNECTION_LEVEL': ligado,
                'CONNECTED_TO_ROUTE': (None if ligado is None
                                       else _fecha(ligado)),
                'EDGE_TEST': passo.get('EDGE_TEST'),
                'EDGE_OBSERVED': passo.get('EDGE_OBSERVED'),
                'PROOF_KIND': passo.get('PROOF_KIND'),
                'PROOF_REF': passo.get('PROOF_REF'),
            }
            if estado == 'NOT_APPLICABLE':
                linha['NOT_APPLICABLE_REASON'] = passo.get('NOT_APPLICABLE_REASON')
                if not linha['NOT_APPLICABLE_REASON']:
                    faltam.append(nome)          # N/A sem razao NAO vale
            else:
                # A etapa so conta como fechada se tem dono NO DISCO e a aresta
                # foi MEDIDA. `ligado is None` = nao ha aresta a medir; nesse
                # caso basta o dono existir.
                # `ligado is None` = nao ha aresta a medir; basta o dono existir.
                if not existe or (ligado is not None and not _fecha(ligado)):
                    faltam.append(nome)
            etapas[nome] = linha

        bloqueada = bool(rc.get('BLOCKED_REASON'))
        divida = bool(rc.get('DEBT_REASON'))
        fechada = (not bloqueada and not divida and not faltam and bool(etapas))
        observadas = [n for n, e in etapas.items()
                      if e['STATE'] in ESTADOS_OBSERVADOS]
        em_banco = [n for n, e in etapas.items()
                    if e['STATE'] in ESTADOS_PROVADOS_EM_BANCO]
        if bloqueada:
            observacao = 'BLOCKED'
        elif divida:
            observacao = 'DEBT'
        elif observadas and len(observadas) + len(
                [n for n, e in etapas.items() if e['STATE'] == 'NOT_APPLICABLE']) == len(etapas):
            observacao = 'OBSERVED'
        elif observadas:
            observacao = 'PARTIALLY_OBSERVED'
        elif em_banco:
            observacao = 'DB_TESTED'
        else:
            observacao = 'NOT_OBSERVED'
        saida.append({
            'ROUTE_CLASS_ID': rc['ID'], 'NAME': rc['NAME'],
            'STEPS': etapas,
            'ARCHITECTURE_CLOSED': fechada,
            'STEPS_BLOQUEANDO': faltam,
            'OBSERVATION_STATE': observacao,
            'BLOCKED_REASON': rc.get('BLOCKED_REASON'),
            'DEBT_REASON': rc.get('DEBT_REASON'),
        })
    return saida


# ═════════════════════════════════════════════════════════════════════════
# ROUTE MEMBERSHIPS — a fonte pertence a que estrada, e com que prova
# ═════════════════════════════════════════════════════════════════════════
# A versao anterior contava assim:
#
#     provadas = 1
#     desconhecidas = fontes sem ACCESS_METHOD conhecido
#     candidatas = o resto
#
# Tres erros num so lugar. `provadas = 1` era um numero escrito a mao.
# `desconhecidas` derivava de ACCESS_METHOD — que e o que o CATALOGO diz, nao a
# rota que a fonte tem. E a subtracao supunha que uma fonte pertence a exatamente
# uma estrada.
#
#     SOURCE_VERDICT != ACCESS_METHOD != ROUTE_MEMBERSHIP.
#     E: SOURCE 1:N ROUTES.
#
# Agora cada pertenca e um registro proprio, derivado de EVIDENCIA PRESERVADA, e
# as contagens saem dos registros.
LEDGER = os.path.join(RAIZ, 'data', 'collection-ledger', 'italy',
                      'observations.ndjson')
PROBE = os.path.join(RAIZ, 'data', 'samples', 'IT-PROBE', 'probe-fase-c.json')

# A ESCADA DA EVIDENCIA. Subir um degrau custa mais do que o anterior, e nenhum
# degrau de baixo vira o de cima por insistencia.
ESPERADO = 'EXPECTED'                       # o catalogo imagina («esperado PDF»)
DECLARADO = 'DECLARED'                      # o catalogo afirma («CSV direto»)
HISTORICO = 'HISTORICALLY_OBSERVED'         # ja foi colhido, e ha recibo
PORTA_VIVA = 'LIVE_METADATA_PROVEN'         # responde, e so
BUSCA_VIVA = 'LIVE_FETCH_PROVEN'            # o byte veio e virou raw_asset

PROVADA = 'PROVEN'
CANDIDATA_M = 'CANDIDATE'
DECLARADA_M = 'DECLARED'
DESCONHECIDA = 'UNKNOWN'


def _ledger():
    """As observacoes preservadas em Git. Recibo historico, nao promessa."""
    if not os.path.exists(LEDGER):
        return {}
    por = {}
    with open(LEDGER, encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            o = json.loads(linha)
            por.setdefault(o.get('SOURCE_ID'), []).append(o)
    return por


def _probe():
    """43 URLs medidas em 2026-09-07 com egresso italiano.

    ACCESS_OK NAO E ROUTE_PROVEN. Medido: os 33 ACCESS_OK devolveram todos
    `text/html` — sao paginas iniciais. Isso prova FRONT_DOOR_ACCESS: a fonte
    responde de Italia. Nao diz por onde se busca o documento.
    """
    if not os.path.exists(PROBE):
        return {}
    with open(PROBE, encoding='utf-8') as f:
        d = json.load(f)
    por = {}
    for r in d.get('RESULTADOS') or []:
        for s in (r.get('SOURCE_IDS') or []):
            por.setdefault(s.get('SOURCE_ID'), []).append(r)
    return por


def _forma_declarada(acesso):
    """O que o catalogo diz da FORMA — e em que degrau isso fica."""
    a = (acesso or '').upper()
    esperado = 'ESPERADO' in a
    if 'SDMX' in a:
        return 'RC-11', (ESPERADO if esperado else DECLARADO)
    if 'CSV' in a or 'XLSX' in a or 'DATASET' in a:
        return 'RC-10', (ESPERADO if esperado else DECLARADO)
    if 'PDF' in a or 'HTML' in a:
        return 'RC-1', (ESPERADO if esperado else DECLARADO)
    return None, None


def memberships():
    """Um registro por (fonte, estrada). Derivado, nunca digitado."""
    with open(MODELO, encoding='utf-8') as f:
        canario = json.load(f).get('CANARIO') or {}
    led, prb = _ledger(), _probe()
    saida = []
    for f in fontes_it():
        sid = f.get('SOURCE_ID')
        acesso = f.get('ACCESS_METHOD')
        obs = led.get(sid) or []
        # 1 · O CANARIO — a unica rota buscada ponta a ponta.
        if sid == canario.get('SOURCE_ID'):
            saida.append({
                'SOURCE_ID': sid, 'ROUTE_CLASS_ID': canario['ROUTE_CLASS_ID'],
                'ROLE': 'PRIMARY', 'STATE': PROVADA,
                'PROOF_KIND': canario['PROOF_KIND'], 'PROOF_REF': canario['PROOF_REF'],
                'ACCESS_METHOD': acesso, 'ACCESS_METHOD_STATE': DECLARADO,
                'BLOCKER': None,
                'WHAT_IS_MISSING': ('nada nesta aresta: o byte veio e virou '
                                    'raw_asset. O que falta e da ESTRADA, nao '
                                    'desta fonte — STRUCTURED e ADMISSION.'),
            })
        # 2 · O LEDGER — coleta recorrente com recibo. E a RC-9 por definicao:
        #     e la que o estado dela mora. Divida, e prova ao mesmo tempo.
        if obs:
            saida.append({
                'SOURCE_ID': sid, 'ROUTE_CLASS_ID': 'RC-9',
                'ROLE': 'HISTORICAL', 'STATE': PROVADA,
                'PROOF_KIND': HISTORICO,
                'PROOF_REF': 'data/collection-ledger/italy/observations.ndjson (%d obs)' % len(obs),
                'ACCESS_METHOD': acesso, 'ACCESS_METHOD_STATE': DECLARADO,
                'BLOCKER': None,
                'WHAT_IS_MISSING': 'a memoria e Git, nao os donos canonicos (P-011)',
            })
            # E a FORMA observada sugere a estrada canonica equivalente — mas
            # so como candidata: o recibo prova que houve busca, nao que a
            # cadeia canonica foi usada.
            mimes = {o.get('MIME_ASSINATURA') for o in obs}
            alvo = 'RC-10' if mimes <= {'TEXTO'} else 'RC-1'
            if not (sid == canario.get('SOURCE_ID') and alvo == canario.get('ROUTE_CLASS_ID')):
                saida.append({
                    'SOURCE_ID': sid, 'ROUTE_CLASS_ID': alvo,
                    'ROLE': 'PRIMARY', 'STATE': CANDIDATA_M,
                    'PROOF_KIND': HISTORICO,
                    'PROOF_REF': 'MIME_ASSINATURA observado: %s' % ', '.join(sorted(m for m in mimes if m)),
                    'ACCESS_METHOD': acesso, 'ACCESS_METHOD_STATE': DECLARADO,
                    'BLOCKER': None,
                    'WHAT_IS_MISSING': ('uma captura pela cadeia canonica '
                                        '(Storage + raw_asset), como a do canario'),
                })
        # 3 · A FORMA que o catalogo declara ou espera.
        alvo, degrau = _forma_declarada(acesso)
        if alvo and not obs and sid != canario.get('SOURCE_ID'):
            saida.append({
                'SOURCE_ID': sid, 'ROUTE_CLASS_ID': alvo,
                'ROLE': 'PRIMARY',
                'STATE': DECLARADA_M if degrau == DECLARADO else CANDIDATA_M,
                'PROOF_KIND': degrau, 'PROOF_REF': acesso,
                'ACCESS_METHOD': acesso, 'ACCESS_METHOD_STATE': degrau,
                'BLOCKER': None,
                'WHAT_IS_MISSING': ('uma busca real: o catalogo descreve a forma, '
                                    'e descricao nao prova rota'),
            })
    return saida, led, prb, canario


def resolucao_das_fontes(regs, led, prb):
    """Resumo POR FONTE. Uma fonte com 1 PROVEN + 1 CANDIDATE tem rota provada."""
    por = {}
    for f in fontes_it():
        sid = f.get('SOURCE_ID')
        meus = [r for r in regs if r['SOURCE_ID'] == sid]
        estados = {r['STATE'] for r in meus}
        alcancavel = any(str(r.get('RESULTADO', '')).startswith('ACCESS_OK')
                         for r in (prb.get(sid) or []))
        # `BLOCKED_PARA_CURL` NAO e BLOCKED. O probe usou curl; o servidor
        # recusou curl. Isso e um impedimento de FERRAMENTA, e a mesma URL pode
        # abrir com um agente comum. BLOCKED e para impedimento CONHECIDO de
        # politica — login, autorizacao que a casa nao tem, termo que proibe.
        #
        #     BLOCKED NAO E O ARMARIO ONDE SE GUARDA O DESCONHECIDO.
        recusou_a_ferramenta = bool(prb.get(sid)) and all(
            r.get('RESULTADO') == 'BLOCKED_PARA_CURL' for r in prb[sid])
        bloqueado = False
        if PROVADA in estados:
            estado = 'HAS_PROVEN_ROUTE'
        elif estados & {CANDIDATA_M, DECLARADA_M}:
            estado = 'ONLY_CANDIDATE_ROUTE'
        elif bloqueado:
            estado = 'BLOCKED'
        elif recusou_a_ferramenta:
            estado = 'ROUTE_UNKNOWN'
        elif alcancavel:
            # A porta abre e nao sabemos por onde se busca. E mais do que
            # UNKNOWN puro, e menos do que candidata: nao ha forma nenhuma.
            estado = 'REACHABLE_ROUTE_UNKNOWN'
        else:
            estado = 'ROUTE_UNKNOWN'
        por[sid] = {
            'SOURCE_ID': sid,
            'HAS_PROVEN_ROUTE': PROVADA in estados,
            'HAS_CANDIDATE_ROUTE': bool(estados & {CANDIDATA_M, DECLARADA_M}),
            'ROUTE_RESOLUTION_STATE': estado,
            'MEMBERSHIPS': len(meus),
            'FRONT_DOOR_ACCESS': alcancavel,
            'CHEAPEST_NEXT_PROOF': (
                'nada — ja provada' if PROVADA in estados else
                'uma captura pela cadeia canonica' if estados else
                'ler a pagina inicial ja preservada e achar o link do documento'
                if alcancavel else
                'repetir o probe read-only com agente comum: curl foi recusado, '
                'e recusar curl nao e recusar a casa'
                if recusou_a_ferramenta else 'probe read-only da porta de entrada'),
            'TOOL_REFUSED': recusou_a_ferramenta,
        }
    return por


def orquestrador():
    """Existe uma peca que ESCOLHE o executor e coordena? MEDIDO, nao lembrado.

    O mapa anterior publicou «nao existe orquestrador» apoiado numa metrica de
    `censo_da_coleta.py` — «0 pecas coordenam mais de um executor». Essa metrica
    conta IMPORT direto, e `orquestrador/orquestrador.py` despacha por
    `subprocess`. A metrica estava certa; a leitura dela e que respondia outra
    pergunta.

        UMA METRICA NAO E UMA RESPOSTA
        ENQUANTO NINGUEM CONFERIR O QUE ELA MEDE.

    Aqui a pergunta e direta: o ficheiro existe, e quantos executores as
    receitas lhe dao para escolher?
    """
    caminho = os.path.join(RAIZ, 'orquestrador', 'orquestrador.py')
    if not os.path.exists(caminho):
        return {'EXISTE': False, 'PROVA': 'orquestrador/orquestrador.py nao existe'}
    alcance = None
    try:
        import receitas                                    # noqa: PLC0415
        alcance = len(getattr(receitas, 'EXECUTORES', ()) or ())
    except Exception:                                      # noqa: BLE001
        alcance = None
    return {
        'EXISTE': True,
        'FICHEIRO': 'orquestrador/orquestrador.py',
        'EXECUTORES_ALCANCADOS': alcance,
        'PROVA': ('recebe um Pedido, resolve um Plano em `pedido/receitas.py` e '
                  'despacha por subprocess. NAO coleta: escolhe quem coleta.'),
        'RESSALVA': ('alcanca %s dos executores medidos por censo_da_coleta.py — '
                     'existir nao e cobrir. E `SINTONIA SCRAP` continua sendo '
                     'COMPOSITE_EXECUTOR, nao um segundo orquestrador: ele '
                     'coordena rotas de UMA aquisicao.' % alcance),
    }


def main():
    fontes = ordenadas = fontes_it()
    dec, perm, sem_razao = classes_sociais()
    ap_def, ap_fb = apify()
    rotas = rotas_medidas()

    # ── AS CONTAGENS SAO DERIVADAS, NUNCA DIGITADAS ──────────────────────
    # A versao anterior deste mapa publicava «2 CLOSED» porque uma pessoa
    # escreveu 2. Agora o numero nao existe ate ser contado.
    fechadas = [r['ROUTE_CLASS_ID'] for r in rotas if r['ARCHITECTURE_CLOSED']]
    observadas = [r['ROUTE_CLASS_ID'] for r in rotas
                  if r['OBSERVATION_STATE'] in ('OBSERVED', 'PARTIALLY_OBSERVED')]
    em_banco = [r['ROUTE_CLASS_ID'] for r in rotas
                if r['OBSERVATION_STATE'] == 'DB_TESTED']
    bloqueadas = [r['ROUTE_CLASS_ID'] for r in rotas
                  if r['OBSERVATION_STATE'] == 'BLOCKED']
    dividas = [r['ROUTE_CLASS_ID'] for r in rotas
               if r['OBSERVATION_STATE'] == 'DEBT']

    # ── AS CONTAGENS DE FONTE SAEM DAS MEMBERSHIPS ───────────────────────
    # `provadas = 1` era um numero escrito a mao, e `desconhecidas` derivava de
    # ACCESS_METHOD — que e o que o CATALOGO diz, nao a rota que a fonte tem.
    #
    #     ACCESS METHOD NAO E ROUTE MEMBERSHIP.
    regs, led, prb, canario = memberships()
    resolucao = resolucao_das_fontes(regs, led, prb)
    por_estado = collections.Counter(v['ROUTE_RESOLUTION_STATE']
                                     for v in resolucao.values())
    por_membership = collections.Counter(r['STATE'] for r in regs)
    provadas = por_estado['HAS_PROVEN_ROUTE']
    candidatas = por_estado['ONLY_CANDIDATE_ROUTE']
    desconhecidas = (por_estado['ROUTE_UNKNOWN']
                     + por_estado['REACHABLE_ROUTE_UNKNOWN'])
    # Que classes ja tem pelo menos UMA pertenca provada.
    classes_com_prova = sorted({r['ROUTE_CLASS_ID'] for r in regs
                                if r['STATE'] == PROVADA})
    por_classe = {}
    for r in rotas:
        rid = r['ROUTE_CLASS_ID']
        meus = [x for x in regs if x['ROUTE_CLASS_ID'] == rid]
        por_classe[rid] = {
            'PROVEN_SOURCE_MEMBERSHIPS': sum(1 for x in meus if x['STATE'] == PROVADA),
            'CANDIDATE_SOURCE_MEMBERSHIPS': sum(
                1 for x in meus if x['STATE'] in (CANDIDATA_M, DECLARADA_M)),
            'BLOCKED_SOURCE_MEMBERSHIPS': sum(1 for x in meus if x['STATE'] == 'BLOCKED'),
            'EVIDENCE_LEVELS': sorted({x['PROOF_KIND'] for x in meus if x.get('PROOF_KIND')}),
        }

    rel = {
        'SCHEMA': 'estradas-it/v1',
        'PROVENANCE': {
            'CATALOGO': os.path.relpath(CATALOGO, RAIZ).replace('\\', '/'),
            'MATRIZ': 'leis/social_matriz.py',
            'NOTA': ('a CLASSE de rota social vem da matriz, que ja era a dona. '
                     'As classes nao-sociais sao derivadas do codigo medido, e '
                     'estao no mapa em prosa — este ficheiro conta o que da para '
                     'contar sem opinar.'),
        },
        'ROUTE_CLASSES': rotas,
        'ROUTE_CLASSES_MODELED': len(rotas),
        'ROUTE_CLASSES_ARCHITECTURE_CLOSED': fechadas,
        'ROUTE_CLASSES_OBSERVED': observadas,
        'ROUTE_CLASSES_DB_TESTED': em_banco,
        'ROUTE_CLASSES_BLOCKED': bloqueadas,
        'ROUTE_CLASSES_DEBT': dividas,
        # Quantas classes o sistema PRECISA no total? Enquanto houver fonte com
        # rota desconhecida, nao da para saber: uma delas pode exigir uma
        # estrada que ninguem modelou ainda. UNKNOWN e a resposta honesta.
        'ROUTE_CLASSES_REQUIRED_TOTAL': 'UNKNOWN',
        'ROUTE_CLASSES_REQUIRED_TOTAL_PORQUE': (
            '%d fonte(s) sem rota conhecida. Ate a M1 provar, nenhuma delas '
            'garante caber nas %d classes modeladas.' % (desconhecidas, len(rotas))),
        'ROUTE_MEMBERSHIPS': regs,
        'ROUTE_MEMBERSHIP_COUNTS': {
            'TOTAL_PROVEN_MEMBERSHIPS': por_membership[PROVADA],
            'TOTAL_CANDIDATE_MEMBERSHIPS': (por_membership[CANDIDATA_M]
                                            + por_membership[DECLARADA_M]),
            'TOTAL_BLOCKED_MEMBERSHIPS': por_membership['BLOCKED'],
            'TOTAL': len(regs),
        },
        'ROUTE_RESOLUTION_COUNTS': dict(por_estado),
        'POR_ROUTE_CLASS': por_classe,
        'ROUTE_CLASSES_COM_MEMBERSHIP_PROVADA': classes_com_prova,
        'RESOLUCAO_POR_FONTE': resolucao,
        'FONTES_IT': {
            'TOTAL': len(fontes),
            'SOURCES_WITH_PROVEN_ROUTE': provadas,
            'SOURCES_WITH_ONLY_CANDIDATE_ROUTE': candidatas,
            'SOURCES_ROUTE_UNKNOWN': desconhecidas,
            'SOURCES_BLOCKED': por_estado['BLOCKED'],
            'PROVEN_PORQUE': ('derivado de ROUTE_MEMBERSHIPS, nunca digitado. '
                              'Descricao («boletim», «PDF») nao prova route '
                              'class: CANDIDATE NAO E PROVEN.'),
            # O PROXY ANTIGO fica publicado ao lado, e so para isto: um teste
            # compara os dois e falha se voltarem a bater. Se batessem, seria o
            # mesmo numero de ACCESS_METHOD com nome novo.
            'PROXY_ANTIGO_ACCESS_METHOD_NAO_SEI': sum(
                1 for f in ordenadas if not rota_conhecida(f)),
            'COM_ROTA_DECLARADA': sum(1 for f in ordenadas if rota_conhecida(f)),
            'POR_PAPEL': dict(collections.Counter(str(f.get('SOURCE_ROLE')) for f in fontes)),
        },
        'CLASSES_SOCIAIS': {
            'DECLARADAS': dict(dec),
            'PERMITIDAS': dict(perm),
            'ROTAS_SEM_RAZAO_ESCRITA': sem_razao,
        },
        'APIFY': {'DEFAULT': ap_def, 'FALLBACK': ap_fb,
                  'NOTA': 'APIFY-LAST: default zero e a leitura correta'},
        'GIT_COMO_BANCO_OPERACIONAL': git_como_banco(),
        'ORQUESTRADOR': orquestrador(),
        'COLLECTION_FOUNDATION_CLOSED': fdc.COLLECTION_FOUNDATION_CLOSED,
    }
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
    print('FONTES IT %d · com rota PROVADA %d · so CANDIDATA %d · UNKNOWN %d · BLOCKED %d'
          % (rel['FONTES_IT']['TOTAL'], provadas, candidatas, desconhecidas,
             por_estado['BLOCKED']))
    print('MEMBERSHIPS %d · provadas %d · candidatas %d'
          % (len(regs), por_membership[PROVADA],
             por_membership[CANDIDATA_M] + por_membership[DECLARADA_M]))
    print()
    print('ROTA  NOME                        ARQUITETURA  OBSERVACAO')
    for r in rotas:
        print('  %-4s %-26s %-12s %s%s'
              % (r['ROUTE_CLASS_ID'], r['NAME'],
                 'FECHADA' if r['ARCHITECTURE_CLOSED'] else 'ABERTA',
                 r['OBSERVATION_STATE'],
                 ('  falta: ' + ', '.join(r['STEPS_BLOQUEANDO'])) if r['STEPS_BLOQUEANDO'] else ''))
    print()
    print('ARCHITECTURE_CLOSED %d · OBSERVED %d · DB_TESTED %d · BLOCKED %d · DEBT %d'
          % (len(fechadas), len(observadas), len(em_banco), len(bloqueadas), len(dividas)))
    print('CLASSES SOCIAIS %d · APIFY default %d / fallback %d'
          % (len(dec), ap_def, ap_fb))
    print('GIT COMO BANCO: %d ficheiro(s)' % len(rel['GIT_COMO_BANCO_OPERACIONAL']))
    orq = rel['ORQUESTRADOR']
    print('ORQUESTRADOR: %s%s'
          % ('EXISTE' if orq['EXISTE'] else 'nao existe',
             (' · alcanca %s executores' % orq.get('EXECUTORES_ALCANCADOS'))
             if orq['EXISTE'] else ''))
    print('COLLECTION_FOUNDATION_CLOSED = %s'
          % ('SIM' if rel['COLLECTION_FOUNDATION_CLOSED'] else 'NAO'))
    print('\nescrito em %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))


if __name__ == '__main__':
    main()
